# Soma Transcriber

Soma Transcriber es una CLI local para convertir cursos en video en transcripciones Markdown estudiables por IA. Funciona con cursos de cualquier tema: marketing, finanzas, trading, programación, filosofía, ventas y más.

La herramienta recorre una carpeta de curso, detecta videos, extrae audio con FFmpeg, divide audios grandes o largos en chunks seguros, transcribe con OpenAI API y conserva la estructura original de módulos dentro del output.

## Instalación

Requisitos:

- Python 3.11+
- FFmpeg instalado en el sistema, incluyendo FFprobe
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
ffprobe -version
```

Soma usa FFmpeg para extraer audio y crear chunks, y FFprobe para medir duración. Esto evita depender de librerías Python de audio que pueden fallar en Python 3.13 por la remoción de `audioop`.

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

## Perfiles de configuración

Soma usa perfiles YAML para adaptar el prompt de transcripción sin atar el proyecto a un curso, marca, idioma o nicho específico. Los perfiles ayudan a mejorar precisión en nombres propios, términos técnicos y contexto, pero la transcripción sigue siendo literal.

Archivos y carpetas relevantes:

- `config.example.yaml`: plantilla universal versionada.
- `config.yaml`: configuración local por defecto; está ignorada por Git.
- `configs/examples/`: perfiles genéricos versionados para distintos tipos de curso.
- `configs/local/`: perfiles reales privados por curso; está ignorada por Git salvo `.gitkeep`.

Opcionalmente crear `config.yaml` desde la plantilla:

```bash
cp config.example.yaml config.yaml
```

Para un curso concreto, puedes crear un perfil privado en `configs/local/` y pasarlo con `--config`:

```bash
python3 src/main.py \
  --input "/ruta/curso" \
  --output "./output" \
  --course-name "Curso" \
  --config "configs/local/mi-curso.yaml" \
  --max-videos 1
```

Los perfiles pueden definir modelo, prompt base, contexto opcional del curso, idioma esperado, nombres propios, glosario y reglas de preservación. Si pasas `--model`, el valor de la CLI tiene prioridad sobre el YAML. `configs/local/` no debe subirse a GitHub.

En `audio`, `max_file_mb` controla el límite por tamaño y `max_chunk_minutes` controla el límite preventivo por duración. El valor recomendado por defecto es `10`, útil para reducir errores `input_too_large` en videos largos aunque el archivo pese menos de 24 MB.

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

Las transcripciones de V1 son literales: Soma no resume, no reescribe y no mejora el contenido. El Markdown generado sí se formatea en párrafos para facilitar lectura, revisión, estudio y análisis posterior por IA.

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

## Soma Studio Local

Soma Studio Local es una interfaz personal y local construida con Streamlit. No reemplaza la CLI: la usa por debajo para listar videos, hacer dry-run, transcribir y reintentar fallidos.

Abrir la interfaz:

```bash
streamlit run app/streamlit_app.py
```

Si no activaste el entorno virtual:

```bash
.venv/bin/streamlit run app/streamlit_app.py
```

Soma Studio sirve para preparar cursos como contexto de aprendizaje para IA: primero transcripciones literales, luego documentos de estudio y paquetes de contexto. No es una app pública, no tiene login, no usa base de datos externa y no sube datos a la nube.

Puedes seleccionar la carpeta del curso desde la interfaz o pegar la ruta manualmente. También puedes elegir la carpeta de output desde la UI. En macOS, el selector usa el diálogo nativo mediante `osascript`/AppleScript; si falla, puedes seguir pegando la ruta manualmente.

En Soma Studio, `max_videos = 0` significa sin límite. Para pruebas controladas, usa `max_videos = 1`; usa `0` solo cuando quieras procesar todo lo pendiente y entiendas el costo potencial de API.

La UI no cambia el flujo de privacidad: `output/`, `data/`, `.env`, `configs/local/` y `.tmp/` siguen siendo privados y no deben subirse a GitHub.

Estado actual del pipeline: el primer curso real fue procesado completo como prueba de pipeline: 90 videos, 90 `completed`, 0 `failed`. El siguiente paso es generar Study Packs a partir de esas transcripciones privadas.

## V2 Study Pack

El Study Pack Builder convierte transcripciones Markdown privadas en documentos de estudio para IA. No incluye transcripciones completas ni largos fragmentos verbatim: trabaja con síntesis, principios, frameworks, conceptos, ejemplos y referencias internas al archivo fuente.

Dry-run sin llamar a OpenAI:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --dry-run \
  --max-videos 2
```

Generar solo notas por video para una prueba controlada:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase video-notes \
  --max-videos 2
```

Generar el Study Pack completo:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0" \
  --config "configs/local/victor-heras-marca-personal-5.yaml"
```

`output/study/` es privado y está cubierto por la regla general de `output/`: no se sube a GitHub. El manifest de V2 se guarda en `data/study_manifest.json`, también privado.

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
  study/
    Mi curso/
      00_STUDY_PACK_INDEX.md
      video_notes/
      module_notes/
  index.csv
```

Además se mantiene `data/manifest.json` con el estado de cada archivo:

- `pending`
- `processing`
- `completed`
- `failed`

Si un video ya está `completed`, se salta automáticamente salvo que uses `--force`. Esto evita costos duplicados.

V2 mantiene además `data/study_manifest.json` para evitar regenerar notas de estudio ya completadas.

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

Después de validar un módulo completo, se recomienda procesar la carpeta raíz del curso completo. `output/` y `data/` siguen siendo privados y no deben subirse a GitHub.

## Privacidad

Soma Transcriber no sube videos ni transcripciones a ningún servicio externo. Solo envía los audios o chunks necesarios a OpenAI API para generar la transcripción.

La carpeta `.tmp/` es local para patches o archivos temporales de revisión y está ignorada por Git. No se debe subir al repositorio.

También están ignorados `data/`, `output/`, `outputs/`, videos, audios y transcripciones generadas. Estos archivos pueden contener material privado del curso o resultados de transcripción y no deben subirse a GitHub.

Los perfiles reales en `configs/local/` también son privados. Los ejemplos genéricos en `configs/examples/` sí pueden versionarse.
