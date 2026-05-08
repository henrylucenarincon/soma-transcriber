# Estado del Proyecto

Versión actual: V2.3 / V1.5.6

Estado: pipeline V1 completamente validado. Study Pack Builder V2 migrado de OpenAI a Claude Sonnet 4.6 con prompt caching. Soma Studio rediseñado con FastAPI como interfaz local moderna. Pendiente: regenerar course-pack completo con la nueva configuración y validar calidad de output.

Soma Transcriber ya tiene una primera base funcional para detectar videos, extraer audio, dividir archivos grandes, transcribir con OpenAI API y escribir resultados organizados. La versión V1.1 agregó controles para reducir riesgo operativo y costos accidentales antes de ejecutar transcripciones reales. En V1.3 se ejecutó el primer test real controlado con 1 video y fue exitoso.

## Funcionalidades Implementadas

- CLI local en Python.
- Flags disponibles: `--input`, `--output`, `--course-name`, `--model`, `--force`, `--dry-run`, `--max-videos`, `--list-videos`, `--config`.
- Scan recursivo de videos con extensiones `.mp4`, `.mov`, `.mkv`, `.webm`, `.m4v`, `.ts`.
- Orden natural de módulos y videos numerados.
- Extracción de audio con FFmpeg a MP3 mono, 16000 Hz, 64k.
- División de audios con FFmpeg/FFprobe por tamaño y por duración máxima configurable.
- Eliminación de la dependencia funcional de audio en Python para evitar problemas de `audioop` en Python 3.13.
- Transcripción con OpenAI API.
- Prompt configurable desde `config.yaml`.
- Perfiles universales de configuración por curso con `--config`.
- Construcción de prompt final desde prompt base, contexto, idioma, nombres propios, glosario y reglas de preservación.
- Transcripciones Markdown con metadata.
- Formato de párrafos en Markdown para mejorar legibilidad sin resumir ni reescribir.
- Manifest en `data/manifest.json`.
- Saltar archivos ya `completed` salvo que se use `--force`.
- Índice CSV en `output/index.csv`.
- Soma Studio rediseñado con FastAPI en `app/server.py` — interfaz local moderna con dark theme minimal.
- Streaming de output en tiempo real desde CLI hacia la UI vía `StreamingResponse`.
- Tabs: Transcripción (listar, dry-run, transcribir, reintentar), Study Pack (por fase), Estado (manifest, índice).
- Selector nativo de carpetas macOS con `osascript`.
- Confirmación antes de procesar sin límite de videos o módulo.
- Interfaz Streamlit legacy (`app/streamlit_app.py`) conservada como fallback.
- Dropdown inteligente de cursos detectados automáticamente desde `output/transcripts/`.
- Filtro de módulos en tab Study Pack — procesa solo un módulo seleccionado.
- Sistema de jobs con reconexión: recargar la página reconecta al proceso activo.
- Barra de progreso por fases con pasos visuales (○ → ◉ → ✓) y porcentaje en tiempo real.
- Fix de buffering Python con `PYTHONUNBUFFERED=1` para stream en tiempo real.
- `.claude/settings.json` con allowlist de permisos para reducir prompts de aprobación.
- Study Pack Builder V2.0 en `src/study_pack.py`.
- Generación por fases: `video-notes`, `module-summaries`, `course-pack` y `all`.
- Prompts V2.0.1 para video-notes más profundas, accionables y útiles para IA.
- Prompts V2.0.2 para tratar clases introductorias, onboarding, cierre o mapa como arquitectura del módulo sin inventar principios ni ejemplos.
- Detección V2.0.3 de clases introductorias por título/ruta para activar instrucciones especiales de mapa del módulo.
- Prompts V2.0.4 para evitar arquitectura del módulo en clases operativas y forzar framework operativo real o implícito.
- Prompts V2.0.5 para `module summaries` más profundos, conectados y útiles como metodología aplicable por IA.
- Prompts V2.0.6 para corregir superficialidad de `module summaries` y producir sistemas operativos de módulo con checklist, reglas, frameworks y conexiones entre lecciones.
- Prompts V2.0.7 para corregir el riesgo de relleno genérico en `module summaries`; ejemplos, frameworks, principios y reglas deben estar respaldados por `video-notes`.
- Prompts V2.0.8 para corregir omisiones de lecciones/frameworks en `module summaries` mediante Coverage Matrix obligatorio y cobertura completa de `video-notes`.
- Prompts V2.1 específicos por archivo maestro del Course Pack para mejorar `03_CORE_PRINCIPLES`, `04_FRAMEWORKS`, `07_APPLICATION_GUIDE`, `08_AI_STUDY_CONTEXT` y `09_MASTER_PROMPT_FOR_AI`.
- Course Pack Evidence Layer V2.2 en `output/study/{course-name}/_course_pack_evidence/`.
- Inventarios V2.2 de cobertura, principios, frameworks, conceptos, ejemplos, aplicaciones y tareas de IA.
- Quality Report V2.2 en `99_QUALITY_REPORT.md` con validación simple de cobertura por módulos.
- V2.2.1 reduce prompts gigantes en la fase `course-pack`: los archivos maestros usan `_course_pack_evidence/` como fuente principal y reciben `module_notes` solo como índice de cobertura.
- V2.3 migra el Study Pack Builder de OpenAI a Claude Sonnet 4.6 con prompt caching.
- El prompt caching cachea el system prompt (1996 chars) compartido por todas las llamadas de análisis, reduciendo costos en ciclos de generación masiva.
- El modelo por defecto del Study Pack cambia a `claude-sonnet-4-6` (configurable con `--model` o `study.model` en YAML).
- La transcripción de audio (V1) sigue con OpenAI Whisper como única opción para audio.
- Documentación de handoff en `docs/HANDOFF_FOR_NEXT_AI.md` para continuar el desarrollo con otra IA sin perder contexto.
- Manifest V2 privado en `data/study_manifest.json`.
- Configuración V2 mediante sección `study` en YAML.
- Chunking de texto por caracteres para analizar transcripciones largas.
- Salidas privadas en `output/study/{course-name}/`.
- `.gitignore` configurado para excluir `.env`, `.tmp/`, `data/`, `output/`, `outputs/`, videos, audios y archivos pesados.

