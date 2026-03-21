# ================================================================
#  pages/9_AICoach.py — AI Coach Guide & Chat
#  Personalized guidance and interactive chat with AI Coach
# ================================================================

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from core.engine import get_user, load_kb
from core.sidebar import render_sidebar
from datetime import datetime

st.set_page_config(
    page_title="LearnPath AI — AI Coach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── INJECT CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #f0f4ff !important;
}
.stApp { background: #f0f4ff !important; }

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebarContent"] { padding: 1rem 0.8rem !important; }

/* Main content */
.block-container { padding: 2rem 2.5rem 2rem 2.5rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Cards */
.card {
    background: white; border: 1.5px solid #e2e8f0;
    border-radius: 18px; padding: 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05); margin-bottom: 16px;
}
.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;
}
.card-sub { font-size: .78rem; color: #64748b; margin-bottom: 12px; }

/* Chat message */
.chat-msg {
    padding: 12px 16px; margin: 8px 0; border-radius: 12px;
    font-size: .85rem; line-height: 1.5;
}
.msg-user {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white; margin-left: auto; max-width: 75%;
    border-bottom-right-radius: 4px;
}
.msg-ai {
    background: #f1f5f9; color: #1e293b; margin-right: auto; max-width: 85%;
    border: 1.5px solid #e2e8f0; border-bottom-left-radius: 4px;
}

/* Chat container */
.chat-container {
    background: white; border: 1.5px solid #e2e8f0;
    border-radius: 14px; padding: 16px;
    height: 400px; overflow-y: auto; margin-bottom: 16px;
}

/* Input area */
.stTextInput > div > div > input {
    background: #f8fafc !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1e293b !important; font-size: .88rem !important;
}
.stTextInput > div > div > input::placeholder {
    color: #94a3b8 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important; box-shadow: 0 0 0 3px #6366f120 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: .95rem !important; padding: 0.6rem 1.5rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px #10b98144 !important;
}

/* Tips box */
.tips-box {
    background: linear-gradient(135deg, #ede9fe, #ddd6fe);
    border: 1.5px solid #c4b5fd; border-radius: 12px;
    padding: 16px; margin-bottom: 16px;
}
.tips-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: .9rem; font-weight: 700; color: #5b21b6; margin-bottom: 8px;
}
.tips-item {
    font-size: .8rem; color: #4c1d95; margin: 6px 0;
    padding-left: 20px; position: relative;
}
.tips-item::before {
    content: '✓'; position: absolute; left: 0;
    color: #7c3aed; font-weight: 700;
}

/* Onboarding box */
.onboard-box {
    background: linear-gradient(135deg, #e0f2fe, #bae6fd);
    border: 1.5px solid #7dd3fc; border-radius: 14px;
    padding: 20px; margin-bottom: 20px;
}
.onboard-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.2rem; font-weight: 700; color: #0c4a6e; margin-bottom: 8px;
}
.onboard-desc {
    font-size: .85rem; color: #0e7490; margin-bottom: 12px;
}

/* Feature grid */
.feature-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 12px;
}
.feature-item {
    background: white; border: 1.5px solid #bae6fd;
    border-radius: 10px; padding: 12px; text-align: center;
}
.feature-icon {
    font-size: 1.5rem; margin-bottom: 6px;
}
.feature-name {
    font-size: .75rem; font-weight: 600; color: #0c4a6e;
}

/* Recommendation box */
.rec-box {
    background: white; border-left: 4px solid #6366f1;
    border-radius: 8px; padding: 14px; margin: 8px 0;
    font-size: .82rem; color: #334155;
}

.divider {
    height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    margin: 20px 0;
}

</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

