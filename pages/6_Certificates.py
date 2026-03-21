import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import datetime
from core.engine import get_user
from core.sidebar import render_sidebar
import streamlit as st

st.set_page_config(page_title="Certificates", page_icon="🏅",
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

.pb { background: #f1f5f9; border-radius: 6px; height: 7px; overflow: hidden; }
.pbf { height: 100%; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

# ── RENDER SIDEBAR ───────────────────────────────────────────
render_sidebar()

st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.6rem;font-weight:800;color:#0f172a;margin-bottom:4px">🏅 Certificates</h2>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b;font-size:.86rem;margin-bottom:20px">Earn certificates as you complete your roadmap</p>', unsafe_allow_html=True)

if not st.session_state.get("generated"):
    st.info("ℹ️ Please generate your roadmap from the **Dashboard** first.")
    st.stop()

res = st.session_state.result
roadmap = res["roadmap"]
age = st.session_state.get("age",22)
user = get_user(st.session_state.name, age)
done = user.get("completed",[])
pct  = round(len(done)/max(len(roadmap),1)*100)
name = st.session_state.get("name","Learner")

certs=[("Beginner","🥉","#f59e0b",25),("Intermediate","🥈","#94a3b8",50),
       ("Advanced","🥇","#f59e0b",75),("Expert","🏆","#6366f1",100)]
for title,icon,color,req in certs:
    earned = pct >= req
    st.markdown(f"""
    <div style="background:{"#fffbeb" if earned else "#f8fafc"};border:2px solid {color+("66" if earned else "22")};border-radius:18px;padding:24px;margin:12px 0;display:flex;align-items:center;gap:20px">
      <div style="font-size:2.8rem">{icon}</div>
      <div style="flex:1">
        <div style="font-size:1.1rem;font-weight:800;color:#0f172a">{title} Certificate</div>
        <div style="font-size:.82rem;color:#64748b;margin:4px 0">Complete {req}% of your {res["domain"]} roadmap</div>
        <div style="font-size:.78rem;color:{color};font-weight:600">Learner: {name} · Domain: {res["domain"]}</div>
      </div>
      <div style="text-align:right;min-width:130px">
        <div style="font-size:.7rem;color:#94a3b8;margin-bottom:4px">Progress: {min(pct,req)}/{req}%</div>
        <div style="background:#f1f5f9;border-radius:6px;height:8px;overflow:hidden;width:120px;margin-bottom:8px">
          <div style="height:100%;border-radius:6px;background:{color};width:{min(pct,req)/req*100:.0f}%"></div>
        </div>
        <div style="background:{"linear-gradient(135deg,"+color+","+color+"bb)" if earned else "#f1f5f9"};color:{"white" if earned else "#94a3b8"};padding:6px 14px;border-radius:8px;font-size:.78rem;font-weight:700;text-align:center">
          {"🏅 EARNED" if earned else "🔒 Locked"}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    if earned:
        st.download_button(f"⬇️ Download {title} Certificate",
            f"CERTIFICATE OF COMPLETION\n{'='*40}\nName: {name}\nCertificate: {title}\nDomain: {res['domain']}\nProgress: {pct}%\nDate: {datetime.date.today()}\n\nAI-Driven Personalized Learning Path System",
            f"{name}_{title}_Certificate.txt","text/plain",key=f"dl_{req}")