# Testing

Soma Transcriber todavía no tiene una suite automatizada formal. Por ahora se usan validaciones de sintaxis, ayuda de CLI y comandos sin API para reducir riesgo antes de transcribir videos reales.

## Validaciones Ya Usadas

Compilar módulos Python:

```bash
python3 -m compileall src
```

Compilar CLI y app:

```bash
python3 -m compileall src app
```

Ver ayuda de CLI:

```bash
python3 src/main.py --help
```

Validar import de helpers de audio:

```bash
python3 -c "from src.audio import get_audio_duration_seconds; print('audio helpers OK')"
```

Validar Streamlit:

```bash
python3 -c "import streamlit; print('streamlit OK')"
```

Si el Python del sistema está gestionado por Homebrew, ejecutar la validación desde el entorno virtual:

```bash
.venv/bin/python -c "import streamlit; print('streamlit OK')"
```

Abrir Soma Studio Local:

```bash
streamlit run app/streamlit_app.py
```

La selección de carpeta se valida manualmente abriendo Soma Studio Local y usando los botones `Seleccionar carpeta` y `Seleccionar output`. Si el selector del sistema no abre, la UI debe permitir continuar pegando la ruta manualmente.

No ejecutar transcripción real como parte de estas validaciones salvo que se esté haciendo una prueba controlada.

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

Dry run con perfil de configuración versionado:

```bash
python3 src/main.py \
  --input "/ruta/curso" \
  --output "./output" \
  --course-name "Curso Demo" \
  --config "configs/examples/generic-spanish-course.yaml" \
  --dry-run \
  --max-videos 1
```

## Primer Test Real Ejecutado

Comando usado para el primer test real controlado:

```bash
python3 src/main.py \
  --input "/Users/henry/Library/CloudStorage/GoogleDrive-henrylucena7@gmail.com/Mi unidad/Cursos/VICOR HERAS - MARCA PERSONAL 5.0/1. Como funciona el algoritmo" \
  --output "./output" \
  --course-name "Victor Heras - Marca Personal 5.0 - Test Modulo 1" \
  --max-videos 1 \
  --force
```

Resultado observado: procesado 1, fallidos 0. Se generó audio, `output/index.csv` y transcripción Markdown.

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

## Qué Revisar Después de Regenerar V1.3.1

- metadata YAML intacta
- `status: completed`
- transcripción separada en párrafos
- que no haya resumen
- que no haya reescritura
- que se mantenga el contenido literal y en orden
- que `output/` y `data/` sigan ignorados por Git

## Reprocesar Fallidos Sin `--force`

Después de V1.3.3, se puede reintentar el video fallido del módulo 1 sin `--force`. Los videos `completed` deberían saltarse y Soma debería intentar el archivo `failed`:

```bash
python3 src/main.py \
  --input "/Users/henry/Library/CloudStorage/GoogleDrive-henrylucena7@gmail.com/Mi unidad/Cursos/VICOR HERAS - MARCA PERSONAL 5.0/1. Como funciona el algoritmo" \
  --output "./output" \
  --course-name "Victor Heras - Marca Personal 5.0 - Modulo 1" \
  --config "configs/local/victor-heras-marca-personal-5.yaml"
```

Sin `--force`, el manifest debe evitar reprocesar archivos `completed` y concentrarse en los `failed` o pendientes.

## Validación del Módulo 1

Comando usado para reprocesar el módulo 1 sin `--force`:

```bash
python3 src/main.py \
  --input "/Users/henry/Library/CloudStorage/GoogleDrive-henrylucena7@gmail.com/Mi unidad/Cursos/VICOR HERAS - MARCA PERSONAL 5.0/1. Como funciona el algoritmo" \
  --output "./output" \
  --course-name "Victor Heras - Marca Personal 5.0 - Modulo 1" \
  --config "configs/local/victor-heras-marca-personal-5.yaml"
```

Comandos locales para validar resultados privados:

```bash
find output/transcripts -type f -name "*.md" | sort | wc -l
cat output/index.csv
grep -A 20 -B 5 "primeros clientes" data/manifest.json
```

Resultado esperado:

- 13 transcripciones del módulo 1.
- 13 registros `completed`.
- 0 registros `failed` después del reproceso.
- video 12 con `chunks_count: 3`.

No incluir transcripciones reales ni contenido del curso en docs o commits.

## Criterios de Éxito Iniciales

- El proceso termina sin detenerse por errores globales.
- El video procesado genera audio.
- El Markdown final existe y conserva metadata.
- El manifest marca el archivo como `completed`.
- `output/index.csv` refleja el estado correcto.
- La transcripción es suficientemente literal para estudiar el curso.
