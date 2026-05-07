# Arquitectura

Soma Transcriber es una CLI local en Python. Su arquitectura está dividida por responsabilidades pequeñas para que cada paso del pipeline pueda probarse, reemplazarse o endurecerse sin reescribir todo el sistema.

## Stack Actual

- Python 3.11+
- FFmpeg y FFprobe instalados en el sistema
- OpenAI API
- `python-dotenv`
- `tqdm`
- `pandas`
- `pyyaml`
- `streamlit`

## Estructura de Carpetas

```text
soma-transcriber/
  src/
    main.py
    scanner.py
    audio.py
    transcriber.py
    manifest.py
    writer.py
    study_pack.py
    study_prompts.py
    study_writer.py
    study_manifest.py
    utils.py
  app/
    streamlit_app.py
  docs/
  configs/
    examples/
    local/
  data/
    manifest.json
  output/
  .tmp/
  README.md
  requirements.txt
  config.example.yaml
  .env.example
  .gitignore
```

`data/`, `output/` y `.tmp/` son carpetas locales ignoradas por Git. `configs/local/` también es privado y se ignora salvo `.gitkeep`. Pueden existir durante el trabajo diario, pero no deben versionarse con datos reales.

## Responsabilidad de `src/`

`main.py`: punto de entrada de la CLI. Parseo de argumentos, carga de configuración, coordinación del pipeline, `--dry-run`, `--list-videos`, `--max-videos`, validaciones previas y manejo por archivo.

`scanner.py`: scan recursivo del curso y detección de archivos de video soportados: `.mp4`, `.mov`, `.mkv`, `.webm`, `.m4v` y `.ts` MPEG-TS. Devuelve rutas absolutas, rutas relativas, módulo y nombre de video. Usa orden natural por ruta relativa para respetar módulos y lecciones numeradas, evitando que `10` aparezca antes de `2`.

`audio.py`: extracción de audio con FFmpeg, medición de duración con FFprobe y división en chunks con FFmpeg. Produce MP3 mono, 16000 Hz, 64k. Puede dividir por tamaño (`audio.max_file_mb` o `audio.max_chunk_mb`) y por duración preventiva (`audio.max_chunk_minutes`) para reducir errores `input_too_large` en audios largos. No depende de librerías Python de audio para chunking.

`transcriber.py`: llamada a OpenAI API para transcribir un audio o chunk. Usa `OPENAI_API_KEY` desde `.env` o variable de entorno. También construye el prompt final con `build_transcription_prompt(config)`.

`manifest.py`: lectura y escritura de `data/manifest.json`. Registra estado por archivo: `pending`, `processing`, `completed`, `failed`, rutas generadas, chunks, errores y fecha de actualización.

`writer.py`: escritura de transcripciones Markdown con metadata y generación de `output/index.csv`.

`study_pack.py`: CLI V2 para generar Study Packs privados desde transcripciones Markdown. Coordina fases `video-notes`, `module-summaries`, `course-pack` y `all`, soporta `--dry-run`, `--max-videos`, `--force`, `--model` y `--config`.

`study_prompts.py`: prompts y plantillas para transformar transcripciones en notas de estudio, resúmenes de módulo y documentos globales para IA. Sus instrucciones evitan copiar transcripciones completas, priorizan paráfrasis fiel y bloquean conocimiento externo salvo que se configure lo contrario.

`study_writer.py`: lectura de transcripciones Markdown, parseo de metadata YAML, extracción de la sección `## Transcripción literal`, chunking de texto por caracteres y escritura de archivos Markdown del Study Pack.

`study_manifest.py`: manifest privado de V2 en `data/study_manifest.json`. Registra estado por transcripción para evitar regenerar notas y costos duplicados.

`utils.py`: helpers compartidos para fechas, rutas seguras, configuración, conversión de tamaños y mensajes por defecto.

## Responsabilidad de `app/`

`streamlit_app.py`: interfaz local Soma Studio. Es una capa visual encima de la CLI existente: invoca `src/main.py` con `subprocess.run`, usando `sys.executable` para respetar el mismo entorno Python. Permite configurar curso, perfil YAML, output, `max_videos`, `force`, listar videos, hacer dry-run, transcribir, reintentar fallidos y revisar estado local.

V1.5 no agrega base de datos, backend propio, login, multiusuario ni servicios externos. La CLI sigue siendo la base operativa.

## Perfiles de Configuración

Soma soporta perfiles YAML universales por curso sin cambiar código. La CLI ya acepta `--config`, por ejemplo:

```bash
python src/main.py --input "/ruta/curso" --output "./output" --course-name "Curso" --config "configs/local/mi-curso.yaml"
```

El prompt final se construye de forma incremental:

- `transcription.base_prompt` como prompt base moderno.
- `transcription.prompt` como compatibilidad con configuraciones anteriores si no existe `base_prompt`.
- `transcription.course_context` como contexto opcional del curso.
- `transcription.proper_names` como sección de nombres propios.
- `transcription.glossary_terms` como sección de glosario.
- `transcription.preserve` como reglas de preservación.

Las secciones vacías no se incluyen. Esto permite mejorar precisión en nombres, términos e idioma sin hardcodear prompts específicos en el código.

El modelo puede declararse en `transcription.model`; si el usuario pasa `--model`, la CLI tiene prioridad.

La sección opcional `study` configura V2:

- `study.model`
- `study.output_language`
- `study.max_chars_per_analysis_chunk`
- `study.include_short_quotes`
- `study.quote_max_words`
- `study.avoid_external_knowledge`

## Study Pack Builder

V2 lee `output/transcripts/{course-name}/...` y genera documentos privados en `output/study/{course-name}/...`.

El flujo interno es:

```text
transcripciones Markdown
  -> notas por video en video_notes/
  -> resúmenes por módulo en module_notes/
  -> documentos globales del Study Pack
```

El builder no incluye transcripciones completas dentro del Study Pack. Trabaja con síntesis, principios, frameworks, conceptos, ejemplos y referencias internas al archivo fuente.

`study_pack.py` usa OpenAI API para análisis textual y requiere `OPENAI_API_KEY` solo cuando no se ejecuta con `--dry-run`. No toca audio, FFmpeg ni la CLI de transcripción.

## Código Fuente

Debe versionarse:

- `src/`
- `app/`
- `docs/`
- `README.md`
- `requirements.txt`
- `.gitignore`
- `.env.example`
- `config.example.yaml`
- `configs/examples/`

## Archivos Generados

No deben versionarse:

- `data/manifest.json`
- `output/index.csv`
- `output/audio/...`
- `output/chunks/...`
- `output/transcripts/...`
- `output/study/...`
- `data/study_manifest.json`

## Archivos Privados

No deben versionarse:

- `.env`
- `.env.*` excepto `.env.example`
- Videos originales del curso.
- Audios extraídos.
- Chunks.
- Transcripciones privadas.
- `data/`
- `output/`
- `outputs/`
- `.tmp/`
- `configs/local/` excepto `.gitkeep`

## Archivos Versionables

Sí deben versionarse:

- Código fuente.
- Documentación.
- Ejemplos sin secretos.
- Configuración de ejemplo.
- Perfiles genéricos en `configs/examples/`.
- Lista de dependencias.
