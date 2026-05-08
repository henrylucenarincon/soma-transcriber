# Log de Desarrollo

## 2026-05-06: Entrada Inicial V1

Se creó la base del proyecto Soma Transcriber como CLI local en Python para transcribir cursos en video. La V1 incluye:

- estructura `src/`
- scan recursivo de videos
- extracción de audio con FFmpeg
- chunking para audios mayores a 24 MB
- transcripción con OpenAI API
- Markdown con metadata
- `data/manifest.json`
- `output/index.csv`
- README inicial
- `.env.example`
- `config.example.yaml`
- `.gitignore`

La prioridad de la V1 fue lograr una transcripción literal ordenada, preservando la estructura del curso.

## 2026-05-06: Entrada V1.1

Se aplicaron mejoras de seguridad operativa y control de costos antes de ejecutar transcripciones reales:

- `.gitignore` actualizado con `.tmp/` y `data/`.
- Soporte para `--max-videos`.
- Soporte para `--list-videos`.
- `--dry-run` mejorado con conteo de videos procesables y saltados.
- Validación previa de FFmpeg.
- Validación previa de `OPENAI_API_KEY` solo para transcripción real.
- Prompt más fuerte en `config.example.yaml`.
- README actualizado con flujo recomendado.

## 2026-05-06: Entrada V1.2

Se creó la documentación viva del proyecto en `docs/`:

- contexto del proyecto
- estado actual
- arquitectura
- flujo de datos
- roadmap
- decisiones
- log de desarrollo
- prompts de Codex
- testing
- seguridad y privacidad
- runbook operativo
- tareas completadas y pendientes

La documentación viva queda como fuente principal de contexto para futuras tareas con Codex.

## 2026-05-06: Entrada V1.2.2

Se agregó soporte para archivos `.ts` porque el primer curso real detectado usa MPEG-TS.

- Se actualizó `.gitignore` para ignorar `*.ts` como archivos de video pesados.
- Se actualizó README y documentación viva para reflejar el nuevo formato soportado.
- No se ejecutó transcripción real.

## 2026-05-06: Entrada V1.2.3

Se corrigió el ordenamiento de módulos y videos para usar orden natural.

- Esto evita que `10`, `11` y `12` aparezcan antes de `2`.
- El orden natural se aplica sobre cada parte de la ruta relativa para respetar módulos y lecciones numeradas.
- No se ejecutó transcripción real.

## 2026-05-06: Entrada V1.3

Se ejecutó el primer test real controlado con 1 video.

- Resultado: procesado 1, fallidos 0.
- Se generó audio, `output/index.csv` y transcripción Markdown.
- La metadata quedó correcta y el estado fue `completed`.
- La transcripción fue literal, pero quedó como bloque único de texto.

## 2026-05-06: Entrada V1.3.1

Se agregó formato de párrafos para mejorar legibilidad sin alterar la transcripción literal.

- No se resume el contenido.
- No se reescribe el contenido.
- No se cambia el orden.
- Se conserva la metadata YAML del Markdown.
- No se ejecutó transcripción real durante este ajuste.

## 2026-05-06: Entrada V1.3.2

Se agregaron perfiles universales de configuración por curso.

- Se separó prompt base universal de contexto específico.
- Se agregó construcción de prompt final desde contexto, idioma, nombres propios, glosario y reglas de preservación.
- Se agregaron ejemplos genéricos para español, inglés, marketing, finanzas y trading.
- `configs/local/` queda reservado para perfiles reales privados.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.3.3

Se detectó error `input_too_large` en un video largo del módulo 1 real.

- El archivo fallido fue `12. Cómo tener tus primeros clientes sin resultados.ts`.
- El audio no necesariamente superó el límite por MB, pero sí el límite práctico de audio + instrucciones del modelo.
- Se agregó chunking preventivo por duración configurable con `audio.max_chunk_minutes`.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.3.4

Se detectó que la dependencia anterior para chunking fallaba en Python 3.13 por `audioop`/`pyaudioop`.

- Se reemplazó el chunking con librerías Python de audio por FFmpeg/FFprobe.
- FFprobe obtiene la duración del audio.
- FFmpeg exporta chunks MP3 con los nombres `chunk_001.mp3`, `chunk_002.mp3`, etc.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.3.5

Se reprocesó el módulo 1 completo.

- Resultado: 13/13 videos `completed`.
- El video 12 se dividió en 3 chunks.
- Se validó que FFmpeg/FFprobe resolvió el error `input_too_large`.
- `output/`, `data/` y las transcripciones privadas no deben versionarse.

## 2026-05-06: Entrada V1.5

Se agregó Soma Studio Local con Streamlit.

