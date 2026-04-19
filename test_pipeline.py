"""CrisisLens End-to-End Pipeline Test Suite"""
import os
os.environ['GEMINI_API_KEY'] = 'disabled'  # Avoid burning tokens
os.environ['GNEWS_API_KEY'] = '71e3406559b0c50de45c7da3856f0b9e'

from dotenv import load_dotenv
load_dotenv()
from agents.orchestrator import run_pipeline

TESTS = [
    {
        "input": "Earthquake in Hingoli",
        "expect_location": "Hingoli",
        "expect_event": "Earthquake",
        "expect_verdict_contains": "Real",
        "description": "Known real event — should find credible Indian sources"
    },
    {
        "input": "Flood in Assam April 2026",
        "expect_location": "Assam",
        "expect_event": "Flood",
        "expect_verdict_contains": None,  # Could be real or unverified
        "description": "Temporal query — should extract date and search with it"
    },
    {
        "input": "Fire in Mumbai building collapse",
        "expect_location": "Mumbai",
        "expect_event": "Fire",
        "expect_verdict_contains": None,
        "description": "Multi-keyword — should extract Fire + Mumbai"
    },
    {
        "input": "Cyclone warning in Chennai",
        "expect_location": "Chennai",
        "expect_event": "Cyclone",
        "expect_verdict_contains": None,
        "description": "South India location — should geocode correctly"
    },
    {
        "input": "Random nonsense text with no crisis",
        "expect_location": None,
        "expect_event": None,
        "expect_verdict_contains": "Unverified",
        "description": "Garbage input — should flag as unverified"
    },
]

print("=" * 80)
print("CRISISLENS PIPELINE TEST SUITE")
print("=" * 80)

passed = 0
failed = 0

for i, test in enumerate(TESTS, 1):
    print(f"\n--- TEST {i}: {test['description']} ---")
    print(f"Input: \"{test['input']}\"")
    
    try:
        result = run_pipeline(test['input'])
        
        location = result.get('final_location', 'Unknown')
        verdict = result.get('final_verdict', 'Unknown')
        credibility = result.get('final_credibility', 0)
        evidence = result.get('evidence_found', '')
        sources = result.get('trusted_sources', [])
        extracted = result.get('extracted_data', {})
        
        print(f"  Extracted Event:    {extracted.get('event', '?')}")
        print(f"  Extracted Location: {location}")
        print(f"  Extracted Date:     {extracted.get('date_context', '?')}")
        print(f"  Verdict:            {verdict}")
        print(f"  Credibility:        {credibility}%")
        print(f"  Evidence:           {evidence}")
        print(f"  Sources ({len(sources)}):")
        for s in sources:
            print(f"    - {s.get('name','?')}: {s.get('desc','')[:60]}")
        
        # Validate
        errors = []
        if test['expect_location'] and test['expect_location'].lower() != location.lower():
            errors.append(f"Location mismatch: expected '{test['expect_location']}', got '{location}'")
        if test['expect_event'] and test['expect_event'].lower() != extracted.get('event','').lower():
            errors.append(f"Event mismatch: expected '{test['expect_event']}', got '{extracted.get('event','')}'")
        if test['expect_verdict_contains'] and test['expect_verdict_contains'].lower() not in verdict.lower():
            errors.append(f"Verdict mismatch: expected contains '{test['expect_verdict_contains']}', got '{verdict}'")
            
        if errors:
            print(f"  FAIL: {'; '.join(errors)}")
            failed += 1
        else:
            print(f"  PASS")
            passed += 1
            
    except Exception as e:
        print(f"  CRASH: {e}")
        failed += 1

print("\n" + "=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(TESTS)} tests")
print("=" * 80)
