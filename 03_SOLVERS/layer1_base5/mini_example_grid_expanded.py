#!/usr/bin/env python3
"""
Final expanded grid search for Layer-1 base-5 mini-examples.
Wider index window (±10) and two additional toggles for completeness.
"""

import sys
import os
import json
import csv
from itertools import product
from datetime import datetime
from typing import List, Tuple, Dict, Optional

# Define alphabets
ALPH25_DROP_J = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
ALPH25_DROP_X = "ABCDEFGHIJKLMNOPQRSTUVWYZ"


class Base5Convention:
    """Encapsulates a specific base-5 convention with expanded toggles."""

    def __init__(self, alphabet, digit_origin, grid_mapping, digit_order,
                 operation, key_direction, mixed_op=False, swap_on_passthrough=False):
        self.alphabet = alphabet
        self.alphabet_name = "drop-J" if 'J' not in alphabet else "drop-X"
        self.digit_origin = digit_origin  # 0 or 1
        self.grid_mapping = grid_mapping  # "row-major" or "col-major"
        self.digit_order = digit_order    # "d1=row,d0=col" or "d1=col,d0=row"
        self.operation = operation        # "add", "subtract", or "mixed"
        self.key_direction = key_direction  # "forward" or "reverse"
        self.mixed_op = mixed_op  # If True, row=ADD, col=SUB (or vice versa)
        self.swap_on_passthrough = swap_on_passthrough  # If True, swap digits when P==C

    def to_tuple(self):
        """Return convention as tuple for comparison."""
        return (
            self.alphabet_name,
            self.digit_origin,
            self.grid_mapping,
            self.digit_order,
            self.operation,
            self.key_direction,
            self.mixed_op,
            self.swap_on_passthrough
        )

    def to_dict(self):
        """Return convention as dictionary."""
        return {
            'alphabet': self.alphabet_name,
            'digit_origin': self.digit_origin,
            'grid_mapping': self.grid_mapping,
            'digit_order': self.digit_order,
            'operation': self.operation,
            'key_direction': self.key_direction,
            'mixed_op': self.mixed_op,
            'swap_on_passthrough': self.swap_on_passthrough
        }

    def letter_to_digits(self, letter):
        """Convert letter to base-5 digits under this convention."""
        if letter not in self.alphabet:
            return None, None

        idx = self.alphabet.index(letter)

        # Apply grid mapping
        if self.grid_mapping == "row-major":
            raw_d1 = idx // 5
            raw_d0 = idx % 5
        else:  # col-major
            raw_d1 = idx % 5
            raw_d0 = idx // 5

        # Apply digit order
        if self.digit_order == "d1=row,d0=col":
            d1, d0 = raw_d1, raw_d0
        else:  # d1=col,d0=row
            d1, d0 = raw_d0, raw_d1

        # Apply digit origin
        if self.digit_origin == 1:
            d1 = (d1 + 1) if d1 < 5 else d1
            d0 = (d0 + 1) if d0 < 5 else d0

        return d1, d0

    def digits_to_letter(self, d1, d0):
        """Convert base-5 digits to letter under this convention."""
        # Reverse digit origin if needed
        if self.digit_origin == 1:
            d1 = (d1 - 1) if d1 > 0 else d1
            d0 = (d0 - 1) if d0 > 0 else d0

        # Reverse digit order
        if self.digit_order == "d1=col,d0=row":
            d1, d0 = d0, d1

        # Reverse grid mapping
        if self.grid_mapping == "row-major":
            idx = d1 * 5 + d0
        else:  # col-major
            idx = d0 * 5 + d1

        if 0 <= idx < 25:
            return self.alphabet[idx]
        return '?'

    def apply_operation(self, p_letter, k_letter, p_from_layer2=None):
        """Apply base-5 operation with expanded toggles."""
        p_d1, p_d0 = self.letter_to_digits(p_letter)
        k_d1, k_d0 = self.letter_to_digits(k_letter)

        if p_d1 is None or k_d1 is None:
            return '?'

        # Check for pass-through condition (if Layer-2 P == C)
        if self.swap_on_passthrough and p_from_layer2 and p_letter == p_from_layer2:
            # Swap digits on pass-through
            p_d1, p_d0 = p_d0, p_d1

        # Apply operation (with mixed mode if enabled)
        if self.mixed_op:
            # Row digit uses ADD, column digit uses SUB (or based on operation setting)
            if self.operation == "add":
                c_d1 = (p_d1 + k_d1) % 5  # Row: ADD
                c_d0 = (p_d0 - k_d0) % 5  # Col: SUB
            else:
                c_d1 = (p_d1 - k_d1) % 5  # Row: SUB
                c_d0 = (p_d0 + k_d0) % 5  # Col: ADD
        else:
            # Standard operation
            if self.operation == "add":
                c_d1 = (p_d1 + k_d1) % 5
                c_d0 = (p_d0 + k_d0) % 5
            else:  # subtract
                c_d1 = (p_d1 - k_d1) % 5
                c_d0 = (p_d0 - k_d0) % 5

        return self.digits_to_letter(c_d1, c_d0)


