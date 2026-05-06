# Testing

Soma Transcriber todavía no tiene una suite automatizada formal. Por ahora se usan validaciones de sintaxis, ayuda de CLI y comandos sin API para reducir riesgo antes de transcribir videos reales.

## Validaciones Ya Usadas

Compilar módulos Python:

```bash
python3 -m compileall src
```

Ver ayuda de CLI:

```bash
python3 src/main.py --help
```

Listar videos sin extraer audio ni llamar a OpenAI:

```bash
python3 src/main.py \
  --input /private/tmp/soma-course \
  --output /private/tmp/soma-output \
  --course-name Curso\ Demo \
  --list-videos \
  --max-videos 1
```

Dry run sin extraer audio ni llamar a OpenAI:

```bash
python3 src/main.py \
  --input /private/tmp/soma-course \
  --output /private/tmp/soma-output \
  --course-name Curso\ Demo \
  --dry-run \
  --max-videos 1
```

## Primer Test Real Recomendado

Cuando estén instaladas las dependencias, configurada la API key y elegido un curso real, ejecutar solo un video:

```bash
python3 src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Curso Demo" \
  --max-videos 1
```

## Qué Revisar Después del Primer Test Real

- `output/transcripts/{course-name}/...`
- `output/audio/{course-name}/...`
- `output/chunks/{course-name}/...` si aplica
- `output/index.csv`
- `data/manifest.json`
- calidad de transcripción literal
- metadata en Markdown
- tamaño de chunks
- estado `completed` o `failed`
- errores registrados por archivo
- costos aproximados si se pueden estimar manualmente desde duración y uso de API

## Criterios de Éxito Iniciales

- El proceso termina sin detenerse por errores globales.
- El video procesado genera audio.
- El Markdown final existe y conserva metadata.
- El manifest marca el archivo como `completed`.
- `output/index.csv` refleja el estado correcto.
- La transcripción es suficientemente literal para estudiar el curso.
