# Fork S - Surveying Cipher Parameters

Position-preserving cryptography driven by plaza/survey geometry parameters.

## Overview

Fork S tests whether surveying-derived quantities (bearings, DMS triples, rectangular components, distances, declinations) provide cipher parameters that can:

1. **Preserve all four anchors** exactly at their known indices
   - EAST at positions 21-24
   - NORTHEAST at positions 25-33  
   - BERLIN at positions 63-68
   - CLOCK at positions 69-73

2. **Produce plausible head text** (positions 0-20) without nonsense consonant walls

3. **Use position-preserving transforms** (or transforms with explicit inversion)

## Quick Start

```bash
# Run complete test suite
make survey-params-all

# Or run specific test batteries
make survey-bearings    # Pure bearing parameters
make survey-transpose   # Transposition with distances
make survey-hybrid      # Two-stage pipelines
```

## Architecture

### Parameter Extraction (`lib/survey_params.py`)

Converts surveying quantities to cipher parameters:

- **Bearings**: 61.6959° (NE+), 50.8041° (ENE-), etc.
- **DMS**: (16, 41, 45), (61, 41, 45), (50, 48, 15)
- **Rectangular**: ΔN=11.923m, ΔE=22.140m for 5 rods NE
- **Declinations**: Langley 1990 ~9.5°W, Berlin 1989 ~2°E
- **Arc Transforms**: Arc length, chord, sector from angles

### Cipher Families (`lib/cipher_families.py`)

#### Position-Preserving (no inversion needed)
- **Polyalphabetic**: Vigenère, Beaufort, Variant Beaufort
- **Substitution**: Caesar, Affine, Periodic Affine
- **Segmented**: Different parameters for head/anchors/tail

#### Position-Changing (requires inversion)
- **Transposition**: Columnar, Rail Fence, Route (spiral/snake/diagonal)
- **Matrix**: Hill 2×2/3×3, Playfair, Four-square
- **Fractionation**: ADFGX/ADFGVX, Polybius

#### Hybrid Pipelines
Two-stage chains with position restoration:
```python
Stage 1: Position-changing (columnar, route, etc.)
Stage 2: Position-preserving (polyalphabetic, affine)
Invert Stage 1 permutation before evaluation
```

### Validation (`lib/validation.py`)

- **Hard Constraints**: Exact anchor matching (case-sensitive)
- **Text Analysis**: Vowel ratio, consonant runs, dictionary words
- **Survey Terms**: Search for MERIDIAN, BEARING, ANGLE, etc.
- **Negative Controls**: Scrambled anchors, random parameters

## Test Batteries

### Set A - Pure Bearings (Polyalphabetic)
- L = 61, 50, 17 from bearing integer/round/offset
- Phase from DMS minutes (41, 48)
- Offset from DMS seconds mod 26

### Set B - Quadrant/Angles
- Quadrant number as wheel count
- Reference angle as L
- Complement/supplement as parameters

### Set C - Magnetic Corrections
- Pre/post Caesar with declination shifts
- True vs magnetic bearing adjustments

### Set D - Distance/Rectangular
- L from meters (25), rods (5), feet (82)
- Columns from distance/coordinates
- Key order from DMS sequences

### Set E - Arc/Chord/Sector
- Arc length mapped to L
- Chord × 100 mod 26 as offset
- Sector fraction as family selector

### Hybrid - Two-Stage Pipelines
- Stage 1: Transposition/matrix (position-changing)
- Stage 2: Polyalphabetic/affine (position-preserving)
- Explicit inversion to restore positions

## Output Format

### Result Cards (JSON)
```json
{
  "id": "A-true_ne_plus-L61-vigenere",
  "family": "vigenere",
  "stages": [...],
  "parameter_source": {
    "bearing_deg": 61.6959,
    "dms": [61, 41, 45]
  },
  "results": {
    "anchors_preserved": false,
    "plaintext_head_0_20": "...",
    "survey_terms_found": ["MERIDIAN"]
  },
  "repro": {
    "seed": 1337,
    "ct_sha256": "..."
  }
}
```

### Summary Files
- `RUN_SUMMARY.csv`: All tests with key metrics
- `METHODS_MANIFEST.json`: Constants and provenance
- `FINAL_REPORT.md`: Human-readable summary

## Key Parameters

### Reference Bearings (degrees from TRUE)
- `true_ne_plus`: 61.6959°
- `true_ene_minus`: 50.8041°
- `mag_ne_plus_1989_B`: 59.5959°
- `mag_ene_minus_1989_B`: 48.7041°
- `offset_only`: 16.6959°

### DMS Exemplars
- (16, 41, 45) - Offset/correction
- (61, 41, 45) - NE+ bearing
- (50, 48, 15) - ENE- bearing

### Units
- 1 rod = 16.5 feet = 5.0292 meters
- 5 rods ≈ 82.5 feet ≈ 25.146 meters

## Determinism

- **MASTER_SEED**: 1337 (fixed for reproducibility)
- **No randomness**: All transformations are deterministic
- **Explicit logging**: Every parameter mapping is recorded

## Acceptance Criteria

A configuration is considered a **candidate** if:
1. All anchors preserved exactly
2. Head has max_consonant_run ≤ 4
3. At least one survey term appears

Ranking: anchors → min consonant run → survey terms → shorter L

## Negative Controls

1. **Scrambled anchors**: Re-run with scrambled anchor positions
2. **Random parameters**: Test with random L, phase, offset
3. **Success rate**: Should be ~0 for valid tests

## CI Integration

```yaml
validate-survey-params:
  - Lint parameter extraction
  - Unit test cipher families
  - Smoke test: 3 configs
  - Verify anchor checks execute
  - Confirm JSON/CSV output
```

## Troubleshooting

### No matches found?
This is valuable! Clean negatives rule out surveying parameters as the cipher key source.

### Position mismatch?
Ensure Stage 1 transpositions are properly inverted before anchor checking.

### Invalid parameters?
- L must be in [2, 97]
- Affine 'a' must be coprime to 26
- Hill matrices must be invertible mod 26

## Forum Bundle

```bash
make package
# Creates FORK_S_forum_bundle.zip with:
# - All result JSONs
# - RUN_SUMMARY.csv
# - METHODS_MANIFEST.json
# - FINAL_REPORT.md
# - This README
```

## Contact

Part of the Kryptos K4 CLI Plus framework.
Master seed: 1337 for all operations.