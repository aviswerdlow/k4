# 01_PUBLISHED - Main Results

This directory contains the published K4 solution and runner-up candidates.

## Current Winner: HEAD_0020_v522B

**Note on wording**: Earlier preview bundles displayed "XXXX … YYYYYYY" at the anchor boundaries as boundary-tokenizer scaffolding. The published bundle uses lexicon fillers ("THEN", "BETWEEN") only. Rails/gates/nulls unchanged; receipts pinned (see PT/T₂/Policy SHAs below).

### Key Files
- `winner_HEAD_0020_v522B/` - The winning solution bundle with v5.2.2-B boundary tokenizer
- `runner_up_cand_004/` - Runner-up for comparison
- `uniqueness_confirm_summary_GRID.json` - Comprehensive uniqueness analysis
- `latest` - Symlink to current winner (HEAD_0020_v522B with fillers)

### Verification
```bash
k4 confirm \
  --ct 02_DATA/ciphertext_97.txt \
  --pt 01_PUBLISHED/latest/plaintext_97.txt \
  --proof 01_PUBLISHED/latest/proof_digest.json \
  --perm 02_DATA/permutations/GRID_W14_ROWS.json \
  --cuts 02_DATA/canonical_cuts.json \
  --fwords 02_DATA/function_words.txt \
  --policy 01_PUBLISHED/latest/phrase_gate_policy.json \
  --out /tmp/k4_verify
```

### Receipts
- **PT SHA-256**: `4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79`
- **T2 SHA-256**: `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31`
- **Policy SHA**: `bc083cc4129fedbc`

### Archive
- `previous_winners/` - Historical winners including sentinel version
  - `HEAD_0020_v522B_padding_sentinel/` - Original with visual scaffolding

## Reports
- `FILLER_MIGRATION_REPORT.md` - Complete migration from sentinels to fillers
- `METRICS_COMPARISON.md` - Before/after metrics showing no change
- Filler rescreen results (entire promotion queue): `04_EXPERIMENTS/filler_rescreen/FILLER_RESCREEN.csv`