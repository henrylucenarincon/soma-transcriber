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


class Manifest:
    def __init__(self, path: Path, records: dict[str, dict[str, Any]] | None = None) -> None:
        self.path = path
        self.records: dict[str, dict[str, Any]] = records or {}

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        path = path.expanduser()
        if not path.exists():
            return cls(path=path)

        with path.open("r", encoding="utf-8") as manifest_file:
            raw_data = json.load(manifest_file)

        if isinstance(raw_data, dict) and "files" in raw_data and isinstance(raw_data["files"], dict):
            records = raw_data["files"]
        elif isinstance(raw_data, dict):
            records = raw_data
        elif isinstance(raw_data, list):
            records = {
                str(item.get("original_path")): item
                for item in raw_data
                if isinstance(item, dict) and item.get("original_path")
            }
        else:
            raise ValueError(f"Formato de manifest inválido: {path}")

        return cls(path=path, records=records)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as manifest_file:
            json.dump(self.records, manifest_file, ensure_ascii=False, indent=2)
            manifest_file.write("\n")

    def get_record(self, original_path: Path) -> dict[str, Any] | None:
        return self.records.get(self._key(original_path))

    def ensure_pending(self, original_path: Path, relative_path: Path | str) -> dict[str, Any]:
        key = self._key(original_path)
        if key not in self.records:
            self.records[key] = self._base_record(
                original_path=original_path,
                relative_path=relative_path,
                status=STATUS_PENDING,
            )
        return self.records[key]

    def mark_processing(
        self,
        original_path: Path,
        relative_path: Path | str,
        transcript_path: Path,
        audio_path: Path,
    ) -> dict[str, Any]:
        return self._upsert(
            original_path=original_path,
            relative_path=relative_path,
            status=STATUS_PROCESSING,
            transcript_path=str(transcript_path),
            audio_path=str(audio_path),
            chunks_count=0,
            error="",
        )

    def mark_completed(
        self,
        original_path: Path,
        relative_path: Path | str,
        transcript_path: Path,
        audio_path: Path,
        chunks_count: int,
    ) -> dict[str, Any]:
        return self._upsert(
            original_path=original_path,
            relative_path=relative_path,
            status=STATUS_COMPLETED,
            transcript_path=str(transcript_path),
            audio_path=str(audio_path),
            chunks_count=chunks_count,
            error="",
        )

    def mark_failed(
        self,
        original_path: Path,
        relative_path: Path | str,
        error: BaseException | str,
        transcript_path: Path | None = None,
        audio_path: Path | None = None,
        chunks_count: int | None = None,
    ) -> dict[str, Any]:
        current = self.get_record(original_path) or {}
        return self._upsert(
            original_path=original_path,
            relative_path=relative_path,
            status=STATUS_FAILED,
            transcript_path=str(transcript_path or current.get("transcript_path", "")),
            audio_path=str(audio_path or current.get("audio_path", "")),
            chunks_count=chunks_count if chunks_count is not None else int(current.get("chunks_count", 0) or 0),
            error=truncate_error(error),
        )

    def _upsert(
        self,
        original_path: Path,
        relative_path: Path | str,
        status: str,
        transcript_path: str,
        audio_path: str,
        chunks_count: int,
        error: str,
    ) -> dict[str, Any]:
        if status not in VALID_STATUSES:
            raise ValueError(f"Status inválido para manifest: {status}")

        key = self._key(original_path)
        record = self.records.get(key) or self._base_record(original_path, relative_path, status)
        record.update(
            {
                "original_path": key,
                "relative_path": Path(relative_path).as_posix(),
                "status": status,
                "transcript_path": transcript_path,
                "audio_path": audio_path,
                "chunks_count": chunks_count,
                "error": error,
                "updated_at": utc_now_iso(),
            }
        )
        self.records[key] = record
        return record

    @staticmethod
    def _base_record(
        original_path: Path,
        relative_path: Path | str,
        status: str,
    ) -> dict[str, Any]:
        return {
            "original_path": str(original_path.expanduser().resolve()),
            "relative_path": Path(relative_path).as_posix(),
            "status": status,
            "transcript_path": "",
            "audio_path": "",
            "chunks_count": 0,
            "error": "",
            "updated_at": utc_now_iso(),
        }

    @staticmethod
    def _key(original_path: Path) -> str:
        return str(original_path.expanduser().resolve())
