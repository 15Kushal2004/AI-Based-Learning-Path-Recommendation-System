import streamlit as st


def render_sidebar():
    # Hide Streamlit's default page navigation.
    st.markdown(
        """
    <style>
    [data-testid="stSidebarContent"] > ul { display: none !important; }
    [data-testid="stSidebarContent"] > div > ul { display: none !important; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            """
        <div style="display:flex;align-items:center;gap:10px;padding:1px 0 0;margin-bottom:10px;margin-top:0">
          <div style="width:36px;height:36px;border-radius:10px;
              background:linear-gradient(135deg,#6366f1,#818cf8);
              display:flex;align-items:center;justify-content:center;font-size:1.1rem;
              box-shadow:0 0 25px rgba(99,102,241,0.3)">🧠</div>
          <div>
            <div style="font-size:0.95rem;font-weight:700;color:#fafafa;letter-spacing:-0.02em">AI Learning Path</div>
            <div style="font-size:0.6rem;color:rgba(255,255,255,0.3);font-weight:500;letter-spacing:0.02em">Adaptive Personalised Learning</div>
          </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        user_name = st.session_state.get("name", "Learner")
        user_email = st.session_state.get("user_email", "")
        if user_email:
            initials = "".join(w[0].upper() for w in user_name.split()[:2]) or "L"
            st.markdown(
                f"""
            <div style="display:flex;align-items:center;gap:8px;background:rgba(99,102,241,0.1);
                border:1px solid rgba(99,102,241,0.15);border-radius:8px;padding:8px 10px;margin-bottom:14px">
              <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#818cf8);
                  display:flex;align-items:center;justify-content:center;color:white;font-weight:600;font-size:.65rem;flex-shrink:0">{initials}</div>
              <div>
                <div style="font-size:.73rem;font-weight:600;color:#e2e8f0">{user_name}</div>
                <div style="font-size:.58rem;color:rgba(255,255,255,0.3)">{user_email[:24]}{'...' if len(user_email) > 24 else ''}</div>
              </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
        <div style="font-size:0.6rem;font-weight:600;color:rgba(255,255,255,0.25);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;margin-top:4px">Navigation</div>
        """,
            unsafe_allow_html=True,
        )
        st.page_link("app.py", label="📊  Dashboard")
        st.page_link("pages/2_Roadmap.py", label="🗺️  Skill Roadmap")
        st.page_link("pages/3_Courses.py", label="📚  My Courses")
        st.page_link("pages/4_Progress.py", label="📈  My Progress")
        st.page_link("pages/5_Assessments.py", label="📋  Assessments")
        st.page_link("pages/6_Certificates.py", label="🏅  Certificates")
        st.page_link("pages/7_Analytics.py", label="📉  Analytics")
        st.page_link("pages/9_AICoach.py", label="🤖  AI Coach")

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown(
            """
        <div style="font-size:0.6rem;font-weight:600;color:rgba(255,255,255,0.25);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px">Account</div>
        """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/8_Settings.py", label="⚙️  Settings")

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", key="sidebar_logout", use_container_width=True):
            from utils.session_manager import perform_logout

            perform_logout()
