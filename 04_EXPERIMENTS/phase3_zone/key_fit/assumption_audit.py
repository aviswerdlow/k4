#!/usr/bin/env python3
"""
Assumption Audit: Systematically test core assumptions
A) Tableau: A-Z vs KRYPTOS
B) Direction: Encrypt vs Decrypt
C) Anchor position: PT-index vs CT-index
D) Length: 97 vs 98 character diagnostic
"""

import sys
import os
from typing import Dict, Any, List, Tuple, Optional

# Add path to zone_mask_v1
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
from cipher_families import VigenereCipher, BeaufortCipher

# Import path transforms
from path_transforms import ring24_path, ring24_inverse, serpentine_turn, serpentine_turn_inverse

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Expected anchors
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

# Standard A-Z tableau
STANDARD_TABLEAU = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_TABLEAU = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def check_anchors_fast(text: str, positions: Dict = None) -> bool:
    """Check anchors at specified positions (default PT indices)"""
    if positions is None:
        positions = ANCHORS
    
    if len(text) < 74:
        return False
    
    for anchor, (start, end) in positions.items():
        if text[start:end+1] != anchor:
            return False
    
    return True

def derive_keystream_for_anchors(ct: str, pt_anchors: Dict, tableau: str) -> Dict[int, str]:
    """Derive required keystream letters to produce anchors"""
    keystream = {}
    
    for anchor_text, (start, end) in pt_anchors.items():
        for i, pt_char in enumerate(anchor_text):
            ct_char = ct[start + i] if start + i < len(ct) else 'X'
            
            # For Vigenere: K = (C - P) mod 26
            if ct_char in tableau and pt_char in tableau:
                ct_pos = tableau.index(ct_char)
                pt_pos = tableau.index(pt_char)
                key_pos = (ct_pos - pt_pos) % 26
                keystream[start + i] = tableau[key_pos]
    
    return keystream

def find_periodic_fit(keystream: Dict[int, str], max_period: int = 40) -> List[Tuple[int, str]]:
    """Find periodic keys that match the keystream requirements"""
    matches = []
    
    for period in range(3, max_period + 1):
        # Try to build a key of this period
        key = ['?'] * period
        valid = True
        
        for pos, required_char in keystream.items():
            key_pos = pos % period
            if key[key_pos] == '?':
                key[key_pos] = required_char
            elif key[key_pos] != required_char:
                valid = False
                break
        
        if valid and '?' not in key:
            matches.append((period, ''.join(key)))
    
    return matches

def test_a_tableau_check():
    """Test A: Check standard A-Z tableau vs KRYPTOS"""
    print("TEST A: Tableau Check (A-Z vs KRYPTOS)")
    print("-" * 40)
    
    results = []
    
    # Test with standard A-Z tableau
    print("Testing standard A-Z tableau...")
    
    # Derive required keystream for anchors
    keystream = derive_keystream_for_anchors(K4_CIPHERTEXT, ANCHORS, STANDARD_TABLEAU)
    
    # Find periodic fits
    periodic_fits = find_periodic_fit(keystream)
    
    if periodic_fits:
        print(f"  ✅ Found {len(periodic_fits)} periodic fits with A-Z tableau!")
        for period, key in periodic_fits[:3]:  # Show first 3
            print(f"     Period {period}: {key[:20]}...")
            
            # Verify with full decrypt
            vig = VigenereCipher(tableau='standard')  # Standard A-Z tableau
            pt = vig.decrypt(K4_CIPHERTEXT, key)
            if check_anchors_fast(pt):
                results.append(("A-Z-Vigenere", period, key, pt))
    else:
        print("  ❌ No periodic fits with A-Z tableau")
    
    # Also test with routes
    for route_name, route_func in [("Ring24", ring24_path), ("Serpentine", serpentine_turn)]:
        routed_ct = route_func(K4_CIPHERTEXT)
        keystream = derive_keystream_for_anchors(routed_ct, ANCHORS, STANDARD_TABLEAU)
        periodic_fits = find_periodic_fit(keystream)
        
        if periodic_fits:
            print(f"  ✅ Found fits with A-Z + {route_name}!")
            results.append((f"A-Z-{route_name}", len(periodic_fits), None, None))
    
    return results

def test_b_direction_check():
    """Test B: Check encrypt vs decrypt direction"""
    print("\nTEST B: Direction Check (Encrypt vs Decrypt)")
    print("-" * 40)
    
    results = []
    
    # Test "encrypting" K4 as if it were plaintext
    test_keys = ["BERLIN", "CLOCK", "KRYPTOS", "PALIMPSEST"]
    
    for key in test_keys:
        # Try encrypting K4 with Vigenere
        vig = VigenereCipher(tableau='kryptos')
        result = vig.encrypt(K4_CIPHERTEXT, key)  # Treating CT as PT
        
        if check_anchors_fast(result):
            print(f"  ✅ Anchors found when ENCRYPTING with key: {key}")
            results.append(("Encrypt-Vigenere", key, result))
        
        # Try with Beaufort (different direction behavior)
        beau = BeaufortCipher(tableau='kryptos')
        result = beau.encrypt(K4_CIPHERTEXT, key)
        
        if check_anchors_fast(result):
            print(f"  ✅ Anchors found when ENCRYPTING with Beaufort key: {key}")
            results.append(("Encrypt-Beaufort", key, result))
    
    if not results:
        print("  ❌ No anchors found with encrypt direction")
    
    return results

