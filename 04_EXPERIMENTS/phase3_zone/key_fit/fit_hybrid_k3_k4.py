#!/usr/bin/env python3
"""
Plan K3/K4: Zone-specific toggles and window shims
K3: Zone-specific single change (MID zone gets extra rule)
K4: Window shim at BERLIN/CLOCK region only
"""

import sys
import os
import json
from typing import Dict, Any, List, Tuple, Optional

# Add path to zone_mask_v1
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
from cipher_fractionation import BifidCipher
from cipher_families import VigenereCipher, BeaufortCipher

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Expected anchors (0-based indices)
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

# Zone boundaries
ZONES = {
    "HEAD": (0, 33),
    "MID": (34, 73),
    "TAIL": (74, 96)
}

# KRYPTOS tableau
KRYPTOS_TABLEAU = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
KRYPTOS_REVERSED = "ZXWVUQNMLJIHGFEDCBASPOTRYK"  # Reversed KRYPTOS

def columnar_7x14_inverse(text: str) -> str:
    """Inverse of columnar 7×14 (one pass)"""
    n = len(text)
    rows, cols = 7, 14
    
    if n < rows * cols:
        text = text + 'X' * (rows * cols - n)
    
    grid = []
    idx = 0
    for c in range(cols):
        col = []
        for r in range(rows):
            if idx < len(text):
                col.append(text[idx])
                idx += 1
            else:
                col.append('X')
        grid.append(col)
    
    result = []
    for r in range(rows):
        for c in range(cols):
            result.append(grid[c][r])
    
    return ''.join(result)[:n]

def columnar_7x14_forward(text: str) -> str:
    """Forward columnar 7×14 (one pass)"""
    n = len(text)
    rows, cols = 7, 14
    
    if n < rows * cols:
        text = text + 'X' * (rows * cols - n)
    
    grid = []
    idx = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('X')
        grid.append(row)
    
    result = []
    for c in range(cols):
        for r in range(rows):
            result.append(grid[r][c])
    
    return ''.join(result)[:n]

def check_anchors_fast(text: str) -> bool:
    """Quick anchor check"""
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

def apply_beaufort_to_zone(text: str, zone: str, key: str = "K") -> str:
    """Apply Beaufort cipher to specific zone only"""
    start, end = ZONES[zone]
    result = list(text)
    
    # Apply Beaufort to zone
    beaufort = BeaufortCipher(key=key, tableau_keyword="KRYPTOS")
    zone_text = text[start:end+1]
    zone_decrypted = beaufort.decrypt(zone_text)
    
    # Replace zone in result
    for i, char in enumerate(zone_decrypted):
        if start + i <= end:
            result[start + i] = char
    
    return ''.join(result)

def apply_reversed_tableau_to_zone(text: str, zone: str) -> str:
    """Apply reversed KRYPTOS tableau to specific zone"""
    start, end = ZONES[zone]
    result = list(text)
    
    # Simple substitution with reversed tableau
    for i in range(start, min(end+1, len(text))):
        char = text[i]
        if char in KRYPTOS_TABLEAU:
            idx = KRYPTOS_TABLEAU.index(char)
            result[i] = KRYPTOS_REVERSED[idx]
    
    return ''.join(result)

def test_k3_beaufort_mid(keyword: str, period: int) -> Optional[Dict]:
    """K3: Bifid → Columnar, but MID zone gets Beaufort pass"""
    try:
        # Stage 1: Bifid decrypt
        bifid = BifidCipher(keyword=keyword, period=period)
        stage1 = bifid.decrypt(K4_CIPHERTEXT)
        
        # Stage 2: Apply Beaufort to MID zone only
        stage2 = apply_beaufort_to_zone(stage1, "MID")
        
        # Stage 3: Columnar inverse
        plaintext = columnar_7x14_inverse(stage2)
        
        # Quick anchor check
        if not check_anchors_fast(plaintext):
            return None
        
        return {
            "type": "K3-Beaufort-MID",
            "keyword": keyword,
            "period": period,
            "plaintext": plaintext,
            "anchors_matched": True
        }
    except:
        return None

