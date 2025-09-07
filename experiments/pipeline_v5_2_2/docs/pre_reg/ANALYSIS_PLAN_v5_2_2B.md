# Analysis Plan v5.2.2-B: Boundary Hardening

**Version**: 5.2.2-B  
**Date**: 2025-01-07  
**Commit**: [TO BE FILLED AFTER COMMIT]  
**Status**: Pre-registered

## Executive Summary

v5.2.2-B implements boundary hardening with per-gap quotas and micro-repair to achieve ≥80% post-anchor pass rate while maintaining zero collisions.

## Rails and Gates (UNCHANGED)

### Fixed Anchor Positions (0-indexed, inclusive)
- **EAST**: [21, 24]
- **NORTHEAST**: [25, 33]  
- **BERLINCLOCK**: [63, 73] (single 11-char anchor, NOT split)

### Head Window
- **Canonical**: [0, 74] inclusive
- **Format**: Letters-only (A-Z), no spaces in canonical plaintext

### Explore Gates
- **Near-gate**: coverage ≥ 0.85, f_words ≥ 8, has_verb = true
- **Deltas**: Fixed + windowed (r ∈ {2,3,4})
- **Leakage**: 0.000 (Generic masked vs unmasked)
- **Context Gate**: Overall ≥ 4, semantic_specificity ≥ 3, no repetition penalty

### Phrase/Cadence Gates
- **Flint v2**: As defined in v5.2
- **Generic**: Perplexity and POS-trigram thresholds
- **Cadence**: FW gaps, cosine n-grams, word-length χ², V:C ratio

## New Boundary Policy

### Boundary Tokenizer Specification
1. **Hard Splits** (character index boundaries):
   - 20|21 (G1 → EAST)
   - 24|25 (EAST → NORTHEAST)
   - 33|34 (NORTHEAST → G2)
   - 62|63 (G2 → BERLINCLOCK)

2. **Token Classification**:
   - Anchor tokens: {"text": "EAST", "class": "anchor"}
   - Function words: {"text": "THE", "class": "function"}
   - Content words: {"text": "DIAL", "class": "content"}
   - Verbs: {"text": "READ", "class": "verb"}

3. **Scoring Rules**:
   - Exclude anchor-class tokens from function word counts
   - Exclude anchor-class tokens from cadence FW gaps
   - Include anchor-class tokens as content for perplexity/POS

### Per-Gap Quotas

#### Pre-Anchor Requirements
- **G1** [0, 20]: f_words ≥ 4
- **G2** [34, 62]: f_words ≥ 4
- **Total**: verbs ≥ 2, coverage ≥ 0.85

#### Post-Anchor Verification
- Re-check quotas using boundary tokenizer
- If any gap < quota, apply micro-repair
- Maximum 2 operations per gap

### Micro-Repair Policy

#### Allowed Operations (Gap-Only)
1. **Synonym Swaps** (length-preserving):
   - SIGN ↔ MARK (4 chars)
   - NOTE ↔ READ (4 chars)
   - DIAL ↔ GRID (4 chars)

2. **Function Word Upgrades** (same length):
   - Replace 3-letter content with THE/AND/FOR
   - Only if semantically valid

3. **Token Transposition** (within gap):
   - Reorder to meet quota
   - Preserve total length

#### Constraints
- Budget: ≤2 ops per gap (≤4 total)
- Never touch anchor spans
- Never cross hard splits
- Maintain verbs ≥ 2
- Preserve V...(THEN/AND)...V patterns

## Promotion Rules (UNCHANGED)

1. Pass near-gate (f_words ≥ 8, verbs ≥ 2, coverage ≥ 0.85)
2. Beat both deltas (fixed + windowed)
3. Orbit isolation
4. Fast nulls (1k samples)

## Pilot Success Criteria

- **Post-anchor pass rate**: ≥ 80%
- **Collisions**: 0
- **Leakage**: 0.000
- **Mean |ΔS_actual|**: Report only

## Artifacts

### Required Files
- `tokenization_report.json`: Token boundaries and classes
- `micro_repair_log.json`: Repair operations per head
- `EXPLORE_MATRIX.csv`: Full metrics including per-gap counts
- `DASHBOARD.csv`: Stage counts and histograms
- `promotion_queue.json`: Candidates meeting all criteria
- `MANIFEST.sha256`: Bundle integrity

### Optional Files
- `gap_quota_report.json`: Per-gap function word tracking
- `boundary_audit.json`: Verification of splits

## Quality Assurance

### Unit Tests
- `test_boundary_tokenizer.py`: Verify splits and anchor classification
- `test_neargate_quota.py`: Verify per-gap quotas maintained
- `test_micro_repair.py`: Verify length-neutral operations

### CI Checks
- Collisions = 0 (anchors untouched)
- Leakage = 0.000 (identical masked/unmasked deltas)
- Schema validation for all JSON outputs

## Seeds and Reproducibility

- **MASTER_SEED**: 1337
- **Per-head derivation**: SHA256(f"v5.2.2B_{label}_{MASTER_SEED}")
- **Random state**: Fully deterministic

---
**Pre-registered**: 2025-01-07  
**Principal**: v5.2.2-B Boundary Hardening  
**Predecessor**: v5.2.2 (52% post-anchor pass rate)