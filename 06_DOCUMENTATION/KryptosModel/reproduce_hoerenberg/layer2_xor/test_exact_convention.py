#!/usr/bin/env python3
"""
Test Hörenberg's EXACT XOR convention with R27-31 as pass-through.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xor5_hoerenberg import xor5_hoerenberg, xor5_string_hoerenberg, letter_to_code5
from ioc import calculate_ioc


def test_exact_convention():
    """
    Test if our discovered convention produces EXACT match.
    """
    print("TESTING HÖRENBERG'S EXACT XOR CONVENTION")
    print("=" * 70)

    # Load Hörenberg's exact strings
    data_file = 'data/hoerenberg_withoutOBKR_extraL.json'
    with open(data_file, 'r') as f:
        hoerenberg_data = json.load(f)

    c_string = hoerenberg_data['C']
    k_string = hoerenberg_data['K']
    p_expected = hoerenberg_data['P']
    ioc_expected = hoerenberg_data['IoC']

    print("Convention: R27-31 treated as pass-through (output C)")
    print()

    # Apply the XOR
    p_computed = xor5_string_hoerenberg(c_string, k_string)

    # Check exact match
    exact_match = (p_computed == p_expected)

    print(f"C: {c_string[:50]}...")
    print(f"K: {k_string[:50]}...")
    print()
    print(f"P computed: {p_computed[:50]}...")
    print(f"P expected: {p_expected[:50]}...")
    print()
    print(f"EXACT MATCH: {exact_match}")

    if not exact_match:
        # Show mismatches
        mismatches = []
        for i, (comp, exp) in enumerate(zip(p_computed, p_expected)):
            if comp != exp:
                c = c_string[i]
                k = k_string[i]
                r = letter_to_code5(c) ^ letter_to_code5(k)
                mismatches.append({
                    'pos': i,
                    'c': c,
                    'k': k,
                    'r': r,
                    'computed': comp,
                    'expected': exp
                })

        print(f"\nMismatches: {len(mismatches)}")
        for m in mismatches[:5]:
            print(f"  Pos {m['pos']}: C={m['c']}, K={m['k']}, r={m['r']}, "
                  f"computed={m['computed']}, expected={m['expected']}")
    else:
        print("\n✅ PERFECT REPRODUCTION ACHIEVED!")

    # Check IoC
    ioc_computed = calculate_ioc(p_computed)
    print(f"\nIndex of Coincidence:")
    print(f"  Computed: {ioc_computed:.8f}")
    print(f"  Expected: {ioc_expected:.8f}")
    print(f"  Match: {abs(ioc_computed - ioc_expected) < 0.000001}")

    # Analyze R values distribution
    r_distribution = {}
    for c, k in zip(c_string, k_string):
        r = letter_to_code5(c) ^ letter_to_code5(k)
        r_distribution[r] = r_distribution.get(r, 0) + 1

    print(f"\nR value distribution:")
    print(f"  R=0 (pass-through): {r_distribution.get(0, 0)}")
    print(f"  R=1-26 (normal): {sum(r_distribution.get(i, 0) for i in range(1, 27))}")
    print(f"  R=27-31 (special): {sum(r_distribution.get(i, 0) for i in range(27, 32))}")

    return exact_match


def document_convention():
    """
    Document the discovered convention.
    """
    print("\n" + "=" * 70)
    print("HÖRENBERG'S EXACT XOR CONVENTION (DISCOVERED)")
    print("=" * 70)
    print()
    print("For Layer 2 (5-bit XOR):")
    print()
    print("1. Encoding: A=1, B=2, ..., Z=26")
    print()
    print("2. XOR Operation: r = code5(C) ⊕ code5(K)")
    print()
    print("3. Output Mapping:")
    print("   - If r = 0:     P = C  (standard pass-through)")
    print("   - If 1 ≤ r ≤ 26: P = letter(r)")
    print("   - If 27 ≤ r ≤ 31: P = C  (SPECIAL: treat as pass-through!)")
    print()
    print("The key discovery is that R27-31 values are treated as pass-through,")
    print("outputting the cipher letter C, not a cyclic mapping.")
    print()
    print("This convention produces Hörenberg's exact P string and IoC value.")


def main():
    """
    Test and document Hörenberg's exact XOR convention.
    """
    exact_match = test_exact_convention()

    if exact_match:
        document_convention()

        # Save the convention
        convention = {
            "layer2_xor": {
                "encoding": "A=1..Z=26",
                "operation": "r = code5(C) XOR code5(K)",
                "mapping": {
                    "r=0": "output C (pass-through)",
                    "r=1-26": "output letter(r)",
                    "r=27-31": "output C (pass-through)"
                },
                "note": "R27-31 treated as pass-through is the key discovery"
            }
        }

        with open('hoerenberg_convention.json', 'w') as f:
            json.dump(convention, f, indent=2)

        print("\nConvention saved to hoerenberg_convention.json")


if __name__ == "__main__":
    main()