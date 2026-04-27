from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote, unquote

from backend.app.config import MERCH_ANALYSIS_DIR
from backend.app.services.data_service import categorize_topic, read_hotboard
from backend.app.services.keyword_topic_service import (
    keyword_topic_available_topics,
    local_heuristic_summary,
    read_keyword_topic_posts,
    resolve_keyword_topic_name,
    summarize_keyword_topic_posts,
)


MERCH_WEEKLY_LIMIT = 6
MERCH_ANALYSIS_BUNDLE_PATH = MERCH_ANALYSIS_DIR.with_suffix(".json")

TOPIC_EN_NAMES = {
    "拼豆": "Perler Beads",
    "穿搭": "Outfits",
    "春季穿搭": "Spring Outfits",
    "冬季穿搭": "Winter Outfits",
    "小个子穿搭春天": "Spring Outfits for Petite Users",
    "高跟鞋穿搭冬季": "Winter Heel Outfits",
    "手机壳": "Phone Cases",
    "蛋糕": "Cakes",
    "花束": "Bouquets",
    "帽子": "Hats",
    "外套": "Outerwear",
    "穿戴甲": "Press-on Nails",
    "防晒霜推荐": "Sunscreen Recommendations",
    "洗发水推荐": "Shampoo Recommendations",
    "染发发色推荐": "Hair Color Recommendations",
    "染发颜色推荐2026": "2026 Hair Color Recommendations",
    "大疆pocket3": "DJI Pocket 3",
    "家居收纳": "Home Storage",
    "圣诞帽": "Christmas Hats",
    "圣诞蛋糕": "Christmas Cakes",
    "儿童小短指甲": "Kids Short Nails",
    "情人节喝什么奶茶": "Valentine's Day Milk Tea",
    "过年买什么年货": "Chinese New Year Goods",
    "玉米皮爆改鲜花": "Corn Husk Flower DIY",
    "stanley杯子为什么这么火": "Stanley Cups",
}

CATEGORY_EN_NAMES = {
    "时尚穿搭": "Fashion",
    "美食餐饮": "Food & Beverage",
    "旅行出行": "Travel",
    "数码科技": "Tech",
    "家居生活": "Home & Living",
    "兴趣文娱": "Hobbies & Culture",
    "其他": "Lifestyle",
}

THEME_EN_NAMES = {
    "兴趣DIY": "DIY hobbies",
    "搭配场景": "styling occasions",
    "送礼礼物": "gifting moments",
    "教程攻略": "how-to decisions",
    "功能解决方案": "functional needs",
    "种草展示": "inspiration content",
    "其他": "everyday lifestyle needs",
    "内容需求": "consumer interest",
}


def topic_to_filename(topic: str) -> str:
    return f"{quote(topic, safe='')}.json"


def filename_to_topic(path: Path) -> str:
    return unquote(path.stem)


def analysis_path(topic: str) -> Path:
    return MERCH_ANALYSIS_DIR / topic_to_filename(topic)


def list_cached_analysis_topics() -> list[str]:
    if MERCH_ANALYSIS_BUNDLE_PATH.exists():
        payload = json.loads(MERCH_ANALYSIS_BUNDLE_PATH.read_text(encoding="utf-8"))
        return sorted(payload.keys())
    if not MERCH_ANALYSIS_DIR.exists():
        return []
    return sorted(filename_to_topic(path) for path in MERCH_ANALYSIS_DIR.glob("*.json"))


