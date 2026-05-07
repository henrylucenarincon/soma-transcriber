from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import unicodedata


INTRODUCTORY_LESSON_TERMS = (
    "introduccion",
    "intro",
    "bienvenida",
    "overview",
    "mapa",
    "onboarding",
    "cierre",
    "conclusion",
)


VIDEO_NOTE_TEMPLATE = """# {video_title}

**Curso:** {course_name}
**Módulo:** {module_path}
**Fuente:** {relative_path}
**Tipo:** Nota de estudio por video

## 1. Resumen fiel de la lección

Explicar qué enseña la lección sin agregar teoría externa.
Si esta clase es introductoria, bienvenida, onboarding, cierre o mapa del módulo,
explica su función dentro del curso y la arquitectura que presenta.

## 2. Principio central extraído o función de la lección

Identificar el principio más importante de la clase, o la función de la lección dentro
del curso si es introductoria.
Si la clase es introductoria, no inventes un principio central. Explica la función de
la clase dentro del curso.
No elijas como principio central un tema secundario si la clase solo presenta el mapa
completo del módulo.
Debe incluir:
- Nombre del principio o función de la lección
- Explicación
- Por qué importa dentro del curso
- Qué problema resuelve

## 3. Mecanismo explicado

Explicar cómo funciona la idea según la clase.
Debe responder:
- Qué causa qué
- Qué condición activa el resultado
- Qué relación hay entre conceptos
- Qué lógica usa el profesor

## 4. Framework operativo

Si la lección es introductoria/mapa, usar "Arquitectura del módulo" con:
- Bloques o lecciones anunciadas
- Función de cada bloque
- Por qué el orden importa
- Resultado esperado del módulo

Si la lección es operativa/no introductoria, usar "Framework operativo" con:
- Nombre del framework o principio operativo
- Paso 1
- Paso 2
- Paso 3
- Pasos adicionales si aplica
- Condiciones de uso
- Resultado esperado

Para una clase introductoria/mapa, la arquitectura del módulo puede incluir:
- Bloque 1
- Bloque 2
- Bloque 3
- Bloques adicionales si aparecen
- Qué función cumple cada bloque
- Por qué el orden importa
- Resultado esperado del módulo
No reduzcas una arquitectura de módulo a tres pasos si la transcripción enumera más
bloques o lecciones. No uses "Arquitectura del módulo" en clases operativas.

## 5. Conceptos clave de esta lección

Lista de conceptos explicados según la clase.
Cada concepto debe tener definición breve basada solo en la transcripción.

## 6. Ejemplos usados por el profesor

Listar ejemplos, casos, analogías o comparaciones.
Solo listar ejemplos que aparezcan realmente en la transcripción.
No inventar ejemplos genéricos para llenar la sección.
Si no hay ejemplos, escribir: "No aparecen ejemplos concretos en esta lección."
Para cada ejemplo:
- Qué ejemplo es
- Qué idea ilustra
- Cómo se podría aplicar

## 7. Aplicación práctica

Explicar cómo aplicar la lección en un proyecto real.
Debe incluir:
- Cómo usarlo
- Cuándo usarlo
- Qué revisar antes de aplicarlo
- Qué resultado buscar

## 8. Implicaciones para creación de contenido, estrategia o ejecución

Aunque el curso no sea de marketing, adaptar esta sección al tema del curso.
Debe responder:
- Qué cambiaría en la forma de crear, decidir o ejecutar
- Qué debe priorizarse
- Qué debe evitarse

## 9. Errores que esta lección ayuda a evitar

Listar errores, falsas creencias, malas prácticas o confusiones que la lección corrige.

## 10. Instrucciones para una IA

Escribir instrucciones concretas para una IA que deba usar esta lección.
Ejemplo:
- Cuando el usuario pida X, recuerda Y.
- No respondas de forma genérica sobre Z.
- Prioriza este principio antes que consejos externos.
- Pregunta por A si falta contexto.
Para clases introductorias, la IA debe usar esta nota como mapa de navegación del
módulo, no como regla operativa única.

## 11. Referencias internas

- Transcript: {relative_path}
"""


