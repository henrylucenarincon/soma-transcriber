"""Soma Studio — FastAPI backend for local course processing."""
from __future__ import annotations

import asyncio
import json
import platform
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Soma Studio", docs_url=None, redoc_url=None)


# ── Job system ────────────────────────────────────────────────────────────────

class RunningJob:
    """Tracks a running subprocess and buffers its output for reconnection."""

    def __init__(self, job_id: str, job_type: str):
        self.job_id = job_id
        self.job_type = job_type
        self.log: list[str] = []
        self._subscribers: list[asyncio.Queue] = []
        self.done = False
        self.returncode: int | None = None

    def write(self, chunk: str) -> None:
        self.log.append(chunk)
        for q in self._subscribers:
            q.put_nowait(chunk)

    def finish(self, returncode: int = 0) -> None:
        self.done = True
        self.returncode = returncode
        for q in self._subscribers:
            q.put_nowait(None)  # sentinel

    async def stream(self) -> AsyncGenerator[str, None]:
        # Subscribe BEFORE reading buffer so no chunk is missed
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            # Replay existing log
            for chunk in list(self.log):
                yield chunk
            if self.done:
                return
            # Stream live chunks
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item
        finally:
            if queue in self._subscribers:
                self._subscribers.remove(queue)


# Single-slot job registry (one active job at a time)
current_job: RunningJob | None = None

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Pydantic models ──────────────────────────────────────────────────────────

class FolderPickerRequest(BaseModel):
    title: str = "Selecciona una carpeta"


class TranscribeRequest(BaseModel):
    course_path: str
    output_path: str = "./output"
    course_name: str
    config_path: str | None = None
    max_videos: int | None = None
    force: bool = False


