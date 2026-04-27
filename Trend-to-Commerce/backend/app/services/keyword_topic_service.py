from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from backend.app.config import KEYWORD_TOPIC_DIR
from backend.app.services.data_service import list_topics, list_weeks, safe_int


THEME_RULES = {
    "教程攻略": ["教程", "攻略", "怎么做", "步骤", "新手", "入门", "避坑", "测评", "推荐"],
    "种草展示": ["分享", "开箱", "展示", "返图", "合集", "安利", "种草", "实拍"],
    "价格优惠": ["平替", "便宜", "优惠", "折扣", "价格", "活动", "值得买", "必买"],
    "送礼礼物": ["礼物", "送人", "生日", "纪念", "情侣", "闺蜜", "伴手礼", "节日"],
    "搭配场景": ["穿搭", "搭配", "ootd", "上身", "通勤", "约会", "春季", "夏季"],
    "功能解决方案": ["收纳", "防晒", "防水", "修复", "漏水", "解决", "神器", "清洁"],
    "兴趣DIY": ["手工", "diy", "图纸", "材料包", "定制", "改造", "教程包"],
}

TOPIC_ALIASES = {
    "phonecases": "手机壳",
    "phonecase": "手机壳",
    "phone": "手机壳",
    "case": "手机壳",
    "cases": "手机壳",
    "pindou": "拼豆",
    "perler": "拼豆",
    "perlerbead": "拼豆",
    "perlerbeads": "拼豆",
    "fusebead": "拼豆",
    "fusebeads": "拼豆",
    "outfits": "穿搭",
    "outfit": "穿搭",
    "dress": "穿搭",
    "dresses": "穿搭",
    "clothes": "穿搭",
    "clothing": "穿搭",
    "fashion": "穿搭",
    "styling": "穿搭风格",
    "outfitstyling": "穿搭风格",
    "styledirection": "穿搭风格",
    "birthdaycake": "生日蛋糕",
    "birthdaycakes": "生日蛋糕",
    "cake": "蛋糕",
    "cakes": "蛋糕",
    "dessert": "蛋糕",
    "desserts": "蛋糕",
    "flower": "花束",
    "flowers": "花束",
    "floral": "花束",
    "bouquet": "花束",
    "bouquets": "花束",
    "nail": "穿戴甲",
    "nails": "穿戴甲",
    "manicure": "穿戴甲",
    "pressonnail": "穿戴甲",
    "pressonnails": "穿戴甲",
    "jacket": "外套",
    "jackets": "外套",
    "coat": "外套",
    "coats": "外套",
    "outerwear": "外套",
    "hat": "帽子",
    "hats": "帽子",
    "cap": "帽子",
    "caps": "帽子",
    "beanie": "帽子",
    "beanies": "帽子",
    "storage": "家居收纳",
    "organizer": "家居收纳",
    "organizers": "家居收纳",
    "organization": "家居收纳",
    "organize": "家居收纳",
    "organising": "家居收纳",
    "organizing": "家居收纳",
    "sunblock": "防晒霜推荐",
    "spf": "防晒霜推荐",
    "sunscreenrecommendations": "防晒霜推荐",
    "sunscreen": "防晒霜推荐",
    "shampoo": "洗发水推荐",
    "haircare": "洗发水推荐",
    "shampoorecommendations": "洗发水推荐",
    "hairdye": "染发发色推荐",
    "haircolor": "染发发色推荐",
    "haircolour": "染发发色推荐",
    "zhuyu": "逐玉",
}

