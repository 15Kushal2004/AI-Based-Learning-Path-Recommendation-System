import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import datetime
from core.engine import get_user
from core.sidebar import render_sidebar
from utils.firebase_storage import get_user_by_uid
from utils.certificate import generate_certificate_image, certificate_image_filename
import streamlit as st

st.set_page_config(page_title="Certificates", page_icon="🏅",
                   layout="wide", initial_sidebar_state="expanded")

# ── INJECT PREMIUM CSS ──────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:4px;letter-spacing:-0.03em">🏅 Certificates</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:var(--text-muted);font-size:.84rem;margin-bottom:20px">Earn certificates as you complete your roadmap</p>', unsafe_allow_html=True)

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
res["domain"] = res.get("domain", "Education")
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
pct  = round(len(done)/max(len(roadmap),1)*100)
name = st.session_state.get("name","Learner")
goal = st.session_state.get("goal", "")

certs=[("Beginner","🥉","#d97706",25),("Intermediate","🥈","#6b7280",50),
       ("Advanced","🥇","#f59e0b",75),("Expert","🏆","#6366f1",100)]
for title,icon,color,req in certs:
    earned = pct >= req
    st.markdown(f"""
    <div style="background:{"rgba(245,158,11,0.08)" if earned else "var(--bg-card)"};border:1px solid {color+("44" if earned else "22")};border-radius:var(--radius);padding:22px;margin:10px 0;display:flex;align-items:center;gap:20px;transition:all 0.15s ease;backdrop-filter:blur(10px)">
      <div style="font-size:2.5rem">{icon}</div>
      <div style="flex:1">
        <div style="font-size:1.05rem;font-weight:700;color:var(--text);font-family:var(--font-display);letter-spacing:-0.02em">{title} Certificate</div>
        <div style="font-size:.82rem;color:var(--text-secondary);margin:4px 0">Complete {req}% of your {res.get("domain", "Education")} roadmap</div>
        <div style="font-size:.75rem;color:{color};font-weight:600">Learner: {name} · Domain: {res["domain"]}</div>
      </div>
      <div style="text-align:right;min-width:130px">
        <div style="font-size:.7rem;color:var(--text-muted);margin-bottom:4px">Progress: {min(pct,req)}/{req}%</div>
        <div class="pb" style="width:120px;margin-bottom:8px">
          <div class="pbf" style="background:{color};width:{min(pct,req)/req*100:.0f}%"></div>
        </div>
        <div style="background:{"linear-gradient(135deg,"+color+","+color+"bb)" if earned else "var(--bg-subtle)"};color:{"white" if earned else "var(--text-muted)"};padding:6px 14px;border-radius:6px;font-size:.75rem;font-weight:600;text-align:center">
          {"🏅 EARNED" if earned else "🔒 Locked"}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    if earned:
      image_data = generate_certificate_image(
        name=name,
        domain=res.get("domain", "Education"),
        goal=goal,
        title=title,
        progress_pct=pct,
        issue_date=str(datetime.date.today()),
      )

      st.download_button(
        f"Download {title} Certificate",
        image_data,
        certificate_image_filename(name, title),
        "image/png",
        key=f"dl_img_{req}",
      )
