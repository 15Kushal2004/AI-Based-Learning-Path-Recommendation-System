import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collections import defaultdict
from core.engine import get_user, CLUSTERS
from core.sidebar import render_sidebar
from utils.firebase_storage import get_user_by_uid
import pandas as pd
import streamlit as st

st.set_page_config(page_title="My Progress", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

# ── INJECT PREMIUM CSS ──────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:4px;letter-spacing:-0.03em">📈 My Progress</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:var(--text-muted);font-size:.84rem;margin-bottom:20px">Track your learning journey</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res    = st.session_state.result
if not isinstance(res, dict):
    st.info("No active roadmap is available right now. Generate a new roadmap from the Dashboard.")
    st.stop()
roadmap= res.get("roadmap", [])
if not roadmap:
    st.info("No active roadmap is available right now. Generate a new roadmap from the Dashboard.")
    st.stop()
age    = st.session_state.get("age",22)
uid    = st.session_state.get("user_uid")
if uid:
    try:
        user = get_user_by_uid(uid)
    except Exception:
        user = {}
else:
    user = get_user(st.session_state.name, age)
done   = user.get("completed",[])
badges = user.get("badges",[])

# Separate: topics completed in CURRENT roadmap vs ALL interests
roadmap_topics = {t["topic"] for t in roadmap}
roadmap_done = [d for d in done if d in roadmap_topics]
pct = round(len(roadmap_done) / max(len(roadmap), 1) * 100)
cinfo  = res.get("cinfo", {"color": "#6366f1", "icon": "📚", "name": "Learning Cluster", "desc": ""})

c1,c2,c3,c4 = st.columns(4)
if not isinstance(cinfo, dict):
    cinfo = {}
cinfo = {
    "color": cinfo.get("color", "#6366f1"),
    "icon": cinfo.get("icon", "📚"),
    "name": cinfo.get("name", "Learning Cluster"),
    "desc": cinfo.get("desc", ""),
}
total_h = res.get("total_h", sum(t.get("duration", 0) for t in roadmap))
res["total_h"] = total_h
for col,(lbl,val,bg) in zip([c1,c2,c3,c4],[
    ("Roadmap Done", f"{len(roadmap_done)}/{len(roadmap)}", "rgba(34,197,94,0.12)"),
    ("All Completed", len(done), "rgba(99,102,241,0.12)"),
    ("Streak Days", user.get("streak_days",1), "rgba(245,158,11,0.12)"),
    ("Badges", len(badges), "rgba(236,72,153,0.12)")]):
    col.markdown(f'<div class="card" style="text-align:center"><div style="font-size:1.75rem;font-weight:700;color:var(--accent-light);font-family:var(--font-display);letter-spacing:-0.03em">{val}</div><div style="font-size:.72rem;color:var(--text-muted);font-weight:500">{lbl}</div></div>', unsafe_allow_html=True)

# ── BUILD A GLOBAL TOPIC → CATEGORY MAP FROM KNOWLEDGE BASE ──
from core.engine import load_kb
kb = load_kb()
topic_to_cat = {}
topic_to_domain = {}
topic_to_dur = {}
for domain_name, levels in kb.items():
    for lvl, topics_list in levels.items():
        for t in topics_list:
            topic_to_cat[t["topic"]] = t.get("category", "General")
            topic_to_domain[t["topic"]] = domain_name
            topic_to_dur[t["topic"]] = t.get("duration", 0)

# Also add current roadmap topics (in case KB is missing any)
for t in roadmap:
    topic_to_cat[t["topic"]] = t.get("category", "General")
    topic_to_domain[t["topic"]] = res.get("domain", "")
    topic_to_dur[t["topic"]] = t.get("duration", 0)

# ── GROUP ALL COMPLETED TOPICS BY CATEGORY ───────────────────
done_by_cat = defaultdict(list)
for d in done:
    cat = topic_to_cat.get(d, "Other")
    done_by_cat[cat].append(d)

# ── GROUP ALL KB TOPICS BY CATEGORY (for total counts) ───────
all_by_cat = defaultdict(list)
for domain_name, levels in kb.items():
    for lvl, topics_list in levels.items():
        for t in topics_list:
            cat = t.get("category", "General")
            if t["topic"] not in all_by_cat[cat]:
                all_by_cat[cat].append(t["topic"])

# ── COLLECT ALL RELEVANT CATEGORIES ──────────────────────────
# Categories from the current roadmap + categories where user has completed topics
roadmap_cats = set()
for t in roadmap:
    roadmap_cats.add(t.get("category", "General"))
all_cats = set(done_by_cat.keys()) | roadmap_cats

# ── DOMAIN ICONS & COLORS ────────────────────────────────────
domain_icons = {"Education": "🎓", "Entrepreneurship": "💼", "Health": "💪", "Hobbies": "🎨"}
cat_colors = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#0ea5e9", "#8b5cf6",
              "#14b8a6", "#f97316", "#059669", "#d97706", "#db2777", "#0284c7"]