TOPIC_MATCH_RULES = {
    "拼豆": {
        "phrases": ["perler bead", "perler beads", "fuse bead", "fuse beads", "pindou"],
        "keyword_groups": [["perler", "fuse", "pindou"], ["bead", "beads"]],
    },
    "手机壳": {
        "phrases": [
            "phone accessory",
            "phone accessories",
            "mobile accessories",
            "iphone case",
            "iphone cases",
            "phone cover",
            "phone covers",
            "mobile phone case",
            "smartphone case",
            "phone shell",
        ],
        "keyword_groups": [
            ["phone", "mobile", "smartphone", "iphone", "cellphone"],
            ["case", "cover", "shell", "protector", "accessory"],
        ],
    },
    "蛋糕": {
        "phrases": [
            "cake ideas",
            "cake market",
            "dessert ideas",
            "bakery ideas",
            "sweet treats",
        ],
        "keyword_groups": [["cake", "dessert", "pastry", "bakery", "sweet"]],
    },
    "生日蛋糕": {
        "phrases": ["birthday cake", "birthday cakes", "celebration cake", "party cake"],
        "keyword_groups": [["birthday", "party", "celebration"], ["cake", "dessert"]],
        "require_all_groups": True,
    },
    "圣诞蛋糕": {
        "phrases": ["christmas cake", "holiday cake", "festive cake"],
        "keyword_groups": [["christmas", "holiday", "festive"], ["cake", "dessert"]],
        "require_all_groups": True,
    },
    "穿搭": {
        "phrases": ["outfit ideas", "fashion styling", "what to wear", "style inspo", "look ideas"],
        "keyword_groups": [["outfit", "style", "fashion", "wardrobe", "look", "wear"]],
    },
    "穿搭风格": {
        "phrases": ["outfit styling", "style direction", "personal style", "fashion style", "style vibe"],
        "keyword_groups": [["style", "styling", "fashion"], ["direction", "personal", "aesthetic", "vibe"]],
        "require_all_groups": True,
    },
    "春季穿搭": {
        "phrases": [
            "spring outfit",
            "spring outfits",
            "spring fashion",
            "spring styling",
            "what to wear in spring",
            "spring look ideas",
        ],
        "keyword_groups": [["spring"], ["outfit", "style", "fashion", "look", "wear"]],
        "require_all_groups": True,
    },
    "小个子穿搭春天": {
        "phrases": [
            "petite spring outfit",
            "petite spring outfits",
            "spring outfit for petites",
            "short girl spring outfit",
            "what to wear in spring for short girls",
            "spring looks for short girls",
            "spring outfit for short girls",
        ],
        "keyword_groups": [["petite", "short", "smallframe"], ["spring"], ["outfit", "style", "fashion", "look", "wear"]],
        "require_all_groups": True,
    },
    "高跟鞋穿搭冬季": {
        "phrases": ["winter heels outfit", "winter high heels outfit", "heels styling for winter"],
        "keyword_groups": [["winter"], ["heel", "heels", "highheel"], ["outfit", "style", "fashion"]],
        "require_all_groups": True,
    },
    "花束": {
        "phrases": ["flower bouquet", "bouquet ideas", "floral arrangement", "flower gift"],
        "keyword_groups": [["flower", "flowers", "bouquet", "floral", "blossom"]],
    },
    "穿戴甲": {
        "phrases": ["press on nails", "press-on nails", "fake nails", "glue on nails", "nail set"],
        "keyword_groups": [["presson", "press", "fake", "glueon"], ["nail", "nails", "manicure"]],
    },
    "防晒霜推荐": {
        "phrases": ["best sunscreen", "sunscreen recommendation", "sun protection", "spf product"],
        "keyword_groups": [["sunscreen", "sunblock", "spf", "uv"], ["protect", "protection", "recommendation"]],
    },
    "洗发水推荐": {
        "phrases": ["best shampoo", "shampoo recommendation", "hair wash", "scalp shampoo"],
        "keyword_groups": [["shampoo", "hairwash", "hair", "scalp"], ["recommendation", "care", "wash"]],
    },
    "染发发色推荐": {
        "phrases": ["hair color ideas", "hair dye color", "hair color recommendation"],
        "keyword_groups": [["hair", "dye", "dyed"], ["color", "colour", "shade"]],
    },
    "染发颜色推荐2026": {
        "phrases": ["2026 hair color", "hair color trend 2026", "2026 hair dye ideas"],
        "keyword_groups": [["2026", "trend"], ["hair", "dye"], ["color", "colour", "shade"]],
    },
    "家居收纳": {
        "phrases": ["home organization", "home storage", "storage ideas", "declutter home"],
        "keyword_groups": [["home", "household", "room"], ["storage", "organizer", "organize", "organization", "declutter"]],
    },
    "外套": {
        "phrases": ["jacket styling", "coat outfit", "outerwear ideas"],
        "keyword_groups": [["coat", "jacket", "outerwear"]],
    },
    "帽子": {
        "phrases": ["hat styling", "cap outfit", "headwear ideas"],
        "keyword_groups": [["hat", "cap", "headwear", "beanie"]],
    },
    "情人节喝什么奶茶": {
        "phrases": ["valentine milk tea", "valentine drink", "date drink", "boba for valentine"],
        "keyword_groups": [["valentine", "date", "romantic"], ["milktea", "boba", "drink", "tea"]],
        "require_all_groups": True,
    },
    "过年买什么年货": {
        "phrases": ["lunar new year gifts", "new year shopping", "holiday essentials", "festival groceries"],
        "keyword_groups": [["newyear", "lunar", "festival", "holiday"], ["gift", "shopping", "essential", "groceries"]],
        "require_all_groups": True,
    },
    "大疆pocket3": {
        "phrases": ["dji pocket 3", "osmo pocket 3", "pocket camera"],
        "keyword_groups": [["dji", "osmo", "pocket3", "camera"]],
    },
    "stanley杯子为什么这么火": {
        "phrases": ["stanley cup", "stanley tumbler", "stanley mug"],
        "keyword_groups": [["stanley"], ["cup", "tumbler", "mug"]],
    },
    "圣诞帽": {
        "phrases": ["christmas hat", "santa hat", "holiday hat"],
        "keyword_groups": [["christmas", "santa", "holiday"], ["hat", "cap"]],
    },
    "儿童小短指甲": {
        "phrases": ["kids nails", "children nails", "short nails for kids"],
        "keyword_groups": [["kid", "kids", "child", "children"], ["nail", "nails", "short"]],
    },
}

