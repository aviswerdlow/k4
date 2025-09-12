#!/usr/bin/env python3
"""
Secondary path - Flint as plaintext, K1/K2/K3 as running key
Construct 97-char plaintext from Flint quotes and test if K1/K2/K3
as running keys can reproduce K4 ciphertext
"""

import json
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


def load_k_plaintexts() -> Dict[str, str]:
    """Load K1, K2, K3 plaintexts"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/02_DATA")
    k_texts = {}
    
    for k_num in [1, 2, 3]:
        k_path = base_path / f"k{k_num}_plaintext.txt"
        with open(k_path) as f:
            k_texts[f"K{k_num}"] = f.read().strip()
    
    return k_texts


def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25"""
    return ord(c) - ord('A')


def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z"""
    return chr((n % 26) + ord('A'))


def vigenere_encode(plaintext: str, key: str) -> str:
    """Vigenère encode: C = (P + K) mod 26"""
    result = []
    for p, k in zip(plaintext, key):
        c_val = (char_to_num(p) + char_to_num(k)) % 26
        result.append(num_to_char(c_val))
    return ''.join(result)


def beaufort_encode(plaintext: str, key: str) -> str:
    """Beaufort encode: C = (K - P) mod 26"""
    result = []
    for p, k in zip(plaintext, key):
        c_val = (char_to_num(k) - char_to_num(p)) % 26
        result.append(num_to_char(c_val))
    return ''.join(result)


def extract_running_key(source_text: str, offset: int, length: int) -> Optional[str]:
    """Extract running key from source text at given offset"""
    if offset < 0 or offset + length > len(source_text):
        return None
    return source_text[offset:offset + length]


def construct_flint_plaintext(quotes_dir: Path, anchors: Dict) -> str:
    """Construct 97-char plaintext using Flint quotes and anchors"""
    plaintext = ['?'] * 97  # Start with unknowns
    
    # Insert known anchors
    for anchor_name, anchor_data in anchors.items():
        start = anchor_data["start"]
        end = anchor_data["end"] + 1
        text = anchor_data["plaintext"]
        for i, char in enumerate(text):
            plaintext[start + i] = char
    
    # Fill in Flint content where appropriate
    # Head (0-20): Use part of Candidate A
    with open(quotes_dir / "candidate_A.json") as f:
        cand_a = json.load(f)
    head_text = cand_a["normalized_AZ"][:21]
    for i, char in enumerate(head_text):
        if plaintext[i] == '?':
            plaintext[i] = char
    
    # Middle (34-62): Use part of Candidate E
    with open(quotes_dir / "candidate_E.json") as f:
        cand_e = json.load(f)
    middle_text = cand_e["normalized_AZ"][:29]
    for i, char in enumerate(middle_text):
        if plaintext[34 + i] == '?' and (34 + i) < 63:
            plaintext[34 + i] = char
    
    # Tail (74-96): Use angle definition excerpt
    if (quotes_dir / "angle_definition.json").exists():
        with open(quotes_dir / "angle_definition.json") as f:
            angle_def = json.load(f)
        # Try to extract a meaningful portion
        tail_text = angle_def["normalized_AZ"][:23]
        for i, char in enumerate(tail_text):
            if 74 + i < 97 and plaintext[74 + i] == '?':
                plaintext[74 + i] = char
    
    return ''.join(plaintext)


def test_with_running_key(plaintext: str, key_source: str, key_name: str,
                         ciphertext: str, offset_range: int = 100) -> List[Dict]:
    """Test plaintext with running key at various offsets"""
    results = []
    
    # Try different offsets
    for offset in range(0, min(len(key_source) - 97, offset_range)):
        running_key = extract_running_key(key_source, offset, 97)
        if not running_key:
            continue
        
        # Test Vigenère encoding
        ct_test_v = vigenere_encode(plaintext, running_key)
        
        # Count matches with actual ciphertext
        matches_v = sum(1 for i in range(97) if plaintext[i] != '?' and ct_test_v[i] == ciphertext[i])
        known_positions = sum(1 for c in plaintext if c != '?')
        match_rate_v = matches_v / known_positions if known_positions > 0 else 0
        
        # Test Beaufort encoding
        ct_test_b = beaufort_encode(plaintext, running_key)
        matches_b = sum(1 for i in range(97) if plaintext[i] != '?' and ct_test_b[i] == ciphertext[i])
        match_rate_b = matches_b / known_positions if known_positions > 0 else 0
        
        # Only record if we have a decent match rate
        if match_rate_v > 0.5:
            results.append({
                "mode": "flint_as_plaintext",
                "key_source": key_name,
                "key_offset": offset,
                "decode_variant": "vigenere",
                "matches": matches_v,
                "known_positions": known_positions,
                "match_rate": match_rate_v,
                "sample_ct": ct_test_v[:40],
                "sample_key": running_key[:40]
            })
        
        if match_rate_b > 0.5:
            results.append({
                "mode": "flint_as_plaintext",
                "key_source": key_name,
                "key_offset": offset,
                "decode_variant": "beaufort",
                "matches": matches_b,
                "known_positions": known_positions,
                "match_rate": match_rate_b,
                "sample_ct": ct_test_b[:40],
                "sample_key": running_key[:40]
            })
    
    return results


def main():
    """Test Flint as plaintext with K1/K2/K3 as running keys"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    quotes_dir = base_path / "quotes"
    results_dir = base_path / "experiments/flint_otp/results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    k_texts = load_k_plaintexts()
    
    print("=" * 70)
    print("FLINT AS PLAINTEXT - K1/K2/K3 AS RUNNING KEYS")
    print("=" * 70)
    
    # Construct Flint-based plaintext
    plaintext = construct_flint_plaintext(quotes_dir, anchors)
    known_count = sum(1 for c in plaintext if c != '?')
    
    print(f"Constructed plaintext with {known_count}/97 known positions")
    print(f"Head (0-20): {plaintext[:21]}")
    print(f"Anchors: EAST @ 21-24, NORTHEAST @ 25-33")
    print(f"Middle (34-62): {plaintext[34:63]}")
    print(f"BERLIN @ 63-68, CLOCK @ 69-73")
    print(f"Tail (74-96): {plaintext[74:]}")
    print()
    
    # Test with each K plaintext as running key
    all_results = []
    
    for k_name, k_text in k_texts.items():
        print(f"\nTesting with {k_name} as running key (length={len(k_text)})...")
        results = test_with_running_key(plaintext, k_text, k_name, ciphertext)
        
        if results:
            print(f"  Found {len(results)} potential matches")
            best = max(results, key=lambda x: x['match_rate'])
            print(f"  Best match: {best['match_rate']:.1%} at offset {best['key_offset']}")
            print(f"    Variant: {best['decode_variant']}")
            print(f"    Key sample: {best['sample_key'][:30]}...")
            all_results.extend(results)
        else:
            print(f"  No significant matches found")
    
    # Save results
    if all_results:
        # Sort by match rate
        all_results.sort(key=lambda x: x['match_rate'], reverse=True)
        
        # Save top results
        output_file = results_dir / "flint_as_plaintext_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results[:10], f, indent=2)  # Top 10 results
        
        print(f"\nTop results saved to {output_file}")
        
        # Summary
        print("\n" + "=" * 70)
        print("TOP MATCHES:")
        for result in all_results[:5]:
            print(f"  {result['key_source']} @ offset {result['key_offset']}: "
                  f"{result['match_rate']:.1%} match ({result['decode_variant']})")
    else:
        print("\n" + "=" * 70)
        print("NO SIGNIFICANT MATCHES FOUND")
        print("K1/K2/K3 as running keys cannot reproduce K4 ciphertext")
        print("with Flint-based plaintext segments")
    
    # Write summary report
    summary_path = results_dir / "FLINT_AS_PLAINTEXT_SUMMARY.md"
    with open(summary_path, 'w') as f:
        f.write("# FLINT AS PLAINTEXT - TEST RESULTS\n\n")
        f.write("## Configuration\n\n")
        f.write(f"- Plaintext: Constructed from Flint quotes with {known_count}/97 known positions\n")
        f.write("- Running keys tested: K1, K2, K3 plaintexts\n")
        f.write("- Encoding methods: Vigenère (C = P + K) and Beaufort (C = K - P)\n\n")
        
        f.write("## Results\n\n")
        if all_results:
            f.write(f"Found {len(all_results)} potential matches above 50% threshold.\n\n")
            f.write("### Top Matches\n\n")
            f.write("| Key Source | Offset | Variant | Match Rate |\n")
            f.write("|------------|--------|---------|------------|\n")
            for result in all_results[:10]:
                f.write(f"| {result['key_source']} | {result['key_offset']} | ")
                f.write(f"{result['decode_variant']} | {result['match_rate']:.1%} |\n")
        else:
            f.write("**No significant matches found.**\n\n")
            f.write("K1/K2/K3 as running keys cannot reproduce K4 ciphertext ")
            f.write("with Flint-based plaintext segments at the anchor positions.\n")
        
        f.write("\n## Conclusion\n\n")
        f.write("The secondary path (Flint as plaintext with K1/K2/K3 as running keys) ")
        f.write("does not produce the K4 ciphertext at the required anchor positions.\n")
    
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()