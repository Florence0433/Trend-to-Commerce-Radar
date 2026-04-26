from __future__ import annotations

import json
import urllib.parse
import re
import urllib.request

from backend.app.config import (
    GENERATION_API_KEY,
    GENERATION_API_URL,
    GENERATION_FALLBACK_ON_ERROR,
    GENERATION_MODEL,
    GENERATION_PREFER_REMOTE,
    GENERATION_TIMEOUT_SECONDS,
    GENERATION_TRANSLATE_WITH_API,
    GENERATION_TRANSLATION_TIMEOUT_SECONDS,
)
from backend.app.services.data_service import (
    list_available_models,
    list_topics,
    list_weeks,
    read_local_summary,
    read_model_suggestion,
    read_topic_posts,
    safe_int,
    summarize_hotboard,
    summarize_topic_posts,
)
from backend.app.services.keyword_topic_service import (
    compact_posts_for_prompt,
    keyword_topic_status_report,
    local_heuristic_summary,
    read_keyword_topic_posts,
    read_selected_keyword_topics,
    resolve_keyword_topic_name,
    summarize_keyword_topic_posts,
)


DEFAULT_MODE = "product_ideas"
MODE_PRODUCT_IDEAS = "product_ideas"
MODE_QUICK_SUMMARY = "quick_summary"
MODE_DETAILED = "detailed"
VALID_MODES = {MODE_PRODUCT_IDEAS, MODE_QUICK_SUMMARY, MODE_DETAILED}
PREFERRED_WEEKLY_MODELS = ("deepseek_v3", "glm5", "kimi_k25")
ENGLISH_GLOSSARY_REPLACEMENTS = [
    (r"#拼豆图纸", "#PerlerBeadPatterns"),
    (r"#我染上了拼豆", "#HookedOnPerlerBeads"),
    (r"#拼豆日常", "#PerlerBeadDaily"),
    (r"#拼豆教程", "#PerlerBeadTutorial"),
    (r"#拼豆", "#PerlerBeads"),
    (r"我染上了拼豆", "Hooked on perler beads"),
    (r"拼豆图纸", "perler bead patterns"),
    (r"拼豆教程", "perler bead tutorial"),
    (r"拼豆日常", "perler bead daily content"),
    (r"材料包", "kit"),
    (r"图纸生成工具", "pattern generator tool"),
    (r"图纸定制", "custom pattern design"),
    (r"图纸分享", "pattern sharing"),
    (r"图纸", "patterns"),
    (r"杯垫", "coasters"),
    (r"钥匙扣", "keychains"),
    (r"收纳神器", "storage organizer"),
    (r"收纳", "storage"),
    (r"教程", "tutorial"),
    (r"帖子", "posts"),
    (r"评论区", "comments"),
    (r"返图", "user remake posts"),
    (r"老师", "creator"),
    (r"评论：", "Comment: "),
    (r"点赞", "likes"),
    (r"拼豆", "Perler beads"),
]
ENGLISH_REGEX_REPLACEMENTS = [
    (r"\bPindou\s*\(\s*Perler beads\s*\)", "Perler beads"),
    (r"\bPindou\s*\(\s*拼豆\s*\)", "Perler beads"),
    (r"\bPindou\b", "Perler beads"),
]
FALLBACK_SUGGESTION_TOPICS = ["穿搭", "手机壳", "拼豆", "蛋糕", "花束", "穿戴甲", "防晒霜推荐"]
TOPIC_DISPLAY_NAMES = {
    "穿搭": {"zh": "穿搭", "en": "Outfits"},
    "手机壳": {"zh": "手机壳", "en": "Phone cases"},
    "拼豆": {"zh": "拼豆", "en": "Perler beads"},
    "蛋糕": {"zh": "蛋糕", "en": "Cakes"},
    "花束": {"zh": "花束", "en": "Bouquets"},
    "穿戴甲": {"zh": "穿戴甲", "en": "Press-on nails"},
    "防晒霜推荐": {"zh": "防晒霜推荐", "en": "Sunscreen recommendations"},
    "外套": {"zh": "外套", "en": "Outerwear"},
}
RELATED_TOPIC_HINT_GROUPS = [
    ({"dress", "dresses", "fashion", "clothes", "clothing", "outfit", "outfits", "styling"}, ["穿搭", "外套"]),
    ({"toy", "toys", "craft", "crafts", "diy", "bead", "beads", "perler", "fuse", "handmade"}, ["拼豆"]),
    ({"cake", "cakes", "dessert", "desserts", "bakery", "sweet"}, ["蛋糕"]),
    ({"flower", "flowers", "bouquet", "bouquets", "floral", "gift"}, ["花束"]),
    ({"nail", "nails", "manicure", "presson", "press-on"}, ["穿戴甲"]),
    ({"phone", "iphone", "case", "cases", "cover", "covers", "accessory", "accessories"}, ["手机壳"]),
    ({"storage", "organizer", "organizers", "organization", "organize", "home", "declutter"}, ["家居收纳"]),
    ({"sunscreen", "sunblock", "spf", "uv"}, ["防晒霜推荐"]),
    ({"shampoo", "haircare", "scalp", "hair"}, ["洗发水推荐", "染发发色推荐"]),
]


