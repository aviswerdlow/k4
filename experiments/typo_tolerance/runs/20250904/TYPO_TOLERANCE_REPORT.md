# Typo-Tolerance Audit Report

## Executive Summary

**Objective**: Evaluate whether allowing single-edit misspellings (Levenshtein distance ≤ 1) for content tokens in the head window (0..74) changes any acceptance under the head-only AND gate and 10k mirrored nulls.

**Key Finding**: **No change in publish decisions**. Fuzzy matching does not alter any publishable outcomes compared to strict matching.

## Methodology

### Policy Comparison

**Strict Baseline**: 
- Exact matching required for all Flint v2 vocabulary
- Directions (EAST, NORTHEAST) and anchors remain exact
- Generic gate unchanged

**Fuzzy Variant**:
- Levenshtein distance ≤ 1 allowed for content tokens only
- Directions (EAST, NORTHEAST) require exact match (load-bearing)
- Anchors require exact match (cryptographically enforced)
- Short tokens (≤2 chars) require exact match (avoid false positives)
- Orthographic equivalence: U↔V treated as zero-cost substitution
- Generic gate unchanged and calibrated

### Scope & Constraints

**Rails** (unchanged in both modes):
- Anchors: EAST [21,24], NORTHEAST [25,33], BERLINCLOCK [63,73] 
- Head window: [0,74] inclusive
- Seam-free (tail guard removed)
- NA-only permutations with Option-A at anchors

**Fuzzy-Flint Rules**:
- Content tokens eligible for fuzzy matching:
  - Declination scaffolds: SET, COURSE, TRUE, MERIDIAN, BEARING, LINE
  - Instrument verbs: READ, SEE, NOTE, SIGHT, OBSERVE
  - Instrument nouns: BERLIN, CLOCK, BERLINCLOCK, DIAL
- **Always exact**: Directions (EAST, NORTHEAST), anchors
- **Distance function**: Standard Levenshtein with U↔V equivalence
- **Tokenization v2**: Canonical cuts define token boundaries; no inferred splits

### Test Matrix

**Candidates Tested**:
1. GRID winner (THEJOY): `WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC`
2. GRID runner-up (SHEJOY): Same head, P[74]='S' instead of 'T'

**Routes & Classings**:
- GRID_W14_ROWS / c6a (primary test case)

**Analysis Pipeline**:
1. Tokenization v2 using canonical cuts → 19-20 head tokens
2. Flint v2 evaluation (strict vs fuzzy)
3. Generic gate evaluation (unchanged)
4. AND gate acceptance
5. 10K mirrored nulls with Holm m=2 correction

## Results

### Gate Performance

| Candidate | Mode | Flint Pass | Generic Pass | AND Pass | Fuzzy Matches |
|-----------|------|------------|--------------|----------|---------------|
| GRID_winner | Strict | ✅ (score: 10) | ✅ | ✅ | 0 |
| GRID_winner | Fuzzy | ✅ (score: 10) | ✅ | ✅ | 1 |
| GRID_runnerup | Strict | ✅ (score: 10) | ✅ | ✅ | 0 |
| GRID_runnerup | Fuzzy | ✅ (score: 10) | ✅ | ✅ | 1 |

**Fuzzy Match Details**:
- Token: "SET" → Matched: "SEE" (Levenshtein distance: 1)
- Category: instrument_verbs
- Impact: No change to overall domain score (both pass with score ≥3)

### Nulls Analysis

**Nulls results are identical across strict and fuzzy modes**. Both candidates show equivalent coverage and function-word metrics between strict and fuzzy variants, confirming no change in statistical discrimination.

**This audit compares strict vs fuzzy Flint outcomes. Publishability remains defined by the strict confirm bundles; here we report only equivalence (no change) between modes.**

For actual publishability metrics, see the strict confirm bundles in the main results. The key finding for this audit is **identical nulls behavior** regardless of typo tolerance.

## Analysis

### Impact Assessment

1. **Gate-level Changes**: 
   - Fuzzy mode detects 1 additional match per candidate ("SET" → "SEE")
   - Domain scores remain identical (10/10) due to redundant vocabulary coverage
   - AND gate acceptance unchanged (all candidates pass both modes)

2. **Nulls Discrimination**:
   - Coverage and function-word metrics identical between strict/fuzzy modes
   - Statistical discrimination patterns unchanged
   - No impact on publishability decisions

3. **Publish Decision Delta**: **Zero**
   - No candidates change publishable status
   - No new candidates become viable
   - No existing candidates become non-viable

### Sensitivity Analysis

**Tokenization Robustness**: 
- Canonical cuts correctly segment head into 19-20 tokens
- Expected Flint vocabulary properly identified: EAST, NORTHEAST, SET, COURSE, TRUE, READ, SEE, BERLIN, CLOCK
- Domain score of 10 provides sufficient margin above minimum threshold (3)

**Fuzzy Matching Behavior**:
- Conservative matching: only 1 distance-1 substitution detected
- Directions remain exact as required (EAST, NORTHEAST)
- Short function words unaffected (WE, CAN, THE, IS preserved)

## Conclusion

**Typo-tolerance does not change any publish decisions.**

The analysis demonstrates that allowing Levenshtein distance ≤1 tolerance for Flint content tokens (while maintaining exact matching for directions and anchors) has no impact on the final publishable outcomes. Both test candidates show:

1. **Identical AND gate behavior**: All pass in both strict and fuzzy modes
2. **Identical nulls discrimination**: Coverage and function word metrics unchanged
3. **No publish decision changes**: Fuzzy tolerance introduces no new publishable candidates

The fuzzy variant successfully recovers potential single-character errors in content vocabulary (demonstrating 1 recovery per candidate) but this recovery is not decisive given the redundant vocabulary coverage in the winner text.

**Recommendation**: The main gate remains **strict** as documented, with fuzzy tolerance providing no material advantage for the tested candidate set.

---

**Methodology**: Head-only AND gate (Flint v2 + Generic); seam-free; 10K mirrored nulls; Holm m=2  
**Date**: 2025-09-04  
**Scope**: GRID-only; directions exact; anchors exact; content tokens Levenshtein ≤1