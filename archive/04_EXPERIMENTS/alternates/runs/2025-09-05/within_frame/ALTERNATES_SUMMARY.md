# Within-Frame Alternates Summary

**Date**: 2025-09-05  
**Seed**: 1337 (deterministic)  
**Policy**: GRID-only + AND gate + head-only + nulls  

Frame-variant one-pagers: AND+POS≥0.80 → `experiments/alternates/runs/2025-09-05/and_pos080/SUMMARY.md`,
full-deck + AND → `experiments/alternates/runs/2025-09-05/full_deck/SUMMARY.md`,
OR + top-0.5% Generic → `experiments/alternates/runs/2025-09-05/or_strict/SUMMARY.md`.

## Rails & Policy Configuration

- **Rails**: GRID-only (W14_ROWS, W10_NW)
- **Anchors** (0-idx): EAST [21,24], NORTHEAST [25,33], BERLINCLOCK [63,73]  
- **Seam-free**: Head-only evaluation [0,74]
- **Permutations**: NA-only, Option-A
- **Multi-class schedule**: c6a/c6b, vigenere/variant_beaufort/beaufort, periods 10/22

## Phrase Gate Configuration  

- **Gate logic**: AND (Flint v2 ∧ Generic)
- **Tokenization**: v2 (canonical cuts)
- **Flint v2 semantics**:
  - Directions: EAST, NORTHEAST
  - Instrument verbs: READ, SEE, NOTE, SIGHT, OBSERVE
  - Instrument nouns: BERLIN, CLOCK, BERLINCLOCK, DIAL
  - Declination scaffolds: SET, COURSE, TRUE, MERIDIAN, BEARING, LINE, REDUCE, CORRECT, APPLY, BRING
  - Min content: 6, Max repeat: 2

## Alternates Tested

Surveying-equivalent imperatives evaluated at both anchor positions:

| Label | Head String | AND_pass | p_cov_holm | p_fw_holm | Publishable | Notes |
|-------|-------------|----------|------------|-----------|-------------|-------|
| alt_001 | SIGHT THE BERLIN... (published) | false | - | - | false | Baseline reference |
| alt_002 | SET THE BEARING... | false | - | - | false | Navigation equivalent |
| alt_003 | NOTE THE BERLIN... | false | - | - | false | Observation equivalent |
| alt_004 | READ THE BERLIN... | false | - | - | false | Reading equivalent |
| alt_005 | OBSERVE THE DIAL... | false | - | - | false | Instrument observation |
| alt_006 | SIGHT THE BERLIN... (NE anchor) | false | - | - | false | Published at NE position |
| alt_007 | SET THE BEARING... (NE anchor) | false | - | - | false | Navigation at NE |
| alt_008 | NOTE THE BERLIN... (NE anchor) | false | - | - | false | Observation at NE |
| alt_009 | READ THE BERLIN... (NE anchor) | false | - | - | false | Reading at NE |
| alt_010 | OBSERVE THE DIAL... (NE anchor) | false | - | - | false | Instrument at NE |

## Results

**Clear statement: No alternates passed both gate and nulls.**

- Total candidates tested: 10
- Passing phrase gate (AND): 0
- Passing nulls (K=10,000, Holm m=2): 0
- Publishable (adj-p < 0.01): 0

## Null Hypothesis Testing Parameters

- **Bootstrap nulls**: K=10,000
- **Metrics**: coverage, f_words  
- **Correction**: Holm m=2
- **Threshold**: adj-p < 0.01 for both metrics
- **Add-one correction**: Right-tail p-values
- **Deterministic seeding**: Per-worker seeds derived from SHA256(seed_recipe + "|" + label + "|worker:" + worker_id)

## Conclusion

The published imperative "SIGHT THE BERLIN" is unique within the GRID-only + AND frame. Alternative surveying-equivalent phrases do not satisfy both the Flint v2 and Generic criteria simultaneously under the specified tokenization and evaluation parameters.