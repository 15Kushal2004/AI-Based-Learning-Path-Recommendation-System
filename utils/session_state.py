"""Helpers for keeping the active learner in Streamlit session state."""

from __future__ import annotations

import streamlit as st

from utils.storage import get_latest_user_record


SESSION_DEFAULTS = {
    "active_user_id": None,
    "active_profile": None,
    "active_plan": None,
}


def bootstrap_session_state(topic_index):
    for key, default_value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    if not st.session_state.active_user_id:
        latest_record = get_latest_user_record(topic_index)
        if latest_record:
            sync_session_with_record(latest_record)


def sync_session_with_record(record):
    st.session_state.active_user_id = record.get("user_id")
    st.session_state.active_profile = record.get("profile")
    st.session_state.active_plan = record.get("latest_plan")
