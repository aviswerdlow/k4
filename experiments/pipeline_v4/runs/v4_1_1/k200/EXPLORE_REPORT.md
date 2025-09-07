# EXPLORE v4.1.1 K=200 Batch Report

## Configuration
- Commit SHA: 6f65f3a (main branch)
- Weights SHA-256: d2b426b77c965c3ecd804c8d25c48ab45f0635db18275f68827cd48fa0d98be0
- Batch size: 200 heads
- Arm: B (diversified weights)

## Funnel Summary
- Total heads generated: 200
- Passed head gate: 197 (98.5%)
- Passed delta thresholds: 200 (100.0%)
- No leakage detected: 200 (100.0%)
- **Promoted to Confirm**: 200

## Weight Distributions

### F-word weights (fw_post)
- fw=7: 1 heads
- fw=9: 2 heads
- fw=10: 6 heads
- fw=11: 11 heads
- fw=12: 20 heads
- fw=13: 25 heads
- fw=14: 27 heads
- fw=15: 21 heads
- fw=16: 19 heads
- fw=17: 10 heads
- fw=18: 13 heads
- fw=19: 13 heads
- fw=20: 10 heads
- fw=21: 10 heads
- fw=22: 6 heads
- fw=23: 3 heads
- fw=24: 2 heads
- fw=25: 1 heads

### Verb weights (verb_post)
- verb=1: 4 heads
- verb=2: 105 heads
- verb=3: 88 heads
- verb=4: 3 heads

### Delta Statistics (survivors)
- Min delta: 0.2301
- Max delta: 0.5149
- Mean delta: 0.3754

## Comparison vs Saturated Run
The previous fw=0.4 run resulted in SATURATION with 0 promoted heads.
This v4.1.1 diversified run promoted 200 heads, demonstrating successful
exploration of the weight space to find viable solutions.
