"""Helpers for loading and normalizing topic data from JSON."""

from __future__ import annotations

import json
from functools import lru_cache

from utils.constants import LEVEL_ORDER, TOPICS_FILE


def _safe_float(value: object, default: float = 1.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_topic(raw_topic, domain=None, level=None):
    return {
        "id": str(raw_topic.get("id", "")).strip(),
        "topic": str(raw_topic.get("topic", "")).strip(),
        "description": str(raw_topic.get("description", "")).strip(),
        "duration": _safe_float(raw_topic.get("duration", raw_topic.get("estimated_hours", 1.0))),
        "category": str(raw_topic.get("category", "General")).strip() or "General",
        "level": str(raw_topic.get("level", level or "Beginner")).strip() or "Beginner",
        "domain": str(raw_topic.get("domain", domain or "General")).strip() or "General",
        "prerequisites": list(dict.fromkeys(raw_topic.get("prerequisites", []) or [])),
        "age_group": str(raw_topic.get("age_group", raw_topic.get("age_group_target", "All"))).strip() or "All",
    }


def _flatten_nested_topics(raw_data):
    topics = []
    for domain, levels in raw_data.items():
        if not isinstance(levels, dict):
            continue
        for level, level_topics in levels.items():
            if not isinstance(level_topics, list):
                continue
            for topic in level_topics:
                if isinstance(topic, dict):
                    topics.append(_normalize_topic(topic, domain=domain, level=level))
    return topics


@lru_cache(maxsize=1)
def load_topics_from_json():
    if not TOPICS_FILE.exists():
        return []
    with TOPICS_FILE.open("r", encoding="utf-8") as handle:
        raw_data = json.load(handle)
    if isinstance(raw_data, list):
        topics = [_normalize_topic(topic) for topic in raw_data if isinstance(topic, dict)]
    else:
        topics = _flatten_nested_topics(raw_data)
    return [topic for topic in topics if topic["id"] and topic["topic"]]


def build_topic_index(topics):
    return {topic["id"]: topic for topic in topics}


def get_topics_for_domain(topics, domain, skill_level):
    max_level = LEVEL_ORDER.get(skill_level, 0)
    return [topic for topic in topics if topic["domain"] == domain and LEVEL_ORDER.get(topic["level"], 0) <= max_level]


def get_dataset_summary(topics):
    return {
        "total_topics": len(topics),
        "domains": sorted({topic["domain"] for topic in topics}),
        "categories": sorted({topic["category"] for topic in topics}),
    }