def normalize_optional_text(value: str | None) -> str | None:
    text = (value or "").strip()
    return text or None


def normalize_mode(mode: str | None) -> str:
    normalized = normalize_optional_text(mode) or DEFAULT_MODE
    return normalized if normalized in VALID_MODES else DEFAULT_MODE


def build_generation_result(
    question: str,
    week: str | None = None,
    topic: str | None = None,
    mode: str = DEFAULT_MODE,
    language: str | None = None,
) -> dict:
    normalized_mode = normalize_mode(mode)
    output_language = resolve_output_language(question=question, requested_language=language)
    resolved_topic = resolve_keyword_topic_name(topic, question)
    resolved_week = resolve_generation_week(resolved_topic, normalize_optional_text(week))
    status_report = keyword_topic_status_report()

    if not resolved_topic:
        return build_missing_topic_result(
            question=question,
            requested_topic=normalize_optional_text(topic),
            week=resolved_week,
            mode=normalized_mode,
            language=output_language,
            missing_topics=status_report["missing_unique_topics"],
        )

    if resolved_topic not in status_report["available_unique_topics"]:
        weekly_fallback = build_weekly_topic_fallback_result(
            question=question,
            week=resolved_week,
            topic=resolved_topic,
            mode=normalized_mode,
            language=output_language,
        )
        if weekly_fallback:
            return weekly_fallback
        return build_missing_topic_result(
            question=question,
            requested_topic=resolved_topic,
            week=resolved_week,
            mode=normalized_mode,
            language=output_language,
            missing_topics=status_report["missing_unique_topics"],
        )

    context = build_context_bundle(resolved_week, resolved_topic)
    saved_model_result = build_weekly_topic_fallback_result(
        question=question,
        week=resolved_week,
        topic=resolved_topic,
        mode=normalized_mode,
        language=output_language,
    )

    if saved_model_result and not GENERATION_PREFER_REMOTE:
        saved_model_result["generation_source"] = "local_saved_model_suggestion"
        saved_model_result.setdefault("context", {})["fallback_reason"] = localized_text(
            output_language,
            zh="本地运行默认使用已保存的周榜模型建议，以保证完整问答快速可用。",
            en="Local running uses saved weekly model suggestions by default so full Q&A stays fast and available.",
        )
        return saved_model_result

    if not (GENERATION_API_URL and GENERATION_API_KEY and GENERATION_MODEL):
        if saved_model_result:
            saved_model_result["generation_source"] = "local_saved_model_suggestion"
            saved_model_result.setdefault("context", {})["fallback_reason"] = localized_text(
                output_language,
                zh="本地运行未配置远程模型，已使用已保存的周榜模型建议生成完整问答。",
                en="Remote generation is not configured for local running, so this answer uses saved weekly model suggestions.",
            )
            return saved_model_result
        return synthesize_local_result(
            question=question,
            week=resolved_week,
            topic=resolved_topic,
            mode=normalized_mode,
            language=output_language,
            context=context,
        )

    try:
        prediction = call_remote_generation_api(
            question=question,
            week=resolved_week,
            topic=resolved_topic,
            mode=normalized_mode,
            language=output_language,
            context=context,
        )
    except Exception as exc:
        if not GENERATION_FALLBACK_ON_ERROR:
            raise
        if saved_model_result:
            saved_model_result["generation_source"] = "remote_error_saved_model_fallback"
            saved_model_result.setdefault("context", {})["remote_error"] = str(exc)
            return saved_model_result
        fallback = synthesize_local_result(
            question=question,
            week=resolved_week,
            topic=resolved_topic,
            mode=normalized_mode,
            language=output_language,
            context=context,
        )
        fallback["generation_source"] = "remote_generation_fallback"
        fallback.setdefault("context", {})["remote_error"] = str(exc)
        return fallback
    return normalize_remote_result(
        question=question,
        week=resolved_week,
        topic=resolved_topic,
        mode=normalized_mode,
        language=output_language,
        context=context,
        prediction=prediction,
        missing_topics=status_report["missing_unique_topics"],
    )