TOPIC_EN_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "for",
    "to",
    "of",
    "in",
    "on",
    "at",
    "by",
    "with",
    "from",
    "i",
    "me",
    "my",
    "you",
    "your",
    "we",
    "our",
    "they",
    "their",
    "is",
    "are",
    "be",
    "do",
    "does",
    "did",
    "what",
    "which",
    "how",
    "should",
    "would",
    "could",
    "can",
    "want",
    "need",
    "know",
    "about",
    "current",
    "market",
    "idea",
    "ideas",
    "product",
    "products",
    "sell",
    "selling",
    "lover",
    "lovers",
}


def normalize_topic_key(value: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", str(value or "").strip().lower())


def normalize_topic_token(value: str) -> str:
    token = str(value or "").strip().lower()
    normalized = normalize_topic_key(token)
    if not normalized or re.search(r"[\u4e00-\u9fff]", normalized):
        return normalized

    if normalized.endswith("ies") and len(normalized) > 4:
        return normalized[:-3] + "y"
    if normalized.endswith("es") and len(normalized) > 4:
        return normalized[:-2]
    if normalized.endswith("s") and len(normalized) > 3:
        return normalized[:-1]
    return normalized


@lru_cache(maxsize=1)
def keyword_topic_directories() -> tuple[str, ...]:
    dirs = []
    if not KEYWORD_TOPIC_DIR.exists():
        return tuple(dirs)
    for path in KEYWORD_TOPIC_DIR.iterdir():
        if not path.is_dir():
            continue
        contents = path / "search_contents_2026-04-20.csv"
        comments = path / "search_comments_2026-04-20.csv"
        if contents.exists() and comments.exists():
            dirs.append(path.name)
    return tuple(sorted(dirs))


@lru_cache(maxsize=1)
def keyword_topic_flat_csv_topics() -> tuple[str, ...]:
    topics = []
    if not KEYWORD_TOPIC_DIR.exists():
        return tuple(topics)
    for path in KEYWORD_TOPIC_DIR.glob("*.csv"):
        if path.name == "关键词.csv":
            continue
        topics.append(path.stem)
    return tuple(sorted(topics))


@lru_cache(maxsize=1)
def weekly_run_topic_names() -> tuple[str, ...]:
    topics = set()
    for week in list_weeks():
        week_name = str(week.get("week") or "").strip()
        if not week_name:
            continue
        try:
            for item in list_topics(week_name):
                topic_name = str(item.get("topic") or "").strip()
                if topic_name:
                    topics.add(topic_name)
        except FileNotFoundError:
            continue
    return tuple(sorted(topics))


def keyword_topic_available_topics() -> tuple[str, ...]:
    return tuple(sorted(set(keyword_topic_directories()) | set(keyword_topic_flat_csv_topics())))


def keyword_topic_alias_map() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for topic in keyword_topic_available_topics():
        aliases[normalize_topic_key(topic)] = topic
    for topic in weekly_run_topic_names():
        normalized_topic = normalize_topic_key(topic)
        if normalized_topic:
            aliases[normalized_topic] = topic
    for alias_key, alias_topic in TOPIC_ALIASES.items():
        normalized_key = normalize_topic_key(alias_key)
        if normalized_key:
            aliases[normalized_key] = alias_topic
    return aliases


def keyword_topic_keywords() -> dict[str, set[str]]:
    keywords: dict[str, set[str]] = defaultdict(set)
    for topic in keyword_topic_available_topics():
        normalized_topic = normalize_topic_key(topic)
        if normalized_topic:
            keywords[topic].add(normalized_topic)
        keywords[topic].update(tokenize_topic_text(topic))
    for topic in weekly_run_topic_names():
        normalized_topic = normalize_topic_key(topic)
        if normalized_topic:
            keywords[topic].add(normalized_topic)
        keywords[topic].update(tokenize_topic_text(topic))

    for alias_key, alias_topic in TOPIC_ALIASES.items():
        normalized_key = normalize_topic_token(alias_key)
        if normalized_key:
            keywords[alias_topic].add(normalized_key)

    for topic_name, rule in TOPIC_MATCH_RULES.items():
        for phrase in rule.get("phrases", []):
            normalized_phrase = normalize_topic_key(phrase)
            if normalized_phrase:
                keywords[topic_name].add(normalized_phrase)
            keywords[topic_name].update(tokenize_topic_text(phrase))
        for group in rule.get("keyword_groups", []):
            keywords[topic_name].update(normalize_topic_token(keyword) for keyword in group if normalize_topic_token(keyword))

    return keywords


def tokenize_topic_text(value: str | None) -> set[str]:
    text = str(value or "").lower()
    tokens = set()
    for token in re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", text):
        normalized = normalize_topic_token(token)
        if normalized and normalized not in TOPIC_EN_STOPWORDS:
            tokens.add(normalized)
    normalized_text = normalize_topic_key(text)
    if normalized_text:
        tokens.add(normalized_text)
    return tokens


def score_topic_rule(candidate_key: str, candidate_tokens: set[str], topic_name: str) -> int:
    rule = TOPIC_MATCH_RULES.get(topic_name) or {}
    score = 0
    phrase_matched = False

    for phrase in rule.get("phrases", []):
        normalized_phrase = normalize_topic_key(phrase)
        if not normalized_phrase:
            continue
        if candidate_key == normalized_phrase:
            return 120
        if normalized_phrase in candidate_key:
            phrase_matched = True
            score = max(score, 95)

    matched_groups = 0
    for group in rule.get("keyword_groups", []):
        normalized_group = {normalize_topic_token(keyword) for keyword in group if normalize_topic_token(keyword)}
        if not normalized_group:
            continue
        if candidate_tokens & normalized_group:
            matched_groups += 1
            score += 25

    if matched_groups and matched_groups == len(rule.get("keyword_groups", [])):
        score += 20

    if rule.get("require_all_groups") and not phrase_matched:
        required = len(rule.get("keyword_groups", []))
        if required and matched_groups < required:
            return 0

    return score


def fuzzy_match_keyword_topic_name(candidate: str | None) -> str | None:
    candidate_text = str(candidate or "").strip().lower()
    candidate_key = normalize_topic_key(candidate_text)
    if not candidate_key:
        return None

    topic_keywords = keyword_topic_keywords()
    candidate_tokens = tokenize_topic_text(candidate_text)
    best_topic = None
    best_score = 0

    for topic_name, keywords in topic_keywords.items():
        score = score_topic_rule(candidate_key, candidate_tokens, topic_name)
        rule = TOPIC_MATCH_RULES.get(topic_name) or {}
        if rule.get("require_all_groups") and score == 0:
            continue
        for keyword in keywords:
            if not keyword:
                continue
            if candidate_key == keyword:
                return topic_name
            if len(keyword) >= 4 and keyword in candidate_key:
                score = max(score, 70 + min(len(keyword), 20))
            if keyword in candidate_tokens:
                score = max(score, 60 + min(len(keyword), 20))

        overlap = len(candidate_tokens & keywords)
        score += overlap * 10

        if score > best_score:
            best_topic = topic_name
            best_score = score

    return best_topic if best_score >= 60 else None


def resolve_keyword_topic_name(topic: str | None, question: str | None = None) -> str | None:
    aliases = keyword_topic_alias_map()
    candidates = [topic or "", question or ""]
    for candidate in candidates:
        normalized = normalize_topic_key(candidate)
        if not normalized:
            continue
        if normalized in aliases:
            return aliases[normalized]

        for token in tokenize_topic_text(candidate):
            if token in aliases:
                return aliases[token]

        fuzzy_match = fuzzy_match_keyword_topic_name(candidate)
        if fuzzy_match:
            return fuzzy_match

        for alias_key, alias_topic in aliases.items():
            if alias_key and len(alias_key) >= 4 and alias_key in normalized:
                return alias_topic

    for candidate in candidates:
        text = str(candidate or "").lower()
        for topic_name in keyword_topic_available_topics():
            if topic_name.lower() in text:
                return topic_name
        for topic_name in weekly_run_topic_names():
            if topic_name.lower() in text:
                return topic_name
    return None


def read_selected_keyword_topics() -> list[dict]:
    path = KEYWORD_TOPIC_DIR / "关键词.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            week = str(row.get("week") or "").strip()
            for key, value in row.items():
                if key == "week":
                    continue
                topic = str(value or "").strip()
                if topic:
                    rows.append({"week": week, "topic": topic})
        return rows


def keyword_topic_status_report() -> dict:
    selected_rows = read_selected_keyword_topics()
    available_topics = set(keyword_topic_available_topics())
    available_rows = [row for row in selected_rows if row["topic"] in available_topics]
    missing_rows = [row for row in selected_rows if row["topic"] not in available_topics]
    return {
        "available_unique_topics": sorted(available_topics),
        "available_selected_rows": available_rows,
        "missing_selected_rows": missing_rows,
        "missing_unique_topics": sorted({row["topic"] for row in missing_rows}),
    }


def _topic_dir(topic: str) -> Path:
    path = KEYWORD_TOPIC_DIR / topic
    if not path.exists():
        raise FileNotFoundError(f"Detailed keyword topic data not found for topic {topic}")
    return path


def _contents_path(topic: str) -> Path:
    path = _topic_dir(topic) / "search_contents_2026-04-20.csv"
    if not path.exists():
        raise FileNotFoundError(f"Post content CSV not found for topic {topic}")
    return path


def _comments_path(topic: str) -> Path:
    path = _topic_dir(topic) / "search_comments_2026-04-20.csv"
    if not path.exists():
        raise FileNotFoundError(f"Comment CSV not found for topic {topic}")
    return path


def _flat_topic_csv_path(topic: str) -> Path:
    path = KEYWORD_TOPIC_DIR / f"{topic}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Flat keyword topic CSV not found for topic {topic}")
    return path


