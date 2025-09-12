# A/B Pilot Report - Explore v4.1.1

**Date**: 2025-09-06 19:27:03
**Master Seed**: 1337
**Sample Size**: 50 heads per arm

## Weight Configurations

### Arm A (Control - v4.1)
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

### Arm B (Treatment - v4.1.1)
```json
{
  "lambda_ng": 1.0,
  "lambda_fw": 0.8,
  "lambda_cov": 0.2,
  "lambda_pattern": 0.8,
  "lambda_verb": 1.2,
  "lambda_fw_cap": 0.2,
  "lambda_fratio": 0.3
}
```

## Results Summary

### Arm A (Control)
- Head-gate Pass Rate: 42.0%
- Delta Pass Rate: 40.0%
- Total Survivors: 8/50

### Arm B (Treatment)
- Head-gate Pass Rate: 44.0%
- Delta Pass Rate: 50.0%
- Total Survivors: 10/50

## Threshold Assessment

### Pre-declared Thresholds
- Head-gate Pass Rate (B): ≥80% - ❌ FAIL
- Delta Pass Rate (B): ≥25% - ✅ PASS
- Leakage: 0.000 - ✅ PASS
- Improvement over A: ✅ YES

## Decision

**Overall**: ❌ DO NOT PROCEED



## Metrics Distributions

### Function Words (fw_post)
- Arm A: Mean=0.412, Std=0.049
- Arm B: Mean=0.512, Std=0.049

### Verb Count
- Arm A: Mean=3.9, Std=1.0
- Arm B: Mean=3.9, Std=1.0

### Coverage
- Arm A: Mean=0.679, Std=0.099
- Arm B: Mean=0.679, Std=0.099

### Pattern
- Arm A: Mean=0.668, Std=0.062
- Arm B: Mean=0.668, Std=0.062
