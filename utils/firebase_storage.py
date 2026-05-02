"""Firestore-backed storage for user profiles, progress, and roadmaps."""

import datetime
from firebase_config import db, admin_auth


def _iso_now():
    return datetime.datetime.now().isoformat()


def _build_roadmap_entry(plan, profile_data=None, created_at=None):
    """Create a stored roadmap entry with metadata for history views."""
    created_at = created_at or _iso_now()
    profile_data = profile_data or {}
    roadmap = plan.get("roadmap", []) if isinstance(plan, dict) else []
    primary_topic = roadmap[0]["topic"] if roadmap else ""
    return {
        "roadmap_id": f"{created_at}_{plan.get('domain', 'General')}_{primary_topic[:24]}",
        "created_at": created_at,
        "domain": plan.get("domain", profile_data.get("domain", "")),
        "goal": profile_data.get("goal", ""),
        "name": profile_data.get("name", "Learner"),
        "skill_level": profile_data.get("skill_level", "Beginner"),
        "hours_per_day": profile_data.get("hours_per_day", 1.5),
        "health_condition": profile_data.get("health_condition", ""),
        "roadmap": roadmap,
        "cid": plan.get("cid"),
        "cinfo": plan.get("cinfo", {}),
        "related": plan.get("related", []),
        "total_h": plan.get("total_h", 0),
        "total_w": plan.get("total_w", 0),
        "total_t": plan.get("total_t", len(roadmap)),
        "goal_category": plan.get("goal_category"),
    }


def _normalize_roadmap_entry(entry):
    """Normalize old and new roadmap formats into one consistent shape."""
    if not isinstance(entry, dict):
        return None

    created_at = entry.get("created_at") or _iso_now()
    roadmap = entry.get("roadmap", []) if isinstance(entry.get("roadmap", []), list) else []
    primary_topic = roadmap[0]["topic"] if roadmap else ""
    domain = entry.get("domain", "General")

    normalized = dict(entry)
    normalized.setdefault("roadmap_id", f"{created_at}_{domain}_{primary_topic[:24]}")
    normalized.setdefault("goal", entry.get("profile", {}).get("goal", ""))
    normalized.setdefault("name", entry.get("profile", {}).get("name", "Learner"))
    normalized.setdefault("skill_level", entry.get("profile", {}).get("skill_level", "Beginner"))
    normalized.setdefault("hours_per_day", entry.get("profile", {}).get("hours_per_day", 1.5))
    normalized.setdefault("health_condition", entry.get("profile", {}).get("health_condition", ""))
    normalized.setdefault("cinfo", entry.get("cinfo", {}))
    normalized.setdefault("related", entry.get("related", []))
    normalized.setdefault("total_t", entry.get("total_t", len(roadmap)))
    normalized.setdefault("total_h", entry.get("total_h", sum(t.get("duration", 0) for t in roadmap)))
    normalized.setdefault("total_w", entry.get("total_w", max((t.get("week", 0) for t in roadmap), default=0)))
    normalized["created_at"] = created_at
    normalized["domain"] = domain
    normalized["roadmap"] = roadmap
    return normalized


# ══════════════════════════════════════════════════════════════
#  USER PROFILE OPERATIONS
# ══════════════════════════════════════════════════════════════

