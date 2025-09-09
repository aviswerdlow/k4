#!/usr/bin/env python3
"""
Build wheels from anchors only (no plaintext required).
Outputs wheel specifications compatible with rederive_min.py.
Pure Python stdlib - no external dependencies.
"""

import json
import sys
from typing import Dict, List, Optional


def class_function(i: int) -> int:
    """Six-track periodic classing: class(i) = ((i % 2) * 3) + (i % 3)"""
    return ((i % 2) * 3) + (i % 3)


def build_wheels_from_anchors(ct_path: str, anchors_path: str, seed: int = 1337) -> Dict:
    """
    Build wheels from anchor constraints only.
    
    Args:
        ct_path: Path to ciphertext file
        anchors_path: Path to anchors JSON file
        seed: Random seed (for reproducibility)
    
    Returns:
        Dictionary with wheel specifications in rederive_min.py format
    """
    # Load ciphertext
    with open(ct_path, 'r') as f:
        ct = f.read().strip().upper()
    
    # Load anchors
    with open(anchors_path, 'r') as f:
        anchors_data = json.load(f)
    
    # Family assignments (fixed for K4)
    families = {
        0: "vigenere",
        1: "vigenere", 
        2: "beaufort",
        3: "vigenere",
        4: "beaufort",
        5: "variant_beaufort"
    }
    
    # Initialize wheels (all L=17, phase=0)
    wheels = {}
    for cls in range(6):
        wheels[cls] = {
            "family": families[cls],
            "L": 17,
            "phase": 0,
            "residues": [None] * 17  # Will be filled from anchors
        }
    
    # Process each anchor
    anchor_list = []
    for anchor_name, anchor_info in anchors_data.items():
        start = anchor_info['start']
        end = anchor_info['end']
        plaintext = anchor_info['plaintext']
        
        # Process each character in the anchor
        for offset, p_char in enumerate(plaintext):
            idx = start + offset
            if idx > end:
                break
            
            c_char = ct[idx]
            cls = class_function(idx)
            slot = idx % 17  # phase=0
            
            anchor_list.append({
                'index': idx,
                'P': p_char,
                'C': c_char,
                'class': cls,
                'slot': slot
            })
            
            # Calculate key residue based on family
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            family = families[cls]
            if family == "vigenere":
                # P = C - K (mod 26) => K = C - P (mod 26)
                k_val = (c_val - p_val) % 26
            elif family == "beaufort":
                # P = K - C (mod 26) => K = P + C (mod 26)
                k_val = (p_val + c_val) % 26
            elif family == "variant_beaufort":
                # P = C + K (mod 26) => K = P - C (mod 26)
                k_val = (p_val - c_val) % 26
            
            # Check consistency and update wheel
            if wheels[cls]["residues"][slot] is not None:
                if wheels[cls]["residues"][slot] != k_val:
                    print(f"ERROR: Inconsistent key at class {cls}, slot {slot}: "
                          f"{wheels[cls]['residues'][slot]} vs {k_val}")
                    return None
            wheels[cls]["residues"][slot] = k_val
    
    # Count undetermined positions
    total_positions = 0
    determined = 0
    for cls in range(6):
        for residue in wheels[cls]["residues"]:
            total_positions += 1
            if residue is not None:
                determined += 1
    
    undetermined = total_positions - determined
    coverage_pct = (determined / total_positions) * 100
    
    print(f"\n=== Wheel Construction Summary ===")
    print(f"Anchors processed: {len(anchors_data)}")
    print(f"Anchor characters: {len(anchor_list)}")
    print(f"Wheel positions determined: {determined}/{total_positions} ({coverage_pct:.1f}%)")
    print(f"Undetermined positions: {undetermined}")
    
    # Print wheel details
    for cls in range(6):
        determined_in_class = sum(1 for r in wheels[cls]["residues"] if r is not None)
        print(f"\nClass {cls} ({families[cls]}):")
        print(f"  Positions: {determined_in_class}/17")
        wheel_str = ""
        for r in wheels[cls]["residues"]:
            if r is None:
                wheel_str += "? "
            else:
                wheel_str += chr(ord('A') + r) + " "
        print(f"  Wheel: {wheel_str}")
    
    # Format for rederive_min.py (which expects "wheels" key)
    output = {
        "wheels": wheels,
        "metadata": {
            "seed": seed,
            "anchors_used": list(anchors_data.keys()),
            "determined_positions": determined,
            "total_positions": total_positions,
            "coverage_percent": coverage_pct
        }
    }
    
    return output


def main():
    if len(sys.argv) != 5:
        print("Usage: python3 rebuild_anchors_to_wheels.py <ct_path> <anchors_path> <seed> <output_path>")
        sys.exit(1)
    
    ct_path = sys.argv[1]
    anchors_path = sys.argv[2] 
    seed = int(sys.argv[3])
    output_path = sys.argv[4]
    
    result = build_wheels_from_anchors(ct_path, anchors_path, seed)
    
    if result is None:
        print("ERROR: Failed to build consistent wheels from anchors")
        sys.exit(1)
    
    # Write output
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nWheels written to: {output_path}")


if __name__ == "__main__":
    main()