#!/usr/bin/env python3
"""
Step 1: Construct plaintext with anchors for BLINDED_CH00_I003.
"""

import hashlib
from pathlib import Path

# Original 75-char head from Explore
head_75 = "NKQCBNYHFQDZEXQBZOAKMWSZLPUKVHLZUQRQJOYQWZUWPJZZHCJKDMCNUXNPWVZZSQXOQWGMQFV"

print("=" * 60)
print("STEP 1: CONSTRUCTING PLAINTEXT")
print("=" * 60)
print(f"Original head (75): {head_75}")
print(f"Length: {len(head_75)}")

# Convert to list for manipulation
pt_list = list(head_75)

# Insert anchors at exact indices (overwrite)
# EAST at [21..24]
pt_list[21:25] = "EAST"
print(f"\nAfter EAST insertion: {''.join(pt_list[:35])}")

# NORTHEAST at [25..33]
pt_list[25:34] = "NORTHEAST"
print(f"After NORTHEAST insertion: {''.join(pt_list[:45])}")

# BERLINCLOCK at [63..73]
pt_list[63:74] = "BERLINCLOCK"
print(f"After BERLINCLOCK insertion: {''.join(pt_list[60:])}")

# Get result with anchors (first 75 chars)
pt_with_anchors = ''.join(pt_list[:75])
print(f"\nWith all anchors (75): {pt_with_anchors}")

# Append tail stub (22 'A's to reach 97)
tail_stub = "A" * 22
pt_97 = pt_with_anchors + tail_stub

print(f"\nFull plaintext (97): {pt_97}")
print(f"Length: {len(pt_97)}")

# Verify anchors are at correct positions
assert pt_97[21:25] == "EAST", f"EAST not at [21:25]: {pt_97[21:25]}"
assert pt_97[25:34] == "NORTHEAST", f"NORTHEAST not at [25:34]: {pt_97[25:34]}"
assert pt_97[63:74] == "BERLINCLOCK", f"BERLINCLOCK not at [63:74]: {pt_97[63:74]}"
print("\n✅ All anchors verified at correct positions")

# Save plaintext
output_dir = Path("runs/confirm/BLINDED_CH00_I003")
output_dir.mkdir(parents=True, exist_ok=True)
pt_file = output_dir / "plaintext_97.txt"

with open(pt_file, 'w') as f:
    f.write(pt_97)

# Compute SHA-256
pt_sha = hashlib.sha256(pt_97.encode()).hexdigest()

print(f"\nSaved to: {pt_file}")
print(f"SHA-256: {pt_sha}")

# Display anchor positions for verification
print("\nAnchor positions:")
print(f"  EAST: [21:25] = '{pt_97[21:25]}'")
print(f"  NORTHEAST: [25:34] = '{pt_97[25:34]}'")
print(f"  BERLINCLOCK: [63:74] = '{pt_97[63:74]}'")

print("\n✅ Step 1 complete - plaintext constructed")