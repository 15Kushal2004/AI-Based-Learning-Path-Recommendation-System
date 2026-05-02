import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
from collections import defaultdict
from core.engine import get_user, toggle_topic, get_resources, CLUSTERS
from core.sidebar import render_sidebar
from utils.firebase_storage import get_user_by_uid, toggle_topic_firestore

st.set_page_config(page_title="Skill Roadmap", page_icon="🗺️",
                   layout="wide", initial_sidebar_state="expanded")

# ── INJECT PREMIUM CSS ──────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:4px;letter-spacing:-0.03em">🗺️ Skill Roadmap</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:var(--text-muted);font-size:.84rem;margin-bottom:20px">Your complete learning journey — every topic, every week</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res     = st.session_state.result
if not isinstance(res, dict):
    st.info("No active roadmap is available right now. Generate a new roadmap from the Dashboard.")
    st.stop()
roadmap = res.get("roadmap", [])
if not roadmap:
    st.info("No active roadmap is available right now. Generate a new roadmap from the Dashboard.")
    st.stop()
age     = st.session_state.get("age", 22)
domain  = res.get("domain", "Education")
uid     = st.session_state.get("user_uid")
if uid:
    try:
        user = get_user_by_uid(uid)
    except Exception:
        user = {}
else:
    user = get_user(st.session_state.name, age)
done    = user.get("completed", [])

tab1, tab2, tab3 = st.tabs(["Step-by-Step Plan", "Node Graph", "Resources"])

with tab1:
    lbadge = {"Beginner":'<span class="lbeg">BEG</span>',
               "Intermediate":'<span class="lint">INT</span>',
               "Advanced":'<span class="ladv">ADV</span>'}
    cw = 0
    for s in roadmap:
        if s["week"] != cw:
            cw = s["week"]
            wh = sum(t["duration"] for t in roadmap if t["week"]==cw)
            st.markdown(f'<div class="wk">Week {cw} · {wh:.1f}h</div>', unsafe_allow_html=True)
        is_done = s["topic"] in done
        c1, c2 = st.columns([0.045, 0.955])
        with c1:
            chk = st.checkbox("", value=is_done, key=f"r2_{s['step']}", label_visibility="collapsed")
            if chk != is_done:
                if uid:
                    try:
                        toggle_topic_firestore(uid, s["topic"])
                    except Exception:
                        st.warning("Could not save progress to cloud. Please try again.")
                else:
                    toggle_topic(st.session_state.name, age, s["topic"])
                st.rerun()
        with c2:
            dn = "done" if is_done else ""
            st.markdown(f"""
            <div class="trow {dn}">
              <div class="tstep">#{s['step']:02d}</div>
              {lbadge.get(s.get('level','Beginner'),'')}
              <div class="tname {dn}">{s['topic']}</div>
              <div class="tcat">{s.get('category','')}</div>
              <div class="tdur">{s['duration']}h</div>
            </div>""", unsafe_allow_html=True)

