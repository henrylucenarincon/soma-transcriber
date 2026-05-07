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

Ver ayuda de Study Pack Builder:

```bash
python3 src/study_pack.py --help
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

La selección de carpeta se valida manualmente abriendo Soma Studio Local:

- Presionar `Seleccionar carpeta`.
- Confirmar que abre Finder en macOS.
- Seleccionar la carpeta del curso.
- Confirmar que la ruta se completa en el sidebar.
- Probar `Seleccionar output` si hace falta.

Si el selector falla, la UI debe permitir continuar pegando la ruta manualmente.

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

## Validación Final del Curso Completo

Comandos locales sobre outputs privados:

```bash
find output/transcripts -type f -name "*.md" | sort | wc -l
grep -c "completed" output/index.csv
grep -c "failed" output/index.csv
```

Resultado esperado:

```text
90
90
0
```

Estos archivos son locales/privados. `output/` y `data/` no se suben al repositorio.

## Validación V2 Study Pack

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

Prueba real controlada recomendada para V2:

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

Regenerar las 2 `video-notes` de prueba después de ajustar prompts:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0/3. Cómo hacer contenido viral en 5 pasos" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0 - Test Modulo 3" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase video-notes \
  --max-videos 2 \
  --force
```

Después de regenerar, revisar que cada nota incluya principios, mecanismos, frameworks implícitos, aplicaciones prácticas, errores que evita e instrucciones concretas para IA.

Después de V2.0.3, usar el mismo comando para validar que una clase introductoria se trate como mapa o arquitectura del módulo, sin forzar un framework operativo artificial:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0/3. Cómo hacer contenido viral en 5 pasos" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0 - Test Modulo 3" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase video-notes \
  --max-videos 2 \
  --force
```

Después de V2.0.4, la validación de calidad debe revisar dos casos:

- `0. Introducción` debe usar arquitectura del módulo.
- `1. Sé el referente de lo que tu cliente quiere ser` debe usar framework operativo, no arquitectura del módulo.

Regenerar el `module summary` del módulo 3 después de ajustar prompts:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0/3. Cómo hacer contenido viral en 5 pasos" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0 - Test Modulo 3" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase module-summaries \
  --force
```

Después de V2.0.5, revisar que el `module summary` conecte las lecciones, extraiga la secuencia metodológica, consolide ejemplos desde las `video-notes`, convierta conceptos en reglas prácticas y dé instrucciones útiles para una IA.

Después de V2.0.6, el mismo comando debe regenerar un Module Operating System del módulo:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0/3. Cómo hacer contenido viral en 5 pasos" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0 - Test Modulo 3" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase module-summaries \
  --force
```

Revisar que el documento resultante no sea un resumen ejecutivo: debe incluir tesis central, sistema operativo del módulo, secuencia de aplicación, función de cada lección, frameworks, mapa de relaciones, ejemplos detectados, reglas prácticas, checklist operativo para IA e instrucciones de uso.

Después de V2.0.7, validar además el enfoque evidence-based:

- No debe incluir ejemplos no presentes en `video-notes`.
- Cada framework debe mencionar lecciones que lo respaldan.
- Cada principio debe tener respaldo interno.
- Si no hay evidencia suficiente, debe decirlo.
- No debe usar ejemplos genéricos de marketing.
- No debe convertir conocimiento general externo en contenido del curso.

Después de V2.0.8, validar además cobertura completa:

- El module summary debe incluir todas las `video-notes`.
- Debe incluir la última lección del módulo.
- El checklist debe cubrir todo el recorrido.
- Los frameworks deben incluir todas las herramientas importantes detectadas.
- Ninguna lección detectada debe quedar fuera del Coverage Matrix.

Regenerar solo el Course Pack maestro después de V2.1:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase course-pack \
  --force
```

Después de V2.1, validar especialmente `03_CORE_PRINCIPLES.md`, `04_FRAMEWORKS.md`, `07_APPLICATION_GUIDE.md`, `08_AI_STUDY_CONTEXT.md` y `09_MASTER_PROMPT_FOR_AI.md`. Deben ser profundos, evidence-based, accionables y útiles para que una IA estudie y aplique la metodología del curso.

No ejecutar generación real durante tareas de documentación o refactor. `output/study/` y `data/study_manifest.json` son privados y no se suben al repositorio.

## Criterios de Éxito Iniciales

- El proceso termina sin detenerse por errores globales.
- El video procesado genera audio.
- El Markdown final existe y conserva metadata.
- El manifest marca el archivo como `completed`.
- `output/index.csv` refleja el estado correcto.
- La transcripción es suficientemente literal para estudiar el curso.
