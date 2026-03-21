import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from collections import defaultdict
from core.engine import get_all_users_summary, load_kb
from core.sidebar import render_sidebar
import streamlit as st

st.set_page_config(page_title="Analytics", page_icon="📉",
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

.pb { background: #f1f5f9; border-radius: 6px; height: 7px; overflow: hidden; }
.pbf { height: 100%; border-radius: 6px; }

.skrow { margin-bottom: 11px; }
.sktop { display: flex; justify-content: space-between; margin-bottom: 3px; }
.skname { font-size: .78rem; font-weight: 500; color: #374151; display: flex; align-items: center; gap: 6px; }
.skpct { font-size: .78rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.6rem;font-weight:800;color:#0f172a;margin-bottom:4px">📉 Analytics</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:.86rem;margin-bottom:20px">Your personal learning statistics</p>', unsafe_allow_html=True)

kb = load_kb()
current_user_name = st.session_state.get("name", "Learner")
current_user_age = st.session_state.get("age", 22)
all_users = get_all_users_summary()

# Filter to show only current user's data
users = [u for u in all_users if u.get("display_name") == current_user_name]
total_t = sum(len(t) for d in kb.values() for t in d.values())

c1,c2,c3,c4 = st.columns(4)
for col,(lbl,val,bg) in zip([c1,c2,c3,c4],[
    ("Learners",len(users),"#ede9fe"),("Topics in KB",total_t,"#d1fae5"),
    ("Topics Completed",sum(len(u.get("completed",[])) for u in users),"#fef3c7"),
    ("Total Sessions",sum(u.get("sessions",0) for u in users),"#fce7f3")]):
    col.markdown(f'<div class="card" style="text-align:center"><div style="font-size:1.8rem;font-weight:800;color:#6366f1">{val}</div><div style="font-size:.75rem;color:#64748b">{lbl}</div></div>', unsafe_allow_html=True)

if users:
    user = users[0]  # Current user's data
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📊 Your Statistics for {user.get("domain", "")} Domain</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Topics in Domain", user.get("total_topics", 0))
    col2.metric("Topics Completed", len(user.get("completed", [])))
    col3.metric("Sessions", user.get("sessions", 0))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">📈 Your Learning Info</div>', unsafe_allow_html=True)
    
    info_text = f"""<div style="font-size:.82rem;color:#374151;line-height:1.8">
    <b>Skill Level:</b> {user.get('skill', 'Beginner')}<br>
    <b>Goal:</b> {user.get('goal', 'Not set')}<br>
    <b>Learning Hours/Day:</b> {user.get('hrs', 1.5)}<br>
    <b>Last Seen:</b> {user.get('last_seen', 'Never')[:10]}<br>
    <b>Badges Earned:</b> {', '.join(user.get('badges', [])) or 'None yet'}
    </div>"""
    st.markdown(info_text, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("ℹ️ Generate a roadmap from the **Dashboard** first to see your analytics.")