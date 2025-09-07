# SATURATED RUN - Explore v4.1 K=200 (Function Word λ=0.4)

## Run Configuration
**Date**: 2025-01-06  
**Tag**: explore-v4.1-K200-fw0.4-saturated-20250106  
**Branch**: pipeline-v4.1-explore-language-first  
**Batch Size**: K=200

## Frozen Weights (FAILED CONFIGURATION)
```json
{
  "lambda_ng": 1.0,
  "lambda_fw": 0.4,
  "lambda_cov": 0.2,
  "lambda_pattern": 0.8,
  "lambda_verb": 1.2,
  "lambda_fw_cap": 0.4,
  "lambda_fratio": 0.5
}
```

## Funnel Results (COMPLETE SATURATION)
- **Input**: 200 heads generated
- **Head-gate Pass**: 1 head (0.5% pass rate)
- **Delta Pass**: 0 heads (0% pass rate)
- **Final Survivors**: 0

## Root Cause Analysis
The function word weight λ_fw=0.4 was too low compared to the sanity check configuration (λ_fw=0.8) that showed 100% head-gate pass rate. This weight mismatch caused near-complete failure at the head-gate stage, with only 1 of 200 heads passing initial quality checks.

## Artifacts
- `EXPLORE_MATRIX.csv`: Full 200-row matrix with metrics
- `MANIFEST.sha256`: Hash verification for reproducibility
- `verb_robust_mcmc.json`: Complete generation logs
- `placement/`: Anchor placement outputs (200 heads)
- `repair/`: Repair operation logs (200 heads)

## Status
**SATURATED** - This configuration has been exhausted and marked as a failed baseline. No further runs will be conducted with λ_fw=0.4.

## Next Steps
Proceeding with v4.1.1 hotfix increasing λ_fw to 0.8 (matching sanity check configuration).