MODULE_SUMMARY_TEMPLATE = """# Módulo: {module_name}

## 0. Coverage Matrix del módulo

Esta sección debe listar TODAS las video-notes detectadas.
Para cada lección:
- Lección:
- Función dentro del módulo:
- Componente/framework asociado:
- Secciones donde se usa:
- Estado de cobertura: cubierta / insuficiente

Regla:
Ninguna lección detectada puede quedar fuera del Coverage Matrix.

## 1. Tesis central del módulo

Explica en 1-3 párrafos cuál es la idea profunda del módulo.
No debe ser una descripción genérica.
Debe responder:
- Qué problema real resuelve este módulo
- Qué transformación produce en quien lo estudia
- Qué cambio de pensamiento exige
- Qué lógica general sostiene todo el módulo

Evita frases débiles como: "Este módulo trata sobre crear contenido atractivo".
Produce una tesis fuerte, específica y metodológica basada solo en las video-notes.
Debe explicar la lógica completa del módulo en términos operativos y conectar:
marca/congruencia -> idea -> validación -> referencia -> tensión/controversia -> formato
-> estructura -> retención -> acción -> medición, solo cuando esos elementos estén respaldados
por las video-notes.

## 2. Sistema operativo del módulo

Extraer la metodología completa como sistema.
No limitarse a una lista corta si las video-notes contienen más piezas.
Debe incluir todos los componentes relevantes respaldados por las video-notes.

Formato:

### 2.1 Componente 1: ...
- Qué es
- Lección o video-note que lo respalda
- Para qué sirve
- Cuándo se aplica
- Qué pasa si se ignora
- Con qué otro componente se conecta

### 2.2 Componente 2: ...

Continuar con todos los componentes relevantes detectados.

## 3. Secuencia de aplicación

Convertir el módulo en una secuencia práctica.
Debe responder:
- Qué se hace primero
- Qué se hace después
- Qué no se debe hacer antes de tiempo
- Qué depende de qué
- Qué se rompe si se salta un paso

Debe ser más detallado que una lista de 5 pasos si el módulo contiene más componentes.

## 4. Función de cada lección dentro del sistema

Listar cada lección detectada en las video-notes y explicar su función dentro de la metodología.

Formato:
- Lección: [nombre de la lección]
  - Función dentro del módulo:
  - Qué aporta al sistema:
  - Qué error ayuda a evitar:
  - Cómo se conecta con la siguiente lección:

No limitarse a repetir títulos.

## 5. Principios profundos del módulo

Extraer principios que realmente gobiernan la metodología.

Cada principio debe incluir:
- Nombre del principio
- Lecciones que lo respaldan
- Explicación
- Por qué importa
- Cómo se aplica
- Qué error evita
- Señales de mala aplicación

Evitar principios obvios o genéricos. Extraer principios con poder operativo.

## 6. Mecanismos causa-efecto

Explicar relaciones de causa y efecto presentes en el módulo.

Formato:
- Si X ocurre, entonces Y pasa porque...
- X aumenta/disminuye Y porque...
- X falla cuando falta Y...

Esta sección debe ayudar a una IA a razonar, no solo a recordar.

## 7. Frameworks y herramientas del módulo

Consolidar todos los frameworks explícitos o implícitos detectados.
No limitar la lista a 3-5 frameworks.
Incluir todas las herramientas, metodologías, subestructuras, criterios operativos,
métricas o componentes narrativos detectados en las video-notes.

Si una herramienta no es un framework formal, clasificarla como:
- framework
- herramienta
- subestructura
- criterio operativo
- métrica
- componente narrativo

Para cada elemento:
- Nombre
- Tipo
- Lecciones que lo respaldan
- Evidencia de la video-note
- Para qué sirve
- Cuándo usarlo
- Entradas necesarias
- Pasos/componentes
- Output esperado
- Errores comunes
- Cómo lo usaría una IA en una tarea real

Reglas:
- Si un framework es implícito, debe ser una inferencia directa de una o más video-notes
- No inventar frameworks externos
- No incluir frameworks sin lecciones que los respalden
- No omitir frameworks o herramientas relevantes que aparezcan en las video-notes

## 8. Conceptos clave y mapa de relaciones

No solo definir conceptos. Explicar cómo se relacionan.

Formato:
- Concepto A:
  - Definición según el curso
  - Se relaciona con B porque...
  - Es previo a C porque...
  - Se aplica cuando...

## 9. Evidencia interna: ejemplos, casos y referencias detectadas

Consolidar ejemplos, casos o referencias reales mencionados en las video-notes.

Reglas:
- Solo incluir ejemplos, casos o referencias que aparezcan explícitamente en las video-notes
- No inventar ejemplos genéricos
- No crear ejemplos hipotéticos
- No usar conocimiento externo
- No afirmar que no hay ejemplos si alguna video-note sí contiene ejemplos

Para cada ejemplo:
- Ejemplo/caso/referencia:
- Lección o video-note donde aparece:
- Qué principio ilustra:
- Cómo puede usarse como referencia:
- Qué NO debe copiarse literalmente:

Si no hay ejemplos detectados, escribir:
"No se detectaron ejemplos concretos en las video-notes analizadas."

## 10. Reglas prácticas de aplicación

Convertir el módulo en reglas accionables.

Ejemplos de formato:
- Antes de escribir un guion, valida...
- No elijas formato antes de...
- Si la idea no pasa..., entonces...
- Usa controversia solo cuando...
- No uses tendencias si...
- Antes de publicar, revisa...
- Después de publicar, mide...

Las reglas deben salir de las video-notes.
Cada regla debe incluir:
- Regla:
- Basada en:
- Cuándo aplicarla:
- Qué evita:
- Cómo la usaría una IA:

## 11. Checklist operativo para IA

Crear un checklist que una IA debe seguir cuando use este módulo.
Debe cubrir todo el recorrido del módulo, no solo los primeros componentes.
Debe estar ordenado de forma secuencial.
Debe incluir validaciones antes de crear un guion, durante la creación y después de publicar.
Debe tener mínimo 12 ítems si el módulo contiene más de 10 lecciones.

Debe estar pensado para tareas reales como:
- crear guiones
- revisar ideas
- crear estrategia de contenido
- analizar una marca
- mejorar retención
- diseñar un calendario
- adaptar una referencia viral

Formato:
- [ ] Acción
  - Basado en:
  - Por qué importa:

Este checklist debe ser específico y no genérico.
Cada ítem debe estar basado en una lección o framework detectado.

## 12. Instrucciones para una IA

Escribir reglas de comportamiento para una IA que use este módulo.

Debe incluir:
- Qué debe hacer antes de responder
- Qué debe evitar
- Qué preguntas debe hacer si falta contexto
- Cómo debe usar los frameworks
- Cómo debe priorizar la metodología del curso por encima de consejos genéricos
- Cómo debe razonar cuando el usuario pida guiones, estrategia o contenido

## 13. Errores que el módulo ayuda a evitar

Listar errores concretos.
No escribir errores genéricos.

Formato:
- Error:
- Por qué ocurre:
- Qué parte del módulo lo corrige:
- Cómo detectarlo:
- Cómo corregirlo:

## 14. Preguntas que este módulo ayuda a responder

Separar por tipo:
- Preguntas estratégicas
- Preguntas creativas
- Preguntas de guion
- Preguntas de métricas
- Preguntas de diagnóstico
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


def is_introductory_lesson(video_title: str, relative_path: str = "") -> bool:
    text = _normalize_lesson_text(f"{video_title} {relative_path}")
    return any(term in text for term in INTRODUCTORY_LESSON_TERMS)


def _normalize_lesson_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(character for character in decomposed if not unicodedata.combining(character))
    return without_accents.casefold()


def _lesson_type_instruction(is_introductory: bool) -> str:
    if is_introductory:
        return (
            "Instrucción especial para esta lección:\n"
            "Esta lección es introductoria/mapa. En la sección 4 usa Arquitectura del módulo. "
            "No generes un framework operativo artificial. Trata la lección como una arquitectura del módulo "
            "o del curso. Prioriza explicar la función de la lección, el recorrido que presenta, los bloques "
            "que anuncia y cómo preparar a la IA para usar ese módulo."
        )

    return (
        "Instrucción especial para esta lección:\n"
        "Esta lección no parece introductoria. En la sección 4 NO uses Arquitectura del módulo. "
        "Extrae un Framework operativo real o implícito. Si no hay framework explícito, convierte la enseñanza "
        "en pasos accionables fieles a la transcripción, sin inventar elementos externos."
    )


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
            "Eres un analista de cursos que crea material de estudio operativo para IA.",
            "Tu objetivo no es hacer un resumen escolar: debes convertir el contenido en conocimiento aplicable.",
            "Extrae principios, mecanismos de causa-efecto, frameworks explícitos o implícitos, reglas de decisión, ejemplos y referencias internas.",
            "El resultado debe ayudar a una IA a ejecutar tareas siguiendo la metodología del curso y evitando respuestas genéricas.",
            "Cuando generes module summaries, tu tarea no es resumir superficialmente. Tu tarea es sintetizar la metodología del módulo para que otra IA pueda aplicarla.",
            "Cuando generes module summaries, no eres un resumidor. Eres un arquitecto de conocimiento para IA. Tu trabajo es convertir las notas del módulo en un sistema operativo aplicable.",
            "Cuando generes module summaries, tu prioridad es cobertura completa + fidelidad interna + utilidad operativa para IA. No sacrifiques lecciones por brevedad.",
            "No eres un generador de contenido genérico. Eres un arquitecto de conocimiento basado en evidencia interna. Tu tarea es convertir las notas disponibles en un sistema operativo fiel al curso. No rellenes huecos con conocimiento externo.",
            "Prioriza profundidad, especificidad y aplicabilidad.",
            "No reproduzcas transcripciones completas ni fragmentos largos del curso.",
            "Parafrasea con fidelidad. No inventes contenido.",
            "No rellenes secciones inventando ejemplos, frameworks o principios. Si algo no aparece, dilo claramente.",
            "No uses arquitectura del módulo en clases operativas. Solo úsala cuando la lección sea introductoria, bienvenida, overview, mapa, onboarding, cierre o conclusión.",
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
    is_introductory = is_introductory_lesson(video_title, relative_path.as_posix())
    lesson_type_instruction = _lesson_type_instruction(is_introductory)
    chunk_notice = (
        f"Esta es la parte {chunk_index} de {chunks_count} de una transcripción larga. "
        "Extrae solo lo que aparezca en esta parte."
        if chunks_count > 1
        else "Esta transcripción entra en una sola parte."
    )
    return f"""{build_system_prompt(settings)}

