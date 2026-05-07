# Registro de Decisiones

Este archivo registra decisiones relevantes para mantener trazabilidad del proyecto.

## Decisiones Iniciales

- Nombre del proyecto: Soma Transcriber.
- El proyecto es personal y reutilizable, no está ligado a Mr.CREDITMIND.
- Primero se construye una CLI, no una app visual.
- Primero se prioriza transcripción literal, no resúmenes.
- Se usa OpenAI API para transcripción.
- Se usa FFmpeg para extracción de audio.
- Se mantiene la estructura original de módulos y lecciones.
- Se usa `data/manifest.json` para evitar costos duplicados y permitir reanudación.
- Se ignoran `.tmp/`, `output/`, `outputs/`, `data/`, videos, audios y `.env`.
- Los patches temporales pueden guardarse en `.tmp/` para revisión con ChatGPT.
- `.tmp/` no se versiona.
- No se suben transcripciones privadas al repositorio.
- Codex se usa como ejecutor principal de cambios.
- La documentación debe mantenerse actualizada con cada avance relevante.
- Soma no tendrá prompts específicos hardcodeados para un curso. El contexto específico se maneja mediante perfiles YAML opcionales.
- Soma usará FFmpeg/FFprobe para operaciones de audio y evitará depender de librerías Python de audio para chunking debido a compatibilidad con Python 3.13.

## Implicaciones

La arquitectura favorece operación local, privacidad y control de costos por encima de automatizaciones más agresivas. Cada nueva funcionalidad debe respetar esos principios: probar primero con pocos videos, registrar estado, evitar reprocesamiento accidental y no versionar datos privados.