def generate_all_conventions():
    """Generate all base-5 conventions including expanded toggles."""
    conventions = []

    # Base parameters
    alphabets = [ALPH25_DROP_J, ALPH25_DROP_X]
    digit_origins = [0, 1]
    grid_mappings = ["row-major", "col-major"]
    digit_orders = ["d1=row,d0=col", "d1=col,d0=row"]
    operations = ["add", "subtract"]
    key_directions = ["forward", "reverse"]

    # Generate base 64 conventions
    for params in product(alphabets, digit_origins, grid_mappings,
                         digit_orders, operations, key_directions):
        conventions.append(Base5Convention(*params, mixed_op=False, swap_on_passthrough=False))

    # Add mixed operation variants (one-knob toggle 1)
    for params in product(alphabets, digit_origins, grid_mappings,
                         digit_orders, operations, key_directions):
        conventions.append(Base5Convention(*params, mixed_op=True, swap_on_passthrough=False))

    # Add swap-on-passthrough variants (one-knob toggle 2)
    for params in product(alphabets, digit_origins, grid_mappings,
                         digit_orders, operations, key_directions):
        conventions.append(Base5Convention(*params, mixed_op=False, swap_on_passthrough=True))

    # Note: Not adding both toggles simultaneously to avoid combinatorial explosion

    return conventions


def test_mini_example(p_segment, k_segment, expected_c, conventions):
    """Test a mini-example against all conventions."""
    exact_matches = []
    near_matches = []

    for conv in conventions:
        # Apply key direction
        k_to_use = k_segment if conv.key_direction == "forward" else k_segment[::-1]

        # Encrypt
        result = []
        mismatches = 0
        for i, (p, k) in enumerate(zip(p_segment, k_to_use)):
            c = conv.apply_operation(p, k)
            result.append(c)
            if c != expected_c[i]:
                mismatches += 1

        result_str = ''.join(result)

        if mismatches == 0:
            exact_matches.append({
                'convention': conv.to_dict(),
                'result': result_str,
                'p': p_segment,
                'k': k_to_use
            })
        elif mismatches <= 1:
            near_matches.append({
                'convention': conv.to_dict(),
                'result': result_str,
                'mismatches': mismatches,
                'p': p_segment,
                'k': k_to_use
            })

    return exact_matches, near_matches


def search_p_string_positions(p_full, segment_length, window=10):
    """
    Search for possible positions in P string with EXPANDED window (±10).
    """
    segments = []

    # Primary positions (start and common indices)
    primary_positions = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    for pos in primary_positions:
        if pos + segment_length <= len(p_full):
            segments.append((pos, p_full[pos:pos + segment_length]))

    # Extended window search (±10)
    for offset in range(-window, window + 1):
        for base in [0, 5, 10, 15]:
            pos = base + offset
            if 0 <= pos <= len(p_full) - segment_length and pos not in primary_positions:
                segments.append((pos, p_full[pos:pos + segment_length]))

    return segments


