# Confirm Near-Gate Policy

## Pre-Registered Threshold
- **Coverage**: ≥ 0.85
- **Function words (f_words)**: ≥ 8
- **Has verb**: true

## Implementation
- **Code path**: `experiments/pipeline_v4/scripts/run_confirm_gates.py`
- **Function**: `run_near_gate()`
- **Lines**: 77-90

## HEAD_135_B Outcome After Fix
**HEAD_135_B now PASSES near-gate** (f_words=9 ≥ 8, coverage=0.944 ≥ 0.85, has_verb=true)