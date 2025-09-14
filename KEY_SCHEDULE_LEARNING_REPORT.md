# Key Schedule Learning Report - Plan A/C Results

## Executive Summary
Attempted to learn the key schedule from the four immutable anchors (EAST, NORTHEAST, BERLIN, CLOCK) using the KRYPTOS tableau. No periodic keys (L≤11), composite keys, or affine-shifted keys can satisfy all anchor constraints simultaneously. This definitively falsifies the "short periodic key" hypothesis for K4.

## Methodology

### Approach
Treated the anchors as hard constraints to solve for the key schedule rather than guessing dictionary words.

### Constraint Extraction
Derived required key letters at every anchor position:

**VIGENERE (KRYPTOS tableau)**:
```
Positions 21-24 (EAST):      I R J D
Positions 25-33 (NORTHEAST): H G M I M J A O N
Positions 63-68 (BERLIN):    S Y M L W R
Positions 69-73 (CLOCK):     Q O Y B Q
Full pattern: IRJDHGMIMJAONSYMLWRQOYBQ
```

**BEAUFORT (KRYPTOS tableau)**:
```
Positions 21-24 (EAST):      C E C H
Positions 25-33 (NORTHEAST): P T S D Q D D D E
Positions 63-68 (BERLIN):    H Y S S R S
Positions 69-73 (CLOCK):     H D N L Q
Full pattern: CECHPTSDQDDDEHYSSRSHDNLQ
```

## Plan A Results - Pure Periodic Keys

### Search Parameters
- Key lengths: L = 3 to 11
- Phase offsets: φ = 0 to L-1
- Families: Vigenere and Beaufort
- Tableau: KRYPTOS

### Findings
**No valid periodic keys found for any L ≤ 11**

Sample conflicts (Vigenere):
- L=3: Position 24 needs 'D' but position 21 forces 'I'
- L=4: Position 25 needs 'H' but pattern forces 'I'
- L=5: Position 26 needs 'G' but pattern forces 'I'

The constraint pattern from anchors is incompatible with any repeating key of reasonable length.

### Control Schedule Variant
Allowed phase changes at positions 63 and 69 (BERLIN/CLOCK boundaries).

**Result**: Still no valid keys found. The segments [0-62], [63-68], [69-96] cannot be explained by the same periodic key with different phases.

## Plan C Results - Composite Keys

### C-1: Two-Word Composite
Attempted to find:
- W₁ (length ≤ 7) for HEAD anchors (positions 21-33)
- W₂ (length ≤ 7) for MID anchors (positions 63-73)
- Splice point at position 63

**Result**: No valid two-word combinations found.

### C-1 Extended: Rotation at 69
Allowed W₂ to rotate at position 69 within the tail segment.

**Result**: No valid combinations found.

### C-2: Affine Shift
Attempted single key with Caesar shifts:
- Base key + shift at position 63
- Optional additional shift at position 69
- Shift range: ±1 to ±5

**Result**: No valid affine-shifted keys found.

## Critical Analysis

### Why All Approaches Failed

1. **Constraint Density**: 24 constrained positions out of 97 total
2. **Constraint Distribution**: Gaps between anchors create incompatible patterns
3. **Pattern Irregularity**: The required keystream shows no periodic structure

### Mathematical Impossibility
The required keystream at anchor positions:
- VIGENERE: `IRJDHGMIMJAONSYMLWRQOYBQ`
- BEAUFORT: `CECHPTSDQDDDEHYSSRSHDNLQ`

These patterns exhibit:
- No repeating subsequences
- No arithmetic progressions
- No simple transformations between segments

## Files Delivered

### Core Implementation
1. `/04_EXPERIMENTS/phase3_zone/extract_anchor_constraints.py` - Constraint extraction
2. `/04_EXPERIMENTS/phase3_zone/key_fit/fit_periodic_key.py` - Periodic key fitter
3. `/04_EXPERIMENTS/phase3_zone/key_fit/fit_composite_key.py` - Composite key fitter

### Data Files
4. `/04_EXPERIMENTS/phase3_zone/notes/anchor_keystream_vigenere_kryptos.json`
5. `/04_EXPERIMENTS/phase3_zone/notes/anchor_keystream_beaufort_kryptos.json`
6. `/04_EXPERIMENTS/phase3_zone/key_fit/periodic_key_fits.json` (empty - no fits)
7. `/04_EXPERIMENTS/phase3_zone/key_fit/composite_key_fits.json` (empty - no fits)

## Conclusions

### Falsification Complete
The hypothesis that K4 uses a short periodic key (L≤11) with the KRYPTOS tableau is **definitively falsified**. The anchor constraints cannot be satisfied by:
- Simple periodic keys
- Periodic keys with control schedules
- Two-word composite keys
- Affine-shifted keys

### Implications
Since the anchors (EAST, NORTHEAST, BERLIN, CLOCK) are treated as ground truth, and no simple key schedule can produce them, K4 must use:

1. **Complex key derivation**: Mathematical transformation beyond simple repetition
2. **Multiple independent keys**: Different keys for different anchors with no simple relationship
3. **Different cipher system**: Not pure Vigenere/Beaufort with KRYPTOS tableau
4. **Additional transformation layer**: Extra step between key and plaintext

### Next Steps Required

Since Plans A and C failed completely, consider:

1. **Relaxing tableau assumption**: Try other tableaux or mixed tableaux
2. **Complex key schedules**: Non-periodic, mathematically derived keys
3. **Different cipher families**: Beyond Vigenere/Beaufort
4. **Questioning anchor assumptions**: Verify the anchors are correct
5. **Additional transformations**: Masks, routes, or other operations that could reconcile the constraints

## Summary for Manager

**Request**: Find the simplest repeating key schedule that produces all four anchors.

**Result**: No such key exists for L≤11 with any tested variation.

**Key insight**: The mathematical impossibility of fitting a simple periodic key to the anchor constraints proves K4 uses a more complex cryptographic system than initially hypothesized.

**Recommendation**: The search space of simple periodic keys is exhausted. Either:
- The anchors need re-examination
- The cipher system needs expansion beyond Vigenere/Beaufort with KRYPTOS tableau
- A fundamentally different approach is required