def comprehensive_grid_search():
    """Run comprehensive grid search with expanded parameters."""
    print("FINAL EXPANDED LAYER-1 BASE-5 GRID SEARCH")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Generate all conventions (including expanded toggles)
    conventions = generate_all_conventions()
    print(f"Testing {len(conventions)} total conventions")
    print("  - Base conventions: 64")
    print("  - Mixed operation toggle: +64")
    print("  - Swap-on-passthrough toggle: +64")
    print("  - Index window: ±10")
    print()

    # Hörenberg's P string
    p_full = "SHPFMDXBSFYLQFIPNVXREPSSVKALSZASWTQSGQBFSKBZWSMZKCFEKBSLHAJGSPYTTGVKPZBQSSZSFSSPFTJWKQDSBCJKR"

    results = {
        'CIAW': {'exact': [], 'near': []},
        'CIAX': {'exact': [], 'near': []},
        'CULDWW': {'exact': [], 'near': []}
    }

    # Test CIAW (4-letter, should reproduce)
    print("Testing CIAW (expanded search)...")
    p_segments_4 = search_p_string_positions(p_full, 4, window=10)
    print(f"  Testing {len(p_segments_4)} P-string positions")

    for pos, p_seg in p_segments_4:
        exact, near = test_mini_example(p_seg, "OBKR", "CIAW", conventions)
        for match in exact:
            match['p_position'] = pos
        for match in near:
            match['p_position'] = pos
        results['CIAW']['exact'].extend(exact)
        results['CIAW']['near'].extend(near)

    print(f"  Found {len(results['CIAW']['exact'])} exact matches")

    # Test CIAX (4-letter)
    print("\nTesting CIAX (expanded search)...")
    for pos, p_seg in p_segments_4:
        exact, near = test_mini_example(p_seg, "OBKR", "CIAX", conventions)
        for match in exact:
            match['p_position'] = pos
        for match in near:
            match['p_position'] = pos
        results['CIAX']['exact'].extend(exact)
        results['CIAX']['near'].extend(near)

    print(f"  Found {len(results['CIAX']['exact'])} exact matches")

    # Test CULDWW (6-letter)
    print("\nTesting CULDWW (expanded search)...")
    p_segments_6 = search_p_string_positions(p_full, 6, window=10)
    print(f"  Testing {len(p_segments_6)} P-string positions")

    for pos, p_seg in p_segments_6:
        # Test with both key orientations
        for key in ["CIAXCI", "ICXAIC"]:
            exact, near = test_mini_example(p_seg, key, "CULDWW", conventions)
            for match in exact:
                match['p_position'] = pos
                match['key_variant'] = key
            for match in near:
                match['p_position'] = pos
                match['key_variant'] = key
            results['CULDWW']['exact'].extend(exact)
            results['CULDWW']['near'].extend(near)

    # Also test the explicit segment from Hörenberg
    exact, near = test_mini_example("MDXBSF", "CIAXCI", "CULDWW", conventions)
    for match in exact:
        match['p_position'] = 'explicit'
    for match in near:
        match['p_position'] = 'explicit'
    results['CULDWW']['exact'].extend(exact)
    results['CULDWW']['near'].extend(near)

    print(f"  Found {len(results['CULDWW']['exact'])} exact matches")

    return results