class StudyPackRequest(BaseModel):
    output_path: str = "./output"
    course_name: str
    config_path: str | None = None
    max_videos: int | None = None
    force: bool = False
    phase: str = "all"
    module: str | None = None


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        return HTMLResponse(html_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Soma Studio — static/ not found</h1>")


@app.get("/api/configs")
async def get_configs():
    return {"configs": _discover_configs()}


@app.get("/api/courses")
async def get_courses(output: str = "./output"):
    output_path = _resolve(output)
    transcripts_dir = output_path / "transcripts"
    if not transcripts_dir.exists():
        return {"courses": []}
    courses = sorted(d.name for d in transcripts_dir.iterdir() if d.is_dir())
    return {"courses": courses}


@app.get("/api/modules")
async def get_modules(output: str = "./output", course_name: str = ""):
    output_path = _resolve(output)
    transcripts_dir = output_path / "transcripts" / course_name
    if not transcripts_dir.exists():
        return {"modules": []}
    modules = sorted(d.name for d in transcripts_dir.iterdir() if d.is_dir())
    return {"modules": modules}


@app.post("/api/select-folder")
async def select_folder(request: FolderPickerRequest):
    path = _pick_folder_macos(request.title)
    return {"path": path}


@app.get("/api/jobs/current")
async def get_current_job():
    if current_job:
        return {
            "job_id": current_job.job_id,
            "type": current_job.job_type,
            "running": not current_job.done,
            "has_log": len(current_job.log) > 0,
        }
    return {"running": False, "job_id": None, "has_log": False}


@app.get("/api/jobs/{job_id}/reconnect")
async def reconnect_job(job_id: str):
    if not current_job or current_job.job_id != job_id:
        raise HTTPException(status_code=404, detail="Job not found or expired")
    return StreamingResponse(current_job.stream(), media_type="text/plain")


@app.post("/api/list-videos")
async def list_videos(request: TranscribeRequest):
    args = _build_transcribe_args(request) + ["--list-videos"]
    return StreamingResponse(_run_script("main.py", args), media_type="text/plain")


@app.post("/api/dry-run")
async def dry_run(request: TranscribeRequest):
    args = _build_transcribe_args(request) + ["--dry-run"]
    return StreamingResponse(_run_script("main.py", args), media_type="text/plain")


@app.post("/api/transcribe")
async def transcribe(request: TranscribeRequest):
    args = _build_transcribe_args(request)
    return StreamingResponse(_start_job("transcribe", "main.py", args), media_type="text/plain")


@app.post("/api/study-pack/dry-run")
async def study_pack_dry_run(request: StudyPackRequest):
    args = _build_study_pack_args(request) + ["--dry-run"]
    return StreamingResponse(_run_script("study_pack.py", args), media_type="text/plain")


@app.post("/api/study-pack/generate")
async def study_pack_generate(request: StudyPackRequest):
    args = _build_study_pack_args(request)
    return StreamingResponse(_start_job("study-pack", "study_pack.py", args), media_type="text/plain")


@app.get("/api/status")
async def get_status(output: str = "./output"):
    output_path = _resolve(output)
    manifest_path = PROJECT_ROOT / "data" / "manifest.json"
    study_manifest_path = PROJECT_ROOT / "data" / "study_manifest.json"
    index_path = output_path / "index.csv"

    return {
        "manifest": _load_manifest_summary(manifest_path),
        "study_manifest": _load_manifest_summary(study_manifest_path),
        "manifest_exists": manifest_path.exists(),
        "study_manifest_exists": study_manifest_path.exists(),
        "index_exists": index_path.exists(),
        "output_path": str(output_path),
    }


@app.get("/api/index")
async def get_index(output: str = "./output", course_name: str = ""):
    output_path = _resolve(output)
    index_path = output_path / "index.csv"
    if not index_path.exists():
        return {"exists": False, "rows": [], "columns": []}
    try:
        import pandas as pd
        df = pd.read_csv(index_path)
        return {
            "exists": True,
            "columns": list(df.columns),
            "rows": df.fillna("").to_dict(orient="records"),
        }
    except Exception as exc:
        return {"exists": True, "error": str(exc), "rows": [], "columns": []}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _resolve(path: str) -> Path:
    p = Path(path).expanduser()
    if p.is_absolute():
        return p
    return (PROJECT_ROOT / p).resolve()


def _discover_configs() -> list[str]:
    candidates: list[Path] = []
    for filename in ("config.yaml", "config.example.yaml"):
        p = PROJECT_ROOT / filename
        if p.exists():
            candidates.append(p)
    for directory in (
        PROJECT_ROOT / "configs" / "examples",
        PROJECT_ROOT / "configs" / "local",
    ):
        if directory.exists():
            candidates.extend(sorted(directory.glob("*.yaml")))
            candidates.extend(sorted(directory.glob("*.yml")))
    seen: set[Path] = set()
    result: list[str] = []
    for p in candidates:
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(p.relative_to(PROJECT_ROOT).as_posix())
    return result


def _pick_folder_macos(title: str) -> str | None:
    if platform.system() != "Darwin":
        return None
    escaped = title.replace("\\", "\\\\").replace('"', '\\"')
    script = f'POSIX path of (choose folder with prompt "{escaped}")'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        path = result.stdout.strip()
        return path if path else None
    return None


def _build_transcribe_args(request: TranscribeRequest) -> list[str]:
    output = _resolve(request.output_path)
    args = [
        "--input", request.course_path,
        "--output", str(output),
        "--course-name", request.course_name,
    ]
    if request.config_path:
        config_path = _resolve(request.config_path)
        args += ["--config", str(config_path)]
    if request.max_videos and request.max_videos > 0:
        args += ["--max-videos", str(request.max_videos)]
    if request.force:
        args.append("--force")
    return args


def _build_study_pack_args(request: StudyPackRequest) -> list[str]:
    output = _resolve(request.output_path)
    transcripts = str(output / "transcripts" / request.course_name)
    index = str(output / "index.csv")
    study_output = str(output / "study")

    args = [
        "--transcripts", transcripts,
        "--index", index,
        "--output", study_output,
        "--course-name", request.course_name,
    ]
    if request.config_path:
        config_path = _resolve(request.config_path)
        args += ["--config", str(config_path)]
    if request.max_videos and request.max_videos > 0:
        args += ["--max-videos", str(request.max_videos)]
    if request.force:
        args.append("--force")
    if request.phase and request.phase != "all":
        args += ["--phase", request.phase]
    if request.module:
        args += ["--module", request.module]
    return args


async def _start_job(job_type: str, script_name: str, args: list[str]) -> AsyncGenerator[str, None]:
    """Start a tracked job and stream its output. Supports page-reload reconnection."""
    global current_job
    job = RunningJob(str(uuid.uuid4()), job_type)
    current_job = job

    async def _run_in_background() -> None:
        returncode = 0
        try:
            async for chunk in _run_script(script_name, args):
                job.write(chunk)
        except Exception as exc:
            job.write(f"\n[ERROR] {exc}\n")
            returncode = 1
        finally:
            job.finish(returncode)

    asyncio.create_task(_run_in_background())
    async for chunk in job.stream():
        yield chunk


async def _run_script(script_name: str, args: list[str]) -> AsyncGenerator[str, None]:
    script_path = PROJECT_ROOT / "src" / script_name
    cmd = [sys.executable, str(script_path)] + args

    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(PROJECT_ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=_env_with_dotenv(),
    )

    if process.stdout:
        async for line in process.stdout:
            yield line.decode("utf-8", errors="replace")

    await process.wait()
    code = process.returncode
    if code == 0:
        yield f"\n[OK] Proceso completado (código {code})\n"
    else:
        yield f"\n[ERROR] El proceso terminó con código {code}\n"


def _env_with_dotenv() -> dict[str, str]:
    import os
    env = dict(os.environ)
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key and key not in env:
                    env[key] = value
    # Force unbuffered output so tqdm progress reaches the stream in real-time
    env["PYTHONUNBUFFERED"] = "1"
    return env


def _load_manifest_summary(manifest_path: Path) -> dict[str, int]:
    if not manifest_path.exists():
        return {}
    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    if isinstance(data, dict) and "files" in data:
        records = [v for v in data["files"].values() if isinstance(v, dict)]
    elif isinstance(data, dict):
        records = [v for v in data.values() if isinstance(v, dict)]
    elif isinstance(data, list):
        records = [r for r in data if isinstance(r, dict)]
    else:
        records = []
    summary: dict[str, int] = {}
    for record in records:
        status = str(record.get("status", "unknown"))
        summary[status] = summary.get(status, 0) + 1
    return summary


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8899)
