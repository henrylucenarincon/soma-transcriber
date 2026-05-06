from __future__ import annotations

from pathlib import Path
import subprocess


MAX_CHUNK_BYTES = 24 * 1024 * 1024


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

    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("FFmpeg no está instalado o no está disponible en PATH.") from exc

    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"FFmpeg falló al extraer audio de {video_path}: {stderr}")

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError(f"FFmpeg no generó un audio válido: {audio_path}")

    return audio_path


def split_audio_if_needed(
    audio_path: Path,
    chunk_dir: Path,
    max_bytes: int = MAX_CHUNK_BYTES,
    force: bool = False,
) -> list[Path]:
    audio_path = audio_path.expanduser()

    if not audio_path.exists():
        raise FileNotFoundError(f"No existe el audio a dividir: {audio_path}")

    if audio_path.stat().st_size <= max_bytes:
        if force and chunk_dir.exists():
            _remove_existing_chunks(chunk_dir)
        return []

    chunk_dir.mkdir(parents=True, exist_ok=True)
    existing_chunks = sorted(chunk_dir.glob("chunk_*.mp3"))
    if existing_chunks and not force and all(chunk.stat().st_size <= max_bytes for chunk in existing_chunks):
        return existing_chunks

    _remove_existing_chunks(chunk_dir)

    try:
        from pydub import AudioSegment
    except ImportError as exc:
        raise RuntimeError(
            "pydub no está instalado. Ejecuta: pip install -r requirements.txt"
        ) from exc

    audio = AudioSegment.from_file(str(audio_path), format="mp3")
    if len(audio) == 0:
        raise RuntimeError(f"El audio está vacío y no se puede dividir: {audio_path}")

    bytes_per_ms = max(audio_path.stat().st_size / len(audio), 1)
    target_ms = max(int((max_bytes * 0.92) / bytes_per_ms), 1000)

    for _ in range(8):
        paths = _export_chunks(audio, chunk_dir, target_ms)
        if all(path.stat().st_size <= max_bytes for path in paths):
            return paths

        _remove_existing_chunks(chunk_dir)
        target_ms = max(int(target_ms * 0.8), 1000)

    raise RuntimeError(
        f"No se pudo dividir {audio_path} en chunks menores a {max_bytes} bytes."
    )


def _export_chunks(audio: "AudioSegment", chunk_dir: Path, chunk_duration_ms: int) -> list[Path]:
    paths: list[Path] = []
    total_ms = len(audio)

    for index, start_ms in enumerate(range(0, total_ms, chunk_duration_ms), start=1):
        end_ms = min(start_ms + chunk_duration_ms, total_ms)
        chunk = audio[start_ms:end_ms]
        chunk_path = chunk_dir / f"chunk_{index:03d}.mp3"
        chunk.export(str(chunk_path), format="mp3", bitrate="64k", parameters=["-ac", "1", "-ar", "16000"])
        paths.append(chunk_path)

    return paths


def _remove_existing_chunks(chunk_dir: Path) -> None:
    if not chunk_dir.exists():
        return
    for chunk in chunk_dir.glob("chunk_*.mp3"):
        chunk.unlink()