def resolve_generation_week(topic: str | None, requested_week: str | None) -> str | None:
    if requested_week:
        return requested_week
    if not topic:
        return None

    selected_rows = read_selected_keyword_topics()
    for row in reversed(selected_rows):
        if row["topic"] == topic:
            return row["week"]
    return find_latest_week_for_topic(topic)


def find_latest_week_for_topic(topic: str | None) -> str | None:
    if not topic:
        return None
    weeks = [item.get("week") for item in list_weeks()][::-1]
    for week in weeks:
        if not week:
            continue
        try:
            topics = {str(item.get("topic") or "").strip() for item in list_topics(week)}
        except FileNotFoundError:
            continue
        if topic in topics:
            return week
    return None


def build_context_bundle(week: str | None, topic: str) -> dict:
    posts = read_keyword_topic_posts(topic)
    local_summary = local_heuristic_summary(posts)
    posts_meta = summarize_keyword_topic_posts(topic)
    week_summary = None
    if week:
        try:
            week_summary = summarize_hotboard(week)
        except FileNotFoundError:
            week_summary = None

    return {
        "week_summary": week_summary,
        "posts_meta": posts_meta,
        "local_summary": local_summary,
        "posts": posts,
    }


def select_weekly_model(week: str, topic: str) -> str | None:
    available_models = [item.get("id") for item in list_available_models(week, topic)]
    for model in PREFERRED_WEEKLY_MODELS:
        if model in available_models:
            return model
    return available_models[0] if available_models else None


def summarize_weekly_local_summary(topic: str, local_summary: dict, language: str) -> str:
    theme_top = local_summary.get("theme_top") or []
    top_theme = theme_top[0][0] if theme_top else localized_text(language, zh="内容需求", en="content demand")
    if language == "en":
        top_theme = english_safe_saved_text(top_theme, "content demand")
    return localized_text(
        language,
        zh=f"`{topic}` 已在周榜样本中出现，当前最突出的内容主题是 `{top_theme}`。",
        en=f"`{topic}` already appears in the weekly topic runs, with `{top_theme}` as the strongest content pattern.",
    )


def build_weekly_post_evidence(posts: list[dict]) -> list[dict]:
    evidence = []
    for post in posts[:5]:
        evidence.append(
            {
                "title": str(post.get("note_title") or post.get("search_title") or post.get("title") or "Untitled").strip(),
                "author": str(post.get("nickname") or post.get("author") or "").strip(),
                "likes": safe_int(post.get("note_like_count") or post.get("liked_count")),
                "collects": safe_int(post.get("note_collect_count") or post.get("collected_count")),
                "comments": safe_int(post.get("note_comment_count") or post.get("comment_count")),
                "snippet": str(post.get("note_desc") or post.get("desc") or "")[:180],
            }
        )
    return evidence


def normalize_weekly_suggestions(suggestions: list[dict], source_model: str, language: str) -> list[dict]:
    product_ideas = []
    for index, item in enumerate(suggestions[:5], start=1):
        name = english_safe_saved_text(
            str(item.get("product_name") or item.get("name") or "").strip(),
            f"Product idea {index}",
        ) if language == "en" else str(item.get("product_name") or item.get("name") or "").strip()
        if not name:
            continue
        product_ideas.append(
            {
                "name": name,
                "category": (
                    english_safe_saved_text(str(item.get("category") or item.get("format") or "Uncategorized").strip(), "Product category")
                    if language == "en"
                    else str(item.get("category") or item.get("format") or "未分类").strip()
                ),
                "pricing_hint": english_safe_saved_text(str(item.get("pricing_hint") or "To be priced").strip(), "To be priced")
                if language == "en"
                else str(item.get("pricing_hint") or "待定价").strip(),
                "target_users": normalize_saved_string_list(item.get("target_users") or item.get("user_needs"), language),
                "use_scenarios": normalize_saved_string_list(item.get("use_scenarios") or item.get("scenarios"), language),
                "why": (
                    english_safe_saved_text(
                        str(item.get("why_recommended") or item.get("why_now") or "").strip(),
                        "Saved post and comment evidence shows clear user demand for this product direction.",
                    )
                    if language == "en"
                    else str(item.get("why_recommended") or item.get("why_now") or "").strip()
                ),
                "risk": (
                    english_safe_saved_text(str(item.get("risk_note") or item.get("risk") or "").strip(), "")
                    if language == "en"
                    else str(item.get("risk_note") or item.get("risk") or "").strip()
                ),
                "evidence": normalize_saved_string_list(item.get("evidence") or item.get("evidence_posts"), language),
                "selling_points": normalize_saved_string_list(item.get("selling_points"), language),
                "source_model": source_model,
            }
        )
    return product_ideas


