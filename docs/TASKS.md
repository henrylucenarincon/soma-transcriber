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

Nota: el perfil local real fue creado en `configs/local/` y no se versiona por privacidad.

## Pendientes

- Instalar dependencias localmente si falta.
- Configurar `.env` real.
- Revisar calidad de transcripciones por muestreo.
- Generar documentos de estudio V2.
- Mejorar progreso estructurado.
- Exportar ZIP de transcripciones.
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
