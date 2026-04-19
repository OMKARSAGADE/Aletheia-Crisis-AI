import streamlit as st

def live_alert_card(message, verdict, risk_score, timestamp):
  
    verdict_colors = {
        "REAL": "green",
        "FAKE": "red",
        "UNVERIFIED": "orange"
    }
    
    v_color = verdict_colors.get(verdict.upper(), "grey")
    
    risk_color = "red" if risk_score > 70 else "orange" if risk_score > 30 else "green"
    
    
    short_msg = message[:60] + "..." if len(message) > 60 else message
    
    st.markdown(f"""
    <div style='padding: 10px 15px; border-left: 4px solid {v_color}; background-color: #1e1e1e; border-radius: 5px; margin-bottom: 10px; font-size: 14px;'>
        <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
            <strong style='color: {v_color}; font-size: 12px;'>{verdict.upper()}</strong>
            <span style='color: #888; font-size: 11px;'>{timestamp}</span>
        </div>
        <div style='color: #ddd; margin-bottom: 5px;'>{short_msg}</div>
        <div style='display: flex; justify-content: flex-end;'>
            <span style='background-color: {risk_color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px; font-weight: bold;'>Risk: {risk_score}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
