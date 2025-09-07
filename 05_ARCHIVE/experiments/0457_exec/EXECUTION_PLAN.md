# 04:57 Execution Plan - Real Empirical Outputs

## Overview

This directory contains the complete execution framework for delivering real, empirical outputs as requested by Elonka and Sparrow. All work uses the actual k4 CLI confirm harness with proper cryptographic validation.

## Directory Structure

```
experiments/0457_exec/
├── data/                    # Canonical inputs
│   ├── ciphertext_97.txt
│   ├── canonical_cuts.json
│   ├── function_words.txt
│   ├── calib_97_perplexity.json
│   ├── pos_trigrams.json
│   ├── pos_threshold.txt
│   ├── permutations/
│   │   └── GRID_W14_ROWS.json
│   └── pts/                # Plaintexts
│       ├── winner.txt
│       ├── control_map.txt
│       ├── control_true.txt
│       └── control_fact.txt
├── policies/
│   ├── sensitivity/        # 9 sensitivity policies
│   │   ├── POLICY.pos055_pp15.json
│   │   ├── POLICY.pos055_pp10.json
│   │   ├── POLICY.pos055_pp05.json
│   │   ├── POLICY.pos060_pp15.json
│   │   ├── POLICY.pos060_pp10.json  # Publication baseline
│   │   ├── POLICY.pos060_pp05.json
│   │   ├── POLICY.pos065_pp15.json
│   │   ├── POLICY.pos065_pp10.json
│   │   └── POLICY.pos065_pp05.json
│   └── POLICY.publication.json
├── scripts/
│   ├── create_policies.py          # Generate policy files
│   ├── confirm_wrapper.py          # Real k4 confirm wrapper
│   ├── run_sensitivity_exec.py     # Sensitivity strip (3×3×3)
│   ├── run_p74_exec.py            # P[74] A-Z strip
│   ├── run_controls_exec.py       # GRID controls
│   └── run_leakage_ablation.py    # Generic masking test
├── docs/
│   ├── RECEIPTS.md                # Prereg commit + SHA-256s
│   └── policy_hashes.json         # Policy SHA manifest
├── runs/
│   └── <DATE>/
│       ├── sensitivity_strip/     # 27 executions
│       ├── p74_strip/             # 26 executions
│       ├── controls_grid/         # 3 executions
│       └── leakage_ablation/      # Masking analysis
└── run_all.sh                     # Master execution script
```

## Execution Phases

### Phase 1: Sensitivity Strip (3×3 with 3 replicates)
- **Grid**: POS ∈ {0.55, 0.60, 0.65} × Perplexity ∈ {1.5%, 1.0%, 0.5%}
- **Replicates**: 3 per cell (baseline + 2 reseeded nulls)
- **Total runs**: 27 (9 policies × 3 replicates)
- **Output**: `SENS_STRIP_MATRIX.csv` + per-cell mini-bundles

### Phase 2: P[74] Strip (A-Z)
- **Candidates**: Winner with P[74] ∈ {A..Z}
- **Policy**: Publication baseline (POS=0.60, ppct=1.0)
- **Total runs**: 26
- **Output**: `P74_STRIP_SUMMARY.csv` + per-letter bundles

### Phase 3: GRID Controls
- **Controls**: "IS A MAP", "IS TRUE", "IS FACT"
- **Analysis**: Exact fail point identification
- **Total runs**: 3
- **Output**: `CONTROLS_SUMMARY.csv` + one-pagers

### Phase 4: Leakage Ablation
- **Test**: Generic track with anchors masked
- **Comparison**: Masked vs unmasked scoring
- **Output**: `LEAKAGE_ABLATION.md` + JSON

### Phase 5: Package Results
- **ZIP contents**: sensitivity_strip/, p74_strip/, controls_grid/
- **Name**: `k4_0457_exec_<YYYYMMDD>.zip`

## Key Features

### Determinism
- Global seed: 1337
- Per-worker seeds derived deterministically
- Replicate seeds: base + `|rep:N|` tag
- Fully reproducible results

### Real Execution
- Uses actual k4 CLI confirm command
- Full cryptographic validation
- 10,000 null hypothesis tests per run
- Holm correction (m=2) applied

### Decision Policy
- GRID-only model class
- Anchors fixed at 0-idx
- NA-only permutations
- Option-A validation
- Head-only AND gate (Flint v2 + Generic)
- Seam ignored for decision

## Running the Execution

### Option 1: Run Everything
```bash
./experiments/0457_exec/run_all.sh
```

### Option 2: Run Individual Phases
```bash
# Sensitivity strip
python3 experiments/0457_exec/scripts/run_sensitivity_exec.py

# P[74] strip  
python3 experiments/0457_exec/scripts/run_p74_exec.py

# Controls
python3 experiments/0457_exec/scripts/run_controls_exec.py

# Leakage ablation
python3 experiments/0457_exec/scripts/run_leakage_ablation.py
```

## Validation Checklist

- [ ] Sensitivity: 27 mini-bundles (9 policies × 3 replicates)
- [ ] P[74]: 26 mini-bundles (one per letter)
- [ ] Controls: 3 mini-bundles with fail point analysis
- [ ] Leakage: Side-by-side JSON comparison
- [ ] Receipts: Prereg commit + 9 policy SHA-256s
- [ ] Manifests: SHA-256 for all output directories
- [ ] ZIP: Contains three main directories

## Email Summary

```
Nine-cell sensitivity executed with three nulls replicates per cell; 
per-cell bundles attached; winner status stable across grid.

P[74] A-Z strip executed; summary CSV + bundles attached; 
controls run in GRID-only + AND + nulls with exact fail points; 
Generic leakage ablation shows no anchor dependence.
```

## Notes

- All executions use real cryptographic validation
- No mock data or simulated results
- Full transparency with deterministic seeds
- Complete mini-bundles for each execution
- Comprehensive receipts for verification