- La interfaz es personal/local.
- Ejecuta la CLI con `subprocess` y `sys.executable`.
- Permite listar videos, dry-run, transcribir y reintentar fallidos.
- Muestra estado local desde `output/index.csv` y resumen de `data/manifest.json`.
- Deja preparada una sección para Study Pack V2.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.1

Se mejoró la experiencia de Soma Studio Local.

- Se agregó selector local de carpetas para curso/output.
- Se mantiene input manual como respaldo.
- Se aclaró el comportamiento de `max_videos`.
- Se refuerza que `max_videos = 1` es recomendado para pruebas y `0` significa sin límite.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.2

Se corrigió el selector de carpetas en macOS.

- Se reemplazó la dependencia principal de `tkinter` por `osascript`/AppleScript en macOS.
- `tkinter` queda como fallback si el selector nativo no está disponible.
- El input manual queda como fallback final.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.3

Se corrigió el manejo de `session_state` en Soma Studio para seleccionar carpetas sin error en Streamlit.

- Las rutas seleccionadas usan keys internas separadas de las keys de los widgets.
- El input manual sigue funcionando como respaldo.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.4

Se corrigió la sincronización entre selector de carpetas y `text_input` en Soma Studio.

- El selector ahora actualiza las keys visibles del widget.
- Se guarda la última ruta seleccionada para confirmación visual.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.6

Se procesó completo el primer curso real.

- Resultado: 90/90 videos `completed`, 0 `failed`.
- Se corrigió el nombre de salida del curso a `Victor Heras - Marca Personal 5.0`.
- El `original_path` se mantiene apuntando a la ruta real del curso fuente.
- `output/` y `data/` siguen siendo privados y no se versionan.
- Próximo paso: V2 Study Pack para convertir transcripciones en conocimiento estudiable por IA.

## 2026-05-06: Entrada V2.0

Se agregó Study Pack Builder.

- Permite generar notas por video, resúmenes por módulo y documentos globales para IA.
- La implementación inicial vive en `src/study_pack.py`, `src/study_prompts.py`, `src/study_writer.py` y `src/study_manifest.py`.
- El flujo V2 trabaja desde transcripciones privadas hacia `output/study/`.
- No debe incluir transcripciones completas ni largos fragmentos verbatim dentro del Study Pack.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.1

Se mejoraron los prompts de Study Pack para generar `video-notes` más profundas y accionables.

- Las primeras pruebas reales de `video-notes` funcionaron técnicamente, pero quedaron demasiado resumidas.
- Las `video-notes` ahora deben extraer principios, mecanismos, frameworks implícitos, aplicaciones e instrucciones para IA.
- Los resúmenes de módulo también quedan preparados para consumir notas más profundas.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.2

Se ajustaron prompts para clases introductorias o mapas de módulo.

- Las clases introductorias, de bienvenida, onboarding, cierre o mapa ya no deben forzar principios centrales estrechos.
- Si una clase presenta el recorrido del módulo, la nota debe extraer la función de la lección y la arquitectura del módulo.
- Se reforzó que no deben inventarse principios, frameworks ni ejemplos cuando no aparecen explícitamente.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.3

Se agregó detección de clases introductorias por título/ruta.

- Las introducciones ahora se tratan como mapas o arquitectura del módulo.
- Se evita reducir una introducción a un framework operativo artificial.
- La detección soporta términos como introducción, intro, bienvenida, overview, mapa, onboarding, cierre y conclusión.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.4

Se separó el tratamiento de clases introductorias y operativas.

- Las introductorias usan arquitectura del módulo.
- Las operativas usan framework operativo real o implícito.
- Se corrigió el riesgo de usar arquitectura del módulo en clases operativas.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.5

Se mejoraron prompts de `module summaries`.

- El objetivo es generar síntesis metodológicas profundas y no resúmenes genéricos.
- Los resúmenes de módulo ahora deben conectar lecciones, extraer el sistema operativo del módulo y consolidar ejemplos desde las `video-notes`.
- También deben convertir conceptos en reglas prácticas e instrucciones útiles para IA.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.6

Se reforzaron los prompts de `module summaries` para convertirlos en Module Operating Systems.

- El objetivo es evitar resúmenes genéricos y producir síntesis metodológicas accionables para IA.
- El prompt ahora prioriza profundidad, especificidad y aplicabilidad sobre brevedad.
- Se agregó una autoevaluación interna para revisar lecciones, frameworks, conexiones, reglas aplicables y ejemplos antes de responder.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.7

Se reforzó el enfoque evidence-based para `module summaries`.

