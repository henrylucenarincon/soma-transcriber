# Contexto del Proyecto

Soma Transcriber es una herramienta personal para convertir cursos en video en una base de conocimiento estudiable por IA. No está ligado a Mr.CREDITMIND ni a ninguna marca específica. Está pensado para servir con cualquier curso en video: marketing, finanzas, trading, programación, filosofía, ventas, productividad, idiomas o cualquier otro dominio.

El problema que resuelve es práctico: muchos cursos comprados o adquiridos legítimamente quedan atrapados en videos difíciles de buscar, repasar, citar y estudiar con asistencia de IA. Soma Transcriber transforma esos videos en transcripciones literales organizadas por módulos y lecciones, manteniendo la estructura original del curso.

El objetivo no es distribuir contenido de cursos ni republicar material ajeno. El objetivo es convertir cursos adquiridos legítimamente en material privado de estudio, análisis y consulta personal. Por eso los outputs generados, incluyendo audios extraídos, chunks, transcripciones, `output/` y `data/`, no deben subirse a GitHub ni compartirse sin autorización.

La prioridad inicial es la transcripción literal. En esta etapa no se busca resumir, reinterpretar, mejorar, corregir ni transformar el contenido. Primero se necesita capturar fielmente lo que dice el curso. Los resúmenes, mapas conceptuales, preguntas, análisis y documentos derivados vendrán después.

Una "base de conocimiento estudiable por IA" significa un conjunto ordenado de archivos de texto que una IA pueda leer, buscar, comparar y usar como contexto para ayudar a estudiar. En la práctica, esto implica transcripciones Markdown con metadata, estructura por módulos, un manifest de estado y un índice CSV que permita saber qué existe, qué falta y qué fue procesado.

Principios iniciales:

- Mantener el proyecto local y controlado.
- Evitar costos duplicados con `data/manifest.json`.
- Probar de forma incremental con `--max-videos`.
- Mantener privados videos, audios, chunks y transcripciones.
- Usar Codex como ejecutor principal de cambios y mantener documentación viva para conservar contexto entre iteraciones.
