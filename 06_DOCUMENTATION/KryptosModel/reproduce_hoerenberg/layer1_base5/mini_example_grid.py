#!/usr/bin/env python3
"""
Comprehensive, bounded grid search for Layer-1 base-5 mini-examples.
Exhaustively tests all reasonable conventions to find exact matches or prove infeasibility.
"""

import sys
import os
import json
import csv
from itertools import product
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from alph25 import ALPH25_DROP_J, ALPH25_DROP_X


class Base5Convention:
    """Encapsulates a specific base-5 convention."""

    def __init__(self, alphabet, digit_origin, grid_mapping, digit_order, operation, key_direction):
        self.alphabet = alphabet
        self.alphabet_name = "drop-J" if 'J' not in alphabet else "drop-X"
        self.digit_origin = digit_origin  # 0 or 1
        self.grid_mapping = grid_mapping  # "row-major" or "col-major"
        self.digit_order = digit_order    # "d1=row,d0=col" or "d1=col,d0=row"
        self.operation = operation        # "add" or "subtract"
        self.key_direction = key_direction  # "forward" or "reverse"

    def to_tuple(self):
        """Return convention as tuple for comparison."""
        return (
            self.alphabet_name,
            self.digit_origin,
            self.grid_mapping,
            self.digit_order,
            self.operation,
            self.key_direction
        )

    def to_dict(self):
        """Return convention as dictionary."""
        return {
            'alphabet': self.alphabet_name,
            'digit_origin': self.digit_origin,
            'grid_mapping': self.grid_mapping,
            'digit_order': self.digit_order,
            'operation': self.operation,
            'key_direction': self.key_direction
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

    def apply_operation(self, text1, text2):
        """Apply base-5 operation to two texts."""
        # Handle key direction
        if self.key_direction == "reverse":
            text2 = text2[::-1]

        result = []
        for c1, c2 in zip(text1, text2):
            d1_1, d0_1 = self.letter_to_digits(c1)
            d1_2, d0_2 = self.letter_to_digits(c2)

            if d1_1 is None or d1_2 is None:
                result.append('?')
                continue

            # Apply operation
            if self.operation == "add":
                r_d1 = (d1_1 + d1_2) % 5
                r_d0 = (d0_1 + d0_2) % 5
            else:  # subtract
                r_d1 = (d1_1 - d1_2) % 5
                r_d0 = (d0_1 - d0_2) % 5

            r_letter = self.digits_to_letter(r_d1, r_d0)
            result.append(r_letter)

        return ''.join(result)


def generate_all_conventions():
    """Generate all possible base-5 conventions to test."""
    conventions = []

    alphabets = [
        ("drop-J", ALPH25_DROP_J),
        ("drop-X", ALPH25_DROP_X)
    ]

    digit_origins = [0, 1]
    grid_mappings = ["row-major", "col-major"]
    digit_orders = ["d1=row,d0=col", "d1=col,d0=row"]
    operations = ["add", "subtract"]
    key_directions = ["forward", "reverse"]

    for (alph_name, alphabet), origin, grid, order, op, key_dir in product(
        alphabets, digit_origins, grid_mappings, digit_orders, operations, key_directions
    ):
        convention = Base5Convention(
            alphabet=alphabet,
            digit_origin=origin,
            grid_mapping=grid,
            digit_order=order,
            operation=op,
            key_direction=key_dir
        )
        conventions.append(convention)

    return conventions


def test_mini_example(p_segment, key, target, conventions):
    """Test all conventions for a specific mini-example."""
    exact_matches = []
    near_misses = []

    for convention in conventions:
        # Skip if target contains letter not in alphabet
        if any(letter not in convention.alphabet for letter in target):
            continue

        result = convention.apply_operation(p_segment, key)

        if result == target:
            exact_matches.append({
                'convention': convention.to_dict(),
                'p_segment': p_segment,
                'key': key,
                'result': result,
                'target': target
            })
        else:
            # Calculate Hamming distance
            hamming = sum(1 for r, t in zip(result, target) if r != t)
            if hamming == 1:
                near_misses.append({
                    'convention': convention.to_dict(),
                    'p_segment': p_segment,
                    'key': key,
                    'result': result,
                    'target': target,
                    'hamming': hamming
                })

    return exact_matches, near_misses


def search_p_string_positions(p_full, segment_length, window=3):
    """Generate P string segments to test within a window."""
    segments = []

    # Primary positions (start and common indices)
    primary_positions = [0, 1, 2, 3, 4]

    for pos in primary_positions:
        if pos + segment_length <= len(p_full):
            segments.append((pos, p_full[pos:pos + segment_length]))

    # Extended window search if needed
    for offset in range(-window, window + 1):
        for base in [0, 4, 8]:
            pos = base + offset
            if 0 <= pos <= len(p_full) - segment_length and pos not in primary_positions:
                segments.append((pos, p_full[pos:pos + segment_length]))

    return segments


def comprehensive_grid_search():
    """Run comprehensive grid search for all mini-examples."""
    print("COMPREHENSIVE LAYER-1 BASE-5 GRID SEARCH")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Generate all conventions
    conventions = generate_all_conventions()
    print(f"Testing {len(conventions)} total conventions")
    print()

    # Hörenberg's P string
    p_full = "SHPFMDXBSFYLQFIPNVXREPSSVKALSZASWTQSGQBFSKBZWSMZKCFEKBSLHAJGSPYTTGVKPZBQSSZSFSSPFTJWKQDSBCJKR"

    results = {
        'CIAW': {'exact': [], 'near': []},
        'CIAX': {'exact': [], 'near': []},
        'CULDWW': {'exact': [], 'near': []}
    }

    # Test CIAW (4-letter, should reproduce)
    print("Testing CIAW (SHPF + OBKR)...")
    p_segments_4 = search_p_string_positions(p_full, 4)

    for pos, p_seg in p_segments_4:
        exact, near = test_mini_example(p_seg, "OBKR", "CIAW", conventions)
        results['CIAW']['exact'].extend(exact)
        results['CIAW']['near'].extend(near)

    print(f"  Found {len(results['CIAW']['exact'])} exact matches")

    # Test CIAX (4-letter)
    print("\nTesting CIAX (SHPF + OBKR)...")
    for pos, p_seg in p_segments_4:
        exact, near = test_mini_example(p_seg, "OBKR", "CIAX", conventions)
        results['CIAX']['exact'].extend(exact)
        results['CIAX']['near'].extend(near)

    print(f"  Found {len(results['CIAX']['exact'])} exact matches")

    # Test CULDWW (6-letter)
    print("\nTesting CULDWW (MDXBSF + CIAXCI)...")
    p_segments_6 = search_p_string_positions(p_full, 6)

    for pos, p_seg in p_segments_6:
        # Test with both key orientations
        for key in ["CIAXCI", "ICXAIC"]:
            exact, near = test_mini_example(p_seg, key, "CULDWW", conventions)
            results['CULDWW']['exact'].extend(exact)
            results['CULDWW']['near'].extend(near)

    # Also test the explicit segment from Hörenberg
    exact, near = test_mini_example("MDXBSF", "CIAXCI", "CULDWW", conventions)
    results['CULDWW']['exact'].extend(exact)
    results['CULDWW']['near'].extend(near)

    print(f"  Found {len(results['CULDWW']['exact'])} exact matches")

    return results


def save_results(results):
    """Save search results to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save exact matches
    exact_file = f'grid_search_exact_{timestamp}.json'
    exact_data = {
        'timestamp': timestamp,
        'CIAW': results['CIAW']['exact'],
        'CIAX': results['CIAX']['exact'],
        'CULDWW': results['CULDWW']['exact']
    }

    with open(exact_file, 'w') as f:
        json.dump(exact_data, f, indent=2)

    print(f"\nExact matches saved to: {exact_file}")

    # Save near misses to CSV
    near_file = f'grid_search_near_{timestamp}.csv'
    with open(near_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Target', 'P_Segment', 'Key', 'Result', 'Hamming',
                        'Alphabet', 'Origin', 'Grid', 'Order', 'Operation', 'KeyDir'])

        for target in ['CIAW', 'CIAX', 'CULDWW']:
            for miss in results[target]['near']:
                conv = miss['convention']
                writer.writerow([
                    target, miss['p_segment'], miss['key'], miss['result'], miss['hamming'],
                    conv['alphabet'], conv['digit_origin'], conv['grid_mapping'],
                    conv['digit_order'], conv['operation'], conv['key_direction']
                ])

    print(f"Near misses saved to: {near_file}")

    # Generate no-solution certificate if needed
    if not results['CIAX']['exact'] or not results['CULDWW']['exact']:
        cert_file = 'no_solution_certificate.json'
        certificate = {
            'timestamp': timestamp,
            'search_parameters': {
                'alphabets': ['drop-J', 'drop-X'],
                'digit_origins': [0, 1],
                'grid_mappings': ['row-major', 'col-major'],
                'digit_orders': ['d1=row,d0=col', 'd1=col,d0=row'],
                'operations': ['add', 'subtract'],
                'key_directions': ['forward', 'reverse'],
                'total_conventions': 64,
                'p_string_window': 3
            },
            'results': {
                'CIAW': 'REPRODUCED' if results['CIAW']['exact'] else 'NOT_FOUND',
                'CIAX': 'REPRODUCED' if results['CIAX']['exact'] else 'NOT_FOUND',
                'CULDWW': 'REPRODUCED' if results['CULDWW']['exact'] else 'NOT_FOUND'
            },
            'near_misses': {
                'CIAX': len(results['CIAX']['near']),
                'CULDWW': len(results['CULDWW']['near'])
            }
        }

        with open(cert_file, 'w') as f:
            json.dump(certificate, f, indent=2)

        print(f"\nNo-solution certificate saved to: {cert_file}")

    return exact_file, near_file


def main():
    """Run comprehensive grid search and save results."""
    results = comprehensive_grid_search()

    print("\n" + "=" * 70)
    print("GRID SEARCH SUMMARY")
    print("=" * 70)

    for target in ['CIAW', 'CIAX', 'CULDWW']:
        exact_count = len(results[target]['exact'])
        near_count = len(results[target]['near'])

        if exact_count > 0:
            print(f"\n✅ {target}: {exact_count} exact match(es) found!")
            # Show first match
            if results[target]['exact']:
                first = results[target]['exact'][0]
                print(f"   Convention: {first['convention']}")
                print(f"   {first['p_segment']} + {first['key']} = {first['result']}")
        else:
            print(f"\n❌ {target}: No exact matches (Hamming-1: {near_count})")

    # Save all results
    exact_file, near_file = save_results(results)

    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    ciaw_found = bool(results['CIAW']['exact'])
    ciax_found = bool(results['CIAX']['exact'])
    culdww_found = bool(results['CULDWW']['exact'])

    if ciaw_found and ciax_found and culdww_found:
        print("✅ ALL MINI-EXAMPLES REPRODUCED EXACTLY!")
    elif ciaw_found:
        print("⚠️ PARTIAL REPRODUCTION: Only CIAW reproduced exactly")
        print("   CIAX and CULDWW appear to be idealized or use different data")
    else:
        print("❌ CRITICAL: Even CIAW not reproduced - check implementation")

    return ciaw_found, ciax_found, culdww_found


if __name__ == "__main__":
    main()