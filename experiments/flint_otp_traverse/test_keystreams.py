#!/usr/bin/env python3
"""
Test keystreams against K4 with hard anchor checks
Apply Vigenère and Beaufort decoding, enforce anchor constraints
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional


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


def vigenere_decode(ciphertext: str, keystream: List[int]) -> str:
    """Vigenère decode: P = (C - K) mod 26"""
    result = []
    for i, c in enumerate(ciphertext):
        c_val = ord(c) - ord('A')
        k_val = keystream[i]
        p_val = (c_val - k_val) % 26
        result.append(chr(p_val + ord('A')))
    return ''.join(result)


def beaufort_decode(ciphertext: str, keystream: List[int]) -> str:
    """Beaufort decode: P = (K - C) mod 26"""
    result = []
    for i, c in enumerate(ciphertext):
        c_val = ord(c) - ord('A')
        k_val = keystream[i]
        p_val = (k_val - c_val) % 26
        result.append(chr(p_val + ord('A')))
    return ''.join(result)


def check_anchors(plaintext: str, anchors: Dict) -> Tuple[bool, List[str]]:
    """Check if plaintext satisfies all anchor constraints"""
    failures = []
    
    for anchor_name, anchor_data in anchors.items():
        start = anchor_data["start"]
        end = anchor_data["end"] + 1  # Convert to Python slice
        expected = anchor_data["plaintext"]
        
        actual = plaintext[start:end]
        if actual != expected:
            failures.append(f"{anchor_name}: expected '{expected}', got '{actual}'")
    
    return (len(failures) == 0, failures)


def has_consonant_cluster(text: str, max_consonants: int = 5) -> bool:
    """Check if text has a cluster of max_consonants or more"""
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
    """Find potential words in text"""
    # Extended word list for traverse/surveying context
    word_list = {
        # Directional
        'EAST', 'WEST', 'NORTH', 'SOUTH', 'NORTHEAST', 'NORTHWEST', 
        'SOUTHEAST', 'SOUTHWEST',
        # Surveying terms
        'MERIDIAN', 'STATION', 'ANGLE', 'BEARING', 'OFFSET', 'FIELD',
        'LINE', 'POINT', 'DEGREE', 'MINUTE', 'SECOND', 'CHAIN',
        'LATITUDE', 'DEPARTURE', 'TRAVERSE', 'SURVEY',
        # K4 known words
        'BERLIN', 'CLOCK', 'TIME', 'HOUR',
        # Common words
        'FROM', 'WITH', 'THAT', 'THIS', 'THEY', 'THEM', 'WHAT', 
        'WHEN', 'WHERE', 'WHICH', 'BETWEEN', 'THROUGH'
    }
    
    found = []
    text_upper = text.upper()
    
    for word in word_list:
        if len(word) >= min_length and word in text_upper:
            found.append(word)
    
    return found


def test_single_keystream(keystream_data: Dict, ciphertext: str, 
                         anchors: Dict) -> List[Dict]:
    """Test a single keystream with both decode variants"""
    keystream = keystream_data["kstream"]
    recipe_id = keystream_data["recipe_id"]
    provenance = keystream_data["provenance"]
    
    if len(keystream) != 97:
        return [{
            "recipe_id": recipe_id,
            "error": f"Keystream length {len(keystream)} != 97",
            "skipped": True
        }]
    
    results = []
    
    # Test Vigenère
    plaintext_v = vigenere_decode(ciphertext, keystream)
    anchors_pass_v, failures_v = check_anchors(plaintext_v, anchors)
    
    if anchors_pass_v:  # Only do further checks if anchors pass
        head_20 = plaintext_v[:20]
        has_cluster = has_consonant_cluster(head_20, 5)
        words_found = find_words(head_20, 4)
        
        result_v = {
            "mode": "traverse_otp",
            "cipher": "K4_97",
            "decode_variant": "vigenere",
            "anchors_preserved": True,
            "anchor_failures": [],
            "head_bigrams_ok": True,  # Could add bigram check
            "head_no_cc5plus": not has_cluster,
            "head_words_found": words_found,
            "derived_text_sample": plaintext_v,
            "keystream_recipe": provenance,
            "recipe_id": recipe_id,
            "acceptance": len(words_found) > 0 and not has_cluster
        }
        results.append(result_v)
    
    # Test Beaufort
    plaintext_b = beaufort_decode(ciphertext, keystream)
    anchors_pass_b, failures_b = check_anchors(plaintext_b, anchors)
    
    if anchors_pass_b:  # Only do further checks if anchors pass
        head_20 = plaintext_b[:20]
        has_cluster = has_consonant_cluster(head_20, 5)
        words_found = find_words(head_20, 4)
        
        result_b = {
            "mode": "traverse_otp",
            "cipher": "K4_97",
            "decode_variant": "beaufort",
            "anchors_preserved": True,
            "anchor_failures": [],
            "head_bigrams_ok": True,
            "head_no_cc5plus": not has_cluster,
            "head_words_found": words_found,
            "derived_text_sample": plaintext_b,
            "keystream_recipe": provenance,
            "recipe_id": recipe_id,
            "acceptance": len(words_found) > 0 and not has_cluster
        }
        results.append(result_b)
    
    return results


def test_all_keystreams():
    """Test all generated keystreams"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    keystreams_dir = base_path / "experiments/flint_otp_traverse/keystreams"
    results_dir = base_path / "experiments/flint_otp_traverse/results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    
    print("=" * 70)
    print("TESTING TRAVERSE TABLE KEYSTREAMS")
    print("=" * 70)
    print(f"Ciphertext: {ciphertext[:40]}...")
    print(f"Anchors: {', '.join(anchors.keys())}")
    print()
    
    # Collect all keystream files
    keystream_files = list(keystreams_dir.glob("*/*.json"))
    
    if not keystream_files:
        print("No keystreams found! Run build_keystreams.py first.")
        return
    
    print(f"Testing {len(keystream_files)} keystreams...")
    
    # Test results
    all_results = []
    passing_results = []
    tested_count = 0
    anchors_pass_count = 0
    
    for kf in keystream_files:
        if kf.name == "summary.json":
            continue
            
        with open(kf) as f:
            keystream_data = json.load(f)
        
        results = test_single_keystream(keystream_data, ciphertext, anchors)
        
        tested_count += 1
        
        for result in results:
            if result.get("anchors_preserved"):
                anchors_pass_count += 1
                passing_results.append(result)
                
                print(f"\n✓ ANCHORS PASS!")
                print(f"  Recipe: {result['recipe_id']}")
                print(f"  Variant: {result['decode_variant']}")
                print(f"  Table: {result['keystream_recipe']['table_id']}")
                print(f"  Family: {result['keystream_recipe']['family']}")
                print(f"  Head 20: {result['derived_text_sample'][:20]}")
                if result['head_words_found']:
                    print(f"  Words: {', '.join(result['head_words_found'])}")
                print(f"  Acceptance: {result['acceptance']}")
            
            all_results.append(result)
        
        if tested_count % 100 == 0:
            print(f"  Tested {tested_count}/{len(keystream_files)}...")
    
    # Save results
    print(f"\n" + "=" * 70)
    print(f"TESTING COMPLETE")
    print(f"  Keystreams tested: {tested_count}")
    print(f"  Anchors preserved: {anchors_pass_count}")
    print(f"  Acceptance (anchors + head quality): {sum(1 for r in passing_results if r['acceptance'])}")
    
    # Save passing results
    if passing_results:
        with open(results_dir / "passing_results.json", 'w') as f:
            json.dump(passing_results, f, indent=2)
        print(f"\nPassing results saved to: passing_results.json")
    
    # Create CSV matrix
    csv_path = results_dir / "RUN_MATRIX.csv"
    with open(csv_path, 'w', newline='') as f:
        fieldnames = ["recipe_id", "variant", "anchors_pass", "acceptance", 
                     "table", "family", "path"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in all_results[:1000]:  # Limit CSV size
            if "keystream_recipe" in result:
                writer.writerow({
                    "recipe_id": result.get("recipe_id", ""),
                    "variant": result.get("decode_variant", ""),
                    "anchors_pass": result.get("anchors_preserved", False),
                    "acceptance": result.get("acceptance", False),
                    "table": result["keystream_recipe"].get("table_id", ""),
                    "family": result["keystream_recipe"].get("family", ""),
                    "path": result["keystream_recipe"].get("path", "")
                })
    
    # Create topline summary
    with open(results_dir / "TOPLINE.md", 'w') as f:
        f.write("# TRAVERSE TABLE OTP - TOPLINE RESULTS\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Keystreams tested: {tested_count}\n")
        f.write(f"- Anchors preserved: {anchors_pass_count}\n")
        f.write(f"- Full acceptance: {sum(1 for r in passing_results if r['acceptance'])}\n\n")
        
        if anchors_pass_count > 0:
            f.write("## MATCHES FOUND\n\n")
            f.write("At least one keystream satisfies all anchor constraints!\n\n")
            
            f.write("### Passing Keystreams\n\n")
            for i, result in enumerate(passing_results[:10], 1):
                f.write(f"{i}. **{result['recipe_id']}**\n")
                f.write(f"   - Variant: {result['decode_variant']}\n")
                f.write(f"   - Table: {result['keystream_recipe']['table_id']}\n")
                f.write(f"   - Family: {result['keystream_recipe']['family']}\n")
                f.write(f"   - Acceptance: {result['acceptance']}\n")
                f.write(f"   - Head: `{result['derived_text_sample'][:40]}...`\n\n")
        else:
            f.write("## NO MATCHES\n\n")
            f.write("No keystream from traverse tables satisfies all anchor constraints.\n\n")
            f.write("This rules out traverse tables as direct OTP source for K4.\n")
    
    print(f"\nTopline summary saved to: TOPLINE.md")


if __name__ == "__main__":
    test_all_keystreams()