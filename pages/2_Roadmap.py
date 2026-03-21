import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
from collections import defaultdict
from core.engine import get_user, toggle_topic, get_resources, CLUSTERS
from core.sidebar import render_sidebar

st.set_page_config(page_title="Skill Roadmap", page_icon="🗺️",
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

.wk { display: inline-flex; align-items: center; gap: 6px; background: linear-gradient(135deg,#ede9fe,#ddd6fe); border: 1px solid #c4b5fd; border-radius: 8px; padding: 5px 14px; margin: 10px 0 5px; font-family: 'Plus Jakarta Sans',sans-serif; font-size: .78rem; font-weight: 700; color: #5b21b6; }

.trow { display: flex; align-items: center; gap: 10px; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 9px 13px; margin: 4px 0; }
.trow.done { background: #f0fdf4; border-color: #bbf7d0; }
.tstep { background: #ede9fe; color: #6d28d9; font-size: .65rem; font-weight: 800; width: 22px; height: 22px; border-radius: 5px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tname { flex: 1; font-size: .84rem; font-weight: 500; color: #1e293b; }
.tname.done { text-decoration: line-through; color: #94a3b8; }
.tcat { background: #e0e7ff; color: #4338ca; font-size: .64rem; font-weight: 600; padding: 2px 7px; border-radius: 4px; }
.tdur { font-size: .73rem; font-weight: 700; color: #8b5cf6; min-width: 30px; text-align: right; }

.lbeg { background: #dcfce7; color: #15803d; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
.lint { background: #dbeafe; color: #1d4ed8; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
.ladv { background: #fef3c7; color: #b45309; font-size: .6rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; }

.res { display: flex; align-items: center; gap: 12px; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 10px 14px; margin: 7px 0; }
.res-btn { background: linear-gradient(135deg,#6366f1,#8b5cf6); color: white; border: none; border-radius: 7px; padding: 5px 12px; font-size: .7rem; font-weight: 600; text-decoration: none; flex-shrink: 0; margin-left: auto; }
</style>
""", unsafe_allow_html=True)

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.6rem;font-weight:800;color:#0f172a;margin-bottom:4px">🗺️ Skill Roadmap</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:.86rem;margin-bottom:20px">Your complete learning journey — every topic, every week</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("ℹ️ Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res     = st.session_state.result
roadmap = res["roadmap"]
age     = st.session_state.get("age", 22)
domain  = res["domain"]
user    = get_user(st.session_state.name, age)
done    = user.get("completed", [])

tab1, tab2, tab3 = st.tabs(["📋 Full Plan", "🌐 Node Graph", "🔗 Resources"])

with tab1:
    lbadge = {"Beginner":'<span class="lbeg">BEG</span>',
               "Intermediate":'<span class="lint">INT</span>',
               "Advanced":'<span class="ladv">ADV</span>'}
    cw = 0
    for s in roadmap:
        if s["week"] != cw:
            cw = s["week"]
            wh = sum(t["duration"] for t in roadmap if t["week"]==cw)
            st.markdown(f'<div class="wk">📅 Week {cw} · {wh:.1f}h</div>', unsafe_allow_html=True)
        is_done = s["topic"] in done
        c1, c2 = st.columns([0.045, 0.955])
        with c1:
            chk = st.checkbox("", value=is_done, key=f"r2_{s['step']}", label_visibility="collapsed")
            if chk != is_done:
                toggle_topic(st.session_state.name, age, s["topic"]); st.rerun()
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
    st.info("🌐 Node tree: Root → Weeks → Topics. Green = completed.")
    weeks_m = defaultdict(list)
    for t in roadmap: weeks_m[t["week"]].append(t)
    swks = sorted(weeks_m.keys())
    NW,NH,HG,VG,MR = 170,40,28,65,4
    mc = max(min(len(weeks_m[w]),MR) for w in swks)
    SW = max(60 + mc*NW + (mc-1)*HG + 60, 680)
    nodes=[]; prev=[(SW//2, 68)]; cy=68+55
    lcols={"Beginner":"#10b981","Intermediate":"#6366f1","Advanced":"#f59e0b"}
    nodes.append(f'<rect x="{SW//2-65}" y="32" width="130" height="36" rx="18" fill="#6366f1" filter="url(#sh)"/>')
    nodes.append(f'<text x="{SW//2}" y="55" text-anchor="middle" font-family="Inter" font-size="12.5" font-weight="700" fill="white">🧠 Learning Path</text>')
    for wk in swks:
        tops=weeks_m[wk]; wx,wy=SW//2,cy
        nodes.append(f'<rect x="{wx-52}" y="{wy-13}" width="104" height="26" rx="13" fill="#ede9fe" stroke="#c4b5fd" stroke-width="1.5"/>')
        nodes.append(f'<text x="{wx}" y="{wy+4}" text-anchor="middle" font-family="Inter" font-size="11" font-weight="700" fill="#6d28d9">Week {wk}</text>')
        for px,py in prev: nodes.append(f'<line x1="{px}" y1="{py}" x2="{wx}" y2="{wy-13}" stroke="#c4b5fd" stroke-width="1.5" stroke-dasharray="4,3"/>')
        cy=wy+26+26; rows=[tops[i:i+MR] for i in range(0,len(tops),MR)]; wb=[]
        for row in rows:
            rn=len(row); rw=rn*NW+(rn-1)*HG; sx=(SW-rw)//2; ry=cy
            for ci,t in enumerate(row):
                nx_=sx+ci*(NW+HG); ny_=ry; cx_=nx_+NW//2
                id_=t["topic"] in done
                col="#94a3b8" if id_ else lcols.get(t.get("level","Beginner"),"#6366f1")
                fill="#f0fdf4" if id_ else "white"
                nodes.append(f'<line x1="{wx}" y1="{wy+13}" x2="{cx_}" y2="{ny_}" stroke="#ddd6fe" stroke-width="1.5"/>')
                tick="✓ " if id_ else ""; nm=t["topic"][:20]+("…" if len(t["topic"])>20 else "")
                nodes.append(f'<rect x="{nx_}" y="{ny_}" width="{NW}" height="{NH}" rx="8" fill="{fill}" stroke="{col}" stroke-width="1.8" filter="url(#sh)"/>')
                nodes.append(f'<circle cx="{nx_+12}" cy="{ny_+NH//2}" r="4" fill="{col}"/>')
                nodes.append(f'<text x="{nx_+22}" y="{ny_+14}" font-family="Inter" font-size="10" font-weight="600" fill="{"#94a3b8" if id_ else "#1e293b"}">{tick}{nm}</text>')
                nodes.append(f'<text x="{nx_+22}" y="{ny_+27}" font-family="Inter" font-size="9" fill="#94a3b8">{t["duration"]}h · {t.get("category","")[:13]}</text>')
                wb.append((cx_, ny_+NH))
            cy=ry+NH+18
        prev=wb[:MR]; cy+=VG-18
    SH=cy+50
    svg=f"""<svg width="100%" viewBox="0 0 {SW} {SH}" xmlns="http://www.w3.org/2000/svg">
    <defs><filter id="sh"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-opacity="0.07"/></filter></defs>
    <rect width="{SW}" height="{SH}" fill="#f8fafc" rx="12"/>{''.join(nodes)}</svg>"""
    st.markdown(f'<div style="overflow:auto;background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:14px;padding:12px">{svg}</div>', unsafe_allow_html=True)

with tab3:
    st.markdown("**Click any resource to open it directly →**")
    for s in roadmap[:12]:
        with st.expander(f"{'✅' if s['topic'] in done else '📖'} {s['topic']} ({s['duration']}h)"):
            for r in get_resources(s["topic"], domain, s.get("level","Beginner")):
                st.markdown(f"""
                <div class="res">
                  <span style="font-size:1.2rem">{r['icon']}</span>
                  <div>
                    <div style="font-size:.83rem;font-weight:600;color:#1e293b">{r['title']}</div>
                    <div style="font-size:.71rem;color:#64748b">{r['desc']} · {r['platform']}</div>
                  </div>
                  <a href="{r['url']}" target="_blank" class="res-btn">Open →</a>
                </div>""", unsafe_allow_html=True)