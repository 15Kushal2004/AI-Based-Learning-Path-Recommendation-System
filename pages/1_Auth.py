import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import time

st.set_page_config(
    page_title="LearnPath AI — Sign In",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── PREMIUM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg-primary: #09090b;
    --bg-card: rgba(255,255,255,0.04);
    --border-subtle: rgba(255,255,255,0.08);
    --border-focus: rgba(139,92,246,0.5);
    --text-primary: #fafafa;
    --text-secondary: rgba(255,255,255,0.5);
    --text-muted: rgba(255,255,255,0.35);
    --accent: #8b5cf6;
    --accent-glow: rgba(139,92,246,0.15);
    --gradient-start: #6366f1;
    --gradient-end: #a855f7;
    --input-bg: rgba(255,255,255,0.04);
    --success: #22c55e;
    --error: #ef4444;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: var(--bg-primary) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(120,119,198,0.15), transparent),
        radial-gradient(ellipse 60% 40% at 80% 50%, rgba(139,92,246,0.08), transparent),
        radial-gradient(ellipse 60% 40% at 20% 80%, rgba(99,102,241,0.06), transparent) !important;
}

/* Hide sidebar, menu, footer */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[aria-label="Toggle sidebar"],
button[aria-label*="sidebar"],
header button[kind="header"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
}
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}

/* Form inputs — refined */
.stTextInput > div > div > input {
    background: var(--input-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    padding: 11px 14px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    letter-spacing: -0.01em !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--text-muted) !important;
    font-weight: 400 !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px var(--accent-glow), 0 0 20px rgba(139,92,246,0.08) !important;
    background: rgba(255,255,255,0.06) !important;
}
label {
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
}

