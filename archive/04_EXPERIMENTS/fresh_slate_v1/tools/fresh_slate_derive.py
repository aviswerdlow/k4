#!/usr/bin/env python3
"""
Fresh-slate derivation program - derives from CT + cribs only.
No AI, no hypothesis scaffolding, fixed non-adaptive rules.
Pure Python stdlib only.
"""

import json
import os
import sys
import hashlib
from pathlib import Path


def compute_class(i, formula):
    """Compute class for index i using the given formula."""
    # Safe evaluation of simple formulas
    return eval(formula, {"__builtins__": {}}, {"i": i})


def decrypt_char(c_char, k_val, family):
    """
    Decrypt a single character using the specified family.
    
    Args:
        c_char: ciphertext character (A-Z)
        k_val: key value (0-25)
        family: decryption family (vigenere, beaufort, variant_beaufort)
    
    Returns:
        plaintext character (A-Z)
    """
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


def determine_family(ciphertext, cribs, class_indices, class_id):
    """
    Determine which family works for a class given the cribs.
    Returns the first working family in order [vigenere, variant_beaufort, beaufort].
    Enforces Option-A: no K=0 at anchor cells for additive families.
    """
    families = ["vigenere", "variant_beaufort", "beaufort"]
    
    for family in families:
        works = True
        k_values = {}
        
        # Check each crib position in this class
        for crib in cribs:
            start, end = crib["span"]
            plaintext = crib["plaintext"]
            
            for offset, p_char in enumerate(plaintext):
                idx = start + offset
                if idx not in class_indices[class_id]:
                    continue
                    
                c_char = ciphertext[idx]
                c_val = ord(c_char) - ord('A')
                p_val = ord(p_char) - ord('A')
                
                # Calculate required K
                if family == "vigenere":
                    k = (c_val - p_val) % 26
                    # Option-A: no K=0 for additive family at anchor
                    if k == 0:
                        works = False
                        break
                elif family == "beaufort":
                    k = (p_val + c_val) % 26
                elif family == "variant_beaufort":
                    k = (p_val - c_val) % 26
                    # Option-A: no K=0 for additive family at anchor
                    if k == 0:
                        works = False
                        break
                
                # Store K value for consistency check
                k_values[idx] = k
                
            if not works:
                break
        
        if works:
            return family, k_values
    
    return None, None


def determine_period_phase(class_indices, cribs, class_id):
    """
    Determine the smallest L and phase that seats all crib indices 
    on distinct slots with no collisions.
    """
    indices_in_class = []
    for crib in cribs:
        start, end = crib["span"]
        for idx in range(start, end + 1):
            if idx in class_indices[class_id]:
                indices_in_class.append(idx)
    
    if not indices_in_class:
        return None, None
    
    # Try L from 10 to 22
    for L in range(10, 23):
        # Try each phase
        for phase in range(L):
            slots = set()
            collision = False
            
            for idx in indices_in_class:
                slot = (idx - phase) % L
                if slot in slots:
                    collision = True
                    break
                slots.add(slot)
            
            if not collision:
                return L, phase
    
    return None, None


def build_wheels(ciphertext, cribs, classing):
    """Build wheel objects for each class."""
    formula = classing["formula"]
    num_classes = classing["classes"]
    
    # Build class index lists
    class_indices = {c: [] for c in range(num_classes)}
    for i in range(97):
        c = compute_class(i, formula)
        class_indices[c].append(i)
    
    wheels = []
    
    for class_id in range(num_classes):
        # Determine family
        family, k_values = determine_family(ciphertext, cribs, class_indices, class_id)
        if family is None:
            print(f"ERROR: Class {class_id} is infeasible - no family satisfies cribs")
            return None
        
        # Determine L and phase
        L, phase = determine_period_phase(class_indices, cribs, class_id)
        if L is None:
            print(f"ERROR: Class {class_id} is infeasible - no L/phase found")
            return None
        
        # Build residues array with nulls for unknown slots
        residues = [None] * L
        present_slots_mask = [0] * L
        
        # Fill in known residues from cribs
        for crib in cribs:
            start, end = crib["span"]
            plaintext = crib["plaintext"]
            
            for offset, p_char in enumerate(plaintext):
                idx = start + offset
                if idx not in class_indices[class_id]:
                    continue
                
                slot = (idx - phase) % L
                c_char = ciphertext[idx]
                c_val = ord(c_char) - ord('A')
                p_val = ord(p_char) - ord('A')
                
                # Calculate K for this slot
                if family == "vigenere":
                    k = (c_val - p_val) % 26
                elif family == "beaufort":
                    k = (p_val + c_val) % 26
                elif family == "variant_beaufort":
                    k = (p_val - c_val) % 26
                
                residues[slot] = k
                present_slots_mask[slot] = 1
        
        wheel = {
            "class_id": class_id,
            "family": family,
            "L": L,
            "phase": phase,
            "residues": residues,
            "present_slots_mask": present_slots_mask
        }
        wheels.append(wheel)
    
    return wheels


def derive_plaintext(ciphertext, wheels, classing):
    """Derive plaintext using wheels. Unknown positions get '?'."""
    formula = classing["formula"]
    plaintext = []
    
    for i in range(97):
        c_char = ciphertext[i]
        c = compute_class(i, formula)
        wheel = wheels[c]
        
        slot = (i - wheel["phase"]) % wheel["L"]
        
        if wheel["present_slots_mask"][slot] == 1:
            k = wheel["residues"][slot]
            p_char = decrypt_char(c_char, k, wheel["family"])
            plaintext.append(p_char)
        else:
            plaintext.append("?")
    
    return ''.join(plaintext)


