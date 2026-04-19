import streamlit as st
from .navbar import render_navbar
from .theme import apply_premium_theme

def page_wrapper(title):
    st.set_page_config(page_title=title, layout="wide", page_icon="👁️")
    apply_premium_theme()
    render_navbar()
    st.title(title)
    st.markdown("---")