def test_c_ct_index_anchors():
    """Test C: Check if anchors are at CT indices instead of PT"""
    print("\nTEST C: CT-Index Anchors Check")
    print("-" * 40)
    
    results = []
    
    # Check if BERLINCLOCK appears at CT positions 63-73
    ct_segment = K4_CIPHERTEXT[63:74]
    print(f"  CT[63:74] = {ct_segment}")
    
    if ct_segment == "BERLINCLOCK":
        print("  ✅ BERLINCLOCK found at CT indices!")
        results.append(("CT-index", True))
    else:
        print("  ❌ BERLINCLOCK not at CT indices")
        
        # Check if any transformation preserves these CT positions
        test_keys = ["BERLIN", "CLOCK", "KRYPTOS"]
        
        for key in test_keys:
            vig = VigenereCipher(tableau='kryptos')
            pt = vig.decrypt(K4_CIPHERTEXT, key)
            
            # Check if CT positions are preserved
            if pt[63:69] == K4_CIPHERTEXT[63:69]:
                print(f"  🔍 Key {key} preserves CT[63:69]")
                results.append(("Preserve-CT", key, pt))
    
    return results

def test_d_length_diagnostic():
    """Test D: 97 vs 98 character diagnostic"""
    print("\nTEST D: Length Diagnostic (97 vs 98)")
    print("-" * 40)
    
    results = []
    best_fit = None
    best_score = 0
    
    # Test insertions at each position
    for insert_pos in range(98):
        # Create 98-char version with 'X' inserted
        if insert_pos == 0:
            modified = 'X' + K4_CIPHERTEXT
        elif insert_pos >= 97:
            modified = K4_CIPHERTEXT + 'X'
        else:
            modified = K4_CIPHERTEXT[:insert_pos] + 'X' + K4_CIPHERTEXT[insert_pos:]
        
        # Adjust anchor positions for insertion
        adjusted_anchors = {}
        for anchor, (start, end) in ANCHORS.items():
            if start >= insert_pos:
                adjusted_anchors[anchor] = (start + 1, end + 1)
            elif end >= insert_pos:
                adjusted_anchors[anchor] = (start, end + 1)
            else:
                adjusted_anchors[anchor] = (start, end)
        
        # Derive keystream for adjusted positions
        keystream = derive_keystream_for_anchors(modified, adjusted_anchors, KRYPTOS_TABLEAU)
        
        # Find periodic fits
        periodic_fits = find_periodic_fit(keystream, max_period=28)
        
        if periodic_fits:
            score = len(periodic_fits)
            if score > best_score:
                best_score = score
                best_fit = (insert_pos, periodic_fits[0])
    
    if best_fit:
        insert_pos, (period, key) = best_fit
        print(f"  ✅ Best insertion at position {insert_pos}")
        print(f"     Period {period}: {key}")
        results.append(("Insert", insert_pos, period, key))
    else:
        print("  ❌ No clean periodic fits with insertions")
    
    # Test deletions
    for delete_pos in range(97):
        # Create 96-char version with one char deleted
        modified = K4_CIPHERTEXT[:delete_pos] + K4_CIPHERTEXT[delete_pos+1:]
        
        # Adjust anchor positions for deletion
        adjusted_anchors = {}
        for anchor, (start, end) in ANCHORS.items():
            if start > delete_pos:
                adjusted_anchors[anchor] = (start - 1, end - 1)
            elif end > delete_pos:
                adjusted_anchors[anchor] = (start, end - 1)
            else:
                adjusted_anchors[anchor] = (start, end)
        
        # Quick check if anchors still possible
        valid = True
        for anchor, (s, e) in adjusted_anchors.items():
            if e - s + 1 != len(anchor):
                valid = False
                break
        
        if valid:
            keystream = derive_keystream_for_anchors(modified, adjusted_anchors, KRYPTOS_TABLEAU)
            periodic_fits = find_periodic_fit(keystream, max_period=28)
            
            if periodic_fits and len(periodic_fits) > best_score:
                best_score = len(periodic_fits)
                best_fit = (delete_pos, periodic_fits[0], "delete")
    
    if best_fit and len(best_fit) == 3:  # Deletion result
        delete_pos, (period, key), _ = best_fit
        print(f"  ✅ Best deletion at position {delete_pos}")
        print(f"     Period {period}: {key}")
        results.append(("Delete", delete_pos, period, key))
    
    return results

def main():
    """Run complete assumption audit"""
    print("=" * 80)
    print("ASSUMPTION AUDIT: SYSTEMATIC VERIFICATION")
    print("=" * 80)
    print()
    
    all_results = {}
    
    # Test A: Tableau
    all_results['A'] = test_a_tableau_check()
    
    # Test B: Direction
    all_results['B'] = test_b_direction_check()
    
    # Test C: CT-index
    all_results['C'] = test_c_ct_index_anchors()
    
    # Test D: Length
    all_results['D'] = test_d_length_diagnostic()
    
    # Summary
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    
    findings = []
    
    if all_results['A']:
        findings.append("✅ TEST A: Alternative tableau (A-Z) shows promise")
    else:
        findings.append("❌ TEST A: Tableau is not the blocker")
    
    if all_results['B']:
        findings.append("✅ TEST B: Direction flip yields results")
    else:
        findings.append("❌ TEST B: Direction assumption is correct")
    
    if all_results['C']:
        findings.append("✅ TEST C: CT-index anchors detected")
    else:
        findings.append("❌ TEST C: Anchors are at PT indices")
    
    if all_results['D']:
        findings.append("✅ TEST D: Length anomaly detected")
    else:
        findings.append("❌ TEST D: 97 characters is correct")
    
    for finding in findings:
        print(finding)
    
    # Decision
    print("\n" + "=" * 80)
    if any(all_results.values()):
        print("🎯 ASSUMPTION VIOLATIONS FOUND - Investigate further")
    else:
        print("📊 ALL ASSUMPTIONS VALIDATED - Move to non-classical approaches")
    print("=" * 80)

if __name__ == "__main__":
    main()