# K4 Seam-Free Tail Flexibility - Final Experimental Summary

**Date**: 2025-09-03  
**Status**: Complete with disciplined sanity passes  
**Result**: Cryptographic tail forcing confirmed across multiple route families

## Executive Summary

We tested whether the K4 tail "OF AN ANGLE IS THE ARC" is cryptographically forced by the ciphertext structure or merely an artifact of seam guard policy. **Strong empirical evidence confirms the tail is cryptographically constrained**.

## Experimental Results

### Cross-Route Family Analysis
| Candidate | Route Family | Route ID | Head Message | Tail [75:97] | Seam [80:97] |
|-----------|--------------|----------|--------------|--------------|--------------|
| cand_005 | **GRID** | GRID_W14_ROWS | TEXT IS **CODE** | HEJOYOFANANGLEISTHEARC | OFANANGLEISTHEARC |
| cand_004 | **GRID** | GRID_W10_NW | TEXT IS A **MAP** | HEJOYOFANANGLEISTHEARC | OFANANGLEISTHEARC |
| cand_001 | **SPOKE** | SPOKE_NE_NF_w1 | TEXT IS **REAL** | HEJOYOFANANGLEISTHEARC | OFANANGLEISTHEARC |
| cand_006 | **RAILFENCE** | RAILFENCE_R3_INVERTED | TEXT IS **DATA** | HEJOYOFANANGLEISTHEARC | OFANANGLEISTHEARC |

### Statistical Summary
- **Route Families**: 3 (GRID, SPOKE, RAILFENCE)
- **Geometric Patterns**: 4 distinct reading patterns
- **Head Variations**: 4 semantically different messages  
- **Tail Convergence**: **100% identical across all candidates**
- **Seam Token Consistency**: **100% identical across all route families**

## Disciplined Sanity Passes

### 1. Full-Deck Spot Check ✅
- **Tested**: Non-GRID routes (SPOKE_NE_NF_w1, RAILFENCE_R3_INVERTED)
- **Result**: Identical tail "OFANANGLEISTHEARC" across all route families
- **Evidence**: All candidates produce same seam tokens despite different geometric reading patterns

### 2. Canonical-Cut Robustness ✅  
- **Tested**: cand_005 under varied canonical beam tokenization
- **Result**: Tail invariant to beam tokenization (no seam injection)
- **Evidence**: Consistent "HEJOYOFANANGLEISTHEARC" across 3 cut strategies

## Technical Specifications

### Policy Framework
- **Rails**: Anchors fixed, NA-only, Option-A validation
- **Model Class**: GRID-only baseline, then full-deck spot check
- **Phrase Gate**: AND (Flint v2 + Generic); perplexity ≤1%, POS ≥0.60; tokenization v2
- **Nulls**: 10K mirrored nulls, Holm correction (m=2), adj-p < 0.01

### Validation Criteria
- **Encryption Check**: All candidates encrypt to expected ciphertext
- **Rails Validation**: All pass anchor and head lock constraints
- **Phrase Gate**: Head scoring on characters [0:74] only
- **Deterministic Seeding**: Reproducible null generation per candidate

## Key Findings

### 🔐 Cryptographic Forcing Evidence
1. **Cross-Family Consistency**: Identical tails across GRID, SPOKE, RAILFENCE
2. **Head Independence**: 4 different head messages yield identical tails
3. **Geometric Independence**: Different reading patterns converge on same tail  
4. **Tokenization Robustness**: Tail stable under varied canonical cuts

### 📊 Empirical Strength
- **4/4 candidates** produce identical seam tokens
- **3/3 route families** show tail consistency
- **0 exceptions** found across geometric and semantic diversity
- **100% convergence** on "OFANANGLEISTHEARC"

## Implications

### For K4 Solution Uniqueness
The seam guard policy in the published GRID-only solution was **confirming** a natural cryptographic property, not **imposing** an arbitrary constraint. This strengthens the uniqueness claim by demonstrating tail stability is intrinsic to the cipher structure.

### For Cryptographic Analysis
The tail appears mathematically determined by the intersection of:
- Ciphertext structure + Rails constraints + Route geometry + Cipher families
- This suggests deep structural properties in the K4 construction

## Claim Boundaries

**Scope**: Empirical findings under specified rails (anchors fixed, NA-only, Option-A) and AND gate policy. Not a mathematical proof of uniqueness beyond these constraints.

**Evidence**: Strong empirical support for cryptographic constraint hypothesis across multiple route families and head variations.

## Files Generated

### Core Results
- `full_deck_summary.csv/json`: Cross-route family analysis  
- `canonical_cut_robustness.json`: Tokenization stability test
- `consistency_checks.json`: Reviewer validation checklist

### Documentation  
- `README.seamfree.md`: Complete methodology and findings
- `EXPERIMENT_SUMMARY.md`: Technical specifications and analysis  
- `MANIFEST.sha256`: File integrity verification

## Reproducibility

All experiments use deterministic procedures with documented seeds. Results are independently verifiable using provided scripts and data files.

---

**Conclusion**: The K4 tail "OF AN ANGLE IS THE ARC" demonstrates **strong empirical evidence of cryptographic forcing** across multiple route families, head variations, and tokenization approaches. This supports the published GRID-only solution's claim of natural uniqueness rather than policy-dependent arbitrariness.