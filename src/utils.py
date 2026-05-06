from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any


DEFAULT_TRANSCRIPTION_PROMPT = (
    "Transcribe el audio de forma literal. Conserva el idioma original, "
    "no resumas, no omitas detalles y no agregues explicaciones."
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_path_part(value: str, fallback: str = "course") -> str:
    cleaned = value.strip().replace("/", "-").replace("\\", "-")
    cleaned = re.sub(r'[\x00-\x1f<>:"|?*]+', "-", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip(" .-")
    return cleaned or fallback


def path_to_posix(path: Path | str) -> str:
    return Path(path).as_posix()


def megabytes_to_bytes(value: int | float) -> int:
    return int(float(value) * 1024 * 1024)


def truncate_error(error: BaseException | str, limit: int = 2000) -> str:
    text = str(error)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def load_config(config_path: Path | None) -> dict[str, Any]:
    if config_path is None:
        return {}

    path = config_path.expanduser()
    if not path.exists():
        return {}

    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "pyyaml no está instalado. Ejecuta: pip install -r requirements.txt"
        ) from exc

    with path.open("r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"El archivo de configuración debe ser un objeto YAML: {path}")

    return data


def config_get(config: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
