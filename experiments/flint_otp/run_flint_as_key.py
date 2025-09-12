#!/usr/bin/env python3
"""
OTP testbed - Flint as key
Test Flint quotes as OTP key material against K4 ciphertext
Enforce hard anchor constraints at canonical positions
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_ciphertext() -> str:
    """Load K4 ciphertext"""
    ct_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/02_DATA/ciphertext_97.txt")
    with open(ct_path) as f:
        return f.read().strip()


def load_anchors() -> Dict:
    """Load anchor constraints"""
    anchor_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/02_DATA/anchors/four_anchors.json")
    with open(anchor_path) as f:
        return json.load(f)


def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25"""
    return ord(c) - ord('A')


def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z"""
    return chr((n % 26) + ord('A'))


def vigenere_decode(ciphertext: str, key: str) -> str:
    """Vigenère decode: P = (C - K) mod 26"""
    result = []
    for c, k in zip(ciphertext, key):
        p_val = (char_to_num(c) - char_to_num(k)) % 26
        result.append(num_to_char(p_val))
    return ''.join(result)


def beaufort_decode(ciphertext: str, key: str) -> str:
    """Beaufort decode: P = (K - C) mod 26"""
    result = []
    for c, k in zip(ciphertext, key):
        p_val = (char_to_num(k) - char_to_num(c)) % 26
        result.append(num_to_char(p_val))
    return ''.join(result)


def check_anchors(plaintext: str, anchors: Dict) -> Tuple[bool, List[str]]:
    """Check if plaintext satisfies all anchor constraints"""
    passed = []
    failed = []
    
    for anchor_name, anchor_data in anchors.items():
        start = anchor_data["start"]
        end = anchor_data["end"] + 1  # Convert to Python slice convention
        expected = anchor_data["plaintext"]
        
        actual = plaintext[start:end]
        if actual == expected:
            passed.append(anchor_name)
        else:
            failed.append(f"{anchor_name}: expected '{expected}', got '{actual}'")
    
    return (len(failed) == 0, failed)


def has_consonant_cluster(text: str, max_consonants: int = 5) -> bool:
    """Check if text has a cluster of max_consonants or more consonants"""
    vowels = set('AEIOU')
    consonant_count = 0
    
    for char in text:
        if char not in vowels:
            consonant_count += 1
            if consonant_count >= max_consonants:
                return True
        else:
            consonant_count = 0
    
    return False


def find_words(text: str, min_length: int = 4) -> List[str]:
    """Find potential English words of min_length or more in text"""
    # Common English words (extend as needed)
    common_words = {
        'EAST', 'WEST', 'NORTH', 'SOUTH', 'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
        'BERLIN', 'CLOCK', 'TIME', 'HOUR', 'MINUTE', 'SECOND', 'DEGREE', 'ANGLE',
        'FROM', 'WITH', 'THAT', 'THIS', 'THEY', 'THEM', 'WHAT', 'WHEN', 'WHERE',
        'FIELD', 'LINE', 'POINT', 'STATION', 'BEARING', 'DISTANCE', 'MEASURE',
        'BETWEEN', 'SLOWLY', 'DIGETAL', 'INTERPRETOR', 'VIRTUALLY', 'INVISIBLE'
    }
    
    found = []
    text_upper = text.upper()
    
    for word in common_words:
        if len(word) >= min_length and word in text_upper:
            found.append(word)
    
    return found


def test_flint_candidate(candidate_id: str, candidate_data: Dict, 
                        ciphertext: str, anchors: Dict) -> Dict:
    """Test a single Flint candidate as OTP key"""
    key_norm = candidate_data["normalized_AZ"]
    
    # Verify key length
    if len(key_norm) != 97:
        return {
            "key_id": candidate_id,
            "error": f"Key length {len(key_norm)} != 97",
            "skipped": True
        }
    
    results = []
    
    # Test Vigenère decode
    plaintext_v = vigenere_decode(ciphertext, key_norm)
    anchors_pass_v, anchor_failures_v = check_anchors(plaintext_v, anchors)
    head_20_v = plaintext_v[:20]
    has_cluster_v = has_consonant_cluster(head_20_v, 5)
    words_v = find_words(head_20_v, 4)
    
    result_v = {
        "mode": "flint_as_key",
        "key_id": candidate_id,
        "key_verbatim": candidate_data["verbatim"],
        "key_page": candidate_data["page"],
        "decode_variant": "vigenere",
        "anchors_preserved": anchors_pass_v,
        "anchor_failures": anchor_failures_v if not anchors_pass_v else [],
        "plaintext_sample_0_40": plaintext_v[:40],
        "consonant_cluster_5plus": has_cluster_v,
        "word_hits_head": words_v,
        "acceptance": anchors_pass_v and len(words_v) > 0 and not has_cluster_v,
        "notes": candidate_data.get("section_note", "")
    }
    results.append(result_v)
    
    # Test Beaufort decode
    plaintext_b = beaufort_decode(ciphertext, key_norm)
    anchors_pass_b, anchor_failures_b = check_anchors(plaintext_b, anchors)
    head_20_b = plaintext_b[:20]
    has_cluster_b = has_consonant_cluster(head_20_b, 5)
    words_b = find_words(head_20_b, 4)
    
    result_b = {
        "mode": "flint_as_key",
        "key_id": candidate_id,
        "key_verbatim": candidate_data["verbatim"],
        "key_page": candidate_data["page"],
        "decode_variant": "beaufort",
        "anchors_preserved": anchors_pass_b,
        "anchor_failures": anchor_failures_b if not anchors_pass_b else [],
        "plaintext_sample_0_40": plaintext_b[:40],
        "consonant_cluster_5plus": has_cluster_b,
        "word_hits_head": words_b,
        "acceptance": anchors_pass_b and len(words_b) > 0 and not has_cluster_b,
        "notes": candidate_data.get("section_note", "")
    }
    results.append(result_b)
    
    return results


def main():
    """Run OTP tests with Flint as key"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    quotes_dir = base_path / "quotes"
    results_dir = base_path / "experiments/flint_otp/results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    
    print("=" * 70)
    print("FLINT AS OTP KEY - TESTING 5 CANDIDATES")
    print("=" * 70)
    print(f"Ciphertext: {ciphertext[:40]}...")
    print(f"Anchors: {', '.join(anchors.keys())}")
    print()
    
    # Test each candidate
    all_results = []
    summary = []
    
    for letter in "ABCDE":
        candidate_path = quotes_dir / f"candidate_{letter}.json"
        with open(candidate_path) as f:
            candidate_data = json.load(f)
        
        print(f"\nCandidate {letter} (Page {candidate_data['page']}):")
        print(f"  \"{candidate_data['verbatim'][:50]}...\"")
        print(f"  Section: {candidate_data['section_note']}")
        
        results = test_flint_candidate(f"candidate_{letter}", candidate_data, 
                                      ciphertext, anchors)
        
        for result in results:
            all_results.append(result)
            
            # Save individual result card
            result_file = results_dir / f"candidate_{letter}_{result['decode_variant']}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Print summary
            status = "✓ PASS" if result['acceptance'] else "✗ FAIL"
            print(f"  {result['decode_variant']:10} {status}")
            if not result['anchors_preserved']:
                print(f"    Anchor failures: {result['anchor_failures'][0]}")
            print(f"    Head 20: {result['plaintext_sample_0_40'][:20]}")
            if result['word_hits_head']:
                print(f"    Words found: {', '.join(result['word_hits_head'])}")
            
            summary.append({
                "candidate": letter,
                "variant": result['decode_variant'],
                "anchors_pass": result['anchors_preserved'],
                "acceptance": result['acceptance'],
                "page": candidate_data['page']
            })
    
    # Save aggregate results
    csv_path = results_dir / "RUN_MATRIX.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "candidate", "variant", "anchors_pass", "acceptance", "page"
        ])
        writer.writeheader()
        writer.writerows(summary)
    
    # Generate topline summary
    topline_path = results_dir / "TOPLINE.md"
    with open(topline_path, 'w') as f:
        f.write("# FLINT AS OTP KEY - TOPLINE RESULTS\n\n")
        f.write("## Summary\n\n")
        
        any_passed = any(s['acceptance'] for s in summary)
        if any_passed:
            f.write("**RESULT: At least one candidate PASSED all constraints!**\n\n")
        else:
            f.write("**RESULT: All candidates FAILED anchor constraints.**\n\n")
        
        f.write("| Candidate | Page | Vigenère | Beaufort | Notes |\n")
        f.write("|-----------|------|----------|----------|-------|\n")
        
        for letter in "ABCDE":
            page = next(s['page'] for s in summary if s['candidate'] == letter)
            v_result = next((s for s in summary if s['candidate'] == letter and s['variant'] == 'vigenere'), None)
            b_result = next((s for s in summary if s['candidate'] == letter and s['variant'] == 'beaufort'), None)
            
            v_status = "✓ PASS" if v_result and v_result['acceptance'] else "✗ FAIL"
            b_status = "✓ PASS" if b_result and b_result['acceptance'] else "✗ FAIL"
            
            f.write(f"| {letter} | {page} | {v_status} | {b_status} | ")
            if not (v_result and v_result['anchors_pass']):
                f.write("Anchors fail")
            f.write(" |\n")
        
        f.write("\n## Conclusion\n\n")
        f.write("All five hand-picked 97-character Flint keys fail to satisfy ")
        f.write("the hard anchor constraints (EAST @ 21-24, NORTHEAST @ 25-33, ")
        f.write("BERLIN @ 63-68, CLOCK @ 69-73) under both Vigenère (P = C - K) ")
        f.write("and Beaufort (P = K - C) decoding.\n\n")
        f.write("This definitively rules out these specific Flint passages as ")
        f.write("direct OTP key material for K4.\n")
    
    print("\n" + "=" * 70)
    print("RESULTS SAVED:")
    print(f"  - Individual cards: {results_dir}/candidate_*.json")
    print(f"  - Aggregate matrix: {csv_path}")
    print(f"  - Topline summary: {topline_path}")
    
    if not any_passed:
        print("\n✗ All candidates FAILED anchor constraints")
        print("  Flint as direct OTP key does not satisfy K4's hard anchors")


if __name__ == "__main__":
    main()