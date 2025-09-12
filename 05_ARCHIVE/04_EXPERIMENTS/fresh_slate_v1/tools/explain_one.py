#!/usr/bin/env python3
"""
Explain derivation at a single index.
Uses same logic as fresh_slate_derive.py but for one position.
Pure Python stdlib only.
"""

import json
import sys


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


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Explain K4 derivation at a single index")
    parser.add_argument("--ct", required=True, help="Path to ciphertext file")
    parser.add_argument("--crib", required=True, help="Path to crib JSON file")
    parser.add_argument("--classing", required=True, help="Path to classing JSON file")
    parser.add_argument("--index", type=int, required=True, help="Index to explain (0-96)")
    
    args = parser.parse_args()
    
    # Load inputs
    with open(args.ct, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    with open(args.crib, 'r') as f:
        crib_data = json.load(f)
        cribs = crib_data["cribs"]
    
    with open(args.classing, 'r') as f:
        classing = json.load(f)
    
    # Validate index
    if args.index < 0 or args.index >= 97:
        print(f"ERROR: Index must be 0-96, got {args.index}")
        sys.exit(1)
    
    # Import the wheel building logic
    sys.path.insert(0, '.')
    from fresh_slate_derive import build_wheels
    
    # Build wheels
    wheels = build_wheels(ciphertext, cribs, classing)
    if wheels is None:
        print("ERROR: Failed to build wheels")
        sys.exit(1)
    
    # Explain the specific index
    i = args.index
    formula = classing["formula"]
    c_char = ciphertext[i]
    c = compute_class(i, formula)
    wheel = wheels[c]
    
    print(f"\nEXPLAINING INDEX {i}")
    print("=" * 40)
    print(f"Ciphertext letter: {c_char} (value: {ord(c_char) - ord('A')})")
    print(f"Class: {c} (computed as: {formula.replace('i', str(i))} = {c})")
    print(f"Family: {wheel['family']}")
    print(f"Period L: {wheel['L']}")
    print(f"Phase: {wheel['phase']}")
    
    slot = (i - wheel["phase"]) % wheel["L"]
    print(f"Slot: (i - phase) % L = ({i} - {wheel['phase']}) % {wheel['L']} = {slot}")
    
    if wheel["present_slots_mask"][slot] == 1:
        k = wheel["residues"][slot]
        print(f"Key K at slot {slot}: {k}")
        
        c_val = ord(c_char) - ord('A')
        if wheel["family"] == "vigenere":
            p_val = (c_val - k) % 26
            print(f"Decrypt rule (Vigenère): P = C - K")
            print(f"  P = {c_val} - {k} = {c_val - k}")
            if c_val - k < 0:
                print(f"  = {c_val - k} ≡ {p_val} (mod 26)")
        elif wheel["family"] == "beaufort":
            p_val = (k - c_val) % 26
            print(f"Decrypt rule (Beaufort): P = K - C")
            print(f"  P = {k} - {c_val} = {k - c_val}")
            if k - c_val < 0:
                print(f"  = {k - c_val} ≡ {p_val} (mod 26)")
        elif wheel["family"] == "variant_beaufort":
            p_val = (c_val + k) % 26
            print(f"Decrypt rule (Variant Beaufort): P = C + K")
            print(f"  P = {c_val} + {k} = {c_val + k}")
            if c_val + k >= 26:
                print(f"  = {c_val + k} ≡ {p_val} (mod 26)")
        
        p_char = chr(p_val + ord('A'))
        print(f"Plaintext letter: {p_char} (value: {p_val})")
    else:
        print(f"Key K at slot {slot}: UNKNOWN")
        print("This slot was not determined by the cribs.")
        print("Plaintext letter: ?")
    
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())