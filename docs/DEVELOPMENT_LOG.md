# Log de Desarrollo

## 2026-05-06: Entrada Inicial V1

Se creó la base del proyecto Soma Transcriber como CLI local en Python para transcribir cursos en video. La V1 incluye:

- estructura `src/`
- scan recursivo de videos
- extracción de audio con FFmpeg
- chunking para audios mayores a 24 MB
- transcripción con OpenAI API
- Markdown con metadata
- `data/manifest.json`
- `output/index.csv`
- README inicial
- `.env.example`
- `config.example.yaml`
- `.gitignore`

La prioridad de la V1 fue lograr una transcripción literal ordenada, preservando la estructura del curso.

## 2026-05-06: Entrada V1.1

Se aplicaron mejoras de seguridad operativa y control de costos antes de ejecutar transcripciones reales:

- `.gitignore` actualizado con `.tmp/` y `data/`.
- Soporte para `--max-videos`.
- Soporte para `--list-videos`.
- `--dry-run` mejorado con conteo de videos procesables y saltados.
- Validación previa de FFmpeg.
- Validación previa de `OPENAI_API_KEY` solo para transcripción real.
- Prompt más fuerte en `config.example.yaml`.
- README actualizado con flujo recomendado.

## 2026-05-06: Entrada V1.2

Se creó la documentación viva del proyecto en `docs/`:

- contexto del proyecto
- estado actual
- arquitectura
- flujo de datos
- roadmap
- decisiones
- log de desarrollo
- prompts de Codex
- testing
- seguridad y privacidad
- runbook operativo
- tareas completadas y pendientes

La documentación viva queda como fuente principal de contexto para futuras tareas con Codex.

## 2026-05-06: Entrada V1.2.2

Se agregó soporte para archivos `.ts` porque el primer curso real detectado usa MPEG-TS.

- Se actualizó `.gitignore` para ignorar `*.ts` como archivos de video pesados.
- Se actualizó README y documentación viva para reflejar el nuevo formato soportado.
- No se ejecutó transcripción real.

## 2026-05-06: Entrada V1.2.3

Se corrigió el ordenamiento de módulos y videos para usar orden natural.

- Esto evita que `10`, `11` y `12` aparezcan antes de `2`.
- El orden natural se aplica sobre cada parte de la ruta relativa para respetar módulos y lecciones numeradas.
- No se ejecutó transcripción real.

## 2026-05-06: Entrada V1.3

Se ejecutó el primer test real controlado con 1 video.

- Resultado: procesado 1, fallidos 0.
- Se generó audio, `output/index.csv` y transcripción Markdown.
- La metadata quedó correcta y el estado fue `completed`.
- La transcripción fue literal, pero quedó como bloque único de texto.

## 2026-05-06: Entrada V1.3.1

Se agregó formato de párrafos para mejorar legibilidad sin alterar la transcripción literal.

- No se resume el contenido.
- No se reescribe el contenido.
- No se cambia el orden.
- Se conserva la metadata YAML del Markdown.
- No se ejecutó transcripción real durante este ajuste.

## 2026-05-06: Entrada V1.3.2

Se agregaron perfiles universales de configuración por curso.

- Se separó prompt base universal de contexto específico.
- Se agregó construcción de prompt final desde contexto, idioma, nombres propios, glosario y reglas de preservación.
- Se agregaron ejemplos genéricos para español, inglés, marketing, finanzas y trading.
- `configs/local/` queda reservado para perfiles reales privados.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.3.3

Se detectó error `input_too_large` en un video largo del módulo 1 real.

- El archivo fallido fue `12. Cómo tener tus primeros clientes sin resultados.ts`.
- El audio no necesariamente superó el límite por MB, pero sí el límite práctico de audio + instrucciones del modelo.
- Se agregó chunking preventivo por duración configurable con `audio.max_chunk_minutes`.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.3.4

Se detectó que la dependencia anterior para chunking fallaba en Python 3.13 por `audioop`/`pyaudioop`.

- Se reemplazó el chunking con librerías Python de audio por FFmpeg/FFprobe.
- FFprobe obtiene la duración del audio.
- FFmpeg exporta chunks MP3 con los nombres `chunk_001.mp3`, `chunk_002.mp3`, etc.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.3.5

Se reprocesó el módulo 1 completo.

- Resultado: 13/13 videos `completed`.
- El video 12 se dividió en 3 chunks.
- Se validó que FFmpeg/FFprobe resolvió el error `input_too_large`.
- `output/`, `data/` y las transcripciones privadas no deben versionarse.

## 2026-05-06: Entrada V1.5

Se agregó Soma Studio Local con Streamlit.

- La interfaz es personal/local.
- Ejecuta la CLI con `subprocess` y `sys.executable`.
- Permite listar videos, dry-run, transcribir y reintentar fallidos.
- Muestra estado local desde `output/index.csv` y resumen de `data/manifest.json`.
- Deja preparada una sección para Study Pack V2.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.1

Se mejoró la experiencia de Soma Studio Local.

- Se agregó selector local de carpetas para curso/output.
- Se mantiene input manual como respaldo.
- Se aclaró el comportamiento de `max_videos`.
- Se refuerza que `max_videos = 1` es recomendado para pruebas y `0` significa sin límite.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.2

Se corrigió el selector de carpetas en macOS.

