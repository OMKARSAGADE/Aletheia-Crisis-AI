import streamlit as st
import pandas as pd
from components.layout import page_wrapper
from components.cards import metric_card, verdict_badge, info_panel
from services.auth import get_role, is_logged_in
from agents.orchestrator import run_pipeline
from services.db import save_report, get_recent_reports
from services.ocr import extract_text_from_image
from services.gemini import generate_analysis
import time

def process_verification(input_text, source_type):
    if not input_text.strip():
        st.warning("⚠️ Please provide text or an image with text to verify.")
        return

    with st.spinner("🧠 Analyzing claim through LangGraph Pipeline..."):
        time.sleep(1) # Polish delay
        
        try:
            result = run_pipeline(input_text)
            verdict = result.get("final_verdict", "UNVERIFIED")
            credibility = result.get("final_credibility", 50)
            risk = result.get("final_risk", 50)
            location = result.get("final_location", "Unknown")
            trusted_sources = result.get("trusted_sources", [])
            evidence = result.get("evidence_found", "No evidence available.")
        except Exception as e:
            st.error(f"Pipeline Analysis Failed: {str(e)}")
            return

    with st.spinner("🤖 Generating intelligence report..."):
        # Get structured analysis
        analysis = generate_analysis(input_text, verdict, credibility, evidence)
        
        # Save to DB
        try:
            save_report(input_text, verdict, credibility, risk, source_type, location)
        except Exception as e:
            st.warning("Analysis complete, but failed to save history.")
        
        st.markdown("---")
        st.markdown("### 📊 Analysis Results")
        
        # Top Row: Verdict & Scores
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            verdict_badge(verdict)
            st.progress(credibility / 100.0, text=f"Confidence Level: {credibility}%")
        with col2:
            metric_card("Credibility Score", f"{credibility}/100")
        with col3:
            metric_card("Risk Score", f"{risk}/100")
            
        # Middle Row: Structured Analysis
        st.markdown("<br>", unsafe_allow_html=True)
        info_panel("AI Intelligence Report", analysis.replace("\n", "<br>"), icon="🤖")
            
        # Bottom Row: Dynamic Trusted Sources
        st.markdown("#### 📰 Dynamic Sources Checked")
        if trusted_sources:
            cols = st.columns(len(trusted_sources))
            for i, source in enumerate(trusted_sources):
                with cols[i]:
                    st.markdown(f"""
                    <div style='padding: 15px; background: #f0f2f6; border-radius: 8px; border-left: 4px solid #0068c9; margin-bottom: 10px; border: 1px solid #e6e9ef;'>
                        <h4 style='margin:0; font-size: 16px; color: #31333f; font-weight: 600;'>{source.get('name', 'Source')}</h4>
                        <p style='margin: 5px 0 10px 0; font-size: 13px; color: #6e7589;'>{source.get('desc', '')}</p>
                        <a href='{source.get('url', '#')}' target='_blank' style='color: #0068c9; text-decoration: none; font-size: 13px; font-weight: bold;'>View Source →</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No specific external sources linked for this claim.")

def render():
    if not is_logged_in() or get_role() != "user":
        st.warning("Unauthorized.")
        return
        
    page_wrapper("Citizen Verification Portal")
    st.markdown("#### 🛡️ Check suspicious crisis messages instantly")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Styled Tabs
    tab1, tab2 = st.tabs(["📝 Text Verification", "📸 Image Verification"])
    
    with tab1:
        st.markdown("**Paste suspicious text messages or claims here:**")
        text_input = st.text_area("Message Content", height=150, placeholder="Example: Flood in Pimpri Chinchwad evacuate now!", label_visibility="collapsed")
        if st.button("Verify Text", type="primary", use_container_width=True):
            process_verification(text_input, "text")
            
    with tab2:
        st.markdown("**Upload a screenshot of a suspicious message (PNG/JPG):**")
        uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", width=400)
            if st.button("Run OCR & Verify", type="primary", use_container_width=True):
                with st.spinner("🔍 Extracting text using OCR..."):
                    extracted_text = extract_text_from_image(uploaded_file)
                if extracted_text:
                    st.info(f"**Extracted Text:**\n{extracted_text}")
                    process_verification(extracted_text, "image")
                else:
                    st.error("❌ Could not extract text from the image. Please try a clearer screenshot.")

    st.markdown("---")
    st.markdown("### 🕒 Recent Verification History")
    
    try:
        recent = get_recent_reports(limit=5)
        if recent:
            df = pd.DataFrame(recent)
            # Format for display
            df = df[['timestamp', 'input_text', 'verdict', 'credibility_score']]
            df.columns = ['Timestamp', 'Message Snippet', 'Verdict', 'Credibility (%)']
            df['Message Snippet'] = df['Message Snippet'].apply(lambda x: x[:60] + "..." if len(x) > 60 else x)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent verifications found in your history.")
    except Exception as e:
        st.error("Could not load history.")

if __name__ == "__main__":
    render()
