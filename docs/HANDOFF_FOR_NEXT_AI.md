# Soma Transcriber — Handoff para próxima IA

> **Actualizado 2026-05-07:** V2 migrado a Claude Sonnet 4.6 con prompt caching. Soma Studio rediseñado con FastAPI. Ver secciones actualizadas abajo.

Este documento resume el estado real del proyecto para que otra IA o desarrollador pueda continuar sin perder contexto. Debe leerse junto con `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `TASKS.md`, `TESTING.md` y `DEVELOPMENT_LOG.md`.

## 1. Visión del proyecto

Soma Transcriber es un proyecto personal para convertir cursos completos en video en conocimiento estudiable por IA. No es Mr.CREDITMIND, no es una app pública, no es SaaS, no es multiusuario y no está pensado para clientes. Es una herramienta local para el dueño del proyecto.

El proyecto existe porque el usuario quiere trabajar con IA usando conocimiento real de cursos estudiados, no respuestas genéricas. Antes de pedirle a una IA que haga guiones, estrategias, análisis o tareas, quiere poder darle un curso completo ya procesado para que la IA entienda la metodología, los principios, los frameworks y los ejemplos del curso.

El objetivo no es solo transcribir. La visión completa es:

```text
curso en video
→ transcripciones literales
→ notas de estudio por video
→ sistemas operativos por módulo
→ documentos maestros de Study Pack
→ contexto listo para ChatGPT, Claude, Codex u otra IA
```

La meta final es reducir respuestas genéricas y lograr que la IA responda aplicando el conocimiento del curso estudiado.

## 2. Alcance actual del proyecto

Ya existe una base funcional con:

- CLI de transcripción en Python.
- Extracción de audio con FFmpeg.
- Chunking por tamaño y duración con FFmpeg/FFprobe.
- OpenAI Whisper para transcripción de audio (no reemplazable por Claude).
- **Claude Sonnet 4.6 con prompt caching para Study Pack** (V2.3).
- Soporte para videos `.ts`.
- Orden natural de módulos y lecciones.
- Markdown con metadata.
- Manifest local e `index.csv`.
- Perfiles YAML por curso.
- **Soma Studio rediseñado con FastAPI** (V1.5.5) — `app/server.py`, `app/static/`.
- Study Pack Builder completo con Evidence Layer y Quality Report.

La parte de transcripción V1 está validada (90/90 videos). V2 Study Pack está construido y migrado a Claude, pero la calidad de los documentos maestros (`08`, `09`) aún necesita validación con una generación real.

## 3. Estructura actual del proyecto

Carpetas y archivos principales:

```text
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

app/
  streamlit_app.py

configs/
  examples/
  local/        # privado, no versionado

docs/
  documentación viva del proyecto

output/         # privado, no versionado
data/           # privado, no versionado
.tmp/           # privado, patches temporales, no versionado
```

Responsabilidades rápidas:

- `src/main.py`: CLI de transcripción literal.
- `src/scanner.py`: detección recursiva de videos y orden natural.
- `src/audio.py`: extracción de audio y chunking con FFmpeg/FFprobe.
- `src/transcriber.py`: llamadas de transcripción a OpenAI.
- `src/manifest.py`: estado de archivos procesados.
- `src/writer.py`: escritura de Markdown e índice CSV.
- `src/study_pack.py`: CLI V2 para generar Study Pack.
- `src/study_prompts.py`: prompts y templates de video-notes, module-notes, evidence layer y course-pack.
- `src/study_writer.py`: escritura de documentos del Study Pack.
- `src/study_manifest.py`: manifest de V2.
- `app/streamlit_app.py`: Soma Studio Local, UI Streamlit encima de la CLI.

## 4. Estado V1 — Transcripción literal

V1 está validado con un curso real completo.

Resultado validado localmente:

- Curso real procesado: Victor Heras - Marca Personal 5.0.
- Videos detectados: 90.
- Transcripciones generadas: 90.
- `completed`: 90.
- `failed`: 0.
- Output final corregido:

```text
output/transcripts/Victor Heras - Marca Personal 5.0/
```

Problemas resueltos durante V1:

- Soporte para archivos `.ts` porque el curso real venía en MPEG-TS.
- Orden natural para que módulo 10 no aparezca antes que módulo 2.
- Chunking preventivo por duración para evitar `input_too_large`.
- Reemplazo de `pydub` por FFmpeg/FFprobe por incompatibilidad con Python 3.13 y `audioop`.
- Perfil YAML local privado para mejorar precisión de transcripción.
- Markdown con párrafos legibles sin resumir ni reescribir la transcripción literal.

V1 debe considerarse una base funcional confiable para transcripción local.

## 5. Estado V1.5.5 — Soma Studio rediseñado

Soma Studio fue rediseñado completamente con FastAPI + HTML/CSS/JS puro.

Iniciar: `python app/server.py` → `http://127.0.0.1:8899`