def _has_structured_topic_files(topic: str) -> bool:
    path = KEYWORD_TOPIC_DIR / topic
    if not path.is_dir():
        return False
    return (path / "search_contents_2026-04-20.csv").exists() and (path / "search_comments_2026-04-20.csv").exists()


def _has_flat_topic_csv(topic: str) -> bool:
    path = KEYWORD_TOPIC_DIR / f"{topic}.csv"
    return path.exists() and path.is_file()


def _parse_flat_top_comments(value: str | None) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    return [item.strip() for item in text.split("||") if item.strip()]


def _parse_flat_topic_posts(topic: str) -> list[dict]:
    posts = []
    with _flat_topic_csv_path(topic).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = str(row.get("note_title") or row.get("search_title") or row.get("title") or "").strip()
            desc = str(row.get("note_desc") or row.get("desc") or "").strip()
            tags = str(row.get("note_tags") or row.get("tag_list") or "").strip().replace("|", ",")
            top_comments = _parse_flat_top_comments(row.get("top_comments"))
            text = " ".join([title, desc, tags, " ".join(top_comments)])
            posts.append(
                {
                    "note_id": str(row.get("note_url") or row.get("note_id") or title).strip(),
                    "title": title,
                    "desc": desc,
                    "tags": tags,
                    "author": str(row.get("note_author") or row.get("search_author") or row.get("nickname") or "").replace(" 关注", "").strip(),
                    "likes": safe_int(row.get("note_like_count") or row.get("liked_count") or row.get("search_like_count")),
                    "collects": safe_int(row.get("note_collect_count") or row.get("collected_count")),
                    "comments": safe_int(row.get("note_comment_count") or row.get("comment_count")),
                    "shares": safe_int(row.get("share_count")),
                    "engagement_score": (
                        safe_int(row.get("note_like_count") or row.get("liked_count") or row.get("search_like_count"))
                        + safe_int(row.get("note_collect_count") or row.get("collected_count")) * 1.8
                        + safe_int(row.get("note_comment_count") or row.get("comment_count")) * 3.0
                    ),
                    "themes": detect_themes(text),
                    "top_comments": top_comments[:5],
                    "comment_samples": [{"content": item, "likes": 0, "nickname": ""} for item in top_comments[:8]],
                    "source_keyword": str(row.get("source_keyword") or topic).strip(),
                    "note_url": str(row.get("note_url") or row.get("search_href") or "").strip(),
                }
            )
    return posts


