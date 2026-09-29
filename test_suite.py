"""Comprehensive Unit and Verification Test Suite for Aletheia Crisis AI."""
import pytest
from services.duplicates import check_duplicate_claim, normalize_text
from agents.risk_agent import run_risk
from agents.extraction_agent import run_extraction
from agents.verification_agent import run_verification
from services.auth import hash_password, verify_password

def test_text_normalization():
    raw = "Breaking: Urgent Flood In Pimpri Chinchwad! Evacuate NOW!! https://news.example.com"
    norm = normalize_text(raw)
    assert "breaking urgent flood in pimpri chinchwad evacuate now" in norm
    assert "http" not in norm

def test_duplicate_detection():
    existing = [
        {"id": 1, "input_text": "Urgent flood warning in Pimpri Chinchwad, evacuate immediately!", "verdict": "CONTRADICTED"},
        {"id": 2, "input_text": "Major fire breakout near Pune railway junction.", "verdict": "SUPPORTED"}
    ]
    
    # Near-duplicate query
    query = "Urgent flood alert in Pimpri Chinchwad, please evacuate now!"
    is_dup, sim, match, count = check_duplicate_claim(query, threshold=0.60, existing_reports=existing)
    
    assert is_dup is True
    assert sim >= 0.60
    assert match is not None
    assert match["id"] == 1
    assert count >= 1

    # Completely different query
    diff_query = "Cyclone warning issued along the coast of Odisha."
    is_dup2, sim2, _, _ = check_duplicate_claim(diff_query, threshold=0.60, existing_reports=existing)
    assert is_dup2 is False
    assert sim2 < 0.40

def test_risk_decoupling():
    # Scenario A: Real/Supported severe earthquake
    state_real = {
        "input_text": "Magnitude 6.4 earthquake struck Hingoli, severe structural tremors.",
        "extracted_data": {"is_crisis": True, "event": "Earthquake", "location": "Hingoli"},
        "verification_result": {"verdict": "SUPPORTED", "credibility": 88}
    }
    res_real = run_risk(state_real)["risk_result"]
    assert res_real["physical_severity"] >= 75  # High physical severity
    assert res_real["misinformation_risk"] <= 30  # Low misinformation risk
    assert "Physical Severity:" in res_real["explanation"]

    # Scenario B: Fake panic rumor
    state_fake = {
        "input_text": "Urgent! Chemical leak in city center, evacuate now, run for your lives!",
        "extracted_data": {"is_crisis": True, "event": "Leak", "location": "City Center"},
        "verification_result": {"verdict": "CONTRADICTED", "credibility": 10}
    }
    res_fake = run_risk(state_fake)["risk_result"]
    assert res_fake["misinformation_risk"] >= 80  # High misinformation danger / panic harm

    # Scenario C: Non-crisis text
    state_non = {
        "input_text": "The football team won the championship yesterday afternoon.",
        "extracted_data": {"is_crisis": False, "event": None, "location": None},
        "verification_result": {"verdict": "UNVERIFIED", "credibility": 15}
    }
    res_non = run_risk(state_non)["risk_result"]
    assert res_non["physical_severity"] <= 15
    assert res_non["misinformation_risk"] <= 15

def test_extraction_non_crisis():
    state = {"input_text": "Random nonsense text with no crisis"}
    res = run_extraction(state)
    data = res["extracted_data"]
    assert data["is_crisis"] is False
    assert data["event"] is None
    assert data["location"] is None

def test_extraction_known_crisis():
    state = {"input_text": "Flood in Assam April 2026"}
    res = run_extraction(state)
    data = res["extracted_data"]
    assert data["is_crisis"] is True
    assert data["event"] == "Flood"
    assert data["location"] == "Assam"
    assert "April 2026" in data["date_context"]

def test_auth_bcrypt_security():
    plain = "secureAdminPass2026"
    hashed = hash_password(plain)
    assert hashed.startswith("$2")
    assert verify_password(plain, hashed) is True
    assert verify_password("wrongPass", hashed) is False

if __name__ == "__main__":
    print("Running Aletheia Component Test Suite...")
    test_text_normalization()
    print("  [PASS] Text normalization test passed")
    test_duplicate_detection()
    print("  [PASS] Duplicate detection test passed")
    test_risk_decoupling()
    print("  [PASS] Risk decoupling test passed")
    test_extraction_non_crisis()
    print("  [PASS] Non-crisis extraction test passed")
    test_extraction_known_crisis()
    print("  [PASS] Crisis entity extraction test passed")
    test_auth_bcrypt_security()
    print("  [PASS] Bcrypt authentication test passed")
    print("\nALL UNIT TESTS PASSED SUCCESSFULLY!")
