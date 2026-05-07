from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys
from typing import Any

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LIST_VIDEO_PATTERN = re.compile(r"^\s*(\d+)\.\s+\[([^\]]+)\]\s+(.+?)\s*$")


def run_cli_command(args: list[str]) -> tuple[int, str, str]:
    command = [sys.executable, "src/main.py", *args]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def select_directory_dialog(title: str = "Selecciona una carpeta") -> str | None:
    try:
        from tkinter import Tk, filedialog

        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(title=title)
        root.destroy()
    except Exception as exc:
        st.warning(f"No se pudo abrir el selector de carpetas. Usa el input manual. Detalle: {exc}")
        return None

    return selected or None


def discover_config_files() -> list[str]:
    candidates: list[Path] = []

    for filename in ("config.yaml", "config.example.yaml"):
        path = PROJECT_ROOT / filename
        if path.exists():
            candidates.append(path)

    for directory in (PROJECT_ROOT / "configs" / "examples", PROJECT_ROOT / "configs" / "local"):
        if directory.exists():
            candidates.extend(sorted(directory.glob("*.yaml")))
            candidates.extend(sorted(directory.glob("*.yml")))

    unique_paths = []
    seen = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_paths.append(path)

    return [path.relative_to(PROJECT_ROOT).as_posix() for path in unique_paths]