- Cada ejemplo, framework, principio o regla debe estar respaldado por `video-notes`.
- Se busca evitar ejemplos genéricos, casos hipotéticos, frameworks inventados o conocimiento externo.
- Los documentos globales del Study Pack también quedan preparados para mantener fidelidad a la evidencia interna.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.8

Se agregó enfoque coverage-based a los Module Operating Systems.

- Los `module summaries` deben cubrir todas las `video-notes` detectadas.
- Se agregó Coverage Matrix obligatorio.
- Se reforzó el checklist operativo para IA para cubrir todo el recorrido del módulo.
- Si hay conflicto entre brevedad y cobertura, se prioriza cobertura.
- No se ejecutó generación real durante esta tarea.

## 2026-05-07: Entrada V2.1

Se reforzó la generación de archivos maestros del Course Pack.

- Se corrigió la superficialidad de `AI_STUDY_CONTEXT` y `MASTER_PROMPT_FOR_AI`.
- Cada archivo maestro ahora tiene instrucciones específicas en lugar de depender de un prompt genérico.
- Se agregó énfasis en documentos maestros evidence-based, profundos y accionables para IA.
- No se ejecutó generación real durante esta tarea.

## 2026-05-07: Entrada V2.2

Se agregó Course Pack Evidence Layer.

- Se generan inventarios intermedios antes de archivos maestros.
- Se agregó `99_QUALITY_REPORT.md`.
- Se agregó validación simple de cobertura por módulos en `01_COURSE_MAP.md`, `02_MODULE_SUMMARIES.md` y `08_AI_STUDY_CONTEXT.md`.
- El flujo `course-pack` ahora usa `_course_pack_evidence/` como fuente principal y `module_notes` como respaldo.
- No se ejecutó generación real durante esta tarea.

## 2026-05-07: Entrada V2.2.1

Se redujo el tamaño de los prompts de documentos maestros.

- Los archivos maestros ahora usan `_course_pack_evidence/` como fuente principal.
- `module_notes` se pasan como índice de cobertura, no como contenido completo.
- Esto reduce riesgo de prompts gigantes, lentitud, costos altos o errores `input_too_large` en `course-pack`.
- No se ejecutó generación real durante esta tarea.

## 2026-05-07: Entrada Handoff para próxima IA

Se creó documentación de traspaso completa en `docs/HANDOFF_FOR_NEXT_AI.md`.

- El handoff resume visión, alcance, estructura, estado V1/V1.5/V2, problemas encontrados y próximos pasos.
- También documenta la decisión de arquitectura: transcripciones → video-notes → module-notes → evidence layer → master course-pack → quality report.
- La intención es evitar nuevos ciclos de microajustes aislados y orientar a la próxima IA hacia arquitectura, cobertura y calidad final.
- No se ejecutó transcripción real ni generación real con OpenAI durante esta tarea.

## 2026-05-07: Entrada V2.3 — Migración a Claude

Se migró el Study Pack Builder de OpenAI a Anthropic Claude.

- `src/study_pack.py` reemplaza cliente, funciones y validaciones de OpenAI por equivalentes de Anthropic.
- Modelo por defecto cambia de `gpt-4o-mini` a `claude-sonnet-4-6`.
- Se implementó prompt caching: el system prompt (1996 chars, idéntico en cada llamada) se cachea con `cache_control: ephemeral`. Esto reduce costos en ciclos de generación con muchos videos.
- La separación system/user se hace extrayendo el prefijo del system prompt del string completo antes de enviarlo a la API.
- La transcripción de audio (V1) sigue usando OpenAI Whisper porque Claude no tiene capacidad de audio.
- `requirements.txt` agrega `anthropic>=0.40.0`.
- `.env.example` actualizado con `ANTHROPIC_API_KEY`.
- `config.example.yaml` actualiza `study.model` a `claude-sonnet-4-6`.

## 2026-05-07: Entrada V1.5.5 — Soma Studio rediseñado con FastAPI

Se reemplazó la interfaz Streamlit por una app local moderna construida con FastAPI y HTML/CSS/JS puro.

- Nuevo archivo: `app/server.py` — backend FastAPI con 12 rutas.
- Nuevos archivos: `app/static/index.html`, `app/static/app.css`, `app/static/app.js`.
- La app corre en `http://127.0.0.1:8899` con `python app/server.py`.
- El streaming de output usa `StreamingResponse` con `asyncio.create_subprocess_exec`.
- El frontend consume el stream con `fetch()` + `ReadableStream` en tiempo real.
- La interfaz Streamlit legacy (`app/streamlit_app.py`) se conserva como fallback.
- `requirements.txt` agrega `fastapi>=0.111.0` y `uvicorn[standard]>=0.30.0`.

Funcionalidades de la nueva UI:

