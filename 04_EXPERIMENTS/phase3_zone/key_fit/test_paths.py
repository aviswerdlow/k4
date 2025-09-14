#!/usr/bin/env python3
"""
Test path transformations against K4 anchors
Plan J: path-first approach with Vigenere cipher
"""

import sys
import os
import json
from typing import Dict, Any, List, Tuple

# Add path to zone_mask_v1
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../03_SOLVERS/zone_mask_v1/scripts'))
from zone_runner import ZoneRunner

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Expected anchors
ANCHORS = {
    "EAST": (21, 24),      # 0-based indices
    "NORTHEAST": (25, 33),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73)
}

def check_anchors(plaintext: str) -> Dict[str, bool]:
    """Check if plaintext contains expected anchors at correct positions"""
    results = {}
    for anchor, (start, end) in ANCHORS.items():
        if start < len(plaintext):
            actual = plaintext[start:end+1]
            results[anchor] = (actual == anchor)
        else:
            results[anchor] = False
    return results

def test_manifest(manifest_path: str) -> Tuple[str, Dict[str, bool], str]:
    """Test a single manifest and return results"""
    # Load manifest for control indices
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Create runner and decrypt
    runner = ZoneRunner()
    runner.load_manifest(manifest_path)  # Pass the path, not the loaded dict
    
    try:
        plaintext = runner.decrypt(K4_CIPHERTEXT)
        anchor_results = check_anchors(plaintext)
        
        # Get control text for debugging
        control_indices = manifest['control']['indices']
        control_text = ''.join([plaintext[i] for i in control_indices if i < len(plaintext)])
        
        return plaintext, anchor_results, control_text
    except Exception as e:
        return str(e), {anchor: False for anchor in ANCHORS}, "ERROR"

def main():
    """Test all path manifests"""
    print("=" * 80)
    print("PLAN J: PATH TRANSFORMATIONS + VIGENERE")
    print("=" * 80)
    print()
    
    # Define manifests to test
    config_dir = "../configs/path_vigenere"
    manifests = [
        ("Helix-28 → Vigenere(BERLIN/CLOCK/WATCH)", "helix28_berlin.json"),
        ("Helix-28 → Vigenere(EAST/NORTH/WEST)", "helix28_compass.json"),
        ("Helix-28 → Vigenere(TIME/ZONE/HOUR)", "helix28_time.json"),
        ("Vigenere(BERLIN/CLOCK/WATCH) → Helix-28", "helix28_reverse.json"),
        ("Serpentine-turn → Vigenere(BERLIN/CLOCK/WATCH)", "serpentine_berlin.json"),
        ("Ring24 → Vigenere(BERLIN/CLOCK/WATCH)", "ring24_berlin.json"),
    ]
    
    total_tested = 0
    any_success = False
    
    for description, filename in manifests:
        manifest_path = os.path.join(config_dir, filename)
        
        if not os.path.exists(manifest_path):
            print(f"⚠️  {description}: Manifest not found")
            continue
        
        print(f"\nTesting: {description}")
        print("-" * 40)
        
        plaintext, anchor_results, control_text = test_manifest(manifest_path)
        total_tested += 1
        
        # Check if all anchors match
        all_match = all(anchor_results.values())
        if all_match:
            any_success = True
            print("🎯 SUCCESS! All anchors match!")
        
        # Display results
        for anchor, matched in anchor_results.items():
            symbol = "✅" if matched else "❌"
            print(f"  {symbol} {anchor}")
        
        # Show control text (what we got at anchor positions)
        if not all_match and control_text != "ERROR":
            print(f"  Control text: {control_text[:24]}  (Expected: EASTNORTHEASTBERLINCLOCK)")
            # Show first 40 chars of plaintext for debugging
            if isinstance(plaintext, str) and len(plaintext) > 40:
                print(f"  First 40 chars: {plaintext[:40]}")
    
    # Summary
    print("\n" + "=" * 80)
    print(f"SUMMARY: Tested {total_tested} configurations")
    if any_success:
        print("🎉 AT LEAST ONE CONFIGURATION FOUND THE ANCHORS!")
    else:
        print("❌ No configurations matched the anchors")
    print("=" * 80)

if __name__ == "__main__":
    main()