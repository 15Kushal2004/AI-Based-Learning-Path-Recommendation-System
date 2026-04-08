import streamlit as st

def render_sidebar():
    # Hide Streamlit's default page navigation and the built-in sidebar toggle (<<)
    st.markdown("""
    <style>
    [data-testid="stSidebarContent"] > ul { display: none !important; }
    [data-testid="stSidebarContent"] > div > ul { display: none !important; }

    /* Hide Streamlit default collapse/expand button */
    [data-testid="collapsedControl"], button[aria-label="Toggle sidebar"] {
      display: none !important;
      visibility: hidden !important;
      pointer-events: none !important;
    }

    /* Keep sidebar always expanded */
    [data-testid="stSidebar"] {
      transform: translateX(0) !important;
      width: 18rem !important;
      min-width: 18rem !important;
    }

    /* Page content offset for sidebar width */
    .css-18e3th9 { margin-left: 18rem !important; }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 0;margin-bottom:8px">
          <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:1.2rem">🧠</div>
          <div>
            <div style="font-size:1.05rem;font-weight:700;color:white">AI Learning Path</div>
            <div style="font-size:.65rem;color:#64748b">Adaptive Learning System</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
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