def read_keyword_topic_posts(topic: str) -> list[dict]:
    if _has_flat_topic_csv(topic):
        return _parse_flat_topic_posts(topic)

    comments_by_note = _read_comments_grouped(topic)
    posts = []
    with _contents_path(topic).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            note_id = str(row.get("note_id") or "").strip()
            title = str(row.get("title") or "").strip()
            desc = str(row.get("desc") or "").strip()
            tags = str(row.get("tag_list") or "").strip()
            comments = comments_by_note.get(note_id, [])
            top_comments = [item["content"] for item in comments[:5] if item["content"]]
            text = " ".join([title, desc, tags, " ".join(top_comments)])
            posts.append(
                {
                    "note_id": note_id,
                    "title": title,
                    "desc": desc,
                    "tags": tags,
                    "author": str(row.get("nickname") or "").strip(),
                    "likes": safe_int(row.get("liked_count")),
                    "collects": safe_int(row.get("collected_count")),
                    "comments": safe_int(row.get("comment_count")),
                    "shares": safe_int(row.get("share_count")),
                    "engagement_score": (
                        safe_int(row.get("liked_count"))
                        + safe_int(row.get("collected_count")) * 1.8
                        + safe_int(row.get("comment_count")) * 3.0
                    ),
                    "themes": detect_themes(text),
                    "top_comments": top_comments,
                    "comment_samples": comments[:8],
                    "source_keyword": str(row.get("source_keyword") or "").strip(),
                    "note_url": str(row.get("note_url") or "").strip(),
                }
            )
    return posts


