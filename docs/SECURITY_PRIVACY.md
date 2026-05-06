# Seguridad y Privacidad

Soma Transcriber trabaja con material privado: cursos adquiridos, audios extraídos, transcripciones y una API key. La seguridad principal del proyecto consiste en mantener esos datos fuera del repositorio.

## No Subir

No debe subirse a GitHub:

- `.env`
- `.env.*` excepto `.env.example`
- videos originales
- audios extraídos
- chunks
- transcripciones privadas
- `output/`
- `outputs/`
- `data/`
- `.tmp/`

## Sí Puede Subirse

Puede subirse al repositorio:

- código fuente en `src/`
- documentación en `docs/`
- `README.md`
- `.env.example`
- `config.example.yaml`
- `requirements.txt`
- `.gitignore`

## Riesgos

API key expuesta: si `.env` se versiona por accidente, la clave debe revocarse y reemplazarse.

Transcripciones privadas versionadas: pueden contener contenido del curso y notas sensibles. No deben entrar al repositorio.

Videos o audios versionados: son archivos pesados y privados. También pueden violar términos de uso si se comparten.

Ejecutar todo el curso sin `--max-videos`: puede generar costos inesperados y mucho output.

Costos duplicados con `--force`: `--force` ignora el estado `completed` y reprocesa archivos. Usarlo solo con intención clara.

## Prácticas Recomendadas

- Empezar pruebas reales con `--max-videos 1`.
- Usar `--list-videos` antes de transcribir.
- Usar `--dry-run` antes de una corrida grande.
- Revisar `git status --short` antes de preparar patches o commits.
- Mantener `.tmp/` para revisión local, pero nunca versionarla.
- No pegar API keys ni transcripciones privadas en prompts.
