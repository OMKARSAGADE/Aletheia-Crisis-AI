"""UI Card and Badge Components."""
import streamlit as st

def metric_card(title, value, subtitle=None):
    sub_html = f"<p style='margin: 4px 0 0 0; color: #6e7589; font-size: 12px;'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 8px; background: #ffffff; border: 1px solid #e6e9ef; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);'>
        <h4 style='margin: 0; color: #6e7589; font-size: 14px; font-weight: 500;'>{title}</h4>
        <h2 style='margin: 8px 0 0 0; color: #31333f; font-size: 32px; font-weight: 700;'>{value}</h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def verdict_badge(verdict):
    v = verdict.upper()
    colors = {
        "SUPPORTED": "#e2f0e6",
        "REAL": "#e2f0e6",
        "LIKELY REAL": "#e2f0e6",
        "CONTRADICTED": "#fce8e8",
        "FAKE": "#fce8e8",
        "UNVERIFIED": "#fff4d9",
        "NEEDS VERIFICATION": "#fff4d9",
        "CONFLICTING": "#f3e8ff",
        "NON-CRISIS": "#e5e7eb"
    }
    text_colors = {
        "SUPPORTED": "#15803d",
        "REAL": "#15803d",
        "LIKELY REAL": "#15803d",
        "CONTRADICTED": "#b91c1c",
        "FAKE": "#b91c1c",
        "UNVERIFIED": "#b45309",
        "NEEDS VERIFICATION": "#b45309",
        "CONFLICTING": "#7e22ce",
        "NON-CRISIS": "#4b5563"
    }
    icons = {
        "SUPPORTED": "✅ CORROBORATED EVIDENCE",
        "REAL": "✅ CORROBORATED EVIDENCE",
        "LIKELY REAL": "✅ CORROBORATED EVIDENCE",
        "CONTRADICTED": "❌ CONTRADICTED / DEBUNKED",
        "FAKE": "❌ CONTRADICTED / DEBUNKED",
        "UNVERIFIED": "⚠️ UNVERIFIED CLAIM",
        "NEEDS VERIFICATION": "⚠️ UNVERIFIED CLAIM",
        "CONFLICTING": "⚖️ CONFLICTING EVIDENCE",
        "NON-CRISIS": "ℹ️ NON-CRISIS CONTENT"
    }
    
    bg_color = colors.get(v, "#f0f2f6")
    text_color = text_colors.get(v, "#31333f")
    display_text = icons.get(v, f"🔍 {v}")
    
    st.markdown(f"""
    <div style='text-align: center; padding: 18px; border-radius: 8px; background: {bg_color}; margin-bottom: 20px; border: 1.5px solid {text_color};'>
        <h3 style='margin: 0; color: {text_color}; font-size: 20px; font-weight: 700; letter-spacing: 0.5px;'>{display_text}</h3>
        <p style='margin: 4px 0 0 0; color: {text_color}; font-size: 12px; font-weight: 500;'>Official Cautious Verification Status</p>
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
