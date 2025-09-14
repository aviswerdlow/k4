#!/usr/bin/env python3
"""
Diagnostic script to understand the grid vs tick alignment
"""

import pandas as pd
from pathlib import Path

base_dir = Path('/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus')
model_dir = base_dir / '06_DOCUMENTATION/KryptosModel'

# Load files
grid = pd.read_csv(model_dir / 'kryptos_whole_sculpture_grid.csv')
ticks = pd.read_csv(model_dir / '04_full_sculpture/kryptos_full_sculpture_ticks.csv')
mapped = pd.read_csv(model_dir / '04_full_sculpture/grid_to_ticks_left.csv')

print("=== Grid vs Tick Alignment Diagnostic ===\n")

# Grid analysis
left_grid = grid[grid['side'] == 'LEFT']
print(f"Grid (LEFT side):")
print(f"  Total characters: {len(left_grid)}")
print(f"  Rows: {left_grid['row'].min()}-{left_grid['row'].max()}")
print(f"  Cols per row: {left_grid.groupby('row')['col'].count().describe()}")

# Tick analysis
print(f"\nTicks (full sculpture):")
print(f"  Total ticks: {len(ticks)}")
print(f"  Sections: {ticks['section'].value_counts().to_dict()}")

# Mapped analysis
print(f"\nSuccessfully mapped:")
print(f"  Total: {len(mapped)}")
print(f"  By section: {mapped['section'].value_counts().to_dict()}")

# Show sample of what mapped
print("\nSample of mapped grid positions:")
print(mapped[['row', 'col', 'char', 'section', 'section_index']].head(10))

# Check which rows got mapped
mapped_rows = sorted(mapped['row'].unique())
print(f"\nMapped rows: {mapped_rows}")

# Expected K1-K4 text
k1_ct = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
k2_ct = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKK?DQMCPFQZDQMMIAGPFXHQRLG"
k3_ct = "EVLNOZEKQMGQZHKWNZFWZJEZFWZZQETBQETHEZLBQOKQHULBKQHQTEVLZGOZFELGWHKKDQMEHGQZHKWNZFWZJEZFWZJFTIQ"
k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

print(f"\nExpected first 32 chars of K1 CT: {k1_ct[:32]}")
print(f"Actual mapped chars (first 32):")
if len(mapped) >= 32:
    first_32 = ''.join(mapped.sort_values('global_index').head(32)['char'].values)
    print(f"  {first_32}")

# Check if we're getting the right text
print("\nVerifying text match:")
k1_mapped = mapped[mapped['section'] == 'K1'].sort_values('section_index')
if len(k1_mapped) > 0:
    k1_mapped_text = ''.join(k1_mapped['char'].values)
    print(f"  K1 mapped ({len(k1_mapped_text)} chars): {k1_mapped_text[:40]}...")
    if k1_mapped_text[:20] == k1_ct[:20]:
        print("  ✓ K1 text matches expected ciphertext")
    else:
        print("  ✗ K1 text does NOT match expected")