# Roadmap

## V1: Transcripción Literal Ordenada

Crear una CLI local capaz de recorrer un curso, extraer audio, dividir archivos grandes, transcribir literalmente y guardar Markdown manteniendo módulos y lecciones.

Estado: completado como base funcional.

## V1.1: Seguridad Operativa y Control de Costos

Agregar controles para operar con menos riesgo antes de usar videos reales:

- `--max-videos`
- `--list-videos`
- dry-run más informativo
- validación previa de FFmpeg y `OPENAI_API_KEY`
- `.gitignore` reforzado
- README actualizado

Estado: completado.

## V1.2: Documentación Viva

Crear `docs/` con contexto, arquitectura, flujo de datos, decisiones, runbook, testing, privacidad, roadmap, tasks y prompts.

Estado: completado.

## V1.3: Primera Transcripción Real Controlada

Procesar un solo video real con:

```bash
python src/main.py --input "/ruta/curso" --output "./output" --course-name "Curso Demo" --max-videos 1
```

Objetivo: validar el circuito completo antes de escalar.

## V1.4: Robustez Después del Primer Test Real

Mejorar el sistema según hallazgos reales:

- errores de FFmpeg
- límites de tamaño
- calidad de Markdown
- reintentos
- logs
- estimación de costo/duración
- selección por índice/rango si hace falta

## V2: Estudio del Curso

Generar documentos de análisis a partir de transcripciones:

- resúmenes por módulo
- conceptos clave
- preguntas de repaso
- glosario
- mapas de temas
- guías de estudio

## V3: Base Consultable para IA

Convertir el curso transcrito en una base consultable:

- búsqueda por módulo/lección
- recuperación semántica
- preguntas y respuestas con citas
- selección de contexto relevante

## V4: Ejecución de Tareas Aplicando el Curso

Usar el conocimiento del curso para producir entregables concretos:

- planes
- scripts
- checklists
- estrategias
- análisis
- implementaciones guiadas por el contenido estudiado

## V5: Posible Interfaz Local

Evaluar una interfaz local, probablemente Streamlit, solo si hace falta. La CLI sigue siendo suficiente mientras el flujo sea simple y controlado.
