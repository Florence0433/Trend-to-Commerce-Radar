from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from backend.app.config import HOTBOARD_DIR, WEEKLY_RUNS_DIR


CATEGORY_PATTERNS = [
    (
        "时尚穿搭",
        re.compile(
            r"穿搭|外套|羽绒服|围巾|毛衣|睡衣|包包|鞋|裙|皮衣|皮草|雪地靴|帽子|内搭|大衣|拉夫劳伦|阿迪|lululemon|lululenmon|穿戴甲|美甲|染发|发色|彩妆|妆容|防晒|护手霜|身体乳|洗发水|精油|面霜",
            re.I,
        ),
    ),
    (
        "美食餐饮",
        re.compile(
            r"美食|家常菜|蛋糕|麻辣烫|寿司|茶姬|一点点|古茗|瑞幸|喜茶|盒马|山姆|奶茶|咖啡|小马糕|鸡翅|排骨|火锅|空气炸锅|草莓|年夜饭|糖醋|西红柿|香椿|牛肉",
            re.I,
        ),
    ),
    (
        "旅行出行",
        re.compile(
            r"旅游攻略|游玩攻略|旅游|旅行|机场|机票|酒店|迪士尼|长白山|威海|云南|南京|广州|重庆|西安|上海|厦门|长沙|苏州|杭州|景德镇|洛阳|福州|南昌|泉州|大理|东湖|海洋公园|里昂|迪拜|川藏线|新加坡|韩国|贝加尔湖",
            re.I,
        ),
    ),
    ("数码科技", re.compile(r"手机|平板|macbook|iphone|苹果17|oppo|vivo|华为|mate|reno|find|pocket3|大疆|三星|问界|电脑", re.I)),
    ("家居生活", re.compile(r"家居|家装|收纳|置物架|漏水|净水器|柜子|纸巾猫|狗|猫|花束|幼儿园|环创|主题墙", re.I)),
    ("兴趣文娱", re.compile(r"拼豆|逐玉|江湖夜雨十年灯|刘宇宁|舞蹈|儿歌|f1|泡泡玛特|画画|绘画|open claw|三角洲|小马宝莉|海龟汤|生命树|exo|演唱会|玉簟秋|小马糕", re.I)),
]


MODEL_FILE_MAP = {
    "deepseek_v3": "deepseek_v3_suggestions.json",
    "glm5": "glm5_suggestions.json",
    "kimi_k25": "kimi_k25_suggestions.json",
}


def week_sort_key(week_name: str) -> tuple[int, int, int]:
    match = re.match(r"(\d{2})\.(\d{1,2})\.(\d{1,2})-", week_name)
    if not match:
        return (0, 0, 0)
    return (2000 + int(match.group(1)), int(match.group(2)), int(match.group(3)))


def categorize_topic(topic: str) -> str:
    for category, pattern in CATEGORY_PATTERNS:
        if pattern.search(topic):
            return category
    return "其他"


def list_weeks() -> list[dict]:
    weeks = []
    for path in sorted(HOTBOARD_DIR.glob("*行业热度榜.csv"), key=lambda p: week_sort_key(p.stem)):
        week_name = path.stem.replace("行业热度榜", "")
        has_runs = (WEEKLY_RUNS_DIR / path.stem).exists()
        weeks.append(
            {
                "week": week_name,
                "label": week_name.replace("-", " - "),
                "has_topic_runs": has_runs,
            }
        )
    return weeks


def get_hotboard_csv_path(week: str) -> Path:
    path = HOTBOARD_DIR / f"{week}行业热度榜.csv"
    if not path.exists():
        raise FileNotFoundError(f"Hotboard not found for week {week}")
    return path


def read_hotboard(week: str) -> list[dict]:
    path = get_hotboard_csv_path(week)
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader, start=1):
            keyword = str(row.get("热词", "")).strip()
            search_index = int(float(str(row.get("搜索指数", 0)).replace(",", "") or 0))
            surge_text = str(row.get("热度飙升", "")).strip()
            rows.append(
                {
                    "rank": index,
                    "keyword": keyword,
                    "search_index": search_index,
                    "surge": "飙升" in surge_text,
                    "surge_text": surge_text,
                    "category": categorize_topic(keyword),
                }
            )
    return rows


def summarize_hotboard(week: str) -> dict:
    rows = read_hotboard(week)
    top_row = rows[0] if rows else None
    return {
        "week": week,
        "top_keyword": top_row["keyword"] if top_row else None,
        "keyword_count": len(rows),
        "surge_count": sum(1 for row in rows if row["surge"]),
    }


