import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.engine import get_user, toggle_topic
from core.sidebar import render_sidebar
import streamlit as st

st.set_page_config(page_title="Assessments", page_icon="📋",
                   layout="wide", initial_sidebar_state="expanded")

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

.card { background: white; border: 1.5px solid #e2e8f0; border-radius: 18px; padding: 22px; box-shadow: 0 1px 4px rgba(0,0,0,.05); margin-bottom: 16px; }
.card-title { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.card-sub { font-size: .76rem; color: #64748b; margin-bottom: 16px; }

.asuc { background: #dcfce7; border: 1.5px solid #bbf7d0; border-radius: 10px; padding: 12px 16px; margin: 10px 0; font-size: .82rem; color: #14532d; }
</style>
""", unsafe_allow_html=True)

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.6rem;font-weight:800;color:#0f172a;margin-bottom:4px">📋 Assessments</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:.86rem;margin-bottom:20px">Test your knowledge and mark topics complete</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("ℹ️ Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res = st.session_state.result
roadmap = res["roadmap"]
age = st.session_state.get("age",22)
user = get_user(st.session_state.name, age)
done = user.get("completed",[])

by_cat = {}
for t in roadmap:
    cat = t.get("category","General")
    if cat not in by_cat: by_cat[cat] = []
    by_cat[cat].append(t)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🎯 Self Assessment Quiz</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.78rem;color:#64748b;margin-bottom:14px">Answer all 3 questions to mark a topic as complete</div>', unsafe_allow_html=True)
selected_cat = st.selectbox("Select Category", list(by_cat.keys()))
topics_to_assess = by_cat[selected_cat][:5]
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

QS = {"Beginner":["Can you explain the basic concept?","Have you done at least one practice?","Could you teach the basics to someone?"],
      "Intermediate":["Can you apply this in a project?","Solved 3+ problems with this skill?","Understand advanced concepts?"],
      "Advanced":["Built something significant with this?","Can you mentor others?","Know edge cases and best practices?"]}

scores = {}
for t in topics_to_assess:
    is_done = t["topic"] in done
    st.markdown(f'<div style="background:{"#f0fdf4" if is_done else "#f8fafc"};border:1.5px solid {"#bbf7d0" if is_done else "#e2e8f0"};border-radius:12px;padding:14px;margin:10px 0"><div style="font-size:.9rem;font-weight:600;color:#0f172a;margin-bottom:10px">{"✅" if is_done else "📖"} {t["topic"]}</div>', unsafe_allow_html=True)
    qs = QS.get(t.get("level","Beginner"), QS["Beginner"])
    score = 0
    for q in qs:
        if st.checkbox(q, key=f"q_{t['id']}_{q[:15]}", value=is_done): score += 1
    scores[t["topic"]] = score
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

_, bc, _ = st.columns([2,2,2])
with bc:
    if st.button("✅ Submit Assessment", use_container_width=True):
        newly = sum(1 for tn,sc in scores.items() if sc >= 3 and tn not in done and not toggle_topic(st.session_state.name, age, tn))
        st.markdown(f'<div class="asuc">🎉 {newly if newly else "No new"} topic(s) marked complete!</div>', unsafe_allow_html=True)
        if newly: st.rerun()

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🎯 Self Assessment Quiz</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.78rem;color:#64748b;margin-bottom:14px">Answer all 3 questions to mark a topic as complete</div>', unsafe_allow_html=True)
selected_cat = st.selectbox("Select Category", list(by_cat.keys()))
topics_to_assess = by_cat[selected_cat][:5]
st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

QS = {"Beginner":["Can you explain the basic concept?","Have you done at least one practice?","Could you teach the basics to someone?"],
      "Intermediate":["Can you apply this in a project?","Solved 3+ problems with this skill?","Understand advanced concepts?"],
      "Advanced":["Built something significant with this?","Can you mentor others?","Know edge cases and best practices?"]}

scores = {}
for t in topics_to_assess:
    is_done = t["topic"] in done
    st.markdown(f'<div style="background:{"#f0fdf4" if is_done else "#f8fafc"};border:1.5px solid {"#bbf7d0" if is_done else "#e2e8f0"};border-radius:12px;padding:14px;margin:10px 0"><div style="font-size:.9rem;font-weight:600;color:#0f172a;margin-bottom:10px">{"✅" if is_done else "📖"} {t["topic"]}</div>', unsafe_allow_html=True)
    qs = QS.get(t.get("level","Beginner"), QS["Beginner"])
    score = 0
    for q in qs:
        if st.checkbox(q, key=f"q_{t['id']}_{q[:15]}", value=is_done): score += 1
    scores[t["topic"]] = score
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

_, bc, _ = st.columns([2,2,2])
with bc:
    if st.button("✅ Submit Assessment", use_container_width=True):
        newly = sum(1 for tn,sc in scores.items() if sc >= 3 and tn not in done and not toggle_topic(st.session_state.name, age, tn))
        st.markdown(f'<div class="asuc">🎉 {newly if newly else "No new"} topic(s) marked complete!</div>', unsafe_allow_html=True)
        if newly: st.rerun()