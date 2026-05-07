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
- Crear interfaz local inicial Soma Studio.
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

Nota: el perfil local real fue creado en `configs/local/` y no se versiona por privacidad.

## Pendientes

- Instalar dependencias localmente si falta.
- Configurar `.env` real.
- Revisar calidad de transcripciones por muestreo.
- Ejecutar dry-run de V2.
- Regenerar 2 video-notes de prueba con `--force`.
- Validar calidad de video-notes mejoradas.
- Generar video-notes del módulo 3 completo.
- Regenerar module summary del módulo 3.
- Validar calidad del nuevo module summary.
- Generar course pack completo.
- Integrar Study Pack en Soma Studio.
- Exportar ZIP.
- Generar documentos de estudio V2.
- Mejorar progreso estructurado.
- Generar AI_STUDY_CONTEXT.md.
- Vista de revisión por muestreo.
- Mejorar manejo de errores según nuevos hallazgos reales.
- Agregar estimación de duración/costo.
- Agregar selección por índice/rango de videos si sigue siendo necesaria.
- Evaluar interfaz local en V5.

## Siguiente Acción Recomendada

Preparar el entorno real, elegir un curso de prueba y ejecutar primero:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Curso Demo" \
  --max-videos 1
```
