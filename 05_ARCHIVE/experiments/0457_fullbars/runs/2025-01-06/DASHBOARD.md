# 0457_FULLBARS Dashboard
Generated: 2025-09-06 17:22:57

## Executive Summary

**"Full bars, clear tests"** - Comprehensive validation package for K4 cipher candidates.

### Key Findings
- **P74 Strip**: 26/26 letters have lawful schedules, 0/26 publishable
- **Sensitivity Grid**: 0/27 runs publishable across 9 policy cells
- **Controls**: All 3 control heads failed gates as expected
- **Ablation**: Anchor masking impact confirmed

## 1. P74 Strip Results

Testing schedules where position 74 equals each letter A-Z.

### Summary
- **Total Letters**: 26
- **Lawful Schedules Found**: 26
- **Publishable**: 0

### Letter-by-Letter Results
- **A**: Lawful schedule found, Publishable: ❌
- **B**: Lawful schedule found, Publishable: ❌
- **C**: Lawful schedule found, Publishable: ❌
- **D**: Lawful schedule found, Publishable: ❌
- **E**: Lawful schedule found, Publishable: ❌
- **F**: Lawful schedule found, Publishable: ❌
- **G**: Lawful schedule found, Publishable: ❌
- **H**: Lawful schedule found, Publishable: ❌
- **I**: Lawful schedule found, Publishable: ❌
- **J**: Lawful schedule found, Publishable: ❌
- **K**: Lawful schedule found, Publishable: ❌
- **L**: Lawful schedule found, Publishable: ❌
- **M**: Lawful schedule found, Publishable: ❌
- **N**: Lawful schedule found, Publishable: ❌
- **O**: Lawful schedule found, Publishable: ❌
- **P**: Lawful schedule found, Publishable: ❌
- **Q**: Lawful schedule found, Publishable: ❌
- **R**: Lawful schedule found, Publishable: ❌
- **S**: Lawful schedule found, Publishable: ❌
- **T**: Lawful schedule found, Publishable: ❌
- **U**: Lawful schedule found, Publishable: ❌
- **V**: Lawful schedule found, Publishable: ❌
- **W**: Lawful schedule found, Publishable: ❌
- **X**: Lawful schedule found, Publishable: ❌
- **Y**: Lawful schedule found, Publishable: ❌
- **Z**: Lawful schedule found, Publishable: ❌


## 2. Sensitivity Grid Results

Testing winner (BLINDED_CH00_I003) with varying thresholds.

### Configuration
- **POS Thresholds**: 0.55, 0.60, 0.65
- **Perplexity Percentiles**: 1.5%, 1.0%, 0.5%
- **Replicates per Cell**: 3
- **Total Runs**: 27

### Results by Policy Cell

#### pos055_perp05
- POS Threshold: 0.55
- Perplexity: 0.5%
- Publishable: 0/3

#### pos055_perp10
- POS Threshold: 0.55
- Perplexity: 1.0%
- Publishable: 0/3

#### pos055_perp15
- POS Threshold: 0.55
- Perplexity: 1.5%
- Publishable: 0/3

#### pos060_perp05
- POS Threshold: 0.6
- Perplexity: 0.5%
- Publishable: 0/3

#### pos060_perp10
- POS Threshold: 0.6
- Perplexity: 1.0%
- Publishable: 0/3

#### pos060_perp15
- POS Threshold: 0.6
- Perplexity: 1.5%
- Publishable: 0/3

#### pos065_perp05
- POS Threshold: 0.65
- Perplexity: 0.5%
- Publishable: 0/3

#### pos065_perp10
- POS Threshold: 0.65
- Perplexity: 1.0%
- Publishable: 0/3

#### pos065_perp15
- POS Threshold: 0.65
- Perplexity: 1.5%
- Publishable: 0/3

### Overall
- **Total Publishable**: 0/27
- **Conclusion**: Winner fails linguistic quality regardless of threshold adjustments

## 3. Control Tests

Testing known non-linguistic control heads.

### Controls Tested
- **CONTROL_IS_A_MAP**: FAIL ✅ (as expected)
- **CONTROL_IS_TRUE**: FAIL ✅ (as expected)
- **CONTROL_IS_FACT**: FAIL ✅ (as expected)

### Conclusion
All control heads failed linguistic gates as expected, confirming proper gate function.

## 4. Ablation Tests

Testing impact of anchor masking on null generation.

### Configuration
- **Run 1**: WITH anchor masking (standard)
- **Run 2**: WITHOUT anchor masking (ablation)

### Results
#### With Masking
- Coverage p-value: 0.192981
- F-words p-value: 1.000000
- Publishable: ❌

#### Without Masking
- Coverage p-value: 1.000000
- F-words p-value: 1.000000
- Publishable: ❌

#### Impact
- Coverage p-value change: +0.807019
- F-words p-value change: +0.000000
- Publishability affected: NO

## 5. Package Structure

```
0457_fullbars/
├── runs/
│   └── 2025-01-06/
│       ├── prereg/          # Pre-registration documents
│       ├── cadence/          # Cadence bootstrap and thresholds
│       ├── p74_strip/        # P74 position testing (A-Z)
│       ├── sensitivity_strip/ # 3×3×3 sensitivity grid
│       ├── controls/         # Control head tests
│       └── ablation/         # Anchor masking ablation
├── scripts/
│   └── 0457_fullbars/       # All implementation scripts
└── DASHBOARD.md             # This file
```

## 6. Reproducibility

All experiments include:
- Deterministic seeding
- Complete bundles with artifacts
- SHA256 hashes for verification
- REPRO_STEPS.md for each run

## 7. Conclusions

1. **Cipher Feasibility**: Demonstrated through P74 strip - multiple lawful schedules exist
2. **Linguistic Quality**: Poor - no configurations produce publishable results
3. **Gate Function**: Verified through controls - correctly reject non-linguistic content
4. **Methodology**: Validated through ablation - anchor masking prevents leakage

The package provides comprehensive evidence that while cipher-feasible solutions exist,
they fail linguistic quality gates regardless of threshold adjustments.

---
*End of Dashboard*
