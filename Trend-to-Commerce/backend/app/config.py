import os
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "Data"


def _load_local_env() -> None:
    data_dir = Path(os.getenv("TREND_TO_COMMERCE_DATA_DIR", DEFAULT_DATA_DIR)).expanduser()
    candidates = [
        PROJECT_ROOT / ".env.local",
        PROJECT_ROOT / ".env",
        data_dir / ".env.local",
        data_dir / ".env",
    ]
    if os.getenv("TREND_TO_COMMERCE_LOAD_RTF_ENV", "").strip() == "1":
        candidates.append(data_dir / ".env.local.rtf")
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() == ".rtf":
            text = text.replace("\\par", "\n")
            text = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", text)
            text = text.replace("{", "").replace("}", "")
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'").rstrip("\\").strip()
            if key and value and key not in os.environ:
                os.environ[key] = value


def _normalize_generation_url() -> str:
    explicit_url = os.getenv("GENERATION_API_URL", "").strip()
    if explicit_url:
        return explicit_url

    base_url = os.getenv("API_BASE_URL", "").strip()
    if base_url:
        return base_url.rstrip("/") + "/chat/completions"

    return ""


_load_local_env()
_load_local_env()

DATA_DIR = Path(os.getenv("TREND_TO_COMMERCE_DATA_DIR", DEFAULT_DATA_DIR)).expanduser()
HOTBOARD_DIR = DATA_DIR / "行业热度榜"
WEEKLY_RUNS_DIR = Path(os.getenv("TREND_TO_COMMERCE_MODEL_RUNS_DIR", DATA_DIR / "model_runs")).expanduser()
KEYWORD_TOPIC_DIR = DATA_DIR / "关键词具体帖子评论"
APP_DB_PATH = Path(
    os.getenv("TREND_TO_COMMERCE_DB_PATH")
    or PROJECT_ROOT / "backend" / "trend_to_commerce.db"
).expanduser()

# Optional external generation settings. If these are not configured,
# the backend will still generate structured answers from local project data.
GENERATION_API_URL = _normalize_generation_url()
GENERATION_API_KEY = os.getenv("GENERATION_API_KEY", "").strip() or os.getenv("API_KEY", "").strip()
GENERATION_MODEL = (
    os.getenv("GENERATION_MODEL", "").strip()
    or os.getenv("MODEL_DEEPSEEK_V3", "").strip()
    or os.getenv("MODEL_NAME", "").strip()
)
GENERATION_TIMEOUT_SECONDS = int(os.getenv("GENERATION_TIMEOUT_SECONDS", "45"))
GENERATION_FALLBACK_ON_ERROR = os.getenv("GENERATION_FALLBACK_ON_ERROR", "1").strip().lower() not in {"0", "false", "no"}
GENERATION_PREFER_REMOTE = os.getenv("GENERATION_PREFER_REMOTE", "1").strip().lower() in {"1", "true", "yes"}
GENERATION_TRANSLATE_WITH_API = os.getenv("GENERATION_TRANSLATE_WITH_API", "0").strip().lower() in {"1", "true", "yes"}
GENERATION_TRANSLATION_TIMEOUT_SECONDS = int(os.getenv("GENERATION_TRANSLATION_TIMEOUT_SECONDS", "5"))

