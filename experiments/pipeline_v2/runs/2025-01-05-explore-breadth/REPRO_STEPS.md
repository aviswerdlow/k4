# Reproduction Steps

Generated: 2025-09-05T22:26:40.758179

## Configuration
- Global seed: 1337
- Campaign: PV2-001
- Mode: confirm

## Commands

## Seed Derivation
```
seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
```

## Output Files
- `ANCHOR_MODE_MATRIX.csv`
- `promotion_queue.json`

## Verification
```bash
python experiments/pipeline_v2/scripts/common/make_manifest.py --verify MANIFEST.sha256
```
