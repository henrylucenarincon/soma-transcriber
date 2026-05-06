from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

try:
    from .utils import ensure_directory
except ImportError:
    from utils import ensure_directory


INDEX_COLUMNS = [
    "course_name",
    "module_path",
    "video_name",
    "original_path",
    "transcript_path",
    "status",
    "chunks_count",
    "updated_at",
]


def build_transcript_path(output_dir: Path, course_dir_name: str, relative_video_path: Path) -> Path:
    return output_dir / "transcripts" / course_dir_name / relative_video_path.with_suffix(".md")


def build_audio_path(output_dir: Path, course_dir_name: str, relative_video_path: Path) -> Path:
    return output_dir / "audio" / course_dir_name / relative_video_path.with_suffix(".mp3")


def build_chunk_dir(output_dir: Path, course_dir_name: str, relative_video_path: Path) -> Path:
    return output_dir / "chunks" / course_dir_name / relative_video_path.with_suffix("")


def write_transcript(transcript_path: Path, metadata: dict[str, Any], transcript_text: str) -> Path:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "pyyaml no está instalado. Ejecuta: pip install -r requirements.txt"
        ) from exc

    ensure_directory(transcript_path.parent)
    front_matter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True).strip()
    content = f"---\n{front_matter}\n---\n\n## Transcripción literal\n\n{transcript_text.strip()}\n"

    with transcript_path.open("w", encoding="utf-8") as markdown_file:
        markdown_file.write(content)

    return transcript_path


def write_index(
    output_dir: Path,
    course_name: str,
    videos: Iterable[Any],
    manifest: Any,
) -> Path:
    try:
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "pandas no está instalado. Ejecuta: pip install -r requirements.txt"
        ) from exc

    rows: list[dict[str, Any]] = []
    for video in videos:
        record = manifest.get_record(video.original_path) or {}
        rows.append(
            {
                "course_name": course_name,
                "module_path": video.module_path,
                "video_name": video.video_name,
                "original_path": str(video.original_path),
                "transcript_path": record.get("transcript_path", ""),
                "status": record.get("status", "pending"),
                "chunks_count": record.get("chunks_count", 0),
                "updated_at": record.get("updated_at", ""),
            }
        )

    ensure_directory(output_dir)
    index_path = output_dir / "index.csv"
    pd.DataFrame(rows, columns=INDEX_COLUMNS).to_csv(index_path, index=False)
    return index_path
