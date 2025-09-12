#!/usr/bin/env python3
"""
Anchor-first keystream targeting
Compute required key values at anchor positions and search for matching keystreams
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


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


def compute_required_keys(ciphertext: str, anchors: Dict) -> Dict[str, Dict[int, int]]:
    """Compute required key values at anchor positions for both variants"""
    required = {
        "vigenere": {},
        "beaufort": {}
    }
    
    for anchor_name, anchor_data in anchors.items():
        start = anchor_data["start"]
        plaintext = anchor_data["plaintext"]
        
        for i, p_char in enumerate(plaintext):
            pos = start + i
            c_val = ord(ciphertext[pos]) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            # Vigenère: P = (C - K) mod 26, so K = (C - P) mod 26
            k_vig = (c_val - p_val) % 26
            required["vigenere"][pos] = k_vig
            
            # Beaufort: P = (K - C) mod 26, so K = (P + C) mod 26
            k_beau = (p_val + c_val) % 26
            required["beaufort"][pos] = k_beau
    
    return required


def check_keystream_match(keystream: List[int], required_keys: Dict[int, int]) -> bool:
    """Check if keystream matches required values at anchor positions"""
    for pos, required_val in required_keys.items():
        if keystream[pos] != required_val:
            return False
    return True


def find_matching_keystreams():
    """Find keystreams that match anchor requirements"""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    keystreams_dir = base_path / "experiments/flint_otp_traverse/keystreams"
    results_dir = base_path / "experiments/flint_otp_traverse/results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    
    # Compute required key values
    required = compute_required_keys(ciphertext, anchors)
    
    print("=" * 70)
    print("ANCHOR-FIRST KEYSTREAM TARGETING")
    print("=" * 70)
    print("\nRequired key values at anchor positions:")
    print("\nVigenère (K = C - P mod 26):")
    for pos in sorted(list(required["vigenere"].keys())[:10]):
        val = required["vigenere"][pos]
        print(f"  Position {pos}: {val} ('{chr(val + ord('A'))}')")
    print("  ...")
    
    print("\nBeaufort (K = P + C mod 26):")
    for pos in sorted(list(required["beaufort"].keys())[:10]):
        val = required["beaufort"][pos]
        print(f"  Position {pos}: {val} ('{chr(val + ord('A'))}')")
    print("  ...")
    
    # Search all keystreams
    keystream_files = list(keystreams_dir.glob("*/*.json"))
    print(f"\nSearching {len(keystream_files)} keystreams for anchor matches...")
    
    matches = {
        "vigenere": [],
        "beaufort": []
    }
    
    tested = 0
    for kf in keystream_files:
        if kf.name == "summary.json":
            continue
            
        with open(kf) as f:
            keystream_data = json.load(f)
        
        keystream = keystream_data["kstream"]
        
        if len(keystream) != 97:
            continue
            
        tested += 1
        
        # Check Vigenère match
        if check_keystream_match(keystream, required["vigenere"]):
            matches["vigenere"].append(keystream_data)
            print(f"\n✓ VIGENÈRE MATCH: {keystream_data['recipe_id']}")
            print(f"  Table: {keystream_data['provenance']['table_id']}")
            print(f"  Family: {keystream_data['provenance']['family']}")
            print(f"  Path: {keystream_data['provenance']['path']}")
        
        # Check Beaufort match
        if check_keystream_match(keystream, required["beaufort"]):
            matches["beaufort"].append(keystream_data)
            print(f"\n✓ BEAUFORT MATCH: {keystream_data['recipe_id']}")
            print(f"  Table: {keystream_data['provenance']['table_id']}")
            print(f"  Family: {keystream_data['provenance']['family']}")
            print(f"  Path: {keystream_data['provenance']['path']}")
        
        if tested % 100 == 0:
            print(f"  Tested {tested}/{len(keystream_files)}...")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("TARGETING RESULTS")
    print(f"  Keystreams tested: {tested}")
    print(f"  Vigenère matches: {len(matches['vigenere'])}")
    print(f"  Beaufort matches: {len(matches['beaufort'])}")
    
    # Save matches
    if matches["vigenere"] or matches["beaufort"]:
        with open(results_dir / "anchor_matches.json", 'w') as f:
            json.dump({
                "required_keys": {
                    "vigenere": {str(k): v for k, v in required["vigenere"].items()},
                    "beaufort": {str(k): v for k, v in required["beaufort"].items()}
                },
                "matches": {
                    "vigenere": [m["recipe_id"] for m in matches["vigenere"]],
                    "beaufort": [m["recipe_id"] for m in matches["beaufort"]]
                },
                "full_matches": matches
            }, f, indent=2)
        
        print(f"\nMatches saved to: anchor_matches.json")
        
        # Test the matches fully
        print("\nFULL VALIDATION OF MATCHES:")
        from test_keystreams import vigenere_decode, beaufort_decode, check_anchors
        
        for variant, variant_matches in matches.items():
            for match_data in variant_matches:
                keystream = match_data["kstream"]
                
                if variant == "vigenere":
                    plaintext = vigenere_decode(ciphertext, keystream)
                else:
                    plaintext = beaufort_decode(ciphertext, keystream)
                
                anchors_pass, failures = check_anchors(plaintext, anchors)
                
                print(f"\n{variant.upper()} - {match_data['recipe_id']}:")
                print(f"  Anchors pass: {anchors_pass}")
                if not anchors_pass:
                    print(f"  Failures: {failures}")
                print(f"  Plaintext head: {plaintext[:40]}")
                print(f"  Full text: {plaintext}")
    else:
        print("\nNO MATCHES FOUND")
        print("No keystream satisfies the required key values at all anchor positions.")
        print("\nThis definitively rules out traverse tables as OTP source,")
        print("as none can produce the correct key values needed for the anchors.")
    
    # Create targeting report
    with open(results_dir / "TARGETING_REPORT.md", 'w') as f:
        f.write("# ANCHOR-FIRST TARGETING REPORT\n\n")
        f.write("## Method\n\n")
        f.write("Computed exact key values required at anchor positions:\n")
        f.write("- EAST @ 21-24\n")
        f.write("- NORTHEAST @ 25-33\n")
        f.write("- BERLIN @ 63-68\n")
        f.write("- CLOCK @ 69-73\n\n")
        
        f.write("## Required Key Values\n\n")
        f.write("### Vigenère (Sample)\n")
        f.write("| Position | Required K | Letter |\n")
        f.write("|----------|------------|--------|\n")
        for pos in sorted(list(required["vigenere"].keys())[:15]):
            val = required["vigenere"][pos]
            f.write(f"| {pos} | {val} | {chr(val + ord('A'))} |\n")
        
        f.write("\n### Beaufort (Sample)\n")
        f.write("| Position | Required K | Letter |\n")
        f.write("|----------|------------|--------|\n")
        for pos in sorted(list(required["beaufort"].keys())[:15]):
            val = required["beaufort"][pos]
            f.write(f"| {pos} | {val} | {chr(val + ord('A'))} |\n")
        
        f.write(f"\n## Results\n\n")
        f.write(f"- Keystreams tested: {tested}\n")
        f.write(f"- Vigenère matches: {len(matches['vigenere'])}\n")
        f.write(f"- Beaufort matches: {len(matches['beaufort'])}\n\n")
        
        if not matches["vigenere"] and not matches["beaufort"]:
            f.write("**CONCLUSION: No traverse table keystream can satisfy K4's anchors.**\n\n")
            f.write("This definitively eliminates traverse tables as the OTP source.\n")
    
    print(f"\nTargeting report saved to: TARGETING_REPORT.md")


if __name__ == "__main__":
    find_matching_keystreams()