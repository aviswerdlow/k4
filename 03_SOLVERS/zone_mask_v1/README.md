# Zone Mask v1 Solver

## Overview
Zone-based solver for K4 cryptanalysis using masks, routes, and classical ciphers.

## Architecture
- **Zones**: HEAD (0-20), MID (34-62), TAIL (74-96)
- **Control**: BERLINCLOCK at positions 64-73
- **Masks**: Periodic interleaves, cycles, diagonal weaves, etc.
- **Routes**: Columnar, serpentine, spiral, tumble
- **Ciphers**: Vigenere and Beaufort with short keys

## Usage
```bash
python scripts/zone_runner.py --manifest <manifest.json>
python scripts/verifier.py --manifest <manifest.json> --ct ../../02_DATA/ciphertext_97.txt
python scripts/notecard.py --manifest <manifest.json> --out notecard.md
```

## Manifest Format
See `recipes/recipe.schema.json` for full schema.

## Key Features
- Paper-doable operations only
- Deterministic round-trip validation
- Single-page notecard output
- Null control testing
- Antipodes mode support