# ── AI COACH RESPONSE GENERATOR ──────────────────────────────
def generate_coach_response(user_message, name, goal, skill_level, user_data):
    """
    Generate personalized AI Coach responses based on user input.
    """
    msg_lower = user_message.lower()
    
    # Greetings
    if any(word in msg_lower for word in ["hi", "hello", "hey", "start", "begin"]):
        return f"Hi {name}! 👋 Great to see you here! I'm your AI Coach, and I'm excited to help you achieve your goal of '{goal}'. What would you like to focus on today? I can help with:\n\n• Why your goal is important\n• How to stay motivated\n• Tips for your {skill_level} level\n• Time management strategies\n• Overcoming challenges"
    
    # Motivation requests
    if any(word in msg_lower for word in ["motiv", "encourage", "inspire", "boost", "confidence"]):
        completed = len(user_data.get("completed", []))
        return f"You're doing amazing, {name}! 💪 You've already completed {completed} topics, which shows real commitment. Remember:\n\n✓ Progress over perfection\n✓ Every small step counts\n✓ Your goal is worth it\n✓ Learning is a journey, not a race\n\nYou've chosen to improve yourself - that's already a huge win! Keep that momentum going! 🚀"
    
    # Tips & suggestions
    if any(word in msg_lower for word in ["tip", "suggest", "recommend", "advice", "help", "how"]):
        tips_list = get_personalized_tips(skill_level, user_data)
        return f"Great question, {name}! Here are my top recommendations for your {skill_level} level:\n\n" + "\n".join(f"• {tip}" for tip in tips_list[:5])
    
    # Schedule/planning
    if any(word in msg_lower for word in ["schedule", "plan", "time", "how long", "when", "week"]):
        hours = st.session_state.get("hrs", 1.5)
        return f"Perfect timing question! Here's my advice for planning your {goal} learning:\n\n📅 Study Schedule:\n• Daily: {hours}h of focused learning\n• Consistency matters more than intensity\n• Best time: Pick when you're most alert\n• Mix: Theory + Practice + Real projects\n\nTry dedicating specific days to different topics. Would you like specific recommendations?"
    
    # General question
    return f"That's a great question, {name}! 🤔\n\nFor your goal of '{goal}', here's what I think:\n\n• Your {skill_level} level is perfect for building solid fundamentals\n• Focus on understanding concepts deeply\n• Practice regularly to reinforce learning\n• Don't hesitate to revisit basics when needed\n\nWhat specific aspect would you like to dive deeper into? I'm here to help!"


def get_personalized_tips(skill_level, user_data):
    """Generate tips based on skill level."""
    if skill_level == "Beginner":
        return [
            "Start with foundational concepts - don't rush",
            "Write down key concepts to reinforce learning",
            "Practice regularly with small, achievable goals",
            "Join study groups or communities",
            "Don't compare your beginning to someone else's middle"
        ]
    elif skill_level == "Intermediate":
        return [
            "Build projects to apply your knowledge",
            "Explore advanced topics at your own pace",
            "Teach others - it deepens your understanding",
            "Contribute to open-source or real projects",
            "Network with people at your level and above"
        ]
    else:  # Advanced
        return [
            "Mentor beginners to solidify your knowledge",
            "Explore niche specializations",
            "Contribute to cutting-edge projects",
            "Stay updated with latest trends and research",
            "Write blogs or create content to share expertise"
        ]


def generate_tips(skill_level, age, completed, total_topics, domain_topics):
    """Generate quick tips for the tip panel."""
    tips = []
    
    if completed == 0:
        tips.append("🌟 Start your first topic today! The first step is the most important.")
    elif completed < 5:
        tips.append(f"🚀 You're off to a great start! {completed} topics down, keep the momentum!")
    else:
        tips.append(f"💎 Impressive! You've mastered {completed} topics. That's real dedication!")
    
    if skill_level == "Beginner":
        tips.append("📚 Master the basics first - they're the foundation for everything.")
    elif skill_level == "Intermediate":
        tips.append("🎯 Time to build projects! Apply what you've learned to real scenarios.")
    else:
        tips.append("🏆 You're at an advanced level - now it's time to innovate and lead!")
    
    pct = round((completed / max(total_topics, 1)) * 100)
    if pct < 25:
        tips.append(f"⏳ {pct}% complete - you've got plenty of exciting learning ahead!")
    elif pct < 50:
        tips.append(f"🔥 Halfway there! {pct}% complete - the momentum is building!")
    elif pct < 100:
        tips.append(f"🎉 Almost there! {pct}% complete - the finish line is in sight!")
    else:
        tips.append("🏅 Congratulations! You've completed your learning journey!")
    
    if age < 25:
        tips.append("⚡ Youth is on your side - embrace curiosity and experiment boldly!")
    elif age < 40:
        tips.append("⚖️ Balance learning with real-world application for maximum impact.")
    else:
        tips.append("🎓 Your experience is your superpower - connect new learning to past knowledge.")
    
    return tips[:3]


