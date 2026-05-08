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
- Agregar progreso estructurado en la nueva UI.

Nota: el perfil local real fue creado en `configs/local/` y no se versiona por privacidad.

## Pendientes

- Agregar `ANTHROPIC_API_KEY` real en `.env`.
- Regenerar course-pack completo con V2.3 (Claude) y `--force`.
- Validar `99_QUALITY_REPORT.md` con la nueva generación.
- Validar calidad de `08_AI_STUDY_CONTEXT.md` y `09_MASTER_PROMPT_FOR_AI.md`.
- Probar que una IA externa (ChatGPT, Claude) da guiones específicos del curso desde el Study Pack.
- Revisar calidad de transcripciones por muestreo.
- Exportar ZIP del Study Pack desde Soma Studio.
- Vista de revisión por muestreo.
- Agregar estimación de duración/costo de API.
- Agregar selección por índice/rango de videos si sigue siendo necesaria.

## Siguiente Acción Recomendada

1. Agregar `ANTHROPIC_API_KEY` real al `.env`.
2. Abrir Soma Studio: `python app/server.py` → http://127.0.0.1:8899
3. Seleccionar el curso Victor Heras, perfil `configs/local/victor-heras-marca-personal-5.yaml`, max_videos=2, fase=video-notes.
4. Ejecutar "Generar Study Pack" para validar la nueva integración con Claude.
5. Revisar los outputs y validar calidad.
