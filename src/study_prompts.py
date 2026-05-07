from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


VIDEO_NOTE_TEMPLATE = """# {video_title}

**Curso:** {course_name}
**Módulo:** {module_path}
**Fuente:** {relative_path}
**Tipo:** Nota de estudio por video

## Propósito de la lección

## Ideas principales

## Conceptos explicados

## Frameworks o estructuras mencionadas

## Ejemplos y casos usados

## Reglas prácticas / instrucciones accionables

## Errores, advertencias o matices

## Aplicaciones posibles

## Referencias internas
- Transcript: {relative_path}
"""


MODULE_SUMMARY_TEMPLATE = """# Módulo: {module_name}

## Resumen del módulo

## Lecciones incluidas

## Principios del módulo

## Frameworks del módulo

## Conceptos clave

## Ejemplos importantes

## Cómo se aplica este módulo

## Preguntas que este módulo ayuda a responder
"""


GLOBAL_DOCUMENTS: dict[str, dict[str, str]] = {
    "00_STUDY_PACK_INDEX.md": {
        "title": "Study Pack Index",
        "goal": (
            "Crear un índice del Study Pack: qué contiene, cómo usarlo con una IA, "
            "lista de documentos y nota de privacidad."
        ),
    },
    "01_COURSE_MAP.md": {
        "title": "Course Map",
        "goal": (
            "Crear el mapa completo del curso por módulos y lecciones, explicar el flujo lógico "
            "y qué se aprende en cada bloque."
        ),
    },
    "02_MODULE_SUMMARIES.md": {
        "title": "Module Summaries",
        "goal": "Consolidar los resúmenes de módulos en un documento unificado.",
    },
    "03_CORE_PRINCIPLES.md": {
        "title": "Core Principles",
        "goal": (
            "Extraer principios centrales del curso. Cada principio debe incluir nombre, explicación, "
            "dónde aparece, cómo aplicarlo y qué errores evita."
        ),
    },
    "04_FRAMEWORKS.md": {
        "title": "Frameworks",
        "goal": (
            "Extraer frameworks, métodos, estructuras o modelos mentales. Cada uno debe incluir "
            "para qué sirve, pasos/componentes, cuándo usarlo y referencias internas."
        ),
    },
    "05_KEY_CONCEPTS.md": {
        "title": "Key Concepts",
        "goal": (
            "Crear un glosario conceptual según el curso, sin definiciones externas, incluyendo "
            "relaciones entre conceptos."
        ),
    },
    "06_EXAMPLES_AND_CASES.md": {
        "title": "Examples and Cases",
        "goal": (
            "Organizar ejemplos y casos mencionados, explicando qué principio ilustra cada uno "
            "sin copiar fragmentos largos."
        ),
    },
    "07_APPLICATION_GUIDE.md": {
        "title": "Application Guide",
        "goal": (
            "Explicar cómo aplicar el curso a proyectos reales con plantillas, preguntas de diagnóstico "
            "y formas de convertir conocimiento en tareas."
        ),
    },
    "08_AI_STUDY_CONTEXT.md": {
        "title": "AI Study Context",
        "goal": (
            "Crear un documento para darle a una IA. Debe instruirla a estudiar el curso usando el Study Pack, "
            "evitar respuestas genéricas, priorizar la metodología del curso, citar internamente cuando sea útil "
            "y preguntar si falta contexto."
        ),
    },
    "09_MASTER_PROMPT_FOR_AI.md": {
        "title": "Master Prompt for AI",
        "goal": (
            "Crear un prompt maestro listo para copiar y pegar, con rol de la IA, contexto del curso, reglas de uso, "
            "cómo responder, límites y prohibición de reproducir largas partes del curso."
        ),
    },
}


@dataclass(frozen=True)
class StudySettings:
    model: str
    output_language: str = "same-as-course"
    max_chars_per_analysis_chunk: int = 25000
    include_short_quotes: bool = False
    quote_max_words: int = 20
    avoid_external_knowledge: bool = True


def build_system_prompt(settings: StudySettings) -> str:
    quote_rule = (
        f"Puedes incluir citas literales muy breves de máximo {settings.quote_max_words} palabras."
        if settings.include_short_quotes
        else "No incluyas citas literales salvo que sea estrictamente necesario."
    )
    external_rule = (
        "No agregues teoría externa, datos externos ni recomendaciones que no salgan del material."
        if settings.avoid_external_knowledge
        else "Prioriza el material del curso; usa conocimiento externo solo si se pide explícitamente."
    )
    return "\n".join(
        [
            "Eres un analista de cursos para crear materiales de estudio privados para IA.",
            "Trabaja con síntesis, principios, frameworks, conceptos, ejemplos y referencias internas.",
            "No reproduzcas transcripciones completas ni fragmentos largos del curso.",
            "Parafrasea con fidelidad. No inventes contenido.",
            external_rule,
            quote_rule,
            f"Idioma de salida preferido: {settings.output_language}.",
        ]
    )