def read_cached_analysis(topic: str) -> dict:
    if MERCH_ANALYSIS_BUNDLE_PATH.exists():
        payload = json.loads(MERCH_ANALYSIS_BUNDLE_PATH.read_text(encoding="utf-8"))
        if topic not in payload:
            raise FileNotFoundError(f"Merch analysis cache not found for {topic}")
        return normalize_analysis_payload(topic, payload[topic])
    path = analysis_path(topic)
    if not path.exists():
        raise FileNotFoundError(f"Merch analysis cache not found for {topic}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return normalize_analysis_payload(topic, payload)


def write_cached_analysis(topic: str, payload: dict) -> Path:
    MERCH_ANALYSIS_BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    bundle = {}
    if MERCH_ANALYSIS_BUNDLE_PATH.exists():
        bundle = json.loads(MERCH_ANALYSIS_BUNDLE_PATH.read_text(encoding="utf-8"))
    bundle[topic] = normalize_analysis_payload(topic, payload)
    MERCH_ANALYSIS_BUNDLE_PATH.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    return MERCH_ANALYSIS_BUNDLE_PATH


def normalize_analysis_payload(topic: str, payload: dict) -> dict:
    if should_use_presentation_payload(payload):
        return build_presentation_analysis_payload(topic, payload)
    title = payload.get("title") if isinstance(payload.get("title"), dict) else {}
    subtitle = payload.get("subtitle") if isinstance(payload.get("subtitle"), dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    forecast = payload.get("forecast") if isinstance(payload.get("forecast"), dict) else {}
    quote_payload = payload.get("quote") if isinstance(payload.get("quote"), dict) else {}
    topic_en = str(title.get("en") or payload.get("topic_en") or topic).strip()
    topic_zh = str(title.get("zh") or payload.get("topic") or topic).strip()
    suggestions = payload.get("suggestions") if isinstance(payload.get("suggestions"), list) else []
    return {
        "id": str(payload.get("id") or f"cached-{safe_id(topic)}"),
        "topic": topic,
        "title": {"zh": topic_zh, "en": topic_en},
        "subtitle": {"zh": str(subtitle.get("zh") or "").strip(), "en": str(subtitle.get("en") or "").strip()},
        "summary": {
            "zh": str(summary.get("zh") or payload.get("summary_zh") or f"{topic} 已有具体帖子/评论文本，可用于选品分析。").strip(),
            "en": str(summary.get("en") or payload.get("summary_en") or f"{topic_en} has collected post/comment evidence for merchandising analysis.").strip(),
        },
        "forecast": {
            "zh": str(forecast.get("zh") or "+文本证据").strip(),
            "en": str(forecast.get("en") or "+Evidence-backed").strip(),
        },
        "keywords": normalize_keywords(payload.get("keywords"), topic_zh, topic_en),
        "heatTerms": sorted(set([topic, topic_zh, topic_en, *(payload.get("heatTerms") or [])])),
        "quote": {
            "zh": str(quote_payload.get("zh") or "该话题同时具备榜单热度和可阅读的文本证据。").strip(),
            "en": str(quote_payload.get("en") or "This topic combines leaderboard heat with readable text evidence.").strip(),
        },
        "suggestions": [normalize_suggestion(item, index) for index, item in enumerate(suggestions[:6], start=1)],
        "strategy": normalize_bilingual_text(
            payload.get("strategy"),
            "先从高频评论问题和使用场景切入，再用小批量商品组合测试转化。",
            "Start from recurring comment questions and usage scenarios, then test conversion with small-batch product bundles.",
        ),
    }


def normalize_keywords(value: object, topic_zh: str, topic_en: str) -> list[dict]:
    if isinstance(value, list) and value:
        normalized = []
        for item in value[:4]:
            if isinstance(item, dict):
                label = item.get("label") if isinstance(item.get("label"), dict) else {}
                normalized.append(
                    {
                        "emoji": str(item.get("emoji") or "📌"),
                        "label": {
                            "zh": str(label.get("zh") or item.get("zh") or topic_zh),
                            "en": str(label.get("en") or item.get("en") or topic_en),
                        },
                    }
                )
        if normalized:
            return normalized
    return [
        {"emoji": "🔥", "label": {"zh": topic_zh, "en": topic_en}},
        {"emoji": "📄", "label": {"zh": "帖子/评论证据", "en": "Post/comment evidence"}},
    ]


def normalize_suggestion(item: object, index: int) -> dict:
    data = item if isinstance(item, dict) else {}
    return {
        "product_name": normalize_text_value(data.get("product_name") or data.get("name"), f"商品方向 {index}", f"Product Direction {index}"),
        "category": normalize_text_value(data.get("category"), "未分类", "Uncategorized"),
        "target_users": ensure_list(data.get("target_users") or data.get("user_needs")),
        "use_scenarios": ensure_list(data.get("use_scenarios") or data.get("scenarios")),
        "why_recommended": normalize_text_value(
            data.get("why_recommended") or data.get("why"),
            "围绕当前趋势需求设计，适合快速验证商品转化。",
            "Designed around current demand signals and suitable for fast conversion testing.",
        ),
        "evidence": ensure_list(data.get("evidence") or data.get("evidence_posts")),
        "selling_points": ensure_list(data.get("selling_points")),
        "pricing_hint": normalize_text_value(data.get("pricing_hint"), "按款式和材质分层定价", "Tier pricing by style and material"),
        "risk_note": normalize_text_value(
            data.get("risk_note") or data.get("risk"),
            "注意供应稳定性、图片一致性和售后预期。",
            "Watch supply stability, image consistency, and after-sales expectations.",
        ),
    }


def normalize_bilingual_text(value: object, zh_fallback: str, en_fallback: str) -> dict:
    if isinstance(value, dict):
        return {"zh": str(value.get("zh") or zh_fallback), "en": str(value.get("en") or en_fallback)}
    if isinstance(value, str) and value.strip():
        return {"zh": value.strip(), "en": en_fallback}
    return {"zh": zh_fallback, "en": en_fallback}


def ensure_list(value: object) -> list[str]:
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict):
                zh = str(item.get("zh") or "").strip()
                en = str(item.get("en") or "").strip()
                if zh or en:
                    result.append({"zh": zh or en, "en": en or zh})
            elif str(item).strip():
                result.append(str(item).strip())
        return result
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_text_value(value: object, zh_fallback: str, en_fallback: str) -> object:
    if isinstance(value, dict):
        zh = str(value.get("zh") or zh_fallback).strip()
        en = str(value.get("en") or en_fallback).strip()
        return {"zh": zh, "en": en}
    if isinstance(value, str) and value.strip():
        return value.strip()
    return {"zh": zh_fallback, "en": en_fallback}


def has_cjk(value: object) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", json.dumps(value, ensure_ascii=False)))


def should_use_presentation_payload(payload: dict) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    markers = ["AI 选品分析", "AI merchandising analysis", "已收录", "collected post samples", "本地文本样本", "local text samples"]
    return payload.get("generation_source") == "local_fallback" or any(marker in text for marker in markers)


def topic_en(topic: str) -> str:
    return TOPIC_EN_NAMES.get(topic, topic)


def theme_pair(theme: str) -> dict:
    theme = theme or "内容需求"
    return {"zh": theme, "en": THEME_EN_NAMES.get(theme, "consumer interest")}


def category_pair(category: str) -> dict:
    return {"zh": category, "en": CATEGORY_EN_NAMES.get(category, "Lifestyle")}


def build_presentation_analysis_payload(topic: str, payload: dict | None = None) -> dict:
    posts = read_keyword_topic_posts(topic)
    summary = local_heuristic_summary(posts)
    theme = summary.get("theme_top", [["内容需求"]])[0][0] if summary.get("theme_top") else "内容需求"
    category = categorize_topic(topic)
    theme_text = theme_pair(theme)
    title_en = topic_en(topic)
    evidence = [
        {"zh": f"{topic}的热门讨论集中在{theme_text['zh']}。", "en": f"Popular discussion around {title_en} centers on {theme_text['en']}."},
        {"zh": "用户更容易被明确场景、款式差异和组合价值吸引。", "en": "Users respond better to clear use cases, style differences, and bundle value."},
        {"zh": "适合用短内容展示使用效果、搭配方式或送礼理由。", "en": "Short-form content can show the use effect, styling method, or gifting reason."},
    ]
    return {
        "id": str((payload or {}).get("id") or f"cached-{safe_id(topic)}"),
        "topic": topic,
        "title": {"zh": topic, "en": title_en},
        "subtitle": {"zh": "", "en": ""},
        "summary": {
            "zh": f"{topic}的热度来自清晰的{theme_text['zh']}需求，适合围绕具体场景、风格和组合方案做选品。",
            "en": f"{title_en} is driven by clear {theme_text['en']} demand, making it suitable for product ideas built around specific use cases, styles, and bundles.",
        },
        "forecast": {"zh": "+值得关注", "en": "+Worth watching"},
        "keywords": [
            {"emoji": "🔥", "label": {"zh": topic, "en": title_en}},
            {"emoji": "📌", "label": theme_text},
        ],
        "heatTerms": sorted(set([topic, title_en, *((payload or {}).get("heatTerms") or [])])),
        "quote": {
            "zh": f"优先选择能让用户一眼理解用途的{category}商品，并用场景化内容降低决策成本。",
            "en": f"Prioritize {CATEGORY_EN_NAMES.get(category, 'lifestyle')} products with clear use cases, then use scenario-led content to reduce purchase friction.",
        },
        "suggestions": build_presentation_suggestions(topic, title_en, category, theme_text, evidence),
        "strategy": {
            "zh": "用三步验证：先选一个明确场景做主推，再准备不同价位的组合，最后用短内容测试点击、收藏和加购反馈。",
            "en": "Validate in three steps: lead with one clear scenario, prepare bundles across price tiers, then test clicks, saves, and add-to-cart signals with short-form content.",
        },
    }


def build_presentation_suggestions(topic: str, title_en: str, category: str, theme: dict, evidence: list[str]) -> list[dict]:
    category_value = category_pair(category)
    return [
        {
            "product_name": {"zh": f"{topic}场景入门套装", "en": f"{title_en} Starter Kit"},
            "category": category_value,
            "target_users": [{"zh": "首次尝试用户", "en": "first-time buyers"}, {"zh": "高意向搜索用户", "en": "high-intent search users"}],
            "use_scenarios": [{"zh": "入门尝试", "en": "first trial"}, {"zh": "内容种草", "en": "content seeding"}],
            "why_recommended": {
                "zh": f"把{theme['zh']}需求做成低门槛组合，用户更容易理解购买理由。",
                "en": f"Turns {theme['en']} demand into a low-barrier bundle with an easy-to-understand purchase reason.",
            },
            "evidence": evidence[:1],
            "selling_points": [{"zh": "选择成本低", "en": "low decision effort"}, {"zh": "适合快速上新", "en": "quick to launch"}, {"zh": "容易做内容展示", "en": "easy to demonstrate in content"}],
            "pricing_hint": {"zh": "入门价位", "en": "entry-level pricing"},
            "risk_note": {"zh": "避免套装过复杂，先保留最容易理解的核心组合。", "en": "Avoid overcomplicated bundles; keep the first offer easy to understand."},
        },
        {
            "product_name": {"zh": f"{topic}进阶风格款", "en": f"{title_en} Style Upgrade"},
            "category": category_value,
            "target_users": [{"zh": "愿意比较款式的用户", "en": "style-comparison shoppers"}, {"zh": "复购用户", "en": "repeat buyers"}],
            "use_scenarios": [{"zh": "换季/换风格", "en": "seasonal refresh"}, {"zh": "社交分享", "en": "social sharing"}],
            "why_recommended": {
                "zh": "用更明确的风格、颜色或材质分层承接用户的比较需求。",
                "en": "Uses clearer style, color, or material tiers to serve shoppers who compare options before buying.",
            },
            "evidence": evidence[1:2] or evidence[:1],
            "selling_points": [{"zh": "风格差异清楚", "en": "clear style differences"}, {"zh": "适合做系列化陈列", "en": "works as a product series"}, {"zh": "提升客单价", "en": "raises average order value"}],
            "pricing_hint": {"zh": "中档价位", "en": "mid-tier pricing"},
            "risk_note": {"zh": "图片、标题和实际款式需要保持一致。", "en": "Keep images, titles, and actual variants consistent."},
        },
        {
            "product_name": {"zh": f"{topic}礼品组合包", "en": f"{title_en} Gift Bundle"},
            "category": category_value,
            "target_users": [{"zh": "送礼用户", "en": "gift buyers"}, {"zh": "场景消费用户", "en": "occasion-led shoppers"}],
            "use_scenarios": [{"zh": "节日送礼", "en": "holiday gifting"}, {"zh": "小预算惊喜", "en": "small-budget surprise"}],
            "why_recommended": {
                "zh": "把单品包装成有场景的组合，更适合在节点和社交内容里转化。",
                "en": "Packages single items into an occasion-led bundle that converts better around seasonal moments and social content.",
            },
            "evidence": evidence[2:3] or evidence[:1],
            "selling_points": [{"zh": "送礼理由明确", "en": "clear gifting reason"}, {"zh": "包装感更强", "en": "stronger presentation value"}, {"zh": "适合限时活动", "en": "fits limited-time campaigns"}],
            "pricing_hint": {"zh": "组合价位", "en": "bundle pricing"},
            "risk_note": {"zh": "控制库存和履约复杂度，先从少量组合测试。", "en": "Control inventory and fulfillment complexity; start with a small set of bundles."},
        },
    ]


def safe_id(value: str) -> str:
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value.strip().lower(), flags=re.UNICODE).strip("-")
    return normalized or "topic"


def list_weekly_merch_topics(week: str, limit: int = MERCH_WEEKLY_LIMIT) -> list[dict]:
    cached_topics = set(list_cached_analysis_topics())
    rows = read_hotboard(week)
    selected = []
    seen = set()
    for row in rows:
        keyword = str(row.get("keyword") or "").strip()
        topic = resolve_keyword_topic_name(keyword, keyword)
        if not topic or topic in seen or topic not in cached_topics:
            continue
        analysis = read_cached_analysis(topic)
        selected.append(
            {
                "id": analysis["id"],
                "topic": topic,
                "title": analysis["title"],
                "subtitle": analysis["subtitle"],
                "summary": analysis["summary"],
                "forecast": analysis["forecast"],
                "keywords": analysis["keywords"],
                "category": categorize_topic(topic),
                "heat": row.get("search_index", 0),
                "rank": row.get("rank"),
                "matched_term": keyword,
            }
        )
        seen.add(topic)
        if len(selected) >= limit:
            break
    return selected


def build_local_analysis_payload(topic: str) -> dict:
    return build_presentation_analysis_payload(topic)
