import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collections import defaultdict
from core.engine import get_user, CLUSTERS
from core.sidebar import render_sidebar
import pandas as pd
import streamlit as st

st.set_page_config(page_title="My Progress", page_icon="📈",
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

st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.6rem;font-weight:800;color:#0f172a;margin-bottom:4px">📈 My Progress</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:.86rem;margin-bottom:20px">Track your learning journey</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("ℹ️ Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res    = st.session_state.result
roadmap= res["roadmap"]
age    = st.session_state.get("age",22)
user   = get_user(st.session_state.name, age)
done   = user.get("completed",[])
badges = user.get("badges",[])
pct    = round(len(done)/max(len(roadmap),1)*100)
cinfo  = res["cinfo"]

c1,c2,c3,c4 = st.columns(4)
for col,(lbl,val,bg) in zip([c1,c2,c3,c4],[
    ("Completed",len(done),"#d1fae5"),("Streak Days",user.get("streak_days",1),"#ede9fe"),
    ("Sessions",user.get("sessions",1),"#fef3c7"),("Badges",len(badges),"#fce7f3")]):
    col.markdown(f'<div class="card" style="text-align:center"><div style="font-size:1.8rem;font-weight:800;color:#6366f1">{val}</div><div style="font-size:.75rem;color:#64748b">{lbl}</div></div>', unsafe_allow_html=True)

left, right = st.columns([1.5,1])
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">Overall Progress — {pct}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pb" style="height:14px;margin:8px 0"><div class="pbf" style="width:{pct}%;background:{cinfo["color"]}"></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:.78rem;color:#64748b">{len(done)} of {len(roadmap)} topics · {sum(t["duration"] for t in roadmap if t["topic"] in done):.0f}h of {res["total_h"]}h</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    cat_h=defaultdict(float); cat_done=defaultdict(float)
    for t in roadmap:
        c=t.get("category","General"); cat_h[c]+=t["duration"]
        if t["topic"] in done: cat_done[c]+=t["duration"]
    colors=["#6366f1","#10b981","#f59e0b","#ec4899","#0ea5e9","#8b5cf6","#14b8a6","#f97316"]
    for i,(cat,h) in enumerate(sorted(cat_h.items(),key=lambda x:-x[1])):
        dp=round(cat_done[cat]/h*100) if h>0 else 0; c=colors[i%len(colors)]
        st.markdown(f'<div class="skrow"><div class="sktop"><span class="skname"><span style="width:8px;height:8px;border-radius:50%;background:{c};display:inline-block"></span>{cat}</span><span class="skpct" style="color:{c}">{dp}%</span></div><div class="pb"><div class="pbf" style="width:{dp}%;background:{c}"></div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if done:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">✅ Completed ({len(done)})</div>', unsafe_allow_html=True)
        for d in done:
            st.markdown(f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:7px 12px;margin:4px 0;font-size:.82rem;color:#14532d">✓ {d}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown(f'<div class="card" style="background:{cinfo["bg"]};border-color:{cinfo["color"]}44"><div style="font-size:1.6rem">{cinfo["icon"]}</div><div style="font-weight:700;color:{cinfo["color"]}">{cinfo["name"]}</div><div style="font-size:.78rem;color:#64748b">{cinfo["desc"]}</div></div>', unsafe_allow_html=True)
    all_badges=[("First 5","5 topics",len(done)>=5,"🥉"),("10 Topics","10 topics",len(done)>=10,"🥈"),
                ("25 Topics","25 topics",len(done)>=25,"🥇"),("Halfway","50% done",pct>=50,"⭐"),("Champion","100%!",pct>=100,"🏆")]
    st.markdown('<div class="card"><div class="card-title">🏅 Badges</div>', unsafe_allow_html=True)
    for nm,desc,earned,icon in all_badges:
        bg="#fef3c7" if earned else "#f1f5f9"; tc="#92400e" if earned else "#94a3b8"
        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;background:{bg};border-radius:10px;padding:9px 12px;margin:5px 0"><span style="font-size:1.2rem">{icon}</span><div><div style="font-size:.8rem;font-weight:600;color:{tc}">{nm}</div><div style="font-size:.7rem;color:#94a3b8">{desc}</div></div><div style="margin-left:auto;font-size:.7rem;font-weight:700;color:{"#10b981" if earned else "#94a3b8"}">{"✓ Earned" if earned else "🔒 Locked"}</div></div>', unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
for col,(lbl,val,bg) in zip([c1,c2,c3,c4],[
    ("Completed",len(done),"#d1fae5"),("Streak Days",user.get("streak_days",1),"#ede9fe"),
    ("Sessions",user.get("sessions",1),"#fef3c7"),("Badges",len(badges),"#fce7f3")]):
    col.markdown(f'<div class="card" style="text-align:center"><div style="font-size:1.8rem;font-weight:800;color:#6366f1">{val}</div><div style="font-size:.75rem;color:#64748b">{lbl}</div></div>', unsafe_allow_html=True)

left, right = st.columns([1.5,1])
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">Overall Progress — {pct}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pb" style="height:14px;margin:8px 0"><div class="pbf" style="width:{pct}%;background:{cinfo["color"]}"></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:.78rem;color:#64748b">{len(done)} of {len(roadmap)} topics · {sum(t["duration"] for t in roadmap if t["topic"] in done):.0f}h of {res["total_h"]}h</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    cat_h=defaultdict(float); cat_done=defaultdict(float)
    for t in roadmap:
        c=t.get("category","General"); cat_h[c]+=t["duration"]
        if t["topic"] in done: cat_done[c]+=t["duration"]
    colors=["#6366f1","#10b981","#f59e0b","#ec4899","#0ea5e9","#8b5cf6","#14b8a6","#f97316"]
    for i,(cat,h) in enumerate(sorted(cat_h.items(),key=lambda x:-x[1])):
        dp=round(cat_done[cat]/h*100) if h>0 else 0; c=colors[i%len(colors)]
        st.markdown(f'<div class="skrow"><div class="sktop"><span class="skname"><span style="width:8px;height:8px;border-radius:50%;background:{c};display:inline-block"></span>{cat}</span><span class="skpct" style="color:{c}">{dp}%</span></div><div class="pb"><div class="pbf" style="width:{dp}%;background:{c}"></div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if done:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">✅ Completed ({len(done)})</div>', unsafe_allow_html=True)
        for d in done:
            st.markdown(f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:7px 12px;margin:4px 0;font-size:.82rem;color:#14532d">✓ {d}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown(f'<div class="card" style="background:{cinfo["bg"]};border-color:{cinfo["color"]}44"><div style="font-size:1.6rem">{cinfo["icon"]}</div><div style="font-weight:700;color:{cinfo["color"]}">{cinfo["name"]}</div><div style="font-size:.78rem;color:#64748b">{cinfo["desc"]}</div></div>', unsafe_allow_html=True)
    all_badges=[("First 5","5 topics",len(done)>=5,"🥉"),("10 Topics","10 topics",len(done)>=10,"🥈"),
                ("25 Topics","25 topics",len(done)>=25,"🥇"),("Halfway","50% done",pct>=50,"⭐"),("Champion","100%!",pct>=100,"🏆")]
    st.markdown('<div class="card"><div class="card-title">🏅 Badges</div>', unsafe_allow_html=True)
    for nm,desc,earned,icon in all_badges:
        bg="#fef3c7" if earned else "#f1f5f9"; tc="#92400e" if earned else "#94a3b8"
        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;background:{bg};border-radius:10px;padding:9px 12px;margin:5px 0"><span style="font-size:1.2rem">{icon}</span><div><div style="font-size:.8rem;font-weight:600;color:{tc}">{nm}</div><div style="font-size:.7rem;color:#94a3b8">{desc}</div></div><div style="margin-left:auto;font-size:.7rem;font-weight:700;color:{"#10b981" if earned else "#94a3b8"}">{"✓ Earned" if earned else "🔒 Locked"}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)