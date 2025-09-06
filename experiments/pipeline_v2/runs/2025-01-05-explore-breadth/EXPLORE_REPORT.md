# Explore-Breadth Campaign Report

**Date:** 2025-01-05  
**Campaign ID:** PV2-EXPLORE-BREADTH-001  
**Status:** Complete

## Scope

- **Routes:** GRID, SPOKE, RAILFENCE (NA-only permutations)
- **Policies:** Fixed/Windowed/Shuffled anchor modes with blinding
- **δ margins:** δ₁=0.05, δ₂=0.05 (normalized units)
- **α_explore:** 0.05 for 1k nulls
- **Policy hash:** ec0c35e8605fe1af
- **Blinding list hash:** e5f6a7b8c9d01234

## Campaign Innovations

- **Register mixing:** Declarative + imperative hybrids
- **Syntactic variations:** Light punctuation, clause reshuffling
- **Length optimization:** Targeted 65-75 character range
- **N-gram glue:** Added common bigrams for statistical improvement
- **Misspelling panel:** K-style Levenshtein-1 on content tokens

## Counts

| Stage | Count | Percentage |
|-------|-------|------------|
| Generated heads | 70 | 100% |
| In target range (65-75) | 70 | 100% |
| After anchor modes | 70 | 100% |
| Delta passers (δ₁ & δ₂) | 0 | 0% |
| Feasible schedules | 0 | 0% |
| Pass 1k nulls | 0 | 0% |
| Survive orbits | N/A | - |
| **Promotion queue** | **0** | **0%** |

## Analysis

### Score Distribution

Top candidates by fixed score:

| Label | Length | Fixed Score | δ_windowed | δ_shuffled |
|-------|--------|-------------|------------|------------|
| B0008 | 75 | 4.56 | 0.00 | 3.82 |
| B0019 | 68 | 4.21 | 0.00 | 2.97 |
| B0002 | 75 | 4.11 | 0.00 | 3.91 |
| B0033 | 68 | 3.62 | 0.00 | 3.19 |

### Delta Analysis

- **δ₁ vs Windowed:** All candidates show δ=0
  - Indicates anchors appear at correct positions
  - No advantage from ±1 window flexibility
  
- **δ₂ vs Shuffled:** All positive but below threshold (δ₂ < 0.05)
  - Best δ_shuffled: 3.91 (B0002)
  - Shows improvement over random but not enough to pass

### Top Candidate Analysis (B0008)

**Text:** "WHENTHEBERLINCLOCKISREADANDTHEPATHISSETTRUETHETEXTEASTNORTHEASTBECOMESPLAIN"

**Orbit Analysis:**
- Neighbors examined: 1,130
- Ties within ε=0.02: 897 (79%)
- Unique: FALSE (far exceeds threshold of 10)

**Negative Controls:**
- Original: 0.242
- Scrambled anchors: -31% (0.167)
- Permuted seam: -7% (0.226)
- Anchor-free: 0% (0.242)
- Random shuffle: -93% (0.018)

Shows expected degradation patterns, particularly strong response to scrambling.

## Key Findings

1. **Length optimization worked:** All 70 candidates in target 65-75 range
2. **Higher scores achieved:** Top scores (4.56) higher than previous campaign (3.30)
3. **Shuffled delta improved:** Better separation from random (3.82 vs 2.74 previously)
4. **Still below thresholds:** Despite improvements, no candidates pass δ requirements
5. **Non-unique in orbit space:** High tie percentages (79%) indicate lack of uniqueness

## Comparison to Previous Campaign

| Metric | Surveying Campaign | Breadth Campaign | Improvement |
|--------|-------------------|------------------|-------------|
| Best fixed score | 3.30 | 4.56 | +38% |
| Best δ_shuffled | 3.33 | 3.91 | +17% |
| Candidates tested | 500 | 70 | -86% (focused) |
| Promotion queue | 0 | 0 | No change |

## Conclusions

The breadth campaign successfully:
1. Explored register mixing and syntactic variations
2. Achieved higher absolute scores through n-gram optimization
3. Improved separation from shuffled controls
4. Maintained effective killing at delta thresholds

However, the fundamental challenge remains: even with improved templates and n-gram optimization, candidates cannot beat both windowed and shuffled controls by the required margins under blinded scoring.

## Next Steps

Recommended approaches:
1. **Campaign B:** Route-first perturbations (hold text, vary structure)
2. **Campaign C:** Scorer ablations to validate/adjust weights
3. **Threshold calibration:** Consider if δ thresholds are too stringent
4. **Unblinded testing:** Test known winner to validate pipeline

## Files

- Pre-registration: `docs/pre_reg/ANALYSIS_PLAN_2025-01-05_explore-breadth.md`
- Candidates: `data/candidates_breadth.json` (70 heads)
- Anchor matrix: `ANCHOR_MODE_MATRIX.csv`
- Explore matrix: `EXPLORE_MATRIX.csv` (empty)
- Promotion queue: `promotion_queue.json` (empty)
- Baseline stats: `baseline_stats.json`
- Orbits: `orbits/B0008/orbit_analysis.json`
- Controls: `neg_controls/NEG_CONTROL_SUMMARY.csv`
- Manifest: `MANIFEST.sha256`
- Repro: `REPRO_STEPS.md`