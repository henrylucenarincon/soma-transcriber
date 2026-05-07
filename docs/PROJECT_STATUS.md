# Estado del Proyecto

Versión actual: V2.0

Estado: pipeline V1 validado con un curso completo y Study Pack Builder V2.0 agregado como CLI local inicial.

Soma Transcriber ya tiene una primera base funcional para detectar videos, extraer audio, dividir archivos grandes, transcribir con OpenAI API y escribir resultados organizados. La versión V1.1 agregó controles para reducir riesgo operativo y costos accidentales antes de ejecutar transcripciones reales. En V1.3 se ejecutó el primer test real controlado con 1 video y fue exitoso.

## Funcionalidades Implementadas

- CLI local en Python.
- Flags disponibles: `--input`, `--output`, `--course-name`, `--model`, `--force`, `--dry-run`, `--max-videos`, `--list-videos`, `--config`.
- Scan recursivo de videos con extensiones `.mp4`, `.mov`, `.mkv`, `.webm`, `.m4v`, `.ts`.
- Orden natural de módulos y videos numerados.
- Extracción de audio con FFmpeg a MP3 mono, 16000 Hz, 64k.
- División de audios con FFmpeg/FFprobe por tamaño y por duración máxima configurable.
- Eliminación de la dependencia funcional de audio en Python para evitar problemas de `audioop` en Python 3.13.
- Transcripción con OpenAI API.
- Prompt configurable desde `config.yaml`.
- Perfiles universales de configuración por curso con `--config`.
- Construcción de prompt final desde prompt base, contexto, idioma, nombres propios, glosario y reglas de preservación.
- Transcripciones Markdown con metadata.
- Formato de párrafos en Markdown para mejorar legibilidad sin resumir ni reescribir.
- Manifest en `data/manifest.json`.
- Saltar archivos ya `completed` salvo que se use `--force`.
- Índice CSV en `output/index.csv`.
- Soma Studio Local con Streamlit como interfaz personal encima de la CLI.
- Tabs locales para curso, transcripción, estado y Study Pack próximamente.
- Soma Studio permite seleccionar carpeta local de curso/output desde Finder o pegar rutas manualmente.
- En macOS, el selector de carpetas usa `osascript`/AppleScript con fallback manual.
- La UI aclara que `max_videos = 0` significa sin límite y recomienda `1` para pruebas.
- Study Pack Builder V2.0 en `src/study_pack.py`.
- Generación por fases: `video-notes`, `module-summaries`, `course-pack` y `all`.
- Manifest V2 privado en `data/study_manifest.json`.
- Configuración V2 mediante sección `study` en YAML.
- Chunking de texto por caracteres para analizar transcripciones largas.
- Salidas privadas en `output/study/{course-name}/`.
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

## Probado

- Primer test real con 1 video usando OpenAI API.
- Resultado del primer test: procesado 1, fallidos 0.
- Se generó audio, `output/index.csv` y transcripción Markdown con metadata y `status: completed`.
- Módulo 1 real procesado completo.
- Resultado del módulo 1: 13 videos detectados, 13 `completed`, 0 `failed` después del reproceso.
- El video 12 requirió chunking preventivo y quedó con `chunks_count: 3`.
- Primer curso completo procesado exitosamente.
- Curso: Victor Heras - Marca Personal 5.0.
- Videos detectados: 90.
- Completed: 90.
- Failed: 0.
- Output final: `output/transcripts/Victor Heras - Marca Personal 5.0/`.
- `output/` y `data/` son privados y no se versionan.

## Todavía No Probado

- No se ha estimado costo real por duración de video.
- No se ha ejecutado generación real de Study Pack con OpenAI.
- Falta probar `video-notes` con `--max-videos 2`.

## Hallazgo V1.3

El primer Markdown real quedó como un bloque único de texto. En V1.3.1 se corrige la presentación para escribir la transcripción literal en párrafos legibles, sin resumir, reescribir ni alterar el orden del contenido.

## Hallazgo V1.3.3

Al procesar el módulo 1 real se detectó un caso `input_too_large` en un video largo que no había superado el límite por MB. Para reducir ese riesgo, Soma ahora divide preventivamente audios que superen `audio.max_chunk_minutes`, por defecto 10 minutos.

## Hallazgo V1.3.4

En Python 3.13, la dependencia de chunking anterior falló por la remoción de `audioop` y ausencia de `pyaudioop`. Soma reemplazó ese flujo por FFmpeg/FFprobe para obtener duración y crear chunks sin depender de esa compatibilidad.

## Resultado V1.3.5

El módulo 1 real quedó como prueba de producción local: 13/13 videos `completed`. El caso `input_too_large` del video 12 se resolvió con FFmpeg/FFprobe, generando 3 chunks y una transcripción organizada en partes.

## Próximo Hito Recomendado

Ejecutar un dry-run de V2 y luego una prueba real controlada de `video-notes` con `--max-videos 2`.

## Riesgos Actuales

- Ejecutar un curso completo por accidente sin `--max-videos`.
- Usar `--force` sin intención y duplicar costos.
- Exponer `OPENAI_API_KEY` si se versiona `.env` por error.
- Versionar transcripciones privadas, audios o videos si se cambia `.gitignore`.
- Encontrar errores no visibles hasta probar con videos reales, especialmente FFmpeg/FFprobe y límites de tamaño o duración.
