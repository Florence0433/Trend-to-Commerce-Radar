from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.config import GENERATION_API_KEY, GENERATION_API_URL, GENERATION_MODEL
from backend.app.services.generation_service import call_chat_completion, extract_content_from_response, parse_json_content
from backend.app.services.keyword_topic_service import compact_posts_for_prompt, keyword_topic_available_topics, read_keyword_topic_posts
from backend.app.services.merch_analysis_service import build_local_analysis_payload, write_cached_analysis


def build_prompt(topic: str) -> str:
    posts = read_keyword_topic_posts(topic)
    compact_posts = compact_posts_for_prompt(posts, top_n=18)
    payload = {
        "task": "Generate cached merchandising analysis for a trend-to-commerce dashboard.",
        "topic": topic,
        "source": "Xiaohongshu post and comment samples",
        "language_requirement": "Return bilingual zh/en fields where the schema asks for them. Product suggestions may be Chinese because the source data is Chinese.",
        "output_schema": {
            "title": {"zh": topic, "en": "English topic name"},
            "subtitle": {"zh": "short Chinese subtitle", "en": "short English subtitle"},
            "summary": {"zh": "2-sentence Chinese topic analysis", "en": "2-sentence English topic analysis"},
            "forecast": {"zh": "+short signal", "en": "+short signal"},
            "keywords": [{"emoji": "emoji", "label": {"zh": "keyword", "en": "keyword"}}],
            "quote": {"zh": "insight quote", "en": "insight quote"},
            "suggestions": [
                {
                    "product_name": "specific product direction",
                    "category": "category",
                    "target_users": ["user group"],
                    "use_scenarios": ["scenario"],
                    "why_recommended": "why this product direction fits the evidence",
                    "evidence": ["specific post/comment evidence"],
                    "selling_points": ["selling point"],
                    "pricing_hint": "price band",
                    "risk_note": "risk",
                }
            ],
            "strategy": {"zh": "execution strategy", "en": "execution strategy"},
        },
        "rules": [
            "Use concrete evidence from the supplied posts/comments.",
            "Create exactly 3 specific product suggestions.",
            "Do not mention AI, model generation, local datasets, sample counts, cached files, or backend processing in any user-visible field.",
            "Write the output as polished customer-facing product content, not as a technical data report.",
            "Avoid generic advice.",
            "Output valid JSON only.",
        ],
        "top_posts": compact_posts,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def generate_remote_analysis(topic: str) -> dict:
    if not (GENERATION_API_URL and GENERATION_API_KEY and GENERATION_MODEL):
        raise RuntimeError("Remote model is not configured. Set GENERATION_API_URL, GENERATION_API_KEY, and GENERATION_MODEL.")
    body = call_chat_completion(
        [
            {
                "role": "system",
                "content": "You are a senior e-commerce merchandising analyst. Return valid JSON only.",
            },
            {"role": "user", "content": build_prompt(topic)},
        ],
        temperature=0.25,
    )
    parsed = parse_json_content(extract_content_from_response(body))
    parsed["generation_source"] = "remote_model"
    parsed["model"] = GENERATION_MODEL
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", action="append", help="Generate one topic. Can be repeated. Defaults to all available topics.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of topics for testing.")
    parser.add_argument("--allow-local-fallback", action="store_true", help="Write deterministic local analysis if remote model is unavailable.")
    args = parser.parse_args()

    topics = args.topic or list(keyword_topic_available_topics())
    if args.limit:
        topics = topics[: args.limit]

    failures = []
    for topic in topics:
        try:
            payload = generate_remote_analysis(topic)
        except Exception as exc:
            if not args.allow_local_fallback:
                failures.append((topic, str(exc)))
                print(f"FAILED {topic}: {exc}")
                continue
            payload = build_local_analysis_payload(topic)
            payload["generation_source"] = "local_fallback"
            payload["remote_error"] = str(exc)
        path = write_cached_analysis(topic, payload)
        print(f"WROTE {topic}: {path}")

    if failures:
        print(f"{len(failures)} topic(s) failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
