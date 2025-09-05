# Policy Pre-Registration Document

**Date**: 2025-09-05  
**Version**: 1.0  
**Status**: LOCKED (Do not modify after registration)

## Executive Summary

This document pre-registers all analysis policies and decision criteria before examining any K4 solution candidates. By declaring our methods in advance, we prevent post-hoc adjustments and ensure analytical integrity.

## Core Decision Framework

### 1. Phrase Gate Configuration

**Surveying Semantics (Flint v2)**
- Model: Claude Opus 3.0
- Prompt: Fixed imperative detection
- Binary output: Pass/Fail

**Generic Quality Assessment**
- Model: GPT-4 (July 2024)
- Perplexity threshold: Top 0.5% (99.5 percentile)
- Part-of-speech threshold: ≥0.60
- Gate logic: AND (both must pass)

### 2. Tokenization Policy

**Version 2.0 (Decision)**
- Canonical cuts only
- No inferred word boundaries
- Applied to head window [0, 74]

**Version 2.1 (Report-only)**
- Boundary-aware at position 74
- Splits "THEJOY" if spanning boundary
- Used for tie-break reporting only

### 3. Null Hypothesis Testing

**Bootstrap Configuration**
- Samples: 10,000 mirrored nulls
- Window: 2000 characters
- Skip: 1000 characters

**Multiple Testing Correction**
- Method: Holm-Bonferroni
- Tests: m=2 (coverage, function words)
- Alpha: 0.01
- Decision: Both adjusted p-values must be <0.01

### 4. Evaluation Window

**Seam-Free Head**
- Start: Position 0
- End: Position 74 (inclusive)
- Total: 75 characters
- Tail: Positions 75-96 (not evaluated)

## Registered Analyses

### A. Sensitivity Strip (3x3 Matrix)

Test robustness across threshold variations:

| POS \ Perplexity | 99.5% | 99.0% | 98.5% |
|------------------|-------|-------|-------|
| 0.40 (looser)    | Test  | Test  | Test  |
| 0.60 (baseline)  | Test  | Test  | Test  |
| 0.80 (stricter)  | Test  | Test  | Test  |

**Expected**: Baseline (0.60, 99.5%) admits winner; stricter thresholds may eliminate.

### B. P[74] Strip Analysis

Test all 26 letters at position 74:
- Context: ...HIAP[74]THEJOY...
- Expected: Only 'K' yields publishable result
- Purpose: Confirm cryptographic forcing vs editorial choice

### C. GRID Control Heads

Test invalid imperatives:
1. "LAYER TWO IS A MAP..." 
2. "LAYER TWO IS TRUE..."
3. "LAYER TWO IS A FACT..."

**Expected**: All controls fail (no valid GRID output)

### D. Alternates Within Frame

Search for surveying-equivalent imperatives:
- Routes: GRID only (W14 ROWS)
- Frame: Flint v2 + Generic AND
- Expected: No alternates found

### E. Adjacent Frames

Test frame variations:
1. OR gate logic
2. Full deck routes
3. Stricter POS (0.80)

**Expected**: Different admission patterns, but none publishable

## Quality Assurance

### Reproducibility Requirements
- Seed: 1337 (all random operations)
- Hashes: SHA-256 for all outputs
- Manifests: Complete file listings
- Scripts: Deterministic execution

### Report Classifications
- **Decision**: Affects publishability determination
- **Report-only**: Additional analysis, no impact on results
- **Control**: Validates method selectivity

## Statistical Power

### Coverage Metric
- Bootstrap windows: 2000 per reference text
- Minimum detectable effect: ~0.5 SD
- Power: >0.90 for true differences

### Function Words
- Dictionary: 150 common English words
- Rhythm metrics: Mean gap, CV
- Power: >0.85 for systematic differences

## Locked Parameters

The following MUST NOT change during analysis:

1. **Seed**: 1337
2. **Head window**: [0, 74]
3. **Gate logic**: AND
4. **Alpha**: 0.01
5. **Correction**: Holm m=2
6. **Bootstrap N**: 10,000
7. **Tokenization**: v2 (decision)

## Version Control

| Date | Version | Changes | Hash |
|------|---------|---------|------|
| 2025-09-05 | 1.0 | Initial registration | [pending] |

## Certification

This document represents our complete analytical framework, registered before examining candidates. Any deviation from these policies must be clearly marked as "POST-HOC" and cannot affect publishability decisions.

**Registered by**: K4 Analysis Team  
**Date**: 2025-09-05  
**Time**: [UTC timestamp]

---

*This is a pre-registration document. Once locked, modifications invalidate the registration.*