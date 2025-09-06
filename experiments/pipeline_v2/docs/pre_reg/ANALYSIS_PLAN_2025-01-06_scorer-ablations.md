# Pre-Registration: Campaign C (Scorer Ablations)

**Date:** 2025-01-06  
**Campaign ID:** PV2-EXPLORE-ABLATIONS-001  
**Branch:** `pipeline-v2-scorer-ablations`

## Hypothesis

H₀: Current scorer weights (ngram=0.4, coverage=0.3, compress=0.3) are optimal.  
H₁: Alternative weight configurations can improve delta margins and promotion rates.

## Methodology

### Test Corpus
- **Source:** Top 10 candidates from Explore-Breadth campaign
- **Rationale:** Best performers under current scoring

### Ablation Studies

#### 1. Component Ablations (Single-Component)
Test each component in isolation:
- **Ngram-only:** (1.0, 0.0, 0.0)
- **Coverage-only:** (0.0, 1.0, 0.0)
- **Compress-only:** (0.0, 0.0, 1.0)

#### 2. Pairwise Ablations
Test component pairs:
- **Ngram+Coverage:** (0.5, 0.5, 0.0)
- **Ngram+Compress:** (0.5, 0.0, 0.5)
- **Coverage+Compress:** (0.0, 0.5, 0.5)

#### 3. Weight Sweeps
Systematic grid search:
- Ngram: [0.2, 0.3, 0.4, 0.5, 0.6]
- Coverage: [0.2, 0.3, 0.4]
- Compress: [0.2, 0.3, 0.4]
- Constraint: weights sum to 1.0

#### 4. Extreme Configurations
- **Ngram-heavy:** (0.7, 0.15, 0.15)
- **Coverage-heavy:** (0.15, 0.7, 0.15)
- **Compress-heavy:** (0.15, 0.15, 0.7)
- **Balanced:** (0.33, 0.33, 0.34)

### Experimental Design
- **Total configurations:** ~30
- **Metrics tracked:**
  - Fixed scores
  - Delta margins (δ₁, δ₂)
  - Promotion rates
  - Score variance
  - Component contributions

### Success Criteria
1. At least one configuration achieves δ₂ > 0.05
2. Improved separation from controls
3. Stable rankings (Spearman ρ > 0.7)

## Predictions

Based on previous campaigns:
- **Ngram-only:** Highest absolute scores but poor deltas
- **Coverage-only:** Low scores, moderate deltas
- **Compress-only:** Unstable, high variance
- **Optimal range:** Ngram 0.4-0.5, Coverage 0.3-0.4

## Analysis Plan

1. Run all weight configurations
2. Compute delta improvements
3. Analyze component contributions
4. Identify optimal weight region
5. Test on holdout set (remaining 10 seeds)

## Calibration Tests

### Threshold Calibration
- Test δ thresholds: [0.03, 0.04, 0.05, 0.06, 0.07]
- Measure promotion rates at each level
- Estimate false positive rates

### Penalty Calibration
- Repetition penalty: [0.05, 0.1, 0.15, 0.2]
- Length penalty: [0.0, 0.05, 0.1]
- Anchor bonus: [0.0, 0.1, 0.2]

## Outputs

- `runs/2025-01-06-scorer-ablations/ABLATION_MATRIX.csv`
- `runs/2025-01-06-scorer-ablations/WEIGHT_SWEEP.csv`
- `runs/2025-01-06-scorer-ablations/CALIBRATION_REPORT.md`
- `runs/2025-01-06-scorer-ablations/optimal_weights.json`

## Declaration

This plan is committed before running any tests. No post-hoc weight selection.

---
*Registered: 2025-01-06T00:00:00Z*