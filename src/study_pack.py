from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
from typing import Any, Iterable, Sequence, TypeVar
import unicodedata

try:
    from .study_manifest import STATUS_COMPLETED, STATUS_FAILED, StudyManifest
    from .study_prompts import (
        COURSE_EVIDENCE_DOCUMENTS,
        GLOBAL_DOCUMENTS,
        StudySettings,
        build_course_document_prompt,
        build_course_evidence_prompt,
        build_module_summary_prompt,
        build_video_note_merge_prompt,
        build_video_note_prompt,
    )
    from .study_writer import (
        TranscriptDocument,
        build_module_note_path,
        build_study_paths,
        build_video_note_path,
        discover_transcripts,
        group_transcripts_by_module,
        list_module_notes,
        list_video_notes,
        module_note_name,
        read_markdown,
        read_transcript,
        split_text_chunks,
        write_markdown,
    )
    from .utils import config_get, load_config, truncate_error
except ImportError:
    from study_manifest import STATUS_COMPLETED, STATUS_FAILED, StudyManifest
    from study_prompts import (
        COURSE_EVIDENCE_DOCUMENTS,
        GLOBAL_DOCUMENTS,
        StudySettings,
        build_course_document_prompt,
        build_course_evidence_prompt,
        build_module_summary_prompt,
        build_video_note_merge_prompt,
        build_video_note_prompt,
    )
    from study_writer import (
        TranscriptDocument,
        build_module_note_path,
        build_study_paths,
        build_video_note_path,
        discover_transcripts,
        group_transcripts_by_module,
        list_module_notes,
        list_video_notes,
        module_note_name,
        read_markdown,
        read_transcript,
        split_text_chunks,
        write_markdown,
    )
    from utils import config_get, load_config, truncate_error


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"
DEFAULT_STUDY_MANIFEST_PATH = PROJECT_ROOT / "data" / "study_manifest.json"
DEFAULT_STUDY_MODEL = "gpt-4o-mini"
PHASE_VIDEO_NOTES = "video-notes"
PHASE_MODULE_SUMMARIES = "module-summaries"
PHASE_COURSE_PACK = "course-pack"
PHASE_ALL = "all"
T = TypeVar("T")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="soma-study-pack",
        description="Genera Study Packs privados a partir de transcripciones Markdown de Soma.",
    )
    parser.add_argument(
        "--transcripts",
        required=True,
        type=Path,
        help="Carpeta raíz de transcripciones Markdown del curso.",
    )
    parser.add_argument(
        "--index",
        type=Path,
        help="Ruta opcional a output/index.csv para referencia operativa.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Carpeta donde se generará el Study Pack.",
    )
    parser.add_argument("--course-name", required=True, help="Nombre del curso.")
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        type=Path,
        help="Ruta opcional a YAML de configuración. Default: config.yaml",
    )
    parser.add_argument(
        "--model",
        help=f"Modelo de análisis de OpenAI. Default configurable: {DEFAULT_STUDY_MODEL}",
    )
    parser.add_argument("--dry-run", action="store_true", help="Listar lo que se haría sin llamar a OpenAI.")
    parser.add_argument("--max-videos", type=positive_int, help="Procesar solo N transcripciones para pruebas.")
    parser.add_argument("--force", action="store_true", help="Regenerar aunque ya exista en el manifest.")
    parser.add_argument(
        "--phase",
        choices=[PHASE_VIDEO_NOTES, PHASE_MODULE_SUMMARIES, PHASE_COURSE_PACK, PHASE_ALL],
        default=PHASE_ALL,
        help="Fase a ejecutar. Default: all.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    load_env_file()

    config = load_study_config(args.config, dry_run=args.dry_run)
    settings = build_study_settings(config=config, cli_model=args.model)
    transcripts_root = args.transcripts.expanduser().resolve()
    output_dir = args.output.expanduser().resolve()
    study_paths = build_study_paths(output_dir, args.course_name)

    transcript_paths = discover_transcripts(transcripts_root)
    selected_paths = limit_items(transcript_paths, args.max_videos)

    if args.dry_run:
        print_dry_run(args, transcripts_root, selected_paths, transcript_paths, study_paths, settings)
        return 0

    validate_openai_api_key()
    client = build_openai_client()
    manifest = StudyManifest.load(DEFAULT_STUDY_MANIFEST_PATH)

    if args.phase in {PHASE_VIDEO_NOTES, PHASE_ALL}:
        video_failures = generate_video_notes(
            client=client,
            transcripts_root=transcripts_root,
            transcript_paths=selected_paths,
            course_name=args.course_name,
            study_paths=study_paths,
            settings=settings,
            manifest=manifest,
            force=args.force,
        )
        if video_failures:
            manifest.save()
            print(
                "ERROR: Hay video-notes fallidas. Corrige o reintenta antes de "
                "generar module-summaries/course-pack."
            )
            return 1

    if args.phase in {PHASE_MODULE_SUMMARIES, PHASE_ALL}:
        generate_module_summaries(
            client=client,
            transcripts_root=transcripts_root,
            transcript_paths=selected_paths,
            course_name=args.course_name,
            study_paths=study_paths,
            settings=settings,
            manifest=manifest,
            force=args.force,
        )

    if args.phase in {PHASE_COURSE_PACK, PHASE_ALL}:
        generate_course_pack(
            client=client,
            course_name=args.course_name,
            study_paths=study_paths,
            settings=settings,
            manifest=manifest,
            force=args.force,
        )

    manifest.save()
    print(f"Study Pack listo: {study_paths.course_dir}")
    return 0


def build_study_settings(config: dict[str, Any], cli_model: str | None) -> StudySettings:
    return StudySettings(
        model=str(cli_model or config_get(config, "study", "model", default=DEFAULT_STUDY_MODEL) or DEFAULT_STUDY_MODEL),
        output_language=str(config_get(config, "study", "output_language", default="same-as-course")),
        max_chars_per_analysis_chunk=int(
            config_get(config, "study", "max_chars_per_analysis_chunk", default=25000) or 25000
        ),
        include_short_quotes=bool(config_get(config, "study", "include_short_quotes", default=False)),
        quote_max_words=int(config_get(config, "study", "quote_max_words", default=20) or 20),
        avoid_external_knowledge=bool(config_get(config, "study", "avoid_external_knowledge", default=True)),
    )


def load_study_config(config_path: Path | None, dry_run: bool) -> dict[str, Any]:
    try:
        return load_config(config_path)
    except RuntimeError as exc:
        if dry_run and "pyyaml" in str(exc).lower():
            print(f"WARNING: {exc} Se usarán defaults de Study Pack para este dry-run.")
            return {}
        raise


def generate_video_notes(
    *,
    client: Any,
    transcripts_root: Path,
    transcript_paths: list[Path],
    course_name: str,
    study_paths: Any,
    settings: StudySettings,
    manifest: StudyManifest,
    force: bool,
) -> int:
    failed = 0
    for transcript_path in progress(transcript_paths, desc="Generando video-notes", unit="nota"):
        transcript = read_transcript(transcript_path, transcripts_root)
        video_note_path = build_video_note_path(study_paths, transcript)
        manifest.ensure_pending(transcript.path, transcript.relative_path)

        existing_record = manifest.get_record(transcript.path)
        if should_skip_video_note(existing_record, video_note_path, force):
            continue

        manifest.mark_processing(transcript.path, transcript.relative_path, video_note_path)
        manifest.save()

        try:
            content = generate_single_video_note(
                client=client,
                transcript=transcript,
                course_name=course_name,
                settings=settings,
            )
            write_markdown(video_note_path, content)
            manifest.mark_completed(transcript.path, transcript.relative_path, video_note_path)
        except Exception as exc:
            failed += 1
            print(f"ERROR video-note: {transcript.relative_path.as_posix()} -> {exc}")
            manifest.mark_failed(transcript.path, transcript.relative_path, exc, video_note_path)
        finally:
            manifest.save()

    return failed


def generate_single_video_note(
    *,
    client: Any,
    transcript: TranscriptDocument,
    course_name: str,
    settings: StudySettings,
) -> str:
    chunks = split_text_chunks(transcript.transcript_text, settings.max_chars_per_analysis_chunk)
    if not chunks:
        raise ValueError(f"La transcripción no tiene contenido literal: {transcript.relative_path.as_posix()}")

    partial_notes: list[str] = []
    chunks_count = len(chunks)
    for index, chunk in enumerate(chunks, start=1):
        prompt = build_video_note_prompt(
            course_name=course_name,
            module_path=transcript.module_path,
            video_title=transcript.video_title,
            relative_path=transcript.relative_path,
            transcript_chunk=chunk,
            chunk_index=index,
            chunks_count=chunks_count,
            settings=settings,
        )
        partial_notes.append(call_openai_text(client, model=settings.model, prompt=prompt))

    if len(partial_notes) == 1:
        return partial_notes[0]

    merge_prompt = build_video_note_merge_prompt(
        course_name=course_name,
        module_path=transcript.module_path,
        video_title=transcript.video_title,
        relative_path=transcript.relative_path,
        partial_notes=partial_notes,
        settings=settings,
    )
    return call_openai_text(client, model=settings.model, prompt=merge_prompt)


def generate_module_summaries(
    *,
    client: Any,
    transcripts_root: Path,
    transcript_paths: list[Path],
    course_name: str,
    study_paths: Any,
    settings: StudySettings,
    manifest: StudyManifest,
    force: bool,
) -> None:
    transcripts = [read_transcript(path, transcripts_root) for path in transcript_paths]
    grouped = group_transcripts_by_module(transcripts)

    for module_path, module_transcripts in progress(grouped.items(), desc="Generando module-notes", unit="módulo"):
        module_note_path = build_module_note_path(study_paths, module_path)
        if module_note_path.exists() and not force:
            continue

        video_notes: list[tuple[str, str]] = []
        for transcript in module_transcripts:
            video_note_path = build_video_note_path(study_paths, transcript)
            if not video_note_path.exists():
                raise FileNotFoundError(
                    f"Falta video-note para generar resumen de módulo: {video_note_path}"
                )
            video_notes.append((transcript.relative_path.as_posix(), read_markdown(video_note_path)))

        module_name = module_path or "Curso"
        prompt = build_module_summary_prompt(
            course_name=course_name,
            module_name=module_name,
            video_notes=video_notes,
            settings=settings,
        )
        content = call_openai_text(client, model=settings.model, prompt=prompt)
        write_markdown(module_note_path, content)
        manifest.set_global_output(f"module::{module_note_name(module_path)}", module_note_path, STATUS_COMPLETED)
        manifest.save()


def generate_course_pack(
    *,
    client: Any,
    course_name: str,
    study_paths: Any,
    settings: StudySettings,
    manifest: StudyManifest,
    force: bool,
) -> None:
    module_note_paths = list_module_notes(study_paths.module_notes_dir)
    if not module_note_paths:
        raise FileNotFoundError(
            f"No hay module_notes para generar el course-pack: {study_paths.module_notes_dir}"
        )

    module_notes = [
        (path.relative_to(study_paths.course_dir).as_posix(), read_markdown(path))
        for path in module_note_paths
    ]
    evidence_docs = generate_course_pack_evidence(
        client=client,
        course_name=course_name,
        study_paths=study_paths,
        module_notes=module_notes,
        settings=settings,
        manifest=manifest,
        force=force,
    )
    video_notes_index = [
        path.relative_to(study_paths.course_dir).as_posix()
        for path in list_video_notes(study_paths.video_notes_dir)
    ]

    for filename in progress(list(GLOBAL_DOCUMENTS), desc="Generando course-pack", unit="doc"):
        output_path = study_paths.course_dir / filename
        if output_path.exists() and not force:
            continue

        prompt = build_course_document_prompt(
            course_name=course_name,
            document_filename=filename,
            module_notes=module_notes,
            evidence_docs=evidence_docs,
            video_notes_index=video_notes_index,
            settings=settings,
        )
        content = call_openai_text(client, model=settings.model, prompt=prompt)
        write_markdown(output_path, content)
        manifest.set_global_output(filename, output_path, STATUS_COMPLETED)
        manifest.save()

    quality_report_path = study_paths.course_dir / "99_QUALITY_REPORT.md"
    quality_report = build_quality_report(
        study_paths=study_paths,
        module_note_paths=module_note_paths,
        evidence_docs=evidence_docs,
    )
    write_markdown(quality_report_path, quality_report)
    manifest.set_global_output("99_QUALITY_REPORT.md", quality_report_path, STATUS_COMPLETED)
    manifest.save()


def generate_course_pack_evidence(
    *,
    client: Any,
    course_name: str,
    study_paths: Any,
    module_notes: list[tuple[str, str]],
    settings: StudySettings,
    manifest: StudyManifest,
    force: bool,
) -> list[tuple[str, str]]:
    evidence_dir = study_paths.course_dir / "_course_pack_evidence"
    evidence_docs: list[tuple[str, str]] = []

    for filename in progress(list(COURSE_EVIDENCE_DOCUMENTS), desc="Generando evidencia", unit="doc"):
        output_path = evidence_dir / filename
        if output_path.exists() and not force:
            content = read_markdown(output_path)
        else:
            prompt = build_course_evidence_prompt(
                course_name=course_name,
                evidence_filename=filename,
                module_notes=module_notes,
                settings=settings,
            )
            content = call_openai_text(client, model=settings.model, prompt=prompt)
            write_markdown(output_path, content)
            manifest.set_global_output(f"evidence::{filename}", output_path, STATUS_COMPLETED)
            manifest.save()

        evidence_docs.append((output_path.relative_to(study_paths.course_dir).as_posix(), content))

    return evidence_docs


def build_quality_report(
    *,
    study_paths: Any,
    module_note_paths: list[Path],
    evidence_docs: list[tuple[str, str]],
) -> str:
    module_names = [path.stem for path in module_note_paths]
    coverage_targets = [
        study_paths.course_dir / "01_COURSE_MAP.md",
        study_paths.course_dir / "02_MODULE_SUMMARIES.md",
        study_paths.course_dir / "08_AI_STUDY_CONTEXT.md",
    ]
    coverage_rows: list[str] = []
    warnings: list[str] = []

    for module_name in module_names:
        statuses: list[str] = []
        for target in coverage_targets:
            present = target.exists() and normalized_contains(read_markdown(target), module_name)
            statuses.append(f"{target.name}: {'OK' if present else 'MISSING'}")
            if not present:
                warning = f"WARNING: módulo no encontrado en {target.name}: {module_name}"
                warnings.append(warning)
                print(warning)
        coverage_rows.append(f"- {module_name}: " + " | ".join(statuses))

    evidence_by_name = {name: content for name, content in evidence_docs}
    principles_count = approximate_inventory_count(evidence_by_name.get("_course_pack_evidence/01_PRINCIPLES_INVENTORY.md", ""), "P")
    frameworks_count = approximate_inventory_count(evidence_by_name.get("_course_pack_evidence/02_FRAMEWORKS_INVENTORY.md", ""), "F")
    examples_count = approximate_inventory_count(evidence_by_name.get("_course_pack_evidence/04_EXAMPLES_INVENTORY.md", ""), "E")
    master_prompt_exists = (study_paths.course_dir / "09_MASTER_PROMPT_FOR_AI.md").exists()

    risk_lines = warnings or ["- No se detectaron warnings programáticos de cobertura por módulo."]
    if principles_count == 0:
        risk_lines.append("- Conteo de principios en inventario parece bajo o no detectable.")
    if frameworks_count == 0:
        risk_lines.append("- Conteo de frameworks en inventario parece bajo o no detectable.")

    return "\n".join(
        [
            "# Quality Report",
            "",
            "## Módulos Detectados",
            "",
            *[f"- {module_name}" for module_name in module_names],
            "",
            "## Cobertura en Documentos Maestros",
            "",
            *coverage_rows,
            "",
            "## Conteos Aproximados",
            "",
            f"- Principios: {principles_count}",
            f"- Frameworks/herramientas: {frameworks_count}",
            f"- Ejemplos/casos/referencias: {examples_count}",
            f"- MASTER_PROMPT existe: {'sí' if master_prompt_exists else 'no'}",
            "",
            "## Riesgos Detectados",
            "",
            *risk_lines,
            "",
            "## Secciones Débiles Potenciales",
            "",
            "- Revisar manualmente si `03_CORE_PRINCIPLES.md` cubre todo el curso.",
            "- Revisar manualmente si `04_FRAMEWORKS.md` incluye herramientas de módulos finales.",
            "- Revisar manualmente si `08_AI_STUDY_CONTEXT.md` lista todos los módulos.",
            "- Revisar manualmente si `09_MASTER_PROMPT_FOR_AI.md` es suficientemente operativo.",
            "",
            "## Recomendaciones de Revisión Humana",
            "",
            "- Validar que no haya ejemplos inventados.",
            "- Validar que todos los módulos aparezcan en 01, 02 y 08.",
            "- Validar que los inventarios de evidencia sean más profundos que listas superficiales.",
            "- Regenerar documentos maestros si aparecen warnings de cobertura.",
        ]
    )


def normalized_contains(content: str, needle: str) -> bool:
    return normalize_text(needle) in normalize_text(content)


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(character for character in decomposed if not unicodedata.combining(character))
    return without_accents.casefold()


def approximate_inventory_count(content: str, prefix: str) -> int:
    if not content.strip():
        return 0
    pattern = re.compile(rf"\b{re.escape(prefix)}\d{{2,}}\b", re.IGNORECASE)
    matches = set(pattern.findall(content))
    if matches:
        return len(matches)
    return len(re.findall(r"(?m)^#{2,4}\s+", content))


def should_skip_video_note(record: dict[str, Any] | None, video_note_path: Path, force: bool) -> bool:
    if force:
        return False
    if record and record.get("status") == STATUS_COMPLETED and video_note_path.exists():
        return True
    if video_note_path.exists() and not record:
        return True
    if video_note_path.exists() and record and record.get("status") != STATUS_FAILED:
        return True
    return False


def print_dry_run(
    args: argparse.Namespace,
    transcripts_root: Path,
    selected_paths: list[Path],
    all_paths: list[Path],
    study_paths: Any,
    settings: StudySettings,
) -> None:
    print("Dry run Study Pack: no se llamará a OpenAI API y no se escribirán outputs.")
    print(f"Curso: {args.course_name}")
    print(f"Transcripts: {transcripts_root}")
    print(f"Index: {args.index.expanduser().resolve() if args.index else '(no indicado)'}")
    print(f"Output Study Pack: {study_paths.course_dir}")
    print(f"Manifest: {DEFAULT_STUDY_MANIFEST_PATH}")
    print(f"Config: {args.config}")
    print(f"Modelo de análisis: {settings.model}")
    print(f"Phase: {args.phase}")
    print(f"Transcripciones detectadas: {len(all_paths)}")
    if args.max_videos is not None:
        print(f"Listado limitado por --max-videos {args.max_videos}: {len(selected_paths)} transcripciones")

    planned_phases = expand_phase(args.phase)
    if PHASE_VIDEO_NOTES in planned_phases:
        print(f"Video-notes planificadas: {len(selected_paths)}")
        for path in selected_paths:
            print(f"VIDEO-NOTE: {path.relative_to(transcripts_root).as_posix()}")

    if PHASE_MODULE_SUMMARIES in planned_phases:
        module_count = count_modules_for_paths(transcripts_root, selected_paths)
        print(f"Module summaries planificados: {module_count}")

    if PHASE_COURSE_PACK in planned_phases:
        print(f"Inventarios de evidencia planificados: {len(COURSE_EVIDENCE_DOCUMENTS)}")
        for filename in COURSE_EVIDENCE_DOCUMENTS:
            print(f"EVIDENCE: _course_pack_evidence/{filename}")
        print(f"Documentos globales planificados: {len(GLOBAL_DOCUMENTS)}")
        for filename in GLOBAL_DOCUMENTS:
            print(f"COURSE-PACK: {filename}")
        print("QUALITY: 99_QUALITY_REPORT.md")


def expand_phase(phase: str) -> set[str]:
    if phase == PHASE_ALL:
        return {PHASE_VIDEO_NOTES, PHASE_MODULE_SUMMARIES, PHASE_COURSE_PACK}
    return {phase}


def count_modules_for_paths(transcripts_root: Path, paths: list[Path]) -> int:
    modules: set[str] = set()
    for path in paths:
        relative_path = path.relative_to(transcripts_root)
        modules.add("" if relative_path.parent == Path(".") else relative_path.parent.as_posix())
    return len(modules)


def call_openai_text(client: Any, model: str, prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI devolvió una respuesta vacía para el Study Pack.")
    return content.strip()


def build_openai_client() -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai no está instalado. Ejecuta: pip install -r requirements.txt"
        ) from exc

    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def validate_openai_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "ERROR: Falta OPENAI_API_KEY. Crea un archivo .env desde .env.example "
            "o exporta la variable antes de generar Study Pack."
        )


def load_env_file() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()


def progress(items: Iterable[T], **kwargs: object) -> Iterable[T]:
    try:
        from tqdm import tqdm
    except ImportError:
        return items

    return tqdm(items, **kwargs)


def limit_items(items: list[T], max_items: int | None) -> list[T]:
    if max_items is None:
        return items
    return items[:max_items]


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--max-videos debe ser un entero positivo.") from exc

    if parsed < 1:
        raise argparse.ArgumentTypeError("--max-videos debe ser mayor o igual a 1.")

    return parsed


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit("\nInterrumpido por el usuario.")
    except Exception as exc:
        raise SystemExit(f"ERROR: {truncate_error(exc)}")
