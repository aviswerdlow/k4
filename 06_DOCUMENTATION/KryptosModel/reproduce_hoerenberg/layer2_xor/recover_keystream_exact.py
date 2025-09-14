#!/usr/bin/env python3
"""
Recover Hörenberg's exact keystream from published C and P strings.
This reveals the precise K string and how XOR results map.

Key insight: The XOR operation is C XOR K = r, where:
- If r = 0, output P = C (pass-through)
- If 1 ≤ r ≤ 26, output P = letter(r)
- If 27 ≤ r ≤ 31, output P = letter((r-1) % 26 + 1)

To recover K from C and P, we need to reverse this.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xor5 import letter_to_code5, code5_to_letter


def recover_exact_keystream(ciphertext, plaintext, published_keystream=None):
    """
    Recover the exact keystream K from known C and P using XOR relationship.

    The XOR decrypt operation is:
    r = code5(C) XOR code5(K)
    if r == 0: P = C (pass-through)
    elif 1 <= r <= 26: P = letter(r)
    else: P = letter((r-1) % 26 + 1)  # For r in 27-31

    To recover K:
    1. If P == C, then r = 0, so K = C
    2. Otherwise, P = letter(r) for some r
       - If P corresponds to value p_code (1-26), then r could be:
         a) r = p_code (if 1 <= p_code <= 26)
         b) r = p_code + 26 (if cyclic mapping from 27-31)
       - Then K = C XOR r

    Args:
        ciphertext: The C string from Hörenberg
        plaintext: The P string from Hörenberg
        published_keystream: Optional - Hörenberg's published K for validation

    Returns:
        Dict with recovered keystream and analysis
    """
    if len(ciphertext) != len(plaintext):
        raise ValueError(f"C and P must be same length: {len(ciphertext)} vs {len(plaintext)}")

    results = {
        'positions': [],
        'pass_through_count': 0,
        'r27_31_positions': [],
        'recovered_k': [],
        'matches_published': None
    }

    for i, (c_char, p_char) in enumerate(zip(ciphertext, plaintext)):
        c_code = letter_to_code5(c_char)
        p_code = letter_to_code5(p_char)

        if c_code == -1 or p_code == -1:
            results['positions'].append({
                'index': i,
                'c': c_char,
                'p': p_char,
                'error': 'Invalid character'
            })
            results['recovered_k'].append('?')
            continue

        # Check for pass-through (P == C means r = 0)
        if c_char == p_char:
            # Pass-through: r = 0, so C XOR K = 0, meaning K = C
            k_code = c_code
            k_char = c_char
            r_value = 0
            results['pass_through_count'] += 1
        else:
            # P != C, so r != 0
            # P was produced by the mapping of r
            # If 1 <= r <= 26: P = letter(r), so r = p_code
            # If 27 <= r <= 31: P = letter((r-1) % 26 + 1)

            # First try r = p_code (most common case)
            r_value = p_code
            k_code = c_code ^ r_value

            # Check if this gives us a valid K
            if 1 <= k_code <= 26:
                k_char = code5_to_letter(k_code)
            else:
                # k_code is out of range, which might mean r was actually 27-31
                # Let's check if there's an r in 27-31 that would give us P
                found_valid = False
                for r_test in range(27, 32):
                    # This r would produce letter((r_test-1) % 26 + 1)
                    produced_code = (r_test - 1) % 26 + 1
                    if produced_code == p_code:
                        # This r value would produce our P
                        k_code_test = c_code ^ r_test
                        if 1 <= k_code_test <= 26:
                            # This gives us a valid K
                            r_value = r_test
                            k_code = k_code_test
                            k_char = code5_to_letter(k_code)
                            found_valid = True
                            results['r27_31_positions'].append({
                                'index': i,
                                'r': r_value,
                                'c': c_char,
                                'p': p_char,
                                'k': k_char
                            })
                            break

                if not found_valid:
                    # Couldn't find a valid mapping - use the original attempt
                    k_char = f"[{k_code}]"

        results['positions'].append({
            'index': i,
            'c': c_char,
            'c_code': c_code,
            'p': p_char,
            'p_code': p_code,
            'k': k_char,
            'k_code': k_code if 'k_code' in locals() else c_code,
            'r': r_value,
            'pass_through': c_char == p_char
        })

        results['recovered_k'].append(k_char)

    results['recovered_k_string'] = ''.join(str(k) for k in results['recovered_k'])

    # Compare with published keystream if provided
    if published_keystream:
        matches = []
        mismatches = []
        for i, (recovered, published) in enumerate(zip(results['recovered_k'], published_keystream)):
            if str(recovered) == published:
                matches.append(True)
            else:
                matches.append(False)
                mismatches.append({
                    'index': i,
                    'recovered': recovered,
                    'published': published,
                    'c': ciphertext[i],
                    'p': plaintext[i]
                })

        results['matches_published'] = all(matches)
        results['match_positions'] = matches
        results['match_count'] = sum(matches)
        results['total_positions'] = len(matches)
        results['mismatches'] = mismatches

    return results


def analyze_mismatches(results, c_string, p_string, k_string):
    """
    Analyze mismatches to understand the pattern.
    """
    if 'mismatches' not in results or not results['mismatches']:
        return

    print("\nMismatch Analysis:")
    print("-" * 70)
    print("Pos | C  | P  | K_rec | K_pub | C⊕K_rec | C⊕K_pub | Notes")
    print("----|----|----|-------|-------|---------|---------|------")

    for mismatch in results['mismatches'][:10]:  # First 10 mismatches
        i = mismatch['index']
        c = mismatch['c']
        p = mismatch['p']
        k_rec = mismatch['recovered']
        k_pub = mismatch['published']

        c_code = letter_to_code5(c)
        k_rec_code = letter_to_code5(k_rec) if k_rec != '?' and '[' not in str(k_rec) else -1
        k_pub_code = letter_to_code5(k_pub)

        r_rec = c_code ^ k_rec_code if k_rec_code > 0 else -1
        r_pub = c_code ^ k_pub_code

        notes = []
        if r_pub > 26:
            notes.append(f"R{r_pub}")
        if r_pub > 26 and (r_pub - 1) % 26 + 1 == letter_to_code5(p):
            notes.append("✓cyclic")

        print(f"{i:3d} | {c}  | {p}  | {k_rec:^5} | {k_pub:^5} | {r_rec:^7} | {r_pub:^7} | {' '.join(notes)}")


def main():
    """
    Recover Hörenberg's exact keystream configuration.
    """
    print("RECOVERING HÖRENBERG'S EXACT KEYSTREAM")
    print("=" * 70)

    # Load Hörenberg's exact strings
    data_file = 'data/hoerenberg_withoutOBKR_extraL.json'
    with open(data_file, 'r') as f:
        hoerenberg_data = json.load(f)

    c_string = hoerenberg_data['C']
    p_string = hoerenberg_data['P']
    k_string = hoerenberg_data['K']

    print(f"Loaded Hörenberg's strings from {data_file}")
    print(f"C length: {len(c_string)}")
    print(f"P length: {len(p_string)}")
    print(f"K length: {len(k_string)}")
    print()

    # Recover the keystream
    print("Recovering keystream from C and P...")
    print("-" * 70)

    results = recover_exact_keystream(c_string, p_string, k_string)

    print(f"Recovered K: {results['recovered_k_string'][:50]}...")
    print(f"Published K: {k_string[:50]}...")
    print()

    print(f"Pass-through positions: {results['pass_through_count']}")
    print(f"R27-31 positions: {len(results['r27_31_positions'])}")

    if results['matches_published'] is not None:
        print(f"\nComparison with published K:")
        print(f"  Matches: {results['match_count']}/{results['total_positions']}")
        print(f"  Exact match: {results['matches_published']}")

        if not results['matches_published']:
            print(f"  Mismatches: {len(results['mismatches'])} positions")

    # Analyze mismatches
    analyze_mismatches(results, c_string, p_string, k_string)

    # Show R27-31 positions if any
    if results['r27_31_positions']:
        print("\nR27-31 Positions Found:")
        print("-" * 40)
        for r_pos in results['r27_31_positions'][:5]:
            print(f"  Position {r_pos['index']}: r={r_pos['r']}, C={r_pos['c']}, P={r_pos['p']}, K={r_pos['k']}")

    # Save results
    output_file = 'recovered_keystream.json'
    with open(output_file, 'w') as f:
        # Create a serializable version of results
        save_data = {
            'recovered_k': results['recovered_k_string'],
            'published_k': k_string,
            'exact_match': results.get('matches_published', False),
            'pass_through_count': results['pass_through_count'],
            'r27_31_count': len(results['r27_31_positions']),
            'analysis': {
                'total_positions': len(c_string),
                'match_count': results.get('match_count', 0),
                'mismatch_count': len(results.get('mismatches', []))
            }
        }
        json.dump(save_data, f, indent=2)

    print(f"\nResults saved to {output_file}")

    # Final verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if results.get('matches_published'):
        print("✅ EXACT MATCH: Successfully recovered Hörenberg's keystream!")
        print("   The XOR convention is confirmed:")
        print("   - A=1..Z=26 encoding")
        print("   - Pass-through when r=0 (C XOR K = 0)")
        print("   - Cyclic mapping for r in 27-31: letter((r-1) % 26 + 1)")
    else:
        print("⚠️ PARTIAL MATCH: Keystream recovery shows discrepancies")
        print(f"   Matched {results['match_count']}/{results['total_positions']} positions")

        if results['r27_31_positions']:
            print(f"   Found {len(results['r27_31_positions'])} positions with R27-31 values")
            print("   This confirms cyclic mapping for values 27-31")

        print("\n   The mismatches suggest Hörenberg may have:")
        print("   1. Used a different K string than simple panel stream")
        print("   2. Applied manual adjustments for demonstration")
        print("   3. Used a specific panel stream alignment we haven't found")


if __name__ == "__main__":
    main()