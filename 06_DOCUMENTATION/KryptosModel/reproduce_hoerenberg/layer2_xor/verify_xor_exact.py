#!/usr/bin/env python3
"""
Verify the XOR operation using Hörenberg's exact C and K strings.
Check if we get his exact P string, confirming the XOR convention.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xor5 import xor5_with_passthrough, letter_to_code5, code5_to_letter


def verify_xor_operation(c_string, k_string, p_expected):
    """
    Apply XOR operation C XOR K and compare with expected P.
    """
    print("VERIFYING XOR OPERATION")
    print("-" * 70)

    if len(c_string) != len(k_string):
        raise ValueError(f"C and K must be same length: {len(c_string)} vs {len(k_string)}")

    results = {
        'positions': [],
        'matches': 0,
        'mismatches': 0,
        'pass_throughs': 0,
        'r27_31': 0
    }

    p_computed = []

    for i, (c_char, k_char) in enumerate(zip(c_string, k_string)):
        c_code = letter_to_code5(c_char)
        k_code = letter_to_code5(k_char)

        if c_code == -1 or k_code == -1:
            p_computed.append('?')
            continue

        # Apply XOR
        r = c_code ^ k_code

        # Apply Hörenberg's mapping
        if r == 0:
            p_char = c_char  # Pass-through
            results['pass_throughs'] += 1
        elif 1 <= r <= 26:
            p_char = code5_to_letter(r)
        else:  # r in 27-31
            # Cyclic mapping
            p_char = code5_to_letter((r - 1) % 26 + 1)
            results['r27_31'] += 1

        p_computed.append(p_char)

        # Check if it matches expected
        expected_char = p_expected[i] if i < len(p_expected) else '?'
        match = (p_char == expected_char)

        if match:
            results['matches'] += 1
        else:
            results['mismatches'] += 1

        results['positions'].append({
            'index': i,
            'c': c_char,
            'c_code': c_code,
            'k': k_char,
            'k_code': k_code,
            'r': r,
            'p_computed': p_char,
            'p_expected': expected_char,
            'match': match,
            'is_passthrough': r == 0,
            'is_r27_31': r > 26
        })

    results['p_computed'] = ''.join(p_computed)
    results['exact_match'] = (results['p_computed'] == p_expected)

    return results


def show_detailed_analysis(results, show_all=False):
    """
    Show detailed position-by-position analysis.
    """
    print("\nDETAILED POSITION ANALYSIS")
    print("-" * 70)
    print("Pos | C  | K  | C⊕K | P_comp | P_exp | Match | Notes")
    print("----|----|----|-----|--------|-------|-------|------")

    positions_to_show = results['positions'] if show_all else results['positions'][:20]

    for pos in positions_to_show:
        notes = []
        if pos['is_passthrough']:
            notes.append("pass")
        if pos['is_r27_31']:
            notes.append(f"R{pos['r']}")

        match_str = "✓" if pos['match'] else "✗"

        print(f"{pos['index']:3d} | {pos['c']}  | {pos['k']}  | {pos['r']:3d} | {pos['p_computed']:^6} | {pos['p_expected']:^5} | {match_str:^5} | {' '.join(notes)}")

    if not show_all and len(results['positions']) > 20:
        print(f"... ({len(results['positions']) - 20} more positions)")


def show_mismatches(results):
    """
    Show only the positions that don't match.
    """
    mismatches = [pos for pos in results['positions'] if not pos['match']]

    if not mismatches:
        print("\n✅ NO MISMATCHES - Perfect reproduction!")
        return

    print(f"\n✗ MISMATCHES ({len(mismatches)} positions)")
    print("-" * 70)
    print("Pos | C  | K  | C⊕K | P_comp | P_exp | Notes")
    print("----|----|----|-----|--------|-------|------")

    for pos in mismatches[:10]:
        notes = []
        if pos['is_passthrough']:
            notes.append("pass")
        if pos['is_r27_31']:
            notes.append(f"R{pos['r']}")

        print(f"{pos['index']:3d} | {pos['c']}  | {pos['k']}  | {pos['r']:3d} | {pos['p_computed']:^6} | {pos['p_expected']:^5} | {' '.join(notes)}")

    if len(mismatches) > 10:
        print(f"... ({len(mismatches) - 10} more mismatches)")


def main():
    """
    Verify Hörenberg's exact XOR operation.
    """
    print("VERIFYING HÖRENBERG'S EXACT XOR OPERATION")
    print("=" * 70)

    # Load Hörenberg's exact strings
    data_file = 'data/hoerenberg_withoutOBKR_extraL.json'
    with open(data_file, 'r') as f:
        hoerenberg_data = json.load(f)

    c_string = hoerenberg_data['C']
    k_string = hoerenberg_data['K']
    p_string = hoerenberg_data['P']

    print(f"Using Hörenberg's published strings:")
    print(f"  C: {c_string[:50]}...")
    print(f"  K: {k_string[:50]}...")
    print(f"  P: {p_string[:50]}...")
    print()

    # Verify the XOR operation
    results = verify_xor_operation(c_string, k_string, p_string)

    print(f"\nRESULTS:")
    print(f"  Computed P: {results['p_computed'][:50]}...")
    print(f"  Expected P: {p_string[:50]}...")
    print(f"  Exact match: {results['exact_match']}")
    print()
    print(f"  Matches: {results['matches']}/{len(c_string)}")
    print(f"  Mismatches: {results['mismatches']}")
    print(f"  Pass-throughs: {results['pass_throughs']}")
    print(f"  R27-31 values: {results['r27_31']}")

    # Show detailed analysis
    show_detailed_analysis(results, show_all=False)

    # Show mismatches if any
    show_mismatches(results)

    # Calculate IoC of computed P
    from ioc import calculate_ioc
    computed_ioc = calculate_ioc(results['p_computed'])
    expected_ioc = hoerenberg_data.get('IoC', 0.0)

    print(f"\nIndex of Coincidence:")
    print(f"  Computed P: {computed_ioc:.8f}")
    print(f"  Expected:   {expected_ioc:.8f}")
    print(f"  Difference: {abs(computed_ioc - expected_ioc):.8f}")

    # Save verification results
    output_file = 'xor_verification.json'
    save_data = {
        'exact_match': results['exact_match'],
        'matches': results['matches'],
        'total': len(c_string),
        'pass_throughs': results['pass_throughs'],
        'r27_31': results['r27_31'],
        'computed_ioc': computed_ioc,
        'expected_ioc': expected_ioc,
        'p_computed': results['p_computed']
    }

    with open(output_file, 'w') as f:
        json.dump(save_data, f, indent=2)

    print(f"\nVerification saved to {output_file}")

    # Final verdict
    print("\n" + "=" * 70)
    print("XOR VERIFICATION VERDICT")
    print("=" * 70)

    if results['exact_match']:
        print("✅ PERFECT REPRODUCTION!")
        print("   Hörenberg's XOR convention confirmed:")
        print("   - A=1..Z=26 encoding")
        print("   - Pass-through when r=0")
        print("   - Cyclic mapping for r in 27-31")
    else:
        print("⚠️ IMPERFECT REPRODUCTION")
        print(f"   {results['mismatches']} mismatches found")
        print("   Need to investigate the discrepancies")


if __name__ == "__main__":
    main()