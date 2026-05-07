from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable

try:
    from .scanner import natural_sort_key
    from .utils import ensure_directory, safe_path_part
except ImportError:
    from scanner import natural_sort_key
    from utils import ensure_directory, safe_path_part


TRANSCRIPT_HEADING_PATTERN = re.compile(r"^##\s+Transcripci[oó]n literal\s*$", re.IGNORECASE)
FRONT_MATTER_DELIMITER = "---"


@dataclass(frozen=True)
class TranscriptDocument:
    path: Path
    relative_path: Path
    metadata: dict[str, Any]
    transcript_text: str
    module_path: str
    video_title: str


@dataclass(frozen=True)
class StudyPaths:
    course_dir: Path
    video_notes_dir: Path
    module_notes_dir: Path


def build_study_paths(output_dir: Path, course_name: str) -> StudyPaths:
    course_dir = output_dir.expanduser() / safe_path_part(course_name)
    return StudyPaths(
        course_dir=course_dir,
        video_notes_dir=course_dir / "video_notes",
        module_notes_dir=course_dir / "module_notes",
    )


def discover_transcripts(transcripts_root: Path) -> list[Path]:
    root = transcripts_root.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"No existe la carpeta de transcripciones: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"La ruta de transcripciones no es una carpeta: {root}")

    files = [path for path in root.rglob("*.md") if path.is_file()]
    return sorted(files, key=lambda path: natural_sort_key(path.relative_to(root)))


def read_transcript(transcript_path: Path, transcripts_root: Path) -> TranscriptDocument:
    root = transcripts_root.expanduser().resolve()
    path = transcript_path.expanduser().resolve()
    relative_path = path.relative_to(root)
    raw_text = path.read_text(encoding="utf-8")
    metadata, markdown_body = parse_markdown_with_front_matter(raw_text)
    transcript_text = extract_literal_transcript(markdown_body)
    module_path = str(metadata.get("module_path") or _relative_module_path(relative_path)).strip()
    video_title = relative_path.with_suffix("").name

    return TranscriptDocument(
        path=path,
        relative_path=relative_path,
        metadata=metadata,
        transcript_text=transcript_text,
        module_path=module_path,
        video_title=video_title,
    )


def parse_markdown_with_front_matter(raw_text: str) -> tuple[dict[str, Any], str]:
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith(FRONT_MATTER_DELIMITER + "\n"):
        return {}, normalized

    end_marker = "\n" + FRONT_MATTER_DELIMITER + "\n"
    end_index = normalized.find(end_marker, len(FRONT_MATTER_DELIMITER) + 1)
    if end_index == -1:
        return {}, normalized

    front_matter = normalized[len(FRONT_MATTER_DELIMITER) + 1 : end_index]
    body = normalized[end_index + len(end_marker) :]

    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "pyyaml no está instalado. Ejecuta: pip install -r requirements.txt"
        ) from exc

    parsed = yaml.safe_load(front_matter) or {}
    if not isinstance(parsed, dict):
        parsed = {}

    return parsed, body


def extract_literal_transcript(markdown_body: str) -> str:
    lines = markdown_body.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for index, line in enumerate(lines):
        if TRANSCRIPT_HEADING_PATTERN.match(line.strip()):
            return "\n".join(lines[index + 1 :]).strip()
    return markdown_body.strip()


def split_text_chunks(text: str, max_chars: int) -> list[str]:
    clean_text = text.strip()
    if not clean_text:
        return []
    if max_chars <= 0 or len(clean_text) <= max_chars:
        return [clean_text]

    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", clean_text) if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_paragraph(paragraph, max_chars))
            continue

        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if current and len(candidate) > max_chars:
            chunks.append(current.strip())
            current = paragraph
        else:
            current = candidate

    if current:
        chunks.append(current.strip())

    return chunks


def build_video_note_path(paths: StudyPaths, transcript: TranscriptDocument) -> Path:
    return paths.video_notes_dir / transcript.relative_path.with_suffix(".md")


def build_module_note_path(paths: StudyPaths, module_path: str) -> Path:
    module_name = module_note_name(module_path)
    return paths.module_notes_dir / f"{module_name}.md"


def module_note_name(module_path: str) -> str:
    if not module_path.strip():
        return "Curso"
    return safe_path_part(module_path.replace("/", " - "), fallback="Modulo")


def group_transcripts_by_module(transcripts: Iterable[TranscriptDocument]) -> dict[str, list[TranscriptDocument]]:
    grouped: dict[str, list[TranscriptDocument]] = {}
    for transcript in transcripts:
        grouped.setdefault(transcript.module_path, []).append(transcript)
    return grouped


def list_video_notes(video_notes_dir: Path) -> list[Path]:
    if not video_notes_dir.exists():
        return []
    return sorted(
        [path for path in video_notes_dir.rglob("*.md") if path.is_file()],
        key=lambda path: natural_sort_key(path.relative_to(video_notes_dir)),
    )


def list_module_notes(module_notes_dir: Path) -> list[Path]:
    if not module_notes_dir.exists():
        return []
    return sorted(
        [path for path in module_notes_dir.glob("*.md") if path.is_file()],
        key=lambda path: natural_sort_key(path.relative_to(module_notes_dir)),
    )


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def write_markdown(path: Path, content: str) -> Path:
    ensure_directory(path.parent)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def _relative_module_path(relative_path: Path) -> str:
    return "" if relative_path.parent == Path(".") else relative_path.parent.as_posix()


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    words = paragraph.split()
    chunks: list[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip() if current else word
        if current and len(candidate) > max_chars:
            chunks.append(current.strip())
            current = word
        else:
            current = candidate

    if current:
        chunks.append(current.strip())

    return chunks