def save_user_profile(uid, profile_data, plan=None):
    """
    Save or update user profile in Firestore.
    Called after signup or when generating a new roadmap.
    """
    doc_ref = db.collection("users").document(uid)
    existing = doc_ref.get()
    
    now = _iso_now()
    
    if existing.exists:
        old_data = existing.to_dict()
        update_data = {
            "profile": profile_data,
            "updated_at": now,
            "sessions": old_data.get("sessions", 0) + 1,
        }
        if plan is not None:
            update_data["latest_plan"] = plan
            existing_roadmaps = [
                r for r in (_normalize_roadmap_entry(item) for item in old_data.get("roadmaps", []))
                if r is not None
            ]
            existing_roadmaps.append(_build_roadmap_entry(plan, profile_data, created_at=now))
            update_data["roadmaps"] = existing_roadmaps
        doc_ref.update(update_data)
    else:
        new_data = {
            "profile": profile_data,
            "completed": [],
            "badges": [],
            "sessions": 1,
            "streak_days": 1,
            "created_at": now,
            "updated_at": now,
            "latest_plan": plan or {},
            "roadmaps": [],
        }
        if plan is not None:
            new_data["roadmaps"] = [_build_roadmap_entry(plan, profile_data, created_at=now)]
        doc_ref.set(new_data)


def get_user_profile(uid):
    """Get user profile from Firestore."""
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None


def get_user_by_uid(uid):
    """
    Get user data in the format compatible with existing engine.py functions.
    Returns dict with 'completed', 'badges', 'sessions', 'streak_days' etc.
    """
    data = get_user_profile(uid)
    if not data:
        return {}
    
    profile = data.get("profile", {})
    return {
        "display_name": profile.get("name", "Learner"),
        "age": profile.get("age", 22),
        "domain": profile.get("domain", "Education"),
        "goal": profile.get("goal", ""),
        "skill": profile.get("skill_level", "Beginner"),
        "hours": profile.get("hours_per_day", 1.5),
        "health": profile.get("health_condition", ""),
        "completed": data.get("completed", []),
        "badges": data.get("badges", []),
        "sessions": data.get("sessions", 0),
        "streak_days": data.get("streak_days", 0),
        "last_seen": data.get("updated_at", ""),
        "latest_plan": data.get("latest_plan", {}),
        "created_at": data.get("created_at", ""),
    }


# ══════════════════════════════════════════════════════════════
#  TOPIC COMPLETION (PROGRESS TRACKING)
# ══════════════════════════════════════════════════════════════

def toggle_topic_firestore(uid, topic_name):
    """Toggle a topic's completion status in Firestore."""
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    
    if not doc.exists:
        return
    
    data = doc.to_dict()
    completed = data.get("completed", [])
    
    if topic_name in completed:
        completed.remove(topic_name)
    else:
        completed.append(topic_name)
    
    # Calculate badges
    badges = _calculate_badges(len(completed))
    
    doc_ref.update({
        "completed": completed,
        "badges": badges,
        "updated_at": datetime.datetime.now().isoformat(),
    })


def clear_user_progress_firestore(uid):
    """Clear completed topics and badges for a user in Firestore."""
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()

    if not doc.exists:
        return False

    doc_ref.update({
        "completed": [],
        "badges": [],
        "updated_at": datetime.datetime.now().isoformat(),
    })
    return True


def clear_user_roadmaps_firestore(uid):
    """Remove all saved roadmaps for a user."""
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()

    if not doc.exists:
        return False

    doc_ref.update({
        "roadmaps": [],
        "latest_plan": {},
        "updated_at": _iso_now(),
    })
    return True


def delete_user_roadmap_firestore(uid, roadmap_id):
    """Delete one saved roadmap by roadmap_id and refresh latest_plan."""
    if not roadmap_id:
        return False

    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    if not doc.exists:
        return False

    data = doc.to_dict()
    roadmaps = [_normalize_roadmap_entry(item) for item in data.get("roadmaps", [])]
    roadmaps = [item for item in roadmaps if item]
    remaining = [item for item in roadmaps if item.get("roadmap_id") != roadmap_id]

    if len(remaining) == len(roadmaps):
        return False

    latest_plan = {}
    if remaining:
        remaining.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        latest = remaining[0]
        latest_plan = {
            "roadmap": latest.get("roadmap", []),
            "cid": latest.get("cid"),
            "cinfo": latest.get("cinfo", {}),
            "related": latest.get("related", []),
            "total_h": latest.get("total_h", 0),
            "total_w": latest.get("total_w", 0),
            "total_t": latest.get("total_t", 0),
            "domain": latest.get("domain", ""),
            "goal_category": latest.get("goal_category"),
        }

    doc_ref.update({
        "roadmaps": remaining,
        "latest_plan": latest_plan,
        "updated_at": _iso_now(),
    })
    return True


