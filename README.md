# Soma Transcriber

Soma Transcriber es una CLI local para convertir cursos en video en transcripciones Markdown estudiables por IA. Funciona con cursos de cualquier tema: marketing, finanzas, trading, programación, filosofía, ventas y más.

La herramienta recorre una carpeta de curso, detecta videos, extrae audio con FFmpeg, divide audios grandes en chunks menores a 24 MB, transcribe con OpenAI API y conserva la estructura original de módulos dentro del output.

## Instalación

Requisitos:

- Python 3.11+
- FFmpeg instalado en el sistema
- Una API key de OpenAI

Crear entorno virtual e instalar dependencias:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Instalar FFmpeg en Mac

Con Homebrew:

```bash
brew install ffmpeg
```

Verificar instalación:

```bash
ffmpeg -version
```

## Configurar `.env`

Crear el archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Editar `.env`:

```bash
OPENAI_API_KEY=sk-tu-api-key
```

La API key no se guarda en el código ni debe subirse a Git.

## Configurar prompt

Opcionalmente crear `config.yaml`:

```bash
cp config.example.yaml config.yaml
```

Editar `transcription.prompt` para ajustar las instrucciones enviadas al modelo de transcripción.

## Dry run

Lista los videos que se procesarían sin extraer audio y sin llamar a OpenAI API. También muestra cuántos videos se procesarían realmente y cuántos se saltarían porque ya están `completed` en el manifest:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso" \
  --dry-run
```

Limitar el dry run a los primeros videos detectados:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso" \
  --dry-run \
  --max-videos 2
```

## Listar videos

Para ver los videos detectados con índice, ruta relativa y estado del manifest, sin extraer audio y sin llamar a OpenAI API:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso" \
  --list-videos
```

También puedes combinarlo con `--max-videos`:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso" \
  --list-videos \
  --max-videos 5
```

## Transcripción real

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso"
```

Para el primer test real, se recomienda procesar solo un video:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso" \
  --max-videos 1
```

Modelo por defecto:

```bash
gpt-4o-mini-transcribe
```

Usar otro modelo:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso" \
  --model "gpt-4o-transcribe"
```

Forzar reprocesamiento aunque el archivo figure como `completed`:

```bash
python src/main.py \
  --input "/ruta/al/curso" \
  --output "./output" \
  --course-name "Mi curso" \
  --force
```

## Estructura esperada del curso

Ejemplo:

```text
curso/
  Modulo 01/
    01 - Intro.mp4
    02 - Conceptos.mov
  Modulo 02/
    01 - Caso practico.mkv
```

Extensiones detectadas:

- `.mp4`
- `.mov`
- `.mkv`
- `.webm`
- `.m4v`
- `.ts`

Algunos cursos descargados pueden venir como MPEG-TS (`.ts`). Soma puede detectarlos y procesarlos usando FFmpeg.

## Estructura de output

```text
output/
  audio/
    Mi curso/
      Modulo 01/
        01 - Intro.mp3
  chunks/
    Mi curso/
      Modulo 01/
        01 - Intro/
          chunk_001.mp3
          chunk_002.mp3
  transcripts/
    Mi curso/
      Modulo 01/
        01 - Intro.md
  index.csv
```

Además se mantiene `data/manifest.json` con el estado de cada archivo:

- `pending`
- `processing`
- `completed`
- `failed`

Si un video ya está `completed`, se salta automáticamente salvo que uses `--force`. Esto evita costos duplicados.

## Documentación del proyecto

La documentación viva está en `docs/`:

- [PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md): contexto, propósito y principios del proyecto.
- [PROJECT_STATUS.md](docs/PROJECT_STATUS.md): estado actual, validaciones, pendientes y riesgos.
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): stack, estructura y responsabilidades por archivo.
- [DATA_FLOW.md](docs/DATA_FLOW.md): flujo de datos desde videos hasta Markdown, manifest e index.
- [ROADMAP.md](docs/ROADMAP.md): hitos V1 a V5.
- [DECISIONS.md](docs/DECISIONS.md): decisiones técnicas y operativas.
- [DEVELOPMENT_LOG.md](docs/DEVELOPMENT_LOG.md): registro cronológico de avances.
- [CODEX_PROMPTS.md](docs/CODEX_PROMPTS.md): resumen de prompts y plantilla para futuras tareas.
- [TESTING.md](docs/TESTING.md): comandos de validación y plan de primer test real.
- [SECURITY_PRIVACY.md](docs/SECURITY_PRIVACY.md): qué no subir y riesgos principales.
- [RUNBOOK.md](docs/RUNBOOK.md): comandos operativos.
- [TASKS.md](docs/TASKS.md): tareas completadas y pendientes.

## Flujo de trabajo con Codex y patches

Codex se usa como ejecutor principal de cambios. Para revisiones con ChatGPT, se pueden guardar patches temporales en `.tmp/`. Esa carpeta es local, está ignorada por Git y no debe subirse al repositorio.

Comando sugerido para generar un patch de revisión:

```bash
cd /Users/henry/Documents/soma-transcriber
git status --short
mkdir -p .tmp
git add -A
git diff --cached --stat
git diff --cached > .tmp/soma_transcriber_prompt_3_docs.patch
```

Antes de compartir un patch, revisar que no incluya `.env`, videos, audios, transcripciones privadas, `output/`, `data/` ni otros datos sensibles.

## Privacidad

Soma Transcriber no sube videos ni transcripciones a ningún servicio externo. Solo envía los audios o chunks necesarios a OpenAI API para generar la transcripción.

La carpeta `.tmp/` es local para patches o archivos temporales de revisión y está ignorada por Git. No se debe subir al repositorio.

También están ignorados `data/`, `output/`, `outputs/`, videos, audios y transcripciones generadas. Estos archivos pueden contener material privado del curso o resultados de transcripción y no deben subirse a GitHub.