def get_week_run_dir(week: str) -> Path:
    path = WEEKLY_RUNS_DIR / f"{week}行业热度榜"
    if not path.exists():
        raise FileNotFoundError(f"Weekly run not found for week {week}")
    return path


def _detect_posts_dir(week_dir: Path) -> Path:
    posts_dir = week_dir / "帖子CSV"
    if posts_dir.exists():
        return posts_dir
    raise FileNotFoundError(f"Posts directory not found in {week_dir}")


def _detect_model_dir(week_dir: Path) -> Path:
    model_dir = week_dir / "模型建议"
    if model_dir.exists():
        return model_dir
    raise FileNotFoundError(f"Model suggestion directory not found in {week_dir}")


def list_topics(week: str) -> list[dict]:
    week_dir = get_week_run_dir(week)
    posts_dir = _detect_posts_dir(week_dir)
    model_dir = _detect_model_dir(week_dir)
    topics = []
    for csv_path in sorted(posts_dir.glob("*.csv")):
        topic = infer_topic_name(csv_path)
        topic_model_dir = model_dir / topic
        available_models = [model for model, filename in MODEL_FILE_MAP.items() if (topic_model_dir / filename).exists()]
        topics.append(
            {
                "topic": topic,
                "post_count": count_csv_rows(csv_path),
                "available_models": available_models,
            }
        )
    return topics


def infer_topic_name(csv_path: Path) -> str:
    stem = csv_path.stem
    stem = re.sub(r"^\d+_", "", stem)
    stem = re.sub(r"_posts$", "", stem)
    return stem


def count_csv_rows(csv_path: Path) -> int:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def get_topic_posts_path(week: str, topic: str) -> Path:
    posts_dir = _detect_posts_dir(get_week_run_dir(week))
    for csv_path in posts_dir.glob("*.csv"):
        if infer_topic_name(csv_path) == topic:
            return csv_path
    raise FileNotFoundError(f"Posts CSV not found for topic {topic}")


def read_topic_posts(week: str, topic: str, limit: int | None = None) -> list[dict]:
    csv_path = get_topic_posts_path(week, topic)
    rows = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if limit and len(rows) >= limit:
                break
    return rows


def summarize_topic_posts(week: str, topic: str) -> dict:
    rows = read_topic_posts(week, topic)
    like_values = [safe_int(row.get("note_like_count")) for row in rows]
    collect_values = [safe_int(row.get("note_collect_count")) for row in rows]
    comment_values = [safe_int(row.get("note_comment_count")) for row in rows]
    tags = []
    for row in rows:
        tags.extend([item.strip() for item in str(row.get("note_tags", "")).split("|") if item.strip()])
    tag_counts = {}
    for tag in tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    return {
        "topic": topic,
        "post_count": len(rows),
        "avg_like": round(sum(like_values) / len(like_values), 2) if rows else 0,
        "avg_collect": round(sum(collect_values) / len(collect_values), 2) if rows else 0,
        "avg_comment": round(sum(comment_values) / len(comment_values), 2) if rows else 0,
        "top_tags": sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)[:10],
    }


def safe_int(value: object) -> int:
    try:
        text = str(value or "").replace(",", "").strip()
        if not text:
            return 0
        if text.endswith("万"):
            return int(float(text[:-1]) * 10000)
        return int(float(text))
    except Exception:
        return 0


def read_local_summary(week: str, topic: str) -> dict:
    model_dir = _detect_model_dir(get_week_run_dir(week))
    path = model_dir / topic / "local_summary.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def list_available_models(week: str, topic: str) -> list[dict]:
    model_dir = _detect_model_dir(get_week_run_dir(week)) / topic
    available = []
    for model_key, filename in MODEL_FILE_MAP.items():
        if (model_dir / filename).exists():
            available.append({"id": model_key, "label": model_key})
    return available


def read_model_suggestion(week: str, topic: str, model: str) -> dict:
    if model not in MODEL_FILE_MAP:
        raise FileNotFoundError(f"Unsupported model {model}")
    model_dir = _detect_model_dir(get_week_run_dir(week)) / topic
    path = model_dir / MODEL_FILE_MAP[model]
    if not path.exists():
        raise FileNotFoundError(f"Suggestion file not found for {topic} / {model}")
    parsed = json.loads(path.read_text(encoding="utf-8"))
    parsed["topic"] = topic
    parsed["model"] = model
    return parsed

