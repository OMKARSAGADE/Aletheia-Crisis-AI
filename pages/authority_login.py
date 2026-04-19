import streamlit as st
from services.auth import login
from components.theme import apply_premium_theme

def render():
    st.set_page_config(page_title="Aletheia - Authority Login", page_icon="👁️", layout="centered")
    apply_premium_theme()
    st.markdown("<h2 style='text-align: center;'>🛡️ Authority Command Center</h2>", unsafe_allow_html=True)
    
    with st.form("authority_login"):
        username = st.text_input("Admin ID")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if login(username, password):
                st.switch_page("pages/authority_dashboard.py")
            else:
                st.error("Invalid credentials.")

if __name__ == "__main__":
    render()
