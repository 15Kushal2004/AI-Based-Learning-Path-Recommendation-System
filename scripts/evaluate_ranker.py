import os
import re
import statistics

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.engine import detect_goal_category, generate_roadmap, load_kb


def tokenize(text):
    return {w for w in re.findall(r"[a-zA-Z]+", (text or "").lower()) if len(w) >= 3}


def topk_overlap(goal, roadmap, k=3):
    goal_tokens = tokenize(goal)
    if not goal_tokens or not roadmap:
        return 0.0
    top = roadmap[:k]
    scores = []
    for t in top:
        topic_tokens = tokenize(t.get("topic", ""))
        scores.append(len(goal_tokens & topic_tokens) / len(goal_tokens))
    return sum(scores) / len(scores) if scores else 0.0


def category_hit(goal, roadmap, k=5):
    cat = detect_goal_category(goal)
    if not cat or not roadmap:
        return 0
    return int(any(t.get("category", "").lower() == cat.lower() for t in roadmap[:k]))


def main():
    kb = load_kb()
    cases = [
        ("Education", "learn python for backend development", "Beginner", 22, 2.0, ""),
        ("Education", "become data scientist using machine learning", "Intermediate", 24, 2.5, ""),
        ("Education", "prepare for algebra and calculus basics", "Beginner", 19, 1.5, ""),
        ("Education", "improve spoken english and grammar", "Beginner", 21, 1.0, ""),
        ("Education", "learn ui ux design with figma", "Beginner", 23, 1.5, ""),
        ("Entrepreneurship", "start a startup and build mvp", "Beginner", 27, 2.0, ""),
        ("Entrepreneurship", "improve digital marketing and seo", "Intermediate", 26, 1.5, ""),
        ("Entrepreneurship", "learn sales negotiation and closing deals", "Beginner", 29, 1.5, ""),
        ("Health", "lose weight with workout and diet plan", "Beginner", 35, 1.0, "knee pain"),
        ("Health", "reduce stress with meditation and mindfulness", "Beginner", 31, 1.0, ""),
        ("Hobbies", "learn guitar and music theory", "Beginner", 20, 1.0, ""),
        ("Hobbies", "start gardening and plant care at home", "Beginner", 45, 0.5, ""),
    ]

    top3_scores = []
    hit5_scores = []
    for domain, goal, skill, age, hrs, health in cases:
        result = generate_roadmap("Bench", age, domain, goal, skill, hrs, health, kb)
        roadmap = result.get("roadmap", [])
        top3_scores.append(topk_overlap(goal, roadmap, k=3))
        hit5_scores.append(category_hit(goal, roadmap, k=5))

    top3_overlap_avg = statistics.mean(top3_scores) if top3_scores else 0.0
    top5_cat_hit = (sum(hit5_scores) / len(hit5_scores)) if hit5_scores else 0.0
    quality_score = (0.7 * top3_overlap_avg) + (0.3 * top5_cat_hit)

    print("Model path:", os.path.join(os.path.dirname(__file__), "..", "models", "goal_topic_ranker.pkl"))
    print(f"TOP3_OVERLAP_AVG: {top3_overlap_avg:.4f}")
    print(f"TOP5_CATEGORY_HIT: {top5_cat_hit:.4f}")
    print(f"QUALITY_SCORE: {quality_score:.4f}")


if __name__ == "__main__":
    main()
