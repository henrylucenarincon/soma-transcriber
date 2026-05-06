from __future__ import annotations

from pathlib import Path
import re
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
MIN_PARAGRAPH_CHARS = 500
MAX_PARAGRAPH_CHARS = 900
SENTENCE_BOUNDARY_PATTERN = re.compile(r"(?<=[.!?])\s+")
WHITESPACE_PATTERN = re.compile(r"[ \t\f\v]+")
PART_HEADING_PATTERN = re.compile(r"^#{1,6}\s+Parte\s+\d+\b", re.IGNORECASE)


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
    formatted_text = format_transcript_paragraphs(transcript_text)
    content = f"---\n{front_matter}\n---\n\n## Transcripción literal\n\n{formatted_text}\n"

    with transcript_path.open("w", encoding="utf-8") as markdown_file:
        markdown_file.write(content)

    return transcript_path


def format_transcript_paragraphs(text: str) -> str:
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized_text:
        return ""

    output_blocks: list[str] = []
    prose_lines: list[str] = []

    for raw_line in normalized_text.split("\n"):
        line = raw_line.strip()

        if not line:
            _flush_prose_lines(prose_lines, output_blocks)
            continue

        if PART_HEADING_PATTERN.match(line):
            _flush_prose_lines(prose_lines, output_blocks)
            output_blocks.append(line)
            continue

        prose_lines.append(line)

    _flush_prose_lines(prose_lines, output_blocks)
    return "\n\n".join(block for block in output_blocks if block).strip()


def _flush_prose_lines(prose_lines: list[str], output_blocks: list[str]) -> None:
    if not prose_lines:
        return

    prose = WHITESPACE_PATTERN.sub(" ", " ".join(prose_lines)).strip()
    output_blocks.extend(_split_prose_into_paragraphs(prose))
    prose_lines.clear()


def _split_prose_into_paragraphs(prose: str) -> list[str]:
    if len(prose) <= MAX_PARAGRAPH_CHARS:
        return [prose]

    paragraphs: list[str] = []
    current = ""

    for sentence in SENTENCE_BOUNDARY_PATTERN.split(prose):
        sentence = sentence.strip()
        if not sentence:
            continue

        candidate = f"{current} {sentence}".strip() if current else sentence
        if current and len(candidate) > MAX_PARAGRAPH_CHARS and len(current) >= MIN_PARAGRAPH_CHARS:
            paragraphs.append(current)
            current = sentence
            continue

        current = candidate

        if len(current) > MAX_PARAGRAPH_CHARS:
            wrapped, current = _wrap_long_paragraph(current)
            paragraphs.extend(wrapped)

    if current:
        paragraphs.append(current)

    return paragraphs


def _wrap_long_paragraph(text: str) -> tuple[list[str], str]:
    words = text.split(" ")
    paragraphs: list[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip() if current else word
        if current and len(candidate) > MAX_PARAGRAPH_CHARS:
            paragraphs.append(current)
            current = word
        else:
            current = candidate

    if paragraphs and current and len(current) < MIN_PARAGRAPH_CHARS:
        return paragraphs[:-1], f"{paragraphs[-1]} {current}".strip()

    return paragraphs, current


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
