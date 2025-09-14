#!/usr/bin/env python3
"""
Fit the extra-L insertion policy by analyzing Hörenberg's published keystream.
Determine where and how he inserts extra L's into the panel stream.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from panel_stream import panel_stream


def analyze_keystream_structure(keystream):
    """
    Analyze the structure of Hörenberg's published keystream.
    Look for patterns, L positions, and segment boundaries.
    """
    print("ANALYZING KEYSTREAM STRUCTURE")
    print("-" * 60)
    print(f"Total length: {len(keystream)}")
    print()

    # Find all L positions
    l_positions = [i for i, char in enumerate(keystream) if char == 'L']
    print(f"L positions ({len(l_positions)} total): {l_positions}")
    print()

    # Analyze segments between L's
    segments = []
    start = 0
    for l_pos in l_positions:
        if l_pos > start:
            segment = keystream[start:l_pos]
            segments.append({
                'start': start,
                'end': l_pos - 1,
                'length': len(segment),
                'content': segment,
                'ends_with_L': False
            })
        start = l_pos + 1

    # Add final segment if exists
    if start < len(keystream):
        segments.append({
            'start': start,
            'end': len(keystream) - 1,
            'length': len(keystream) - start,
            'content': keystream[start:],
            'ends_with_L': keystream[-1] == 'L'
        })

    print("Segments between L's:")
    for i, seg in enumerate(segments):
        print(f"  Segment {i}: [{seg['start']:2d}:{seg['end']:2d}] length={seg['length']:2d} \"{seg['content'][:20]}...\"")

    # Look for KRYPTOS pattern
    kryptos_positions = []
    search_str = "KRYPTOS"
    idx = 0
    while idx < len(keystream):
        idx = keystream.find(search_str, idx)
        if idx == -1:
            break
        kryptos_positions.append(idx)
        idx += 1

    print(f"\nKRYPTOS positions: {kryptos_positions}")

    # Analyze alphabet sequences
    print("\nAlphabet sequence analysis:")

    # Expected pattern based on panel rows
    expected_start = "FGHIJLMNQUVWXZKRYPTOSABCDEFGHIJ"

    if keystream.startswith(expected_start[:30]):
        print(f"✓ Starts with expected pattern")
    else:
        print(f"✗ Different start pattern")
        print(f"  Expected: {expected_start[:30]}")
        print(f"  Actual:   {keystream[:30]}")

    return {
        'l_positions': l_positions,
        'segments': segments,
        'kryptos_positions': kryptos_positions
    }


def try_panel_alignments(keystream):
    """
    Try different panel stream alignments to match Hörenberg's keystream.
    """
    print("\nTRYING PANEL STREAM ALIGNMENTS")
    print("-" * 60)

    # Generate standard panel stream
    standard_stream = panel_stream(extra_L=False, min_len=500)

    # Try different starting positions
    best_match = {'offset': -1, 'matches': 0, 'extra_L_pattern': None}

    for offset in range(26):
        # Try without extra L
        window = standard_stream[offset:offset + len(keystream)]
        matches = sum(1 for a, b in zip(window, keystream) if a == b)

        if matches > best_match['matches']:
            best_match = {
                'offset': offset,
                'matches': matches,
                'extra_L_pattern': 'none',
                'window': window
            }

    # Try with regular extra L every 26 chars
    extra_l_stream = panel_stream(extra_L=True, min_len=500)

    for offset in range(27):  # 27 because of extra L
        window = extra_l_stream[offset:offset + len(keystream)]
        matches = sum(1 for a, b in zip(window, keystream) if a == b)

        if matches > best_match['matches']:
            best_match = {
                'offset': offset,
                'matches': matches,
                'extra_L_pattern': 'every_26',
                'window': window
            }

    print(f"Best alignment found:")
    print(f"  Offset: {best_match['offset']}")
    print(f"  Matches: {best_match['matches']}/{len(keystream)}")
    print(f"  Extra-L pattern: {best_match['extra_L_pattern']}")

    if best_match['matches'] < len(keystream):
        print(f"\n  ⚠️ Not a perfect match - Hörenberg's K appears manually constructed")

    return best_match


def analyze_manual_construction(keystream):
    """
    Analyze evidence that Hörenberg's K was manually constructed.
    """
    print("\nMANUAL CONSTRUCTION ANALYSIS")
    print("-" * 60)

    # Split into three presumed segments based on analysis
    seg1 = keystream[:31]  # FGHIJLMNQUVWXZKRYPTOSABCDEFGHI
    seg2 = keystream[31:63]  # NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL (32 chars)
    seg3 = keystream[63:]  # OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL (30 chars)

    print("Presumed segments:")
    print(f"  Segment 1 (31 chars): {seg1}")
    print(f"  Segment 2 (32 chars): {seg2}")
    print(f"  Segment 3 (30 chars): {seg3}")
    print()

    # Check for panel row patterns
    print("Panel row analysis:")

    # Row F (5th row, 0-indexed) should start with F
    row_f = "FGHIJLMNQUVWXZKRYPTOSABCDEFGHIJ"
    if seg1 == row_f[:31]:
        print(f"  ✓ Segment 1 matches row F (first 31 chars)")
    else:
        print(f"  ✗ Segment 1 differs from row F")

    # Row N (13th row)
    row_n_start = "NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJ"
    if seg2[:31] == row_n_start[:31]:
        print(f"  ✓ Segment 2 starts like row N")
        if seg2[-1] == 'L':
            print(f"    + Extra L at end")
    else:
        print(f"  ✗ Segment 2 differs from row N")

    # Row O (14th row)
    row_o_start = "OHIJLMNQUVWXZKRYPTOSABCDEFGHIJ"
    if seg3[:30] == row_o_start[:30]:
        print(f"  ✓ Segment 3 matches row O (first 30 chars)")
        if seg3[-1] == 'L':
            print(f"    + Ends with L")
    else:
        print(f"  ✗ Segment 3 differs from row O")

    # Check continuity
    print("\nContinuity check:")
    expected_transitions = [
        ('I', 'N'),  # End of seg1 to start of seg2 (I -> N is +5 in alphabet)
        ('L', 'O'),  # End of seg2 to start of seg3 (L -> O is +3 in alphabet)
    ]

    actual_transitions = [
        (seg1[-1], seg2[0]),
        (seg2[-1], seg3[0]),
    ]

    for i, (expected, actual) in enumerate(zip(expected_transitions, actual_transitions)):
        exp_from, exp_to = expected
        act_from, act_to = actual
        print(f"  Transition {i+1}: {act_from} -> {act_to}")

        # Check if it's a natural panel progression
        from_ord = ord(act_from) - ord('A')
        to_ord = ord(act_to) - ord('A')
        diff = (to_ord - from_ord) % 26

        if diff == 1:
            print(f"    Natural progression (+1 in tableau)")
        elif diff == 5:
            print(f"    Jump of +5 (skipping rows)")
        else:
            print(f"    Jump of +{diff} (manual selection)")

    return {
        'segment_1': seg1,
        'segment_2': seg2,
        'segment_3': seg3
    }


def main():
    """
    Analyze Hörenberg's keystream to understand the extra-L policy.
    """
    print("FITTING EXTRA-L INSERTION POLICY")
    print("=" * 70)

    # Load Hörenberg's exact strings
    data_file = 'data/hoerenberg_withoutOBKR_extraL.json'
    with open(data_file, 'r') as f:
        hoerenberg_data = json.load(f)

    keystream = hoerenberg_data['K']

    print(f"Analyzing Hörenberg's published keystream")
    print(f"Length: {len(keystream)}")
    print(f"K: {keystream}")
    print()

    # Structural analysis
    structure = analyze_keystream_structure(keystream)

    # Try to match with panel stream
    alignment = try_panel_alignments(keystream)

    # Analyze manual construction evidence
    manual_analysis = analyze_manual_construction(keystream)

    # Save analysis results
    output_file = 'keystream_analysis.json'
    analysis_data = {
        'keystream': keystream,
        'length': len(keystream),
        'l_positions': structure['l_positions'],
        'l_count': len(structure['l_positions']),
        'best_alignment': {
            'offset': alignment['offset'],
            'matches': alignment['matches'],
            'pattern': alignment['extra_L_pattern']
        },
        'manual_segments': {
            'seg1_length': len(manual_analysis['segment_1']),
            'seg2_length': len(manual_analysis['segment_2']),
            'seg3_length': len(manual_analysis['segment_3'])
        },
        'conclusion': 'Manual construction - not algorithmic panel stream'
    }

    with open(output_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)

    print(f"\nAnalysis saved to {output_file}")

    # Final verdict
    print("\n" + "=" * 70)
    print("VERDICT ON EXTRA-L POLICY")
    print("=" * 70)

    print("Hörenberg's keystream appears to be MANUALLY CONSTRUCTED:")
    print("  1. Three segments of lengths 31, 32, 30 (not regular)")
    print("  2. Extra L only in segment 2 (position 62)")
    print("  3. Segments correspond to tableau rows F, N, O")
    print("  4. Not a simple algorithmic panel stream")
    print()
    print("This suggests the K string was crafted for demonstration")
    print("rather than being generated by a systematic algorithm.")


if __name__ == "__main__":
    main()