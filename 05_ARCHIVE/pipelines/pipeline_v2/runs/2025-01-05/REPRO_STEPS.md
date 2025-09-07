# Reproduction Steps

Generated: 2025-09-05T19:38:43.087410

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

## Verification
```bash
python experiments/pipeline_v2/scripts/common/make_manifest.py --verify MANIFEST.sha256
```
