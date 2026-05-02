import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collections import defaultdict
from datetime import datetime
from core.engine import get_user, toggle_topic, get_resources, load_kb
from core.sidebar import render_sidebar
from utils.firebase_storage import (
    delete_user_roadmap_firestore,
    get_user_by_uid,
    toggle_topic_firestore,
    get_all_user_roadmaps,
)
import streamlit as st

st.set_page_config(page_title="My Courses", page_icon="📚",
                   layout="wide", initial_sidebar_state="expanded")

# ── INJECT PREMIUM CSS ──────────────────────────────────────
from ui.theme import PREMIUM_CSS
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── AUTH GUARD ───────────────────────────────────────────────
from utils.session_manager import auth_guard
auth_guard()

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:4px;letter-spacing:-0.03em">📚 My Courses</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:var(--text-muted);font-size:.84rem;margin-bottom:20px">Browse and track all topics across every interest you\'ve explored</p>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  LOAD ALL ROADMAPS FOR THE USER
# ═══════════════════════════════════════════════════════════════
age = st.session_state.get("age", 22)
uid = st.session_state.get("user_uid")

# Get user data and all roadmaps
if uid:
    try:
        user = get_user_by_uid(uid)
        all_roadmaps = get_all_user_roadmaps(uid)
        st.session_state["all_roadmaps"] = all_roadmaps
    except Exception:
        user = {}
        all_roadmaps = st.session_state.get("all_roadmaps", [])
else:
    user = get_user(st.session_state.name, age)
    all_roadmaps = st.session_state.get("all_roadmaps", [])

done = user.get("completed", [])

# If no roadmaps yet, show info message
if not all_roadmaps:
    st.info("Please generate your roadmap from the **Dashboard** first.")
    st.stop()


def _format_saved_at(value):
    if not value:
        return "Saved recently"
    try:
        return datetime.fromisoformat(value).strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return value


def _delete_saved_roadmap(roadmap_id):
    """Delete one saved roadmap and refresh page state."""
    if not uid:
        st.error("You need to be logged in to delete saved roadmaps.")
        return

    try:
        deleted = delete_user_roadmap_firestore(uid, roadmap_id)
    except Exception:
        deleted = False

    if not deleted:
        st.error("Could not delete this roadmap. Please try again.")
        return

    updated_roadmaps = get_all_user_roadmaps(uid)
    st.session_state["all_roadmaps"] = updated_roadmaps

    current_result = st.session_state.get("result")
    current_roadmap_id = current_result.get("roadmap_id") if isinstance(current_result, dict) else None
    if current_roadmap_id == roadmap_id:
        if updated_roadmaps:
            st.session_state["result"] = updated_roadmaps[0]
            st.session_state["generated"] = True
        else:
            st.session_state["result"] = None
            st.session_state["generated"] = False

    st.success("Roadmap deleted.")
    st.rerun()

# ═══════════════════════════════════════════════════════════════
#  BUILD GLOBAL TOPIC MAP FROM KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════
kb = load_kb()
topic_info = {}  # topic_name -> {category, domain, duration, level, id}
for domain_name, levels in kb.items():
    for lvl, topics_list in levels.items():
        for t in topics_list:
            topic_info[t["topic"]] = {
                "category": t.get("category", "General"),
                "domain": domain_name,
                "duration": t.get("duration", 0),
                "level": lvl,
                "id": t.get("id", ""),
                "topic": t["topic"],
                "prerequisites": t.get("prerequisites", []),
            }

