# K4 Repository Structure

## Directory Layout

```
k4_cli_plus/
│
├── 01_PUBLISHED/              # Main results
│   ├── winner_HEAD_0020_v522B/   # Winning solution
│   ├── runner_up_cand_004/       # Runner-up for comparison
│   └── uniqueness_confirm_summary_GRID.json
│
├── 02_DATA/                   # Essential data files
│   ├── ciphertext_97.txt
│   ├── canonical_cuts.json
│   ├── function_words.txt
│   └── permutations/
│       └── GRID_W14_ROWS.json
│
├── 03_SOLVERS/                # Pipeline code
│   ├── v5_2_2_B/                # Winner pipeline (boundary tokenizer)
│   │   └── scripts/
│   │       ├── boundary_tokenizer_v2.py
│   │       ├── gap_composer_v2.py
│   │       └── run_explore_v5_2_2B_production.py
│   ├── v5_2_1/                  # Content+function attempt
│   └── v5_2/                    # Saturated version
│
├── 04_EXPERIMENTS/            # Supporting evidence
│   ├── seam_free/               # Tail invariance
│   ├── anchors_only/            # Anchor analysis
│   ├── anchors_multiclass/      # Multi-class analysis
│   ├── p74_editorial/           # P[74] resolution
│   ├── typo_tolerance/          # Misspelling analysis
│   ├── cadence_panel/           # Style comparison
│   └── alternates/              # Alternative approaches
│
├── 05_ARCHIVE/                # Historical materials
│   ├── results_grid_only/       # v5.2 results
│   ├── pipelines/               # Older pipelines (v2-v5)
│   └── experiments/             # Additional experiments
│
├── data/                      # Additional data (registry, etc.)
├── results/                   # Other results
├── scripts/                   # Tools and utilities
│   ├── schema/                  # JSON schemas
│   └── tools/                   # Migration and validation tools
│
├── README.md                  # Main documentation
├── VALIDATION.md              # How to validate the solution
├── MIGRATION_LOG.md           # Repository reorganization log
└── MANIFEST.sha256           # Top-level file integrity manifest
```

## Quick Start

### Verify the Solution
```bash
k4 confirm \
  --ct 02_DATA/ciphertext_97.txt \
  --pt 01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt \
  --proof 01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest.json \
  --perm 02_DATA/permutations/GRID_W14_ROWS.json \
  --cuts 02_DATA/canonical_cuts.json \
  --fwords 02_DATA/function_words.txt \
  --policy 01_PUBLISHED/winner_HEAD_0020_v522B/phrase_gate_policy.json \
  --out /tmp/k4_verify
```

### Reproduce the Solution
```bash
cd 03_SOLVERS/v5_2_2_B
python scripts/run_explore_v5_2_2B_production.py
```

## Key Files

- **Winner**: `01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt`
- **Proof**: `01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest.json`
- **Pipeline**: `03_SOLVERS/v5_2_2_B/`
- **Evidence**: `04_EXPERIMENTS/`

## Repository Stats

- Total files: ~7,000
- Winner bundle: 14 files
- Solver pipelines: 98 files
- Supporting experiments: 432 files
- Archive: 2,556 files

## Citation

Repository: https://github.com/aviswerdlow/k4
Solution date: September 2025
Method: GRID-only AND gate with boundary tokenizer v5.2.2-B
