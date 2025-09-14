#!/usr/bin/env python3
"""
Extended Plans L, M, N testing with more comprehensive coverage
Including L2 (anchor-derived ring order) and expanded M1 testing
"""

import sys
import os
from typing import Dict, Any, List, Tuple, Optional

# Add path to zone_mask_v1
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
from cipher_families import VigenereCipher, BeaufortCipher
from cipher_fractionation import BifidCipher

# Import path transforms
from path_transforms import ring24_path, ring24_inverse

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Expected anchors (0-based indices)
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

# Extended theme keys
EXTENDED_KEYS = [
    "BERLIN", "CLOCK", "EAST", "NORTH", "WEST", "SOUTH",
    "TIME", "ZONE", "HOUR", "WATCH", "SHADOW", "LIGHT",
    "KRYPTOS", "URANIA", "PALIMPSEST", "ABSCISSA", "ORDINATE",
    "LATITUDE", "LONGITUDE", "MERIDIAN", "AZIMUTH", "GIRASOL",
    "MORSE", "VIGENERE", "SCHEIDT", "SANBORN", "WEBSTER"
]

# KRYPTOS tableau
KRYPTOS_TABLEAU = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def check_anchors_fast(text: str) -> bool:
    """Quick anchor check - returns False on first failure"""
    if len(text) < 74:
        return False
    
    if text[21:25] != "EAST":
        return False
    if text[25:34] != "NORTHEAST":
        return False  
    if text[63:69] != "BERLIN":
        return False
    if text[69:74] != "CLOCK":
        return False
    
    return True

def derive_ring_order_from_anchors() -> List[int]:
    """
    L2: Derive ring-24 order from anchor letters
    Map A=0..Z=25, take mod 24, keep first occurrences
    """
    anchor_text = "EASTNORTHEASTBERLINCLOCK"
    seen = set()
    ring_order = []
    
    for char in anchor_text:
        if char in KRYPTOS_TABLEAU:
            idx = KRYPTOS_TABLEAU.index(char)
            val = idx % 24
            if val not in seen:
                ring_order.append(val)
                seen.add(val)
    
    # Append missing residues in numeric order
    for i in range(24):
        if i not in seen:
            ring_order.append(i)
    
    return ring_order

