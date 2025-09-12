#!/usr/bin/env python3
"""
Fresh-slate K4 derivation from CT + structural params + minimal cribs.
Pure Python stdlib only. No AI. No tail knowledge.
"""

import json
import os
import sys
from pathlib import Path


def compute_class(i, formula):
    """Compute class for index i using the given formula."""
    return eval(formula, {"__builtins__": {}}, {"i": i})


def decrypt_char(c_char, k_val, family):
    """Decrypt a single character using the specified family."""
    c_val = ord(c_char) - ord('A')
    
    if family == "vigenere":
        p_val = (c_val - k_val) % 26
    elif family == "beaufort":
        p_val = (k_val - c_val) % 26
    elif family == "variant_beaufort":
        p_val = (c_val + k_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")
    
    return chr(p_val + ord('A'))


def build_wheels(ciphertext, cribs, params):
    """Build wheel objects from cribs only, enforcing Option-A."""
    formula = params["class_function"]
    periods = params["periods"]
    families = params["families"]
    
    wheels = []
    
    for cls in range(6):
        L = periods[cls]
        family = families[cls]
        phase = 0  # Use phase=0 for simplicity
        
        # Initialize empty wheel
        residues = [None] * L
        
        # Fill in residues from cribs
        for crib in cribs:
            start = crib["start"]
            end = crib["end"]
            text = crib["text"]
            
            for offset, p_char in enumerate(text):
                idx = start + offset
                if idx > end:
                    break
                    
                # Check if this index belongs to current class
                if compute_class(idx, formula) != cls:
                    continue
                
                # Compute slot
                slot = (idx - phase) % L
                
                # Compute required K
                c_char = ciphertext[idx]
                c_val = ord(c_char) - ord('A')
                p_val = ord(p_char) - ord('A')
                
                if family == "vigenere":
                    k = (c_val - p_val) % 26
                    # Option-A: no K=0 for additive family at anchor
                    if k == 0:
                        print(f"WARNING: K=0 at anchor index {idx} for class {cls}")
                elif family == "beaufort":
                    k = (p_val + c_val) % 26
                elif family == "variant_beaufort":
                    k = (p_val - c_val) % 26
                    # Option-A: no K=0 for additive family at anchor
                    if k == 0:
                        print(f"WARNING: K=0 at anchor index {idx} for class {cls}")
                else:
                    raise ValueError(f"Unknown family: {family}")
                
                # Store residue
                if residues[slot] is not None and residues[slot] != k:
                    print(f"ERROR: Slot collision at class {cls}, slot {slot}")
                residues[slot] = k
        
        wheel = {
            "class_id": cls,
            "family": family,
            "L": L,
            "phase": phase,
            "residues": residues
        }
        wheels.append(wheel)
    
    return wheels


def derive_plaintext(ciphertext, wheels, params):
    """Derive plaintext using wheels. Unknown positions get '?'."""
    formula = params["class_function"]
    plaintext = []
    
    for i in range(97):
        c_char = ciphertext[i]
        cls = compute_class(i, formula)
        wheel = wheels[cls]
        
        slot = (i - wheel["phase"]) % wheel["L"]
        
        if wheel["residues"][slot] is not None:
            k = wheel["residues"][slot]
            p_char = decrypt_char(c_char, k, wheel["family"])
            plaintext.append(p_char)
        else:
            plaintext.append("?")
    
    return ''.join(plaintext)


def explain_index(idx, ciphertext, wheels, params):
    """Generate explanation for a single index."""
    formula = params["class_function"]
    c_char = ciphertext[idx]
    cls = compute_class(idx, formula)
    wheel = wheels[cls]
    
    slot = (idx - wheel["phase"]) % wheel["L"]
    
    explanation = []
    explanation.append(f"Index {idx}:")
    explanation.append(f"  Ciphertext: {c_char} (value: {ord(c_char) - ord('A')})")
    explanation.append(f"  Class: {cls} (formula: {formula.replace('i', str(idx))})")
    explanation.append(f"  Family: {wheel['family']}")
    explanation.append(f"  L: {wheel['L']}, Phase: {wheel['phase']}")
    explanation.append(f"  Slot: {slot}")
    
    if wheel["residues"][slot] is not None:
        k = wheel["residues"][slot]
        explanation.append(f"  K at slot {slot}: {k}")
        
        c_val = ord(c_char) - ord('A')
        if wheel["family"] == "vigenere":
            p_val = (c_val - k) % 26
            explanation.append(f"  Decrypt: P = C - K = {c_val} - {k} = {p_val} (mod 26)")
        elif wheel["family"] == "beaufort":
            p_val = (k - c_val) % 26
            explanation.append(f"  Decrypt: P = K - C = {k} - {c_val} = {p_val} (mod 26)")
        elif wheel["family"] == "variant_beaufort":
            p_val = (c_val + k) % 26
            explanation.append(f"  Decrypt: P = C + K = {c_val} + {k} = {p_val} (mod 26)")
        
        p_char = chr(p_val + ord('A'))
        explanation.append(f"  Plaintext: {p_char}")
    else:
        explanation.append(f"  K at slot {slot}: UNKNOWN (not forced by cribs)")
        explanation.append(f"  Plaintext: ?")
    
    return '\n'.join(explanation)


def create_class_strip_text(params):
    """Create text representation of class strip."""
    formula = params["class_function"]
    
    lines = []
    lines.append("CLASS STRIP (6 tracks)")
    lines.append("=" * 70)
    
    for cls in range(6):
        indices = []
        for i in range(97):
            if compute_class(i, formula) == cls:
                indices.append(str(i))
        
        # Format nicely
        line = f"Class {cls}: "
        for j, idx in enumerate(indices):
            if j > 0 and j % 10 == 0:
                line += "\n         "
            line += f"{idx:3} "
        lines.append(line)
    
    return '\n'.join(lines)


def create_tail_grid_text(plaintext):
    """Create text representation of tail grid (75-96)."""
    lines = []
    lines.append("TAIL GRID (positions 75-96)")
    lines.append("-" * 50)
    
    # Indices
    line1 = "Pos: "
    for i in range(75, 97):
        line1 += f"{i:3} "
    lines.append(line1)
    
    # Letters
    line2 = "Ltr: "
    for i in range(75, 97):
        line2 += f" {plaintext[i]}  "
    lines.append(line2)
    
    return '\n'.join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fresh-slate K4 derivation")
    parser.add_argument("--ct", required=True, help="Path to ciphertext file")
    parser.add_argument("--params", required=True, help="Path to structural params JSON")
    parser.add_argument("--cribs", required=True, help="Path to cribs JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out, exist_ok=True)
    
    # Load inputs
    with open(args.ct, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    with open(args.params, 'r') as f:
        params = json.load(f)
    
    with open(args.cribs, 'r') as f:
        cribs = json.load(f)
    
    # Validate ciphertext
    if len(ciphertext) != 97:
        print(f"ERROR: Ciphertext must be 97 characters, got {len(ciphertext)}")
        sys.exit(1)
    
    print(f"Fresh-slate K4 derivation")
    print(f"Cribs: {len(cribs)} spans")
    print()
    
    # Build wheels
    wheels = build_wheels(ciphertext, cribs, params)
    
    # Derive plaintext
    plaintext = derive_plaintext(ciphertext, wheels, params)
    
    # Count derived vs unknown
    derived_count = sum(1 for c in plaintext if c != '?')
    unknown_count = sum(1 for c in plaintext if c == '?')
    
    print(f"Results:")
    print(f"  Derived: {derived_count} letters")
    print(f"  Unknown: {unknown_count} positions")
    
    # Write outputs
    # 1. Partial plaintext
    pt_file = os.path.join(args.out, "PT_PARTIAL.txt")
    with open(pt_file, 'w') as f:
        f.write(plaintext)
    
    # 2. Counts
    counts_file = os.path.join(args.out, "COUNTS.json")
    with open(counts_file, 'w') as f:
        json.dump({"derived": derived_count, "unknown": unknown_count}, f, indent=2)
    
    # 3. Class strip (text version)
    strip_file = os.path.join(args.out, "CLASS_STRIP.txt")
    with open(strip_file, 'w') as f:
        f.write(create_class_strip_text(params))
    
    # 4. Wheels (JSON)
    wheels_file = os.path.join(args.out, "WHEELS.json")
    with open(wheels_file, 'w') as f:
        # Convert to simpler format for display
        wheels_display = []
        for w in wheels:
            wheel_info = {
                "class": w["class_id"],
                "family": w["family"],
                "L": w["L"],
                "phase": w["phase"],
                "forced_slots": {}
            }
            for slot, k in enumerate(w["residues"]):
                if k is not None:
                    wheel_info["forced_slots"][slot] = k
            wheels_display.append(wheel_info)
        json.dump(wheels_display, f, indent=2)
    
    # 5. Tail grid (text)
    tail_file = os.path.join(args.out, "TAIL_GRID.txt")
    with open(tail_file, 'w') as f:
        f.write(create_tail_grid_text(plaintext))
    
    # 6. Explain index 80
    explain_file = os.path.join(args.out, "EXPLAIN_80.txt")
    with open(explain_file, 'w') as f:
        f.write(explain_index(80, ciphertext, wheels, params))
    
    print(f"\nOutputs written to {args.out}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())