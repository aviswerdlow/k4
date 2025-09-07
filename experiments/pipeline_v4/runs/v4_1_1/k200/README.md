# K=200 v4.1.1 Exploration Batch

## Quick Start

1. **Dashboard**: See `DASHBOARD.csv` for funnel summary
2. **Promotion Queue**: See `promotion_queue.json` for Confirm candidates
3. **Full Report**: See `EXPLORE_REPORT.md` for details

## Validation

To validate a head bundle:
```bash
python scripts/tools/validate_bundle.py \
  experiments/pipeline_v4/runs/v4_1_1/k200/generation/HEAD_XXX_B \
  --schema scripts/schema
```

## File Structure
- `EXPLORE_MATRIX.csv` - Raw exploration results
- `DASHBOARD.csv` - Funnel counts
- `promotion_queue.json` - Candidates for Confirm phase
- `MANIFEST.sha256` - Complete file hashes
- `POLICIES.SHA256` - Policy file hashes
- `generation/` - Individual head bundles
