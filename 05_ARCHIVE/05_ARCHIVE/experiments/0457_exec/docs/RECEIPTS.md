# Receipts - 04:57 Execution

## Prereg Commit

**Repository**: https://github.com/aviswerdlow/k4
**Prereg Commit**: `6db668f` (2025-09-03)
**Tag**: `repo_truthful_20250905`
**Description**: Publication policy pinned before winner selection

## Policy SHA-256 Hashes

### Sensitivity Grid (3×3)

| Policy File | POS | Perplexity % | SHA-256 |
|------------|-----|--------------|---------|
| POLICY.pos055_pp15.json | 0.55 | 1.5% | `c6aa41abcf5a6132f58d4e800e58faa1b2b67eccca054a2be287a61d970d5037` |
| POLICY.pos055_pp10.json | 0.55 | 1.0% | `8b31307ca6d87f6d8950b188bc74433c15f3a938fc4bf107fa403e0c1ca8d48a` |
| POLICY.pos055_pp05.json | 0.55 | 0.5% | `09651069bb2eb03ced3ea6364dc3ddef2ff24e02d89d1736eb8b171790bd5c2c` |
| POLICY.pos060_pp15.json | 0.60 | 1.5% | `55ea5b7d3f579c528fddb9e88e0675a3ead303582fc414bbe828ff52afcde3c9` |
| **POLICY.pos060_pp10.json** | **0.60** | **1.0%** | **`3e0f060fe30172b3a125fd5cbaef07a9884f4c4b5968784b1d1b63c0d6165e61`** |
| POLICY.pos060_pp05.json | 0.60 | 0.5% | `a2b7e17d09b29cd1d30e6d9344b0f281a69f6bfe29a3c202f0ca062e5b147a32` |
| POLICY.pos065_pp15.json | 0.65 | 1.5% | `5bae5a73e712348b2984d473af93b211f59ee0d24dcc1af37047f428f19b8e7e` |
| POLICY.pos065_pp10.json | 0.65 | 1.0% | `12adc5404f858730eda57294b0d24b37507c2320c136c54c7aa6f9aac41f9bd2` |
| POLICY.pos065_pp05.json | 0.65 | 0.5% | `c5776eec2f7c4995c91efdb5ebed0a7b3c018cf7e69eace0408ac37a5e04aa9e` |

**Publication baseline** (bold above): POS=0.60, Perplexity=1.0%

## Calibration File Hashes

| File | SHA-256 |
|------|---------|
| calib_97_perplexity.json | `9bbcf015635ccf5b1a3b225f9732d9a587c32eb97ab1eaeb3f52742aecdc45db` |
| pos_trigrams.json | `a5fad7d87294b1c968e58e43e0106bbb49b377e952cdb420db92ce65cdfda3b9` |
| pos_threshold.txt | `7d680231e9793ecd6ad7252404e91c726e564cd57fcbf140289b9256e077143d` |

## Seed Recipe Format

Base recipe:
```
CONFIRM|K4|route:<ROUTE_ID>|classing:<CLASSING>|policy_sha:<SHA8>
```

Replicate additions:
- Replicate 0: Base recipe (no modification)
- Replicate 1: Base + `|rep:1|`
- Replicate 2: Base + `|rep:2|`

Worker seed derivation:
```
seed_worker = lo64(SHA256(seed_recipe + "|worker:" + worker_id))
```

## Determinism

- Global seed: `1337`
- All randomness derived deterministically from seed recipes
- Results fully reproducible with provided seeds and policies