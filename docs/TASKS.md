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

## Pendientes

- Instalar dependencias localmente si falta.
- Configurar `.env` real.
- Probar con 1 video real.
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