def build_weekly_topic_fallback_result(
    question: str,
    week: str | None,
    topic: str,
    mode: str,
    language: str,
) -> dict | None:
    resolved_week = week or find_latest_week_for_topic(topic)
    if not resolved_week:
        return None

    try:
        available_topics = {str(item.get("topic") or "").strip() for item in list_topics(resolved_week)}
    except FileNotFoundError:
        fallback_week = find_latest_week_for_topic(topic)
        if not fallback_week:
            return None
        resolved_week = fallback_week
        try:
            available_topics = {str(item.get("topic") or "").strip() for item in list_topics(resolved_week)}
        except FileNotFoundError:
            return None
    if topic not in available_topics:
        fallback_week = find_latest_week_for_topic(topic)
        if not fallback_week:
            return None
        resolved_week = fallback_week

    try:
        posts_meta = summarize_topic_posts(resolved_week, topic)
        local_summary = read_local_summary(resolved_week, topic)
        posts = read_topic_posts(resolved_week, topic, limit=5)
    except FileNotFoundError:
        return None

    model_id = select_weekly_model(resolved_week, topic)
    suggestion_payload = {}
    if model_id:
        try:
            suggestion_payload = read_model_suggestion(resolved_week, topic, model_id)
        except FileNotFoundError:
            suggestion_payload = {}

    summary = str(suggestion_payload.get("summary") or "").strip() or summarize_weekly_local_summary(topic, local_summary, language)
    if language == "en":
        summary = english_safe_saved_text(
            summary,
            f"`{localize_topic_name(topic, 'en') or topic}` has strong commerce potential based on saved post and comment evidence.",
        )
    product_ideas = normalize_weekly_suggestions(
        suggestion_payload.get("suggestions") or [],
        source_model=model_id or "local_summary",
        language=language,
    )
    risks = [item["risk"] for item in product_ideas if item.get("risk")]
    answer = str(suggestion_payload.get("answer") or "").strip()
    if language == "en" and answer:
        answer = english_safe_saved_text(answer, summary)
    if not answer:
        if product_ideas:
            answer = localized_text(
                language,
                zh="已根据周榜帖子样本和现成模型建议整理出可执行的商品方向，重点优先看图纸工具包、主题材料包和场景化礼品套装。",
                en="A practical answer has been assembled from the weekly topic posts and saved model suggestions, with the strongest directions in pattern toolkits, themed kits, and scene-based gift bundles.",
            )
        else:
            answer = summary

    try:
        week_summary = summarize_hotboard(resolved_week)
    except FileNotFoundError:
        week_summary = None

    payload = {
        "question": question,
        "mode": normalize_mode(mode),
        "resolved_week": resolved_week,
        "resolved_topic": topic,
        "summary": summary,
        "why": [],
        "product_ideas": product_ideas,
        "risk": risks[:5],
        "evidence": build_weekly_post_evidence(posts),
        "answer": answer,
        "generation_source": "weekly_topic_model_suggestion",
        "output_language": language,
        "context": {
            "week_summary": week_summary,
            "posts_meta": posts_meta,
            "local_summary": local_summary,
            "used_post_count": posts_meta.get("post_count", 0),
            "fallback_reason": localized_text(
                language,
                zh="当前使用的是周榜帖子样本和已保存的模型建议回退结果，因为该主题还没有接入详细评论库。",
                en="This answer uses the weekly topic posts and saved model suggestions as a fallback because the topic is not yet connected to the detailed comment dataset.",
            ),
            "selected_model": model_id,
        },
    }
    payload = apply_mode_view(payload)
    if language == "en" and payload_contains_cjk(payload):
        payload = translate_payload_values(payload, target_language="en")
    return payload


