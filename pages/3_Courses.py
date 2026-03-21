import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collections import defaultdict
from core.engine import get_user, toggle_topic, get_resources
from core.sidebar import render_sidebar
import streamlit as st

st.set_page_config(page_title="My Courses", page_icon="📚",
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

.lbeg { background: #dcfce7; color: #15803d; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
.lint { background: #dbeafe; color: #1d4ed8; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
.ladv { background: #fef3c7; color: #b45309; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }

.res { display: flex; align-items: center; gap: 12px; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 10px 14px; margin: 7px 0; }
.res-btn { background: linear-gradient(135deg,#6366f1,#8b5cf6); color: white; border: none; border-radius: 7px; padding: 5px 12px; font-size: .7rem; font-weight: 600; text-decoration: none; flex-shrink: 0; margin-left: auto; }
</style>
""", unsafe_allow_html=True)

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.6rem;font-weight:800;color:#0f172a;margin-bottom:4px">📚 My Courses</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:.86rem;margin-bottom:20px">Browse all topics by category</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("ℹ️ Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res = st.session_state.result
roadmap = res["roadmap"]
domain  = res["domain"]
age     = st.session_state.get("age",22)
user    = get_user(st.session_state.name, age)
done    = user.get("completed",[])

by_cat = defaultdict(list)
for t in roadmap: by_cat[t.get("category","General")].append(t)

c1,c2,c3,c4 = st.columns(4)
for col, (label, val, bg) in zip([c1,c2,c3,c4],[
    ("Total Topics",len(roadmap),"#ede9fe"),
    ("Completed",len(done),"#d1fae5"),
    ("Categories",len(by_cat),"#fef3c7"),
    ("Hours Done",f"{sum(t['duration'] for t in roadmap if t['topic'] in done):.0f}h","#fce7f3")]):
    col.markdown(f'<div class="card" style="text-align:center"><div style="font-size:1.8rem;font-weight:800;color:#6366f1">{val}</div><div style="font-size:.75rem;color:#64748b">{label}</div></div>', unsafe_allow_html=True)

lbadge = {"Beginner":'<span class="lbeg">BEG</span>',"Intermediate":'<span class="lint">INT</span>',"Advanced":'<span class="ladv">ADV</span>'}
for cat, topics in sorted(by_cat.items()):
    dn_count = len([t for t in topics if t["topic"] in done])
    with st.expander(f"📁 {cat}  ·  {dn_count}/{len(topics)} done"):
        for t in topics:
            is_done = t["topic"] in done
            c1,c2 = st.columns([0.045,0.955])
            with c1:
                chk = st.checkbox("",value=is_done,key=f"c3_{t['id']}",label_visibility="collapsed")
                if chk != is_done: toggle_topic(st.session_state.name,age,t["topic"]); st.rerun()
            with c2:
                dn="done" if is_done else ""
                st.markdown(f'<div class="trow {dn}" style="display:flex;align-items:center;gap:10px;background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:9px 13px"><div style="background:#ede9fe;color:#6d28d9;font-size:.65rem;font-weight:800;width:22px;height:22px;border-radius:5px;display:flex;align-items:center;justify-content:center;flex-shrink:0">#{t.get("step","?")}</div>{lbadge.get(t.get("level","Beginner"),"")}<div style="flex:1;font-size:.84rem;font-weight:500;color:#1e293b;text-decoration:{"line-through" if is_done else "none"};color:{"#94a3b8" if is_done else "#1e293b"}">{t["topic"]}</div><div style="font-size:.73rem;font-weight:700;color:#8b5cf6;min-width:30px;text-align:right">{t["duration"]}h</div></div>', unsafe_allow_html=True)
        with st.expander("🔗 Resources for this category"):
            for r in get_resources(topics[0]["topic"], domain, topics[0].get("level","Beginner"))[:2]:
                st.markdown(f'<div class="res"><span style="font-size:1.2rem">{r["icon"]}</span><div><div style="font-size:.83rem;font-weight:600">{r["title"]}</div><div style="font-size:.71rem;color:#64748b">{r["platform"]}</div></div><a href="{r["url"]}" target="_blank" class="res-btn">Open →</a></div>', unsafe_allow_html=True)