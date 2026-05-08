# Roadmap

## V1: Transcripción Literal Ordenada

Crear una CLI local capaz de recorrer un curso, extraer audio, dividir archivos grandes, transcribir literalmente y guardar Markdown manteniendo módulos y lecciones.

Estado: completado como base funcional.

## V1.1: Seguridad Operativa y Control de Costos

Agregar controles para operar con menos riesgo antes de usar videos reales:

- `--max-videos`
- `--list-videos`
- dry-run más informativo
- validación previa de FFmpeg y `OPENAI_API_KEY`
- `.gitignore` reforzado
- README actualizado

Estado: completado.

## V1.2: Documentación Viva

Crear `docs/` con contexto, arquitectura, flujo de datos, decisiones, runbook, testing, privacidad, roadmap, tasks y prompts.

Estado: completado.

## V1.3: Primera Transcripción Real Controlada

Procesar un solo video real con:

```bash
python src/main.py --input "/ruta/curso" --output "./output" --course-name "Curso Demo" --max-videos 1
```

Objetivo: validar el circuito completo antes de escalar.

V1.3.5 deja cerrado el primer módulo real como prueba de producción local: 13/13 videos completados y el caso `input_too_large` resuelto con chunking FFmpeg/FFprobe.

Próximo paso: procesar el curso completo desde la carpeta raíz.

Luego: avanzar a V2 para generar documentos de estudio del curso.

## V1.4: Robustez Después del Primer Test Real

Mejorar el sistema según hallazgos reales:

- errores de FFmpeg
- límites de tamaño
- calidad de Markdown
- reintentos
- logs
- estimación de costo/duración
- selección por índice/rango si hace falta

## V1.5: Soma Studio Local

Estado: rediseñado y completado.

La interfaz local fue inicialmente construida con Streamlit (V1.5.0) y luego rediseñada completamente con FastAPI + HTML/CSS/JS (V1.5.5).

La nueva UI incluye:

- dark theme minimal (paleta zinc + violet)
- sidebar de configuración persistente
- tab Transcripción con streaming en tiempo real
- tab Study Pack con selector de fase integrado
- tab Estado con conteos de manifest, checks de archivos e índice CSV
- selector nativo de carpetas macOS
- confirmación antes de procesar sin límite de videos
- output coloreado en vivo

Iniciar: `python app/server.py` → `http://127.0.0.1:8899`

No tiene login, backend externo, base de datos ni modo SaaS.

## V1.6: Primer Curso Completo Procesado

Estado: completado.

El primer curso real quedó procesado completo: 90 videos detectados, 90 `completed`, 0 `failed`.

V1 queda validado como pipeline completo de transcripción local.

## V2: Study Pack

Estado: etapa activa — migración a Claude completada, validación de calidad pendiente.

El Study Pack Builder usa Claude Sonnet 4.6 (con prompt caching) para generar documentos de estudio desde transcripciones privadas.

La arquitectura es:

```
transcripciones literales
→ video-notes por lección
→ module-notes (Module Operating Systems)
→ _course_pack_evidence/ (inventarios intermedios)
→ documentos maestros del Study Pack
→ 99_QUALITY_REPORT.md
→ contexto listo para IA
```

Documentos del Study Pack:

- `00_STUDY_PACK_INDEX.md`
- `01_COURSE_MAP.md`
- `02_MODULE_SUMMARIES.md`
- `03_CORE_PRINCIPLES.md`
- `04_FRAMEWORKS.md`
- `05_KEY_CONCEPTS.md`
- `06_EXAMPLES_AND_CASES.md`
- `07_APPLICATION_GUIDE.md`
- `08_AI_STUDY_CONTEXT.md`
- `09_MASTER_PROMPT_FOR_AI.md`

Pendiente: regenerar course-pack completo con V2.3 y validar calidad de `08` y `09` como onboarding real para IA.

## V3: Base Consultable para IA

Convertir el curso transcrito en una base consultable:

- búsqueda por módulo/lección
- recuperación semántica
- preguntas y respuestas con citas
- selección de contexto relevante

## V4: Ejecución de Tareas Aplicando el Curso

Usar el conocimiento del curso para producir entregables concretos:

- planes
- scripts
- checklists
- estrategias
- análisis
- implementaciones guiadas por el contenido estudiado

## V5: Posible Interfaz Local

Evaluar una app local más avanzada si Soma Studio necesita crecer más allá de Streamlit. V1.5 ya cubre el uso personal local inicial.
