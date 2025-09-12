# Confirm Batch Execution Summary

## Configuration
- **Date**: 2025-01-06
- **Queue**: experiments/pipeline_v4/runs/v4_1_1/k200/promotion_queue.json
- **Candidates**: 200 total, 199 after previous rejections
- **Max attempts**: 5

## Near-Gate Policy Correction
- **Original threshold**: f_words >= 10 (incorrect)
- **Corrected threshold**: f_words >= 8 (per pre-registration)
- **Impact**: HEAD_135_B now passes near-gate but fails phrase gate

## Execution Results

### Attempt 1: HEAD_66_B
- Near-gate: PASSED (cov=0.895, fw=10)
- Lawfulness: FAILED (no GRID route found)
- **Result**: REJECTED

### Attempt 2: HEAD_147_B
- Near-gate: PASSED (cov=0.895, fw=10)
- Lawfulness: PASSED (GRID_W14_ROWS)
- Phrase gates: PASSED (flint_v2, generic)
- Null hypothesis: PASSED (adj_p_cov=0.0006, adj_p_fw=0.0005)
- **Result**: ✅ PUBLISHED

## Final Status
- **Published candidate**: HEAD_147_B
- **Bundle location**: runs/confirm/HEAD_147_B/
- **Route**: GRID_W14_ROWS
- **Attempts used**: 2 of 5
- **Success rate**: 50% (1 success in 2 attempts)

## Files Generated
- `CONFIRM_NEARGATE_POLICY.md` - Documents corrected threshold
- `CONFIRM_LEDGER.csv` - Tracks all attempts with detailed metrics
- `rejects.json` - Records failed candidates
- `HEAD_147_B/` - Complete Confirm bundle

## HEAD_135_B Status Update
After correcting the near-gate threshold from 10 to 8:
- **Near-gate**: NOW PASSES (f_words=9 >= 8)
- **Phrase gate**: FAILS (generic gate - insufficient content words)
- **Final status**: Still rejected, but for different reason