- Dark theme minimal (paleta zinc + violet, similar a Linear/Vercel).
- Sidebar de configuración persistente: curso, output, nombre, perfil YAML, límite de videos, force.
- Tab Transcripción: listar videos, dry-run, transcribir, reintentar fallidos. Tabla parseada en tiempo real desde output de CLI.
- Tab Study Pack: selector de fase (all / video-notes / module-summaries / course-pack), dry-run, generar.
- Tab Estado: conteos de manifest y study_manifest, checks de archivos, tabla del índice CSV.
- Panel de output con streaming en vivo, coloreado por tipo de línea (ok/error/warning/accent).
- Selector nativo de carpetas macOS con `osascript`.
- Confirmación antes de procesar sin límite de videos para evitar costos accidentales.

## 2026-05-08: Entrada V1.5.6 — Mejoras de UI y filtros Study Pack

Se agregaron varias mejoras a Soma Studio y al pipeline de Study Pack:

**Dropdown inteligente de cursos:**
- `GET /api/courses` detecta automáticamente los cursos con transcripciones en `output/transcripts/`.
- El campo "Nombre del curso" muestra un dropdown con cursos existentes.
- Botón `+` para entrar a modo "Nuevo curso" cuando no hay transcripciones aún.
- Al seleccionar un curso existente, se cargan automáticamente sus módulos.

**Filtro de módulos en Study Pack:**
- `GET /api/modules` lista los módulos de un curso específico.
- Selector de módulo en el tab Study Pack permite procesar solo un módulo a la vez.
- `--module` flag agregado a `src/study_pack.py` con función `filter_by_module`.
- La confirmación antes de lanzar sin límite considera también si hay módulo seleccionado.

**Sistema de jobs con reconexión:**
- `RunningJob` class en `app/server.py` bufferéa todo el output del subproceso.
- `GET /api/jobs/current` expone el job activo (tipo, running, has_log).
- `GET /api/jobs/{job_id}/reconnect` permite reconectarse y reproducir el log acumulado.
- Al recargar la página, el frontend detecta automáticamente el job activo y reconecta.
- Transcripción y Study Pack usan el sistema de jobs para reconexión.

**Barra de progreso en tiempo real:**
- Barra de progreso por fases en el panel de output del Study Pack.
- 4 pasos visuales: Video-notes → Module-summaries → Evidence → Course-pack.
- Cada paso cambia de `○` (pendiente) a `◉` (activo) y `✓` (completado).
- Porcentaje actualizado por fase y por conteo tqdm interno (N/M).

**Fix crítico de buffering:**
- `PYTHONUNBUFFERED=1` agregado al entorno del subproceso en `_env_with_dotenv()`.
- Sin este fix, Python bloqueaba el output hasta llenar 8KB de buffer.
- Consecuencia: tqdm no llegaba al stream en tiempo real y la barra quedaba en 0%.
- Con el fix, cada línea de tqdm llega inmediatamente al frontend.

**Permisos Claude Code:**
- `.claude/settings.json` creado con allowlist de comandos frecuentes del proyecto.
- Reduce prompts de aprobación para git, pip, server, CLI y curl.

**Validación de calidad V2 con Claude:**
- Módulo 3 completo (15 lecciones) regenerado con Claude Sonnet 4.6.
- Nota de "Estructura ViralCopy" validada: duraciones exactas, ejemplos verbatim, instrucciones concretas para IA.
- Calidad confirmada como suficiente para el objetivo del proyecto.

## Validaciones Ejecutadas

```bash
python3 -m compileall src app
python3 src/main.py --help
python3 src/study_pack.py --help
```

Validaciones de imports y lógica:

```bash
python3 -c "from app.server import app; print(f'{len(app.routes)} rutas OK')"
python3 -c "from src.study_pack import call_claude_text, build_claude_client; print('OK')"
python3 -c "
from src.study_prompts import build_video_note_prompt, build_system_prompt, StudySettings
from pathlib import Path
settings = StudySettings(model='claude-sonnet-4-6')
system = build_system_prompt(settings)
prompt = build_video_note_prompt(course_name='Test', module_path='M1', video_title='V1',
    relative_path=Path('M1/V1.md'), transcript_chunk='Test.', chunk_index=1, chunks_count=1, settings=settings)
separator = system + '\n\n'
assert prompt.startswith(separator)
user = prompt[len(separator):]
assert user.startswith('Tarea:')
print('Separación system/user: OK')
"
```

## Nota

V1 validado: 90/90 videos `completed`. Study Pack V2 migrado a Claude con prompt caching. UI rediseñada con FastAPI. Pendiente: agregar `ANTHROPIC_API_KEY` real en `.env` y regenerar el course-pack completo para validar calidad.