def parse_list_videos_output(output: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        match = LIST_VIDEO_PATTERN.match(line)
        if not match:
            continue
        rows.append(
            {
                "index": int(match.group(1)),
                "status": match.group(2),
                "path": match.group(3),
            }
        )
    return rows


def build_base_cli_args(
    course_path: str,
    output_path: str,
    course_name: str,
    config_path: str | None,
    max_videos: int | None = None,
    include_max_videos: bool = True,
    force: bool = False,
) -> list[str]:
    args = [
        "--input",
        course_path,
        "--output",
        output_path,
        "--course-name",
        course_name,
    ]
    if config_path:
        args.extend(["--config", config_path])
    if include_max_videos and max_videos and max_videos > 0:
        args.extend(["--max-videos", str(max_videos)])
    if force:
        args.append("--force")
    return args


def resolve_local_path(path_text: str) -> Path:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def render_command_result(return_code: int, stdout: str, stderr: str) -> None:
    if return_code == 0:
        st.success("Comando finalizado correctamente.")
    else:
        st.error(f"Comando finalizado con código {return_code}.")

    if stdout.strip():
        st.subheader("stdout")
        st.code(stdout, language="text")
    if stderr.strip():
        st.subheader("stderr")
        st.code(stderr, language="text")


def render_path_status(label: str, path: Path) -> None:
    status = "existe" if path.exists() else "no existe"
    st.write(f"**{label}:** `{path}` ({status})")


def load_manifest_summary(manifest_path: Path) -> dict[str, int]:
    if not manifest_path.exists():
        return {}
    with manifest_path.open("r", encoding="utf-8") as manifest_file:
        data = json.load(manifest_file)

    records: list[dict[str, Any]]
    if isinstance(data, dict) and "files" in data and isinstance(data["files"], dict):
        records = [record for record in data["files"].values() if isinstance(record, dict)]
    elif isinstance(data, dict):
        records = [record for record in data.values() if isinstance(record, dict)]
    elif isinstance(data, list):
        records = [record for record in data if isinstance(record, dict)]
    else:
        records = []

    summary: dict[str, int] = {}
    for record in records:
        status = str(record.get("status", "unknown"))
        summary[status] = summary.get(status, 0) + 1
    return summary


def main() -> None:
    st.set_page_config(page_title="Soma Studio", layout="wide")

    st.title("Soma Studio")
    st.caption("Transcribe cursos y prepara conocimiento para IA.")
    st.info(
        "Esta interfaz corre localmente. No es una app pública. Los videos, audios, "
        "outputs y transcripciones permanecen en tu máquina, salvo las llamadas necesarias "
        "a OpenAI API para transcribir."
    )

    config_files = discover_config_files()
    st.session_state.setdefault("course_path", "")
    st.session_state.setdefault("output_path", "./output")

    with st.sidebar:
        st.header("Configuración")
        course_path = st.text_input("Ruta del curso", key="course_path")
        if st.button("Seleccionar carpeta", use_container_width=True):
            selected_directory = select_directory_dialog("Selecciona la carpeta del curso")
            if selected_directory:
                st.session_state.course_path = selected_directory
                st.rerun()

        course_name = st.text_input("Nombre del curso", value="")
        output_path = st.text_input("Output", key="output_path")
        if st.button("Seleccionar output", use_container_width=True):
            selected_output = select_directory_dialog("Selecciona la carpeta de output")
            if selected_output:
                st.session_state.output_path = selected_output
                st.rerun()

        if config_files:
            selected_config = st.selectbox("Perfil YAML", config_files, index=0)
        else:
            selected_config = ""
            st.warning("No se encontraron perfiles YAML.")
        st.caption(f"Perfil seleccionado: `{selected_config or 'ninguno'}`")

        max_videos_input = st.number_input(
            "Límite de videos a procesar",
            min_value=0,
            value=0,
            step=1,
            help="0 significa sin límite. Usa 1 para pruebas controladas.",
        )
        st.caption("Recomendado: usa 1 para probar. Usa 0 solo si quieres procesar todo lo pendiente.")
        if max_videos_input == 0:
            st.warning("Sin límite de videos: Soma intentará procesar todo lo pendiente.")
        max_videos = int(max_videos_input) if max_videos_input else None
        force = st.checkbox("force")
        confirm_no_limit = st.checkbox(
            "Confirmo que quiero procesar sin límite de videos y entiendo que puede generar costos de API."
        )

    ready = all([course_path.strip(), course_name.strip(), output_path.strip(), selected_config])

    tab_course, tab_transcription, tab_status, tab_study_pack = st.tabs(
        ["Curso", "Transcripción", "Estado", "Study Pack Próximamente"]
    )

    with tab_course:
        st.subheader("Curso")
        st.write("Soma Studio organiza el flujo local para convertir cursos en transcripciones estudiables por IA.")
        st.write(f"**Ruta del curso:** `{course_path or 'sin definir'}`")
        st.write(f"**Nombre del curso:** `{course_name or 'sin definir'}`")
        st.write(f"**Output:** `{output_path or 'sin definir'}`")
        st.write(f"**Perfil:** `{selected_config or 'sin definir'}`")

        checklist = pd.DataFrame(
            [
                {"item": "Ruta del curso definida", "ok": bool(course_path.strip())},
                {"item": "Nombre del curso definido", "ok": bool(course_name.strip())},
                {"item": "Perfil seleccionado", "ok": bool(selected_config)},
                {"item": "Output definido", "ok": bool(output_path.strip())},
            ]
        )
        st.dataframe(checklist, hide_index=True, use_container_width=True)

        if not ready:
            st.warning("Completa la configuración del sidebar antes de ejecutar comandos.")

    with tab_transcription:
        st.subheader("Transcripción")

        base_args = build_base_cli_args(
            course_path=course_path,
            output_path=output_path,
            course_name=course_name,
            config_path=selected_config,
            max_videos=max_videos,
            include_max_videos=True,
            force=force,
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            list_clicked = st.button("Listar videos", use_container_width=True)
        with col2:
            dry_run_clicked = st.button("Dry run", use_container_width=True)
        with col3:
            transcribe_clicked = st.button("Transcribir", use_container_width=True)
        with col4:
            retry_clicked = st.button("Reintentar fallidos", use_container_width=True)

        if list_clicked:
            if not ready:
                st.warning("Completa la configuración antes de listar videos.")
            else:
                return_code, stdout, stderr = run_cli_command([*base_args, "--list-videos"])
                rows = parse_list_videos_output(stdout)
                if rows:
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                render_command_result(return_code, stdout, stderr)

        if dry_run_clicked:
            if not ready:
                st.warning("Completa la configuración antes de ejecutar dry-run.")
            else:
                return_code, stdout, stderr = run_cli_command([*base_args, "--dry-run"])
                render_command_result(return_code, stdout, stderr)

        if transcribe_clicked:
            if not ready:
                st.warning("Completa la configuración antes de transcribir.")
            elif not max_videos and not confirm_no_limit:
                st.warning(
                    "Para procesar sin límite de videos, confirma explícitamente el riesgo de costos de API."
                )
            else:
                return_code, stdout, stderr = run_cli_command(base_args)
                render_command_result(return_code, stdout, stderr)

        if retry_clicked:
            st.info("Este modo usa el manifest para saltar completed y volver a intentar pending/failed.")
            if not ready:
                st.warning("Completa la configuración antes de reintentar fallidos.")
            else:
                retry_args = build_base_cli_args(
                    course_path=course_path,
                    output_path=output_path,
                    course_name=course_name,
                    config_path=selected_config,
                    include_max_videos=False,
                    force=False,
                )
                return_code, stdout, stderr = run_cli_command(retry_args)
                render_command_result(return_code, stdout, stderr)

    with tab_status:
        st.subheader("Estado")
        resolved_output = resolve_local_path(output_path or "./output")
        index_path = resolved_output / "index.csv"
        transcripts_dir = resolved_output / "transcripts"
        audio_dir = resolved_output / "audio"
        chunks_dir = resolved_output / "chunks"
        manifest_path = PROJECT_ROOT / "data" / "manifest.json"

        render_path_status("index.csv", index_path)
        render_path_status("transcripts", transcripts_dir)
        render_path_status("audio", audio_dir)
        render_path_status("chunks", chunks_dir)
        render_path_status("manifest.json", manifest_path)

        if index_path.exists():
            index_df = pd.read_csv(index_path)
            st.subheader("Index")
            st.dataframe(index_df, use_container_width=True)
            if "status" in index_df.columns:
                st.subheader("Conteos por status")
                counts = index_df["status"].fillna("unknown").value_counts().reset_index()
                counts.columns = ["status", "count"]
                st.dataframe(counts, hide_index=True, use_container_width=True)
        else:
            st.info("Todavía no existe output/index.csv para este output.")

        manifest_summary = load_manifest_summary(manifest_path)
        if manifest_summary:
            st.subheader("Resumen de manifest")
            st.dataframe(
                pd.DataFrame(
                    [{"status": status, "count": count} for status, count in manifest_summary.items()]
                ),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No hay resumen de manifest disponible.")

    with tab_study_pack:
        st.subheader("Study Pack Próximamente")
        st.write("V2 generará documentos de estudio a partir de las transcripciones completas.")
        st.write(
            "- mapa del curso\n"
            "- resumen por módulo\n"
            "- principios centrales\n"
            "- frameworks\n"
            "- conceptos clave\n"
            "- ejemplos del curso\n"
            "- prompt maestro para IA\n"
            "- AI_STUDY_CONTEXT.md"
        )
        st.info("Esta sección queda preparada como roadmap visual. No genera documentos todavía.")


if __name__ == "__main__":
    main()
