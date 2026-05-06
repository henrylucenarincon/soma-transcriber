# Arquitectura

Soma Transcriber es una CLI local en Python. Su arquitectura está dividida por responsabilidades pequeñas para que cada paso del pipeline pueda probarse, reemplazarse o endurecerse sin reescribir todo el sistema.

## Stack Actual

- Python 3.11+
- FFmpeg instalado en el sistema
- OpenAI API
- `python-dotenv`
- `pydub`
- `tqdm`
- `pandas`
- `pyyaml`

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
    utils.py
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

`audio.py`: extracción de audio con FFmpeg y división en chunks menores al límite configurado. Produce MP3 mono, 16000 Hz, 64k.

`transcriber.py`: llamada a OpenAI API para transcribir un audio o chunk. Usa `OPENAI_API_KEY` desde `.env` o variable de entorno. También construye el prompt final con `build_transcription_prompt(config)`.

`manifest.py`: lectura y escritura de `data/manifest.json`. Registra estado por archivo: `pending`, `processing`, `completed`, `failed`, rutas generadas, chunks, errores y fecha de actualización.

`writer.py`: escritura de transcripciones Markdown con metadata y generación de `output/index.csv`.

`utils.py`: helpers compartidos para fechas, rutas seguras, configuración, conversión de tamaños y mensajes por defecto.

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

## Código Fuente

Debe versionarse:

- `src/`
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