with tab2:
    st.info("Node tree: Root → Weeks → Topics. Green = completed.")
    weeks_m = defaultdict(list)
    for t in roadmap: weeks_m[t["week"]].append(t)
    swks = sorted(weeks_m.keys())
    if not swks:
        st.info("No roadmap nodes to display yet.")
        st.stop()
    NW,NH,HG,VG,MR = 170,40,28,65,4
    mc = max(min(len(weeks_m[w]),MR) for w in swks)
    SW = max(60 + mc*NW + (mc-1)*HG + 60, 680)
    nodes=[]; prev=[(SW//2, 68)]; cy=68+55
    lcols={"Beginner":"#10b981","Intermediate":"#6366f1","Advanced":"#f59e0b"}
    nodes.append(f'<rect x="{SW//2-65}" y="32" width="130" height="36" rx="18" fill="#6366f1" filter="url(#sh)"/>')
    nodes.append(f'<text x="{SW//2}" y="55" text-anchor="middle" font-family="Inter" font-size="12.5" font-weight="700" fill="white">Learning Path</text>')
    for wk in swks:
        tops=weeks_m[wk]; wx,wy=SW//2,cy
        nodes.append(f'<rect x="{wx-52}" y="{wy-13}" width="104" height="26" rx="13" fill="rgba(99,102,241,0.15)" stroke="rgba(99,102,241,0.3)" stroke-width="1.5"/>')
        nodes.append(f'<text x="{wx}" y="{wy+4}" text-anchor="middle" font-family="Inter" font-size="11" font-weight="700" fill="#a5b4fc">Week {wk}</text>')
        for px,py in prev: nodes.append(f'<line x1="{px}" y1="{py}" x2="{wx}" y2="{wy-13}" stroke="rgba(99,102,241,0.3)" stroke-width="1.5" stroke-dasharray="4,3"/>')
        cy=wy+26+26; rows=[tops[i:i+MR] for i in range(0,len(tops),MR)]; wb=[]
        for row in rows:
            rn=len(row); rw=rn*NW+(rn-1)*HG; sx=(SW-rw)//2; ry=cy
            for ci,t in enumerate(row):
                nx_=sx+ci*(NW+HG); ny_=ry; cx_=nx_+NW//2
                id_=t["topic"] in done
                col="#64748b" if id_ else lcols.get(t.get("level","Beginner"),"#6366f1")
                fill="rgba(34,197,94,0.12)" if id_ else "rgba(255,255,255,0.04)"
                nodes.append(f'<line x1="{wx}" y1="{wy+13}" x2="{cx_}" y2="{ny_}" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"/>')
                tick="✓ " if id_ else ""; nm=t["topic"][:20]+("…" if len(t["topic"])>20 else "")
                nodes.append(f'<rect x="{nx_}" y="{ny_}" width="{NW}" height="{NH}" rx="8" fill="{fill}" stroke="{col}" stroke-width="1.8" filter="url(#sh)"/>')
                nodes.append(f'<circle cx="{nx_+12}" cy="{ny_+NH//2}" r="4" fill="{col}"/>')
                nodes.append(f'<text x="{nx_+22}" y="{ny_+14}" font-family="Inter" font-size="10" font-weight="600" fill="{"#64748b" if id_ else "#e2e8f0"}">{tick}{nm}</text>')
                nodes.append(f'<text x="{nx_+22}" y="{ny_+27}" font-family="Inter" font-size="9" fill="rgba(255,255,255,0.35)">{t["duration"]}h · {t.get("category","")[:13]}</text>')
                wb.append((cx_, ny_+NH))
            cy=ry+NH+18
        prev=wb[:MR]; cy+=VG-18
    SH=cy+50
    svg=f"""<svg width="100%" viewBox="0 0 {SW} {SH}" xmlns="http://www.w3.org/2000/svg">
    <defs><filter id="sh"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-opacity="0.2"/></filter></defs>
    <rect width="{SW}" height="{SH}" fill="#0d1117" rx="12"/>{''.join(nodes)}</svg>"""
    st.markdown(f'<div style="overflow:auto;background:#0d1117;border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:12px">{svg}</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("**Click any resource to open it directly →**")
    for s in roadmap[:12]:
        with st.expander(f"{'✅' if s['topic'] in done else '📖'} {s['topic']} ({s['duration']}h)"):
            for r in get_resources(s["topic"], domain, s.get("level","Beginner")):
                st.markdown(f"""
                <div class="res">
                  <span style="font-size:1.2rem">{r['icon']}</span>
                  <div>
                    <div style="font-size:.83rem;font-weight:600;color:var(--text)">{r['title']}</div>
                    <div style="font-size:.71rem;color:var(--text-muted)">{r['desc']} · {r['platform']}</div>
                  </div>
                  <a href="{r['url']}" target="_blank" class="res-btn">Open →</a>
                </div>""", unsafe_allow_html=True)