def apply_custom_ring(text: str, ring_order: List[int]) -> str:
    """Apply custom ring permutation based on anchor-derived order"""
    n = len(text)
    result = [''] * n
    
    # Apply ring permutation
    for i in range(n):
        # Map position i to new position based on ring_order
        new_pos = ring_order[i % 24] + (i // 24) * 24
        if new_pos < n:
            result[new_pos] = text[i]
    
    # Fill any gaps
    for i in range(n):
        if result[i] == '':
            result[i] = text[i]
    
    return ''.join(result)

def inverse_custom_ring(text: str, ring_order: List[int]) -> str:
    """Inverse of custom ring permutation"""
    n = len(text)
    result = [''] * n
    
    # Create inverse mapping
    inverse_order = [0] * 24
    for i, val in enumerate(ring_order):
        inverse_order[val] = i
    
    # Apply inverse permutation
    for i in range(n):
        orig_pos = inverse_order[i % 24] + (i // 24) * 24
        if orig_pos < n:
            result[orig_pos] = text[i]
    
    # Fill any gaps
    for i in range(n):
        if result[i] == '':
            result[i] = text[i]
    
    return ''.join(result)

def caesar_shift(text: str, shift: int) -> str:
    """Apply Caesar shift using KRYPTOS tableau"""
    result = []
    for char in text:
        if char in KRYPTOS_TABLEAU:
            idx = KRYPTOS_TABLEAU.index(char)
            new_idx = (idx + shift) % 26
            result.append(KRYPTOS_TABLEAU[new_idx])
        else:
            result.append(char)
    return ''.join(result)

def atbash(text: str) -> str:
    """Apply Atbash substitution using KRYPTOS tableau"""
    result = []
    for char in text:
        if char in KRYPTOS_TABLEAU:
            idx = KRYPTOS_TABLEAU.index(char)
            new_idx = 25 - idx
            result.append(KRYPTOS_TABLEAU[new_idx])
        else:
            result.append(char)
    return ''.join(result)

def test_l2_anchor_ring() -> List[Dict]:
    """
    L2: Anchor-derived ring order + Vigenere
    """
    successes = []
    ring_order = derive_ring_order_from_anchors()
    print(f"  L2 ring order: {ring_order[:10]}...")
    
    for key in EXTENDED_KEYS[:10]:  # Test more keys
        try:
            # Stage 1: Custom ring path
            stage1 = apply_custom_ring(K4_CIPHERTEXT, ring_order)
            
            # Stage 2: Vigenere decrypt
            vig = VigenereCipher(key=key, tableau_keyword="KRYPTOS")
            plaintext = vig.decrypt(stage1)
            
            if check_anchors_fast(plaintext):
                successes.append({
                    "type": "L2-AnchorRing",
                    "ring_order": ring_order,
                    "vigenere_key": key,
                    "plaintext": plaintext,
                    "anchors_matched": True
                })
        except:
            pass
    
    return successes

def test_m1_extended() -> List[Dict]:
    """
    M1 Extended: More comprehensive Caesar/Atbash testing
    """
    successes = []
    tested = 0
    
    # Test all Caesar shifts with more keys
    for shift in range(1, 26):
        shifted_ct = caesar_shift(K4_CIPHERTEXT, -shift)
        
        for key in EXTENDED_KEYS:
            tested += 1
            try:
                # Try Vigenere
                vig = VigenereCipher(key=key, tableau_keyword="KRYPTOS")
                plaintext = vig.decrypt(shifted_ct)
                
                if check_anchors_fast(plaintext):
                    successes.append({
                        "type": "M1-Caesar-Vigenere",
                        "shift": shift,
                        "key": key,
                        "plaintext": plaintext
                    })
                
                # Also try Beaufort
                beau = BeaufortCipher(key=key, tableau_keyword="KRYPTOS")
                plaintext = beau.decrypt(shifted_ct)
                
                if check_anchors_fast(plaintext):
                    successes.append({
                        "type": "M1-Caesar-Beaufort",
                        "shift": shift,
                        "key": key,
                        "plaintext": plaintext
                    })
            except:
                pass
    
    # Test Atbash with all keys
    atbash_ct = atbash(K4_CIPHERTEXT)
    for key in EXTENDED_KEYS:
        tested += 1
        try:
            # Vigenere
            vig = VigenereCipher(key=key, tableau_keyword="KRYPTOS")
            plaintext = vig.decrypt(atbash_ct)
            
            if check_anchors_fast(plaintext):
                successes.append({
                    "type": "M1-Atbash-Vigenere",
                    "key": key,
                    "plaintext": plaintext
                })
            
            # Beaufort
            beau = BeaufortCipher(key=key, tableau_keyword="KRYPTOS")
            plaintext = beau.decrypt(atbash_ct)
            
            if check_anchors_fast(plaintext):
                successes.append({
                    "type": "M1-Atbash-Beaufort",
                    "key": key,
                    "plaintext": plaintext
                })
        except:
            pass
    
    print(f"  Tested {tested} M1 configurations")
    return successes

def test_n1_extended() -> List[Dict]:
    """
    N1 Extended: More 3-stage combinations
    """
    successes = []
    tested = 0
    
    for bifid_period in [7, 9, 11, 13]:
        for vig_key in EXTENDED_KEYS[:15]:
            tested += 1
            try:
                # Ring-24 → Bifid → Vigenere
                stage1 = ring24_path(K4_CIPHERTEXT)
                
                bifid = BifidCipher(keyword="KRYPTOS", period=bifid_period)
                stage2 = bifid.decrypt(stage1)
                
                vig = VigenereCipher(key=vig_key, tableau_keyword="KRYPTOS")
                plaintext = vig.decrypt(stage2)
                
                if check_anchors_fast(plaintext):
                    successes.append({
                        "type": "N1-Ring-Bifid-Vigenere",
                        "bifid_period": bifid_period,
                        "vigenere_key": vig_key,
                        "plaintext": plaintext
                    })
            except:
                pass
            
            # Also try: Vigenere → Ring-24 → Bifid (different order)
            try:
                vig = VigenereCipher(key=vig_key, tableau_keyword="KRYPTOS")
                stage1 = vig.decrypt(K4_CIPHERTEXT)
                
                stage2 = ring24_path(stage1)
                
                bifid = BifidCipher(keyword="KRYPTOS", period=bifid_period)
                plaintext = bifid.decrypt(stage2)
                
                if check_anchors_fast(plaintext):
                    successes.append({
                        "type": "N1-Vigenere-Ring-Bifid",
                        "bifid_period": bifid_period,
                        "vigenere_key": vig_key,
                        "plaintext": plaintext
                    })
            except:
                pass
    
    print(f"  Tested {tested} N1 configurations")
    return successes

def main():
    """Extended testing of Plans L, M, and N"""
    print("=" * 80)
    print("PLANS L/M/N EXTENDED: COMPREHENSIVE TESTING")
    print("=" * 80)
    print()
    
    all_successes = []
    
    # Plan L2: Anchor-derived ring order
    print("Testing L2: Anchor-derived ring order...")
    print("-" * 40)
    l2_results = test_l2_anchor_ring()
    if l2_results:
        for result in l2_results:
            print(f"🎯 SUCCESS: {result['type']}, Key: {result['vigenere_key']}")
            print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
        all_successes.extend(l2_results)
    else:
        print("  No L2 matches")
    print()
    
    # Plan M1 Extended
    print("Testing M1 Extended: Caesar/Atbash with all keys...")
    print("-" * 40)
    m1_results = test_m1_extended()
    if m1_results:
        for result in m1_results:
            print(f"🎯 SUCCESS: {result['type']}")
            if 'shift' in result:
                print(f"   Shift: {result['shift']}, Key: {result['key']}")
            else:
                print(f"   Key: {result['key']}")
            print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
        all_successes.extend(m1_results)
    else:
        print("  No M1 matches")
    print()
    
    # Plan N1 Extended
    print("Testing N1 Extended: More 3-stage chains...")
    print("-" * 40)
    n1_results = test_n1_extended()
    if n1_results:
        for result in n1_results:
            print(f"🎯 SUCCESS: {result['type']}")
            print(f"   p={result['bifid_period']}, Key={result['vigenere_key']}")
            print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
        all_successes.extend(n1_results)
    else:
        print("  No N1 matches")
    print()
    
    # Summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total successful configurations: {len(all_successes)}")
    
    if all_successes:
        print("\n🎉 ANCHOR MATCHES FOUND!")
        for config in all_successes[:3]:  # Show first 3
            pt = config['plaintext']
            print(f"\n{config['type']}:")
            print(f"  [0:21]: {pt[0:21]}")
            print(f"  [21:34]: {pt[21:34]} (anchors)")
            print(f"  [34:63]: {pt[34:63]}")
            print(f"  [63:74]: {pt[63:74]} (anchors)")
            print(f"  [74:97]: {pt[74:97]}")
    else:
        print("\n❌ No configurations matched the anchors")
        print("\n🔴 CRITICAL: All paper-doable approaches exhausted")
        print("\nRecommendation: Re-examine fundamental assumptions")
        print("  1. Anchor positions (are they really at PT 21-33, 63-73?)")
        print("  2. Tableau (KRYPTOS vs standard A-Z)")
        print("  3. Direction (are we decrypting when we should encrypt?)")
        print("  4. Text completeness (97 chars vs 98 with DYAHR)")

if __name__ == "__main__":
    main()