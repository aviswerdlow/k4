#!/usr/bin/env python3
"""
Plan K: Two-stage hybrid fitter with anchor-first validation
Bifid/Four-Square → Columnar 7×14 (one pass)
"""

import sys
import os
import json
from typing import Dict, Any, List, Tuple, Optional

# Add path to zone_mask_v1
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
from zone_runner import ZoneRunner
from cipher_fractionation import BifidCipher, FourSquareCipher

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Expected anchors (0-based indices)
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

# Bifid square keywords
BIFID_KEYWORDS = [
    "KRYPTOS", "URANIA", "ABSCISSA", "ORDINATE",
    "LATITUDE", "LONGITUDE", "MERIDIAN", "AZIMUTH", "GIRASOL"
]

# Four-Square keywords
FOURSQUARE_TR = ["URANIA", "ABSCISSA", "MERIDIAN"]
FOURSQUARE_BL = ["ORDINATE", "LATITUDE", "AZIMUTH"]

def columnar_7x14_inverse(text: str) -> str:
    """
    Inverse of columnar 7×14 (one pass)
    Takes column-read text and returns row-written text
    """
    n = len(text)
    rows, cols = 7, 14
    
    # Pad if needed
    if n < rows * cols:
        text = text + 'X' * (rows * cols - n)
    
    # Create grid from column-wise reading
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
    
    # Read row-wise
    result = []
    for r in range(rows):
        for c in range(cols):
            result.append(grid[c][r])
    
    return ''.join(result)[:n]

def columnar_7x14_forward(text: str) -> str:
    """
    Forward columnar 7×14 (one pass)
    Write row-wise, read column-wise
    """
    n = len(text)
    rows, cols = 7, 14
    
    # Pad if needed
    if n < rows * cols:
        text = text + 'X' * (rows * cols - n)
    
    # Write into grid row-wise
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
    
    # Read column-wise
    result = []
    for c in range(cols):
        for r in range(rows):
            result.append(grid[r][c])
    
    return ''.join(result)[:n]

def check_anchors_fast(text: str) -> bool:
    """Quick anchor check - returns False on first failure"""
    if len(text) < 74:
        return False
    
    # Check each anchor
    if text[21:25] != "EAST":
        return False
    if text[25:34] != "NORTHEAST":
        return False
    if text[63:69] != "BERLIN":
        return False
    if text[69:74] != "CLOCK":
        return False
    
    return True

def test_bifid_columnar(keyword: str, period: int) -> Optional[Dict]:
    """Test Bifid → Columnar 7×14 configuration"""
    try:
        # Stage 1: Bifid decrypt
        bifid = BifidCipher(keyword=keyword, period=period)
        stage1 = bifid.decrypt(K4_CIPHERTEXT)
        
        # Stage 2: Columnar inverse (to get plaintext)
        plaintext = columnar_7x14_inverse(stage1)
        
        # Quick anchor check
        if not check_anchors_fast(plaintext):
            return None
        
        # Verify round-trip
        # Forward: PT → Columnar → Bifid encrypt → CT
        stage1_enc = columnar_7x14_forward(plaintext)
        ct_verify = bifid.encrypt(stage1_enc)
        
        if ct_verify != K4_CIPHERTEXT:
            return None
        
        # Success! Return details
        return {
            "type": "Bifid→Columnar",
            "keyword": keyword,
            "period": period,
            "plaintext": plaintext,
            "stage1": stage1,
            "anchors_matched": True
        }
        
    except Exception as e:
        return None

def test_foursquare_columnar(tr_keyword: str, bl_keyword: str) -> Optional[Dict]:
    """Test Four-Square → Columnar 7×14 configuration"""
    try:
        # Stage 1: Four-Square decrypt
        fs = FourSquareCipher(top_right_key=tr_keyword, bottom_left_key=bl_keyword)
        stage1 = fs.decrypt(K4_CIPHERTEXT)
        
        # Stage 2: Columnar inverse
        plaintext = columnar_7x14_inverse(stage1)
        
        # Quick anchor check
        if not check_anchors_fast(plaintext):
            return None
        
        # Verify round-trip
        stage1_enc = columnar_7x14_forward(plaintext)
        ct_verify = fs.encrypt(stage1_enc)
        
        if ct_verify != K4_CIPHERTEXT:
            return None
        
        # Success!
        return {
            "type": "FourSquare→Columnar",
            "tr_keyword": tr_keyword,
            "bl_keyword": bl_keyword,
            "plaintext": plaintext,
            "stage1": stage1,
            "anchors_matched": True
        }
        
    except Exception as e:
        return None

def main():
    """Test all Plan K configurations"""
    print("=" * 80)
    print("PLAN K: TWO-STAGE HYBRIDS (ANCHOR-FIRST)")
    print("=" * 80)
    print()
    
    successful_configs = []
    
    # K1: Bifid → Columnar
    print("Testing K1: Bifid → Columnar 7×14...")
    print("-" * 40)
    
    total_bifid = 0
    for keyword in BIFID_KEYWORDS:
        for period in [7, 9, 11]:
            total_bifid += 1
            result = test_bifid_columnar(keyword, period)
            
            if result:
                print(f"🎯 SUCCESS: Bifid({keyword}, p={period}) → Columnar")
                print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
                print(f"   Anchors: ✅ All matched!")
                successful_configs.append(result)
    
    print(f"Tested {total_bifid} Bifid configurations")
    print()
    
    # K2: Four-Square → Columnar
    print("Testing K2: Four-Square → Columnar 7×14...")
    print("-" * 40)
    
    total_fs = 0
    for tr_key in FOURSQUARE_TR:
        for bl_key in FOURSQUARE_BL:
            total_fs += 1
            result = test_foursquare_columnar(tr_key, bl_key)
            
            if result:
                print(f"🎯 SUCCESS: FourSquare({tr_key}/{bl_key}) → Columnar")
                print(f"   Plaintext[0:40]: {result['plaintext'][:40]}")
                print(f"   Anchors: ✅ All matched!")
                successful_configs.append(result)
    
    print(f"Tested {total_fs} Four-Square configurations")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total configurations tested: {total_bifid + total_fs}")
    print(f"Successful (anchors matched): {len(successful_configs)}")
    
    if successful_configs:
        print("\n🎉 ANCHOR MATCHES FOUND!")
        print("\nSuccessful configurations:")
        for i, config in enumerate(successful_configs, 1):
            print(f"\n{i}. {config['type']}")
            if config['type'] == "Bifid→Columnar":
                print(f"   Keyword: {config['keyword']}, Period: {config['period']}")
            else:
                print(f"   TR: {config['tr_keyword']}, BL: {config['bl_keyword']}")
            print(f"   First 40 chars: {config['plaintext'][:40]}")
            
            # Show non-anchor text samples
            pt = config['plaintext']
            print(f"   [0:21]: {pt[0:21]}")
            print(f"   [34:63]: {pt[34:63]}")
            print(f"   [74:97]: {pt[74:97]}")
        
        # Save successful configurations
        with open('plan_k_successes.json', 'w') as f:
            json.dump(successful_configs, f, indent=2)
        print("\n✅ Saved successful configurations to plan_k_successes.json")
    else:
        print("\n❌ No configurations matched the anchors")
        print("\nMoving to K3/K4 variants (zone-specific toggles)...")
    
    return len(successful_configs) > 0

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nK1/K2 empty. Implement K3 (zone-specific) or K4 (window shim) next.")