## Validaciones Ejecutadas

```bash
python3 -m compileall src app
python3 src/main.py --help
python3 src/study_pack.py --help
python3 -c "from app.server import app; print(f'{len(app.routes)} rutas OK')"
```

## Probado

- Primer test real con 1 video usando OpenAI API.
- Resultado del primer test: procesado 1, fallidos 0.
- Módulo 1 real: 13 `completed`, 0 `failed`.
- Primer curso completo: Victor Heras - Marca Personal 5.0, 90 `completed`, 0 `failed`.
- Prueba real controlada de V2 con 2 `video-notes` del módulo 3.
- Prueba real de `module summary` del módulo 3.
- Course Pack completo generado técnicamente con V2.2.1.
- Compilación y carga de imports de V2.3 (Claude) validada.
- Servidor FastAPI levantado y respondiendo en `http://127.0.0.1:8899`.

## Probado en V1.5.6

- Módulo 3 completo (15 lecciones) generado con Claude Sonnet 4.6 — ~80s/nota.
- Calidad validada: nota "Estructura ViralCopy" contiene duraciones exactas, ejemplos verbatim, instrucciones concretas para IA.
- Barra de progreso funcionando en tiempo real tras fix de buffering.
- Filtro de módulos validado: proceso solo procesó módulo 3 correctamente.
- Sistema de reconexión validado: recargar página reconecta al job activo.

## Todavía No Probado

- Course-pack completo (90 video-notes + 11 module-notes + evidence + master docs) regenerado con Claude.
- Estimación de costo real de Claude por ciclo completo del curso.
- Uso real del Study Pack con Claude.ai Projects para generar guiones.

## Próximo Hito Recomendado

Generar el Study Pack completo del curso (fase all, sin límite, con force) y validar los documentos maestros `08_AI_STUDY_CONTEXT.md` y `09_MASTER_PROMPT_FOR_AI.md`.

## Riesgos Actuales

- Ejecutar un curso completo por accidente sin `--max-videos` (la UI pide confirmación pero la CLI no bloquea).
- Usar `--force` sin intención y duplicar costos de API.
- Exponer `OPENAI_API_KEY` o `ANTHROPIC_API_KEY` si se versiona `.env` por error.
- Versionar transcripciones privadas, audios o videos si se cambia `.gitignore`.

## Hallazgos Históricos

- V1.3: primer Markdown quedó como bloque único → corregido con párrafos.
- V1.3.3: `input_too_large` en audio largo → corregido con chunking por duración.
- V1.3.4: `audioop` removido en Python 3.13 → reemplazado por FFmpeg/FFprobe.
- V1.3.5: módulo 1 completo 13/13, video 12 con 3 chunks.
- V2.0.1: primeras `video-notes` demasiado resumidas → prompts reforzados.
- V2.0.5: primer `module summary` demasiado genérico → Module Operating System.
