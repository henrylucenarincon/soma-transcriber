from __future__ import annotations

from pathlib import Path
import json
from typing import Any

try:
    from .utils import truncate_error, utc_now_iso
except ImportError:
    from utils import truncate_error, utc_now_iso


STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
VALID_STATUSES = {STATUS_PENDING, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_FAILED}


class StudyManifest:
    def __init__(self, path: Path, records: dict[str, dict[str, Any]] | None = None) -> None:
        self.path = path
        self.records: dict[str, dict[str, Any]] = records or {}

    @classmethod
    def load(cls, path: Path) -> "StudyManifest":
        path = path.expanduser()
        if not path.exists():
            return cls(path=path)

        with path.open("r", encoding="utf-8") as manifest_file:
            raw_data = json.load(manifest_file)

        if isinstance(raw_data, dict) and "transcripts" in raw_data and isinstance(raw_data["transcripts"], dict):
            records = raw_data["transcripts"]
        elif isinstance(raw_data, dict):
            records = raw_data
        elif isinstance(raw_data, list):
            records = {
                str(item.get("transcript_path")): item
                for item in raw_data
                if isinstance(item, dict) and item.get("transcript_path")
            }
        else:
            raise ValueError(f"Formato de study manifest inválido: {path}")

        return cls(path=path, records=records)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as manifest_file:
            json.dump(self.records, manifest_file, ensure_ascii=False, indent=2)
            manifest_file.write("\n")

    def get_record(self, transcript_path: Path) -> dict[str, Any] | None:
        return self.records.get(self._key(transcript_path))

    def ensure_pending(self, transcript_path: Path, relative_path: Path | str) -> dict[str, Any]:
        key = self._key(transcript_path)
        if key not in self.records:
            self.records[key] = self._base_record(
                transcript_path=transcript_path,
                relative_path=relative_path,
                status=STATUS_PENDING,
            )
        return self.records[key]

    def mark_processing(
        self,
        transcript_path: Path,
        relative_path: Path | str,
        video_note_path: Path,
    ) -> dict[str, Any]:
        return self._upsert(
            transcript_path=transcript_path,
            relative_path=relative_path,
            status=STATUS_PROCESSING,
            video_note_path=str(video_note_path),
            error="",
        )

    def mark_completed(
        self,
        transcript_path: Path,
        relative_path: Path | str,
        video_note_path: Path,
    ) -> dict[str, Any]:
        return self._upsert(
            transcript_path=transcript_path,
            relative_path=relative_path,
            status=STATUS_COMPLETED,
            video_note_path=str(video_note_path),
            error="",
        )

    def mark_failed(
        self,
        transcript_path: Path,
        relative_path: Path | str,
        error: BaseException | str,
        video_note_path: Path | None = None,
    ) -> dict[str, Any]:
        current = self.get_record(transcript_path) or {}
        return self._upsert(
            transcript_path=transcript_path,
            relative_path=relative_path,
            status=STATUS_FAILED,
            video_note_path=str(video_note_path or current.get("video_note_path", "")),
            error=truncate_error(error),
        )

    def set_global_output(self, name: str, output_path: Path, status: str, error: str = "") -> None:
        if status not in VALID_STATUSES:
            raise ValueError(f"Status inválido para study manifest: {status}")
        key = f"global::{name}"
        self.records[key] = {
            "transcript_path": "",
            "relative_path": key,
            "status": status,
            "video_note_path": str(output_path),
            "error": error,
            "updated_at": utc_now_iso(),
        }

    def _upsert(
        self,
        transcript_path: Path,
        relative_path: Path | str,
        status: str,
        video_note_path: str,
        error: str,
    ) -> dict[str, Any]:
        if status not in VALID_STATUSES:
            raise ValueError(f"Status inválido para study manifest: {status}")

        key = self._key(transcript_path)
        record = self.records.get(key) or self._base_record(transcript_path, relative_path, status)
        record.update(
            {
                "transcript_path": key,
                "relative_path": Path(relative_path).as_posix(),
                "status": status,
                "video_note_path": video_note_path,
                "error": error,
                "updated_at": utc_now_iso(),
            }
        )
        self.records[key] = record
        return record

    @staticmethod
    def _base_record(transcript_path: Path, relative_path: Path | str, status: str) -> dict[str, Any]:
        return {
            "transcript_path": str(transcript_path.expanduser().resolve()),
            "relative_path": Path(relative_path).as_posix(),
            "status": status,
            "video_note_path": "",
            "error": "",
            "updated_at": utc_now_iso(),
        }

    @staticmethod
    def _key(transcript_path: Path) -> str:
        return str(transcript_path.expanduser().resolve())
