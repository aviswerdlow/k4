# Light Sweep Scoring Pipeline - Complete Implementation

## Overview

This is the complete Option B implementation for scoring cylindrical projection sweep results once character mappings become available. The pipeline implements frozen 5-gram language model scoring with anchor masking, empirical p-values, Bonferroni correction, and replication testing.

## Files Provided

### Core Pipeline
- `score_light_sweep.py` - Main scoring driver (ready for production)
- `geometry_analysis.py` - Geometry-based selection path analysis

### Test Utilities
- `generate_mock_letters_map.py` - Creates mock character mapping for testing
- `generate_mock_light_sweep.py` - Creates mock projection results for testing

### Required Input Files
1. **`letters_map.csv`** (TO BE PROVIDED)
   ```csv
   index,char
   0,O
   1,B
   ...
   96,R
   ```

2. **`light_sweep_results.json`** (FROM PROJECTION ANALYSIS)
   ```json
   {
     "selections": {
       "M_15": [{"angle": 0, "indices": [...]}, ...],
       "M_20": [{"angle": 0, "indices": [...]}, ...],
       "M_24": [{"angle": 0, "indices": [...]}, ...]
     }
   }
   ```

3. **`letters_surrogate_k4.csv`** (ALREADY PROVIDED)
   - Contains 97 surrogate positions with geometric data

## Scoring Protocol

### 1. Language Model (Frozen)
- **5-gram scorer**: Hash `7f3a2b91c4d8e5f6`
- **Common n-grams**: Weighted log probabilities
- **Function words**: 34 common English words
- **Scoring formula**: `LM_score(text) + function_word_bonus(text)`

### 2. Anchor Masking
- **Windows masked**: [21:25), [25:34), [63:69), [69:74) (0-based)
- **Non-anchor universe**: 73 positions available for null sampling

### 3. Statistical Testing
- **Null distribution**: 1,000 yoked permutations per test
- **Empirical p-value**: `(count >= observed + 1) / (N_nulls + 1)`
- **Bonferroni correction**: `p_adj = min(1.0, p_raw * num_tests)`
- **Significance threshold**: p_adj ≤ 0.001

### 4. Replication Requirements
- **Angular replication**: Must pass at angle ± 2°
- **Both conditions required**:
  1. p_adj ≤ 0.001 at target angle
  2. p_adj ≤ 0.001 at both neighboring angles (±2°)

## Usage Instructions

### Step 1: Prepare Input Files
```bash
# Ensure these files exist in the working directory:
# - letters_surrogate_k4.csv (provided)
# - light_sweep_results.json (from projection analysis)
# - letters_map.csv (to be provided by vendor)
```

### Step 2: Run Scoring
```bash
python3 score_light_sweep.py
```

### Step 3: Review Outputs
The pipeline generates three output files:

1. **`lm_scores.json`** - Complete results for all angle/M combinations
   - Fields: angle, M, size, score, p_raw, p_adj, pass, replicate_pm2

2. **`lm_top.csv`** - Top 10 results sorted by significance
   - Human-readable CSV format
   - Includes overlay text samples

3. **`lm_receipts.json`** - Full audit trail
   - File hashes (SHA-256)
   - Scorer hash and parameters
   - Summary statistics

## Test Mode

To verify the pipeline before real data arrives:

```bash
# Generate mock data
python3 generate_mock_letters_map.py
python3 generate_mock_light_sweep.py

# Run scoring on mock data
python3 score_light_sweep.py
```

## Acceptance Criteria

A selection is considered significant if and only if:

1. **Statistical significance**: p_adj ≤ 0.001 after Bonferroni correction
2. **Replication**: Also passes at angles ±2° with p_adj ≤ 0.001
3. **Both conditions must be met**

## Expected Results

### If Significant Effects Found:
```
✓ SIGNIFICANT RESULTS FOUND
Significant angles with replication:
  Angle 120°, M=20: p_adj=0.000432, score=2.341
    Overlay: THEFOLLOWINGMESSAGE...
```

### If No Significant Effects:
```
✗ No selections passed significance threshold with replication
The projection hypothesis does not show significant effects.
```

## Quality Assurance

✅ **Frozen scorer**: Hash `7f3a2b91c4d8e5f6` ensures reproducibility
✅ **Anchor masking**: Applied consistently across all operations
✅ **Empirical p-values**: 1,000 nulls minimum
✅ **Multiple testing correction**: Bonferroni across all tests
✅ **Replication required**: ±2° angular stability
✅ **Complete audit trail**: SHA-256 hashes for all inputs

## Decision Tree

```
Run scorer with letters_map.csv
├── Any p_adj ≤ 0.001?
│   ├── Yes → Check replication at ±2°
│   │   ├── Replicated → ✓ SIGNIFICANT (escalate)
│   │   └── Not replicated → ✗ FAIL
│   └── No → ✗ FAIL (close hypothesis)
```

## Notes

- The mock data uses random selections and will typically show no significant effects
- Real character mappings from `letters_map.csv` are required for meaningful results
- The scorer is deterministic (seed=20250913) for reproducibility
- All indices are maintained in tick order throughout processing

---

**Status**: Pipeline complete and tested. Awaiting `letters_map.csv` for production run.