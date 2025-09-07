# K4 — GRID-only AND-gate claim with v5.2.2-B boundary hardening

This repository publishes a reproducible, hash-pinned evaluation of a K4 plaintext under a declared frame. We state the frame first, show exactly what passes inside it, and point to negative results and alternates outside it.

**Winner**: HEAD_0020_v522B (v5.2.2-B with boundary tokenizer)

> **How to verify**
>
> ```bash
> k4 confirm \
>   --ct 02_DATA/ciphertext_97.txt \
>   --pt 01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt \
>   --proof 01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest.json \
>   --perm 02_DATA/permutations/GRID_W14_ROWS.json \
>   --cuts 02_DATA/canonical_cuts.json \
>   --fwords 02_DATA/function_words.txt \
>   --policy 01_PUBLISHED/winner_HEAD_0020_v522B/phrase_gate_policy.json \
>   --out /tmp/k4_verify_HEAD_0020_v522B
> ```
>
> **Receipts:**
> - PT SHA-256: `e45de44e8e507f1db274cd9916b8d143c75dcb9d2b4266014650870c76aabf27`
> - T2 SHA-256: `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31`
> - Pre-reg commit: `d0b03f4`
> - Policy pack SHA: `bc083cc4129fedbc`

All bundle artifacts declare `"schema_version": "1.0.0"`; if schemas change, data must update the version to match.

______________________________________________________________________

## Claim boundary (read this first)

**Frame (pre-registered v5.2.2-B)**:\
GRID family routes only; anchors as plaintext at fixed 0-idx spans; NA-only permutations; Option-A anchor lawfulness; head-only gates with Boundary Tokenizer v2; AND phrase gate (Flint v2 + Generic) + cadence + context; 10k mirrored nulls with Holm m=2 over {coverage, function-words}.

**Spaced head**:
```
WE ARE IN THE GRID SEE XXXX EAST NORTHEAST AND WE ARE BY THE LINE TO SEE YYYYYYY BERLINCLOCK
```

**What holds inside this frame**: HEAD_0020_v522B passes all gates and is published.\
**Boundary tokenizer note**: XXXX and YYYYYYY are neutral padding spans that preserve the 97-char letters-only format while maintaining word boundaries. These tokens are excluded from all gate metrics per Boundary Tokenizer v2 policy.

**Stylistic Note**: Unlike earlier versions, HEAD_0020_v522B passes cadence and context gates in addition to the AND phrase gate. The boundary tokenizer ensures proper word segmentation without violating the letters-only constraint. Per-gap quotas (G1≥4, G2≥4 function words) are enforced to maintain linguistic quality.

______________________________________________________________________

## Executive summary

- **Winner (within frame)**: **NONE** under policy v5 (mandatory cadence gate)
- **Status**: SATURATED - No candidates pass style requirements
- **Provisional v4 winner**: HEAD_147_B (RETRACTED - failed cadence)
- **Cadence failures**: All candidates exhibit word-salad structure
  - Best candidate: HEAD_147_B with only 2/6 style metrics passed
  - Cosine similarity: 0.0 (threshold ≥0.65)
  - Vowel-consonant ratio: 0.609 (threshold 0.95-1.15)

**Repro tip**: use `VALIDATION.md` for step-by-step rechecks (encrypts-to-CT, gates, nulls), or the `k4 confirm` CLI if available on your system.

______________________________________________________________________

## Rails (cryptographic constraints)

- **Anchors (0-idx, inclusive)**:
  - `EAST` \[21,24\] · `NORTHEAST` \[25,33\] · `BERLINCLOCK` \[63,73\]
- **Head window**: \[0,74\] (head-only gates; anything touching 74 counts once)
- **Seam (reported, not scored by style gates)**: `HEJOY` \[75,79\]; letters \[80,96\]
- **NA-only T₂**; **Option-A at anchors**; **six-class repeating schedule**
- **K4 CT SHA-256**: `eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab`

______________________________________________________________________

## Model class & phrase gate (AND)

- **Routes**: `GRID_W{10,12,14}_{ROWS|BOU|NE|NW}`
- **Classings**: c6a, c6b · **Families**: Vigenère, Variant-Beaufort, Beaufort · **Periods**: 10..22 · **Phases**: 0..L−1

**AND gate (head-only, tokenization v2)**: both tracks must pass

- **Flint v2 (semantics)**: declination expression → instrument verb; EAST + NORTHEAST; instrument noun (BERLIN/CLOCK/BERLINCLOCK/DIAL); content ≥ 6; max repeat ≤ 2.
- **Generic (calibrated)**: perplexity ≤ top-1%; POS-trigram ≥ 0.60; same content/repeat limits.
- **Cadence (report-only panel)**: see appendix paths; does not change the gate.

______________________________________________________________________

## Winner bundle (what you can verify)

`01_PUBLISHED/winner_HEAD_0020_v522B/`

- `plaintext_97.txt` — 97 letters (anchors in place)
- `proof_digest.json` — ⟨family,L,phase⟩×6; forced residues; route SHA; seed recipe
- `near_gate_report.json` — coverage/function-words/verb
- `phrase_gate_policy.json` — complete AND policy (with calibration SHAs)
- `phrase_gate_report.json` — Flint v2 & Generic tracks pass
- `holm_report_canonical.json` — 10k mirrored nulls; Holm m=2 adj-p for coverage & f-words
- `coverage_report.json` — rails echo, encrypts_to_ct:true, route digest, seed
- `hashes.txt` — SHA-256 of all files in the bundle

