import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.engine import get_user, load_users, save_users, make_uid, load_kb
from core.sidebar import render_sidebar
from utils.firebase_storage import (
    clear_user_progress_firestore,
    clear_user_roadmaps_firestore,
    get_user_by_uid,
)
import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️",
                   layout="wide", initial_sidebar_state="expanded")

# ── INJECT PREMIUM CSS ──────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

name = st.session_state.get("name","Learner")
age  = st.session_state.get("age",22)

if "confirm_clear_progress" not in st.session_state:
    st.session_state["confirm_clear_progress"] = False
if "confirm_reset_roadmaps" not in st.session_state:
    st.session_state["confirm_reset_roadmaps"] = False


def clear_progress_data(current_name, current_age):
    """Clear user progress from local and Firebase storage."""
    # Clear local JSON progress
    db = load_users()
    local_uid = make_uid(current_name, current_age)
    if local_uid in db:
        db[local_uid]["completed"] = []
        db[local_uid]["badges"] = []
        save_users(db)

    # Clear Firebase progress for logged-in users
    firebase_uid = st.session_state.get("user_uid")
    firebase_cleared = False
    if firebase_uid:
        try:
            firebase_cleared = clear_user_progress_firestore(firebase_uid)
        except Exception:
            firebase_cleared = False

    if firebase_uid and not firebase_cleared:
        st.warning("Local progress cleared. Firebase clear failed, please try again.")
    else:
        st.success("Progress cleared successfully.")


def clear_all_saved_roadmaps():
    """Clear all saved roadmaps for the active account and local session."""
    firebase_uid = st.session_state.get("user_uid")
    if firebase_uid:
        try:
            ok = clear_user_roadmaps_firestore(firebase_uid)
        except Exception:
            ok = False
        if not ok:
            st.error("Could not clear saved roadmaps from your account.")
            return

    st.session_state["generated"] = False
    st.session_state["result"] = None
    st.session_state["all_roadmaps"] = []
    st.success("All saved roadmaps were removed.")

left, right = st.columns([1.5,1])
with left:
    st.markdown('<div class="card-title">👤 Profile Settings</div>', unsafe_allow_html=True)
    new_name = st.text_input("Display Name", value=name)
    new_goal = st.text_input("Learning Goal", value=st.session_state.get("goal",""))
    new_dom  = st.selectbox("Domain",["Education","Entrepreneurship","Health","Hobbies"],
                             index=["Education","Entrepreneurship","Health","Hobbies"].index(st.session_state.get("domain","Education")))
    new_hrs  = st.slider("Daily Hours", 0.5, 8.0, float(st.session_state.get("hrs",1.5)), 0.5)
    new_hlth = st.text_input("Health Condition", value=st.session_state.get("health",""))
    _, bc, _ = st.columns([2,2,2])
    with bc:
        if st.button("Save Settings", use_container_width=True):
            st.session_state.update({"name":new_name,"goal":new_goal,"domain":new_dom,"hrs":new_hrs,"health":new_hlth})
            st.markdown('<div class="asuc">✅ Settings saved successfully!</div>', unsafe_allow_html=True)

    
    st.markdown('<div class="card-title" style="color:var(--error)">⚠️ Danger Zone</div>', unsafe_allow_html=True)
    if st.button("Clear Progress"):
        st.session_state["confirm_clear_progress"] = True

    if st.session_state.get("confirm_clear_progress", False):
        st.markdown(
            '<div class="card" style="border:1px solid rgba(239,68,68,0.35);background:rgba(239,68,68,0.08)"><div class="card-title" style="color:#fca5a5">⚠️ Are you sure you want to clear your progress?</div><div style="font-size:.82rem;color:var(--text-secondary)">This will remove completed topics and badges from your account.</div></div>',
            unsafe_allow_html=True,
        )
        c1, c2, _ = st.columns([1.2, 1.2, 3])
        with c1:
            if st.button("Yes, Clear Progress", key="confirm_clear_progress_btn", use_container_width=True):
                clear_progress_data(name, age)
                st.session_state["confirm_clear_progress"] = False
                st.rerun()
        with c2:
            if st.button("Cancel", key="cancel_clear_progress_btn", use_container_width=True):
                st.session_state["confirm_clear_progress"] = False
                st.rerun()

    if st.button("Reset Roadmap"):
        st.session_state["confirm_reset_roadmaps"] = True

    if st.session_state.get("confirm_reset_roadmaps", False):
        st.markdown(
            '<div class="card" style="border:1px solid rgba(239,68,68,0.35);background:rgba(239,68,68,0.08)"><div class="card-title" style="color:#fca5a5">🗑️ Remove all saved roadmaps?</div><div style="font-size:.82rem;color:var(--text-secondary)">This will delete every roadmap saved in your account and clear your Courses history.</div></div>',
            unsafe_allow_html=True,
        )
        c1, c2, _ = st.columns([1.2, 1.2, 3])
        with c1:
            if st.button("Yes, Delete All", key="confirm_reset_roadmaps_btn", use_container_width=True):
                clear_all_saved_roadmaps()
                st.session_state["confirm_reset_roadmaps"] = False
                st.rerun()
        with c2:
            if st.button("Cancel", key="cancel_reset_roadmaps_btn", use_container_width=True):
                st.session_state["confirm_reset_roadmaps"] = False
                st.rerun()


with right:
    kb = load_kb()
    st.markdown(f'<div class="card"><div class="card-title">ℹ️ System Info</div><div style="font-size:.82rem;color:var(--text-secondary);line-height:1.8"><b>Version:</b> 2.0 Pro<br><b>Topics:</b> {sum(len(t) for d in kb.values() for t in d.values())}<br><b>Domains:</b> 4<br><b>AI Modules:</b> NetworkX · K-Means · TF-IDF · Rules<br><b>Storage:</b> Firebase + Local JSON</div></div>', unsafe_allow_html=True)
    if st.session_state.get("generated"):
        uid = st.session_state.get("user_uid")
        if uid:
            try:
                user = get_user_by_uid(uid)
            except Exception:
                user = {}
        else:
            user = get_user(name, age)
        done = user.get("completed",[])
        st.markdown(f'<div class="card"><div class="card-title">📊 Your Stats</div><div style="font-size:.82rem;color:var(--text-secondary);line-height:1.8"><b>Completed:</b> {len(done)}<br><b>Sessions:</b> {user.get("sessions",0)}<br><b>Badges:</b> {", ".join(user.get("badges",[])) or "None yet"}<br><b>Last Seen:</b> {user.get("last_seen","")[:10]}</div></div>', unsafe_allow_html=True)
