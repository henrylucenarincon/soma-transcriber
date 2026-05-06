# Runbook Operativo

Comandos de operación diaria para Soma Transcriber.

## Setup Inicial

```bash
cd /Users/henry/Documents/soma-transcriber
python3.11 -m venv .venv
```

## Activar Entorno Virtual

```bash
source .venv/bin/activate
```

## Instalar Dependencias

```bash
pip install -r requirements.txt
```

## Instalar FFmpeg en Mac

```bash
brew install ffmpeg
ffmpeg -version
```

## Configurar `.env`

```bash
cp .env.example .env
```

Editar `.env` y agregar:

```bash
OPENAI_API_KEY=sk-tu-api-key
```

No incluir `.env` en patches ni commits.

## Listar Videos

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Curso Demo" \
  --list-videos
```

## Dry Run

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Curso Demo" \
  --dry-run
```

## Primer Test Real

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Curso Demo" \
  --max-videos 1
```

## Revisar Outputs

```bash
ls -R output
ls -R data
```

Revisar especialmente:

- `output/transcripts/`
- `output/audio/`
- `output/chunks/` si aplica
- `output/index.csv`
- `data/manifest.json`

## Generar Patch para ChatGPT

```bash
cd /Users/henry/Documents/soma-transcriber
git status --short
mkdir -p .tmp
git add -A
git diff --cached --stat
git diff --cached > .tmp/soma_transcriber_prompt_3_docs.patch
```

Antes de compartir un patch, revisar que no incluya:

- `.env`
- videos
- audios
- transcripciones privadas
- `output/`
- `data/`
- `.tmp/`

## No Incluir Datos Sensibles

No pegar API keys, transcripciones privadas, rutas sensibles innecesarias o contenido completo de cursos en prompts externos.
