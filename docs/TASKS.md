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

## Pendientes

- Instalar dependencias localmente si falta.
- Configurar `.env` real.
- Crear perfil local real para Victor Heras.
- Reprocesar primer video con perfil local.
- Probar nuevamente con `--force --max-videos 1`.
- Reprocesar video fallido del módulo 1.
- Validar módulo 1 completo.
- Procesar módulo completo.
- Procesar curso completo.
- Revisar calidad de transcripción.
- Mejorar manejo de errores según test real.
- Agregar estimación de duración/costo.
- Agregar selección por índice/rango de videos.
- Agregar documentos de estudio V2.
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