def _read_comments_grouped(topic: str) -> dict[str, list[dict]]:
    if not _has_structured_topic_files(topic):
        return {}
    grouped: dict[str, list[dict]] = defaultdict(list)
    with _comments_path(topic).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            note_id = str(row.get("note_id") or "").strip()
            grouped[note_id].append(
                {
                    "content": str(row.get("content") or "").strip(),
                    "likes": safe_int(row.get("like_count")),
                    "nickname": str(row.get("nickname") or "").strip(),
                }
            )
    for note_id, items in grouped.items():
        grouped[note_id] = sorted(items, key=lambda item: item["likes"], reverse=True)
    return grouped


def detect_themes(text: str) -> list[str]:
    hits = []
    lowered = text.lower()
    for theme, keywords in THEME_RULES.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            hits.append(theme)
    return hits or ["其他"]


def local_heuristic_summary(posts: list[dict]) -> dict:
    theme_counter = Counter()
    tag_counter = Counter()
    demand_signals = defaultdict(list)
    phrase_counter = Counter()

    for post in posts:
        for theme in post["themes"]:
            theme_counter[theme] += 1
        for tag in str(post["tags"]).split(","):
            tag = tag.strip()
            if tag:
                tag_counter[tag] += 1

        text = " ".join(
            [
                post["title"],
                post["desc"],
                " ".join(post["top_comments"]),
            ]
        )
        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text.lower())
        for token in normalized.split():
            if len(token) >= 2 and not token.isdigit():
                phrase_counter[token] += 1

        if any(keyword in text for keyword in ["教程", "攻略", "推荐", "怎么", "步骤", "新手"]):
            demand_signals["学习与决策"].append(post["title"])
        if any(keyword in text for keyword in ["开箱", "分享", "展示", "合集", "实拍"]):
            demand_signals["内容种草"].append(post["title"])
        if any(keyword in text for keyword in ["价格", "折扣", "平替", "必买", "值得买", "优惠"]):
            demand_signals["价格敏感"].append(post["title"])
        if any(keyword in text for keyword in ["礼物", "生日", "情侣", "送人", "伴手礼"]):
            demand_signals["送礼场景"].append(post["title"])
        if any(keyword in text for keyword in ["收纳", "便携", "防晒", "防水", "清洁", "解决"]):
            demand_signals["功能诉求"].append(post["title"])

    return {
        "theme_top": theme_counter.most_common(8),
        "tag_top": tag_counter.most_common(20),
        "keyword_top": phrase_counter.most_common(30),
        "demand_buckets": {key: value[:8] for key, value in demand_signals.items()},
    }


