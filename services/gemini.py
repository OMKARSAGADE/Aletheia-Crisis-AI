import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Try to configure Gemini API, but fail gracefully if not available
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

def generate_analysis(text, verdict, confidence, evidence="No specific evidence analyzed."):
    if model:
        try:
            prompt = f"""Analyze this crisis claim strictly using the format below. Do not output anything else.
Claim: '{text}'
Verdict: {verdict}
Confidence: {confidence}%
System Evidence Gathered: '{evidence}'

Format:
Verdict: [Insert Verdict]
Confidence: [Insert Confidence]%
Why: [1 clear sentence explaining why]
Evidence Found: [1 clear sentence citing the System Evidence Gathered]
Recommended Action: [Short, bulleted actionable advice]
"""
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            
    # Fallback if API key missing or error
    if "REAL" in verdict.upper():
        return f"Verdict: Likely Real\nConfidence: {confidence}%\nWhy: This claim aligns with recent official updates.\nEvidence Found: {evidence}\nRecommended Action: Follow local emergency advisories immediately."
    elif "FAKE" in verdict.upper():
        return f"Verdict: Likely False\nConfidence: {confidence}%\nWhy: This claim appears unreliable because no trusted sources confirm these details.\nEvidence Found: {evidence}\nRecommended Action: Do not forward. Check municipal updates."
    else:
        return f"Verdict: UNVERIFIED\nConfidence: {confidence}%\nWhy: Insufficient verifiable information to confirm or deny this claim at the moment.\nEvidence Found: {evidence}\nRecommended Action: Await official confirmation before sharing."

def generate_summary(text):
    if model:
        try:
            prompt = f"Provide a one-sentence summary of this crisis report: '{text}'"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            
    # Fallback
    return text[:60] + "..." if len(text) > 60 else text
