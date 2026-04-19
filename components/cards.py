import streamlit as st

def metric_card(title, value):
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 8px; background: #ffffff; border: 1px solid #e6e9ef; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);'>
        <h4 style='margin: 0; color: #6e7589; font-size: 14px; font-weight: 500;'>{title}</h4>
        <h2 style='margin: 8px 0 0 0; color: #31333f; font-size: 32px; font-weight: 700;'>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

def verdict_badge(verdict):
    colors = {
        "REAL": "#e2f0e6",
        "FAKE": "#fce8e8",
        "UNVERIFIED": "#fff4d9",
        "LIKELY REAL": "#e2f0e6",
        "NEEDS VERIFICATION": "#fff4d9"
    }
    text_colors = {
        "REAL": "#21c354",
        "FAKE": "#ff4b4b",
        "UNVERIFIED": "#f0a613",
        "LIKELY REAL": "#21c354",
        "NEEDS VERIFICATION": "#f0a613"
    }
    bg_color = colors.get(verdict.upper(), "#f0f2f6")
    text_color = text_colors.get(verdict.upper(), "#31333f")
    
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; border-radius: 8px; background: {bg_color}; margin-bottom: 20px; border: 1px solid {bg_color};'>
        <h3 style='margin: 0; color: {text_color}; font-size: 24px; font-weight: 700;'>{verdict.upper()}</h3>
    </div>
    """, unsafe_allow_html=True)

def info_panel(title, content, icon="ℹ️"):
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 8px; background: #ffffff; border-left: 4px solid #0068c9; border-top: 1px solid #e6e9ef; border-right: 1px solid #e6e9ef; border-bottom: 1px solid #e6e9ef; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
        <h4 style='margin: 0 0 12px 0; color: #31333f; font-size: 18px; font-weight: 600;'>{icon} {title}</h4>
        <div style='color: #31333f; font-size: 15px; line-height: 1.6;'>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def source_card(source_name):
    st.markdown(f"""
    <div style='padding: 15px; border-radius: 8px; background: #f0f2f6; border: 1px solid #e6e9ef; margin-bottom: 10px; display: flex; align-items: center;'>
        <span style='font-size: 20px; margin-right: 15px;'>📰</span>
        <span style='color: #31333f; font-size: 15px; font-weight: 500;'>{source_name}</span>
    </div>
    """, unsafe_allow_html=True)
