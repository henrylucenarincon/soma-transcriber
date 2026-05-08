# Tareas

## Completadas

- Crear CLI base.
- Detectar videos.
- Extraer audio.
- Dividir chunks.
- Transcribir con OpenAI.
- Manifest.
- Markdown.
- `index.csv`.
- `--max-videos`.
- `--list-videos`.
- dry-run mejorado.
- validación FFmpeg/API key.
- documentación viva.
- soporte para videos `.ts`.
- orden natural de módulos y videos.
- Primer test real con 1 video.
- Formato legible de transcripciones Markdown.
- perfiles universales de configuración por curso.
- chunking preventivo por duración.
- reemplazar la dependencia anterior por FFmpeg/FFprobe para chunking.
- Reprocesar video fallido del módulo 1.
- Validar módulo 1 completo.
- Crear perfil local real para Victor Heras.
- Reprocesar primer video con perfil local.
- Probar nuevamente con `--force --max-videos 1`.
- Procesar módulo completo.
- Crear interfaz local inicial Soma Studio con Streamlit.
- Selección visual de carpetas.
- Aclarar `max_videos` en UI.
- Procesar curso completo.
- Corregir nombre final del output del curso.
- Crear estructura inicial de Study Pack Builder.
- Probar `video-notes` con `--max-videos 2`.
- Mejorar prompts de video-notes.
- Ajustar prompts para clases introductorias/mapa.
- Detectar clases introductorias por título/ruta.
- Ajustar video-notes introductorias como mapa del módulo.
- Separar video-notes introductorias y operativas.
- Mejorar profundidad de module summaries.
- Convertir module summaries en Module Operating Systems.
- Reforzar module summaries con enfoque evidence-based.
- Agregar Coverage Matrix a module summaries.
- Reforzar cobertura completa de lecciones.
- Mejorar prompts del course-pack maestro.
- Crear Course Pack Evidence Layer.
- Agregar inventarios de principios/frameworks/conceptos/ejemplos/aplicaciones.
- Agregar Quality Report.
- Reducir prompts gigantes en course-pack.
- Usar evidence layer como fuente principal de documentos maestros.
- Crear documentación de handoff para próxima IA.
- Migrar Study Pack Builder de OpenAI a Claude Sonnet 4.6 con prompt caching.
- Rediseñar Soma Studio con FastAPI y UI dark theme minimal.
- Integrar Study Pack en la nueva UI (tab dedicado con selector de fase).
- Agregar streaming de output en tiempo real en la nueva UI.
- Agregar barra de progreso por fases con pasos visuales en tiempo real.
- Corregir bug de buffering Python con PYTHONUNBUFFERED=1.
- Dropdown inteligente de cursos detectados desde output/transcripts/.
- Filtro de módulos en Study Pack (CLI --module + UI selector).
- Sistema de jobs con reconexión al recargar la página.
- Configurar permisos en .claude/settings.json para reducir prompts.
- Validar calidad de notas del módulo 3 con Claude (ViralCopy, Ganchos, Filtro 5-50).

Nota: el perfil local real fue creado en `configs/local/` y no se versiona por privacidad.

## Pendientes

- Generar Study Pack completo del curso (90 notas, 11 módulos, course-pack) con Claude.
- Validar `99_QUALITY_REPORT.md` tras generación completa.
- Validar `08_AI_STUDY_CONTEXT.md` y `09_MASTER_PROMPT_FOR_AI.md` como onboarding real para IA.
- Probar con Claude.ai Projects: subir Study Pack y pedir guion viral basado en el curso.
- Exportar ZIP del Study Pack desde Soma Studio.
- Vista de revisión por muestreo.
- Agregar estimación de duración/costo de API.
- Agregar selección por índice/rango de videos si sigue siendo necesaria.

## Siguiente Acción Recomendada

Generar Study Pack completo desde Soma Studio:
- Curso: Victor Heras - Marca Personal 5.0
- Perfil: configs/local/victor-heras-marca-personal-5.yaml
- Límite: 0 (sin límite)
- Módulo: Todos
- Fase: Todas las fases
- Force: ✓

Tiempo estimado: ~2 horas. Luego validar documentos maestros y probar con Claude.ai.
