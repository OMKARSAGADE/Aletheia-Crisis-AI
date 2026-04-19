import streamlit as st
from services.auth import logout, is_logged_in, get_role

def render_navbar():
    if is_logged_in():
        col1, col2 = st.columns([8, 2])
        with col1:
            st.markdown(f"**Role:** {get_role().capitalize()}")
        with col2:
            if st.button("Logout"):
                logout()
                st.rerun()
