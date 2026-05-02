"""JSON-backed persistence for user profiles, plans, and progress."""

from __future__ import annotations

import datetime as dt
import hashlib
import json

from utils.constants import USERS_FILE


def generate_user_id(name: str, age: int) -> str:
    raw = f"{name.strip().lower()}|{int(age)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_user_store():
    if not USERS_FILE.exists():
        return {}
    with USERS_FILE.open("r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError:
            return {}
    return data if isinstance(data, dict) else {}


def save_user_store(store):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USERS_FILE.open("w", encoding="utf-8") as handle:
        json.dump(store, handle, indent=2)


def _topic_name_lookup(topic_index):
    return {str(topic["topic"]).lower(): topic_id for topic_id, topic in topic_index.items()}


def _normalize_record(user_id, raw_record, topic_index):
    profile = raw_record.get("profile", {}) if isinstance(raw_record.get("profile"), dict) else {}
    completed_ids = list(dict.fromkeys(raw_record.get("completed_topic_ids", []) or []))
    if not completed_ids and raw_record.get("completed"):
        topic_lookup = _topic_name_lookup(topic_index)
        completed_ids = [
            topic_lookup[name.lower()]
            for name in raw_record.get("completed", [])
            if isinstance(name, str) and name.lower() in topic_lookup
        ]

    normalized_profile = {
        "name": profile.get("name") or raw_record.get("display_name", "Learner"),
        "age": int(profile.get("age", raw_record.get("age", 18))),
        "domain": profile.get("domain") or raw_record.get("domain", "Education"),
        "goal": profile.get("goal") or raw_record.get("goal", ""),
        "skill_level": profile.get("skill_level") or raw_record.get("skill", "Beginner"),
        "hours_per_day": float(profile.get("hours_per_day", raw_record.get("hours", 1.0))),
        "health_condition": profile.get("health_condition") or raw_record.get("health", ""),
    }

    latest_plan = raw_record.get("latest_plan") if isinstance(raw_record.get("latest_plan"), dict) else {}
    created_at = raw_record.get("created_at") or raw_record.get("last_seen") or dt.datetime.now().isoformat()
    updated_at = raw_record.get("updated_at") or raw_record.get("last_seen") or created_at

    return {
        "user_id": user_id,
        "display_name": normalized_profile["name"],
        "profile": normalized_profile,
        "completed_topic_ids": completed_ids,
        "badges": list(raw_record.get("badges", [])),
        "sessions": int(raw_record.get("sessions", 0)),
        "created_at": created_at,
        "updated_at": updated_at,
        "latest_plan": latest_plan,
    }


def _storage_shape(record, topic_index):
    profile = record["profile"]
    completed_names = [topic_index[topic_id]["topic"] for topic_id in record["completed_topic_ids"] if topic_id in topic_index]
    return {
        "display_name": profile["name"],
        "age": profile["age"],
        "domain": profile["domain"],
        "goal": profile["goal"],
        "skill": profile["skill_level"],
        "hours": profile["hours_per_day"],
        "health": profile["health_condition"],
        "profile": profile,
        "completed": completed_names,
        "completed_topic_ids": record["completed_topic_ids"],
        "badges": record["badges"],
        "sessions": record["sessions"],
        "created_at": record["created_at"],
        "updated_at": record["updated_at"],
        "last_seen": record["updated_at"],
        "latest_plan": record.get("latest_plan", {}),
    }


def calculate_badges(completed_count):
    badges = []
    if completed_count >= 1:
        badges.append("Started Strong")
    if completed_count >= 5:
        badges.append("Momentum Builder")
    if completed_count >= 10:
        badges.append("Consistency Star")
    if completed_count >= 20:
        badges.append("Roadmap Finisher")
    return badges


def get_user_record(user_id, topic_index):
    raw_record = load_user_store().get(user_id)
    if not isinstance(raw_record, dict):
        return None
    return _normalize_record(user_id, raw_record, topic_index)


def get_latest_user_record(topic_index):
    store = load_user_store()
    if not store:
        return None
    user_id, raw_record = sorted(store.items(), key=lambda item: str(item[1].get("updated_at") or item[1].get("last_seen") or ""), reverse=True)[0]
    return _normalize_record(user_id, raw_record, topic_index)


def list_user_records(topic_index):
    store = load_user_store()
    records = [_normalize_record(user_id, raw_record, topic_index) for user_id, raw_record in store.items() if isinstance(raw_record, dict)]
    return sorted(records, key=lambda record: record["updated_at"], reverse=True)


def upsert_user_record(profile, plan, topic_index):
    store = load_user_store()
    user_id = generate_user_id(str(profile["name"]), int(profile["age"]))
    existing = _normalize_record(user_id, store.get(user_id, {}), topic_index)
    now = dt.datetime.now().isoformat()
    record = {
        "user_id": user_id,
        "display_name": str(profile["name"]),
        "profile": profile,
        "completed_topic_ids": existing.get("completed_topic_ids", []),
        "badges": calculate_badges(len(existing.get("completed_topic_ids", []))),
        "sessions": int(existing.get("sessions", 0)) + 1,
        "created_at": existing.get("created_at", now),
        "updated_at": now,
        "latest_plan": plan,
    }
    store[user_id] = _storage_shape(record, topic_index)
    save_user_store(store)
    return record


def update_topic_completion(user_id, topic_id, completed, topic_index):
    store = load_user_store()
    raw_record = store.get(user_id)
    if not isinstance(raw_record, dict):
        return None
    record = _normalize_record(user_id, raw_record, topic_index)
    completed_ids = set(record["completed_topic_ids"])
    if completed:
        completed_ids.add(topic_id)
    else:
        completed_ids.discard(topic_id)
    record["completed_topic_ids"] = sorted(completed_ids)
    record["badges"] = calculate_badges(len(record["completed_topic_ids"]))
    record["updated_at"] = dt.datetime.now().isoformat()
    store[user_id] = _storage_shape(record, topic_index)
    save_user_store(store)
    return record
