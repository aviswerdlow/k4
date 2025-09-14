#!/usr/bin/env python3
"""
Expanded grid search to find CIAX and CULDWW exactly.
Tests more variations including different P string positions and operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alph25 import ALPH25_DROP_J, ALPH25_DROP_X


def base5_operation_flexible(text1, text2, alphabet, operation='subtract', swap=False):
    """
    Flexible base-5 operation with more options.

    Args:
        text1, text2: Input strings
        alphabet: 25-letter alphabet
        operation: 'subtract', 'add', 'xor'
        swap: If True, swap operands (text2 op text1)
    """
    if swap:
        text1, text2 = text2, text1

    result = []
    for c1, c2 in zip(text1, text2):
        if c1 not in alphabet or c2 not in alphabet:
            result.append('?')
            continue

        idx1 = alphabet.index(c1)
        idx2 = alphabet.index(c2)

        # Convert to base-5 digits
        d1_1, d0_1 = idx1 // 5, idx1 % 5
        d1_2, d0_2 = idx2 // 5, idx2 % 5

        if operation == 'subtract':
            r_d1 = (d1_1 - d1_2) % 5
            r_d0 = (d0_1 - d0_2) % 5
        elif operation == 'add':
            r_d1 = (d1_1 + d1_2) % 5
            r_d0 = (d0_1 + d0_2) % 5
        elif operation == 'xor':
            r_d1 = d1_1 ^ d1_2
            r_d0 = d0_1 ^ d0_2
            if r_d1 >= 5 or r_d0 >= 5:
                result.append('?')
                continue
        else:
            result.append('?')
            continue

        r_idx = r_d1 * 5 + r_d0
        if 0 <= r_idx < 25:
            result.append(alphabet[r_idx])
        else:
            result.append('?')

    return ''.join(result)


def scan_for_ciax():
    """
    Comprehensive scan for CIAX using various approaches.
    """
    print("COMPREHENSIVE SCAN FOR CIAX")
    print("=" * 60)

    target = "CIAX"

    # Hörenberg's P string
    p_full = "SHPFMDXBSFYLQFIPNVXREPSSVKALSZASWTQSGQBFSKBZWSMZKCFEKBSLHAJGSPYTTGVKPZBQSSZSFSSPFTJWKQDSBCJKR"

    # Test configurations
    test_cases = []

    # Different P string positions
    p_positions = [
        (0, "SHPF"),   # Start
        (1, "HPFM"),   # +1
        (2, "PFMD"),   # +2
        (3, "FMDX"),   # +3
        (4, "MDXB"),   # +4
    ]

    # Different keys
    keys = ["OBKR", "KRYP", "RYPT", "YPTO", "PTOS", "TOSA", "OBKR"[::-1], "XAIC"]

    # Operations
    operations = ['subtract', 'add', 'xor']

    # Alphabets
    alphabets = [
        ('drop-J', ALPH25_DROP_J),
        ('drop-X', ALPH25_DROP_X)
    ]

    found_exact = False

    for pos, p_seg in p_positions:
        for key in keys:
            for op in operations:
                for swap in [False, True]:
                    for alph_name, alphabet in alphabets:
                        result = base5_operation_flexible(p_seg, key, alphabet, op, swap)

                        if result == target:
                            print(f"✓ FOUND EXACT CIAX!")
                            print(f"  P[{pos}:{pos+4}] = {p_seg}")
                            print(f"  Key = {key}")
                            print(f"  Operation = {'(' + key + ' ' + op + ' ' + p_seg + ')' if swap else '(' + p_seg + ' ' + op + ' ' + key + ')'}")
                            print(f"  Alphabet = {alph_name}")
                            found_exact = True
                            return True

    # Try with different interpretations of "CIAX"
    # Maybe it's the key, not the result?
    print("\nTrying CIAX as key:")
    key = "CIAX"
    for pos, p_seg in p_positions:
        for op in operations:
            for swap in [False, True]:
                for alph_name, alphabet in alphabets:
                    if key[0] not in alphabet:
                        continue
                    result = base5_operation_flexible(p_seg, key, alphabet, op, swap)
                    if len(result) == 4 and '?' not in result:
                        print(f"  P[{pos}:{pos+4}] = {p_seg} {op} CIAX = {result} ({alph_name}, {'swapped' if swap else 'normal'})")

    if not found_exact:
        print("\n✗ Could not reproduce CIAX exactly")
        print("  This example appears to be idealized or uses different data")

    return found_exact


def scan_for_culdww():
    """
    Comprehensive scan for CULDWW using various approaches.
    """
    print("\nCOMPREHENSIVE SCAN FOR CULDWW")
    print("=" * 60)

    target = "CULDWW"

    # From Hörenberg's description
    cipher_segments = [
        "MDXBSF",  # As shown
        "MDXBSF"[::-1],  # Reversed
        "SFMDXB",  # Rotated
    ]

    key_segments = [
        "CIAXCI",  # As shown
        "CIAXCI"[::-1],  # Reversed
        "XIACIA",  # Rotated
    ]

    # Operations
    operations = ['subtract', 'add', 'xor']

    # Alphabets
    alphabets = [
        ('drop-J', ALPH25_DROP_J),
        ('drop-X', ALPH25_DROP_X)
    ]

    found_exact = False

    for cipher in cipher_segments:
        for key in key_segments:
            for op in operations:
                for swap in [False, True]:
                    for alph_name, alphabet in alphabets:
                        # Check if valid in alphabet
                        if 'X' in cipher and alph_name == 'drop-X':
                            continue
                        if 'J' in cipher and alph_name == 'drop-J':
                            continue
                        if 'X' in key and alph_name == 'drop-X':
                            continue

                        result = base5_operation_flexible(cipher, key, alphabet, op, swap)

                        if result == target:
                            print(f"✓ FOUND EXACT CULDWW!")
                            print(f"  Cipher = {cipher}")
                            print(f"  Key = {key}")
                            print(f"  Operation = {'(' + key + ' ' + op + ' ' + cipher + ')' if swap else '(' + cipher + ' ' + op + ' ' + key + ')'}")
                            print(f"  Alphabet = {alph_name}")
                            found_exact = True
                            return True

    if not found_exact:
        print("\n✗ Could not reproduce CULDWW exactly")
        print("  This example appears to be idealized or uses different data")

    return found_exact


def verify_ciaw_again():
    """
    Re-verify CIAW with our confirmed convention.
    """
    print("\nVERIFYING CIAW (CONFIRMED WORKING)")
    print("=" * 60)

    cipher = "SHPF"
    key = "OBKR"
    target = "CIAW"

    result = base5_operation_flexible(cipher, key, ALPH25_DROP_X, 'add', False)

    print(f"Cipher: {cipher}")
    print(f"Key:    {key}")
    print(f"Result: {result}")
    print(f"Target: {target}")
    print(f"Match:  {'✓ YES' if result == target else '✗ NO'}")

    if result == target:
        print("\nDigit-level verification:")
        for c, k, r in zip(cipher, key, result):
            c_idx = ALPH25_DROP_X.index(c)
            k_idx = ALPH25_DROP_X.index(k)
            r_idx = ALPH25_DROP_X.index(r)

            c_d1, c_d0 = c_idx // 5, c_idx % 5
            k_d1, k_d0 = k_idx // 5, k_idx % 5
            r_d1, r_d0 = r_idx // 5, r_idx % 5

            print(f"  {c}({c_d1},{c_d0}) + {k}({k_d1},{k_d0}) = {r}({r_d1},{r_d0})")

    return result == target


def main():
    """
    Run expanded scans for all Layer 1 examples.
    """
    print("EXPANDED LAYER 1 BASE-5 SCAN")
    print("=" * 70)
    print()

    # Verify CIAW (known working)
    ciaw_works = verify_ciaw_again()

    # Scan for CIAX
    ciax_found = scan_for_ciax()

    # Scan for CULDWW
    culdww_found = scan_for_culdww()

    # Summary
    print("\n" + "=" * 70)
    print("LAYER 1 REPRODUCTION SUMMARY")
    print("=" * 70)
    print(f"CIAW:   {'✓ Reproduced' if ciaw_works else '✗ Failed'} (drop-X, addition)")
    print(f"CIAX:   {'✓ Reproduced' if ciax_found else '✗ Cannot reproduce'}")
    print(f"CULDWW: {'✓ Reproduced' if culdww_found else '✗ Cannot reproduce'}")
    print()

    if not (ciax_found and culdww_found):
        print("The CIAX and CULDWW examples appear to be:")
        print("1. Idealized demonstrations")
        print("2. Using different input data than shown")
        print("3. Or employing a different convention we haven't discovered")


if __name__ == "__main__":
    main()