# ================================================================
#  app.py — Dashboard
#  Run: streamlit run app.py
# ================================================================
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
import pandas as pd
import json
from collections import defaultdict
from core.engine import (load_kb, generate_roadmap, upsert_user,
                          get_user, CLUSTERS, goal_domain_mismatch,
                          toggle_topic, get_all_users_summary)
from core.sidebar import render_sidebar
from utils.firebase_storage import (save_roadmap, get_user_by_uid,
                                      toggle_topic_firestore,
                                      get_all_users_firestore,
                                      get_all_user_roadmaps)

# Testing
import wandb
wandb.init(project="ai-learning-path", name="test-run")

st.set_page_config(
    page_title="LearnPath AI — Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── INJECT PREMIUM CSS ────────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)



# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── SESSION STATE ────────────────────────────────────────────
for k, v in [("generated", False), ("result", None), ("name", ""),
             ("goal", ""), ("domain", "Education"), ("age", 22),
             ("skill", "Beginner"), ("hrs", 1.5), ("health", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── IMPORT AND RENDER SIDEBAR ───────────────────────────────
render_sidebar()

# ── TOPBAR ───────────────────────────────────────────────────
name_d   = st.session_state.name or "Learner"
initials = "".join(w[0].upper() for w in name_d.split()[:2]) or "L"
goal_d   = st.session_state.goal or "No goal set"

# Top bar: feature badges + user pill
# 🔥 HEADER (FIXED ALIGNMENT)
col1, col2 = st.columns([5, 1])

with col1:
  st.markdown("""
<style>
.typing-small {
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  font-size: 2rem;
  font-weight: 600;

  border-right: 2px solid #8b5cf6;

  width: 0;
  animation: typing 3s steps(40, end) forwards,
             blink 0.8s infinite;
}

/* 🔥 IMPORTANT: width goes to exact characters */
@keyframes typing {
  from { width: 0 }
  to { width: 38ch; }   /* 🔥 CHANGE THIS */
}

@keyframes blink {
  50% { border-color: transparent }
}
</style>
""", unsafe_allow_html=True)
   
st.markdown("""
<div class="typing-small" style="margin-top:-30px;">
🎯 Make Your Learning Journey Personalized
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;">
        <div style="display:flex;align-items:center;gap:8px;
            background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:50px;
            padding:5px 14px 5px 5px;">
          <div style="width:32px;height:32px;border-radius:50%;
              background:linear-gradient(135deg,#6366f1,#818cf8);
              display:flex;align-items:center;justify-content:center;
              color:white;font-weight:600;font-size:.78rem">{initials}</div>
          <div>
            <div style="font-size:.8rem;font-weight:600;color:#e2e8f0">Hi, {name_d}</div>
            <div style="font-size:.66rem;color:rgba(255,255,255,0.35)">{goal_d[:25]}</div>
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


 
# Welcome section
st.markdown("""
<style>
.wave {
  display: inline-block;
  font-size: 1.7rem;
  transform-origin: 70% 70%;
  animation: waveReal 2.8s infinite;
}

/* 🔥 HUMAN-LIKE WAVE */
@keyframes waveReal {

  /* normal */
  0%   { transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 0px #8b5cf6); }

  /* 🔥 wave + glow */
  10%  { transform: rotate(20deg) scale(1.2); filter: drop-shadow(0 0 6px #8b5cf6); }
  20%  { transform: rotate(-12deg) scale(1.15); filter: drop-shadow(0 0 8px #8b5cf6); }
  30%  { transform: rotate(20deg) scale(1.2); filter: drop-shadow(0 0 10px #8b5cf6); }
  40%  { transform: rotate(-6deg) scale(1.1); filter: drop-shadow(0 0 6px #8b5cf6); }

  /* back to normal */
  50%  { transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 0px #8b5cf6); }

  /* pause */
  100% { transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 0px #8b5cf6); }
}
</style>
""", unsafe_allow_html=True)
st.markdown(f"""
<div style="font-family:var(--font-display);font-size:1.8rem;font-weight:700;color:#e2e8f0;">
Welcome, {name_d}! <span class="wave">👋</span>
</div>
""", unsafe_allow_html=True)




# ════════════════════════════════════════════════════════════
#  PROFILE FORM
# ════════════════════════════════════════════════════════════
kb = load_kb()

with st.container():

    st.markdown('<div class="card-title">📋 Complete Your Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-sub">Fill in your details — all fields are used by the AI to generate your perfect roadmap</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2, 0.8, 1.4, 1.6])
    with c1: name   = st.text_input("Full Name", placeholder="e.g. Arjun Sharma", value=st.session_state.name)
    with c2: age    = st.number_input("Age", 10, 90, int(st.session_state.age), 1)
    with c3:
        ag = "🧑 Young (15–30)" if age < 30 else ("👨 Adult (30–60)" if age < 60 else "👴 Senior (60+)")
        st.markdown(f"""
        <label style="display:block;margin-bottom:8px;color:rgba(255,255,255,0.5);font-size:.78rem;font-weight:600">Age Group</label>
        <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px 13px;color:#e2e8f0;font-size:.88rem;font-weight:500;margin-top:-8px;">{ag}</div>""", unsafe_allow_html=True)
    with c4:
        dom_list = ["Education","Entrepreneurship","Health","Hobbies"]
        domain   = st.selectbox("Domain", dom_list, index=dom_list.index(st.session_state.domain))

    c5, c6, c7, c8 = st.columns([2.5, 1.3, 1.3, 1.8])
    with c5: goal   = st.text_input("Learning Goal", placeholder="e.g. learn Python, lose weight, start a startup, learn guitar")
    with c6: skill  = st.selectbox("Current Skill Level", ["Beginner","Intermediate","Advanced"])
    with c7: hrs    = st.slider("Hours/Day", 0.5, 8.0, float(st.session_state.hrs), 0.5)
    with c8: health = st.text_input("Health Condition (optional)", placeholder="e.g. knee pain, diabetes")


# Goal-domain mismatch check
if goal.strip():
    mismatch, suggested = goal_domain_mismatch(goal, domain)
    if mismatch and suggested:
        st.markdown(f"""
        <div class="awarn">⚠️ <strong>Domain Mismatch!</strong> Your goal "<em>{goal}</em>" seems to match
        <strong>{suggested}</strong>, but you selected <strong>{domain}</strong>.
        Consider switching for better results.</div>""", unsafe_allow_html=True)
        ca, cb, _ = st.columns([1.2, 1.2, 4])
        with ca:
            if st.button(f"✅ Switch to {suggested}"):
                st.session_state.domain = suggested; st.rerun()
        with cb:
            st.button("Keep my selection")

# ── CENTERED GENERATE BUTTON ─────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
c_l, c_mid, c_r = st.columns([2, 2, 2])
with c_mid:
    gen = st.button("🚀 Generate My Learning Path →", use_container_width=True)

if gen:
    if not goal.strip():
        st.warning("⚠️ Please enter a learning goal.")
    else:
        with st.spinner("🔄 Building your personalised AI roadmap..."):
            result = generate_roadmap(name or "Learner", age, domain, goal, skill, hrs, health, kb)

        # ✅ 🔥 ADD W&B LOGGING HERE ONLY

        goal_match = 1 if domain in result.get("domain", "") else 0

        relevance = sum(
            1 for t in result["roadmap"]
            if any(word in t["topic"].lower() for word in goal.lower().split())
        ) / len(result["roadmap"])

        completion_rate = 0

        import wandb
        wandb.log({
            "goal_match": goal_match,
            "relevance_score": relevance,
            "completion_rate": completion_rate,
            "num_topics": len(result["roadmap"])
        })

        # ✅ existing logic
        st.session_state.update({
            "generated": True, "result": result,
            "name": name or "Learner", "goal": goal, "domain": domain,
            "age": age, "skill": skill, "hrs": hrs, "health": health
        })

        upsert_user(name or "Learner", age, domain, goal, skill, hrs, health, result["roadmap"])

        uid = st.session_state.get("user_uid")
        if uid:
            save_roadmap(uid, name or "Learner", age, domain, goal, skill, hrs, health, result)
            st.session_state["all_roadmaps"] = get_all_user_roadmaps(uid)

        st.rerun()



# ════════════════════════════════════════════════════════════
#  RESULTS
# ════════════════════════════════════════════════════════════
if not st.session_state.generated:
    # Landing overview
    total_kb  = sum(len(t) for d in kb.values() for t in d.values())
    try:
        all_users = get_all_users_firestore()
    except Exception:
        all_users = get_all_users_summary()
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-icon" style="background:rgba(139,92,246,0.15)">📚</div>
        <div class="stat-num">{total_kb}</div><div class="stat-lbl">Topics in Knowledge Base</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:rgba(34,197,94,0.15)">👥</div>
        <div class="stat-num">{len(all_users)}</div><div class="stat-lbl">Registered Learners</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:rgba(245,158,11,0.15)">🌐</div>
        <div class="stat-num">4</div><div class="stat-lbl">Domains</div></div>
      <div class="stat-card"><div class="stat-icon" style="background:rgba(236,72,153,0.15)">🤖</div>
        <div class="stat-num">5</div><div class="stat-lbl">AI Modules</div></div>
    </div>""", unsafe_allow_html=True)

    icons = {"Education":"🎓","Entrepreneurship":"💼","Health":"💪","Hobbies":"🎨"}
    clrs  = {"Education":"#6366f1","Entrepreneurship":"#0ea5e9","Health":"#10b981","Hobbies":"#ec4899"}
    cols  = st.columns(4)
    for col, (d, levels) in zip(cols, kb.items()):
        tot = sum(len(t) for t in levels.values())
        b, m, a = len(levels.get("Beginner",[])), len(levels.get("Intermediate",[])), len(levels.get("Advanced",[]))
        col.markdown(f"""
        <div class="card" style="border-top:2px solid {clrs[d]};text-align:center;padding:18px">
          <div style="font-size:1.6rem;margin-bottom:6px">{icons[d]}</div>
          <div style="font-family:'Instrument Sans';font-weight:700;font-size:.9rem;color:#e2e8f0">{d}</div>
          <div style="font-family:'Instrument Sans';font-size:1.7rem;font-weight:800;color:{clrs[d]};margin:4px 0">{tot}</div>
          <div style="font-size:.68rem;color:rgba(255,255,255,0.35);margin-bottom:8px">topics</div>
          <div style="display:flex;gap:5px;justify-content:center;flex-wrap:wrap">
            <span class="lbeg">B:{b}</span><span class="lint">I:{m}</span><span class="ladv">A:{a}</span>
          </div>
        </div>""", unsafe_allow_html=True)
    st.stop()

# ── SHOW ROADMAP ─────────────────────────────────────────────
res     = st.session_state.result
if not isinstance(res, dict):
    st.session_state["generated"] = False
    st.session_state["result"] = None
    st.info("Generate a roadmap from the Dashboard to continue.")
    st.stop()

roadmap = res.get("roadmap", [])
if not roadmap:
    st.session_state["generated"] = False
    st.session_state["result"] = None
    st.info("No active roadmap is available right now. Generate a new roadmap to continue.")
    st.stop()

cinfo   = res.get("cinfo", {})

# Add safe defaults for all cinfo keys
if not isinstance(cinfo, dict):
    cinfo = {}
cinfo_safe = {
    'color': cinfo.get('color', '#6366f1'),
    'icon': cinfo.get('icon', '📚'),
    'name': cinfo.get('name', 'Learning Cluster'),
    'desc': cinfo.get('desc', 'Your personalized learning path'),
    'bg': cinfo.get('bg', None)
}

# Add safe defaults for res keys
res_safe = {
    'total_t': res.get('total_t', len(roadmap)),
    'total_w': res.get('total_w', 4),
    'total_h': res.get('total_h', 0),
    'domain': res.get('domain', 'Education'),
    'related': res.get('related', [])
}

# Try Firebase first, fallback to local
uid = st.session_state.get("user_uid")
if uid:
    try:
        user = get_user_by_uid(uid)
    except Exception:
        user = {}
else:
    user = get_user(st.session_state.name, st.session_state.age)
done    = user.get("completed", [])
pct     = round(len([t for t in roadmap if t["topic"] in done]) / max(len(roadmap), 1) * 100)

# Construct background color from cluster color
cluster_color = cinfo_safe['color']
bg_color = cinfo_safe['bg'] if cinfo_safe['bg'] else f'{cluster_color}12'
if isinstance(bg_color, str) and bg_color.startswith('#'):
    bg_color = bg_color + '12'

# Cluster banner
st.markdown(f"""
<div class="cl-ban" style="background:{bg_color};border-color:{cinfo_safe['color']}33">
  <div style="font-size:1.8rem">{cinfo_safe['icon']}</div>
  <div>
    <div style="font-family:'Instrument Sans';font-size:.95rem;font-weight:700;color:{cinfo_safe['color']}">
      Cluster: {cinfo_safe['name']}</div>
    <div style="font-size:.78rem;color:rgba(255,255,255,0.4)">{cinfo_safe['desc']}</div>
  </div>
  <div style="margin-left:auto;text-align:right">
    <div style="font-size:.68rem;color:rgba(255,255,255,0.35);margin-bottom:2px">Progress</div>
    <div style="font-family:'Instrument Sans';font-size:1.5rem;font-weight:800;color:{cinfo_safe['color']}">{pct}%</div>
    <div class="pb" style="width:110px"><div class="pbf" style="width:{pct}%;background:{cinfo_safe['color']}"></div></div>
  </div>
</div>""", unsafe_allow_html=True)

# Stats
done_count = len([t for t in roadmap if t["topic"] in done])
st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card"><div class="stat-icon" style="background:rgba(139,92,246,0.15)">📋</div>
    <div class="stat-num">{res_safe['total_t']}</div><div class="stat-lbl">Total Topics</div></div>
  <div class="stat-card"><div class="stat-icon" style="background:rgba(34,197,94,0.15)">📅</div>
    <div class="stat-num">{res_safe['total_w']}</div><div class="stat-lbl">Weeks</div></div>
  <div class="stat-card"><div class="stat-icon" style="background:rgba(245,158,11,0.15)">⏱</div>
    <div class="stat-num">{res_safe['total_h']}h</div><div class="stat-lbl">Total Hours</div></div>
  <div class="stat-card"><div class="stat-icon" style="background:rgba(236,72,153,0.15)">✅</div>
    <div class="stat-num">{done_count}</div><div class="stat-lbl">Completed</div></div>
</div>""", unsafe_allow_html=True)

# Two columns
left, right = st.columns([1.55, 1])
lbadge = {"Beginner":'<span class="lbeg">BEG</span>',
           "Intermediate":'<span class="lint">INT</span>',
           "Advanced":'<span class="ladv">ADV</span>'}

with left:
    tab1, tab2, tab3 = st.tabs(["📋 Step-by-Step Plan", "🌐 Node Graph", "🔗 Learning Resources"])

    with tab1:

        st.markdown(f'<div class="card-title">Week-by-Week Plan — {len(roadmap)} Topics</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-sub">✅ Tick topics as you complete them — saved automatically</div>', unsafe_allow_html=True)
        cw = 0
        for step_item in roadmap:
            if step_item["week"] != cw:
                cw = step_item["week"]
                wh = sum(t["duration"] for t in roadmap if t["week"] == cw)
                st.markdown(f'<div class="wk">📅 Week {cw} · {wh:.1f}h</div>', unsafe_allow_html=True)
            is_done = step_item["topic"] in done
            col1, col2 = st.columns([0.045, 0.955])
            with col1:
                chk = st.checkbox("", value=is_done,
                                  key=f"d_chk_{step_item['step']}",
                                  label_visibility="collapsed")
                if chk != is_done:
                  if st.session_state.get("user_uid"):
                    try:
                      toggle_topic_firestore(st.session_state["user_uid"], step_item["topic"])
                    except Exception:
                      st.warning("Could not save progress to cloud. Please try again.")
                  else:
                    toggle_topic(st.session_state.name, st.session_state.age, step_item["topic"])
                    st.rerun()
            with col2:
                dn = "done" if is_done else ""
                st.markdown(f"""
                <div class="trow {dn}">
                  <div class="tstep">#{step_item['step']:02d}</div>
                  {lbadge.get(step_item.get('level','Beginner'),'')}
                  <div class="tname {dn}">{step_item['topic']}</div>
                  <div class="tcat">{step_item.get('category','')}</div>
                  <div class="tdur">{step_item['duration']}h</div>
                </div>""", unsafe_allow_html=True)


        d1, d2 = st.columns(2)
        df = pd.DataFrame([{"Step":s["step"],"Week":s["week"],"Topic":s["topic"],
                              "Level":s.get("level",""),"Category":s.get("category",""),
                              "Hours":s["duration"],"Done":s["topic"] in done} for s in roadmap])
        with d1:
            st.download_button("📥 CSV", df.to_csv(index=False).encode(),
                               f"{st.session_state.name}_roadmap.csv", "text/csv",
                               use_container_width=True)
        with d2:
            st.download_button("📥 JSON",
                               json.dumps([{"step":s["step"],"week":s["week"],"topic":s["topic"],
                                            "hours":s["duration"],"done":s["topic"] in done}
                                           for s in roadmap], indent=2).encode(),
                               f"{st.session_state.name}_roadmap.json","application/json",
                               use_container_width=True)

    with tab2:

        st.markdown('<div class="card-title">🌐 Node Graph — Knowledge Tree</div>', unsafe_allow_html=True)
        st.caption("Root → Weeks → Topics. Green = completed, default = pending.")

        from collections import defaultdict as ddict
        weeks_map = ddict(list)
        for t in roadmap: weeks_map[t["week"]].append(t)
        swks = sorted(weeks_map.keys())
        if not swks:
            st.info("No roadmap nodes to display yet.")
            st.stop()

        NW,NH,HG,VG,MR = 170,40,28,65,4
        PX = 50
        mc = max(min(len(weeks_map[w]),MR) for w in swks)
        SW = max(PX*2 + mc*NW + (mc-1)*HG, 680)
        nodes = []
        prev  = [(SW//2, PX+18)]
        cy    = PX + 18 + 55
        lcols = {"Beginner":"#10b981","Intermediate":"#6366f1","Advanced":"#f59e0b"}

        nodes.append(f'<rect x="{SW//2-65}" y="{PX-18}" width="130" height="36" rx="18" fill="#6366f1" filter="url(#sh)"/>')
        nodes.append(f'<text x="{SW//2}" y="{PX+5}" text-anchor="middle" font-family="Inter" font-size="12.5" font-weight="700" fill="white">🧠 Learning Path</text>')

        for wk in swks:
            tops = weeks_map[wk]
            wx, wy = SW//2, cy
            nodes.append(f'<rect x="{wx-52}" y="{wy-13}" width="104" height="26" rx="13" fill="rgba(99,102,241,0.15)" stroke="rgba(99,102,241,0.3)" stroke-width="1.5"/>')
            nodes.append(f'<text x="{wx}" y="{wy+4}" text-anchor="middle" font-family="Inter" font-size="11" font-weight="700" fill="#a5b4fc">Week {wk}</text>')
            for px, py in prev:
                nodes.append(f'<line x1="{px}" y1="{py}" x2="{wx}" y2="{wy-13}" stroke="rgba(99,102,241,0.3)" stroke-width="1.5" stroke-dasharray="4,3"/>')
            cy = wy + 26 + 26
            rows = [tops[i:i+MR] for i in range(0,len(tops),MR)]
            wb = []
            for row in rows:
                rn = len(row); rw = rn*NW+(rn-1)*HG
                sx = (SW-rw)//2; ry = cy
                for ci, t in enumerate(row):
                    nx_ = sx+ci*(NW+HG); ny_ = ry
                    cx_ = nx_+NW//2; cy2 = ny_+NH//2
                    id_ = t["topic"] in done
                    col = "#64748b" if id_ else lcols.get(t.get("level","Beginner"),"#6366f1")
                    fill= "rgba(34,197,94,0.12)" if id_ else "rgba(255,255,255,0.04)"
                    nodes.append(f'<line x1="{wx}" y1="{wy+13}" x2="{cx_}" y2="{ny_}" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"/>')
                    tick = "✓ " if id_ else ""
                    nm   = t["topic"][:20]+("…" if len(t["topic"])>20 else "")
                    nodes.append(f'<rect x="{nx_}" y="{ny_}" width="{NW}" height="{NH}" rx="8" fill="{fill}" stroke="{col}" stroke-width="1.8" filter="url(#sh)"/>')
                    nodes.append(f'<circle cx="{nx_+12}" cy="{ny_+NH//2}" r="4" fill="{col}"/>')
                    nodes.append(f'<text x="{nx_+22}" y="{ny_+14}" font-family="Inter" font-size="10" font-weight="600" fill="{"#64748b" if id_ else "#e2e8f0"}">{tick}{nm}</text>')
                    nodes.append(f'<text x="{nx_+22}" y="{ny_+27}" font-family="Inter" font-size="9" fill="rgba(255,255,255,0.35)">{t["duration"]}h · {t.get("category","")[:13]}</text>')
                    wb.append((cx_, ny_+NH))
                cy = ry+NH+18
            prev = wb[:MR]; cy += VG-18

        SH = cy+PX
        svg = f"""<svg width="100%" viewBox="0 0 {SW} {SH}" xmlns="http://www.w3.org/2000/svg">
          <defs><filter id="sh" x="-10%" y="-10%" width="130%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-opacity="0.2"/></filter></defs>
          <rect width="{SW}" height="{SH}" fill="#0d1117" rx="12"/>
          {''.join(nodes)}</svg>"""
        st.markdown(f'<div style="overflow:auto;background:#0d1117;border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:12px">{svg}</div>', unsafe_allow_html=True)


    with tab3:
        from core.engine import get_resources

        st.markdown('<div class="card-title">🔗 AI Learning Resources</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-sub">Click Open to launch YouTube, Coursera, Khan Academy and more directly</div>', unsafe_allow_html=True)
        for s in roadmap[:10]:
            with st.expander(f"{'✅' if s['topic'] in done else '📖'} {s['topic']} ({s['duration']}h)"):
                for r in get_resources(s["topic"], res_safe["domain"], s.get("level","Beginner")):
                    st.markdown(f"""
                    <div class="res">
                      <span style="font-size:1.2rem">{r['icon']}</span>
                      <div>
                        <div style="font-size:.83rem;font-weight:600;color:#e2e8f0">{r['title']}</div>
                        <div style="font-size:.71rem;color:rgba(255,255,255,0.4)">{r['desc']} · {r['platform']}</div>
                      </div>
                      <a href="{r['url']}" target="_blank" class="res-btn">Open →</a>
                    </div>""", unsafe_allow_html=True)


with right:
    # Skill mastery

    st.markdown('<div class="card-title">📊 Skill Mastery</div>', unsafe_allow_html=True)
    cat_h = defaultdict(float); cat_done = defaultdict(float)
    for t in roadmap:
        c = t.get("category","General")
        cat_h[c] += t["duration"]
        if t["topic"] in done: cat_done[c] += t["duration"]
    colors = ["#6366f1","#10b981","#f59e0b","#ec4899","#0ea5e9","#8b5cf6","#14b8a6","#f97316"]
    for i,(cat,h) in enumerate(sorted(cat_h.items(),key=lambda x:-x[1])[:7]):
        dp = round(cat_done[cat]/h*100) if h>0 else 0
        c  = colors[i%len(colors)]
        st.markdown(f"""
        <div class="skrow">
          <div class="sktop">
            <span class="skname">
              <span style="width:8px;height:8px;border-radius:50%;background:{c};display:inline-block;box-shadow:0 0 6px {c}44"></span>
              {cat[:18]}
            </span>
            <span class="skpct" style="color:{c}">{dp}%</span>
          </div>
          <div class="pb"><div class="pbf" style="width:{dp}%;background:{c}"></div></div>
        </div>""", unsafe_allow_html=True)


    # Weekly schedule

    st.markdown('<div class="card-title">📆 Weekly Schedule</div>', unsafe_allow_html=True)
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    hrs = st.session_state.get("hrs", 1.5)
    sh = '<div class="sched">'
    for i, d in enumerate(days):
        if i < 5:   sh += f'<div><div class="sdlbl">{d}</div><div class="sdslot a">{hrs}h</div></div>'
        elif i==5:  sh += f'<div><div class="sdlbl">{d}</div><div class="sdslot r">Review</div></div>'
        else:       sh += f'<div><div class="sdlbl">{d}</div><div class="sdslot x">Rest</div></div>'
    sh += '</div>'
    st.markdown(sh, unsafe_allow_html=True)


    # Roadmap preview

    st.markdown(f'<div class="card-title">🗺️ Your Learning Roadmap</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-sub">Goal: {st.session_state.goal}</div>', unsafe_allow_html=True)
    nc = ["#6366f1","#8b5cf6","#a78bfa","#c4b5fd","#ddd6fe","#ede9fe"]
    for i, s in enumerate(roadmap[:6]):
        dn   = s["topic"] in done
        col  = "#10b981" if dn else nc[min(i,len(nc)-1)]
        lbl  = ("✓ " if dn else "") + s["topic"][:24]
        bdg  = "Done" if dn else ("In Progress" if i==done_count else "Upcoming")
        bc   = "#10b981" if dn else ("#6366f1" if i==done_count else "rgba(255,255,255,0.3)")
        st.markdown(f"""
        <div class="rpnode">
          <div class="rpdot" style="background:{col}">{'✓' if dn else i+1}</div>
          <div class="rplbl">{lbl}{'…' if len(s['topic'])>24 else ''}</div>
          <span style="font-size:.65rem;font-weight:600;color:{bc};background:{bc}15;padding:2px 7px;border-radius:4px">{bdg}</span>
        </div>
        {'<div class="rpline"></div>' if i < 5 else ''}""", unsafe_allow_html=True)
    if len(roadmap) > 6:
        st.caption(f"+ {len(roadmap)-6} more topics → visit Skill Roadmap page")


    # AI Recommendations

    st.markdown('<div class="card-title">💡 AI Recommendations</div>', unsafe_allow_html=True)
    hrs = st.session_state.get("hrs", 1.5)
    next_t = roadmap[done_count]["topic"][:28] if done_count < len(roadmap) else "All done!"
    recs = [
        f"📅 Study {hrs}h/day → finish in {res_safe['total_w']} weeks",
        f"🎯 Next up: {next_t}",
        f"📈 {pct}% complete — keep going!",
        f"💪 {res_safe['total_t'] - done_count} topics remaining",
    ]
    for r in recs:
        st.markdown(f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:8px 12px;margin:5px 0;font-size:.81rem;color:rgba(255,255,255,0.6)">{r}</div>', unsafe_allow_html=True)


    # Related
    if res_safe.get("related"):

        st.markdown('<div class="card-title">🔗 You Might Also Enjoy</div>', unsafe_allow_html=True)
        for r in res_safe["related"]:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:9px 12px;margin:6px 0">
              <div style="font-size:.65rem;color:#a5b4fc;font-weight:700;text-transform:uppercase">{r['domain']} · {r['level']}</div>
              <div style="font-size:.84rem;font-weight:600;color:#e2e8f0;margin:2px 0">{r['topic']}</div>
              <div style="font-size:.71rem;color:rgba(255,255,255,0.4)">📁 {r['category']} · ⏱ {r['duration']}h</div>
            </div>""", unsafe_allow_html=True)
