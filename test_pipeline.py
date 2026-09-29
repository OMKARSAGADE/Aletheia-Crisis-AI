"""Crisis Information Verification & Intelligence Pipeline Test Suite."""
import os
from dotenv import load_dotenv

load_dotenv()

# If no GNews key is set in environment, ensure demo simulation works cleanly without failing
if not os.getenv("GNEWS_API_KEY"):
    os.environ["DEMO_MODE"] = "True"

from agents.orchestrator import run_pipeline

TESTS = [
    {
        "input": "Earthquake in Hingoli",
        "expect_location": "Hingoli",
        "expect_event": "Earthquake",
        "expect_verdict_contains": None,  # Supported or Unverified depending on API/Demo
        "description": "Geographic disaster query -- should extract Earthquake + Hingoli"
    },
    {
        "input": "Flood in Assam April 2026",
        "expect_location": "Assam",
        "expect_event": "Flood",
        "expect_verdict_contains": None,
        "description": "Temporal crisis query -- should extract Flood + Assam + April 2026"
    },
    {
        "input": "Fire in Mumbai building collapse",
        "expect_location": "Mumbai",
        "expect_event": "Fire",
        "expect_verdict_contains": None,
        "description": "Compound hazard text -- should prioritize primary hazard and location"
    },
    {
        "input": "Cyclone warning in Chennai",
        "expect_location": "Chennai",
        "expect_event": "Cyclone",
        "expect_verdict_contains": None,
        "description": "Coastal meteorological alert -- should extract Cyclone + Chennai"
    },
    {
        "input": "Random nonsense text with no crisis",
        "expect_location": None,
        "expect_event": None,
        "expect_verdict_contains": "Unverified",
        "description": "Non-crisis text -- should extract no event or location, marked Unverified"
    },
]

def run_tests():
    print("=" * 80)
    print("ALETHEIA CRISIS AI: MULTI-AGENT PIPELINE VALIDATION TEST SUITE")
    print("=" * 80)

    passed = 0
    failed = 0

    for i, test in enumerate(TESTS, 1):
        print(f"\n--- TEST {i}: {test['description']} ---")
        print(f"Input: \"{test['input']}\"")
        
        try:
            result = run_pipeline(test['input'])
            
            location = result.get('final_location')
            verdict = result.get('final_verdict', 'Unknown')
            credibility = result.get('final_credibility', 0)
            physical_severity = result.get('physical_severity', 0)
            misinfo_risk = result.get('misinformation_risk', 0)
            composite_risk = result.get('final_risk', 0)
            evidence = result.get('evidence_found', '')
            sources = result.get('trusted_sources', [])
            extracted = result.get('extracted_data', {})
            
            print(f"  Extracted Event:       {extracted.get('event')}")
            print(f"  Extracted Location:    {location}")
            print(f"  Extracted Date:        {extracted.get('date_context')}")
            print(f"  Cautious Verdict:      {verdict}")
            print(f"  Credibility Score:     {credibility}%")
            print(f"  Physical Severity:     {physical_severity}/100")
            print(f"  Misinformation Risk:   {misinfo_risk}/100")
            print(f"  Composite Triage Risk: {composite_risk}/100")
            print(f"  Evidence:              {evidence[:80]}...")
            print(f"  Sources ({len(sources)}):")
            for s in sources[:2]:
                print(f"    - {s.get('name','?')}: {s.get('desc','')[:50]}")
            
            # Validation rules
            errors = []
            
            # Location check
            if test['expect_location'] is None:
                if location not in [None, "Unknown", ""]:
                    errors.append(f"Location mismatch: expected None, got '{location}'")
            else:
                if not location or test['expect_location'].lower() != str(location).lower():
                    errors.append(f"Location mismatch: expected '{test['expect_location']}', got '{location}'")
                    
            # Event check
            if test['expect_event'] is None:
                if extracted.get('event') is not None:
                    errors.append(f"Event mismatch: expected None, got '{extracted.get('event')}'")
            else:
                if not extracted.get('event') or test['expect_event'].lower() != str(extracted.get('event')).lower():
                    errors.append(f"Event mismatch: expected '{test['expect_event']}', got '{extracted.get('event')}'")
                    
            # Verdict check
            if test['expect_verdict_contains']:
                if test['expect_verdict_contains'].lower() not in verdict.lower():
                    errors.append(f"Verdict mismatch: expected contains '{test['expect_verdict_contains']}', got '{verdict}'")
                    
            # Explainability check
            if not result.get("risk_explanation"):
                errors.append("Risk explanation is missing or empty")

            if errors:
                print(f"  [FAIL]: {'; '.join(errors)}")
                failed += 1
            else:
                print(f"  [PASS]")
                passed += 1
                
        except Exception as e:
            print(f"  [CRASH]: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(TESTS)} tests")
    print("=" * 80)
    return passed, failed

if __name__ == "__main__":
    run_tests()
