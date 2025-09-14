#!/usr/bin/env python3
"""
Grid search to find the exact base-5 convention that produces CIAX/CIAW/CULDWW
Tests different digit mappings, operation directions, and key orientations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alph25 import ALPH25_DROP_J, ALPH25_DROP_X


def base5_operation(c_char, k_char, alphabet, digit_base=0, operation='subtract', digit_order='row_major'):
    """
    Flexible base-5 operation with different conventions

    Args:
        c_char: Cipher character
        k_char: Key character
        alphabet: 25-letter alphabet
        digit_base: 0 for 0-based (0-4), 1 for 1-based (1-5)
        operation: 'subtract' for (C-K)%5, 'add' for (C+K)%5
        digit_order: 'row_major' for d1=row,d0=col or 'col_major' for d1=col,d0=row

    Returns:
        Resulting character
    """
    if c_char not in alphabet or k_char not in alphabet:
        return '?'

    c_idx = alphabet.index(c_char)
    k_idx = alphabet.index(k_char)

    if digit_order == 'row_major':
        # Standard: d1 = idx // 5, d0 = idx % 5
        c_d1, c_d0 = c_idx // 5, c_idx % 5
        k_d1, k_d0 = k_idx // 5, k_idx % 5
    else:
        # Alternative: d1 = idx % 5, d0 = idx // 5
        c_d1, c_d0 = c_idx % 5, c_idx // 5
        k_d1, k_d0 = k_idx % 5, k_idx // 5

    # Apply digit base adjustment
    if digit_base == 1:
        c_d1, c_d0 = c_d1 + 1, c_d0 + 1
        k_d1, k_d0 = k_d1 + 1, k_d0 + 1

    # Perform operation
    if operation == 'subtract':
        if digit_base == 1:
            # For 1-based, adjust the modulo operation
            p_d1 = ((c_d1 - k_d1 - 1) % 5) + 1
            p_d0 = ((c_d0 - k_d0 - 1) % 5) + 1
        else:
            p_d1 = (c_d1 - k_d1) % 5
            p_d0 = (c_d0 - k_d0) % 5
    else:  # add
        if digit_base == 1:
            p_d1 = ((c_d1 + k_d1 - 2) % 5) + 1
            p_d0 = ((c_d0 + k_d0 - 2) % 5) + 1
        else:
            p_d1 = (c_d1 + k_d1) % 5
            p_d0 = (c_d0 + k_d0) % 5

    # Convert back to index
    if digit_base == 1:
        p_d1, p_d0 = p_d1 - 1, p_d0 - 1

    if digit_order == 'row_major':
        p_idx = p_d1 * 5 + p_d0
    else:
        p_idx = p_d0 * 5 + p_d1

    if 0 <= p_idx < 25:
        return alphabet[p_idx]
    return '?'


def test_configuration(cipher_text, key_text, expected_text, alphabet, config):
    """
    Test a specific configuration to see if it produces the expected output

    Args:
        cipher_text: Input cipher
        key_text: Key
        expected_text: Expected plaintext
        alphabet: 25-letter alphabet
        config: Dict with 'digit_base', 'operation', 'digit_order'

    Returns:
        Tuple of (success, actual_output)
    """
    result = []
    for i, (c, k) in enumerate(zip(cipher_text, key_text)):
        if i < len(key_text):
            p = base5_operation(c, k, alphabet, **config)
            result.append(p)

    actual = ''.join(result)
    return actual == expected_text, actual


def grid_search_ciax():
    """
    Search for the configuration that produces CIAX from SHPF - OBKR
    """
    print("GRID SEARCH FOR CIAX/CIAW")
    print("=" * 60)

    # Test data
    cipher = "SHPF"
    key_variants = ["OBKR", "KROB", "RKBO", "BORK"]  # Try different orientations
    target_j = "CIAX"  # Expected with drop-J
    target_x = "CIAW"  # Expected with drop-X

    # Configuration grid
    configs = []
    for digit_base in [0, 1]:
        for operation in ['subtract', 'add']:
            for digit_order in ['row_major', 'col_major']:
                configs.append({
                    'digit_base': digit_base,
                    'operation': operation,
                    'digit_order': digit_order
                })

    # Test all combinations
    found_j = False
    found_x = False

    print("Testing DROP-J alphabet for CIAX:")
    print("-" * 40)
    for config in configs:
        for key in key_variants:
            success, actual = test_configuration(cipher, key, target_j, ALPH25_DROP_J, config)
            if success:
                print(f"✓ FOUND CIAX!")
                print(f"  Config: {config}")
                print(f"  Key: {key}")
                print(f"  {cipher} - {key} = {actual}")
                found_j = True
                break
        if found_j:
            break

    if not found_j:
        print("✗ No configuration produces CIAX")
        # Show what we get with standard config
        std_result = []
        for c, k in zip(cipher, "OBKR"):
            p = base5_operation(c, k, ALPH25_DROP_J, 0, 'subtract', 'row_major')
            std_result.append(p)
        print(f"  Standard gives: {cipher} - OBKR = {''.join(std_result)}")

    print("\nTesting DROP-X alphabet for CIAW:")
    print("-" * 40)
    for config in configs:
        for key in key_variants:
            success, actual = test_configuration(cipher, key, target_x, ALPH25_DROP_X, config)
            if success:
                print(f"✓ FOUND CIAW!")
                print(f"  Config: {config}")
                print(f"  Key: {key}")
                print(f"  {cipher} - {key} = {actual}")
                found_x = True
                break
        if found_x:
            break

    if not found_x:
        print("✗ No configuration produces CIAW")

    return found_j or found_x


def scan_for_ciax_in_p_string():
    """
    Scan the entire P string to see if CIAX appears anywhere
    """
    print("\nSCANNING P STRING FOR CIAX/CIAW PATTERNS")
    print("=" * 60)

    # Hörenberg's P string
    p_string = "SHPFMDXBSFYLQFIPNVXREPSSVKALSZASWTQSGQBFSKBZWSMZKCFEKBSLHAJGSPYTTGVKPZBQSSZSFSSPFTJWKQDSBCJKR"

    # All possible 4-letter keys to test
    test_keys = ["OBKR", "KROB", "RKBO", "BORK", "CIAX", "XAIC", "KRYP", "YPTOS"]

    configs = [
        {'digit_base': 0, 'operation': 'subtract', 'digit_order': 'row_major'},
        {'digit_base': 0, 'operation': 'add', 'digit_order': 'row_major'},
    ]

    found_positions = []

    for start in range(len(p_string) - 3):
        window = p_string[start:start + 4]

        for key in test_keys:
            for config in configs:
                # Test drop-J
                result_j = []
                valid_j = True
                for c, k in zip(window, key):
                    if c in ALPH25_DROP_J and k in ALPH25_DROP_J:
                        p = base5_operation(c, k, ALPH25_DROP_J, **config)
                        result_j.append(p)
                    else:
                        valid_j = False
                        break

                if valid_j and ''.join(result_j) == "CIAX":
                    print(f"✓ Found CIAX at position {start}!")
                    print(f"  P[{start}:{start+4}] = {window}")
                    print(f"  Key: {key}, Config: {config}")
                    found_positions.append((start, window, key, config))

    if not found_positions:
        print("✗ CIAX does not appear in any 4-letter window of P")
        print("  This suggests the examples are idealized or from different data")

    return found_positions


def test_culdww():
    """
    Test the CULDWW example with CIAXCI key
    """
    print("\nTESTING CULDWW EXAMPLE")
    print("=" * 60)

    # From Hörenberg's Further Investigations
    cipher = "MDXBSF"
    key = "CIAXCI"
    target = "CULDWW"

    configs = []
    for digit_base in [0, 1]:
        for operation in ['subtract', 'add']:
            for digit_order in ['row_major', 'col_major']:
                configs.append({
                    'digit_base': digit_base,
                    'operation': operation,
                    'digit_order': digit_order
                })

    found = False
    for config in configs:
        success, actual = test_configuration(cipher, key, target, ALPH25_DROP_J, config)
        if success:
            print(f"✓ FOUND CULDWW!")
            print(f"  Config: {config}")
            print(f"  {cipher} - {key} = {actual}")
            found = True
            break

    if not found:
        print("✗ No configuration produces CULDWW")
        # Show standard result
        std_result = []
        for c, k in zip(cipher, key):
            if c in ALPH25_DROP_J and k in ALPH25_DROP_J:
                p = base5_operation(c, k, ALPH25_DROP_J, 0, 'subtract', 'row_major')
                std_result.append(p)
        print(f"  Standard gives: {cipher} - {key} = {''.join(std_result)}")


def main():
    """Run all grid searches"""
    # Search for CIAX/CIAW
    found_basic = grid_search_ciax()

    # Scan P string for CIAX patterns
    found_in_p = scan_for_ciax_in_p_string()

    # Test CULDWW
    test_culdww()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if found_basic:
        print("✓ Successfully found configuration for CIAX/CIAW")
    elif found_in_p:
        print("⚠ CIAX found in P string but not at expected position")
    else:
        print("✗ Cannot reproduce Hörenberg's Layer 1 examples")
        print("  The examples appear to be idealized or use different data")


if __name__ == "__main__":
    main()