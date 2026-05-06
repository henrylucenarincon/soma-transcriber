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

No se ha ejecutado todavía una transcripción real.
