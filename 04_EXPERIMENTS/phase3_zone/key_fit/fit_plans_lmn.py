#!/usr/bin/env python3
"""
Plans L, M, N: Anchor-derived parameters, monoalphabetic pre-maps, and 3-stage chains
L: Use anchors to derive stage-2 parameters (symmetric, fair)
M: Simple Caesar/Atbash pre-map before classical cipher
N: Single 3-stage chain (Ring-24 → Bifid → Vigenere)
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

# Theme keys to test
THEME_KEYS = [
    "BERLIN", "CLOCK", "EAST", "NORTH", "WEST",
    "TIME", "ZONE", "HOUR", "WATCH",
    "KRYPTOS", "URANIA", "SHADOW"
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

def derive_columnar_key_from_anchors() -> str:
    """
    L1: Derive columnar key from anchor words
    EAST + NORTHEAST + BERLIN + CLOCK, de-duplicated
    """
    anchor_text = "EASTNORTHEASTBERLINCLOCK"
    seen = set()
    key = []
    
    for char in anchor_text:
        if char not in seen:
            key.append(char)
            seen.add(char)
    
    # If short, pad from KRYPTOS (de-duped)
    if len(key) < 14:
        for char in "KRYPTOS":
            if char not in seen and len(key) < 14:
                key.append(char)
                seen.add(char)
    
    return ''.join(key[:14])  # Return 14 chars for 14×7 grid

def columnar_with_key(text: str, key: str, decrypt: bool = True) -> str:
    """
    Columnar transposition with keyword-derived column order
    """
    n = len(text)
    cols = len(key)
    rows = (n + cols - 1) // cols
    
    # Create column order from key
    sorted_key = sorted(enumerate(key), key=lambda x: x[1])
    col_order = [i for i, _ in sorted_key]
    
    if decrypt:
        # Decrypt: column-read to row-write
        # Pad for complete grid
        padded = text + 'X' * (rows * cols - n)
        
        # Read columns in key order
        grid = [[] for _ in range(rows)]
        idx = 0
        for col_idx in col_order:
            for r in range(rows):
                if idx < len(padded):
                    grid[r].append(padded[idx])
                    idx += 1
        
        # Read row-wise
        result = []
        for row in grid:
            result.extend(row)
        
        return ''.join(result)[:n]
    else:
        # Encrypt: row-write to column-read
        # Write row-wise
        grid = []
        idx = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if idx < n:
                    row.append(text[idx])
                    idx += 1
                else:
                    row.append('X')
            grid.append(row)
        
        # Read columns in key order
        result = []
        for col_idx in col_order:
            for r in range(rows):
                if col_idx < len(grid[r]):
                    result.append(grid[r][col_idx])
        
        return ''.join(result)[:n]

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

def test_l1_anchor_columnar() -> Optional[Dict]:
    """
    L1: Anchor-derived columnar key
    """
    key = derive_columnar_key_from_anchors()
    print(f"  L1 columnar key: {key}")
    
    # Try with simple Vigenere first
    for theme_key in THEME_KEYS[:5]:  # Test subset
        try:
            # Stage 1: Vigenere decrypt
            vig = VigenereCipher(key=theme_key, tableau_keyword="KRYPTOS")
            stage1 = vig.decrypt(K4_CIPHERTEXT)
            
            # Stage 2: Columnar with anchor-derived key
            plaintext = columnar_with_key(stage1, key, decrypt=True)
            
            if check_anchors_fast(plaintext):
                return {
                    "type": "L1-AnchorColumnar",
                    "columnar_key": key,
                    "vigenere_key": theme_key,
                    "plaintext": plaintext,
                    "anchors_matched": True
                }
        except:
            pass
    
    return None

def test_m1_caesar_premap() -> List[Dict]:
    """
    M1: Caesar/Atbash pre-map + Vigenere
    """
    successes = []
    
    # Test Caesar shifts
    for shift in range(1, 26):
        # Apply inverse Caesar to CT
        shifted_ct = caesar_shift(K4_CIPHERTEXT, -shift)
        
        # Try Vigenere with theme keys
        for key in THEME_KEYS[:5]:
            try:
                vig = VigenereCipher(key=key, tableau_keyword="KRYPTOS")
                plaintext = vig.decrypt(shifted_ct)
                
                if check_anchors_fast(plaintext):
                    successes.append({
                        "type": "M1-Caesar",
                        "shift": shift,
                        "vigenere_key": key,
                        "plaintext": plaintext,
                        "anchors_matched": True
                    })
            except:
                pass
    
    # Test Atbash
    atbash_ct = atbash(K4_CIPHERTEXT)
    for key in THEME_KEYS[:5]:
        try:
            vig = VigenereCipher(key=key, tableau_keyword="KRYPTOS")
            plaintext = vig.decrypt(atbash_ct)
            
            if check_anchors_fast(plaintext):
                successes.append({
                    "type": "M1-Atbash",
                    "vigenere_key": key,
                    "plaintext": plaintext,
                    "anchors_matched": True
                })
        except:
            pass
    
    return successes

def test_n1_three_stage() -> List[Dict]:
    """
    N1: Ring-24 → Bifid → Vigenere (3-stage chain)
    """
    successes = []
    
    for bifid_period in [7, 9, 11]:
        for vig_key in THEME_KEYS[:5]:
            try:
                # Stage 1: Ring-24 path
                stage1 = ring24_path(K4_CIPHERTEXT)
                
                # Stage 2: Bifid decrypt
                bifid = BifidCipher(keyword="KRYPTOS", period=bifid_period)
                stage2 = bifid.decrypt(stage1)
                
                # Stage 3: Vigenere decrypt
                vig = VigenereCipher(key=vig_key, tableau_keyword="KRYPTOS")
                plaintext = vig.decrypt(stage2)
                
                if check_anchors_fast(plaintext):
                    successes.append({
                        "type": "N1-ThreeStage",
                        "bifid_period": bifid_period,
                        "vigenere_key": vig_key,
                        "plaintext": plaintext,
                        "anchors_matched": True
                    })
            except:
                pass
    
    return successes

def main():
    """Test Plans L, M, and N"""
    print("=" * 80)
    print("PLANS L/M/N: ANCHOR-DERIVED, PRE-MAPS, AND 3-STAGE")
    print("=" * 80)
    print()
    
    all_successes = []
    
    # Plan L1: Anchor-derived columnar
    print("Testing L1: Anchor-derived columnar key...")
    print("-" * 40)
    l1_result = test_l1_anchor_columnar()
    if l1_result:
        print(f"🎯 SUCCESS: {l1_result['type']}")
        print(f"   Plaintext[0:40]: {l1_result['plaintext'][:40]}")
        all_successes.append(l1_result)
    else:
        print("  No L1 matches")
    print()
    
    # Plan M1: Caesar/Atbash pre-maps
    print("Testing M1: Caesar/Atbash pre-maps...")
    print("-" * 40)
    m1_results = test_m1_caesar_premap()
    if m1_results:
        for result in m1_results:
            print(f"🎯 SUCCESS: {result['type']}")
            if result['type'] == "M1-Caesar":
                print(f"   Shift: {result['shift']}, Key: {result['vigenere_key']}")
            else:
                print(f"   Key: {result['vigenere_key']}")
            print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
        all_successes.extend(m1_results)
    else:
        print("  No M1 matches")
    print()
    
    # Plan N1: Three-stage chain
    print("Testing N1: Ring-24 → Bifid → Vigenere...")
    print("-" * 40)
    n1_results = test_n1_three_stage()
    if n1_results:
        for result in n1_results:
            print(f"🎯 SUCCESS: {result['type']}")
            print(f"   Bifid p={result['bifid_period']}, Vig key={result['vigenere_key']}")
            print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
        all_successes.extend(n1_results)
    else:
        print("  No N1 matches")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total successful configurations: {len(all_successes)}")
    
    if all_successes:
        print("\n🎉 ANCHOR MATCHES FOUND!")
        for i, config in enumerate(all_successes, 1):
            print(f"\n{i}. {config['type']}")
            pt = config['plaintext']
            print(f"   [0:21]: {pt[0:21]}")
            print(f"   [34:63]: {pt[34:63]}")
            print(f"   [74:97]: {pt[74:97]}")
    else:
        print("\n❌ No configurations matched the anchors")
        print("\nPlans L/M/N exhausted. Time to re-examine core assumptions:")
        print("  - Tableau choice (KRYPTOS vs standard)")
        print("  - Direction (decrypt vs encrypt)")
        print("  - Anchor positions (PT indices vs CT indices)")
        print("  - Text length (97 vs 98 with DYAHR)")

if __name__ == "__main__":
    main()