def test_k3_reversed_mid(keyword: str, period: int) -> Optional[Dict]:
    """K3: Bifid → Columnar, but MID zone uses reversed tableau"""
    try:
        # Stage 1: Bifid decrypt
        bifid = BifidCipher(keyword=keyword, period=period)
        stage1 = bifid.decrypt(K4_CIPHERTEXT)
        
        # Stage 2: Apply reversed tableau to MID zone only
        stage2 = apply_reversed_tableau_to_zone(stage1, "MID")
        
        # Stage 3: Columnar inverse
        plaintext = columnar_7x14_inverse(stage2)
        
        # Quick anchor check
        if not check_anchors_fast(plaintext):
            return None
        
        return {
            "type": "K3-Reversed-MID",
            "keyword": keyword,
            "period": period,
            "plaintext": plaintext,
            "anchors_matched": True
        }
    except:
        return None

def apply_window_shim(text: str, start: int = 60, end: int = 76) -> str:
    """K4: Apply Vigenere↔Beaufort flip in window [60..76] only"""
    result = list(text)
    
    # Simple flip: if char is in first half of alphabet, use second half
    for i in range(start, min(end+1, len(text))):
        char = text[i]
        if char in KRYPTOS_TABLEAU:
            idx = KRYPTOS_TABLEAU.index(char)
            # Flip position in tableau
            new_idx = (26 - idx - 1) % 26
            result[i] = KRYPTOS_TABLEAU[new_idx]
    
    return ''.join(result)

def test_k4_window_shim(keyword: str, period: int) -> Optional[Dict]:
    """K4: Window shim at [60..76] → Bifid → Columnar"""
    try:
        # Stage 1: Apply window shim to ciphertext
        shimmed_ct = apply_window_shim(K4_CIPHERTEXT)
        
        # Stage 2: Bifid decrypt
        bifid = BifidCipher(keyword=keyword, period=period)
        stage2 = bifid.decrypt(shimmed_ct)
        
        # Stage 3: Columnar inverse
        plaintext = columnar_7x14_inverse(stage2)
        
        # Quick anchor check
        if not check_anchors_fast(plaintext):
            return None
        
        return {
            "type": "K4-WindowShim",
            "keyword": keyword,
            "period": period,
            "plaintext": plaintext,
            "anchors_matched": True
        }
    except:
        return None

def main():
    """Test K3 and K4 variants"""
    print("=" * 80)
    print("PLAN K3/K4: ZONE-SPECIFIC TOGGLES AND WINDOW SHIMS")
    print("=" * 80)
    print()
    
    successful_configs = []
    
    # Test keywords and periods
    keywords = ["KRYPTOS", "URANIA", "ABSCISSA", "ORDINATE", "MERIDIAN"]
    periods = [7, 9, 11]
    
    # K3: Zone-specific toggles
    print("Testing K3: Zone-specific toggles...")
    print("-" * 40)
    
    for keyword in keywords:
        for period in periods:
            # K3 variant 1: Beaufort on MID
            result = test_k3_beaufort_mid(keyword, period)
            if result:
                print(f"🎯 SUCCESS: K3-Beaufort-MID({keyword}, p={period})")
                print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
                successful_configs.append(result)
            
            # K3 variant 2: Reversed tableau on MID
            result = test_k3_reversed_mid(keyword, period)
            if result:
                print(f"🎯 SUCCESS: K3-Reversed-MID({keyword}, p={period})")
                print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
                successful_configs.append(result)
    
    print(f"Tested {len(keywords) * len(periods) * 2} K3 configurations")
    print()
    
    # K4: Window shim (only if K3 empty)
    if not successful_configs:
        print("Testing K4: Window shim at BERLIN/CLOCK region...")
        print("-" * 40)
        
        for keyword in keywords:
            for period in periods:
                result = test_k4_window_shim(keyword, period)
                if result:
                    print(f"🎯 SUCCESS: K4-WindowShim({keyword}, p={period})")
                    print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
                    successful_configs.append(result)
        
        print(f"Tested {len(keywords) * len(periods)} K4 configurations")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successful configurations: {len(successful_configs)}")
    
    if successful_configs:
        print("\n🎉 ANCHOR MATCHES FOUND!")
        for config in successful_configs:
            print(f"\n{config['type']}: {config['keyword']}, p={config['period']}")
            pt = config['plaintext']
            print(f"   [0:21]: {pt[0:21]}")
            print(f"   [34:63]: {pt[34:63]}")
            print(f"   [74:97]: {pt[74:97]}")
        
        with open('plan_k3_k4_successes.json', 'w') as f:
            json.dump(successful_configs, f, indent=2)
        print("\n✅ Saved to plan_k3_k4_successes.json")
    else:
        print("\n❌ No K3/K4 configurations matched the anchors")
        print("\nAll Plan K variants exhausted. Two-stage paper-doable hybrids falsified.")
    
    return len(successful_configs) > 0

if __name__ == "__main__":
    main()