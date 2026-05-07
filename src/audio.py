from __future__ import annotations

from pathlib import Path
import math
import subprocess


MAX_CHUNK_BYTES = 24 * 1024 * 1024
DEFAULT_MAX_CHUNK_MINUTES = 10
MIN_CHUNK_SECONDS = 30.0
SIZE_MARGIN = 0.90
DURATION_MARGIN = 0.98


def extract_audio(video_path: Path, audio_path: Path, overwrite: bool = False) -> Path:
    video_path = video_path.expanduser().resolve()
    audio_path = audio_path.expanduser()
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    if audio_path.exists() and audio_path.stat().st_size > 0 and not overwrite:
        return audio_path

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-b:a",
        "64k",
        "-f",
        "mp3",
        str(audio_path),
    ]

    completed = _run_media_command(command, "FFmpeg no está instalado o no está disponible en PATH.")

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"FFmpeg falló al extraer audio de {video_path}: {stderr}")

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError(f"FFmpeg no generó un audio válido: {audio_path}")

    return audio_path


def get_audio_duration_seconds(audio_path: Path) -> float:
    audio_path = audio_path.expanduser()
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]

    completed = _run_media_command(command, "FFprobe no está instalado o no está disponible en PATH.")
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"FFprobe falló al obtener duración de {audio_path}: {stderr}")

    raw_duration = completed.stdout.strip()
    try:
        duration = float(raw_duration)
    except ValueError as exc:
        raise RuntimeError(
            f"FFprobe devolvió una duración inválida para {audio_path}: {raw_duration!r}"
        ) from exc

    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError(f"Duración inválida para {audio_path}: {duration}")

    return duration


def split_audio_if_needed(
    audio_path: Path,
    chunk_dir: Path,
    max_bytes: int = MAX_CHUNK_BYTES,
    max_chunk_minutes: float | int | None = DEFAULT_MAX_CHUNK_MINUTES,
    force: bool = False,
) -> list[Path]:
    audio_path = audio_path.expanduser()

    if not audio_path.exists():
        raise FileNotFoundError(f"No existe el audio a dividir: {audio_path}")

    audio_size = audio_path.stat().st_size
    duration_seconds = get_audio_duration_seconds(audio_path)
    max_duration_seconds = _minutes_to_seconds(max_chunk_minutes)
    needs_size_split = audio_size > max_bytes
    needs_duration_split = (
        max_duration_seconds is not None and duration_seconds > max_duration_seconds
    )

    if not needs_size_split and not needs_duration_split:
        if force and chunk_dir.exists():
            _remove_existing_chunks(chunk_dir)
        return []

    chunk_dir.mkdir(parents=True, exist_ok=True)
    existing_chunks = sorted(chunk_dir.glob("chunk_*.mp3"))
    if existing_chunks and not force and _chunks_within_limits(existing_chunks, max_bytes, max_duration_seconds):
        return existing_chunks

    _remove_existing_chunks(chunk_dir)

    target_duration_seconds = _calculate_target_duration_seconds(
        audio_size=audio_size,
        duration_seconds=duration_seconds,
        max_bytes=max_bytes,
        max_duration_seconds=max_duration_seconds,
        needs_size_split=needs_size_split,
    )

    for _ in range(8):
        paths = _export_chunks_with_ffmpeg(audio_path, chunk_dir, target_duration_seconds)
        if _chunks_within_limits(paths, max_bytes, max_duration_seconds):
            return paths

        _remove_existing_chunks(chunk_dir)
        target_duration_seconds = max(target_duration_seconds * 0.8, MIN_CHUNK_SECONDS)
        if max_duration_seconds is not None:
            target_duration_seconds = min(target_duration_seconds, max_duration_seconds * DURATION_MARGIN)

    duration_label = (
        f" y duración menor o igual a {max_chunk_minutes} minutos"
        if max_duration_seconds is not None
        else ""
    )
    raise RuntimeError(
        f"No se pudo dividir {audio_path} en chunks menores a {max_bytes} bytes{duration_label}."
    )


def _calculate_target_duration_seconds(
    audio_size: int,
    duration_seconds: float,
    max_bytes: int,
    max_duration_seconds: float | None,
    needs_size_split: bool,
) -> float:
    candidates: list[float] = []

    if needs_size_split:
        bytes_per_second = max(audio_size / duration_seconds, 1)
        candidates.append((max_bytes * SIZE_MARGIN) / bytes_per_second)

    if max_duration_seconds is not None:
        candidates.append(max_duration_seconds * DURATION_MARGIN)

    if not candidates:
        return duration_seconds

    target = min(candidates)
    if max_duration_seconds is not None and max_duration_seconds < MIN_CHUNK_SECONDS:
        return max(target, 1.0)

    return max(target, MIN_CHUNK_SECONDS)


def _export_chunks_with_ffmpeg(
    audio_path: Path,
    chunk_dir: Path,
    chunk_duration_seconds: float,
) -> list[Path]:
    paths: list[Path] = []
    total_duration = get_audio_duration_seconds(audio_path)
    start = 0.0
    index = 1

    while start < total_duration:
        duration = min(chunk_duration_seconds, total_duration - start)
        if duration <= 0.5:
            break

        chunk_path = chunk_dir / f"chunk_{index:03d}.mp3"
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(audio_path),
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{duration:.3f}",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "64k",
            str(chunk_path),
        ]

        completed = _run_media_command(command, "FFmpeg no está instalado o no está disponible en PATH.")
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"FFmpeg falló al crear chunk {chunk_path}: {stderr}")

        if chunk_path.exists() and chunk_path.stat().st_size > 0:
            paths.append(chunk_path)
        elif duration > 1.0:
            raise RuntimeError(f"FFmpeg no generó un chunk válido: {chunk_path}")

        start += chunk_duration_seconds
        index += 1

    if not paths:
        raise RuntimeError(f"No se generaron chunks para {audio_path}")

    return paths


def _minutes_to_seconds(value: float | int | None) -> float | None:
    if value is None:
        return None

    minutes = float(value)
    if minutes <= 0:
        return None

    return minutes * 60


def _chunks_within_limits(
    chunks: list[Path],
    max_bytes: int,
    max_duration_seconds: float | None,
) -> bool:
    for chunk in chunks:
        if chunk.stat().st_size > max_bytes:
            return False
        if max_duration_seconds is not None and get_audio_duration_seconds(chunk) > max_duration_seconds:
            return False
    return True


def _remove_existing_chunks(chunk_dir: Path) -> None:
    if not chunk_dir.exists():
        return
    for chunk in chunk_dir.glob("chunk_*.mp3"):
        chunk.unlink()


def _run_media_command(command: list[str], missing_binary_message: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError(missing_binary_message) from exc
