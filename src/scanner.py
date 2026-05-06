from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


@dataclass(frozen=True)
class VideoFile:
    original_path: Path
    relative_path: Path
    module_path: str
    video_name: str


def scan_videos(input_dir: Path) -> list[VideoFile]:
    root = input_dir.expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"No existe la carpeta de input: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"La ruta de input no es una carpeta: {root}")

    videos: list[VideoFile] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        relative_path = path.relative_to(root)
        module_path = "" if relative_path.parent == Path(".") else relative_path.parent.as_posix()
        videos.append(
            VideoFile(
                original_path=path.resolve(),
                relative_path=relative_path,
                module_path=module_path,
                video_name=path.name,
            )
        )

    return sorted(videos, key=lambda video: video.relative_path.as_posix().lower())
