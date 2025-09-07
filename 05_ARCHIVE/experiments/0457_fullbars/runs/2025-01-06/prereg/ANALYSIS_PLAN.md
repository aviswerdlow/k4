# Analysis Plan: Full Bars, Clear Tests Package
**Pre-registered**: 2025-01-06  
**Commit Hash**: 650162be7327b697569e3e64ae2ef8f87d1812a6  
**Master Seed**: 1337  
**CT SHA-256**: eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab

## Model Class

Primary: GRID_W14_ROWS for head-to-head runs  
Controls: GRID variants only (W{10,12,14} × {ROWS,BOU,NE,NW})

## Rails (Confirm Lane Strength)

- **Anchors**: Fixed plaintext at 0-idx spans:
  - EAST [21,24]
  - NORTHEAST [25,33]
  - BERLINCLOCK [63,73]
- **Option-A**: No illegal pass-through for Vigenère/Variant-Beaufort at anchors
- **NA-only T₂**: Anchors map to self in permutations
- **Head Lock**: [0,74] for all gates
- **Seam Policy**: Ignored in phrase gates; tail reported but not scored

## Gates & Order

1. **Near-gate**: Neutral scorer, tokenization v2, head-only
2. **Phrase Gate** (AND of three tracks):
   - **Flint v2**: Declination → instrument verb, EAST+NORTHEAST, instrument noun, content≥6, max repeat≤2
   - **Generic**: Parameters from policy JSONs (POS threshold, perplexity percentile)
   - **Cadence**: Four primitives with bootstrapped thresholds
3. **Nulls**: 10k mirrored, 3 replicates for sensitivity/P74, Holm m=2, both adj-p<0.01 required

## Seed Formulas

### Candidate Seed
```
seed_recipe = "CONFIRM_P74|K4|route:GRID_W14_ROWS|P74:"+L+
              "|ct:"+CT_SHA+"|cadence_policy:"+SHA256(POLICY.cadence.json)
seed_u64 = lo64(SHA256(seed_recipe))
```

### Worker Seed
```
seed_worker = lo64(SHA256(seed_recipe+"|worker:"+wid))  # wid ∈ {0..W-1}
```

### Null Replicate
```
seed_replicate = lo64(SHA256(seed_recipe+"|replicate:"+j+"|worker:"+wid))  # j ∈ {1,2,3}
```

## Promotion Rules & Kill Criteria

- Only heads passing ALL gates (near, Flint v2, Generic, Cadence) proceed to nulls
- No policy edits mid-run
- Two-lane discipline maintained
- Publishable only if both Holm-adjusted p-values < 0.01

## Tokenization v2 Rules

- Head window: [0,74] inclusive
- No inferred splits (THEJOY, AMAP remain single tokens)
- Tokens touching position 74 counted once as head tokens
- Seam [75,96] ignored by gates

## Deliverables

### P74 Strip
- 26 mini-bundles (A-Z)
- P74_STRIP_SUMMARY.csv

### Sensitivity Grid
- 9 policies × 3 null replicates = 27 bundles
- SENS_STRIP_MATRIX.csv

### Controls
- 3 control heads with ONE_PAGER.md each
- CONTROLS_SUMMARY.csv

### Leakage Ablation
- 2 runs (mask on/off)
- LEAKAGE_ABLATION.md

### Cadence
- REF_BOOTSTRAP.md
- THRESHOLDS.json
- ROC.md (optional)

### Top-level
- DASHBOARD.csv
- MANIFEST.sha256
- README.md

## Quality Assurance

All runs must verify:
- encrypts_to_ct=true for feasible schedules
- accepted_by lists all passing tracks for AND gate
- 3 null replicates present for sensitivity/P74
- All policies hash-pinned in POLICIES.SHA256
- REPRO_STEPS.md with exact CLI in every bundle