left, right = st.columns([1.5, 1])
with left:
    # ── CURRENT ROADMAP PROGRESS ─────────────────────────────
    st.markdown(f'<div class="card-title">📋 Current Roadmap — {pct}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pb" style="height:12px;margin:8px 0"><div class="pbf" style="width:{min(pct,100)}%;background:{cinfo["color"]}"></div></div>', unsafe_allow_html=True)
    roadmap_done_topics = [t for t in roadmap if t["topic"] in done]
    st.markdown(f'<div style="font-size:.78rem;color:var(--text-muted)">{len(roadmap_done)} of {len(roadmap)} topics · {sum(t["duration"] for t in roadmap_done_topics):.0f}h of {res["total_h"]}h</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

    # ── ALL INTERESTS / CATEGORIES PROGRESS ──────────────────
    st.markdown('<div class="card-title">🎯 All Your Interests</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:var(--text-muted);margin-bottom:12px">Progress across every category you\'ve explored</div>', unsafe_allow_html=True)

    sorted_cats = sorted(all_cats, key=lambda c: len(done_by_cat.get(c, [])), reverse=True)
    for i, cat in enumerate(sorted_cats):
        clr = cat_colors[i % len(cat_colors)]
        done_in_cat = done_by_cat.get(cat, [])
        total_in_cat = len(all_by_cat.get(cat, []))
        total_in_cat = max(total_in_cat, len(done_in_cat))  # safety
        cat_pct = round(len(done_in_cat) / max(total_in_cat, 1) * 100)
        cat_hrs = sum(topic_to_dur.get(t, 0) for t in done_in_cat)

        # Determine which domain this category belongs to
        sample_topic = done_in_cat[0] if done_in_cat else (all_by_cat[cat][0] if all_by_cat.get(cat) else "")
        dom = topic_to_domain.get(sample_topic, "")
        dom_icon = domain_icons.get(dom, "📚")

        st.markdown(f'''
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
            border-radius:12px;padding:14px 16px;margin-bottom:10px;
            border-left:3px solid {clr}">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
            <div style="display:flex;align-items:center;gap:8px">
              <span style="font-size:1.1rem">{dom_icon}</span>
              <div>
                <div style="font-size:.85rem;font-weight:700;color:#e2e8f0">{cat}</div>
                <div style="font-size:.68rem;color:rgba(255,255,255,0.35)">{dom} · {cat_hrs:.0f}h completed</div>
              </div>
            </div>
            <div style="text-align:right">
              <div style="font-size:1.1rem;font-weight:800;color:{clr};font-family:var(--font-display)">{cat_pct}%</div>
              <div style="font-size:.65rem;color:rgba(255,255,255,0.35)">{len(done_in_cat)}/{total_in_cat} topics</div>
            </div>
          </div>
          <div class="pb" style="height:6px"><div class="pbf" style="width:{min(cat_pct,100)}%;background:{clr}"></div></div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    # ── COMPLETED TOPICS GROUPED BY CATEGORY ─────────────────
    if done:
        st.markdown(f'<div class="card-title">✅ Completed Topics ({len(done)})</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.78rem;color:var(--text-muted);margin-bottom:10px">All topics you\'ve mastered, grouped by interest</div>', unsafe_allow_html=True)

        for i, cat in enumerate(sorted_cats):
            done_in_cat = done_by_cat.get(cat, [])
            if not done_in_cat:
                continue
            clr = cat_colors[i % len(cat_colors)]
            dom = topic_to_domain.get(done_in_cat[0], "")
            dom_icon = domain_icons.get(dom, "📚")

            with st.expander(f"{dom_icon} {cat} — {len(done_in_cat)} completed", expanded=(i == 0)):
                for d in done_in_cat:
                    hrs = topic_to_dur.get(d, 0)
                    st.markdown(f'''
                    <div style="display:flex;align-items:center;gap:10px;
                        background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.15);
                        border-radius:8px;padding:8px 12px;margin:4px 0">
                      <span style="color:#4ade80;font-size:.85rem;font-weight:700">✓</span>
                      <span style="font-size:.82rem;color:#4ade80;flex:1">{d}</span>
                      <span style="font-size:.68rem;color:rgba(255,255,255,0.3)">{hrs}h</span>
                    </div>''', unsafe_allow_html=True)


with right:
    st.markdown(f'<div class="card" style="border-color:{cinfo["color"]}33"><div style="font-size:1.6rem">{cinfo["icon"]}</div><div style="font-weight:700;color:{cinfo["color"]}">{cinfo["name"]}</div><div style="font-size:.78rem;color:var(--text-muted)">{cinfo["desc"]}</div></div>', unsafe_allow_html=True)

    # ── INTEREST SUMMARY CARD ────────────────────────────────
    st.markdown(f'''
    <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
        border-radius:12px;padding:16px;margin-bottom:12px">
      <div style="font-size:.78rem;font-weight:700;color:#a5b4fc;margin-bottom:10px">📊 INTEREST OVERVIEW</div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px">
        <div style="text-align:center">
          <div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;font-family:var(--font-display)">{len(all_cats)}</div>
          <div style="font-size:.65rem;color:rgba(255,255,255,0.4)">Categories</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;font-family:var(--font-display)">{len(done)}</div>
          <div style="font-size:.65rem;color:rgba(255,255,255,0.4)">Completed</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;font-family:var(--font-display)">{sum(topic_to_dur.get(d,0) for d in done):.0f}h</div>
          <div style="font-size:.65rem;color:rgba(255,255,255,0.4)">Total Hours</div>
        </div>
      </div>
    </div>''', unsafe_allow_html=True)

    # ── BADGES ───────────────────────────────────────────────
    all_badges = [("First 5", "Complete 5 topics", len(done) >= 5, "🥉"),
                  ("10 Topics", "Complete 10 topics", len(done) >= 10, "🥈"),
                  ("25 Topics", "Complete 25 topics", len(done) >= 25, "🥇"),
                  ("Halfway", "Reach 50% progress", pct >= 50, "⭐"),
                  ("Champion", "Complete 100%", pct >= 100, "🏆")]
    st.markdown('<div class="card-title">🏅 Badges</div>', unsafe_allow_html=True)
    for nm, desc, earned, icon in all_badges:
        bg = "rgba(245,158,11,0.12)" if earned else "var(--bg-subtle)"
        tc = "#fbbf24" if earned else "var(--text-muted)"
        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;background:{bg};border-radius:8px;padding:9px 12px;margin:5px 0"><span style="font-size:1.2rem">{icon}</span><div><div style="font-size:.8rem;font-weight:600;color:{tc}">{nm}</div><div style="font-size:.7rem;color:var(--text-muted)">{desc}</div></div><div style="margin-left:auto;font-size:.7rem;font-weight:600;color:{"var(--success)" if earned else "var(--text-muted)"}">{"✓ Earned" if earned else "🔒 Locked"}</div></div>', unsafe_allow_html=True)

    # ── TOP INTERESTS BREAKDOWN ──────────────────────────────
    if done_by_cat:
        st.markdown('<div class="card-title">🔥 Top Interests</div>', unsafe_allow_html=True)
        top_cats = sorted(done_by_cat.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        for i, (cat, topics_in) in enumerate(top_cats):
            clr = cat_colors[i % len(cat_colors)]
            dom = topic_to_domain.get(topics_in[0], "")
            dom_icon = domain_icons.get(dom, "📚")
            st.markdown(f'''
            <div style="display:flex;align-items:center;gap:10px;
                background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                border-radius:10px;padding:10px 12px;margin:5px 0">
              <span style="font-size:1.1rem">{dom_icon}</span>
              <div style="flex:1">
                <div style="font-size:.8rem;font-weight:600;color:#e2e8f0">{cat}</div>
                <div style="font-size:.68rem;color:rgba(255,255,255,0.35)">{len(topics_in)} topics · {dom}</div>
              </div>
              <div style="font-size:.9rem;font-weight:800;color:{clr}">{len(topics_in)}</div>
            </div>''', unsafe_allow_html=True)