def _calculate_badges(completed_count):
    """Calculate badges based on completed topic count."""
    badges = []
    if completed_count >= 1:
        badges.append("Started Strong")
    if completed_count >= 5:
        badges.append("First 5")
    if completed_count >= 10:
        badges.append("10 Topics")
    if completed_count >= 25:
        badges.append("25 Topics")
    if completed_count >= 50:
        badges.append("Halfway Hero")
    return badges


# ══════════════════════════════════════════════════════════════
#  ROADMAP SAVE/LOAD
# ══════════════════════════════════════════════════════════════

def save_roadmap(uid, name, age, domain, goal, skill, hours, health, roadmap_result):
    """Save generated roadmap to Firestore."""
    profile_data = {
        "name": name,
        "age": age,
        "domain": domain,
        "goal": goal,
        "skill_level": skill,
        "hours_per_day": hours,
        "health_condition": health,
    }
    
    # Save plan without non-serializable objects (like NetworkX Graph)
    plan = {
        "roadmap": roadmap_result["roadmap"],
        "cid": roadmap_result["cid"],
        "cinfo": roadmap_result["cinfo"],
        "related": roadmap_result.get("related", []),
        "total_h": roadmap_result["total_h"],
        "total_w": roadmap_result["total_w"],
        "total_t": roadmap_result["total_t"],
        "domain": roadmap_result["domain"],
        "goal_category": roadmap_result.get("goal_category"),
    }
    
    save_user_profile(uid, profile_data, plan)


def get_all_user_roadmaps(uid):
    """
    Get all roadmaps created by the user from Firestore.
    Returns a list of roadmaps, each containing domain, roadmap, and other plan details.
    """
    data = get_user_profile(uid)
    if not data:
        return []
    
    roadmaps = [_normalize_roadmap_entry(item) for item in data.get("roadmaps", [])]
    roadmaps = [item for item in roadmaps if item]
    if not roadmaps:
        # Fallback: check latest_plan
        latest = _normalize_roadmap_entry(data.get("latest_plan", {}))
        if latest and latest.get("domain"):
            return [latest]
        return []

    roadmaps.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return roadmaps


# ══════════════════════════════════════════════════════════════
#  ALL USERS (FOR DASHBOARD STATS)
# ══════════════════════════════════════════════════════════════

def get_all_users_firestore():
    """Get summary of all users for dashboard stats."""
    users = []
    docs = db.collection("users").stream()
    for doc in docs:
        data = doc.to_dict()
        profile = data.get("profile", {})
        users.append({
            "display_name": profile.get("name", "Learner"),
            "domain": profile.get("domain", ""),
            "completed": data.get("completed", []),
            "sessions": data.get("sessions", 0),
        })
    return users


# ══════════════════════════════════════════════════════════════
#  STREAK MANAGEMENT
# ══════════════════════════════════════════════════════════════

def update_streak(uid):
    """Update user's streak when they log in."""
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    
    if not doc.exists:
        return
    
    data = doc.to_dict()
    last_seen = data.get("updated_at", "")
    
    today = datetime.date.today().isoformat()
    
    if last_seen and last_seen[:10] == today:
        # Already visited today
        return
    
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    
    if last_seen and last_seen[:10] == yesterday:
        # Consecutive day — increment streak
        doc_ref.update({
            "streak_days": data.get("streak_days", 0) + 1,
            "updated_at": datetime.datetime.now().isoformat(),
        })
    else:
        # Streak broken or first visit
        doc_ref.update({
            "streak_days": 1,
            "updated_at": datetime.datetime.now().isoformat(),
        })
