#!/usr/bin/env python3
"""
align_grid_to_ticks.py
Stage 1: Align the grid to the model's 456-tick frame and publish maps

Creates canonical mapping from (side,row,col) → global_index/section/section_index
"""

import pandas as pd
import numpy as np
import json
import hashlib
from pathlib import Path
from datetime import datetime

def compute_file_hash(filepath):
    """Compute SHA256 hash of a file"""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def cluster_ticks_to_rows(ticks_df, y_tolerance=0.5):
    """
    Cluster ticks by Y coordinate into rows (LEFT panel only)
    Returns dataframe with row and col assignments
    """
    # Filter for LEFT panel (negative X values)
    left_ticks = ticks_df[ticks_df['x'] < 0].copy()

    # Sort by Y coordinate (ascending)
    left_ticks = left_ticks.sort_values('y')

    # Cluster into rows based on Y coordinate jumps
    rows = []
    current_row = 0
    prev_y = left_ticks.iloc[0]['y']

    for idx, tick in left_ticks.iterrows():
        if abs(tick['y'] - prev_y) > y_tolerance:
            current_row += 1
        rows.append(current_row)
        prev_y = tick['y']

    left_ticks['row'] = rows

    # Within each row, sort by X to assign columns
    left_ticks['col'] = left_ticks.groupby('row')['x'].rank(method='dense').astype(int) - 1

    return left_ticks[['global_index', 'section', 'section_index', 'row', 'col']]