def build_generation_prompt(question: str, week: str | None, topic: str, mode: str, language: str, context: dict) -> str:
    mode_guidance = mode_instruction_text(mode, language)
    payload = {
        "task": f"基于话题【{topic}】的小红书帖子和评论样本做商品预测分析",
        "question": question,
        "mode": normalize_mode(mode),
        "output_language": language,
        "mode_guidance": mode_guidance,
        "resolved_week": week,
        "goal": [
            "判断这个话题是否有明确商业转化机会",
            "给出最值得做的 5 个商品方向",
            "每个方向说明为什么值得做、适合什么售卖形式、面向哪些用户",
            "引用帖子和评论中的证据，而不是空泛描述",
            "指出风险、供货难点或内容偏差风险",
        ],
        "local_heuristic_summary": context.get("local_summary"),
        "posts_meta": context.get("posts_meta"),
        "top_posts": compact_posts_for_prompt(context.get("posts", []), top_n=20),
        "json_schema": {
            "summary": "一句话赛道判断",
            "answer": "一段结构化文字总结",
            "opportunities": [
                {
                    "product_name": "商品方向名",
                    "category": "商品类别",
                    "format": "成品/材料包/工具耗材/图纸订阅/定制服务",
                    "why_recommended": "为什么值得做",
                    "target_users": ["用户1", "用户2"],
                    "use_scenarios": ["场景1", "场景2"],
                    "evidence": ["帖子或评论证据1", "帖子或评论证据2"],
                    "pricing_hint": "价格带",
                    "risk_note": "主要风险",
                    "selling_points": ["卖点1", "卖点2"],
                }
            ],
            "risk": ["整体风险1", "整体风险2"],
            "why": ["支持结论的原因1", "支持结论的原因2"],
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def call_remote_generation_api(question: str, week: str | None, topic: str, mode: str, language: str, context: dict) -> dict:
    prompt = build_generation_prompt(question=question, week=week, topic=topic, mode=mode, language=language, context=context)
    body = call_chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "你是电商选品分析师。请根据小红书热点话题下的帖子与评论内容，提炼用户需求、消费场景与可售商品方向。"
                    "输出必须是 JSON，并且要给出具体证据，不要空泛。"
                    "如果 output_language 是 en，请把所有 value 都写成英文；如果是 zh，请把所有 value 都写成中文。"
                    "JSON key 保持英文。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    content = extract_content_from_response(body)
    parsed = parse_json_content(content)
    parsed["_raw_response"] = body
    return parsed


def call_chat_completion(messages: list[dict], temperature: float) -> dict:
    payload = {
        "model": GENERATION_MODEL,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": messages,
    }
    request = urllib.request.Request(
        GENERATION_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GENERATION_API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=GENERATION_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_remote_result(
    question: str,
    week: str | None,
    topic: str,
    mode: str,
    language: str,
    context: dict,
    prediction: dict,
    missing_topics: list[str],
) -> dict:
    summary = prediction.get("summary") or ""
    if isinstance(summary, list):
        summary = " ".join(str(item).strip() for item in summary if str(item).strip())

    why = ensure_string_list(prediction.get("why"))
    opportunities = prediction.get("opportunities") or prediction.get("suggestions") or prediction.get("product_ideas") or []
    product_ideas = []
    for item in opportunities[:5]:
        name = str(item.get("product_name") or item.get("name") or "").strip()
        if not name:
            continue
        product_ideas.append(
            {
                "name": name,
                "category": str(item.get("category") or item.get("format") or "未分类").strip(),
                "pricing_hint": str(item.get("pricing_hint") or "待定价").strip(),
                "target_users": ensure_string_list(item.get("target_users") or item.get("user_needs")),
                "use_scenarios": ensure_string_list(item.get("use_scenarios") or item.get("scenarios")),
                "why": str(item.get("why_recommended") or item.get("why_now") or "").strip(),
                "risk": str(item.get("risk_note") or item.get("risk") or "").strip(),
                "evidence": ensure_string_list(item.get("evidence") or item.get("evidence_posts")),
                "selling_points": ensure_string_list(item.get("selling_points")),
                "source_model": GENERATION_MODEL,
            }
        )

    risks = ensure_string_list(prediction.get("risk"))
    if not risks:
        risks = [item["risk"] for item in product_ideas if item["risk"]]

    evidence = build_evidence_from_ideas(product_ideas, context.get("posts", []))
    answer = str(prediction.get("answer") or "").strip()
    if not answer:
        answer_parts = [summary] if summary else []
        if why:
            answer_parts.append("Why: " + " ".join(why[:3]))
        if product_ideas:
            answer_parts.append(
                "Ideas: " + "; ".join(f"{item['name']} ({item['pricing_hint']})" for item in product_ideas[:3])
            )
        if risks:
            answer_parts.append("Risks: " + "; ".join(risks[:3]))
        answer = "\n\n".join(part for part in answer_parts if part)

    normalized_payload = {
        "question": question,
        "mode": normalize_mode(mode),
        "resolved_week": week,
        "resolved_topic": topic,
        "summary": summary,
        "why": why,
        "product_ideas": product_ideas,
        "risk": risks,
        "evidence": evidence,
        "answer": answer,
        "generation_source": "deepseek_keyword_topic_analysis",
        "output_language": language,
        "context": {
            "week_summary": context.get("week_summary"),
            "posts_meta": context.get("posts_meta"),
            "used_post_count": len(context.get("posts", [])),
            "missing_detailed_topics": missing_topics,
        },
    }

    normalized_payload = apply_mode_view(normalized_payload)

    if language == "en" and payload_contains_cjk(normalized_payload):
        normalized_payload = translate_payload_values(normalized_payload, target_language="en")

    return normalized_payload


def synthesize_local_result(question: str, week: str | None, topic: str, mode: str, language: str, context: dict) -> dict:
    posts_meta = context.get("posts_meta") or {}
    local_summary = context.get("local_summary") or {}
    theme_top = local_summary.get("theme_top") or []
    top_theme = theme_top[0][0] if theme_top else localized_text(language, zh="内容需求", en="content demand")
    summary = localized_text(
        language,
        zh=(
            f"`{topic}` 已经有详细帖子和评论数据"
            + (f"，对应周次 `{week}`" if week else "")
            + f"，共 {posts_meta.get('post_count', 0)} 条帖子，当前最强主题是 `{top_theme}`。"
            "外部模型当前不可用或未配置，所以后端先返回本地摘要框架。"
        ),
        en=(
            f"`{topic}` already has detailed post and comment data"
            + (f" for week `{week}`" if week else "")
            + f", with {posts_meta.get('post_count', 0)} posts and a strongest theme of `{top_theme}`. "
            "Remote generation is unavailable or not configured, so the backend is returning a local summary scaffold."
        ),
    )
    payload = {
        "question": question,
        "mode": normalize_mode(mode),
        "resolved_week": week,
        "resolved_topic": topic,
        "summary": summary,
        "why": [],
        "product_ideas": [],
        "risk": [],
        "evidence": build_evidence_from_posts(context.get("posts", [])),
        "answer": summary,
        "generation_source": "local_summary_only",
        "output_language": language,
        "context": {
            "week_summary": context.get("week_summary"),
            "posts_meta": posts_meta,
            "used_post_count": len(context.get("posts", [])),
        },
    }
    return apply_mode_view(payload)


def build_missing_topic_result(
    question: str,
    requested_topic: str | None,
    week: str | None,
    mode: str,
    language: str,
    missing_topics: list[str],
) -> dict:
    suggestions = suggest_fallback_topics(question, requested_topic)
    suggestion_text = " / ".join(localize_topic_name(item, language) for item in suggestions)
    requested_topic_label = localize_topic_name(requested_topic, language) if requested_topic else None
    if requested_topic:
        summary = localized_text(
            language,
            zh=f"我识别到了你可能在问“{requested_topic_label}”，但这个主题目前还没有可直接分析的详细帖子样本。",
            en=f"I could infer that you may be asking about '{requested_topic_label}', but this topic does not yet have detailed post samples ready for analysis.",
        )
        answer = localized_text(
            language,
            zh=(
                f"当前还不能直接给出基于详细帖子内容的判断。你是否想先了解这些相关话题：{suggestion_text}？"
                f" 也可以把问题再说具体一点，比如补充人群、场景或商品方向。"
            ),
            en=(
                f"I can't give a detailed evidence-based answer for this topic yet. You may want to explore related supported topics such as {suggestion_text}. "
                f"You can also make the request more specific by adding a user group, use case, or product direction."
            ),
        )
    else:
        summary = localized_text(
            language,
            zh="我还没能从这个问题里识别出一个明确的已支持主题。",
            en="I couldn't identify a clear supported topic from this question yet.",
        )
        answer = localized_text(
            language,
            zh=(
                f"你是否想先了解这些相关话题：{suggestion_text}？"
                f" 也可以把问题再说具体一点，例如直接写主题词，或者补充你想分析的商品、人群、场景。"
            ),
            en=(
                f"You may want to explore related supported topics such as {suggestion_text}. "
                f"You can also make the request more specific by naming the topic directly or adding the product type, audience, or use case you want to analyze."
            ),
        )
    risks = [localized_text(
        language,
        zh="当前缺少可直接引用的详细帖子与评论样本",
        en="Detailed post and comment samples are not available for this request yet",
    )
    ]
    payload = {
        "question": question,
        "mode": normalize_mode(mode),
        "resolved_week": week,
        "resolved_topic": requested_topic,
        "summary": summary,
        "why": [],
        "product_ideas": [],
        "risk": risks,
        "evidence": [],
        "answer": answer,
        "generation_source": "missing_detailed_topic",
        "output_language": language,
        "context": {
            "missing_detailed_topics": missing_topics,
            "suggested_topics": suggestions,
        },
    }
    normalized = apply_mode_view(payload)
    normalized["display_sections"] = ["summary", "answer", "risks"]
    return normalized


def suggest_fallback_topics(question: str, requested_topic: str | None = None, limit: int = 4) -> list[str]:
    candidates: list[str] = []
    if requested_topic:
        candidates.append(requested_topic)
    lowered = str(question or "").lower()
    for words, topic_names in RELATED_TOPIC_HINT_GROUPS:
        if any(word in lowered for word in words):
            candidates.extend(topic_names)
    candidates.extend(FALLBACK_SUGGESTION_TOPICS)
    deduped = []
    seen = set()
    for item in candidates:
        if not item or item in seen:
            continue
        seen.add(item)
        deduped.append(item)
        if len(deduped) >= limit:
            break
    return deduped


def localize_topic_name(topic: str | None, language: str) -> str:
    if not topic:
        return ""
    names = TOPIC_DISPLAY_NAMES.get(topic)
    if names:
        return names.get(language) or names.get("zh") or topic
    return topic


def resolve_output_language(question: str, requested_language: str | None = None) -> str:
    normalized = normalize_optional_text(requested_language)
    if normalized in {"zh", "en"}:
        return normalized
    if re.search(r"[\u4e00-\u9fff]", question or ""):
        return "zh"
    return "en"


def localized_text(language: str, *, zh: str, en: str) -> str:
    return zh if language == "zh" else en


def mode_instruction_text(mode: str, language: str) -> str:
    normalized_mode = normalize_mode(mode)
    if normalized_mode == MODE_QUICK_SUMMARY:
        return localized_text(
            language,
            zh="只返回简短判断：1句summary + 1段answer。不要展开商品机会列表；opportunities 最多 1 条或留空；risk 最多 2 条。",
            en="Return a concise judgment only: 1 summary sentence plus 1 short answer paragraph. Do not expand into a full product opportunity list; keep opportunities to at most 1 item or empty, and risk to at most 2 items.",
        )
    if normalized_mode == MODE_PRODUCT_IDEAS:
        return localized_text(
            language,
            zh="重点输出商品方向。summary 保持简短，answer 用 2-4 句概括，opportunities 输出 3-5 条具体建议，risk 保留 1-3 条。",
            en="Focus on product directions. Keep summary short, answer to 2-4 sentences, provide 3-5 concrete opportunities, and keep risk to 1-3 items.",
        )
    return localized_text(
        language,
        zh="输出完整分析。需要 summary、answer、3-5 条商品机会、why、risk 和证据，结构尽量完整。",
        en="Return the full analysis. Include summary, answer, 3-5 product opportunities, why, risk, and evidence in a complete structure.",
    )


def apply_mode_view(payload: dict) -> dict:
    mode = normalize_mode(payload.get("mode"))
    normalized = dict(payload)
    product_ideas = list(normalized.get("product_ideas") or [])
    risks = list(normalized.get("risk") or [])
    why = list(normalized.get("why") or [])
    answer = str(normalized.get("answer") or "").strip()
    summary = str(normalized.get("summary") or "").strip()

    if mode == MODE_QUICK_SUMMARY:
        normalized["product_ideas"] = []
        normalized["risk"] = risks[:2]
        if not answer:
            answer = summary
        elif summary and answer != summary:
            answer = f"{summary}\n\n{answer}"
        normalized["answer"] = answer.strip()
        normalized["display_sections"] = ["summary", "answer"]
    elif mode == MODE_PRODUCT_IDEAS:
        normalized["product_ideas"] = product_ideas[:5]
        normalized["risk"] = risks[:3]
        if not answer:
            top_names = ", ".join(item.get("name", "").strip() for item in normalized["product_ideas"][:3] if item.get("name"))
            answer = top_names or summary
        normalized["answer"] = answer.strip()
        normalized["display_sections"] = ["summary", "ideas", "risks"]
    else:
        normalized["product_ideas"] = product_ideas[:5]
        normalized["risk"] = risks[:5]
        normalized["why"] = why[:5]
        normalized["answer"] = answer or summary
        normalized["display_sections"] = ["summary", "answer", "ideas", "risks"]

    return normalized


def ensure_string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def payload_contains_cjk(value: object) -> bool:
    if isinstance(value, str):
        return bool(re.search(r"[\u4e00-\u9fff]", value))
    if isinstance(value, list):
        return any(payload_contains_cjk(item) for item in value)
    if isinstance(value, dict):
        return any(payload_contains_cjk(item) for item in value.values())
    return False


def translate_payload_values(value: object, target_language: str) -> object:
    if isinstance(value, str):
        return translate_text_value(value, target_language=target_language)
    if isinstance(value, list):
        return [translate_payload_values(item, target_language=target_language) for item in value]
    if isinstance(value, dict):
        return {key: translate_payload_values(item, target_language=target_language) for key, item in value.items()}
    return value


def translate_text_value(text: str, target_language: str) -> str:
    if target_language != "en":
        return text
    translated = text
    if payload_contains_cjk(text):
        translated = google_translate_text(text, target_language="en") or text
    return cleanup_english_text(translated)


def cleanup_english_text(text: str) -> str:
    cleaned = str(text or "")
    cleaned = re.sub(
        r"(\d+(?:\.\d+)?)万",
        lambda match: f"{int(float(match.group(1)) * 10000):,}",
        cleaned,
        flags=re.I,
    )
    for pattern, replacement in ENGLISH_GLOSSARY_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.I)
    for pattern, replacement in ENGLISH_REGEX_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.I)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


ENGLISH_THEME_FALLBACKS = {
    "教程攻略": "tutorial and how-to demand",
    "种草展示": "product seeding and showcase demand",
    "价格优惠": "price and discount sensitivity",
    "送礼礼物": "gifting demand",
    "搭配场景": "styling and usage scenarios",
    "功能解决方案": "functional problem-solving demand",
    "兴趣DIY": "DIY interest",
}


def english_safe_saved_text(text: str, fallback: str) -> str:
    cleaned = cleanup_english_text(text)
    if not cleaned:
        return fallback
    if cleaned in ENGLISH_THEME_FALLBACKS:
        return ENGLISH_THEME_FALLBACKS[cleaned]
    if payload_contains_cjk(cleaned):
        translated = google_translate_text(cleaned, target_language="en")
        translated = cleanup_english_text(translated) if translated else ""
        if translated and not payload_contains_cjk(translated):
            return translated
        return fallback
    return cleaned


def normalize_saved_string_list(values: object, language: str) -> list[str]:
    items = ensure_string_list(values)
    if language != "en":
        return items
    normalized = []
    for item in items:
        next_item = english_safe_saved_text(item, "")
        if next_item:
            normalized.append(next_item)
    return normalized


def google_translate_text(text: str, target_language: str) -> str:
    if not GENERATION_TRANSLATE_WITH_API:
        return ""
    query = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": "auto",
            "tl": target_language,
            "dt": "t",
            "q": text,
        }
    )
    url = f"https://translate.googleapis.com/translate_a/single?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=GENERATION_TRANSLATION_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
        chunks = body[0] if isinstance(body, list) and body else []
        return "".join(chunk[0] for chunk in chunks if isinstance(chunk, list) and chunk and chunk[0]).strip()
    except Exception:
        return text


