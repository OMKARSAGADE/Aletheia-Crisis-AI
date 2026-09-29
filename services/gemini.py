"""Google Gemini LLM Integration Service.
Provides robust text analysis, intelligence report synthesis,
and extraction capabilities with graceful fallbacks and error handling.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

_cached_model = None
_configured_key = None

def get_model():
    """Retrieve or initialize configured Gemini GenerativeModel instance."""
    global _cached_model, _configured_key
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    # If no key or placeholder/disabled
    if not api_key or api_key in ["your_gemini_api_key_here", "disabled", "none", ""]:
        return None
        
    if _cached_model is not None and _configured_key == api_key:
        return _cached_model
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _cached_model = genai.GenerativeModel('gemini-2.0-flash')
        _configured_key = api_key
        return _cached_model
    except Exception as e:
        print(f"Gemini configuration error: {e}")
        return None

# For backward compatibility with existing imports:
class _ModelProxy:
    def __getattr__(self, name):
        m = get_model()
        if m is None:
            raise AttributeError("Gemini model is not configured or unavailable.")
        return getattr(m, name)
    
    def __bool__(self):
        return get_model() is not None

model = _ModelProxy()

def generate_analysis(text: str, verdict: str, confidence: int, evidence: str = "No specific evidence analyzed.") -> str:
    """Generate structured crisis intelligence report using LLM or structured fallback."""
    m = get_model()
    if m:
        try:
            prompt = f"""You are an expert Crisis Verification and Intelligence Analyst. Analyze this claim objectively.
Claim: '{text}'
Verification Status: {verdict}
Evidence Strength / Credibility: {confidence}%
Investigated Evidence: '{evidence}'

Rules:
1. Treat news articles as evidence to investigate, not automatic conclusive proof.
2. Use cautious terminology (Supported, Contradicted, Unverified, Conflicting).
3. Do not induce panic.

Format your output strictly as:
Verdict: [Supported / Contradicted / Unverified / Conflicting]
Credibility: {confidence}%
Why: [1 clear sentence explaining why based on the evidence]
Evidence Found: [1 clear sentence summarizing investigated sources or lack thereof]
Recommended Action: [Short, bulleted actionable advice for citizens and first responders]
"""
            response = m.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini API Analysis Error: {e}")

    # Deterministic fallback when Gemini is unavailable or errors
    v_upper = verdict.upper()
    if "SUPPORTED" in v_upper or "REAL" in v_upper:
        return (
            f"Verdict: Supported\n"
            f"Credibility: {confidence}%\n"
            f"Why: This claim is corroborated by reports from recognized regional monitoring channels.\n"
            f"Evidence Found: {evidence}\n"
            f"Recommended Action:\n"
            f"• Follow official local emergency management advisories.\n"
            f"• Avoid speculation and monitor verified municipal channels."
        )
    elif "CONTRADICTED" in v_upper or "FAKE" in v_upper:
        return (
            f"Verdict: Contradicted\n"
            f"Credibility: {confidence}%\n"
            f"Why: Official sources or verified reports refute this claim or indicate it is fabricated.\n"
            f"Evidence Found: {evidence}\n"
            f"Recommended Action:\n"
            f"• Do not share or forward this claim.\n"
            f"• Refer citizens to official district disaster portals."
        )
    elif "CONFLICTING" in v_upper:
        return (
            f"Verdict: Conflicting\n"
            f"Credibility: {confidence}%\n"
            f"Why: Divergent or contradictory claims exist between reporting outlets; facts remain contested.\n"
            f"Evidence Found: {evidence}\n"
            f"Recommended Action:\n"
            f"• Exercise caution and wait for official civil authority confirmation."
        )
    else:
        return (
            f"Verdict: Unverified\n"
            f"Credibility: {confidence}%\n"
            f"Why: Insufficient verifiable evidence to corroborate or refute this claim at this time.\n"
            f"Evidence Found: {evidence}\n"
            f"Recommended Action:\n"
            f"• Treat this report with caution.\n"
            f"• Await official confirmation before taking protective measures or spreading information."
        )

def generate_summary(text: str) -> str:
    """Generate concise one-sentence intelligence summary."""
    m = get_model()
    if m:
        try:
            prompt = f"Provide a single concise summary sentence of this crisis incident report: '{text}'"
            response = m.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini Summary Error: {e}")
            
    return text[:80] + "..." if len(text) > 80 else text
