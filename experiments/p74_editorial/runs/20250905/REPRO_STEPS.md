# P74 Editorial Study - Reproduction Steps

Generated: 2025-09-05T16:20:12.084306

## Configuration
- Global seed: 1337
- Policy: experiments/p74_editorial/policies/POLICY.publication.json
- Routes: GRID_W14_ROWS, GRID_W10_NW
- Classing: c6a
- Nulls: K=10,000 mirrored with Holm m=2

## Commands

1. Solve schedules for all letters:
```bash
python3 experiments/p74_editorial/scripts/solve_schedule.py
```

2. Run full confirm + nulls:
```bash
python3 experiments/p74_editorial/scripts/run_full_confirm.py
```

## Seed Derivation

Per-letter seed recipe:
```
seed_recipe = "CONFIRM|K4|route:GRID_W14_ROWS|classing:c6a|p74:<X>|digest_sha:<sha>|policy_sha:<sha>"
seed_u64 = lo64(SHA256(seed_recipe))
```

Per-worker nulls seed:
```
seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))
```

## Output Files
- P74_EDITORIAL_MATRIX.csv: Feasibility for all 26 letters
- P74_EDITORIAL_CONFIRM.csv: Full confirm + nulls results
- p74_re_solve/P74_*/: Mini-bundles for each letter
- EDITORIAL_NOTES.md: Summary and conclusions
- MANIFEST.sha256: SHA-256 hashes of all files
