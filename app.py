import streamlit as st
import os
from dotenv import load_dotenv
from services.db import init_db
from services.auth import is_logged_in, get_role

from components.theme import apply_premium_theme

load_dotenv()

# Page config
st.set_page_config(
    page_title="Aletheia",
    page_icon="👁️",
    layout="wide"
)

apply_premium_theme()

# Initialize DB on first run
@st.cache_resource
def setup_db():
    init_db()
    return True

setup_db()

# Initialize session state for auth if not exists
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None

def main():
    if is_logged_in():
        role = get_role()
        if role == "user":
            st.switch_page("pages/user_dashboard.py")
        elif role == "authority":
            st.switch_page("pages/authority_dashboard.py")
    else:
        st.title("Welcome to Aletheia")
        st.markdown("### Intelligent Crisis Verification Platform")
        
        st.markdown("Please select your login type from the sidebar.")
        
        st.sidebar.title("Navigation")
        st.sidebar.page_link("pages/user_login.py", label="Citizen Login", icon="👤")
        st.sidebar.page_link("pages/authority_login.py", label="Authority Login", icon="🛡️")

if __name__ == "__main__":
    main()