def write_explain_samples(ciphertext, wheels, classing, indices, outfile):
    """Write step-by-step explanations for specific indices."""
    formula = classing["formula"]
    
    with open(outfile, 'w') as f:
        f.write("FRESH-SLATE DERIVATION SAMPLES\n")
        f.write("=" * 50 + "\n\n")
        
        for i in indices:
            c_char = ciphertext[i]
            c = compute_class(i, formula)
            wheel = wheels[c]
            
            f.write(f"Index {i}:\n")
            f.write(f"  Ciphertext: {c_char} ({ord(c_char) - ord('A')})\n")
            f.write(f"  Class: {c} (formula: {formula})\n")
            f.write(f"  Family: {wheel['family']}\n")
            f.write(f"  L: {wheel['L']}, Phase: {wheel['phase']}\n")
            
            slot = (i - wheel["phase"]) % wheel["L"]
            f.write(f"  Slot: {slot}\n")
            
            if wheel["present_slots_mask"][slot] == 1:
                k = wheel["residues"][slot]
                f.write(f"  K: {k}\n")
                
                c_val = ord(c_char) - ord('A')
                if wheel["family"] == "vigenere":
                    p_val = (c_val - k) % 26
                    f.write(f"  Decrypt: P = C - K = {c_val} - {k} = {p_val} (mod 26)\n")
                elif wheel["family"] == "beaufort":
                    p_val = (k - c_val) % 26
                    f.write(f"  Decrypt: P = K - C = {k} - {c_val} = {p_val} (mod 26)\n")
                elif wheel["family"] == "variant_beaufort":
                    p_val = (c_val + k) % 26
                    f.write(f"  Decrypt: P = C + K = {c_val} + {k} = {p_val} (mod 26)\n")
                
                p_char = chr(p_val + ord('A'))
                f.write(f"  Plaintext: {p_char}\n")
            else:
                f.write(f"  K: UNKNOWN (slot not filled by cribs)\n")
                f.write(f"  Plaintext: ?\n")
            
            f.write("\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fresh-slate K4 derivation from CT + cribs only")
    parser.add_argument("--ct", required=True, help="Path to ciphertext file")
    parser.add_argument("--crib", required=True, help="Path to crib JSON file")
    parser.add_argument("--classing", required=True, help="Path to classing JSON file")
    parser.add_argument("--out", required=True, help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out, exist_ok=True)
    
    # Load inputs
    with open(args.ct, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    with open(args.crib, 'r') as f:
        crib_data = json.load(f)
        cribs = crib_data["cribs"]
    
    with open(args.classing, 'r') as f:
        classing = json.load(f)
    
    # Validate ciphertext
    if len(ciphertext) != 97:
        print(f"ERROR: Ciphertext must be exactly 97 characters, got {len(ciphertext)}")
        sys.exit(1)
    
    if not all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in ciphertext):
        print("ERROR: Ciphertext must contain only A-Z")
        sys.exit(1)
    
    # Build wheels
    print("Building wheels from cribs...")
    wheels = build_wheels(ciphertext, cribs, classing)
    if wheels is None:
        print("ERROR: Failed to build wheels")
        sys.exit(1)
    
    # Derive plaintext
    print("Deriving plaintext...")
    plaintext = derive_plaintext(ciphertext, wheels, classing)
    
    # Count derived vs undetermined
    derived_count = sum(1 for c in plaintext if c != '?')
    undetermined_count = sum(1 for c in plaintext if c == '?')
    
    # Write outputs
    output_files = {}
    
    # Write plaintext
    pt_file = os.path.join(args.out, "derived_pt.txt")
    with open(pt_file, 'w') as f:
        f.write(plaintext)
    output_files["derived_pt.txt"] = pt_file
    
    # Write wheels
    wheels_file = os.path.join(args.out, "wheels.json")
    with open(wheels_file, 'w') as f:
        json.dump(wheels, f, indent=2)
    output_files["wheels.json"] = wheels_file
    
    # Write summary
    summary = {
        "crib_count": len(cribs),
        "derived_count": derived_count,
        "undetermined_count": undetermined_count,
        "classing": classing["name"],
        "families": [w["family"] for w in wheels]
    }
    summary_file = os.path.join(args.out, "summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    output_files["summary.json"] = summary_file
    
    # Write explain samples for indices 80-84
    explain_file = os.path.join(args.out, "explain_samples.txt")
    write_explain_samples(ciphertext, wheels, classing, range(80, 85), explain_file)
    output_files["explain_samples.txt"] = explain_file
    
    # Write manifest
    manifest_file = os.path.join(args.out, "MANIFEST.sha256")
    with open(manifest_file, 'w') as f:
        for name, path in sorted(output_files.items()):
            with open(path, 'rb') as infile:
                sha = hashlib.sha256(infile.read()).hexdigest()
                f.write(f"{sha}  {name}\n")
    
    print(f"\nResults written to {args.out}:")
    print(f"  Derived: {derived_count} letters")
    print(f"  Undetermined: {undetermined_count} positions")
    print(f"  Summary: {summary_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())