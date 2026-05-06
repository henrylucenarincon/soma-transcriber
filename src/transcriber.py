from __future__ import annotations

from pathlib import Path
import os
from typing import Any


def transcribe_audio_file(audio_path: Path, model: str, prompt: str | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Crea un archivo .env o exporta la variable de entorno."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai no está instalado. Ejecuta: pip install -r requirements.txt"
        ) from exc

    audio_path = audio_path.expanduser()
    if not audio_path.exists():
        raise FileNotFoundError(f"No existe el audio a transcribir: {audio_path}")

    client = OpenAI(api_key=api_key)
    request: dict[str, Any] = {
        "model": model,
        "response_format": "text",
    }
    if prompt:
        request["prompt"] = prompt

    with audio_path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(file=audio_file, **request)

    if isinstance(result, str):
        return result.strip()

    text = getattr(result, "text", None)
    if isinstance(text, str):
        return text.strip()

    return str(result).strip()
