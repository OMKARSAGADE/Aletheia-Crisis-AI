import streamlit as st
from .db import get_connection

def login(username, password):
    db = get_connection()
    user_record = list(db["users"].rows_where("username = ? AND password = ?", [username, password]))
    
    if user_record:
        user = user_record[0]
        st.session_state["logged_in"] = True
        st.session_state["username"] = user["username"]
        st.session_state["role"] = user["role"]
        return True
    return False

def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None

def is_logged_in():
    return st.session_state.get("logged_in", False)

def get_role():
    return st.session_state.get("role", None)