# Collect all topics from all user roadmaps
all_roadmap_topics = []
all_domains = set()
roadmaps_by_domain = defaultdict(list)
for roadmap_plan in all_roadmaps:
    domain = roadmap_plan.get("domain", "") or "General"
    all_domains.add(domain)
    roadmaps_by_domain[domain].append(roadmap_plan)
    roadmap = roadmap_plan.get("roadmap", [])
    for t in roadmap:
        all_roadmap_topics.append(t)
        if t["topic"] not in topic_info:
            topic_info[t["topic"]] = {
                "category": t.get("category", "General"),
                "domain": domain,
                "duration": t.get("duration", 0),
                "level": t.get("level", "Beginner"),
                "id": t.get("id", ""),
                "topic": t["topic"],
                "prerequisites": t.get("prerequisites", []),
            }

# ═══════════════════════════════════════════════════════════════
#  GROUP ALL COMPLETED TOPICS BY DOMAIN → CATEGORY
# ═══════════════════════════════════════════════════════════════
done_by_domain = defaultdict(lambda: defaultdict(list))
for d in done:
    info = topic_info.get(d)
    if info:
        done_by_domain[info["domain"]][info["category"]].append(info)
        all_domains.add(info["domain"])  # Add domain if not already present
    else:
        done_by_domain["Other"]["Uncategorized"].append({
            "topic": d, "category": "Uncategorized", "domain": "Other",
            "duration": 0, "level": "—", "id": "", "prerequisites": []
        })
        all_domains.add("Other")

# ═══════════════════════════════════════════════════════════════
#  DOMAIN ICONS & COLORS
# ═══════════════════════════════════════════════════════════════
domain_icons = {"Education": "🎓", "Entrepreneurship": "💼", "Health": "💪", "Hobbies": "🎨"}
domain_colors = {"Education": "#6366f1", "Entrepreneurship": "#0ea5e9", "Health": "#10b981", "Hobbies": "#ec4899"}
cat_colors = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#0ea5e9", "#8b5cf6",
              "#14b8a6", "#f97316", "#059669", "#d97706", "#db2777", "#0284c7"]
lbadge = {
    "Beginner": '<span class="lbeg">BEG</span>',
    "Intermediate": '<span class="lint">INT</span>',
    "Advanced": '<span class="ladv">ADV</span>'
}

# ═══════════════════════════════════════════════════════════════
#  STATS CARDS
# ═══════════════════════════════════════════════════════════════
total_hrs_done = sum(topic_info.get(d, {}).get("duration", 0) for d in done)
all_categories = set()
for d in done:
    info = topic_info.get(d)
    if info:
        all_categories.add(info["category"])
for t in all_roadmap_topics:
    all_categories.add(t.get("category", "General"))

c1, c2, c3, c4 = st.columns(4)
for col, (label, val, bg) in zip([c1, c2, c3, c4], [
    ("Total Topics", len(all_roadmap_topics), "rgba(99,102,241,0.12)"),
    ("Completed", len(done), "rgba(34,197,94,0.12)"),
    ("Roadmaps", len(all_roadmaps), "rgba(245,158,11,0.12)"),
    ("Hours Done", f"{total_hrs_done:.0f}h", "rgba(236,72,153,0.12)")]):
    col.markdown(f'<div class="card" style="text-align:center"><div style="font-size:1.75rem;font-weight:700;color:var(--accent-light);font-family:var(--font-display);letter-spacing:-0.03em">{val}</div><div style="font-size:.72rem;color:var(--text-muted);font-weight:500">{label}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="card-title" style="margin-top:18px">🗂 Saved Roadmaps</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.78rem;color:var(--text-muted);margin-bottom:14px">Every roadmap saved for this account, across all domains and goals</div>', unsafe_allow_html=True)

