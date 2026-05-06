# Estado del Proyecto

Versión actual: V1.2

Estado: CLI base funcional con seguridad operativa inicial y documentación viva creada.

Soma Transcriber ya tiene una primera base funcional para detectar videos, extraer audio, dividir archivos grandes, transcribir con OpenAI API y escribir resultados organizados. La versión V1.1 agregó controles para reducir riesgo operativo y costos accidentales antes de ejecutar transcripciones reales.

## Funcionalidades Implementadas

- CLI local en Python.
- Flags disponibles: `--input`, `--output`, `--course-name`, `--model`, `--force`, `--dry-run`, `--max-videos`, `--list-videos`, `--config`.
- Scan recursivo de videos con extensiones `.mp4`, `.mov`, `.mkv`, `.webm`, `.m4v`.
- Extracción de audio con FFmpeg a MP3 mono, 16000 Hz, 64k.
- División de audios mayores a 24 MB usando pydub.
- Transcripción con OpenAI API.
- Prompt configurable desde `config.yaml`.
- Transcripciones Markdown con metadata.
- Manifest en `data/manifest.json`.
- Saltar archivos ya `completed` salvo que se use `--force`.
- Índice CSV en `output/index.csv`.
- `.gitignore` configurado para excluir `.env`, `.tmp/`, `data/`, `output/`, `outputs/`, videos, audios y archivos pesados.

## Validaciones Ejecutadas

```bash
python3 -m compileall src
python3 src/main.py --help
```

También se probaron comandos sin API:

```bash
python3 src/main.py --input /private/tmp/soma-course --output /private/tmp/soma-output --course-name Curso\ Demo --list-videos --max-videos 1
python3 src/main.py --input /private/tmp/soma-course --output /private/tmp/soma-output --course-name Curso\ Demo --dry-run --max-videos 1
```

## Todavía No Probado

- No se ha ejecutado una transcripción real con OpenAI API.
- No se ha validado la calidad de transcripción sobre un curso real.
- No se ha medido comportamiento real de chunking con archivos grandes.
- No se ha estimado costo real por duración de video.
- No se ha revisado el Markdown generado a partir de audio real.

## Próximo Hito Recomendado

V1.3: primer test real controlado con un solo video usando `--max-videos 1`.

El objetivo de ese hito no es procesar un curso completo, sino validar el circuito end to end: audio, chunking si aplica, API, Markdown, manifest e index.

## Riesgos Actuales

- Ejecutar un curso completo por accidente sin `--max-videos`.
- Usar `--force` sin intención y duplicar costos.
- Exponer `OPENAI_API_KEY` si se versiona `.env` por error.
- Versionar transcripciones privadas, audios o videos si se cambia `.gitignore`.
- Encontrar errores no visibles hasta probar con videos reales, especialmente FFmpeg, pydub y límites de tamaño.