def summarize_keyword_topic_posts(topic: str) -> dict:
    posts = read_keyword_topic_posts(topic)
    like_values = [post["likes"] for post in posts]
    collect_values = [post["collects"] for post in posts]
    comment_values = [post["comments"] for post in posts]
    tag_counter = Counter()
    for post in posts:
        for tag in str(post["tags"]).split(","):
            cleaned = tag.strip()
            if cleaned:
                tag_counter[cleaned] += 1
    return {
        "topic": topic,
        "post_count": len(posts),
        "avg_like": round(sum(like_values) / len(like_values), 2) if posts else 0,
        "avg_collect": round(sum(collect_values) / len(collect_values), 2) if posts else 0,
        "avg_comment": round(sum(comment_values) / len(comment_values), 2) if posts else 0,
        "top_tags": tag_counter.most_common(12),
    }


def compact_posts_for_prompt(posts: list[dict], top_n: int = 20) -> list[dict]:
    ranked = sorted(posts, key=lambda item: item["engagement_score"], reverse=True)[:top_n]
    compact = []
    for index, post in enumerate(ranked, start=1):
        compact.append(
            {
                "rank": index,
                "title": post["title"],
                "desc": post["desc"][:360],
                "tags": post["tags"],
                "likes": post["likes"],
                "collects": post["collects"],
                "comments": post["comments"],
                "themes": post["themes"],
                "top_comments": [
                    {"content": item["content"][:120], "likes": item["likes"]}
                    for item in post["comment_samples"][:5]
                    if item["content"]
                ],
            }
        )
    return compact