Archivos:

- `app/server.py`: backend FastAPI con 12 rutas.
- `app/static/index.html`: UI single-page.
- `app/static/app.css`: dark theme minimal (zinc + violet).
- `app/static/app.js`: lógica frontend, fetch streaming.
- `app/streamlit_app.py`: interfaz legacy conservada como fallback.

Funcionalidades:

- Tab Transcripción: listar videos, dry-run, transcribir, reintentar fallidos.
- Tab Study Pack: selector de fase, dry-run, generar.
- Tab Estado: conteos de manifest y study_manifest, checks de archivos, tabla índice CSV.
- Streaming de output en tiempo real vía `StreamingResponse` + `fetch` ReadableStream.
- Selector nativo de carpetas macOS con `osascript`.
- Confirmación antes de procesar sin límite de videos.
- Coloreado de líneas de output (ok/error/warning/accent).

Características:

- Local y personal.
- Sin login, sin backend externo, sin base de datos externa, sin modo SaaS.
- El streaming resuelve el problema de "UI congelada" que tenía la versión Streamlit.

## 6. Estado V2 — Study Pack Builder

V2 existe, pero todavía está en proceso de calidad.

Ya se generó técnicamente:

- 90 video-notes.
- 11 module-notes.
- 10 archivos maestros del Course Pack.
- `_course_pack_evidence/` como capa intermedia de evidencia.
- `99_QUALITY_REPORT.md`.

Pero el Study Pack maestro todavía no está aprobado. La calidad de los documentos globales necesita revisión y mejora estructural.

## 7. Qué funciona bien en V2

Las video-notes mejoraron bastante después de varios ajustes. Ya no son solo resúmenes planos; buscan extraer:

- resumen fiel;
- principio central;
- mecanismo;
- framework operativo;
- conceptos;
- ejemplos;
- aplicación práctica;
- instrucciones para IA.

También se corrigió el tratamiento de clases introductorias:

- una intro, bienvenida, overview, mapa, onboarding, cierre o conclusión se trata como arquitectura del módulo;
- una clase operativa normal debe extraer framework operativo real o implícito.

Se validó especialmente el módulo 3 con 15 video-notes. Los module summaries también mejoraron con Coverage Matrix y el enfoque de Module Operating System.

## 8. Problemas encontrados en V2

### Problema 1: video-notes demasiado genéricas al inicio

Las primeras notas parecían resúmenes escolares. Se corrigió parcialmente reforzando prompts para pedir principios, mecanismos, frameworks, aplicaciones e instrucciones para IA.

### Problema 2: clases introductorias mal interpretadas

La clase `0. Introducción` se trataba como si fuera una clase operativa. Se corrigió agregando detección de intro, bienvenida, overview, mapa, onboarding, cierre y conclusión.

### Problema 3: clases operativas tratadas como arquitectura de módulo

Después de corregir intro, una clase operativa empezó a usar `Arquitectura del módulo`. Se corrigió separando comportamiento:

- intro o mapa → arquitectura del módulo;
- clase operativa → framework operativo real o implícito.

### Problema 4: module summaries superficiales

