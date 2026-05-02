"""
Session persistence for Streamlit auth.

Primary persistence is a local JSON session file so refreshes and app restarts
keep the user signed in on this machine. Browser cookies are used as a
best-effort secondary layer when the optional component is available.
"""

import json
import os

import streamlit as st

try:
    import extra_streamlit_components as stx
except ModuleNotFoundError:
    stx = None

COOKIE_NAME = "learnpath_session"
LOGOUT_COOKIE_NAME = "learnpath_logout_state"
SESSION_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".streamlit",
    "active_session.json",
)


class _FallbackCookieManager:
    """Minimal in-memory fallback when the cookie component is unavailable."""

    def get_all(self):
        return st.session_state.setdefault("_fallback_cookies", {})

    def set(self, name, value, expires_at=None, key=None):
        cookies = self.get_all()
        cookies[name] = value
        return True

    def delete(self, name, key=None):
        cookies = self.get_all()
        cookies.pop(name, None)
        return True


def _get_cookie_manager():
    if "_cookie_manager" not in st.session_state:
        if stx is not None:
            st.session_state["_cookie_manager"] = stx.CookieManager(key="learnpath_cookies")
        else:
            st.session_state["_cookie_manager"] = _FallbackCookieManager()
    return st.session_state["_cookie_manager"]


def _ensure_session_dir():
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)


def _write_local_session(session_data):
    _ensure_session_dir()
    with open(SESSION_FILE, "w", encoding="utf-8") as handle:
        json.dump(session_data, handle)


def _read_local_session():
    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    uid = data.get("uid")
    refresh_token = data.get("refresh_token")
    if not uid or not refresh_token:
        return None
    return data


def _clear_local_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except OSError:
        pass


def _get_persisted_session():
    cm = _get_cookie_manager()
    cookies = cm.get_all()

    if cookies:
        raw = cookies.get(COOKIE_NAME)
        logout_state = cookies.get(LOGOUT_COOKIE_NAME)
        if logout_state == "0" and raw:
            try:
                data = json.loads(raw) if isinstance(raw, str) else raw
                if data.get("uid") and data.get("refresh_token"):
                    return data
            except (json.JSONDecodeError, TypeError):
                pass

    return _read_local_session()


def _populate_session_state(uid, email, id_token, profile=None, fallback_name="Learner"):
    from utils.firebase_storage import get_all_user_roadmaps

    st.session_state["logged_in"] = True
    st.session_state["user_uid"] = uid
    st.session_state["user_email"] = email or ""
    st.session_state["id_token"] = id_token

    if profile:
        p = profile.get("profile", {})
        st.session_state["name"] = p.get("name", fallback_name)
        st.session_state["age"] = p.get("age", 22)
        st.session_state["domain"] = p.get("domain", "Education")
        st.session_state["goal"] = p.get("goal", "")
        st.session_state["skill"] = p.get("skill_level", "Beginner")
        st.session_state["hrs"] = p.get("hours_per_day", 1.5)
        st.session_state["health"] = p.get("health_condition", "")

        roadmaps = get_all_user_roadmaps(uid)
        if roadmaps:
            st.session_state["all_roadmaps"] = roadmaps
            st.session_state["generated"] = True
            st.session_state["result"] = roadmaps[0]
        else:
            st.session_state["generated"] = False
            st.session_state["result"] = None
    else:
        st.session_state["name"] = fallback_name


def _restore_persisted_login():
    if st.session_state.get("logged_in"):
        return True

    session_data = _get_persisted_session()
    if not session_data:
        return False

    uid = session_data.get("uid")
    refresh_token = session_data.get("refresh_token")
    email = session_data.get("email", "")
    fallback_name = session_data.get("name", "Learner")

    try:
        from firebase_config import pyrebase_auth
        from utils.firebase_storage import get_user_profile, update_streak

        refreshed = pyrebase_auth.refresh(refresh_token)
        profile = get_user_profile(uid)
        if profile:
            update_streak(uid)

        _populate_session_state(
            uid=uid,
            email=email,
            id_token=refreshed["idToken"],
            profile=profile,
            fallback_name=fallback_name,
        )

        save_session_cookie(uid, email, refresh_token, st.session_state.get("name", fallback_name))
        return True
    except Exception:
        clear_session_cookie()
        return False


def save_session_cookie(uid, email, refresh_token, name="Learner"):
    """Persist login locally and, when available, in browser cookies."""
    session_data = {
        "uid": uid,
        "email": email,
        "refresh_token": refresh_token,
        "name": name,
    }
    _write_local_session(session_data)

    cm = _get_cookie_manager()
    try:
        cm.set(COOKIE_NAME, json.dumps(session_data), expires_at=None, key="set_session_cookie")
        cm.set(LOGOUT_COOKIE_NAME, "0", expires_at=None, key="set_logout_state_logged_in")
    except Exception:
        pass


def clear_session_cookie():
    """Clear persisted auth state."""
    _clear_local_session()

    cm = _get_cookie_manager()
    try:
        cm.delete(COOKIE_NAME, key="del_session_cookie")
    except Exception:
        pass
    try:
        cm.set(COOKIE_NAME, "", expires_at=None, key="set_session_cookie_empty")
        cm.set(LOGOUT_COOKIE_NAME, "1", expires_at=None, key="set_logout_state_logged_out")
    except Exception:
        pass


def _revoke_user_refresh_tokens(uid):
    if not uid:
        return
    try:
        from firebase_config import admin_auth

        admin_auth.revoke_refresh_tokens(uid)
    except Exception:
        pass


def perform_logout():
    uid = st.session_state.get("user_uid")
    _revoke_user_refresh_tokens(uid)
    clear_session_cookie()

    preserve = {"_cookie_manager"}
    for key in list(st.session_state.keys()):
        if key not in preserve:
            del st.session_state[key]
    st.session_state["logged_in"] = False
    st.switch_page("pages/1_Auth.py")


def auth_guard():
    """Guard for protected pages: restore session or redirect to login."""
    if _restore_persisted_login():
        return
    st.switch_page("pages/1_Auth.py")


def auth_check_for_login_page():
    """Redirect signed-in users away from the login page."""
    if _restore_persisted_login():
        st.switch_page("app.py")
        return True
    return False
