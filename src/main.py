from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
from typing import Iterable, Sequence, TypeVar

try:
    from .audio import MAX_CHUNK_BYTES, extract_audio, split_audio_if_needed
    from .manifest import Manifest, STATUS_COMPLETED
    from .scanner import VideoFile, scan_videos
    from .transcriber import build_transcription_prompt, transcribe_audio_file
    from .utils import (
        config_get,
        load_config,
        megabytes_to_bytes,
        safe_path_part,
        utc_now_iso,
    )
    from .writer import (
        build_audio_path,
        build_chunk_dir,
        build_transcript_path,
        write_index,
        write_transcript,
    )
except ImportError:
    from audio import MAX_CHUNK_BYTES, extract_audio, split_audio_if_needed
    from manifest import Manifest, STATUS_COMPLETED
    from scanner import VideoFile, scan_videos
    from transcriber import build_transcription_prompt, transcribe_audio_file
    from utils import (
        config_get,
        load_config,
        megabytes_to_bytes,
        safe_path_part,
        utc_now_iso,
    )
    from writer import (
        build_audio_path,
        build_chunk_dir,
        build_transcript_path,
        write_index,
        write_transcript,
    )


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest.json"
T = TypeVar("T")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="soma-transcriber",
        description="Transcribe cursos en video a Markdown manteniendo su estructura original.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Ruta local de la carpeta del curso.")
    parser.add_argument("--output", required=True, type=Path, help="Ruta donde se guardarán los resultados.")
    parser.add_argument("--course-name", required=True, help="Nombre del curso.")
    parser.add_argument(
        "--model",
        default=None,
        help=f"Modelo de transcripción de OpenAI. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument("--force", action="store_true", help="Reprocesar aunque el archivo ya esté completed.")
    parser.add_argument("--dry-run", action="store_true", help="Listar lo que se procesaría sin llamar a la API.")
    parser.add_argument(
        "--max-videos",
        type=positive_int,
        help="Limitar la cantidad de videos procesados después del scan.",
    )
    parser.add_argument(
        "--list-videos",
        action="store_true",
        help="Listar videos detectados con índice y estado, sin extraer audio ni llamar a la API.",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        type=Path,
        help="Ruta opcional a config.yaml. Default: config.yaml",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    load_env_file()

    input_dir = args.input.expanduser().resolve()
    output_dir = args.output.expanduser().resolve()
    course_dir_name = safe_path_part(args.course_name)

    scanned_videos = scan_videos(input_dir)
    videos = limit_videos(scanned_videos, args.max_videos)
    manifest = Manifest.load(DEFAULT_MANIFEST_PATH)

    if args.list_videos:
        print_video_list(scanned_videos, videos, manifest, args.max_videos)
        return 0

    if args.dry_run:
        print_dry_run(
            args.course_name,
            input_dir,
            output_dir,
            scanned_videos,
            videos,
            manifest,
            args.force,
            args.max_videos,
        )
        return 0

    config = load_config(args.config)
    prompt = build_transcription_prompt(config)
    selected_model = str(
        args.model
        or config_get(config, "transcription", "model", default=DEFAULT_MODEL)
        or DEFAULT_MODEL
    )
    max_chunk_mb = config_get(
        config,
        "audio",
        "max_chunk_mb",
        default=config_get(config, "audio", "max_file_mb", default=None),
    )
    max_chunk_bytes = megabytes_to_bytes(max_chunk_mb) if max_chunk_mb else MAX_CHUNK_BYTES
    max_chunk_minutes = config_get(config, "audio", "max_chunk_minutes", default=10)

    validate_runtime_dependencies()

    for video in videos:
        manifest.ensure_pending(video.original_path, video.relative_path)
    if videos:
        manifest.save()

    processed = 0
    skipped = 0
    failed = 0

    for video in progress(videos, desc="Procesando videos", unit="video"):
        existing_record = manifest.get_record(video.original_path)
        if existing_record and existing_record.get("status") == STATUS_COMPLETED and not args.force:
            skipped += 1
            continue

        transcript_path = build_transcript_path(output_dir, course_dir_name, video.relative_path)
        audio_path = build_audio_path(output_dir, course_dir_name, video.relative_path)
        chunk_dir = build_chunk_dir(output_dir, course_dir_name, video.relative_path)

        manifest.mark_processing(video.original_path, video.relative_path, transcript_path, audio_path)
        manifest.save()

        try:
            extract_audio(video.original_path, audio_path, overwrite=args.force)
            chunks = split_audio_if_needed(
                audio_path=audio_path,
                chunk_dir=chunk_dir,
                max_bytes=max_chunk_bytes,
                max_chunk_minutes=max_chunk_minutes,
                force=args.force,
            )

            if chunks:
                chunk_texts = [
                    transcribe_audio_file(chunk, model=selected_model, prompt=prompt)
                    for chunk in progress(chunks, desc=f"Chunks: {video.video_name}", unit="chunk", leave=False)
                ]
                transcript_text = combine_chunk_transcripts(chunk_texts)
            else:
                transcript_text = transcribe_audio_file(audio_path, model=selected_model, prompt=prompt)

            metadata = build_metadata(
                course_name=args.course_name,
                video=video,
                audio_path=audio_path,
                model=selected_model,
                chunked=bool(chunks),
                chunks_count=len(chunks),
            )
            write_transcript(transcript_path, metadata, transcript_text)
            manifest.mark_completed(
                video.original_path,
                video.relative_path,
                transcript_path,
                audio_path,
                chunks_count=len(chunks),
            )
            processed += 1
        except Exception as exc:
            print(f"ERROR: {video.relative_path.as_posix()} -> {exc}")
            manifest.mark_failed(
                video.original_path,
                video.relative_path,
                error=exc,
                transcript_path=transcript_path,
                audio_path=audio_path,
            )
            failed += 1
        finally:
            manifest.save()

    index_path = write_index(output_dir, args.course_name, videos, manifest)

    print(
        f"Listo. Procesados: {processed} | Saltados: {skipped} | Fallidos: {failed} | "
        f"Index: {index_path}"
    )
    return 1 if failed else 0


def build_metadata(
    course_name: str,
    video: VideoFile,
    audio_path: Path,
    model: str,
    chunked: bool,
    chunks_count: int,
) -> dict[str, object]:
    return {
        "course_name": course_name,
        "module_path": video.module_path,
        "original_file": str(video.original_path),
        "audio_file": str(audio_path),
        "model": model,
        "processed_at": utc_now_iso(),
        "status": STATUS_COMPLETED,
        "chunked": chunked,
        "chunks_count": chunks_count,
    }


def combine_chunk_transcripts(chunk_texts: list[str]) -> str:
    parts: list[str] = []
    for index, text in enumerate(chunk_texts, start=1):
        parts.append(f"### Parte {index}\n\n{text.strip()}")
    return "\n\n".join(parts)


def print_dry_run(
    course_name: str,
    input_dir: Path,
    output_dir: Path,
    scanned_videos: list[VideoFile],
    videos: list[VideoFile],
    manifest: Manifest,
    force: bool,
    max_videos: int | None,
) -> None:
    summary = summarize_actions(videos, manifest, force)

    print("Dry run: no se extraerá audio y no se llamará a OpenAI API.")
    print(f"Curso: {course_name}")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Videos detectados: {len(scanned_videos)}")
    if max_videos is not None:
        print(f"Listado limitado por --max-videos {max_videos}: {len(videos)} videos")
    print(f"Videos que se procesarían: {summary['process']}")
    print(f"Videos que se saltarían por completed: {summary['skip_completed']}")

    if not videos:
        return

    for video in videos:
        action = action_for_video(video, manifest, force)
        print(f"{action}: {video.relative_path.as_posix()}")


def print_video_list(
    scanned_videos: list[VideoFile],
    videos: list[VideoFile],
    manifest: Manifest,
    max_videos: int | None,
) -> None:
    print("Videos detectados: no se extraerá audio y no se llamará a OpenAI API.")
    print(f"Total detectados: {len(scanned_videos)}")
    if max_videos is not None:
        print(f"Listado limitado por --max-videos {max_videos}: {len(videos)} videos")

    if not videos:
        return

    for index, video in enumerate(videos, start=1):
        record = manifest.get_record(video.original_path)
        status = record.get("status", "pending") if record else "pending"
        print(f"{index:03d}. [{status}] {video.relative_path.as_posix()}")


def summarize_actions(videos: list[VideoFile], manifest: Manifest, force: bool) -> dict[str, int]:
    summary = {"process": 0, "skip_completed": 0}
    for video in videos:
        if action_for_video(video, manifest, force) == "SKIP completed":
            summary["skip_completed"] += 1
        else:
            summary["process"] += 1
    return summary


def action_for_video(video: VideoFile, manifest: Manifest, force: bool) -> str:
    record = manifest.get_record(video.original_path)
    completed = bool(record and record.get("status") == STATUS_COMPLETED)
    return "SKIP completed" if completed and not force else "PROCESS"


def limit_videos(videos: list[VideoFile], max_videos: int | None) -> list[VideoFile]:
    if max_videos is None:
        return videos
    return videos[:max_videos]


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--max-videos debe ser un entero positivo.") from exc

    if parsed < 1:
        raise argparse.ArgumentTypeError("--max-videos debe ser mayor o igual a 1.")

    return parsed


def validate_runtime_dependencies() -> None:
    validate_ffmpeg_available()
    validate_openai_api_key()


def validate_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ERROR: FFmpeg no está disponible en PATH. Instálalo con: brew install ffmpeg")

    completed = subprocess.run(
        ["ffmpeg", "-version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        details = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(f"ERROR: FFmpeg está instalado pero no responde correctamente. {details}")


def validate_openai_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "ERROR: Falta OPENAI_API_KEY. Crea un archivo .env desde .env.example "
            "o exporta la variable antes de transcribir."
        )


def load_env_file() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()


def progress(items: Iterable[T], **kwargs: object) -> Iterable[T]:
    try:
        from tqdm import tqdm
    except ImportError:
        return items

    return tqdm(items, **kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
