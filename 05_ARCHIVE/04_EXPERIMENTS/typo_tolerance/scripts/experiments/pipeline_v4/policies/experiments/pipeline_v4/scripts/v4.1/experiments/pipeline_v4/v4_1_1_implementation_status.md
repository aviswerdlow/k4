# Explore v4.1.1 Implementation Status

## Completed Tasks

### 1. ✅ Preserved Failed K=200 Run
- **Location**: `experiments/pipeline_v4/runs/track_a_l/batch_200/`
- **Tag**: `explore-v4.1-K200-fw0.4-saturated-20250106`
- **Documentation**: `SATURATED_NOTE.md` created with full failure analysis
- **Root Cause**: λ_fw=0.4 too low (only 1/200 head-gate passes)

### 2. ✅ Created v4.1.1 Branch & Pre-Registration
- **Branch**: `pipeline-v4.1.1-explore-language-first`
- **Pre-reg**: `docs/pre_reg/ANALYSIS_PLAN_2025-01-06_explore-v4.1.1.md`
- **Key Change**: λ_fw: 0.4 → 0.8 (matching sanity check config)
- **Thresholds Pre-declared**:
  - Head-gate pass rate ≥80%
  - Delta pass rate ≥25%
  - Zero leakage requirement

### 3. ✅ Externalized Weights Configuration
- **Weights JSON**: `policies/weights.explore_v4_1_1.json`
- **SHA-256**: `457181035efbc666a0babc1c067d48f8c263862447280f21ef0cafd8988f83b6`
- **Loader**: `scripts/v4.1/multi_objective_mcmc.py` updated to read from JSON
- **Validation**: SHA-256 recorded in `POLICIES.SHA256`

### 4. ✅ Created A/B Pilot Framework
- **Script**: `scripts/v4.1/run_ab_pilot_v4_1_1.py`
- **Design**: 50 heads per arm, deterministic seeding (MASTER_SEED=1337)
- **Output**: `runs/track_a_l/pilot/HEAD_GATE_MATRIX.csv` and `PILOT_REPORT.md`

## Current Status

### Pilot Results (SIMULATED - STUB IMPLEMENTATION)
The current pilot uses simulation stubs rather than actual generation logic:
- **Arm A (v4.1)**: 42% head-gate, 40% delta pass
- **Arm B (v4.1.1)**: 44% head-gate, 50% delta pass
- **Decision**: ❌ Does not meet thresholds (needs 80% head-gate)

### Next Steps Required

1. **Replace Simulation Stubs**
   - Integrate actual `verb_robust_mcmc` generation logic
   - Connect to real anchor placement and repair systems
   - Implement actual delta calculations

2. **Run Production Pilot**
   - Execute with real generation pipeline
   - Validate against pre-registered thresholds
   - Make go/no-go decision for K=200

3. **If Pilot Passes**
   - Run full K=200 with v4.1.1 weights
   - Generate complete deliverables
   - Process through orbits and nulls

## File Structure Created

```
experiments/pipeline_v4/
├── docs/
│   └── pre_reg/
│       └── ANALYSIS_PLAN_2025-01-06_explore-v4.1.1.md
├── policies/
│   ├── weights.explore_v4_1_1.json
│   └── POLICIES.SHA256
├── scripts/
│   └── v4.1/
│       ├── run_ab_pilot_v4_1_1.py
│       └── multi_objective_mcmc.py
└── runs/
    └── track_a_l/
        ├── batch_200/
        │   ├── SATURATED_NOTE.md
        │   └── TAG.txt
        └── pilot/
            ├── HEAD_GATE_MATRIX.csv
            └── PILOT_REPORT.md
```

## Decision Points

Per pre-registration, the framework is set up for:
1. **If pilot passes thresholds** → Automatic proceed to K=200
2. **If pilot fails** → Mark v4.1.1 as SATURATED, no tweaking
3. **If marginal (20-24% delta)** → Proceed with ≥10 survivor requirement

## Integration Notes

The framework is ready for integration with your actual generation pipeline. The key integration points are:
1. Replace `simulate_head_generation()` with actual MCMC generation
2. Replace `simulate_deltas()` with actual delta calculations
3. Connect to real anchor placement and repair systems
4. Ensure leakage detection is properly implemented

All weight configurations are externalized and version-controlled for full reproducibility.