Los module summaries inicialmente eran resúmenes genéricos. Se reforzaron como `Module Operating Systems`.

### Problema 5: module summaries omitían lecciones/frameworks

El módulo 3 inicialmente omitía la lección 15 y frameworks importantes como ViralCopy, CTA, ganchos, métricas y otros componentes. Se corrigió con Coverage Matrix y reglas coverage-based.

### Problema 6: course-pack maestro superficial

Los 10 archivos maestros generados seguían siendo demasiado genéricos, especialmente:

- `03_CORE_PRINCIPLES.md`
- `04_FRAMEWORKS.md`
- `07_APPLICATION_GUIDE.md`
- `08_AI_STUDY_CONTEXT.md`
- `09_MASTER_PROMPT_FOR_AI.md`

### Problema 7: AI_STUDY_CONTEXT y MASTER_PROMPT demasiado débiles

Los archivos 08 y 09 todavía no son suficientemente fuertes como onboarding/protocolo para IA. Deben guiar cómo estudiar el pack, cómo priorizar la metodología del curso, cómo pedir contexto faltante y cómo evitar respuestas genéricas.

### Problema 8: V2.2 Evidence Layer empezó a implementarse, pero no está validado

Se propuso y empezó a implementar:

- `_course_pack_evidence/`
- inventarios intermedios;
- `99_QUALITY_REPORT.md`.

Todavía no está validado como solución final.

### Problema 9: Quality Report daba falsos MISSING

El reporte puede marcar módulos como missing aunque aparezcan con otra forma, por ejemplo:

```text
Módulo 1: Cómo funciona el algoritmo
```

frente a:

```text
1. Como funciona el algoritmo
```

Se propuso mejorar la normalización para reducir falsos positivos.

## 9. Estado exacto del último trabajo (actualizado 2026-05-07)

El último trabajo entregado fue V2.3 (Claude) + V1.5.5 (FastAPI UI).

Course Pack Evidence Layer:

```text
_course_pack_evidence/
  00_MODULE_COVERAGE_MATRIX.md
  01_PRINCIPLES_INVENTORY.md
  02_FRAMEWORKS_INVENTORY.md
  03_CONCEPTS_INVENTORY.md
  04_EXAMPLES_INVENTORY.md
  05_APPLICATIONS_INVENTORY.md
  06_AI_TASKS_INVENTORY.md
```

Objetivo del enfoque:

- Los 10 archivos maestros no deben generarse directamente desde `module_notes` completos.
- Primero deben generarse inventarios intermedios.
- Los master docs deben usar `evidence_docs` como fuente principal.
- `module_notes` deben pasarse solo como índice de cobertura.

El cambio V2.2.1 corrigió el riesgo de prompts gigantes:

- antes, los documentos maestros recibían todos los `evidence_docs` completos y todos los `module_notes` completos;
- ahora, deben recibir los `evidence_docs` completos y un índice liviano de `module_notes`;
- esto reduce costo, lentitud y riesgo de `input_too_large`.

Este cambio debe revisarse cuidadosamente antes de continuar.

## 10. Decisión importante de arquitectura

La arquitectura correcta para V2 debería ser:

```text
Transcripciones literales
→ video-notes
→ module-notes
→ evidence layer
→ master course-pack files
→ quality report
→ AI-ready context / master prompt
```

No se debe generar el master course-pack directamente desde transcripciones ni desde `module_notes` completos en cada llamada, porque:

- sale genérico;
- puede exceder tamaño;
- cuesta más;
- el modelo se pierde;
- es difícil validar cobertura;
- vuelve más probable que el modelo invente o rellene.

## 11. Qué falta por hacer

Lista concreta para la próxima IA:

1. Agregar `ANTHROPIC_API_KEY` real en `.env`.
2. Regenerar `course-pack` con `--force` y validar `_course_pack_evidence/`.
3. Validar `99_QUALITY_REPORT.md` — corregir falsos MISSING si aparecen.
4. Revisar calidad de `08_AI_STUDY_CONTEXT.md` como onboarding real para IA.
5. Revisar calidad de `09_MASTER_PROMPT_FOR_AI.md` como prompt maestro robusto.
6. Probar que una IA externa (ChatGPT, Claude) da guiones específicos del curso desde el Study Pack.
7. Agregar export ZIP desde Soma Studio.
8. Crear vista de revisión por muestreo.
9. Agregar estimación de costo/duración de API.

## 12. Recomendación para la próxima IA

La próxima IA no debe seguir haciendo microajustes aislados. El usuario está frustrado porque los prompts anteriores generaron demasiados ciclos de pequeñas correcciones.

Debe enfocarse en:

- arquitectura;
- evidence layer;
- quality gates;
- validación programática;
- reducción de prompts gigantes;
- calidad final de master docs;
- cobertura completa de módulos y frameworks;
- utilidad real para que otra IA trabaje con el curso.

Debe evitar:

- regenerar todo sin razón;
- tocar transcripciones;
- tocar output privado innecesariamente;
- modificar perfiles locales privados;
- inventar ejemplos o contenido del curso;
- hacer commits sin patch/revisión;
- pedir regeneraciones repetidas sin haber revisado antes la arquitectura y la calidad esperada.

## 13. Comandos útiles

Validar transcripciones:

```bash
find "output/transcripts/Victor Heras - Marca Personal 5.0" -type f -name "*.md" | wc -l
grep -c "completed" output/index.csv
grep -c "failed" output/index.csv
```

Generar video-notes:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase video-notes
```

Generar module summaries:

```bash
python3 src/study_pack.py \
  --transcripts "./output/transcripts/Victor Heras - Marca Personal 5.0" \
  --index "./output/index.csv" \
  --output "./output/study" \
  --course-name "Victor Heras - Marca Personal 5.0" \
  --config "configs/local/victor-heras-marca-personal-5.yaml" \
  --phase module-summaries \
  --force
```

Generar course-pack:

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

Crear ZIP de revisión completo:

```bash
zip -r .tmp/review_packs/soma_course_pack_full_review.zip \
  "output/study/Victor Heras - Marca Personal 5.0/_course_pack_evidence" \
  "output/study/Victor Heras - Marca Personal 5.0/"*.md
```

## 14. Archivos privados que NO deben versionarse

No versionar:

- `.env`
- `output/`
- `data/`
- `.tmp/`
- `configs/local/`
- videos
- audios
- transcripciones privadas
- study packs privados

Sí se pueden versionar:

- código fuente;
- documentación;
- `README.md`;
- `.env.example`;
- `config.example.yaml`;
- `configs/examples/`;
- `requirements.txt`.

## 15. Flujo de trabajo con patches

Flujo obligatorio para revisar cambios antes de commit:

```bash
cd /Users/henry/Documents/soma-transcriber

git status --short

mkdir -p .tmp

git add -A

git diff --cached --stat

git diff --cached > .tmp/<nombre_del_patch>.patch
```

No hacer commit sin que el usuario revise o pida explícitamente el commit.

## 16. Validaciones base

Validaciones mínimas antes de entregar cambios:

```bash
python3 -m compileall src app
python3 src/main.py --help
python3 src/study_pack.py --help
.venv/bin/python -c "import streamlit; print('streamlit OK')"
```

Para cambios de UI, además abrir Soma Studio manualmente:

```bash
.venv/bin/streamlit run app/streamlit_app.py
```

No ejecutar transcripción real ni generación real con OpenAI salvo que el usuario lo pida explícitamente.

## 17. Última nota para próxima IA

El usuario está frustrado porque los prompts anteriores generaron demasiados ciclos de microajustes. La siguiente IA debe priorizar una solución completa, revisando arquitectura, calidad y cobertura antes de pedir regeneraciones repetidas.

El objetivo no es que los documentos suenen bonitos. El objetivo es que una IA pueda estudiar el curso, aplicar su metodología y dejar de responder desde conocimiento genérico.
