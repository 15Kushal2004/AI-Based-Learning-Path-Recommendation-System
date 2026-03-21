import streamlit as st

def render_sidebar():
    # Hide Streamlit's default page navigation
    st.markdown("""
    <style>
    [data-testid="stSidebarContent"] > ul { display: none !important; }
    [data-testid="stSidebarContent"] > div > ul { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize sidebar state
    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = False
    
    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 0;margin-bottom:8px">
          <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:1.2rem">🧠</div>
          <div>
            <div style="font-size:1.05rem;font-weight:700;color:white">AI Learning Path</div>
            <div style="font-size:.65rem;color:#64748b">Adaptive Learning System</div>
          </div>
        </div>
        <div style="font-size:.62rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px">MAIN MENU</div>
        """, unsafe_allow_html=True)
        st.page_link("app.py",                 label="📊  Dashboard")
        st.page_link("pages/2_Roadmap.py",     label="🗺️  Skill Roadmap")
        st.page_link("pages/3_Courses.py",     label="📚  My Courses")
        st.page_link("pages/4_Progress.py",    label="📈  My Progress")
        st.page_link("pages/5_Assessments.py", label="📋  Assessments")
        st.page_link("pages/6_Certificates.py",label="🏅  Certificates")
        st.page_link("pages/7_Analytics.py",   label="📉  Analytics")
        st.page_link("pages/8_Settings.py",    label="⚙️  Settings")
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🤖 AI Coach - Get Guidance →", use_container_width=True, key="ai_coach_btn"):
            st.switch_page("pages/9_AICoach.py")