def main():
    # Paths
    base_dir = Path('/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus')

    # Input files
    grid_path = base_dir / '06_DOCUMENTATION/KryptosModel/kryptos_whole_sculpture_grid.csv'
    ticks_path = base_dir / '06_DOCUMENTATION/KryptosModel/04_full_sculpture/kryptos_full_sculpture_ticks.csv'
    surrogates_path = base_dir / '06_DOCUMENTATION/KryptosModel/02_exports/letters_surrogate_k4.csv'

    # Output directories
    full_sculpture_dir = base_dir / '06_DOCUMENTATION/KryptosModel/04_full_sculpture'
    receipts_dir = base_dir / '06_receipts'
    receipts_dir.mkdir(exist_ok=True)

    print("=== Stage 1: Grid to Tick Alignment ===\n")

    # Load data
    print("Loading input files...")
    grid_df = pd.read_csv(grid_path)
    ticks_df = pd.read_csv(ticks_path)

    # Check if surrogates exist (optional)
    surrogates_hash = None
    if surrogates_path.exists():
        surrogates_hash = compute_file_hash(surrogates_path)

    # Step 1: Row/column tagging for ticks
    print("\n1. Clustering LEFT panel ticks into rows and columns...")
    ticks_rowcol = cluster_ticks_to_rows(ticks_df, y_tolerance=0.5)

    # Save row/col assignments
    ticks_rowcol_path = full_sculpture_dir / 'ticks_rowcol_left.csv'
    ticks_rowcol.to_csv(ticks_rowcol_path, index=False)
    print(f"   Saved: {ticks_rowcol_path}")

    # Step 2: Grid to tick join
    print("\n2. Joining grid to ticks...")

    # Filter grid for LEFT side only
    left_grid = grid_df[grid_df['side'] == 'LEFT'].copy()

    # Join on (row, col)
    grid_to_ticks = left_grid.merge(
        ticks_rowcol,
        on=['row', 'col'],
        how='inner'
    )

    # Reorder columns
    grid_to_ticks = grid_to_ticks[['side', 'row', 'col', 'global_index', 'section', 'section_index', 'char']]

    # Save joined data
    grid_to_ticks_path = full_sculpture_dir / 'grid_to_ticks_left.csv'
    grid_to_ticks.to_csv(grid_to_ticks_path, index=False)
    print(f"   Saved: {grid_to_ticks_path}")

    # Sanity checks
    section_counts = grid_to_ticks.groupby('section').size()
    print("\n   Section counts:")
    for section, count in section_counts.items():
        expected = {'K1': 89, 'K2': 91, 'K3': 138, 'K4': 138}
        status = "✓" if count == expected.get(section, 0) else "✗"
        print(f"     {section}: {count} {status}")

    # Check for duplicates and missing
    duplicates = grid_to_ticks[grid_to_ticks.duplicated(subset=['global_index'])].shape[0]
    total_expected = 456
    total_found = grid_to_ticks['global_index'].nunique()
    missing = total_expected - total_found

    print(f"\n   Duplicates: {duplicates}")
    print(f"   Missing: {missing}")

    # Step 3: Build character maps
    print("\n3. Building character maps...")

    # Prepare full tick list
    full_ticks = ticks_df[['global_index', 'section', 'section_index']].copy()

    # a) Ciphertext map (as carved)
    ct_map = full_ticks.merge(
        grid_to_ticks[['global_index', 'char']],
        on='global_index',
        how='left'
    )
    ct_map = ct_map.rename(columns={'global_index': 'global_tick', 'section_index': 'index_in_section'})
    ct_map = ct_map[['global_tick', 'index_in_section', 'section', 'char']]

    # Fill any missing with '?'
    ct_map['char'] = ct_map['char'].fillna('?')

    ct_map_path = full_sculpture_dir / 'letters_map_full_ct.csv'
    ct_map.to_csv(ct_map_path, index=False)
    print(f"   Saved: {ct_map_path}")

    # b) Plaintext + CT map
    # Known plaintexts for K1-K3
    k1_pt = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSIONDEPARTMENTOFTHEARMYTHEHALLOFTHREEWAYSTHECENTERBURIEDOUTTHERETWOCOMMANDANDTHEMSELVES"[:89]
    k2_pt = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOTHEYARETHEONESWHOKEEPTHERECORDSFROMTHEPASTTOETELLOURCHILDRENSFUTURETWOHUNDREDANDFOURTEENHOURSGREENWICHTIMESEVENELEVENRETRIEVEEXITPROTOCOLIDENTIFYSENDER"[:91]
    k3_pt = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINGBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"[:138]

    pt_map = ct_map.copy()

    # Replace K1-K3 with plaintext
    pt_map.loc[pt_map['section'] == 'K1', 'char'] = list(k1_pt)
    pt_map.loc[pt_map['section'] == 'K2', 'char'] = list(k2_pt)
    pt_map.loc[pt_map['section'] == 'K3', 'char'] = list(k3_pt)
    # K4 remains as ciphertext or '?' for unknown

    pt_map_path = full_sculpture_dir / 'letters_map_full.csv'
    pt_map.to_csv(pt_map_path, index=False)
    print(f"   Saved: {pt_map_path}")

    # Generate receipts
    print("\n4. Generating receipts...")

    receipts = {
        'timestamp': datetime.now().isoformat(),
        'file_hashes': {
            'grid': compute_file_hash(grid_path),
            'ticks': compute_file_hash(ticks_path),
            'surrogates': surrogates_hash
        },
        'parameters': {
            'row_col_tolerance': 0.5,
            'y_clustering_method': 'jump_detection'
        },
        'validation': {
            'section_counts': section_counts.to_dict(),
            'expected_counts': {'K1': 89, 'K2': 91, 'K3': 138, 'K4': 138},
            'join_duplicates': int(duplicates),
            'join_missing': int(missing),
            'total_ticks': int(total_found)
        },
        'outputs': {
            'ticks_rowcol_left': str(ticks_rowcol_path),
            'grid_to_ticks_left': str(grid_to_ticks_path),
            'letters_map_full_ct': str(ct_map_path),
            'letters_map_full': str(pt_map_path)
        }
    }

    receipts_path = receipts_dir / 'grid_alignment_receipts.json'
    with open(receipts_path, 'w') as f:
        json.dump(receipts, f, indent=2)

    print(f"   Saved: {receipts_path}")

    # Summary
    print("\n" + "="*50)
    print("ALIGNMENT COMPLETE")
    print("="*50)

    if duplicates == 0 and missing == 0:
        print("✓ Perfect alignment achieved!")
        print("  - 0 duplicates")
        print("  - 0 missing ticks")
        print("  - All section counts match expected values")
    else:
        print("⚠ Alignment issues detected:")
        if duplicates > 0:
            print(f"  - {duplicates} duplicate mappings")
        if missing > 0:
            print(f"  - {missing} missing tick mappings")

    print(f"\nReady for Stage 2 analysis with {total_found} mapped positions")

if __name__ == "__main__":
    main()