/* Password toggle icon */
input[type="password"] {
    background: var(--input-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* Primary button */
.stButton > button {
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.7rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(139,92,246,0.3), 0 0 0 1px rgba(139,92,246,0.2) !important;
    filter: brightness(1.1) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid var(--border-subtle) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    padding: 9px 20px !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Expander */
.streamlit-expanderHeader {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    background: transparent !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}
details {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}

/* Alert overrides */
.stAlert { border-radius: 10px !important; }

/* Grid pattern overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}
</style>
""", unsafe_allow_html=True)


# ── AUTH HELPER FUNCTIONS ─────────────────────────────────────
def sign_up(email, password, name):
    """Create user with Firebase Auth + Firestore profile."""
    from firebase_config import pyrebase_auth, admin_auth
    from utils.firebase_storage import save_user_profile
    
    try:
        # Create user in Firebase Auth
        user = pyrebase_auth.create_user_with_email_and_password(email, password)
        uid = user["localId"]
        
        # Save initial profile to Firestore
        profile = {
            "name": name,
            "email": email,
            "age": 22,
            "domain": "Education",
            "goal": "",
            "skill_level": "Beginner",
            "hours_per_day": 1.5,
            "health_condition": "",
        }
        save_user_profile(uid, profile)
        
        return True, uid, user["idToken"], user.get("refreshToken", ""), None
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            return False, None, None, None, "This email is already registered. Please log in instead."
        elif "WEAK_PASSWORD" in error_msg:
            return False, None, None, None, "Password is too weak — at least 6 characters required."
        elif "INVALID_EMAIL" in error_msg:
            return False, None, None, None, "Invalid email format. Please check and try again."
        else:
            return False, None, None, None, f"Error: {error_msg[:100]}"


def sign_in(email, password):
    """Sign in with Firebase Auth."""
    from firebase_config import pyrebase_auth
    from utils.firebase_storage import get_user_profile, update_streak
    
    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email, password)
        uid = user["localId"]
        refresh_token = user.get("refreshToken", "")
        
        # Update streak
        update_streak(uid)
        
        # Load profile
        profile = get_user_profile(uid)
        
        return True, uid, user["idToken"], refresh_token, profile, None
    except Exception as e:
        error_msg = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_msg or "INVALID_PASSWORD" in error_msg:
            return False, None, None, None, None, "Incorrect email or password. Please try again."
        elif "EMAIL_NOT_FOUND" in error_msg:
            return False, None, None, None, None, "This email is not registered. Please sign up first."
        elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_msg:
            return False, None, None, None, None, "Too many attempts. Please try again later."
        else:
            return False, None, None, None, None, f"Error: {error_msg[:100]}"


def reset_password(email):
    """Send password reset email."""
    from firebase_config import pyrebase_auth
    try:
        pyrebase_auth.send_password_reset_email(email)
        return True, None
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


# ── CHECK IF ALREADY LOGGED IN ────────────────────────────────
from utils.session_manager import auth_check_for_login_page, save_session_cookie
auth_check_for_login_page()

# ── MAIN AUTH PAGE ────────────────────────────────────────────
_, center, _ = st.columns([1.2, 1.6, 1.2])

with center:
    # Logo & branding — minimal, refined
    st.markdown("""
    <div style="text-align:center;margin-bottom:36px;margin-top:48px">
        <div style="width:56px;height:56px;border-radius:14px;
            background:linear-gradient(135deg,#6366f1,#8b5cf6,#a855f7);
            display:inline-flex;align-items:center;justify-content:center;font-size:1.6rem;
            box-shadow:0 0 40px rgba(139,92,246,0.25),0 0 0 1px rgba(139,92,246,0.15);
            margin-bottom:20px">🧠</div>
        <div style="font-family:'Instrument Sans','Inter',sans-serif;font-size:1.6rem;font-weight:700;
            color:#fafafa;letter-spacing:-0.03em">
            LearnPath AI</div>
        <div style="color:rgba(255,255,255,0.4);font-size:0.82rem;margin-top:6px;font-weight:400;
            letter-spacing:-0.01em">
            Adaptive AI-Powered Learning Platform</div>
    </div>
    """, unsafe_allow_html=True)
    

    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    # ── LOGIN TAB ─────────────────────────────────────────────
    with tab1:
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        
        login_email = st.text_input("Email", placeholder="you@example.com",
                                     key="login_email")
        login_password = st.text_input("Password", type="password",
                                        placeholder="Enter your password",
                                        key="login_pass")
        
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        
        if st.button("Sign In", key="login_btn"):
            if not login_email or not login_password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Authenticating..."):
                    success, uid, token, refresh_token, profile, error = sign_in(login_email, login_password)
                
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["user_uid"] = uid
                    st.session_state["user_email"] = login_email
                    st.session_state["id_token"] = token
                    
                    if profile:
                        p = profile.get("profile", {})
                        st.session_state["name"] = p.get("name", "Learner")
                        st.session_state["age"] = p.get("age", 22)
                        st.session_state["domain"] = p.get("domain", "Education")
                        st.session_state["goal"] = p.get("goal", "")
                        st.session_state["skill"] = p.get("skill_level", "Beginner")
                        st.session_state["hrs"] = p.get("hours_per_day", 1.5)
                        st.session_state["health"] = p.get("health_condition", "")
                        
                        # Load saved roadmap
                        plan = profile.get("latest_plan", {})
                        if plan and plan.get("roadmap"):
                            st.session_state["generated"] = True
                            st.session_state["result"] = plan
                    
                    st.success("Welcome back! Redirecting...")
                    save_session_cookie(
                        uid,
                        login_email,
                        refresh_token,
                        st.session_state.get("name", "Learner"),
                    )
                    time.sleep(0.3)
                    st.switch_page("app.py")
                else:
                    st.error(error)
        
        # Forgot password
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        with st.expander("Forgot your password?"):
            reset_email = st.text_input("Enter your email address", key="reset_email",
                                         placeholder="you@example.com")
            if st.button("Send Reset Link", key="reset_btn"):
                if reset_email:
                    ok, err = reset_password(reset_email)
                    if ok:
                        st.success("Password reset email sent! Check your inbox.")
                    else:
                        st.error(err)
    
    # ── SIGNUP TAB ────────────────────────────────────────────
    with tab2:
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        
        signup_name = st.text_input("Full Name", placeholder="e.g. Arjun Sharma",
                                     key="signup_name")
        signup_email = st.text_input("Email Address", placeholder="you@example.com",
                                      key="signup_email")
        
        sc1, sc2 = st.columns(2)
        with sc1:
            signup_pass = st.text_input("Password", type="password",
                                         placeholder="Min 6 characters",
                                         key="signup_pass")
        with sc2:
            signup_confirm = st.text_input("Confirm Password", type="password",
                                            placeholder="Re-enter password",
                                            key="signup_confirm")
        
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        
        if st.button("Create Account", key="signup_btn"):
            if not signup_name or not signup_email or not signup_pass:
                st.error("Please fill in all fields.")
            elif signup_pass != signup_confirm:
                st.error("Passwords do not match.")
            elif len(signup_pass) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                with st.spinner("Creating your account..."):
                    success, uid, token, refresh_token, error = sign_up(signup_email, signup_pass, signup_name)
                
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["user_uid"] = uid
                    st.session_state["user_email"] = signup_email
                    st.session_state["id_token"] = token
                    st.session_state["name"] = signup_name
                    
                    # Show success
                    st.markdown("""
                    <div style="text-align:center;padding:24px">
                        <div style="font-size:2.5rem;margin-bottom:12px">✓</div>
                        <div style="font-family:'Instrument Sans','Inter',sans-serif;font-size:1.1rem;
                            font-weight:600;color:#22c55e;margin-bottom:6px">Account Created Successfully</div>
                        <div style="color:rgba(255,255,255,0.4);font-size:0.82rem">
                            Setting up your personalized learning environment...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Minimal progress animation
                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.012)
                        progress.progress(i + 1)
                    
                    save_session_cookie(
                        uid,
                        signup_email,
                        refresh_token,
                        signup_name,
                    )
                    time.sleep(0.3)
                    st.switch_page("app.py")
                else:
                    st.error(error)
    

    
    # Footer
    st.markdown("""
    <div style="text-align:center;margin-top:28px;color:rgba(255,255,255,0.2);font-size:0.7rem;
        letter-spacing:0.02em">
        Secured by Firebase · LearnPath AI v2.0
    </div>
    """, unsafe_allow_html=True)
