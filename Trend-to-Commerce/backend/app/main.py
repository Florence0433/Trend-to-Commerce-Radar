from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.app.config import CORS_ALLOWED_ORIGINS, PROJECT_ROOT
from backend.app.database import (
    create_generation_job,
    get_generation_job,
    init_db,
    list_generation_jobs,
    update_generation_job_status,
)
from backend.app.services.data_service import (
    list_available_models,
    list_topics,
    list_weeks,
    read_hotboard,
    read_local_summary,
    read_model_suggestion,
    read_topic_posts,
    summarize_hotboard,
    summarize_topic_posts,
)
from backend.app.services.generation_service import DEFAULT_MODE, build_generation_result, normalize_optional_text
from backend.app.services.keyword_topic_service import keyword_topic_status_report


app = FastAPI(title="Trend-to-Commerce API", version="0.1.0")
WEB_DIR = PROJECT_ROOT / "web"

if CORS_ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def handle_not_found(exc: FileNotFoundError):
    raise HTTPException(status_code=404, detail=str(exc))


def mount_web_static() -> None:
    """Serve the product web frontend from the same origin as the API."""
    static_dirs = {
        "/css": WEB_DIR / "css",
        "/js": WEB_DIR / "js",
        "/vendor": WEB_DIR / "vendor",
    }
    for route, directory in static_dirs.items():
        if directory.exists():
            app.mount(route, StaticFiles(directory=directory), name=f"web-{route.strip('/')}")


mount_web_static()


class GenerateAnswerRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    week: str | None = Field(default=None, max_length=64)
    topic: str | None = Field(default=None, max_length=128)
    mode: str = Field(default=DEFAULT_MODE, max_length=64)
    language: str | None = Field(default=None, max_length=16)


@app.on_event("startup")
def startup():
    init_db()


def process_generation_job(
    job_id: int,
    question_override: str | None = None,
    week_override: str | None = None,
    topic_override: str | None = None,
    mode_override: str | None = None,
    language_override: str | None = None,
) -> None:
    job = get_generation_job(job_id)
    if not job:
        return

    update_generation_job_status(job_id, "running")
    try:
        result = build_generation_result(
            question=question_override or job["question"],
            week=week_override or job.get("week"),
            topic=topic_override or job.get("topic"),
            mode=mode_override or job.get("mode") or DEFAULT_MODE,
            language=language_override,
        )
        update_generation_job_status(
            job_id,
            "succeeded",
            result=result,
            week=result.get("resolved_week"),
            topic=result.get("resolved_topic"),
        )
    except Exception as exc:
        update_generation_job_status(job_id, "failed", error_message=str(exc))


@app.get("/api/health")
def health():
    return {"ok": True, "jobs_api": True}


@app.get("/", include_in_schema=False)
def web_index():
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Product web frontend not found")
    return FileResponse(index_path)


@app.get("/index.html", include_in_schema=False)
def web_index_html():
    return web_index()


@app.get("/api/jobs")
def jobs(limit: int = Query(20, ge=1, le=100)):
    return {"items": list_generation_jobs(limit=limit)}


@app.get("/api/jobs/{job_id}")
def job_detail(job_id: int):
    job = get_generation_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@app.get("/api/keyword-topics/status")
def keyword_topic_status():
    return keyword_topic_status_report()


@app.post("/api/generate-answer")
def generate_answer(payload: GenerateAnswerRequest, background_tasks: BackgroundTasks):
    question = payload.question.strip()
    week = normalize_optional_text(payload.week)
    topic = normalize_optional_text(payload.topic)
    mode = normalize_optional_text(payload.mode) or DEFAULT_MODE
    language = normalize_optional_text(payload.language)

    job = create_generation_job(question=question, week=week, topic=topic, mode=mode)
    background_tasks.add_task(process_generation_job, job["id"], question, week, topic, mode, language)
    return {"job_id": job["id"], "status": job["status"], "job": job}


@app.get("/api/weeks")
def weeks():
    return list_weeks()


@app.get("/api/weeks/{week}/hotboard")
def week_hotboard(week: str):
    try:
        return {"week": week, "rows": read_hotboard(week)}
    except FileNotFoundError as exc:
        handle_not_found(exc)


@app.get("/api/weeks/{week}/summary")
def week_summary(week: str):
    try:
        return summarize_hotboard(week)
    except FileNotFoundError as exc:
        handle_not_found(exc)


@app.get("/api/weeks/{week}/topics")
def week_topics(week: str):
    try:
        return list_topics(week)
    except FileNotFoundError as exc:
        handle_not_found(exc)


@app.get("/api/weeks/{week}/topics/{topic}")
def topic_detail(week: str, topic: str):
    try:
        return {
            "topic": topic,
            "week": week,
            "posts_meta": summarize_topic_posts(week, topic),
            "models": list_available_models(week, topic),
            "local_summary": read_local_summary(week, topic),
        }
    except FileNotFoundError as exc:
        handle_not_found(exc)


@app.get("/api/weeks/{week}/topics/{topic}/posts")
def topic_posts(week: str, topic: str, limit: int = Query(20, ge=1, le=200)):
    try:
        return {
            "topic": topic,
            "week": week,
            "items": read_topic_posts(week, topic, limit=limit),
        }
    except FileNotFoundError as exc:
        handle_not_found(exc)


@app.get("/api/weeks/{week}/topics/{topic}/posts/meta")
def topic_posts_meta(week: str, topic: str):
    try:
        return summarize_topic_posts(week, topic)
    except FileNotFoundError as exc:
        handle_not_found(exc)


@app.get("/api/weeks/{week}/topics/{topic}/suggestions")
def topic_models(week: str, topic: str):
    try:
        return {"topic": topic, "week": week, "models": list_available_models(week, topic)}
    except FileNotFoundError as exc:
        handle_not_found(exc)


@app.get("/api/weeks/{week}/topics/{topic}/suggestions/{model}")
def topic_model_suggestion(week: str, topic: str, model: str):
    try:
        return read_model_suggestion(week, topic, model)
    except FileNotFoundError as exc:
        handle_not_found(exc)

