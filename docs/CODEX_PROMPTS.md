# Prompts de Codex

Este archivo resume los prompts principales usados para construir Soma Transcriber. Los prompts completos, patches o borradores temporales pueden guardarse en `.tmp/`, pero `.tmp/` no se versiona.

## Prompt 1: Creación Inicial del Proyecto

Objetivo resumido: crear un proyecto local en Python llamado Soma Transcriber para convertir cursos en video en transcripciones Markdown organizadas por módulos.

Requisitos principales:

- CLI con `--input`, `--output`, `--course-name`, `--model`, `--force`, `--dry-run`.
- Scan recursivo de videos.
- Extracción de audio con FFmpeg.
- División en chunks menores a 24 MB.
- Transcripción literal con OpenAI API.
- Markdown con metadata.
- Manifest para estado por archivo.
- `output/index.csv`.
- README, `.env.example`, `.gitignore`, `requirements.txt`, `config.example.yaml`.

Resultado: base V1 funcional.

## Prompt 2: Mejora V1.1

Objetivo resumido: agregar controles de seguridad operativa y costos antes de transcribir videos reales.

Cambios principales:

- `.gitignore` reforzado con `.tmp/` y `data/`.
- `--max-videos`.
- `--list-videos`.
- dry-run más informativo.
- validación previa de FFmpeg y `OPENAI_API_KEY`.
- prompt fuerte en `config.example.yaml`.
- README actualizado.

Resultado: V1.1 lista para una primera prueba real controlada.

## Uso de `.tmp/`

`.tmp/` puede contener:

- patches generados para revisar con ChatGPT
- prompts completos
- notas temporales
- salidas de comparación

`.tmp/` no debe versionarse ni subirse a GitHub.

## Plantilla para Futuros Prompts

```text
Contexto:
- Estado actual del proyecto.
- Qué ya existe.
- Qué no debe cambiarse.

Objetivo:
- Resultado concreto esperado.

Cambios requeridos:
- Lista clara de archivos, flags, comportamientos o documentación.

Restricciones:
- Qué no ejecutar.
- Qué no borrar.
- Qué no versionar.
- Compatibilidad esperada.

Validaciones:
- Comandos a ejecutar.
- Qué resultados revisar.

Entrega esperada:
- Resumen de archivos creados/modificados.
- Validaciones ejecutadas.
- Notas de riesgo o pendientes.
```
