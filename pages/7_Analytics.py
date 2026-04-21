import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from collections import defaultdict
from core.engine import get_all_users_summary, load_kb
from core.sidebar import render_sidebar
import streamlit as st

st.set_page_config(page_title="Analytics", page_icon="📉",
                   layout="wide", initial_sidebar_state="expanded")

# ── INJECT PREMIUM CSS ──────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:4px;letter-spacing:-0.03em">📉 Analytics</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:var(--text-muted);font-size:.84rem;margin-bottom:20px">Your personal learning statistics</p>', unsafe_allow_html=True)

kb = load_kb()
current_user_name = st.session_state.get("name", "Learner")
current_user_age = st.session_state.get("age", 22)
all_users = get_all_users_summary()

# Filter to show only current user's data
users = [u for u in all_users if u.get("display_name") == current_user_name]
total_t = sum(len(t) for d in kb.values() for t in d.values())

c1,c2,c3,c4 = st.columns(4)
for col,(lbl,val,bg) in zip([c1,c2,c3,c4],[
    ("Learners",len(users),"rgba(99,102,241,0.12)"),("Topics in KB",total_t,"rgba(34,197,94,0.12)"),
    ("Topics Completed",sum(len(u.get("completed",[])) for u in users),"rgba(245,158,11,0.12)"),
    ("Total Sessions",sum(u.get("sessions",0) for u in users),"rgba(236,72,153,0.12)")]):
    col.markdown(f'<div class="card" style="text-align:center"><div style="font-size:1.75rem;font-weight:700;color:var(--accent-light);font-family:var(--font-display);letter-spacing:-0.03em">{val}</div><div style="font-size:.72rem;color:var(--text-muted);font-weight:500">{lbl}</div></div>', unsafe_allow_html=True)

if users:
    user = users[0]  # Current user's data

    st.markdown(f'<div class="card-title">📊 Your Statistics for {user.get("domain", "")} Domain</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Topics in Domain", user.get("total_topics", 0))
    col2.metric("Topics Completed", len(user.get("completed", [])))
    col3.metric("Sessions", user.get("sessions", 0))
    

    

    st.markdown(f'<div class="card-title">📈 Your Learning Info</div>', unsafe_allow_html=True)
    
    info_text = f"""<div style="font-size:.82rem;color:var(--text-secondary);line-height:1.8">
    <b>Skill Level:</b> {user.get('skill', 'Beginner')}<br>
    <b>Goal:</b> {user.get('goal', 'Not set')}<br>
    <b>Learning Hours/Day:</b> {user.get('hrs', 1.5)}<br>
    <b>Last Seen:</b> {user.get('last_seen', 'Never')[:10]}<br>
    <b>Badges Earned:</b> {', '.join(user.get('badges', [])) or 'None yet'}
    </div>"""
    st.markdown(info_text, unsafe_allow_html=True)

else:
    st.info("Generate a roadmap from the **Dashboard** first to see your analytics.")