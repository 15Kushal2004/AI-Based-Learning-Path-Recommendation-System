import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.engine import get_user, load_users, save_users, make_uid, load_kb
from core.sidebar import render_sidebar
import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️",
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

name = st.session_state.get("name","Learner")
age  = st.session_state.get("age",22)

left, right = st.columns([1.5,1])
with left:
    st.markdown('<div class="card"><div class="card-title">👤 Profile Settings</div>', unsafe_allow_html=True)
    new_name = st.text_input("Display Name", value=name)
    new_goal = st.text_input("Learning Goal", value=st.session_state.get("goal",""))
    new_dom  = st.selectbox("Domain",["Education","Entrepreneurship","Health","Hobbies"],
                             index=["Education","Entrepreneurship","Health","Hobbies"].index(st.session_state.get("domain","Education")))
    new_hrs  = st.slider("Daily Hours", 0.5, 8.0, float(st.session_state.get("hrs",1.5)), 0.5)
    new_hlth = st.text_input("Health Condition", value=st.session_state.get("health",""))
    _, bc, _ = st.columns([2,2,2])
    with bc:
        if st.button("💾 Save Settings", use_container_width=True):
            st.session_state.update({"name":new_name,"goal":new_goal,"domain":new_dom,"hrs":new_hrs,"health":new_hlth})
            st.markdown('<div class="asuc">✅ Settings saved!</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title" style="color:#ef4444">⚠️ Danger Zone</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Progress"):
        db=load_users(); uid=make_uid(name,age)
        if uid in db: db[uid]["completed"]=[]; db[uid]["badges"]=[]; save_users(db)
        st.success("Progress cleared.")
    if st.button("🔄 Reset Roadmap"):
        st.session_state.update({"generated":False,"result":None}); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    kb = load_kb()
    st.markdown(f'<div class="card"><div class="card-title">ℹ️ System Info</div><div style="font-size:.82rem;color:#374151;line-height:1.8"><b>Version:</b> 2.0 Pro<br><b>Topics:</b> {sum(len(t) for d in kb.values() for t in d.values())}<br><b>Domains:</b> 4<br><b>AI Modules:</b> NetworkX · K-Means · TF-IDF · Rules<br><b>Storage:</b> Local JSON (SHA-256)</div></div>', unsafe_allow_html=True)
    if st.session_state.get("generated"):
        user=get_user(name,age); done=user.get("completed",[])
        st.markdown(f'<div class="card"><div class="card-title">📊 Your Stats</div><div style="font-size:.82rem;color:#374151;line-height:1.8"><b>Completed:</b> {len(done)}<br><b>Sessions:</b> {user.get("sessions",0)}<br><b>Badges:</b> {", ".join(user.get("badges",[])) or "None yet"}<br><b>Last Seen:</b> {user.get("last_seen","")[:10]}</div></div>', unsafe_allow_html=True)