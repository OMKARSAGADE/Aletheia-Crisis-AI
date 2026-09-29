"""Citizen Verification Portal: Submit text or screenshot claims,
detect duplicates, and receive verified intelligence briefings with separated risk scores.
"""
import streamlit as st
import pandas as pd
from components.layout import page_wrapper
from components.cards import metric_card, verdict_badge, info_panel
from services.auth import get_role, is_logged_in
from agents.orchestrator import run_pipeline
from services.db import save_report, get_recent_reports
from services.ocr import extract_text_from_image, is_ocr_available
from services.gemini import generate_analysis
from services.duplicates import check_duplicate_claim
import time

def process_verification(input_text: str, source_type: str):
    clean_text = input_text.strip()
    if not clean_text:
        st.warning("⚠️ Please provide text or an image containing text to verify.")
        return

    # Check for duplicate / similar claims in the database
    is_dup, similarity, matched_rep, cluster_count = check_duplicate_claim(clean_text)
    if is_dup and matched_rep:
        st.warning(
            f"ℹ️ **High-Similarity Claim Detected ({int(similarity * 100)}% match):** "
            f"A similar report was previously cataloged with status **{matched_rep.get('verdict', 'UNVERIFIED')}**. "
            f"Cluster report frequency: **{cluster_count} occurrence(s)**."
        )

    with st.spinner("🧠 Analyzing claim through LangGraph multi-agent pipeline..."):
        try:
            result = run_pipeline(clean_text)
            verdict = result.get("final_verdict", "UNVERIFIED")
            credibility = result.get("final_credibility", 50)
            composite_risk = result.get("final_risk", 50)
            physical_severity = result.get("physical_severity", 50)
            misinfo_risk = result.get("misinformation_risk", 50)
            risk_explanation = result.get("risk_explanation", "")
            location = result.get("final_location", "Unknown")
            trusted_sources = result.get("trusted_sources", [])
            evidence = result.get("evidence_found", "No evidence available.")
            citizen_action = result.get("citizen_action", "")
            has_simulated = result.get("has_simulated_sources", False)
        except Exception as e:
            st.error(f"Pipeline Analysis Failed: {str(e)}")
            return

    with st.spinner("🤖 Formulating intelligence synthesis..."):
        analysis = generate_analysis(clean_text, verdict, credibility, evidence)
        
        # Save to database
        try:
            save_report(
                input_text=clean_text,
                verdict=verdict,
                credibility_score=credibility,
                risk_score=composite_risk,
                source_type=source_type,
                location=location,
                physical_severity=physical_severity,
                misinformation_risk=misinfo_risk,
                is_simulated=1 if has_simulated else 0
            )
        except Exception as e:
            st.warning("Analysis generated, but could not save to persistent history.")
        
        st.markdown("---")
        st.markdown("### 📊 Crisis Intelligence Assessment")

        if has_simulated:
            st.info("ℹ️ **Notice:** External news APIs are running in demonstration mode. Corroborating sources below are labeled as simulated.")

        # Row 1: Verdict Badge & Separated Numerical Scores
        verdict_badge(verdict)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Credibility Score", f"{credibility}/100", "Evidence Strength")
        with col2:
            metric_card("Physical Severity", f"{physical_severity}/100", "Incident Danger")
        with col3:
            metric_card("Misinfo Risk", f"{misinfo_risk}/100", "Harm Potential")
        with col4:
            metric_card("Operational Priority", f"{composite_risk}/100", "Triage Urgency")

        # Row 2: Explainable Risk Rationale & Action Guidance
        st.markdown("<br>", unsafe_allow_html=True)
        if risk_explanation:
            info_panel("Explainable Risk Breakdown", risk_explanation, icon="📐")

        if citizen_action:
            st.markdown(f"""
            <div style='padding: 16px; border-radius: 8px; background: #f0fdf4; border-left: 4px solid #16a34a; border: 1px solid #bbf7d0; margin-bottom: 20px;'>
                <h4 style='margin: 0 0 6px 0; color: #166534; font-size: 16px; font-weight: 600;'>🛡️ Citizen Action Guidance</h4>
                <p style='margin: 0; color: #15803d; font-size: 14px;'>{citizen_action}</p>
            </div>
            """, unsafe_allow_html=True)

        # Row 3: Structured AI Intelligence Report
        info_panel("AI Intelligence Report", analysis.replace("\n", "<br>"), icon="🤖")
            
        # Row 4: Evidence Sources
        st.markdown("#### 📰 Investigated Evidence Sources")
        if trusted_sources:
            cols = st.columns(min(3, len(trusted_sources)))
            for i, source in enumerate(trusted_sources[:3]):
                with cols[i]:
                    sim_tag = "<span style='color: #d97706; font-size: 11px; font-weight: bold;'>[SIMULATED]</span> " if source.get('is_simulated') else ""
                    st.markdown(f"""
                    <div style='padding: 15px; background: #ffffff; border-radius: 8px; border-left: 4px solid #0068c9; margin-bottom: 10px; border: 1px solid #e6e9ef;'>
                        <h4 style='margin:0; font-size: 15px; color: #31333f; font-weight: 600;'>{sim_tag}{source.get('name', 'Source')}</h4>
                        <p style='margin: 6px 0 10px 0; font-size: 13px; color: #6e7589;'>{source.get('desc', '')}</p>
                        <a href='{source.get('url', '#')}' target='_blank' style='color: #0068c9; text-decoration: none; font-size: 13px; font-weight: bold;'>View Source →</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No corroborating external sources discovered for this claim. Treat with high caution.")

def render():
    if not is_logged_in() or get_role() != "user":
        st.warning("Unauthorized. Please log in as a Citizen.")
        return
        
    page_wrapper("Citizen Verification Portal")
    st.markdown("#### 🛡️ Verify Crisis Claims & Screen Misinformation")
    st.caption("Cross-reference suspicious disaster messages, rumors, and evacuation calls against live intelligence feeds.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Text Verification", "📸 Image / Screenshot OCR"])
    
    with tab1:
        st.markdown("**Paste suspicious message, rumor, or social media post:**")
        text_input = st.text_area(
            "Message Content",
            height=130,
            placeholder="Example: Urgent! Flood waters breaching dam near Pimpri Chinchwad, evacuate immediately!",
            label_visibility="collapsed"
        )
        if st.button("Verify Claim", type="primary", use_container_width=True):
            process_verification(text_input, "text")
            
    with tab2:
        ocr_ready, ocr_msg = is_ocr_available()
        st.caption(f"OCR Status: {ocr_msg}")
        st.markdown("**Upload a screenshot or photo of a suspicious message (PNG/JPG):**")
        uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", width=380)
            if st.button("Extract Text & Verify", type="primary", use_container_width=True):
                with st.spinner("🔍 Extracting text using OCR / Vision engine..."):
                    extracted_text = extract_text_from_image(uploaded_file)
                if extracted_text and extracted_text.strip():
                    st.info(f"**Extracted Text:**\n\n{extracted_text}")
                    process_verification(extracted_text, "image")
                else:
                    st.error("❌ Could not extract legible text from image. Please ensure text is legible or paste text directly.")

    st.markdown("---")
    st.markdown("### 🕒 Recent Verification History")
    
    try:
        recent = get_recent_reports(limit=6)
        if recent:
            df = pd.DataFrame(recent)
            cols_to_show = ['timestamp', 'input_text', 'location', 'verdict', 'credibility_score', 'risk_score']
            existing_cols = [c for c in cols_to_show if c in df.columns]
            df_display = df[existing_cols].copy()
            df_display.rename(columns={
                'timestamp': 'Timestamp',
                'input_text': 'Claim Message',
                'location': 'Location',
                'verdict': 'Status',
                'credibility_score': 'Credibility (%)',
                'risk_score': 'Priority Risk'
            }, inplace=True)
            df_display['Claim Message'] = df_display['Claim Message'].apply(lambda x: str(x)[:55] + "..." if len(str(x)) > 55 else str(x))
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No prior verifications recorded.")
    except Exception as e:
        st.error(f"Could not load verification history: {e}")

if __name__ == "__main__":
    render()
