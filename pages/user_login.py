import streamlit as st
from services.auth import login
from components.theme import apply_premium_theme

def render():
    st.set_page_config(page_title="Aletheia - Citizen Login", page_icon="👁️", layout="centered")
    apply_premium_theme()
    st.markdown("<h2 style='text-align: center;'>👥 Citizen Portal</h2>", unsafe_allow_html=True)
    
    with st.form("citizen_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if login(username, password):
                st.switch_page("pages/user_dashboard.py")
            else:
                st.error("Invalid credentials.")

if __name__ == "__main__":
    render()