# ── GET USER INFO ────────────────────────────────────────────
user_name = st.session_state.get("name", "Learner")
user_age = st.session_state.get("age", 22)
user_goal = st.session_state.get("goal", "No goal set")
user_skill = st.session_state.get("skill", "Beginner")
user_data = get_user(user_name, user_age)

# ── HEADER ───────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:16px">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.7rem;font-weight:800;color:#0f172a">🤖 Your AI Coach</div>
  <div style="color:#64748b;font-size:.86rem">Get personalized guidance, tips, and recommendations for your learning journey</div>
</div>""", unsafe_allow_html=True)

# ── FIRST-TIME ONBOARDING ────────────────────────────────────
if st.session_state.first_visit and user_goal:
    st.markdown(f"""
    <div class="onboard-box">
      <div class="onboard-title">👋 Welcome to Your AI Coach!</div>
      <div class="onboard-desc">
        I'm here to help you achieve your goal of <strong>{user_goal}</strong>. Ask me anything about your learning journey!
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.first_visit = False

# ── AI COACH TIPS & RECOMMENDATIONS ──────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💬 Chat with AI Coach</div>', unsafe_allow_html=True)
    
    # Display chat history
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.markdown(f"""
        <div style="text-align: center; padding: 40px 20px; color: #94a3b8;">
          <div style="font-size: 1.5rem; margin-bottom: 8px;">💬</div>
          <div style="font-size: .85rem;">Start a conversation with your AI Coach!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            msg_class = "msg-user" if msg["role"] == "user" else "msg-ai"
            st.markdown(f'<div class="chat-msg {msg_class}">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    user_input = st.text_input(
        "Your message",
        placeholder="Ask me for tips, ideas, recommendations, or motivation...",
        key="chat_input",
        label_visibility="collapsed"
    )
    
    col_send, col_clear = st.columns([4, 1])
    with col_send:
        if st.button("Send Message", use_container_width=True):
            if user_input.strip():
                # Add user message
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Generate AI response
                ai_response = generate_coach_response(user_input, user_name, user_goal, user_skill, user_data)
                st.session_state.chat_history.append({"role": "ai", "content": ai_response})
                st.rerun()
    
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ── QUICK TIPS & RECOMMENDATIONS ────────────────────────────
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">✨ Quick Tips</div>', unsafe_allow_html=True)
    
    kb = load_kb()
    domain_topics = kb.get(st.session_state.get("domain", "Education"), {})
    total_topics = sum(len(topics) for topics in kb.values())
    completed = len(user_data.get("completed", []))
    
    tips = generate_tips(user_skill, user_age, completed, total_topics, domain_topics)
    
    for tip in tips:
        st.markdown(f'<div class="rec-box">{tip}</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ede9fe, #ddd6fe); border-radius: 10px; padding: 14px; text-align: center;">
      <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size: .95rem; font-weight: 700; color: #6d28d9; margin-bottom: 4px;">Your Goal</div>
      <div style="font-size: 1rem; font-weight: 600; color: #5b21b6; margin-bottom: 8px;">{user_goal}</div>
      <div style="font-size: .75rem; color: #7c3aed;">You've got this! 🚀</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
