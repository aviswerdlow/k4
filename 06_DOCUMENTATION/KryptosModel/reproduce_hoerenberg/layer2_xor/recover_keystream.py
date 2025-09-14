#!/usr/bin/env python3
"""
Recover Hörenberg's exact keystream from his published C and P strings
This will reveal the precise alignment and extra-L placement he used
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xor5 import letter_to_code5, code5_to_letter
from panel_stream import panel_stream


def recover_keystream_from_cp(ciphertext, plaintext):
    """
    Recover the keystream K from known C and P using XOR relationship

    For each position:
    - If P[i] == C[i], then it was a pass-through (XOR result = 0)
    - Otherwise, K[i] = C[i] XOR P[i]

    Args:
        ciphertext: The C string
        plaintext: The P string (Hörenberg's published result)

    Returns:
        Tuple of (keystream_letters, zero_positions)
    """
    if len(ciphertext) != len(plaintext):
        raise ValueError(f"C and P must be same length: {len(ciphertext)} vs {len(plaintext)}")

    keystream = []
    zero_positions = []

    for i, (c_char, p_char) in enumerate(zip(ciphertext, plaintext)):
        if c_char == p_char:
            # Pass-through occurred, meaning XOR result was 0
            # This means K[i] = C[i] (since C XOR C = 0)
            keystream.append(c_char)
            zero_positions.append(i)
        else:
            # Normal XOR: K = C XOR P
            c_code = letter_to_code5(c_char)
            p_code = letter_to_code5(p_char)

            if c_code == -1 or p_code == -1:
                keystream.append('?')
            else:
                k_code = c_code ^ p_code
                if 1 <= k_code <= 26:
                    keystream.append(code5_to_letter(k_code))
                else:
                    # This shouldn't happen if P was generated correctly
                    keystream.append(f'[{k_code}]')

    return ''.join(keystream), zero_positions


def find_alignment_in_panel_stream(recovered_k, extra_L_variants):
    """
    Find which panel stream variant and offset produces the recovered keystream

    Args:
        recovered_k: The recovered keystream string
        extra_L_variants: List of (name, extra_L_rule, stream) tuples to test

    Returns:
        Best matching configuration
    """
    best_match = None
    best_score = 0

    for variant_name, extra_L_rule, stream in extra_L_variants:
        # Try to find recovered_k as a substring
        if recovered_k in stream:
            offset = stream.index(recovered_k)
            return {
                'variant': variant_name,
                'extra_L_rule': extra_L_rule,
                'offset': offset,
                'exact_match': True
            }

        # Otherwise, find best partial match
        for offset in range(len(stream) - len(recovered_k) + 1):
            window = stream[offset:offset + len(recovered_k)]
            matches = sum(1 for a, b in zip(recovered_k, window) if a == b and a != '?')

            if matches > best_score:
                best_score = matches
                best_match = {
                    'variant': variant_name,
                    'extra_L_rule': extra_L_rule,
                    'offset': offset,
                    'match_score': matches,
                    'total_chars': len(recovered_k),
                    'exact_match': False
                }

    return best_match


def generate_extra_l_variants():
    """
    Generate different extra-L placement variants

    Returns:
        List of (name, rule_description, panel_stream) tuples
    """
    variants = []

    # Variant 1: Extra L after each 26-char row
    stream1 = panel_stream(extra_L=True, min_len=10000)
    variants.append(("After each row", "L inserted after every 26 chars", stream1))

    # Variant 2: No extra L
    stream2 = panel_stream(extra_L=False, min_len=10000)
    variants.append(("No extra L", "Standard panel stream", stream2))

    # Variant 3: Custom - Looking at Hörenberg's K string pattern
    # His K has irregular L placement: ...FGHINGHIJL... and ...GHIJLOHIJL...
    # This suggests specific positions, not regular intervals

    # Let's build what his K string actually shows
    hoerenberg_k_without_obkr = (
        "FGHIJLMNQUVWXZKRYPTOSABCDEFGHI"  # 31 chars
        "NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL"  # 32 chars (extra L at end)
        "OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL"  # 31 chars (L at end)
    )

    # This doesn't follow a simple pattern - it's manually constructed
    variants.append(("Hörenberg manual", "As shown in publication", hoerenberg_k_without_obkr))

    return variants


def main():
    """
    Recover Hörenberg's exact keystream configuration
    """
    print("RECOVERING HÖRENBERG'S EXACT KEYSTREAM")
    print("=" * 70)

    # Hörenberg's published strings (without OBKR)
    hoerenberg_c = "UOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    hoerenberg_p = "SHPFMDXBSFYLQFIPNVXREPSSVKALSZASWTQSGQBFSKBZWSMZKCFEKBSLHAJGSPYTTGVKPZBQSSZSFSSPFTJWKQDSBCJKR"
    hoerenberg_k = "FGHIJLMNQUVWXZKRYPTOSABCDEFGHINGHIJLMNQUVWXZKRYPTOSABCDEFGHIJLOHIJLMNQUVWXZKRYPTOSABCDEFGHIJL"

    print(f"C length: {len(hoerenberg_c)}")
    print(f"P length: {len(hoerenberg_p)}")
    print(f"K length: {len(hoerenberg_k)}")
    print()

    # Step 1: Recover keystream from C and P
    print("Step 1: Recovering keystream from C XOR P = K")
    print("-" * 70)

    recovered_k, zero_pos = recover_keystream_from_cp(hoerenberg_c, hoerenberg_p)

    print(f"Recovered K: {recovered_k[:50]}...")
    print(f"Published K: {hoerenberg_k[:50]}...")
    print(f"Match: {recovered_k == hoerenberg_k}")
    print(f"Pass-through positions: {len(zero_pos)} positions")

    if zero_pos:
        print(f"First few pass-throughs at: {zero_pos[:10]}")
    print()

    # Step 2: Find alignment in panel stream variants
    print("Step 2: Finding panel stream alignment")
    print("-" * 70)

    variants = generate_extra_l_variants()
    best_config = find_alignment_in_panel_stream(hoerenberg_k, variants)

    if best_config:
        print(f"Best match: {best_config['variant']}")
        if best_config['exact_match']:
            print(f"✓ EXACT MATCH at offset {best_config['offset']}")
        else:
            print(f"Partial match: {best_config['match_score']}/{best_config['total_chars']} chars")
            print(f"Offset: {best_config['offset']}")

    # Step 3: Verify the reconstruction
    print("\nStep 3: Verification")
    print("-" * 70)

    # The published K string appears to be manually constructed
    # It doesn't follow a simple algorithmic pattern
    print("Analysis: Hörenberg's K string appears to be manually constructed")
    print("Pattern observed:")
    print("  Segment 1 (31 chars): FGHIJLMNQUVWXZKRYPTOSABCDEFGHI")
    print("  Segment 2 (32 chars): NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL (extra L)")
    print("  Segment 3 (31 chars): OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL (L at end)")
    print()
    print("This doesn't match a simple 'extra L every N chars' rule.")
    print("It appears to be a specific construction for demonstration.")

    # Save the recovered configuration
    import json
    config = {
        'recovered_keystream': hoerenberg_k,
        'c_string': hoerenberg_c,
        'p_string': hoerenberg_p,
        'pass_through_count': len(zero_pos),
        'analysis': 'Manual construction, not algorithmic panel stream'
    }

    with open('recovered_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("\nConfiguration saved to recovered_config.json")


if __name__ == "__main__":
    main()