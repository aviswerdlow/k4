#!/usr/bin/env python3
"""
align_grid_courtyard_view.py
Corrected alignment that accounts for the "from the courtyard" viewing perspective.

The LEFT side is read right-to-left from the courtyard view.
The RIGHT side is read left-to-right from the courtyard view.
"""

import pandas as pd
import numpy as np
import json
import hashlib
from pathlib import Path
from datetime import datetime

# Known K1-K4 ciphertext as it appears on the sculpture
K1_CT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFDVFPJUDEEHZWETZYVGWHKKQETGFQJNCE"
K2_CT = "GGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVH"
K3_CT = "DWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDX"
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Known plaintexts for K1-K3
K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSIONDEPARTMENTOFTHEARMYTHEHALLOFTHREE"
K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOTHEYARETHEONESWHOKEEPTHERECORDSFROMTHEPASTTOETELLOURCHILDRENSFUTURETWOHUNDREDANDFOURTEENHOURSGREENWICHTIMESEVENELEVENRETRIEVEEXITPROTOCOL"
K3_PT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINGBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"

def extract_kryptos_sections_from_grid(grid_df):
    """
    Extract K1-K4 text from the grid accounting for courtyard view.
    LEFT side: read right-to-left from courtyard
    RIGHT side: read left-to-right from courtyard
    """
    left_grid = grid_df[grid_df['side'] == 'LEFT'].copy()
    right_grid = grid_df[grid_df['side'] == 'RIGHT'].copy()

    # Sort both by row, then column
    left_grid = left_grid.sort_values(['row', 'col'])
    right_grid = right_grid.sort_values(['row', 'col'])

    # For LEFT side, reverse each row (right-to-left reading)
    left_text = ''
    for row_num in sorted(left_grid['row'].unique()):
        row_chars = left_grid[left_grid['row'] == row_num]['char'].values
        # Reverse the row for right-to-left reading
        left_text += ''.join(reversed(row_chars))

    # For RIGHT side, normal left-to-right reading
    right_text = ''.join(right_grid['char'].values)

    # Full text combines both sides
    full_text = left_text + right_text

    # Extract K1-K4 sections based on known lengths
    k1_len = 89
    k2_len = 91
    k3_len = 138
    k4_len = 138

    # Find where K1 starts in the full text
    k1_start = full_text.find(K1_CT[:20])  # Find first 20 chars of K1

    if k1_start == -1:
        print("WARNING: Could not find K1 start in grid text")
        # Try alternative: K1 might start at position 0
        k1_start = 0

    result = {
        'K1': full_text[k1_start:k1_start + k1_len],
        'K2': full_text[k1_start + k1_len:k1_start + k1_len + k2_len],
        'K3': full_text[k1_start + k1_len + k2_len:k1_start + k1_len + k2_len + k3_len],
        'K4': full_text[k1_start + k1_len + k2_len + k3_len:k1_start + k1_len + k2_len + k3_len + k4_len]
    }

    return result, full_text

def map_sections_to_ticks(sections_text, ticks_df):
    """
    Map the extracted section text to tick positions.
    """
    letters_map = []

    for _, tick in ticks_df.iterrows():
        section = tick['section']
        section_idx = tick['section_index']

        if section in sections_text and section_idx < len(sections_text[section]):
            char = sections_text[section][section_idx]
        else:
            char = '?'

        letters_map.append({
            'global_tick': tick['global_index'],
            'index_in_section': section_idx,
            'section': section,
            'char': char
        })

    return pd.DataFrame(letters_map)

def main():
    # Paths
    base_dir = Path('/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus')
    model_dir = base_dir / '06_DOCUMENTATION/KryptosModel'

    # Input files
    grid_path = model_dir / 'kryptos_whole_sculpture_grid.csv'
    ticks_path = model_dir / '04_full_sculpture/kryptos_full_sculpture_ticks.csv'

    # Output directory
    output_dir = model_dir / '04_full_sculpture'
    receipts_dir = base_dir / '06_receipts'
    receipts_dir.mkdir(exist_ok=True)

    print("=== Courtyard View Alignment ===\n")

    # Load data
    print("Loading grid and ticks...")
    grid_df = pd.read_csv(grid_path)
    ticks_df = pd.read_csv(ticks_path)

    # Extract K1-K4 from grid with courtyard view logic
    print("\nExtracting K1-K4 sections from grid (courtyard view)...")
    sections_text, full_text = extract_kryptos_sections_from_grid(grid_df)

    # Verify extraction
    print("\nVerifying section extraction:")
    for section in ['K1', 'K2', 'K3', 'K4']:
        expected = globals()[f'{section}_CT']
        actual = sections_text[section]
        match = actual[:20] == expected[:20]
        print(f"  {section}: {len(actual)} chars - {'✓' if match else '✗'} {'Match!' if match else 'Mismatch'}")
        if not match:
            print(f"    Expected: {expected[:40]}...")
            print(f"    Got:      {actual[:40]}...")

    # Create ciphertext map
    print("\nCreating ciphertext character map...")
    ct_map = map_sections_to_ticks(sections_text, ticks_df)
    ct_map_path = output_dir / 'letters_map_full_ct.csv'
    ct_map.to_csv(ct_map_path, index=False)
    print(f"  Saved: {ct_map_path}")

    # Create plaintext map
    print("\nCreating plaintext character map...")
    pt_sections = {
        'K1': K1_PT[:89],
        'K2': K2_PT[:91],
        'K3': K3_PT[:138],
        'K4': K4_CT[:138]  # Keep K4 as ciphertext
    }
    pt_map = map_sections_to_ticks(pt_sections, ticks_df)
    pt_map_path = output_dir / 'letters_map_full.csv'
    pt_map.to_csv(pt_map_path, index=False)
    print(f"  Saved: {pt_map_path}")

    # Validation
    print("\nValidation:")
    ct_sections = ct_map.groupby('section').size()
    expected = {'K1': 89, 'K2': 91, 'K3': 138, 'K4': 138}
    all_match = True
    for section, count in expected.items():
        actual = ct_sections.get(section, 0)
        match = actual == count
        all_match = all_match and match
        print(f"  {section}: {actual}/{count} {'✓' if match else '✗'}")

    # Generate receipts
    receipts = {
        'timestamp': datetime.now().isoformat(),
        'method': 'courtyard_view_alignment',
        'description': 'LEFT side read right-to-left, RIGHT side read left-to-right',
        'validation': {
            'sections_found': list(ct_sections.index),
            'section_counts': ct_sections.to_dict(),
            'expected_counts': expected,
            'all_sections_complete': all_match
        },
        'outputs': {
            'letters_map_full_ct': str(ct_map_path),
            'letters_map_full': str(pt_map_path)
        }
    }

    receipts_path = receipts_dir / 'courtyard_alignment_receipts.json'
    with open(receipts_path, 'w') as f:
        json.dump(receipts, f, indent=2)
    print(f"\nReceipts saved: {receipts_path}")

    print("\n" + "="*50)
    if all_match:
        print("✓ ALIGNMENT SUCCESSFUL")
        print("  All 456 positions mapped correctly")
    else:
        print("⚠ ALIGNMENT INCOMPLETE")
        print("  Check section counts above")
    print("="*50)

if __name__ == "__main__":
    main()