for i, saved_plan in enumerate(all_roadmaps):
    saved_domain = saved_plan.get("domain", "General")
    saved_goal = saved_plan.get("goal") or "No goal saved"
    saved_topics = saved_plan.get("roadmap", [])
    saved_done = len([item for item in saved_topics if item.get("topic") in done])
    saved_total = max(len(saved_topics), 1)
    saved_pct = round(saved_done / saved_total * 100)
    saved_color = domain_colors.get(saved_domain, "#6366f1")
    saved_icon = domain_icons.get(saved_domain, "📚")
    created_label = _format_saved_at(saved_plan.get("created_at"))
    roadmap_id = saved_plan.get("roadmap_id", str(i))
    button_key = f"open_saved_roadmap_{roadmap_id}"
    delete_key = f"delete_saved_roadmap_{roadmap_id}"

    st.markdown(f'''
    <div style="background:linear-gradient(135deg, {saved_color}10, rgba(255,255,255,0.02));
        border:1px solid {saved_color}22;border-radius:14px;padding:16px 18px;margin-bottom:10px">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:14px">
        <div>
          <div style="font-size:.72rem;color:{saved_color};font-weight:700;text-transform:uppercase">{saved_icon} {saved_domain}</div>
          <div style="font-size:.95rem;font-weight:700;color:#e2e8f0;margin-top:4px">{saved_goal}</div>
          <div style="font-size:.72rem;color:rgba(255,255,255,0.38);margin-top:6px">{created_label} · {len(saved_topics)} topics · {saved_plan.get("total_h", 0):.0f}h</div>
        </div>
        <div style="min-width:110px;text-align:right">
          <div style="font-size:1.1rem;font-weight:800;color:{saved_color};font-family:var(--font-display)">{saved_pct}%</div>
          <div style="font-size:.68rem;color:rgba(255,255,255,0.35)">{saved_done}/{len(saved_topics)} done</div>
        </div>
      </div>
    </div>''', unsafe_allow_html=True)

    open_col, delete_col, _ = st.columns([1.4, 1.0, 3.6])
    with open_col:
        if st.button("Open This Roadmap", key=button_key, use_container_width=True):
            st.session_state["generated"] = True
            st.session_state["result"] = saved_plan
            st.switch_page("pages/2_Roadmap.py")
    with delete_col:
        if st.button("Delete", key=delete_key, use_container_width=True):
            _delete_saved_roadmap(roadmap_id)

# ═══════════════════════════════════════════════════════════════
#  DOMAIN TABS — Show all domains the user has explored
# ═══════════════════════════════════════════════════════════════
# Sort domains alphabetically
sorted_domains = sorted(list(all_domains))
tab_labels = [f"{domain_icons.get(d, '📚')} {d}" for d in sorted_domains]

tabs = st.tabs(tab_labels)