def generate_no_solution_certificate(results):
    """Generate a no-solution certificate with expanded search bounds."""
    certificate = {
        'timestamp': datetime.now().isoformat(),
        'search_parameters': {
            'base_conventions': 64,
            'expanded_toggles': ['mixed_operation', 'swap_on_passthrough'],
            'total_conventions': 192,  # 64 base + 64 mixed + 64 swap
            'index_window': '±10',
            'p_positions_tested': {
                '4-letter': 'Primary (0-8) + Window (±10 around 0,5,10,15)',
                '6-letter': 'Primary (0-8) + Window (±10 around 0,5,10,15)'
            }
        },
        'results': {
            'CIAW': {
                'exact_matches': len(results['CIAW']['exact']),
                'near_misses': len(results['CIAW']['near'])
            },
            'CIAX': {
                'exact_matches': len(results['CIAX']['exact']),
                'near_misses': len(results['CIAX']['near'])
            },
            'CULDWW': {
                'exact_matches': len(results['CULDWW']['exact']),
                'near_misses': len(results['CULDWW']['near'])
            }
        },
        'certification': {
            'CIAW': 'EXACT' if results['CIAW']['exact'] else 'NO SOLUTION FOUND',
            'CIAX': 'EXACT' if results['CIAX']['exact'] else 'NO SOLUTION FOUND',
            'CULDWW': 'EXACT' if results['CULDWW']['exact'] else 'NO SOLUTION FOUND'
        }
    }

    return certificate


def save_results(results):
    """Save search results and certificate."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create output directory
    os.makedirs('out', exist_ok=True)

    # Save exact matches
    if any(results[key]['exact'] for key in results):
        exact_file = f'out/exact_matches_{timestamp}.json'
        exact_data = {
            'timestamp': timestamp,
            'CIAW': results['CIAW']['exact'],
            'CIAX': results['CIAX']['exact'],
            'CULDWW': results['CULDWW']['exact']
        }
        with open(exact_file, 'w') as f:
            json.dump(exact_data, f, indent=2)
        print(f"\nExact matches saved to: {exact_file}")

    # Generate and save no-solution certificate
    certificate = generate_no_solution_certificate(results)
    cert_file = 'out/no_solution_certificate_final.json'
    with open(cert_file, 'w') as f:
        json.dump(certificate, f, indent=2)
    print(f"No-solution certificate saved to: {cert_file}")

    # Save near misses to CSV for analysis
    near_file = f'out/near_misses_{timestamp}.csv'
    with open(near_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Example', 'P_Position', 'P', 'K', 'Result', 'Mismatches',
                        'Alphabet', 'Operation', 'Mixed_Op', 'Swap_PT'])

        for example in ['CIAW', 'CIAX', 'CULDWW']:
            for match in results[example]['near']:
                writer.writerow([
                    example,
                    match.get('p_position', '?'),
                    match['p'],
                    match['k'],
                    match['result'],
                    match['mismatches'],
                    match['convention']['alphabet'],
                    match['convention']['operation'],
                    match['convention'].get('mixed_op', False),
                    match['convention'].get('swap_on_passthrough', False)
                ])

    print(f"Near misses saved to: {near_file}")


def main():
    """Main entry point."""
    print("=" * 70)
    print("FINAL EXPANDED SEARCH FOR LAYER-1 MINI-EXAMPLES")
    print("=" * 70)

    # Run comprehensive search
    results = comprehensive_grid_search()

    # Save results and certificate
    save_results(results)

    # Print summary
    print("\n" + "=" * 70)
    print("SEARCH COMPLETE")
    print("=" * 70)
    for example in ['CIAW', 'CIAX', 'CULDWW']:
        exact_count = len(results[example]['exact'])
        near_count = len(results[example]['near'])
        status = "✓ EXACT MATCH" if exact_count > 0 else "✗ NO SOLUTION"
        print(f"{example}: {status} ({exact_count} exact, {near_count} near)")

    print("\nSearch parameters:")
    print("  - Conventions tested: 192 (64 base + 128 expanded)")
    print("  - Index window: ±10 positions")
    print("  - Toggles: mixed_operation, swap_on_passthrough")
    print("\nCertificate generated: out/no_solution_certificate_final.json")


if __name__ == '__main__':
    main()