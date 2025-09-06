#!/usr/bin/env python3
"""
Verify updated plaintext still encrypts to CT and create canonical cuts.
"""

import json
import sys
from pathlib import Path
sys.path.append('.')
from tycho_min.feasibility import MinimalTychoSolver

# Load updated plaintext
with open('runs/confirm/BLINDED_CH00_I003/plaintext_97.txt') as f:
    plaintext = f.read().strip()

print("=" * 60)
print("VERIFYING UPDATED PLAINTEXT")
print("=" * 60)
print(f"Plaintext: {plaintext[:50]}...")
print(f"Tail: ...{plaintext[-22:]}")

# Frozen schedule
families = ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'beaufort', 'beaufort']
periods = [17, 16, 16, 16, 19, 20]
phases = [0, 0, 0, 0, 0, 0]

# Verify it still encrypts to CT
solver = MinimalTychoSolver()
route_file = 'routes/permutations/GRID_W14_ROWS.json'
result = solver.test_feasibility(plaintext, route_file, families, periods, phases)

if not result['feasible']:
    print(f"❌ ERROR: Updated plaintext no longer encrypts to CT!")
    print(f"Reason: {result.get('reason')}")
    sys.exit(1)

print("✅ Still encrypts to K4 CT")

# Create canonical space map
canonical_cuts = [
    1, 4, 7, 10, 14, 16, 20, 24, 33, 35, 38, 41, 
    47, 51, 55, 59, 62, 68, 73, 79, 81, 83, 88, 90, 93, 96
]

space_map = {
    "cuts": canonical_cuts,
    "type": "canonical",
    "window": [0, 96],
    "description": "0-indexed inclusive end positions for word boundaries"
}

output_dir = Path("runs/confirm/BLINDED_CH00_I003")
space_map_file = output_dir / "space_map.json"
with open(space_map_file, 'w') as f:
    json.dump(space_map, f, indent=2)

print(f"✅ Space map saved to {space_map_file}")

# Create readable version
readable_parts = []
prev = 0
for cut in canonical_cuts:
    readable_parts.append(plaintext[prev:cut+1])
    prev = cut + 1

readable_text = ' '.join(readable_parts)

readable_file = output_dir / "readable_canonical.txt"
with open(readable_file, 'w') as f:
    f.write(readable_text)

print(f"✅ Readable version saved to {readable_file}")
print(f"\nReadable text:")
print(readable_text)

# Update proof and coverage with new PT SHA
import hashlib
pt_sha = hashlib.sha256(plaintext.encode()).hexdigest()
print(f"\nUpdated PT SHA-256: {pt_sha}")

# Update proof digest
with open(output_dir / "proof_digest.json") as f:
    proof = json.load(f)
proof['pt_sha256'] = pt_sha
with open(output_dir / "proof_digest.json", 'w') as f:
    json.dump(proof, f, indent=2)

# Update coverage report
with open(output_dir / "coverage_report.json") as f:
    coverage = json.load(f)
coverage['pt_sha256'] = pt_sha
with open(output_dir / "coverage_report.json", 'w') as f:
    json.dump(coverage, f, indent=2)

print("✅ Updated proof and coverage with new PT SHA")