def build_video_note_prompt(
    *,
    course_name: str,
    module_path: str,
    video_title: str,
    relative_path: Path,
    transcript_chunk: str,
    chunk_index: int,
    chunks_count: int,
    settings: StudySettings,
) -> str:
    chunk_notice = (
        f"Esta es la parte {chunk_index} de {chunks_count} de una transcripción larga. "
        "Extrae solo lo que aparezca en esta parte."
        if chunks_count > 1
        else "Esta transcripción entra en una sola parte."
    )
    return f"""{build_system_prompt(settings)}

Tarea: crear una nota de estudio por video a partir de una transcripción literal.

{chunk_notice}

Curso: {course_name}
Módulo: {module_path or "Sin módulo"}
Video: {video_title}
Fuente interna: {relative_path.as_posix()}

Estructura obligatoria:
{VIDEO_NOTE_TEMPLATE.format(
    video_title=video_title,
    course_name=course_name,
    module_path=module_path or "Sin módulo",
    relative_path=relative_path.as_posix(),
)}

Reglas:
- No copies largos fragmentos textuales.
- No resumas de forma genérica: conserva los matices del contenido.
- No agregues teoría externa.
- Si algo no está claro en la transcripción, dilo.
- Usa referencias internas al transcript cuando sea útil.

Transcripción a analizar:
<<<TRANSCRIPT_CHUNK
{transcript_chunk}
TRANSCRIPT_CHUNK>>>
"""


def build_video_note_merge_prompt(
    *,
    course_name: str,
    module_path: str,
    video_title: str,
    relative_path: Path,
    partial_notes: list[str],
    settings: StudySettings,
) -> str:
    joined_notes = "\n\n---\n\n".join(partial_notes)
    return f"""{build_system_prompt(settings)}

Tarea: unir notas parciales de una misma lección en una sola nota de estudio clara.

Curso: {course_name}
Módulo: {module_path or "Sin módulo"}
Video: {video_title}
Fuente interna: {relative_path.as_posix()}

Usa exactamente esta estructura:
{VIDEO_NOTE_TEMPLATE.format(
    video_title=video_title,
    course_name=course_name,
    module_path=module_path or "Sin módulo",
    relative_path=relative_path.as_posix(),
)}

Reglas:
- Integra ideas repetidas sin perder matices importantes.
- No agregues teoría externa.
- No copies fragmentos largos.
- Mantén referencias internas al transcript.

Notas parciales:
<<<PARTIAL_NOTES
{joined_notes}
PARTIAL_NOTES>>>
"""


def build_module_summary_prompt(
    *,
    course_name: str,
    module_name: str,
    video_notes: list[tuple[str, str]],
    settings: StudySettings,
) -> str:
    notes_text = "\n\n---\n\n".join(
        f"Fuente: {relative_path}\n\n{content}" for relative_path, content in video_notes
    )
    return f"""{build_system_prompt(settings)}

Tarea: crear un resumen de módulo usando notas de estudio por video.

Curso: {course_name}
Módulo: {module_name}

Usa exactamente esta estructura:
{MODULE_SUMMARY_TEMPLATE.format(module_name=module_name)}

Reglas:
- Sintetiza el módulo sin copiar largas partes del curso.
- Mantén el significado de las notas.
- No agregues teoría externa.
- Incluye lecciones y referencias internas cuando ayuden a ubicar ideas.

Notas por video:
<<<VIDEO_NOTES
{notes_text}
VIDEO_NOTES>>>
"""


def build_course_document_prompt(
    *,
    course_name: str,
    document_filename: str,
    module_notes: list[tuple[str, str]],
    video_notes_index: list[str],
    settings: StudySettings,
) -> str:
    if document_filename not in GLOBAL_DOCUMENTS:
        raise ValueError(f"Documento global desconocido: {document_filename}")

    definition = GLOBAL_DOCUMENTS[document_filename]
    modules_text = "\n\n---\n\n".join(
        f"Fuente: {relative_path}\n\n{content}" for relative_path, content in module_notes
    )
    lessons_text = "\n".join(f"- {item}" for item in video_notes_index)
    return f"""{build_system_prompt(settings)}

Tarea: {definition["goal"]}

Curso: {course_name}
Documento a generar: {document_filename}
Título sugerido: {definition["title"]}

Reglas:
- Usa las notas del curso como fuente principal.
- No incluyas transcripciones completas.
- No copies fragmentos largos.
- No agregues teoría externa.
- Cuando sea útil, referencia módulo/lección usando las fuentes internas disponibles.

Índice de lecciones disponibles:
{lessons_text}

Notas de módulos:
<<<MODULE_NOTES
{modules_text}
MODULE_NOTES>>>
"""
