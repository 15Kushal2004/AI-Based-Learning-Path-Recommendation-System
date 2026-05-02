import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.engine import get_user, toggle_topic
from core.sidebar import render_sidebar
from utils.firebase_storage import get_user_by_uid, toggle_topic_firestore
import streamlit as st

st.set_page_config(page_title="Assessments", page_icon="📋",
                   layout="wide", initial_sidebar_state="expanded")

# ── INJECT PREMIUM CSS ──────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:4px;letter-spacing:-0.03em">📋 Assessments</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:var(--text-muted);font-size:.84rem;margin-bottom:20px">Test your knowledge and mark topics complete</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res = st.session_state.result
if not isinstance(res, dict):
    st.info("No active roadmap is available right now. Generate a new roadmap from the Dashboard.")
    st.stop()
roadmap = res.get("roadmap", [])
if not roadmap:
    st.info("No active roadmap is available right now. Generate a new roadmap from the Dashboard.")
    st.stop()
age = st.session_state.get("age",22)
uid = st.session_state.get("user_uid")
if uid:
    try:
        user = get_user_by_uid(uid)
    except Exception:
        user = {}
else:
    user = get_user(st.session_state.name, age)
done = user.get("completed",[])

by_cat = {}
for t in roadmap:
    cat = t.get("category","General")
    if cat not in by_cat: by_cat[cat] = []
    by_cat[cat].append(t)


st.markdown('<div class="card-title">🎯 Self Assessment Quiz</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.78rem;color:var(--text-muted);margin-bottom:14px">Answer MCQs for each topic. Score 2/3 to complete a topic.</div>', unsafe_allow_html=True)
selected_cat = st.selectbox("Select Category", list(by_cat.keys()))
topics_to_assess = by_cat[selected_cat][:5]
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

if "assessment_mcq_answers" not in st.session_state:
    st.session_state["assessment_mcq_answers"] = {}
if "assessment_feedback" not in st.session_state:
    st.session_state["assessment_feedback"] = []
if "assessment_feedback_cat" not in st.session_state:
    st.session_state["assessment_feedback_cat"] = ""


def saved_answer_count_for_topic(topic):
    """Return count of answered MCQs for sorting and continuation."""
    topic_id = str(topic.get("id", topic["topic"]))
    saved = st.session_state["assessment_mcq_answers"].get(topic_id, {})
    return sum(1 for v in saved.values() if v is not None)


def build_mcqs(topic_name, level, domain_name, goal_text, category_topics):
    """Create topic-aware MCQs with one correct answer each."""
    goal_text = (goal_text or "your learning goal").strip()
    goal_short = goal_text if len(goal_text) <= 70 else goal_text[:67] + "..."

    distractors = [t["topic"] for t in category_topics if t["topic"] != topic_name][:3]
    while len(distractors) < 3:
        distractors.append(f"Other {domain_name} topic {len(distractors) + 1}")

    identify_options = [topic_name] + distractors[:3]

    if level == "Advanced":
        milestone_options = [
            "I can optimize and handle difficult real-world edge cases.",
            "I only know definitions and no practical usage.",
            "I have never practiced this topic.",
            "I skip testing and validation while using this topic.",
        ]
        milestone_correct = 0
    elif level == "Intermediate":
        milestone_options = [
            "I can solve basic definitions only.",
            "I can apply this topic in projects with moderate confidence.",
            "I avoid using this topic in any real task.",
            "I do not need to revise or practice at all.",
        ]
        milestone_correct = 1
    else:
        milestone_options = [
            "I can explain basics and do one guided practice.",
            "I can already mentor experts in this topic.",
            "I should skip fundamentals and jump to advanced parts.",
            "I only read theory and never try practically.",
        ]
        milestone_correct = 0

    goal_options = [
        f"Do a mini practice using '{topic_name}' aligned to '{goal_short}'.",
        "Skip practice and directly mark topic complete.",
        "Move to unrelated topics without revision.",
        "Only watch videos and avoid any hands-on attempt.",
    ]

    return [
        {
            "q": f"Which exact topic is this MCQ set focused on in {domain_name}?",
            "options": identify_options,
            "correct": 0,
            "explanation": f"The correct answer is '{topic_name}' because this assessment block is specifically designed for that topic.",
        },
        {
            "q": f"What best shows you are ready to continue after '{topic_name}' ({level})?",
            "options": milestone_options,
            "correct": milestone_correct,
            "explanation": "Readiness means applying the topic practically with confidence appropriate to your current level.",
        },
        {
            "q": "What is the best next action to continue your learning goal?",
            "options": goal_options,
            "correct": 0,
            "explanation": "Hands-on practice aligned to your goal is the most effective and reliable way to progress.",
        },
    ]


domain_name = res.get("domain", st.session_state.get("domain", "Education"))
goal_text = st.session_state.get("goal", "")

# Show unfinished topics first and prioritize where user already started.
topics_to_assess = sorted(
    topics_to_assess,
    key=lambda t: (t["topic"] in done, -saved_answer_count_for_topic(t), t.get("step", 9999)),
)

next_topic = next((t for t in topics_to_assess if t["topic"] not in done), None)
if next_topic:
    st.markdown(
        f'<div class="card" style="border:1px solid rgba(99,102,241,0.35);background:rgba(99,102,241,0.08);padding:12px 14px;margin-bottom:10px"><div style="font-size:.78rem;color:#a5b4fc;font-weight:700">Continue From Here</div><div style="font-size:.9rem;color:var(--text);margin-top:4px">📌 Next recommended topic: {next_topic["topic"]}</div></div>',
        unsafe_allow_html=True,
    )

