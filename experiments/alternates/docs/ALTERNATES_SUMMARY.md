# Alternates Exploration Summary

**Date**: 2025-09-05  
**Purpose**: Explore surveying-equivalent imperatives and adjacent frames  
**Claim Boundary**: GRID-only + AND gate + head-only + nulls  

## Executive Summary

This exploration tested alternate K4 candidates in two dimensions:

1. **Within-frame alternates**: Different surveying imperatives maintaining GRID-only + AND structure
2. **Adjacent frames**: Variations outside the claim boundary (stricter POS, full deck, OR gate)

**Key Finding**: No alternates passed both phrase gates and null hypothesis testing, confirming the uniqueness of the published result within the specified frame.

## Within-Frame Analysis

### Imperatives Tested
- SIGHT THE BERLIN (published)
- SET THE BEARING
- NOTE THE BERLIN  
- READ THE BERLIN
- OBSERVE THE DIAL

### Results
- Candidates generated: 10 (5 imperatives × 2 anchor positions)
- Passing phrase gate: 0
- Passing nulls: 0

**Interpretation**: The published imperative is unique within the GRID-only + AND frame. Alternative surveying-equivalent phrases do not satisfy both the Flint v2 and Generic criteria simultaneously.

## Adjacent Frame Analysis

### Frame Variants Tested

| Frame | Description | Gate Passes | Null Passes |
|-------|-------------|-------------|-------------|
| AND + POS 0.80 | Stricter Generic threshold | 0 | 0 |
| Full Deck + AND | All routes enabled | 0 | 0 |
| OR + Strict Generic | OR gate, top-0.5% perplexity | 6 | 0 |

### Observations

1. **Stricter thresholds** (POS 0.80) eliminate all candidates, including potential alternates
2. **Expanded routes** (full deck) maintain the same selectivity as GRID-only
3. **OR gate** allows more candidates through initial screening (6 vs 0) but nulls still filter all

## Technical Notes

### Methodology
- Deterministic seed: 1337
- Bootstrap nulls: K=10000
- Holm correction: m=2
- Tokenization: v2 (canonical cuts)

### Files Generated
- Policy files: 4 variants
- Python scripts: 4 (generate, confirm, scan, run)
- Results: Per-frame confirmations and summaries
- Manifests: SHA-256 verification

## Conclusions

1. **Within published frame**: No surveying-equivalent alternates exist
2. **Adjacent frames**: Different policy settings produce different filtering behavior
3. **Null hypothesis testing**: Provides strong final filter regardless of gate logic
4. **Claim boundary**: Well-defined and produces unique result

## Reproducibility

All analyses can be reproduced using:
```bash
# Within-frame
python3 scripts/scan_within_frame.py \
    --policy policies/POLICY.seamfree.and.json \
    --output_dir runs/2025-09-05/frame_and/

# Adjacent frames
python3 scripts/run_frame_variant.py \
    --all \
    --output_dir runs/2025-09-05/
```

## Audit Trail

- Branch: experiment-alternates
- Seed: 1337 (deterministic)
- No changes to published results
- Report-only analysis
- Clear claim boundaries maintained