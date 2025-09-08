#!/usr/bin/env python3
"""
Pretty-print the wheel configurations from the enhanced proof.
Shows each class table with slot → residue mapping and presence mask.
"""

import json
from pathlib import Path
import sys


def print_wheels(proof_path: Path):
    """Pretty-print all wheel configurations."""
    
    # Load proof
    with open(proof_path, 'r') as f:
        proof = json.load(f)
    
    print("=" * 70)
    print("K4 WHEEL CONFIGURATIONS")
    print("=" * 70)
    print()
    print(f"Class Formula: {proof.get('class_formula', 'N/A')}")
    print()
    
    # Print each class
    for class_data in proof.get('per_class', []):
        class_id = class_data['class_id']
        family = class_data['family']
        L = class_data['L']
        phase = class_data['phase']
        residues = class_data['residues']
        residues_alpha = class_data.get('residues_alpha', [])
        present_mask = class_data.get('present_slots_mask', '1' * L)
        anchors = class_data.get('forced_anchor_residues', [])
        optionA = class_data.get('optionA_checks', [])
        
        print(f"CLASS {class_id}")
        print("-" * 40)
        print(f"  Family: {family}")
        print(f"  Period L: {L}")
        print(f"  Phase: {phase}")
        print(f"  Anchors: {len(anchors)}")
        if optionA:
            print(f"  ⚠️  Option-A violations: {len(optionA)}")
        print()
        
        # Print wheel table
        print("  Slot | K  | Letter | Present")
        print("  -----|----+--------+---------")
        
        for slot in range(L):
            if slot < len(present_mask) and present_mask[slot] == '1':
                k_val = residues[slot] if residues[slot] is not None else '-'
                k_letter = residues_alpha[slot] if slot < len(residues_alpha) and residues_alpha[slot] else '-'
                present = '✓'
            else:
                k_val = '-'
                k_letter = '-'
                present = '✗'
            
            # Mark anchor slots
            is_anchor = False
            for anchor in anchors:
                anchor_slot = (anchor['index'] - phase) % L
                if anchor_slot == slot:
                    is_anchor = True
                    break
            
            anchor_mark = '*' if is_anchor else ' '
            print(f"  {slot:4} | {k_val:2} |   {k_letter:1}    |    {present}   {anchor_mark}")
        
        print()
        
        # Print anchor details
        if anchors:
            print("  Anchor Residues:")
            for anchor in anchors:
                i = anchor['index']
                slot = anchor.get('slot', (i - phase) % L)
                k = anchor['residue']
                c = anchor.get('C', '?')
                p = anchor.get('P', '?')
                print(f"    Index {i:2} (slot {slot:2}): C={c} → K={k:2} → P={p}")
        
        print()
    
    # Print summary
    print("=" * 70)
    print("SUMMARY")
    print("-" * 40)
    
    total_slots = sum(class_data['L'] for class_data in proof.get('per_class', []))
    filled_slots = sum(
        class_data.get('present_slots_mask', '1' * class_data['L']).count('1')
        for class_data in proof.get('per_class', [])
    )
    
    print(f"Total slots: {total_slots}")
    print(f"Filled slots: {filled_slots}")
    print(f"Coverage: {filled_slots/total_slots*100:.1f}%")
    
    # Check Option-A
    violations = sum(
        len(class_data.get('optionA_checks', []))
        for class_data in proof.get('per_class', [])
    )
    
    if violations == 0:
        print("Option-A: ✅ All additive family anchors have K ≠ 0")
    else:
        print(f"Option-A: ❌ {violations} violations found")
    
    print()
    print("Legend:")
    print("  * = Anchor-constrained slot")
    print("  ✓ = Slot filled by class indices")
    print("  ✗ = Slot not hit by any index in this class")
    print()


def main():
    """Main entry point."""
    
    # Default path
    proof_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json")
    
    # Accept path from command line
    if len(sys.argv) > 1:
        proof_path = Path(sys.argv[1])
    
    if not proof_path.exists():
        print(f"❌ Proof file not found: {proof_path}")
        sys.exit(1)
    
    print_wheels(proof_path)


if __name__ == "__main__":
    main()