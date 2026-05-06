from __future__ import annotations

from pathlib import Path
import os
from typing import Any

try:
    from .utils import DEFAULT_TRANSCRIPTION_PROMPT, config_get
except ImportError:
    from utils import DEFAULT_TRANSCRIPTION_PROMPT, config_get


def build_transcription_prompt(config: dict[str, Any]) -> str:
    base_prompt = (
        config_get(config, "transcription", "base_prompt")
        or config_get(config, "transcription", "prompt")
        or DEFAULT_TRANSCRIPTION_PROMPT
    )

    sections = [str(base_prompt).strip()]

    language = config_get(config, "profile", "language")
    if language and str(language).strip().lower() != "auto":
        sections.append(f"Expected language / Idioma esperado:\n{str(language).strip()}")

    course_context = config_get(config, "transcription", "course_context")
    if course_context and str(course_context).strip():
        sections.append(f"Course context / Contexto del curso:\n{str(course_context).strip()}")

    proper_names = _normalize_prompt_list(config_get(config, "transcription", "proper_names", default=[]))
    if proper_names:
        sections.append("Proper names / Nombres propios:\n" + _format_prompt_list(proper_names))

    glossary_terms = _normalize_prompt_list(config_get(config, "transcription", "glossary_terms", default=[]))
    if glossary_terms:
        sections.append("Glossary / Glosario:\n" + _format_prompt_list(glossary_terms))

    preserve = _normalize_prompt_list(config_get(config, "transcription", "preserve", default=[]))
    if preserve:
        sections.append("Preserve / Preservar:\n" + _format_prompt_list(preserve))

    return "\n\n".join(section for section in sections if section).strip()


def _normalize_prompt_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    if isinstance(value, dict):
        items = []
        for key, item_value in value.items():
            if item_value is None or str(item_value).strip() == "":
                items.append(str(key).strip())
            else:
                items.append(f"{str(key).strip()}: {str(item_value).strip()}")
        return [item for item in items if item]

    if not isinstance(value, list):
        text = str(value).strip()
        return [text] if text else []

    items: list[str] = []
    for item in value:
        if isinstance(item, dict):
            items.extend(_normalize_prompt_list(item))
            continue

        text = str(item).strip()
        if text:
            items.append(text)

    return items


def _format_prompt_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


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