scores = {}
topic_mcqs_map = {}
topic_id_map = {}
completed_in_assessment = 0
for t in topics_to_assess:
    is_done = t["topic"] in done
    is_next = next_topic is not None and t["topic"] == next_topic["topic"] and not is_done
    topic_border = "rgba(99,102,241,0.45)" if is_next else ("var(--success-border)" if is_done else "var(--border)")
    topic_bg = "rgba(99,102,241,0.08)" if is_next else ("var(--success-bg)" if is_done else "var(--bg-subtle)")
    prefix = "▶️" if is_next else ("✅" if is_done else "📖")
    st.markdown(f'<div style="background:{topic_bg};border:1px solid {topic_border};border-radius:10px;padding:14px;margin:10px 0"><div style="font-size:.9rem;font-weight:600;color:var(--text);margin-bottom:10px">{prefix} {t["topic"]}</div>', unsafe_allow_html=True)

    topic_id = str(t.get("id", t["topic"]))
    if topic_id not in st.session_state["assessment_mcq_answers"]:
        st.session_state["assessment_mcq_answers"][topic_id] = {}

    mcqs = build_mcqs(
        t["topic"],
        t.get("level", "Beginner"),
        domain_name,
        goal_text,
        by_cat[selected_cat],
    )
    topic_mcqs_map[t["topic"]] = mcqs
    topic_id_map[t["topic"]] = topic_id

    score = 0
    for idx, mcq in enumerate(mcqs):
        options = mcq["options"]
        placeholder = "Select an answer"
        radio_options = [placeholder] + options

        stored_idx = st.session_state["assessment_mcq_answers"][topic_id].get(str(idx), None)
        default_index = (stored_idx + 1) if isinstance(stored_idx, int) and 0 <= stored_idx < len(options) else 0

        choice = st.radio(
            mcq["q"],
            radio_options,
            index=default_index,
            key=f"mcq_{topic_id}_{idx}",
            disabled=is_done,
        )

        if choice == placeholder:
            st.session_state["assessment_mcq_answers"][topic_id][str(idx)] = None
        else:
            selected_idx = options.index(choice)
            st.session_state["assessment_mcq_answers"][topic_id][str(idx)] = selected_idx
            if selected_idx == mcq["correct"]:
                score += 1

    st.markdown(
        f'<div style="font-size:.74rem;color:var(--text-muted);margin-top:6px">Score: {score}/3</div></div>',
        unsafe_allow_html=True,
    )

    scores[t["topic"]] = score
    if score >= 2 or is_done:
        completed_in_assessment += 1


assessment_pct = round(completed_in_assessment / max(len(topics_to_assess), 1) * 100)
st.markdown(
    f'<div style="font-size:.78rem;color:var(--text-muted);margin:8px 0 10px">Assessment progress in this category: {completed_in_assessment}/{len(topics_to_assess)} topics</div>',
    unsafe_allow_html=True,
)
st.progress(assessment_pct / 100)

if st.session_state.get("assessment_feedback") and st.session_state.get("assessment_feedback_cat") == selected_cat:
    st.markdown('<div class="card-title" style="margin-top:14px">🧠 Quiz Feedback (English)</div>', unsafe_allow_html=True)
    for topic_feedback in st.session_state["assessment_feedback"]:
        status = "✅ Passed" if topic_feedback["score"] >= 2 else "❌ Needs Review"
        with st.expander(f"{status} · {topic_feedback['topic']} · Score {topic_feedback['score']}/3", expanded=False):
            for idx, item in enumerate(topic_feedback["items"], start=1):
                st.markdown(f"**Q{idx}. {item['question']}**")
                st.markdown(f"Your answer: {item['selected']}")
                st.markdown(f"Correct answer: {item['correct']}")
                st.markdown(f"Explanation: {item['explanation']}")
                st.markdown("---")




_, bc, _ = st.columns([2,2,2])
with bc:
    if st.button("✅ Submit Assessment", use_container_width=True):
        feedback_payload = []
        newly = 0
        for topic_name, score in scores.items():
            topic_items = []
            topic_mcqs = topic_mcqs_map.get(topic_name, [])
            topic_id = topic_id_map.get(topic_name, topic_name)
            for idx, mcq in enumerate(topic_mcqs):
                selected_idx = st.session_state["assessment_mcq_answers"].get(topic_id, {}).get(str(idx), None)
                selected_text = (
                    mcq["options"][selected_idx]
                    if isinstance(selected_idx, int) and 0 <= selected_idx < len(mcq["options"])
                    else "Not answered"
                )
                correct_text = mcq["options"][mcq["correct"]]
                topic_items.append({
                    "question": mcq["q"],
                    "selected": selected_text,
                    "correct": correct_text,
                    "explanation": mcq.get("explanation", ""),
                })

            feedback_payload.append({
                "topic": topic_name,
                "score": score,
                "items": topic_items,
            })

            if score >= 2 and topic_name not in done:
                if uid:
                    try:
                        toggle_topic_firestore(uid, topic_name)
                        newly += 1
                    except Exception:
                        st.warning("Could not save some progress to cloud. Please try again.")
                else:
                    toggle_topic(st.session_state.name, age, topic_name)
                    newly += 1

            st.session_state["assessment_feedback"] = feedback_payload
            st.session_state["assessment_feedback_cat"] = selected_cat
        st.markdown(f'<div class="asuc">🎉 {newly if newly else "No new"} topic(s) marked complete!</div>', unsafe_allow_html=True)
        if newly: st.rerun()