Tarea: crear una nota de estudio por video a partir de una transcripción literal.

La nota debe ser profunda, específica y accionable. Debe servir para que una IA estudie esta lección y luego aplique la metodología del curso en tareas reales.

{chunk_notice}

{lesson_type_instruction}

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
- No hagas una respuesta genérica: usa detalles concretos de la transcripción.
- No te quedes en resumen superficial: extrae principios, mecanismos, reglas y aplicaciones.
- Convierte ideas en reglas aplicables.
- Si no hay framework explícito, extrae el framework implícito a partir de la lógica de la clase.
- Si la lección es introductoria, bienvenida, cierre, onboarding o mapa del módulo, no fuerces un principio central estrecho.
- Para clases introductorias o mapas de módulo, identifica la función de la lección dentro del curso y explica la arquitectura del módulo.
- Si la lección no es introductoria, NO uses "Arquitectura del módulo"; extrae un "Framework operativo" real o implícito.
- Un framework implícito debe convertir la enseñanza en pasos accionables fieles a la transcripción.
- No inventes ejemplos genéricos para llenar la sección de ejemplos.
- No agregues teoría externa.
- No dejes secciones vacías. Si algo no aparece, escribe: "No aparece explícitamente en esta lección."
- Si algo no está claro en la transcripción, dilo sin inventar.
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
    is_introductory = is_introductory_lesson(video_title, relative_path.as_posix())
    lesson_type_instruction = _lesson_type_instruction(is_introductory)
    joined_notes = "\n\n---\n\n".join(partial_notes)
    return f"""{build_system_prompt(settings)}

Tarea: unir notas parciales de una misma lección en una sola nota de estudio profunda, específica y accionable.

{lesson_type_instruction}

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
- Elimina duplicados.
- Mantén profundidad operativa: principios, mecanismos, framework implícito o explícito, aplicaciones e instrucciones para IA.
- Convierte ideas en reglas aplicables cuando la transcripción lo permita.
- Si la lección es introductoria, bienvenida, cierre, onboarding o mapa del módulo, no fuerces un principio central estrecho.
- Para clases introductorias o mapas de módulo, identifica la función de la lección dentro del curso y explica la arquitectura del módulo.
- Si la lección no es introductoria, NO uses "Arquitectura del módulo"; extrae un "Framework operativo" real o implícito.
- Un framework implícito debe convertir la enseñanza en pasos accionables fieles a la transcripción.
- No inventes ejemplos genéricos para llenar la sección de ejemplos.
- No agregues teoría externa.
- No copies fragmentos largos.
- No dejes secciones vacías. Si algo no aparece, escribe: "No aparece explícitamente en esta lección."
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

Tarea: crear un Module Operating System usando notas de estudio por video.

No generes un resumen superficial. Se quiere una síntesis metodológica profunda del módulo.
Tu tarea es construir el sistema operativo del módulo para que otra IA pueda aplicarlo en tareas reales.
Debes extraer la lógica completa del módulo: la secuencia, los principios, los mecanismos, los frameworks, los ejemplos y las reglas de aplicación.
Este documento debe ser evidence-based. Solo puedes incluir elementos presentes en las video-notes. No rellenes con conocimiento general, ejemplos inventados, casos hipotéticos o frameworks no mencionados o no inferibles directamente desde las notas.
Este documento también debe ser coverage-based. Primero identifica todas las video-notes recibidas. Luego construye el Coverage Matrix. Después genera el sistema operativo del módulo. No termines el documento hasta que todas las video-notes estén cubiertas.
Si hay conflicto entre brevedad y profundidad, prioriza profundidad.
Si hay conflicto entre brevedad y cobertura, prioriza cobertura.
El resultado debe ser más largo y más útil que un resumen ejecutivo.

Curso: {course_name}
Módulo: {module_name}

Usa exactamente esta estructura:
{MODULE_SUMMARY_TEMPLATE.format(module_name=module_name)}

Reglas:
- Usa solo las video-notes como fuente.
- Primero identifica todas las video-notes recibidas.
- Construye el Coverage Matrix antes de desarrollar el sistema operativo.
- Sintetiza el módulo sin copiar largas partes del curso.
- Mantén el significado de las notas y conecta las lecciones entre sí.
- Integra todas las lecciones disponibles.
- Todas las lecciones detectadas deben aparecer al menos en Coverage Matrix, Función de cada lección, Sistema operativo del módulo y, cuando aplique, Frameworks / Checklist / Reglas prácticas.
- No termines el documento hasta que todas las video-notes estén cubiertas.
- Si una lección no encaja en un framework, crea un componente auxiliar o explica su función dentro del sistema.
- No omitas lecciones finales por falta de espacio.
- Explica la lógica completa que une las lecciones, no solo una lista de temas.
- Extrae el sistema operativo del módulo: secuencia de aplicación, principios, mecanismos recurrentes y frameworks explícitos o implícitos.
- No reduzcas el módulo a una lista corta si las video-notes contienen más componentes.
- No omitas frameworks, herramientas o estructuras detectadas en las video-notes.
- Consolida ejemplos desde las video-notes.
- No digas "no hay ejemplos" si alguna video-note contiene ejemplos, casos, analogías o comparaciones.
- No inventes ejemplos.
- No uses frases como "por ejemplo" para introducir casos que no aparezcan en las notas.
- No crees ejemplos hipotéticos.
- No uses nichos, marcas o plataformas no mencionadas en las notas salvo que aparezcan en las video-notes.
- Si una sección no tiene suficiente evidencia, dilo.
- Prioriza fidelidad sobre completar secciones.
- Si dudas entre ser completo o ser fiel, sé fiel.
- No conviertas conocimiento general de marketing en contenido del curso.
- Toda afirmación importante debe poder rastrearse a una video-note.
- No uses frases genéricas como "crear contenido atractivo" sin explicar el mecanismo.
- Convierte conceptos en reglas prácticas de aplicación.
- Genera instrucciones útiles para una IA que deba crear guiones, estrategias, calendarios, análisis o contenidos usando este módulo.
- No agregues teoría externa.
- No dejes secciones vacías. Si algo no aparece, escribe: "No aparece explícitamente en este módulo."
- Incluye lecciones y referencias internas cuando ayuden a ubicar ideas.

Antes de entregar, revisa internamente:
- ¿Incluí todas las lecciones detectadas?
- ¿Incluí la última lección?
- ¿Incluí todos los frameworks relevantes?
- ¿Los frameworks incluyen también formatos, calculadora, ViralCopy, ganchos, historia, moraleja, CTA y métricas si aparecen?
- ¿Expliqué cómo se conectan las ideas?
- ¿Convertí conceptos en reglas aplicables?
- ¿Le di a una IA instrucciones concretas para usar este módulo?
- ¿El checklist cubre todo el módulo?
- ¿Evité tesis genéricas?
- ¿Evité frases genéricas?
- ¿Evité inventar ejemplos?
- ¿Evité decir que no hay ejemplos si sí aparecen en las notas?
- ¿Cada afirmación importante puede rastrearse a una video-note?
- ¿Prioricé cobertura sobre brevedad?

No muestres esta autoevaluación como sección final; úsala para mejorar la respuesta.

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
- Mantén enfoque evidence-based: no agregues ejemplos, frameworks, conceptos o casos que no estén presentes en module_notes o video_notes_index.
- No incluyas transcripciones completas.
- No copies fragmentos largos.
- No agregues teoría externa.
- No rellenes huecos con conocimiento externo ni contenido genérico.
- Cuando sea útil, referencia módulo/lección usando las fuentes internas disponibles.

Índice de lecciones disponibles:
{lessons_text}

Notas de módulos:
<<<MODULE_NOTES
{modules_text}
MODULE_NOTES>>>
"""