for tab, dom in zip(tabs, sorted_domains):
    with tab:
        dom_clr = domain_colors.get(dom, "#6366f1")
        dom_icon = domain_icons.get(dom, "📚")

        # Aggregate every saved roadmap for this domain
        roadmap_entries = roadmaps_by_domain.get(dom, [])
        roadmap_for_domain = []
        seen_topics = set()
        for roadmap_plan in roadmap_entries:
            for topic in roadmap_plan.get("roadmap", []):
                if topic["topic"] not in seen_topics:
                    seen_topics.add(topic["topic"])
                    roadmap_for_domain.append(topic)

        # Collect ALL categories in this domain from KB
        kb_cats_in_domain = defaultdict(list)
        for lvl_name, topics_list in kb.get(dom, {}).items():
            for t in topics_list:
                cat = t.get("category", "General")
                entry = dict(t)
                entry["level"] = lvl_name
                # avoid duplicates
                if not any(e["topic"] == entry["topic"] for e in kb_cats_in_domain[cat]):
                    kb_cats_in_domain[cat].append(entry)

        # Also add roadmap topics for this domain
        for t in roadmap_for_domain:
            cat = t.get("category", "General")
            if not any(e["topic"] == t["topic"] for e in kb_cats_in_domain[cat]):
                kb_cats_in_domain[cat].append(t)

        # Categories where user has completed topics in this domain
        user_cats_in_domain = done_by_domain.get(dom, {})

        # Merge: show categories from KB + categories from user completions
        all_cats_for_domain = set(kb_cats_in_domain.keys()) | set(user_cats_in_domain.keys())

        if not all_cats_for_domain:
            st.markdown(f'''
            <div style="text-align:center;padding:40px;color:var(--text-muted)">
              <div style="font-size:2rem;margin-bottom:8px">{dom_icon}</div>
              <div style="font-size:.85rem">No topics explored in {dom} yet</div>
            </div>''', unsafe_allow_html=True)
            continue

        # Domain summary bar
        dom_done_count = sum(len(v) for v in user_cats_in_domain.values())
        dom_total = sum(len(v) for v in kb_cats_in_domain.values())
        dom_total = max(dom_total, dom_done_count)
        dom_pct = round(dom_done_count / max(dom_total, 1) * 100)

        st.markdown(f'''
        <div style="background:linear-gradient(135deg, {dom_clr}12, {dom_clr}06);
            border:1px solid {dom_clr}25;border-radius:14px;padding:16px 20px;margin-bottom:16px">
          <div style="display:flex;align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="font-size:1.6rem">{dom_icon}</div>
              <div>
                <div style="font-size:1rem;font-weight:700;color:#e2e8f0;font-family:var(--font-display)">{dom}</div>
                <div style="font-size:.72rem;color:rgba(255,255,255,0.4)">{len(all_cats_for_domain)} categories · {dom_done_count} of {dom_total} topics done</div>
              </div>
            </div>
            <div style="text-align:right">
              <div style="font-size:1.3rem;font-weight:800;color:{dom_clr};font-family:var(--font-display)">{dom_pct}%</div>
            </div>
          </div>
          <div class="pb" style="height:8px;margin-top:10px"><div class="pbf" style="width:{min(dom_pct,100)}%;background:{dom_clr}"></div></div>
        </div>''', unsafe_allow_html=True)

        if roadmap_entries:
            st.markdown('<div style="font-size:.76rem;color:var(--text-muted);margin:-4px 0 14px">Saved roadmap history for this domain</div>', unsafe_allow_html=True)
            for idx, roadmap_entry in enumerate(roadmap_entries):
                entry_goal = roadmap_entry.get("goal") or "No goal saved"
                entry_label = _format_saved_at(roadmap_entry.get("created_at"))
                entry_topics = roadmap_entry.get("roadmap", [])
                entry_done = len([item for item in entry_topics if item.get("topic") in done])
                entry_roadmap_id = roadmap_entry.get("roadmap_id", f"{dom}_{idx}")
                entry_key = f"open_domain_history_{dom}_{entry_roadmap_id}"
                entry_delete_key = f"delete_domain_history_{dom}_{entry_roadmap_id}"
                st.markdown(f'''
                <div style="display:flex;align-items:center;justify-content:space-between;
                    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                    border-radius:10px;padding:10px 12px;margin-bottom:8px">
                  <div>
                    <div style="font-size:.82rem;font-weight:600;color:#e2e8f0">{entry_goal}</div>
                    <div style="font-size:.68rem;color:rgba(255,255,255,0.35)">{entry_label} · {len(entry_topics)} topics</div>
                  </div>
                  <div style="font-size:.72rem;color:{dom_clr};font-weight:700">{entry_done}/{len(entry_topics)} done</div>
                </div>''', unsafe_allow_html=True)
                view_col, delete_col, _ = st.columns([1.1, 0.9, 4])
                with view_col:
                    if st.button("View Plan", key=entry_key, use_container_width=True):
                        st.session_state["generated"] = True
                        st.session_state["result"] = roadmap_entry
                        st.switch_page("pages/2_Roadmap.py")
                with delete_col:
                    if st.button("Delete", key=entry_delete_key, use_container_width=True):
                        _delete_saved_roadmap(entry_roadmap_id)

        # Sort categories: ones with completions first, then alphabetical
        sorted_cats = sorted(all_cats_for_domain,
                             key=lambda c: (-len(user_cats_in_domain.get(c, [])), c))

        for ci, cat in enumerate(sorted_cats):
            clr = cat_colors[ci % len(cat_colors)]
            topics_in_kb = kb_cats_in_domain.get(cat, [])
            done_topics_in_cat = [t["topic"] for t in user_cats_in_domain.get(cat, [])]
            total_count = len(topics_in_kb) if topics_in_kb else len(done_topics_in_cat)
            total_count = max(total_count, len(done_topics_in_cat))
            dn_count = len(done_topics_in_cat)
            cat_pct = round(dn_count / max(total_count, 1) * 100)

            # Status indicator
            if cat_pct >= 100:
                status = f'<span style="font-size:.65rem;font-weight:700;color:#4ade80;background:rgba(34,197,94,0.15);padding:2px 8px;border-radius:4px">✓ Complete</span>'
            elif cat_pct > 0:
                status = f'<span style="font-size:.65rem;font-weight:700;color:{clr};background:{clr}15;padding:2px 8px;border-radius:4px">{cat_pct}%</span>'
            else:
                status = '<span style="font-size:.65rem;font-weight:600;color:rgba(255,255,255,0.3);background:rgba(255,255,255,0.05);padding:2px 8px;border-radius:4px">Not started</span>'

            with st.expander(f"📁 {cat}  ·  {dn_count}/{total_count} done"):
                # Category progress bar inside expander
                st.markdown(f'''
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
                  <div class="pb" style="height:5px;flex:1"><div class="pbf" style="width:{min(cat_pct,100)}%;background:{clr}"></div></div>
                  {status}
                </div>''', unsafe_allow_html=True)

                # Show topics from KB if available, else from done list
                topics_to_show = topics_in_kb if topics_in_kb else [
                    {"topic": t, "duration": topic_info.get(t, {}).get("duration", 0),
                     "level": topic_info.get(t, {}).get("level", "—"),
                     "id": topic_info.get(t, {}).get("id", f"done_{j}")}
                    for j, t in enumerate(done_topics_in_cat)
                ]

                for t in topics_to_show:
                    is_done = t["topic"] in done
                    t_id = t.get("id", t["topic"])
                    col1, col2 = st.columns([0.045, 0.955])
                    with col1:
                        chk = st.checkbox("", value=is_done,
                                          key=f"c3_{dom}_{cat}_{t_id}",
                                          label_visibility="collapsed")
                        if chk != is_done:
                            if uid:
                                try:
                                    toggle_topic_firestore(uid, t["topic"])
                                except Exception:
                                    st.warning("Could not save progress to cloud. Please try again.")
                            else:
                                toggle_topic(st.session_state.name, age, t["topic"])
                            st.rerun()
                    with col2:
                        dn = "done" if is_done else ""
                        lvl = t.get("level", "Beginner")
                        dur = t.get("duration", 0)
                        st.markdown(f'''<div class="trow {dn}">
                          <div class="tstep">{lbadge.get(lvl, "")}</div>
                          <div class="tname {dn}">{t["topic"]}</div>
                          <div class="tdur">{dur}h</div>
                        </div>''', unsafe_allow_html=True)

                # Show resources for first topic in this category
                if topics_to_show:
                    topic_for_res = topics_to_show[0]["topic"]
                    level_for_res = topics_to_show[0].get("level", "Beginner")
                    with st.expander("🔗 Resources for this category"):
                        for r in get_resources(topic_for_res, dom, level_for_res)[:2]:
                            st.markdown(f'<div class="res"><span style="font-size:1.2rem">{r["icon"]}</span><div><div style="font-size:.83rem;font-weight:600;color:var(--text)">{r["title"]}</div><div style="font-size:.71rem;color:var(--text-muted)">{r["platform"]}</div></div><a href="{r["url"]}" target="_blank" class="res-btn">Open →</a></div>', unsafe_allow_html=True)