def extract_content_from_response(resp: dict) -> str:
    choices = resp.get("choices") or []
    if not choices:
        raise RuntimeError("Missing choices in model response")
    first = choices[0]
    message = first.get("message") if isinstance(first, dict) else None
    if not message:
        raise RuntimeError("Missing message in model response")
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(part for part in text_parts if part).strip()
    raise RuntimeError(f"Unsupported content type: {type(content).__name__}")


def parse_json_content(content: str) -> dict:
    raw = (content or "").strip()
    if not raw:
        raise RuntimeError("Empty model content")
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, re.S)
    if match:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, dict):
            return parsed
    raise RuntimeError("Model did not return a valid JSON object")


def build_evidence_from_ideas(product_ideas: list[dict], posts: list[dict]) -> list[dict]:
    evidence = []
    seen = set()
    for item in product_ideas:
        for entry in item.get("evidence", []):
            if entry in seen:
                continue
            seen.add(entry)
            evidence.append({"title": entry, "snippet": entry})
            if len(evidence) >= 5:
                return evidence
    return evidence or build_evidence_from_posts(posts)


def build_evidence_from_posts(posts: list[dict]) -> list[dict]:
    ranked = sorted(posts, key=lambda item: item.get("engagement_score", 0), reverse=True)[:5]
    return [
        {
            "title": post.get("title") or "Untitled",
            "author": post.get("author") or "",
            "likes": post.get("likes") or 0,
            "collects": post.get("collects") or 0,
            "comments": post.get("comments") or 0,
            "snippet": str(post.get("desc") or "")[:180],
        }
        for post in ranked
    ]