- Se reemplazó la dependencia principal de `tkinter` por `osascript`/AppleScript en macOS.
- `tkinter` queda como fallback si el selector nativo no está disponible.
- El input manual queda como fallback final.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.3

Se corrigió el manejo de `session_state` en Soma Studio para seleccionar carpetas sin error en Streamlit.

- Las rutas seleccionadas usan keys internas separadas de las keys de los widgets.
- El input manual sigue funcionando como respaldo.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.5.4

Se corrigió la sincronización entre selector de carpetas y `text_input` en Soma Studio.

- El selector ahora actualiza las keys visibles del widget.
- Se guarda la última ruta seleccionada para confirmación visual.
- No se ejecutó transcripción real durante esta tarea.

## 2026-05-06: Entrada V1.6

Se procesó completo el primer curso real.

- Resultado: 90/90 videos `completed`, 0 `failed`.
- Se corrigió el nombre de salida del curso a `Victor Heras - Marca Personal 5.0`.
- El `original_path` se mantiene apuntando a la ruta real del curso fuente.
- `output/` y `data/` siguen siendo privados y no se versionan.
- Próximo paso: V2 Study Pack para convertir transcripciones en conocimiento estudiable por IA.

## 2026-05-06: Entrada V2.0

Se agregó Study Pack Builder.

- Permite generar notas por video, resúmenes por módulo y documentos globales para IA.
- La implementación inicial vive en `src/study_pack.py`, `src/study_prompts.py`, `src/study_writer.py` y `src/study_manifest.py`.
- El flujo V2 trabaja desde transcripciones privadas hacia `output/study/`.
- No debe incluir transcripciones completas ni largos fragmentos verbatim dentro del Study Pack.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.1

Se mejoraron los prompts de Study Pack para generar `video-notes` más profundas y accionables.

- Las primeras pruebas reales de `video-notes` funcionaron técnicamente, pero quedaron demasiado resumidas.
- Las `video-notes` ahora deben extraer principios, mecanismos, frameworks implícitos, aplicaciones e instrucciones para IA.
- Los resúmenes de módulo también quedan preparados para consumir notas más profundas.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.2

Se ajustaron prompts para clases introductorias o mapas de módulo.

- Las clases introductorias, de bienvenida, onboarding, cierre o mapa ya no deben forzar principios centrales estrechos.
- Si una clase presenta el recorrido del módulo, la nota debe extraer la función de la lección y la arquitectura del módulo.
- Se reforzó que no deben inventarse principios, frameworks ni ejemplos cuando no aparecen explícitamente.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.3

Se agregó detección de clases introductorias por título/ruta.

- Las introducciones ahora se tratan como mapas o arquitectura del módulo.
- Se evita reducir una introducción a un framework operativo artificial.
- La detección soporta términos como introducción, intro, bienvenida, overview, mapa, onboarding, cierre y conclusión.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.4

Se separó el tratamiento de clases introductorias y operativas.

- Las introductorias usan arquitectura del módulo.
- Las operativas usan framework operativo real o implícito.
- Se corrigió el riesgo de usar arquitectura del módulo en clases operativas.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.5

Se mejoraron prompts de `module summaries`.

- El objetivo es generar síntesis metodológicas profundas y no resúmenes genéricos.
- Los resúmenes de módulo ahora deben conectar lecciones, extraer el sistema operativo del módulo y consolidar ejemplos desde las `video-notes`.
- También deben convertir conceptos en reglas prácticas e instrucciones útiles para IA.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.6

Se reforzaron los prompts de `module summaries` para convertirlos en Module Operating Systems.

- El objetivo es evitar resúmenes genéricos y producir síntesis metodológicas accionables para IA.
- El prompt ahora prioriza profundidad, especificidad y aplicabilidad sobre brevedad.
- Se agregó una autoevaluación interna para revisar lecciones, frameworks, conexiones, reglas aplicables y ejemplos antes de responder.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.7

Se reforzó el enfoque evidence-based para `module summaries`.

- Cada ejemplo, framework, principio o regla debe estar respaldado por `video-notes`.
- Se busca evitar ejemplos genéricos, casos hipotéticos, frameworks inventados o conocimiento externo.
- Los documentos globales del Study Pack también quedan preparados para mantener fidelidad a la evidencia interna.
- No se ejecutó generación real durante esta tarea.

## 2026-05-06: Entrada V2.0.8

Se agregó enfoque coverage-based a los Module Operating Systems.

- Los `module summaries` deben cubrir todas las `video-notes` detectadas.
- Se agregó Coverage Matrix obligatorio.
- Se reforzó el checklist operativo para IA para cubrir todo el recorrido del módulo.
- Si hay conflicto entre brevedad y cobertura, se prioriza cobertura.
- No se ejecutó generación real durante esta tarea.

## Validaciones Ejecutadas

```bash
python3 -m compileall src
python3 src/main.py --help
```

Comandos probados sin API:

```bash
python3 src/main.py --input /private/tmp/soma-course --output /private/tmp/soma-output --course-name Curso\ Demo --list-videos --max-videos 1
python3 src/main.py --input /private/tmp/soma-course --output /private/tmp/soma-output --course-name Curso\ Demo --dry-run --max-videos 1
```

## Nota

Ya se ejecutó un primer test real con 1 video, el módulo 1 completo y el curso completo. Todavía no se ha ejecutado generación real del Study Pack.
