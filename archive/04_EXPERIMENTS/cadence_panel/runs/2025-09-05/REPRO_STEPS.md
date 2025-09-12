# Reproduction Steps - Cadence Panel Sensitivity Analysis

All commands run from repository root: `/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus`
Seed: 1337 (deterministic across all runs)

## 1. Generate Reference Distributions

### Token-Window Reference (Baseline)
```bash
python3 experiments/cadence_panel/scripts/bootstrap_ref.py \
  --k1 experiments/cadence_panel/data/K1.txt \
  --k2 experiments/cadence_panel/data/K2.txt \
  --k3 experiments/cadence_panel/data/K3.txt \
  --windows 2000 --tokens 75 --seed 1337 \
  --out experiments/cadence_panel/runs/2025-09-05/ref_metrics_token.json
```

### Character-Window Reference
```bash
python3 experiments/cadence_panel/scripts/bootstrap_ref.py \
  --k1 experiments/cadence_panel/data/K1.txt \
  --k2 experiments/cadence_panel/data/K2.txt \
  --k3 experiments/cadence_panel/data/K3.txt \
  --windows 2000 --chars 450 --seed 1337 \
  --out experiments/cadence_panel/runs/2025-09-05/ref_metrics_char.json
```

### Declarative Reference (K2 without coordinates)
```bash
python3 experiments/cadence_panel/scripts/bootstrap_ref.py \
  --k1 experiments/cadence_panel/data/K1.txt \
  --k2-decl experiments/cadence_panel/data/K2_decl.txt \
  --k3 experiments/cadence_panel/data/K3.txt \
  --windows 2000 --tokens 75 --seed 1337 \
  --out experiments/cadence_panel/runs/2025-09-05/ref_metrics_decl.json
```

## 2. Run Panel Analyses

### Baseline Token-Window Analysis
```bash
python3 experiments/cadence_panel/scripts/panel.py \
  --heads_dir experiments/cadence_panel/data/heads \
  --ref experiments/cadence_panel/runs/2025-09-05/ref_metrics_token.json \
  --cuts experiments/cadence_panel/data/canonical_cuts.json \
  --fwords experiments/cadence_panel/data/function_words.txt \
  --weights experiments/cadence_panel/data/weights_baseline.json \
  --out experiments/cadence_panel/runs/2025-09-05/baseline_token/
```

### Character-Window Analysis
```bash
python3 experiments/cadence_panel/scripts/panel.py \
  --heads_dir experiments/cadence_panel/data/heads \
  --ref experiments/cadence_panel/runs/2025-09-05/ref_metrics_char.json \
  --cuts experiments/cadence_panel/data/canonical_cuts.json \
  --fwords experiments/cadence_panel/data/function_words.txt \
  --weights experiments/cadence_panel/data/weights_baseline.json \
  --out experiments/cadence_panel/runs/2025-09-05/char_windows/
```

### Declarative Reference Analysis
```bash
python3 experiments/cadence_panel/scripts/panel.py \
  --heads_dir experiments/cadence_panel/data/heads \
  --ref experiments/cadence_panel/runs/2025-09-05/ref_metrics_decl.json \
  --cuts experiments/cadence_panel/data/canonical_cuts.json \
  --fwords experiments/cadence_panel/data/function_words.txt \
  --weights experiments/cadence_panel/data/weights_baseline.json \
  --out experiments/cadence_panel/runs/2025-09-05/declarative/
```

## 3. Weight Sensitivity Tests

### Bigram/Trigram-Heavy Weights
```bash
python3 experiments/cadence_panel/scripts/panel.py \
  --heads_dir experiments/cadence_panel/data/heads \
  --ref experiments/cadence_panel/runs/2025-09-05/ref_metrics_token.json \
  --cuts experiments/cadence_panel/data/canonical_cuts.json \
  --fwords experiments/cadence_panel/data/function_words.txt \
  --weights experiments/cadence_panel/data/weights_bi_tri_heavy.json \
  --out experiments/cadence_panel/runs/2025-09-05/weights_bi_tri_heavy/
```

### Rhythm-Heavy Weights
```bash
python3 experiments/cadence_panel/scripts/panel.py \
  --heads_dir experiments/cadence_panel/data/heads \
  --ref experiments/cadence_panel/runs/2025-09-05/ref_metrics_token.json \
  --cuts experiments/cadence_panel/data/canonical_cuts.json \
  --fwords experiments/cadence_panel/data/function_words.txt \
  --weights experiments/cadence_panel/data/weights_rhythm_heavy.json \
  --out experiments/cadence_panel/runs/2025-09-05/weights_rhythm_heavy/
```

### Uniform Weights
```bash
python3 experiments/cadence_panel/scripts/panel.py \
  --heads_dir experiments/cadence_panel/data/heads \
  --ref experiments/cadence_panel/runs/2025-09-05/ref_metrics_token.json \
  --cuts experiments/cadence_panel/data/canonical_cuts.json \
  --fwords experiments/cadence_panel/data/function_words.txt \
  --weights experiments/cadence_panel/data/weights_uniform.json \
  --out experiments/cadence_panel/runs/2025-09-05/weights_uniform/
```

## 4. Generate Manifest
```bash
python3 experiments/cadence_panel/scripts/make_manifest.py \
  experiments/cadence_panel/runs/2025-09-05/
```

## Expected Outputs

Each panel run generates:
- `cadence_panel_summary.csv` - Raw metrics and CCS scores
- `cadence_panel_detailed.json` - Complete analysis data
- `CADENCE_PANEL_REPORT.md` - Formatted report

Final outputs:
- `CADENCE_PANEL_REPORT_COMPREHENSIVE.md` - Combined analysis with appendices
- `SENSITIVITY_SUMMARY.md` - Quick results table
- `QUICK_READ.md` - Executive summary
- `MANIFEST.sha256` - File integrity verification

## Weight Configurations

### Baseline (`weights_baseline.json`)
```json
{
  "J_content": 0.25,
  "J_content_lev1": 0.10,
  "cosine_bigram": 0.20,
  "cosine_trigram": 0.15,
  "chi2_wordlen_abs": -0.10,
  "vc_ratio_abs": -0.10,
  "fw_mean_gap_abs": -0.05,
  "fw_cv_abs": -0.05
}
```

### Bigram/Trigram-Heavy (+50% on n-grams)
Increases cosine_bigram to 0.30, cosine_trigram to 0.22

### Rhythm-Heavy (+180% on function word metrics)
Increases fw_mean_gap_abs to -0.14, fw_cv_abs to -0.14

### Uniform (equal weights within categories)
All positive metrics: 0.16 each
All negative metrics: -0.09 each