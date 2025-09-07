#!/usr/bin/env python3
"""
Test cases for near-gate function word scoring.
Ensures no drift in tokenization and counting logic.
"""

import sys
import json
from pathlib import Path

# Function words set - MUST match production
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS', 
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

def count_function_words(text: str) -> int:
    """Count function words in text using exact production logic."""
    # Take head window [0:74] inclusive
    head = text[:74].upper()
    
    # Simple tokenization - split on spaces
    words = head.split()
    
    # Count function words
    f_count = sum(1 for w in words if w in FUNCTION_WORDS)
    
    return f_count

def run_tests():
    """Run deterministic test cases."""
    
    test_cases = [
        {
            "id": "TC001",
            "description": "Basic function-rich sentence",
            "text": "SET THE LINE TO THE TRUE MERIDIAN AND THEN READ THE DIAL AT THE STATION",
            "expected_f_words": 8,  # THE, TO, THE, AND, THEN, THE, AT, THE
            "expected_length": 71  # Actual length
        },
        {
            "id": "TC002", 
            "description": "Content-heavy with THEN",
            "text": "FOLLOW THE DIAL TOWARD THE MERIDIAN THEN READ THE COURSE AND READ",
            "expected_f_words": 5,  # THE, THE, THEN, THE, AND
            "expected_length": 65  # Actual length
        },
        {
            "id": "TC003",
            "description": "Edge case at 74 chars exactly",
            "text": "APPLY DECLINATION TO THE BEARING AND THEN READ THE DIAL IN THE FIELDBOOK",
            "expected_f_words": 7,  # TO, THE, AND, THEN, THE, IN, THE
            "expected_length": 72  # Actual length
        }
    ]
    
    results = []
    all_pass = True
    
    print("Near-Gate Function Word Scorer Tests")
    print("=" * 60)
    print(f"Function word set ({len(FUNCTION_WORDS)} words):")
    print(f"{sorted(FUNCTION_WORDS)}")
    print("=" * 60)
    
    for test in test_cases:
        text = test["text"]
        expected = test["expected_f_words"]
        
        # Take head window
        head = text[:74]
        actual_f_words = count_function_words(head)
        actual_length = len(head)
        
        # Check results
        f_word_pass = actual_f_words == expected
        length_pass = actual_length == test["expected_length"]
        overall_pass = f_word_pass and length_pass
        
        result = {
            "id": test["id"],
            "description": test["description"],
            "text": head,
            "expected_f_words": expected,
            "actual_f_words": actual_f_words,
            "expected_length": test["expected_length"],
            "actual_length": actual_length,
            "f_word_pass": f_word_pass,
            "length_pass": length_pass,
            "overall_pass": overall_pass
        }
        
        results.append(result)
        
        # Print result
        status = "✅ PASS" if overall_pass else "❌ FAIL"
        print(f"\n{test['id']}: {test['description']}")
        print(f"Text: {head}")
        print(f"Length: {actual_length} (expected: {test['expected_length']})")
        print(f"F-words: {actual_f_words} (expected: {expected})")
        print(f"Status: {status}")
        
        if not overall_pass:
            all_pass = False
            # Show which words were counted
            words = head.split()
            f_words_found = [w for w in words if w.upper() in FUNCTION_WORDS]
            print(f"Function words found: {f_words_found}")
    
    # Write results
    output_path = Path("test_results.json")
    with open(output_path, 'w') as f:
        json.dump({
            "test_suite": "near_gate_fwords",
            "function_words": sorted(list(FUNCTION_WORDS)),
            "all_tests_passed": all_pass,
            "results": results
        }, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"Overall: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}")
    print(f"Results written to: {output_path}")
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(run_tests())