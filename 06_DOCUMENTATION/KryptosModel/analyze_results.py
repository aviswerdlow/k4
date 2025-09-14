#!/usr/bin/env python3
"""
Analyze the scoring results to understand the distribution
"""

import json
import pandas as pd
import numpy as np

# Load results
with open('lm_scores.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

print("="*60)
print("SCORING RESULTS ANALYSIS")
print("="*60)

# Basic statistics
print(f"\nTotal tests: {len(df)}")
print(f"Tests by M value:")
for m in sorted(df['M'].unique()):
    count = len(df[df['M'] == m])
    print(f"  M={m}: {count} tests")

# Score distribution
print(f"\nScore distribution:")
print(f"  Min: {df['score'].min():.3f}")
print(f"  Max: {df['score'].max():.3f}")
print(f"  Mean: {df['score'].mean():.3f}")
print(f"  Std: {df['score'].std():.3f}")

# P-value distribution
print(f"\nRaw p-value distribution:")
print(f"  Min: {df['p_raw'].min():.6f}")
print(f"  Max: {df['p_raw'].max():.6f}")
print(f"  Median: {df['p_raw'].median():.6f}")

# Count by p-value thresholds
print(f"\nTests by p-value threshold:")
print(f"  p_raw < 0.05: {len(df[df['p_raw'] < 0.05])}")
print(f"  p_raw < 0.01: {len(df[df['p_raw'] < 0.01])}")
print(f"  p_raw < 0.001: {len(df[df['p_raw'] < 0.001])}")

print(f"\nAfter Bonferroni correction:")
print(f"  p_adj < 0.05: {len(df[df['p_adj'] < 0.05])}")
print(f"  p_adj < 0.01: {len(df[df['p_adj'] < 0.01])}")
print(f"  p_adj < 0.001: {len(df[df['p_adj'] < 0.001])}")

# Best results
print(f"\nTop 5 results by raw p-value:")
top5 = df.nsmallest(5, 'p_raw')[['angle', 'M', 'score', 'p_raw', 'p_adj', 'overlay_sample']]
for idx, row in top5.iterrows():
    print(f"  Angle {row['angle']}°, M={row['M']}: p_raw={row['p_raw']:.4f}, p_adj={row['p_adj']:.4f}")
    print(f"    Score: {row['score']:.3f}, Text: {row['overlay_sample']}")

# Check for any patterns in angles
print(f"\nAngles tested: {sorted(df['angle'].unique())}")

# Check size after masking
print(f"\nEffect of anchor masking:")
for m in sorted(df['M'].unique()):
    subset = df[df['M'] == m]
    avg_masked = subset['size_masked'].mean()
    print(f"  M={m}: Average {avg_masked:.1f} letters after masking (from {m})")

print("\n" + "="*60)
print("INTERPRETATION")
print("="*60)

if df['p_adj'].min() > 0.001:
    print("\n✗ NO SIGNIFICANT RESULTS")
    print("All adjusted p-values exceed the 0.001 threshold.")
    print("The projection hypothesis shows no significant effects.")
    print("\nThis is expected with random mock data.")
    print("Real character mappings may produce different results.")
else:
    sig_count = len(df[df['p_adj'] <= 0.001])
    print(f"\n✓ {sig_count} SIGNIFICANT RESULTS FOUND")
    
print("\nNote: Using mock data with random selections.")
print("Production run requires actual letters_map.csv from vendor.")