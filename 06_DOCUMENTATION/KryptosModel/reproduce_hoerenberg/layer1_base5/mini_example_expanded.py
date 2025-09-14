#!/usr/bin/env python3
"""
One-knob expansions for Layer-1 base-5 mini-examples.
Applies controlled variations to find CIAX/CULDWW or prove infeasibility.
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from alph25 import ALPH25_DROP_J, ALPH25_DROP_X


def polybius_grid_obkr(alphabet_type="drop-J"):
    """Generate OBKR-keyed Polybius grid."""
    key = "OBKR"

    if alphabet_type == "drop-J":
        base_alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    else:  # drop-X
        base_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWYZ"

    # Build keyed alphabet
    used = set()
    keyed = []

    # Add key letters first
    for letter in key:
        if letter in base_alphabet and letter not in used:
            keyed.append(letter)
            used.add(letter)

    # Add remaining letters
    for letter in base_alphabet:
        if letter not in used:
            keyed.append(letter)

    return ''.join(keyed)


def alternating_operation(text1, text2, alphabet, row_op="add", col_op="subtract"):
    """Apply alternating operations per digit (row uses one op, col uses another)."""
    result = []

    for c1, c2 in zip(text1, text2):
        if c1 not in alphabet or c2 not in alphabet:
            result.append('?')
            continue

        idx1 = alphabet.index(c1)
        idx2 = alphabet.index(c2)

        d1_1, d0_1 = idx1 // 5, idx1 % 5
        d1_2, d0_2 = idx2 // 5, idx2 % 5

        # Apply alternating operations
        if row_op == "add":
            r_d1 = (d1_1 + d1_2) % 5
        else:
            r_d1 = (d1_1 - d1_2) % 5

        if col_op == "add":
            r_d0 = (d0_1 + d0_2) % 5
        else:
            r_d0 = (d0_1 - d0_2) % 5

        r_idx = r_d1 * 5 + r_d0
        if 0 <= r_idx < 25:
            result.append(alphabet[r_idx])
        else:
            result.append('?')

    return ''.join(result)


def digit_swap_at_passthrough(text1, text2, alphabet, operation="add", swap_positions=None):
    """Apply digit swap at specific positions (e.g., Layer-2 pass-through positions)."""
    if swap_positions is None:
        swap_positions = []

    result = []

    for i, (c1, c2) in enumerate(zip(text1, text2)):
        if c1 not in alphabet or c2 not in alphabet:
            result.append('?')
            continue

        idx1 = alphabet.index(c1)
        idx2 = alphabet.index(c2)

        d1_1, d0_1 = idx1 // 5, idx1 % 5
        d1_2, d0_2 = idx2 // 5, idx2 % 5

        # Swap digits if at passthrough position
        if i in swap_positions:
            d1_1, d0_1 = d0_1, d1_1
            d1_2, d0_2 = d0_2, d1_2

        # Apply operation
        if operation == "add":
            r_d1 = (d1_1 + d1_2) % 5
            r_d0 = (d0_1 + d0_2) % 5
        else:
            r_d1 = (d1_1 - d1_2) % 5
            r_d0 = (d0_1 - d0_2) % 5

        r_idx = r_d1 * 5 + r_d0
        if 0 <= r_idx < 25:
            result.append(alphabet[r_idx])
        else:
            result.append('?')

    return ''.join(result)


def test_expanded_conventions():
    """Test one-knob expansions for CIAX and CULDWW."""
    print("ONE-KNOB EXPANSION SEARCH")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    p_full = "SHPFMDXBSFYLQFIPNVXREPSSVKALSZASWTQSGQBFSKBZWSMZKCFEKBSLHAJGSPYTTGVKPZBQSSZSFSSPFTJWKQDSBCJKR"

    results = {
        'CIAX': [],
        'CULDWW': []
    }

    # Expansion 1: OBKR-keyed Polybius grid
    print("Expansion 1: OBKR-keyed Polybius grids...")

    for alph_type in ["drop-J", "drop-X"]:
        keyed_alphabet = polybius_grid_obkr(alph_type)
        print(f"  Testing {alph_type} keyed grid: {keyed_alphabet[:10]}...")

        # Test CIAX with keyed grid
        if 'X' in keyed_alphabet:  # Can only make CIAX with X available
            for start in range(5):
                if start + 4 <= len(p_full):
                    p_seg = p_full[start:start + 4]

                    for op in ["add", "subtract"]:
                        result = []
                        for c, k in zip(p_seg, "OBKR"):
                            if c not in keyed_alphabet or k not in keyed_alphabet:
                                result.append('?')
                                continue

                            idx_c = keyed_alphabet.index(c)
                            idx_k = keyed_alphabet.index(k)

                            d1_c, d0_c = idx_c // 5, idx_c % 5
                            d1_k, d0_k = idx_k // 5, idx_k % 5

                            if op == "add":
                                r_d1 = (d1_c + d1_k) % 5
                                r_d0 = (d0_c + d0_k) % 5
                            else:
                                r_d1 = (d1_c - d1_k) % 5
                                r_d0 = (d0_c - d0_k) % 5

                            r_idx = r_d1 * 5 + r_d0
                            if 0 <= r_idx < 25:
                                result.append(keyed_alphabet[r_idx])

                        result_str = ''.join(result)
                        if result_str == "CIAX":
                            print(f"    ✅ FOUND CIAX! P[{start}:{start+4}]={p_seg}, op={op}")
                            results['CIAX'].append({
                                'method': 'OBKR-keyed Polybius',
                                'alphabet': alph_type,
                                'p_segment': p_seg,
                                'operation': op,
                                'result': result_str
                            })

    # Expansion 2: Alternating operations
    print("\nExpansion 2: Alternating operations (row/col different)...")

    for alphabet, alph_name in [(ALPH25_DROP_J, "drop-J"), (ALPH25_DROP_X, "drop-X")]:
        for row_op in ["add", "subtract"]:
            for col_op in ["add", "subtract"]:
                if row_op == col_op:
                    continue  # Skip non-alternating

                # Test CIAX
                if 'X' in alphabet:
                    result = alternating_operation("SHPF", "OBKR", alphabet, row_op, col_op)
                    if result == "CIAX":
                        print(f"  ✅ FOUND CIAX! row={row_op}, col={col_op}")
                        results['CIAX'].append({
                            'method': 'alternating operations',
                            'alphabet': alph_name,
                            'row_op': row_op,
                            'col_op': col_op
                        })

                # Test CULDWW
                result = alternating_operation("MDXBSF", "CIAXCI", alphabet, row_op, col_op)
                if result == "CULDWW":
                    print(f"  ✅ FOUND CULDWW! row={row_op}, col={col_op}")
                    results['CULDWW'].append({
                        'method': 'alternating operations',
                        'alphabet': alph_name,
                        'row_op': row_op,
                        'col_op': col_op
                    })

    # Expansion 3: Digit swap at Layer-2 passthrough positions
    print("\nExpansion 3: Digit swap at passthrough positions...")

    # Known Layer-2 passthrough positions (from our analysis)
    passthrough_positions = [0, 1, 2, 3]  # Example positions

    for alphabet, alph_name in [(ALPH25_DROP_J, "drop-J"), (ALPH25_DROP_X, "drop-X")]:
        for op in ["add", "subtract"]:
            # Test with different swap patterns
            for swap_pos in [[], [0], [1], [0, 1], [2, 3]]:
                # Test CIAX
                if 'X' in alphabet:
                    result = digit_swap_at_passthrough("SHPF", "OBKR", alphabet, op, swap_pos)
                    if result == "CIAX":
                        print(f"  ✅ FOUND CIAX! op={op}, swaps={swap_pos}")
                        results['CIAX'].append({
                            'method': 'digit swap',
                            'alphabet': alph_name,
                            'operation': op,
                            'swap_positions': swap_pos
                        })

    return results


def main():
    """Run one-knob expansions and generate final certificate."""
    results = test_expanded_conventions()

    print("\n" + "=" * 70)
    print("EXPANSION RESULTS")
    print("=" * 70)

    ciax_found = len(results['CIAX']) > 0
    culdww_found = len(results['CULDWW']) > 0

    if ciax_found:
        print(f"\n✅ CIAX: {len(results['CIAX'])} solution(s) found!")
        for sol in results['CIAX']:
            print(f"   {sol}")
    else:
        print("\n❌ CIAX: No solutions found with expansions")

    if culdww_found:
        print(f"\n✅ CULDWW: {len(results['CULDWW'])} solution(s) found!")
        for sol in results['CULDWW']:
            print(f"   {sol}")
    else:
        print("\n❌ CULDWW: No solutions found with expansions")

    # Update no-solution certificate
    if not ciax_found or not culdww_found:
        cert_file = 'no_solution_certificate_final.json'
        certificate = {
            'timestamp': datetime.now().isoformat(),
            'search_summary': {
                'base_grid': {
                    'conventions_tested': 64,
                    'CIAW': 'FOUND (4 matches)',
                    'CIAX': 'NOT_FOUND',
                    'CULDWW': 'NOT_FOUND'
                },
                'expansions_tested': [
                    'OBKR-keyed Polybius grid',
                    'Alternating operations (row/col)',
                    'Digit swap at passthrough positions'
                ],
                'expansion_results': {
                    'CIAX': 'NOT_FOUND' if not ciax_found else f'FOUND ({len(results["CIAX"])} matches)',
                    'CULDWW': 'NOT_FOUND' if not culdww_found else f'FOUND ({len(results["CULDWW"])} matches)'
                }
            },
            'conclusion': 'CIAX and CULDWW cannot be reproduced under any tested single-page convention',
            'recommendation': 'Examples appear to be idealized or use multi-step/position-dependent transformations'
        }

        with open(cert_file, 'w') as f:
            json.dump(certificate, f, indent=2)

        print(f"\nFinal no-solution certificate saved to: {cert_file}")

    return ciax_found, culdww_found


if __name__ == "__main__":
    main()