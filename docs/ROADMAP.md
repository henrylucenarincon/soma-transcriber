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

V1.3.5 deja cerrado el primer módulo real como prueba de producción local: 13/13 videos completados y el caso `input_too_large` resuelto con chunking FFmpeg/FFprobe.

Próximo paso: procesar el curso completo desde la carpeta raíz.

Luego: avanzar a V2 para generar documentos de estudio del curso.

## V1.4: Robustez Después del Primer Test Real

Mejorar el sistema según hallazgos reales:

- errores de FFmpeg
- límites de tamaño
- calidad de Markdown
- reintentos
- logs
- estimación de costo/duración
- selección por índice/rango si hace falta

## V1.5: Soma Studio Local

Crear una interfaz local con Streamlit para controlar el flujo personal encima de la CLI:

- seleccionar curso
- seleccionar perfil YAML
- listar videos
- ejecutar dry-run
- transcribir con controles de seguridad
- reintentar fallidos
- ver rutas de outputs y estado
- preparar la sección visual de Study Pack

Estado: implementado como interfaz local inicial. No tiene login, backend propio, base de datos externa ni modo SaaS.

## V1.6: Primer Curso Completo Procesado

El primer curso real quedó procesado completo: 90 videos detectados, 90 `completed`, 0 `failed`.

V1 queda validado como pipeline completo de transcripción local: detección, orden natural, extracción, chunking, transcripción, Markdown, manifest, index y operación desde CLI/Soma Studio.

Próximo gran bloque: V2 Study Pack.

## V2: Estudio del Curso

Generar Study Pack y documentos de análisis a partir de transcripciones:

- resúmenes por módulo
- conceptos clave
- preguntas de repaso
- glosario
- mapas de temas
- guías de estudio
- prompt maestro para IA
- `AI_STUDY_CONTEXT.md`

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

Evaluar una app local más avanzada si Soma Studio necesita crecer más allá de Streamlit. V1.5 ya cubre el uso personal local inicial.
