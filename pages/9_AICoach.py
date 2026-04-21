# ================================================================
#  pages/9_AICoach.py - AI Coach Guide & Chat
#  Personalized guidance and interactive chat with AI Coach
# ================================================================

import html
import os
import re
import sys
from datetime import datetime
from urllib.parse import quote_plus

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st

from core.engine import get_user, load_kb
from core.sidebar import render_sidebar
from ui.theme import PREMIUM_CSS
from utils.session_manager import auth_guard

try:
    from google import genai as genai_new
    from google.genai import types as genai_types

    GENAI_AVAILABLE = True
except Exception:
    genai_new = None
    genai_types = None
    GENAI_AVAILABLE = False


st.set_page_config(
    page_title="LearnPath AI - AI Coach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

auth_guard()

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)
st.markdown(
    """
<style>
.coach-hero {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:16px;
    margin:8px 0 18px;
}
.coach-title {
    font-family:var(--font-display);
    font-size:1.85rem;
    font-weight:800;
    color:var(--text);
    letter-spacing:-0.04em;
    margin-bottom:6px;
}
.coach-subtitle {
    color:var(--text-muted);
    font-size:.84rem;
}
.coach-pill {
    background:rgba(99,102,241,0.1);
    border:1px solid rgba(99,102,241,0.22);
    color:#a5b4fc;
    padding:6px 12px;
    border-radius:999px;
    font-size:.7rem;
    font-weight:700;
    white-space:nowrap;
}
.coach-grid {
    display:grid;
    grid-template-columns:repeat(3, minmax(0,1fr));
    gap:12px;
    margin-bottom:16px;
}
.coach-stat {
    background:var(--bg-card);
    border:1px solid var(--border);
    border-radius:var(--radius);
    padding:16px;
    backdrop-filter:blur(10px);
}
.coach-stat-label {
    color:var(--text-muted);
    font-size:.68rem;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:.08em;
    margin-bottom:8px;
}
.coach-stat-value {
    color:var(--text);
    font-size:1.02rem;
    font-weight:700;
    line-height:1.35;
}
.coach-shell {
    background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
    border:1px solid rgba(255,255,255,0.07);
    border-radius:18px;
    padding:18px;
    min-height:100%;
    backdrop-filter:blur(10px);
}
.coach-shell-title {
    font-family:var(--font-display);
    font-size:1rem;
    font-weight:700;
    color:var(--text);
    margin-bottom:4px;
}
.coach-shell-sub {
    color:var(--text-muted);
    font-size:.76rem;
    margin-bottom:14px;
}
.chat-frame {
    background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:16px;
    min-height:430px;
    max-height:430px;
    overflow-y:auto;
    padding:16px;
    margin-bottom:14px;
}
.chat-frame::-webkit-scrollbar {
    width:6px;
}
.chat-frame::-webkit-scrollbar-thumb {
    background:rgba(129,140,248,0.28);
    border-radius:999px;
}
.msg-row {
    display:flex;
    gap:10px;
    margin:10px 0;
}
.msg-row.user {
    justify-content:flex-end;
}
.msg-avatar {
    width:34px;
    height:34px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-shrink:0;
    font-size:.95rem;
}
.msg-avatar.ai {
    background:linear-gradient(135deg,#6366f1,#818cf8);
    box-shadow:0 0 18px rgba(99,102,241,0.2);
}
.msg-avatar.user {
    background:linear-gradient(135deg,#10b981,#14b8a6);
    box-shadow:0 0 18px rgba(16,185,129,0.16);
}
.msg-bubble {
    max-width:80%;
    padding:12px 14px;
    border-radius:14px;
    font-size:.84rem;
    line-height:1.7;
    white-space:normal;
    word-break:break-word;
}
.msg-bubble.ai {
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.07);
    color:var(--text);
    border-top-left-radius:6px;
}
.msg-bubble.user {
    background:linear-gradient(135deg,#6366f1,#818cf8);
    color:white;
    border-top-right-radius:6px;
}
.msg-bubble pre {
    background:#0b1220 !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    border-radius:10px !important;
    padding:12px !important;
    overflow-x:auto !important;
}
.msg-bubble code {
    background:rgba(129,140,248,0.14) !important;
    color:#c7d2fe !important;
    border-radius:6px !important;
    padding:2px 6px !important;
}
.coach-empty {
    height:100%;
    min-height:350px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    color:var(--text-muted);
}
.coach-empty-title {
    color:var(--text);
    font-size:1rem;
    font-weight:700;
    margin:8px 0 4px;
}
.coach-tip {
    background:rgba(99,102,241,0.08);
    border:1px solid rgba(99,102,241,0.16);
    color:#c7d2fe;
    border-radius:12px;
    padding:12px 14px;
    margin-bottom:10px;
    font-size:.8rem;
    line-height:1.6;
}
.coach-resource {
    display:block;
    text-decoration:none;
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:12px;
    padding:12px 14px;
    margin-bottom:8px;
    transition:all .18s ease;
}
.coach-resource:hover {
    transform:translateY(-1px);
    border-color:rgba(129,140,248,0.25);
    box-shadow:0 10px 24px rgba(15,23,42,0.22);
}
.coach-resource-row {
    display:flex;
    align-items:center;
    gap:10px;
}
.coach-resource-icon {
    width:34px;
    height:34px;
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:rgba(99,102,241,0.12);
    font-size:1rem;
    flex-shrink:0;
}
.coach-resource-title {
    color:var(--text);
    font-size:.82rem;
    font-weight:700;
}
.coach-resource-sub {
    color:var(--text-muted);
    font-size:.7rem;
    margin-top:2px;
}
.coach-section-label {
    color:#a5b4fc;
    font-size:.72rem;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:.08em;
    margin:10px 0 8px;
}
div[data-testid="stTextInput"] input {
    background:rgba(255,255,255,0.04) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    color:var(--text) !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color:var(--text-muted) !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color:rgba(99,102,241,0.45) !important;
    box-shadow:0 0 0 3px rgba(99,102,241,0.12) !important;
}
@media (max-width: 900px) {
    .coach-grid {
        grid-template-columns:1fr;
    }
    .coach-hero {
        flex-direction:column;
        align-items:flex-start;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

render_sidebar()


def get_gemini_api_key():
    api_key = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    return api_key


@st.cache_resource(show_spinner=False)
def get_gemini_client(api_key):
    if not api_key or not GENAI_AVAILABLE:
        return None
    return genai_new.Client(api_key=api_key)


def sanitize_youtube_links(text, fallback_query):
    query = quote_plus(fallback_query or "learning tutorial")
    return re.sub(
        r"https?://www\.youtube\.com/watch\?v=[^\s)>\"']+",
        f"https://www.youtube.com/results?search_query={query}",
        text,
    )


def markdown_to_html_block(text):
    safe = html.escape(text or "")
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
    safe = safe.replace("\n", "<br>")
    return safe


def build_recent_history():
    history = st.session_state.get("chat_history", [])
    recent = history[-6:]
    lines = []
    for item in recent:
        role = "Coach" if item.get("role") == "ai" else "User"
        content = (item.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content[:500]}")
    return "\n".join(lines)


def generate_search_resource_block(user_message):
    topic = quote_plus((user_message or "learning").strip())
    return (
        "\n\nQuick resources:\n"
        f"- YouTube search: https://www.youtube.com/results?search_query={topic}+tutorial\n"
        f"- Beginner search: https://www.youtube.com/results?search_query={topic}+for+beginners\n"
        f"- Practice ideas: https://www.youtube.com/results?search_query={topic}+projects\n"
    )


def fallback_coach_response(user_message, name, goal, skill_level, user_data):
    msg = (user_message or "").lower().strip()
    completed = len(user_data.get("completed", []))
    hours = st.session_state.get("hrs", 1.5)

    if any(word in msg for word in ["hi", "hello", "hey", "start", "begin"]):
        return (
            f"Hi {name}! I'm ready to help with your goal: **{goal or 'your learning journey'}**.\n\n"
            f"- Skill level: {skill_level}\n"
            f"- Completed topics: {completed}\n"
            f"- Suggested daily time: {hours}h\n\n"
            "Ask me for a study plan, motivation, resources, practice ideas, or help with any topic."
        )

    if any(word in msg for word in ["motivation", "encourage", "stuck", "demotivated", "confidence"]):
        return (
            f"You're doing better than you think, {name}.\n\n"
            f"- You've already completed **{completed}** topics.\n"
            "- Progress beats perfection.\n"
            "- A short focused session today is enough to keep momentum.\n"
            f"- Stay consistent with your **{hours}h/day** plan.\n\n"
            "If you want, I can turn your current goal into a 3-step plan for today."
        )

    if any(word in msg for word in ["playlist", "course", "youtube", "resource", "video"]):
        return (
            f"Here are safe search links for **{user_message.strip()}**:\n"
            + generate_search_resource_block(user_message)
        )

    if any(word in msg for word in ["schedule", "plan", "routine", "time table", "weekly"]):
        return (
            f"Here is a simple plan for **{goal or 'your goal'}**:\n\n"
            f"- Study {hours}h each day.\n"
            "- Split time into learning, practice, and review.\n"
            "- Use 25-30 minute focus blocks.\n"
            "- End each session by noting one takeaway and one next step.\n\n"
            "If you want, I can make this into a weekday-by-weekday schedule."
        )

    return (
        f"I can help with that, {name}.\n\n"
        f"- Goal: {goal or 'Not set'}\n"
        f"- Skill level: {skill_level}\n"
        f"- Completed so far: {completed}\n\n"
        "Tell me what you need: explanation, study plan, practice tasks, resource links, troubleshooting, or motivation."
    )


def generate_coach_response(user_message, name, goal, skill_level, user_data, api_key):
    if not user_message or not user_message.strip():
        return "Please type a question and I'll help right away."

    if api_key and GENAI_AVAILABLE:
        try:
            client = get_gemini_client(api_key)
            if client is not None:
                system_instruction = (
                    "You are a practical AI learning coach inside a study-planning app. "
                    "Be warm, clear, concise, and action-oriented. "
                    "Answer the user's actual question directly. "
                    "Use short paragraphs or flat bullets when useful. "
                    "Do not invent private facts, course enrollments, or exact YouTube videos. "
                    "If suggesting YouTube, prefer search URLs instead of direct watch links. "
                    "If the user asks broad or emotional questions, still answer supportively and concretely."
                )
                context = (
                    f"User name: {name}\n"
                    f"Goal: {goal or 'Not set'}\n"
                    f"Skill level: {skill_level}\n"
                    f"Age: {st.session_state.get('age', 22)}\n"
                    f"Hours per day: {st.session_state.get('hrs', 1.5)}\n"
                    f"Completed topics: {len(user_data.get('completed', []))}\n"
                    f"Health notes: {st.session_state.get('health', '') or 'None'}\n"
                )
                recent_history = build_recent_history()
                prompt = (
                    f"{context}\n"
                    f"Recent conversation:\n{recent_history or 'None'}\n\n"
                    f"User question: {user_message}\n\n"
                    "Respond in markdown. Keep the answer useful and not overly long."
                )

                model_order = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]
                for model_name in model_order:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=genai_types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.45,
                                top_p=0.9,
                                max_output_tokens=700,
                            ),
                        )
                        text = getattr(response, "text", "") or ""
                        text = text.strip()
                        if text:
                            return sanitize_youtube_links(text, user_message)
                    except Exception:
                        continue
        except Exception:
            pass

    return fallback_coach_response(user_message, name, goal, skill_level, user_data)


def generate_tips(skill_level, age, completed, total_topics):
    tips = []
    if completed == 0:
        tips.append("Start with one small win today. Momentum matters more than intensity.")
    elif completed < 5:
        tips.append(f"You already finished {completed} topics. Keep the streak alive with one more focused session.")
    else:
        tips.append(f"You've completed {completed} topics. This is real progress, not just intention.")

    if skill_level == "Beginner":
        tips.append("Protect your fundamentals. Strong basics make every later topic easier.")
    elif skill_level == "Intermediate":
        tips.append("Shift more time toward projects and recall practice, not just passive watching.")
    else:
        tips.append("At your level, deliberate practice and feedback loops matter more than volume.")

    pct = round((completed / max(total_topics, 1)) * 100)
    if pct < 25:
        tips.append("You're in the build phase. Consistency now will compound later.")
    elif pct < 75:
        tips.append("You're in the middle stretch. Review regularly so earlier topics stay sharp.")
    else:
        tips.append("You're close to strong mastery. Focus on weak spots and real-world application.")

    if age >= 40:
        tips.append("Tie new learning to what you already know. Experience is an advantage, not a limitation.")
    elif age >= 25:
        tips.append("Balance learning with practical output. Even a tiny project each week will help.")
    else:
        tips.append("Experiment broadly, then double down on what feels engaging and sustainable.")
    return tips[:3]


def get_categorized_playlists(age, goal, skill):
    goal_query = quote_plus(goal or "learning")
    if age < 18:
        return {
            "Gardening & Nature": [
                {"label": "Urban Gardening Basics", "icon": "🌿", "url": "https://www.youtube.com/results?search_query=urban+gardening+basics"},
                {"label": "Indoor Plant Care", "icon": "🌱", "url": "https://www.youtube.com/results?search_query=indoor+plant+care+beginners"},
            ],
            "Health & Fitness": [
                {"label": "Teen Fitness Routines", "icon": "🏃", "url": "https://www.youtube.com/results?search_query=teen+fitness+routine"},
                {"label": "Healthy Eating Basics", "icon": "🥗", "url": "https://www.youtube.com/results?search_query=healthy+eating+for+teens"},
            ],
            "Education & Skills": [
                {"label": "Goal-Based Tutorials", "icon": "🎓", "url": f"https://www.youtube.com/results?search_query={goal_query}+tutorial"},
                {"label": "Khan Academy Search", "icon": "📚", "url": f"https://www.khanacademy.org/search?page_search_query={goal_query}"},
            ],
        }
    if age < 40:
        return {
            "Gardening & Home": [
                {"label": "Home Garden Design", "icon": "🏡", "url": "https://www.youtube.com/results?search_query=home+garden+design+ideas"},
                {"label": "Vegetable Gardening", "icon": "🥬", "url": "https://www.youtube.com/results?search_query=vegetable+gardening+guide"},
            ],
            "Health & Wellness": [
                {"label": "Stress Management", "icon": "🧘", "url": "https://www.youtube.com/results?search_query=stress+management+techniques"},
                {"label": "Fitness & Mobility", "icon": "💪", "url": "https://www.youtube.com/results?search_query=fitness+mobility+routine"},
            ],
            "Professional Growth": [
                {"label": "Goal-Based Learning", "icon": "🚀", "url": f"https://www.youtube.com/results?search_query={goal_query}+complete+course"},
                {"label": "Project Practice", "icon": "🛠️", "url": f"https://www.youtube.com/results?search_query={goal_query}+projects"},
            ],
        }
    return {
        "Gardening & Relaxation": [
            {"label": "Therapeutic Gardening", "icon": "🌸", "url": "https://www.youtube.com/results?search_query=therapeutic+gardening"},
            {"label": "Growing Herbs", "icon": "🌿", "url": "https://www.youtube.com/results?search_query=growing+herbs+beginners"},
        ],
        "Health & Wellness": [
            {"label": "Low-Impact Exercise", "icon": "🚶", "url": "https://www.youtube.com/results?search_query=low+impact+exercise+adults"},
            {"label": "Nutrition After 40", "icon": "🥗", "url": "https://www.youtube.com/results?search_query=nutrition+after+40"},
        ],
        "Lifelong Learning": [
            {"label": "Step-by-Step Tutorials", "icon": "🎓", "url": f"https://www.youtube.com/results?search_query={goal_query}+step+by+step"},
            {"label": "Beginner-Friendly Search", "icon": "📚", "url": f"https://www.youtube.com/results?search_query={goal_query}+for+beginners"},
        ],
    }


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "pending_msg" not in st.session_state:
    st.session_state.pending_msg = ""


def on_enter():
    value = st.session_state.get(f"chat_input_{st.session_state.input_key}", "").strip()
    if value:
        st.session_state.pending_msg = value
        st.session_state.input_key += 1


user_name = st.session_state.get("name", "Learner")
user_age = st.session_state.get("age", 22)
user_goal = st.session_state.get("goal", "No goal set")
user_skill = st.session_state.get("skill", "Beginner")
user_data = get_user(user_name, user_age)
completed_topics = len(user_data.get("completed", []))
kb = load_kb()
kb_topic_count = sum(len(topics) for levels in kb.values() for topics in levels.values())
current_domain = st.session_state.get("domain", "Education")
gemini_api_key = get_gemini_api_key()

st.markdown(
    f"""
<div class="coach-hero">
  <div>
    <div class="coach-title">Your AI Coach</div>
    <div class="coach-subtitle">Ask questions, get study guidance, generate resource ideas, and stay consistent with your learning path.</div>
  </div>
  <div class="coach-pill">{'Gemini Connected' if gemini_api_key and GENAI_AVAILABLE else 'Smart Fallback Active'}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="coach-grid">
  <div class="coach-stat">
    <div class="coach-stat-label">Current Goal</div>
    <div class="coach-stat-value">{html.escape(user_goal or 'No goal set')}</div>
  </div>
  <div class="coach-stat">
    <div class="coach-stat-label">Focus Profile</div>
    <div class="coach-stat-value">{html.escape(current_domain)} · {html.escape(user_skill)}</div>
  </div>
  <div class="coach-stat">
    <div class="coach-stat-label">Progress Snapshot</div>
    <div class="coach-stat-value">{completed_topics} topics completed · {kb_topic_count} in knowledge base</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if st.session_state.first_visit and user_goal and user_goal != "No goal set":
    st.markdown(
        f"""
    <div class="card" style="margin-bottom:16px">
      <div class="card-title">Welcome Back</div>
      <div class="card-sub">Your coach is tuned to your current goal and study profile.</div>
      <div style="font-size:.82rem;color:var(--text-secondary);line-height:1.7">
        Goal: <strong>{html.escape(user_goal)}</strong><br>
        Domain: <strong>{html.escape(current_domain)}</strong><br>
        Recommended habit: <strong>{st.session_state.get('hrs', 1.5)}h/day</strong>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.session_state.first_visit = False

left, right = st.columns([1.9, 1], gap="large")

with left:
    st.markdown('<div class="coach-shell">', unsafe_allow_html=True)
    st.markdown('<div class="coach-shell-title">Chat with your AI Coach</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="coach-shell-sub">Ask about concepts, study plans, practice tasks, motivation, resources, routines, or any confusion you have.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chat-frame">', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.markdown(
            """
        <div class="coach-empty">
          <div>
            <div style="font-size:2rem">🤖</div>
            <div class="coach-empty-title">Your coach is ready</div>
            <div style="font-size:.8rem">Try asking for a study plan, a topic explanation, playlist ideas, or motivation for today.</div>
          </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        for message in st.session_state.chat_history:
            role = message.get("role")
            content_html = markdown_to_html_block(message.get("content", ""))
            if role == "user":
                st.markdown(
                    f"""
                <div class="msg-row user">
                  <div class="msg-bubble user">{content_html}</div>
                  <div class="msg-avatar user">👤</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="msg-row">
                  <div class="msg-avatar ai">🤖</div>
                  <div class="msg-bubble ai">{content_html}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.pending_msg:
        outgoing = st.session_state.pending_msg
        st.session_state.pending_msg = ""
        st.session_state.chat_history.append({"role": "user", "content": outgoing})
        with st.spinner("Thinking..."):
            reply = generate_coach_response(
                outgoing,
                user_name,
                user_goal,
                user_skill,
                user_data,
                gemini_api_key,
            )
        st.session_state.chat_history.append({"role": "ai", "content": reply})
        st.rerun()

    user_input = st.text_input(
        "Message",
        placeholder="Type your message and press Enter...",
        key=f"chat_input_{st.session_state.input_key}",
        label_visibility="collapsed",
        on_change=on_enter,
    )

    send_col, clear_col = st.columns([5, 1])
    with send_col:
        if st.button("Send Message", use_container_width=True):
            if user_input.strip():
                st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
                with st.spinner("Thinking..."):
                    reply = generate_coach_response(
                        user_input.strip(),
                        user_name,
                        user_goal,
                        user_skill,
                        user_data,
                        gemini_api_key,
                    )
                st.session_state.chat_history.append({"role": "ai", "content": reply})
                st.session_state.input_key += 1
                st.rerun()
    with clear_col:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.input_key += 1
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="coach-shell">', unsafe_allow_html=True)
    st.markdown('<div class="coach-shell-title">Coach Suggestions</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="coach-shell-sub">Quick nudges and resource shortcuts based on your profile, domain, and pace.</div>',
        unsafe_allow_html=True,
    )

    total_topics = max(len(st.session_state.get("result", {}).get("roadmap", [])), completed_topics, 1)
    for tip in generate_tips(user_skill, user_age, completed_topics, total_topics):
        st.markdown(f'<div class="coach-tip">{html.escape(tip)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="coach-section-label">Suggested Resource Paths</div>', unsafe_allow_html=True)
    playlists_by_category = get_categorized_playlists(user_age, user_goal, user_skill)
    for category, resources in playlists_by_category.items():
        st.markdown(f'<div style="font-size:.8rem;font-weight:700;color:var(--text);margin:10px 0 8px">{html.escape(category)}</div>', unsafe_allow_html=True)
        for item in resources:
            st.markdown(
                f"""
            <a class="coach-resource" href="{item['url']}" target="_blank">
              <div class="coach-resource-row">
                <div class="coach-resource-icon">{item['icon']}</div>
                <div style="flex:1">
                  <div class="coach-resource-title">{html.escape(item['label'])}</div>
                  <div class="coach-resource-sub">Open learning resources</div>
                </div>
                <div style="color:#a5b4fc;font-size:.9rem;font-weight:700">→</div>
              </div>
            </a>
            """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
