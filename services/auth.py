"""Authentication and Session Management Service.
Supports bcrypt hashed password verification with seamless backward compatibility.
"""
import streamlit as st
import bcrypt
from .db import get_connection

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_or_plain: str) -> bool:
    """Verify password against either bcrypt hash or legacy plaintext."""
    if not hashed_or_plain:
        return False
    # If bcrypt hash format ($2b$, $2a$, etc.)
    if hashed_or_plain.startswith("$2"):
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_or_plain.encode('utf-8'))
        except Exception:
            return False
    # Legacy plaintext check
    return plain_password == hashed_or_plain

def login(username, password):
    if not username or not password:
        return False
        
    db = get_connection()
    user_records = list(db["users"].rows_where("username = ?", [username]))
    
    if user_records:
        user = user_records[0]
        stored_pw = user.get("password", "")
        if verify_password(password, stored_pw):
            # If stored as plaintext, upgrade to bcrypt hash
            if not stored_pw.startswith("$2"):
                try:
                    new_hash = hash_password(password)
                    db["users"].update(username, {"password": new_hash})
                except Exception:
                    pass
                    
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
