"""Central constants and filesystem locations for the learning path app."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
TOPICS_FILE = DATA_DIR / "knowledge_base.json"
USERS_FILE = DATA_DIR / "users_data.json"

DOMAINS = ["Education", "Entrepreneurship", "Health", "Hobbies"]
SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced"]
LEVEL_ORDER = {level: index for index, level in enumerate(SKILL_LEVELS)}
STUDY_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

CLUSTER_METADATA = {
    "starter_sprint": {
        "name": "Starter Sprint",
        "accent": "#2563eb",
        "description": "Best for younger learners building core fundamentals with a clear short-term goal.",
    },
    "career_accelerator": {
        "name": "Career Accelerator",
        "accent": "#7c3aed",
        "description": "Suited to practical learners aiming for business, startup, or career growth.",
    },
    "wellness_reset": {
        "name": "Wellness Reset",
        "accent": "#059669",
        "description": "Balanced for health-focused plans that need sustainable pacing and safety checks.",
    },
    "steady_upskiller": {
        "name": "Steady Upskiller",
        "accent": "#ea580c",
        "description": "Designed for structured learners progressing through deeper intermediate or advanced work.",
    },
    "creative_explorer": {
        "name": "Creative Explorer",
        "accent": "#db2777",
        "description": "Ideal for hobby-led learning paths with variety, experimentation, and discovery.",
    },
    "lifelong_balancer": {
        "name": "Lifelong Balancer",
        "accent": "#0f766e",
        "description": "A calm, consistency-first path for mature learners balancing wellness and pace.",
    },
}

DOMAIN_KEYWORDS = {
    "Education": {"python", "coding", "programming", "machine learning", "data science", "study", "exam", "language", "math", "science", "ai", "software"},
    "Entrepreneurship": {"startup", "business", "marketing", "sales", "branding", "funding", "revenue", "product", "leadership", "finance", "company", "growth"},
    "Health": {"fitness", "health", "nutrition", "weight", "sleep", "stress", "workout", "wellness", "diet", "anxiety", "mobility", "meditation"},
    "Hobbies": {"guitar", "dance", "painting", "photography", "music", "cooking", "gardening", "art", "chess", "craft", "singing", "design"},
}

HEALTH_RULES = [
    {"conditions": ["heart", "cardiac", "hypertension", "blood pressure"], "blocked_keywords": ["hiit", "marathon", "crossfit", "powerlifting", "sprint"]},
    {"conditions": ["knee", "joint", "arthritis"], "blocked_keywords": ["jump", "plyometric", "running", "marathon", "powerlifting"]},
    {"conditions": ["back", "spine"], "blocked_keywords": ["deadlift", "heavy squat", "powerlifting"]},
]

TIME_RULES = [
    {"max_hours_per_day": 1.0, "max_topic_duration": 10.0},
    {"max_hours_per_day": 2.0, "max_topic_duration": 14.0},
]
