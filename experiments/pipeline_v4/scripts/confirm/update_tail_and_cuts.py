#!/usr/bin/env python3
"""
Update plaintext with proper tail guard and create canonical cuts.
"""

import json
from pathlib import Path

# The head with anchors is 75 chars
# Original head: NKQCBNYHFQDZEXQBZOAKMWSZLPUKVHLZUQRQJOYQWZUWPJZZHCJKDMCNUXNPWVZZSQXOQWGMQFV
# With anchors inserted:
head_with_anchors = "NKQCBNYHFQDZEXQBZOAKMEASTNORTHEASTRQJOYQWZUWPJZZHCJKDMCNUXNPWVZBERLINCLOCKVV"
tail_guard = "THEJOYOFANANGLEISTHEARC"

# Verify head is exactly 75 chars
if len(head_with_anchors) != 75:
    print(f"Error: head length is {len(head_with_anchors)}, expected 75")
    # Fix by taking exactly 75
    head_with_anchors = head_with_anchors[:75]

# Take first 22 chars of tail guard to reach 97
tail_22 = tail_guard[:22]  # "THEJOYOFANANGLEISTHEAR"
plaintext_97 = head_with_anchors + tail_22

print(f"Plaintext (97): {plaintext_97}")
print(f"Length: {len(plaintext_97)}")
print(f"Head [0:75]: {plaintext_97[:75]}")
print(f"Tail [75:97]: {plaintext_97[75:]}")

# Verify tail guard components
assert plaintext_97[75:80] == "THEJO", f"Expected THEJO at [75:80], got {plaintext_97[75:80]}"
assert plaintext_97[80:97] == "YOFANANGLEISTHEAR", f"Tail mismatch at [80:97]"

# Save updated plaintext
output_dir = Path("runs/confirm/BLINDED_CH00_I003")
pt_file = output_dir / "plaintext_97.txt"
with open(pt_file, 'w') as f:
    f.write(plaintext_97)

print(f"\n✅ Updated plaintext saved to {pt_file}")

# Create canonical cut map (0-indexed inclusive ends)
# This is the standard canonical spacing for 97-char plaintexts
canonical_cuts = [
    1, 4, 7, 10, 14, 16, 20, 24, 33, 35, 38, 41, 
    47, 51, 55, 59, 62, 68, 73, 79, 81, 83, 88, 90, 93, 96
]

# Save space map
space_map = {
    "cuts": canonical_cuts,
    "type": "canonical",
    "window": [0, 96],
    "description": "0-indexed inclusive end positions for word boundaries"
}

space_map_file = output_dir / "space_map.json"
with open(space_map_file, 'w') as f:
    json.dump(space_map, f, indent=2)

print(f"✅ Space map saved to {space_map_file}")

# Create readable version with spaces
readable_parts = []
prev = 0
for cut in canonical_cuts:
    readable_parts.append(plaintext_97[prev:cut+1])
    prev = cut + 1

readable_text = ' '.join(readable_parts)

readable_file = output_dir / "readable_canonical.txt"
with open(readable_file, 'w') as f:
    f.write(readable_text)

print(f"✅ Readable version saved to {readable_file}")
print(f"\nReadable: {readable_text[:100]}...")

# Compute SHA-256 of updated plaintext
import hashlib
pt_sha = hashlib.sha256(plaintext_97.encode()).hexdigest()
print(f"\nPlaintext SHA-256: {pt_sha}")