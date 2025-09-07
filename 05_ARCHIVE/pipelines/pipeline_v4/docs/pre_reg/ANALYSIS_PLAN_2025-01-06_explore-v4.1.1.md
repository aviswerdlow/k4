# Pre-Registration: Explore v4.1.1 Language Weights Hotfix

**Date**: 2025-01-06  
**Branch**: pipeline-v4.1.1-explore-language-first  
**Pre-reg Hash**: [TO BE FILLED AFTER COMMIT]

## Hypothesis

The v4.1 production run (K=200) saturated at head-gate with only 1/200 passes due to insufficient function word weight (λ_fw=0.4). Sanity checks with λ_fw=0.8 showed 100% head-gate pass rate. This pre-registration documents a single, targeted weights adjustment to the language objective.

## Intervention (SINGLE CHANGE)

### Weight Changes
```json
{
  "lambda_ng": 1.0,        // UNCHANGED
  "lambda_fw": 0.8,        // CHANGED from 0.4 → 0.8
  "lambda_cov": 0.2,       // UNCHANGED  
  "lambda_pattern": 0.8,   // UNCHANGED
  "lambda_verb": 1.2,      // UNCHANGED
  "lambda_fw_cap": 0.2,    // CHANGED from 0.4 → 0.2
  "lambda_fratio": 0.3     // CHANGED from 0.5 → 0.3
}
```

### All Other Parameters FROZEN
- Anchor placer: α=0.6, β=0.2, γ=0.2
- Placement rules: min_start≥10, min_inter≥5, avoid±2 verb tokens
- Repair budget limits: UNCHANGED
- Blinding/leakage checks: UNCHANGED
- Delta thresholds: UNCHANGED

## A/B Pilot Design

### Setup
- **Sample Size**: 50 heads per arm (100 total)
- **Randomization**: MASTER_SEED=1337, deterministic seed derivation
- **Arm A (Control)**: v4.1 weights (λ_fw=0.4)
- **Arm B (Treatment)**: v4.1.1 weights (λ_fw=0.8)

### Measurements
1. Head-gate metrics: fw_post, verb_post, cov_post, pattern_post
2. Delta performance: windowed_min (r∈{2,3,4}), shuffled
3. Leakage test: Must be 0.000 for all heads

## Acceptance Thresholds (Pre-Declared)

For proceeding to full K=200 run, Arm B must achieve:
- **Head-gate pass rate**: ≥80%
- **Delta pass rate**: ≥25% (min across r + shuffled)
- **Leakage**: 0.000 for every head
- **Lift Requirement**: B must show clear improvement over A

### Marginal Case
If delta pass rate is 20-24% (close miss), proceed but require ≥10 survivors at K=200 delta stage before orbits/nulls.

## Full Production Run (K=200)

Only executed if pilot meets thresholds:
1. Generate 200 heads with v4.1.1 weights
2. Full Explore pipeline (placement → repair → head-gate → deltas)
3. Survivors continue to orbits (ε_tie ≤ 0.15) and fast nulls (K=1000, Holm m=2)
4. Output promotion_queue.json with all passing heads

## Analysis Plan

### Primary Outcomes
- Head-gate pass rate comparison (v4.1 vs v4.1.1)
- Delta pass rate improvement
- Final survivor count through full funnel

### Secondary Analyses  
- Distribution of language metrics (fw_post, verb_post)
- Repair operation frequency and types
- Pattern preservation through pipeline

## Deliverables

### Pilot
- `HEAD_GATE_MATRIX.csv`: 100 rows with A/B labels
- `PILOT_REPORT.md`: Funnel counts and threshold assessment

### Full Run (if pilot passes)
- `EXPLORE_MATRIX.csv`: 200 rows, full metrics
- `DASHBOARD.csv`: Stage counts, distributions
- `promotion_queue.json`: Orbit/null survivors
- `EXPLORE_REPORT.md`: Complete funnel analysis
- `MANIFEST.sha256`: Reproducibility hashes

## Reproducibility

All runs use:
- Frozen weights JSON: `policies/weights.explore_v4_1_1.json`
- Policy SHA-256 in `POLICIES.SHA256`
- Ciphertext SHA: [existing pinned]
- Exact CLI in `REPRO_STEPS.md`

## Decision Rules

1. **If pilot passes all thresholds** → Execute full K=200
2. **If pilot fails thresholds** → Mark v4.1.1 as SATURATED, no further tweaking
3. **If marginal delta performance** → Proceed with caution, require strong K=200 delta survival

## Ethics & Integrity

This pre-registration locks the analysis before seeing results. No post-hoc adjustments to thresholds or cherry-picking of metrics.