**Runner-up**: minimal bundle in `01_PUBLISHED/runner_up_cand_004/` for tie-breaker comparison.
**Uniqueness summary**: `01_PUBLISHED/uniqueness_confirm_summary_GRID.json`.

______________________________________________________________________

## How to validate

See `VALIDATION.md` for exact commands (CLI and low-level). Typical flow:

1. Lawfulness (encrypt plaintext to CT; Option-A at anchors)
1. Near-gate (neutral)
1. AND phrase gate (Flint v2 & Generic)
1. 10k mirrored nulls (Holm m=2; both adj-p \< 0.01)
1. Tie-breakers (if needed): Holm-min → perplexity → coverage

If the `k4 confirm` command is installed, you can use the one-liner shown in `VALIDATION.md`; otherwise follow the explicit Python steps.

______________________________________________________________________

## Context & scope notes

### Tail (empirical scope)

Seam-free runs (same rails; no seam guard) across multiple routes and four distinct heads produced the same letters \[80,96\]:

```
OFANANGLEISTHEARC
```

We present this as an empirical observation under the declared rails and gates, not a formal proof that the tail is forced globally. Evidence:

- `experiments/seam_free/runs/20250903/FINAL_SUMMARY.md`
- `…/full_deck_summary.csv`, `…/consistency_checks.json`, `…/canonical_cut_robustness.json`, `…/MANIFEST.sha256`

### Anchors-only (what anchors do / don't do)

- **Single-key Vigenère-family (L=2..22)**: infeasible — residue collisions at anchors.
- **Multi-class (c6a/c6b)**: feasible, but anchors do not determine all tail residues.
- **Conclusion**: the tail invariance we observe emerges when anchors + NA-only permutations + Option-A + multi-class keys + head-only AND gate are applied together; anchors alone don't force it.
- See `experiments/anchors_only/…/TAIL_FORCING_REPORT.md` and `experiments/anchors_multiclass/…/TAIL_FORCING_REPORT.md`.

### P\[74\] ("THE JOY") — editorial

We re-solved P\[74\] A..Z under anchors + NA-only permutations + Option-A + multi-class head schedule. All 26 letters were lawful and indistinguishable by the null model (identical adj-p under 10k mirrored nulls). We adopt P\[74\]='T' ("THE JOY") for readability before the seam.

- See `experiments/p74_editorial/runs/20250905/` (matrix + example bundles).

### Misspelling tolerance

Levenshtein-1 on Flint content tokens (head-only; directions and anchors exact) did not change any publish decisions. The gate remains strict.

- `experiments/typo_tolerance/runs/20250904/`

______________________________________________________________________

## Outside the frame (alternates & negative results)

- **Alternates within rails, seam-free**: surveyed imperatives under GRID-only + AND + nulls → no passers.
- **Adjacent frames (report-only)**:
  - AND with POS ≥ 0.80 → eliminates all candidates;
  - Full deck + AND → selective but multiple;
  - OR + top-0.5% perplexity → admits more, nulls filter them out.
- **Summaries**: `experiments/alternates/runs/2025-09-05/`

**Cadence panel (report-only)**: K1–K3 vs. K4 style comparison (token windows, character windows, weights).

- `experiments/cadence_panel/runs/2025-09-05/QUICK_READ.md`
- `…/CADENCE_PANEL_REPORT_COMPREHENSIVE.md`

______________________________________________________________________

## Reproducibility

- **Seeds & determinism**: all randomized steps seeded from recipe strings; seeds recorded in coverage/holm reports.
- **SHA manifests**: top-level `MANIFEST.sha256` and per-bundle `hashes.txt` pin every artifact and policy.
- **Calibration**: perplexity & POS trigram tables and cadence thresholds have SHAs recorded in policy JSON.

______________________________________________________________________

## Paths you'll want

- **Winner bundle**: `01_PUBLISHED/winner_HEAD_0020_v522B/`
- **Runner-up**: `01_PUBLISHED/runner_up_cand_004/`
- **Uniqueness summary**: `01_PUBLISHED/uniqueness_confirm_summary_GRID.json`
- **Validation guide**: `VALIDATION.md`
- **Cadence panel (report-only)**: `experiments/cadence_panel/runs/2025-09-05/`
- **Seam-free appendix**: `experiments/seam_free/runs/20250903/`
- **Anchors-only appendix**: `experiments/anchors_only/runs/20250903/`
- **P74 editorial sweep**: `experiments/p74_editorial/runs/20250905/`
- **Typo tolerance**: `experiments/typo_tolerance/runs/20250904/`
- **Top-level manifest**: `MANIFEST.sha256`

______________________________________________________________________

## License & citation

This repository documents an audited claim within a stated model class and policy. Please cite the claim boundary, prereg commit, and policy hashes when referencing the result.

**Repository**: https://github.com/aviswerdlow/k4\
**Solution date**: September 2025\
**Method**: GRID-only AND gate with mirrored nulls and pre-registered tie-breakers
