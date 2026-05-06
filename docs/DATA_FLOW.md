# Flujo de Datos

Soma Transcriber procesa un curso desde una carpeta local y genera transcripciones Markdown organizadas. El flujo está diseñado para preservar la estructura original del curso y evitar reprocesar archivos ya completados.

## Diagrama Textual

```text
Curso en video
  -> scan recursivo
  -> detección de videos soportados
  -> consulta de manifest
  -> extracción de audio con FFmpeg
  -> chunking si el audio supera el límite
  -> transcripción con OpenAI API
  -> unión de chunks en orden
  -> Markdown con metadata
  -> actualización de data/manifest.json
  -> generación de output/index.csv
```

## Paso a Paso

1. Curso en video: el usuario entrega una carpeta local con módulos y lecciones en video.
2. Scan recursivo: `scanner.py` recorre la carpeta y detecta videos con extensiones soportadas.
3. Manifest: `manifest.py` revisa si un archivo ya está `completed`. Si lo está y no se usa `--force`, se salta.
4. Extracción de audio: `audio.py` usa FFmpeg para crear MP3 mono, 16000 Hz, 64k en `output/audio/{course-name}/...`.
5. Chunking: si el MP3 supera 24 MB, se divide con pydub en `output/chunks/{course-name}/{video-name}/chunk_001.mp3`.
6. Transcripción: `transcriber.py` envía el audio o chunks a OpenAI API con `response_format text`.
7. Unión de chunks: si hubo chunks, se unen en orden con separadores internos `Parte 1`, `Parte 2`, etc.
8. Markdown: `writer.py` crea una transcripción con metadata y sección `## Transcripción literal`.
9. Manifest: se registra el resultado como `completed` o `failed`.
10. Index: se genera `output/index.csv` con curso, módulo, video, rutas, estado, chunks y fecha.

## Salidas Principales

```text
output/audio/{course-name}/...
output/chunks/{course-name}/...
output/transcripts/{course-name}/...
output/index.csv
data/manifest.json
```

Todas estas salidas son privadas y están ignoradas por Git.
