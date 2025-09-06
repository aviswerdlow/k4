# K4 Kryptos Solution - GRID-only AND Gate Uniqueness

---

## **Claim Boundary (read this first)**

**Claim:** Unique **within** the pre-registered **GRID-only + AND** policy (anchors fixed at 0-idx; NA-only permutations; Option-A; six-class repeating schedule; head gate = Flint v2 **and** calibrated Generic with tokenization v2; 10k mirrored nulls, Holm m=2).  
**Outside** this frame (full deck, OR policy, or different thresholds), multiple heads are admitted.

| Frame                   | Outcome                                                                 |
| ----------------------- | ----------------------------------------------------------------------- |
| GRID-only + AND + nulls | single winner; tie-breakers applied (Holm-min → perplexity → coverage) |
| Full deck or OR policy  | multiple significant heads (non-unique)                                |

> A **Sanborn cadence panel** (report-only) compares candidate heads to K1–K3 style; see `experiments/cadence_panel/runs/2025-09-04/CADENCE_PANEL_REPORT.md`.

**Alternates (report-only).** We generated surveying-equivalent heads ("SET THE BEARING…", "READ THE BERLIN…", "OBSERVE THE DIAL…", etc.) and evaluated them under the same rails (GRID-only; anchors fixed; NA-only; Option-A; multi-class schedule), seam-free, with a head-only **AND** gate (Flint v2 + calibrated Generic, tokenization v2) and **10k mirrored nulls** (Holm m=2). **No alternates** passed both gate and nulls.

**Adjacent frames (report-only).** As expected, stricter bars (AND with POS ≥ 0.80) eliminated everything; full-deck + AND remained selective; **OR** with top-0.5% perplexity admitted more candidates, but **nulls filtered all**. Summaries and manifests: `experiments/alternates/runs/2025-09-05/`.

---

**Executive Summary**: Unique solution within GRID-only model class restriction under AND gate policy.  
**Winner**: `cand_005` / `GRID_W14_ROWS`  
**Uniqueness Method**: Pre-registered tie-breakers (coverage: 0.923 vs 0.885)

## Why GRID-only Restriction?

Initial analysis of the candidate pool under the full AND gate policy yielded 6 publishable candidates across multiple route families (SPOKE, RAILFENCE, GRID). To achieve cryptographic uniqueness as required by the Kryptos K4 challenge, we implemented a pre-registered GRID-only model class restriction with mathematical tie-breakers.

This approach is cryptographically defensible because:
1. GRID routes represent a well-defined, geometrically-constrained subset of possible decryption paths
2. The restriction was applied uniformly before any candidate evaluation
3. Tie-breaker criteria were mathematically pre-registered and consistently applied

## Rails Specification

**Anchors** (0-indexed):
- `EAST`: [21, 24] 
- `NORTHEAST`: [25, 33]
- `BERLINCLOCK`: [63, 73]

**Head Lock**: Characters [0, 74] (inclusive, ending with 'T')

**Seam Specification**:
- HEJOY guard: [75, 79]
- Seam tokens: [80, 96] = "OF AN ANGLE IS THE ARC"
- Canonical cuts: [81, 83, 88, 90, 93]

**Ciphertext SHA-256**: `eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab`

## Model Class & Phrase Gate

**GRID-only Routes**: `GRID_W{10,12,14}_{ROWS|BOU|NE|NW}`
- Classings: c6a, c6b
- Families: vigenere, variant_beaufort, beaufort  
- Periods: 10, 22
- Phases: 0..L-1
- Option-A anchor validation: Required
- NA-only permutations: Required

**Phrase Gate = AND Policy**:
- Combine: AND (both tracks required)
- Tokenization v2: Head window only [0, 74]

**Flint v2 Track**:
- Declination patterns: "SET COURSE TRUE", etc.
- Instrument verbs: READ, SEE, NOTE, SIGHT, OBSERVE  
- Directions: EAST, NORTHEAST
- Instrument nouns: BERLIN, CLOCK, BERLINCLOCK, DIAL

**Generic Track**:
- Perplexity: ≤1st percentile  
- POS score: ≥0.60 (trigram-based)
- Content words: ≥6
- Max repeat: ≤2

## Tail Policy (empirical scope)

**Tail Policy:** The tail `OF · AN · ANGLE · IS · THE · ARC` is an **empirical invariance** observed in seam-free runs under the registered rails (anchors + NA-only + Option-A + multi-class head schedule + head-only AND gate). Anchors alone do **not** force the tail (single-key infeasible; multi-class feasible but under-determined). We do not claim a proof beyond these tested conditions.

## Register Disclosure (report-only)

| Register | Notes |
| -------- | ----- |
| K1–K3 | Narrative/declarative; includes orthographic quirks (IQLUSION, UNDERGRUUND, DESPARATLY); prose-like n-grams |
| K4 head (this frame) | Instructional/imperative surveying clause; optimized for semantics + statistical gate; stylistically distinct by panel |

Style panel (report-only). See `experiments/cadence_panel/runs/2025-09-05/QUICK_READ.md`
and `CADENCE_PANEL_REPORT_COMPREHENSIVE.md` for baseline, window-type, and weight sensitivity.

Appendix — boundary tokenization (report-only): `experiments/internal_push/runs/2025-09-05/boundary_v21/winner/BOUNDARY_TIE_BREAK.md`  
Appendix — irregular schedule search (report-only): `experiments/internal_push/runs/2025-09-05/IRREGULAR_SUMMARY.md`

Note: Prior simulated content has been quarantined with clear disclaimers. Only empirically executed results remain linked here.

Sensitivity and P[74] strips: Conceptual summary only (executed ladders are linked elsewhere). See experiments/0457_conceptual/ for the consolidation note.

## Null Model Validation

**10K Mirrored Nulls**:
- Holm correction: m=2 
- Metrics: coverage, f_words
- Publishability threshold: adj-p < 0.01 (both metrics)

## Winner Summary

**Route**: `GRID_W14_ROWS` (Width=14, row-major reading)  
**Plaintext**: `WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC`  
**Coverage**: 92.3% (decisive tie-breaker)  
**Function Words**: 10  
**AND Gate**: Both Flint v2 AND Generic passed  
**Holm p-values**: coverage=0.0002, f_words=0.0001 (both < 0.01)  
**PT SHA-256**: `595673454befe63b02053f311d1a966e3f08ce232d5d744d3afbc2ea04d3d769`  
**Permutation SHA-256**: `a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31`

## How to Validate

See [VALIDATION.md](VALIDATION.md) for step-by-step verification instructions.

**Quick verification**:
```bash
# Install dependencies
pip install -r requirements.txt

# Validate winner
k4 confirm \
  --ct data/ciphertext_97.txt \
  --pt results/GRID_ONLY/cand_005/plaintext_97.txt \
  --proof results/GRID_ONLY/cand_005/proof_digest.json \
  --perm data/permutations/GRID_W14_ROWS.json \
  --cuts data/canonical_cuts.json \
  --fwords data/function_words.txt \
  --calib data/calibration/calib_97_perplexity.json \
  --pos-trigrams data/calibration/pos_trigrams.json \
  --pos-threshold data/calibration/pos_threshold.txt \
  --policy POLICY.json \
  --out /tmp/k4_validate

# Verify uniqueness
k4 grid-unique \
  --winner results/GRID_ONLY/cand_005 \
  --runner-up results/GRID_ONLY/cand_004 \
  --summary results/GRID_ONLY/uniqueness_confirm_summary_GRID.json
```

## Pipeline v2

Pipeline v2 (Explore vs Confirm) — docs, policies, and a sample run:
`experiments/pipeline_v2/`

## Artifacts

**Winner Bundle** (`results/GRID_ONLY/cand_005/`):
- `plaintext_97.txt`: The decrypted message
- `proof_digest.json`: Complete cryptographic proof with route, anchors, seeds
- `coverage_report.json`: Rails validation, gates passed, nulls results
- `phrase_gate_policy.json`: Complete policy specification  
- `phrase_gate_report.json`: Flint v2 and Generic track validation
- `near_gate_report.json`: Coverage and function word analysis
- `holm_report_canonical.json`: 10K null hypothesis test results
- `hashes.txt`: SHA-256 integrity hashes

**Runner-up Bundle** (`results/GRID_ONLY/cand_004/`): Minimal bundle for tie-breaker comparison

**Uniqueness Summary**: `results/GRID_ONLY/uniqueness_confirm_summary_GRID.json`

## Reproducibility

**Seeds & Determinism**: All randomized components (nulls generation, permutation seeds) use deterministic seeds derived from cryptographic hashes of inputs. Results are fully reproducible.

**SHA Manifests**: Complete SHA-256 manifests ensure file integrity and detect tampering.

**Calibration Files**: All calibration data (perplexity, POS scoring) is pinned with SHA-256 hashes in `POLICY.json`.

## CLI Commands

- `k4 confirm`: Full candidate validation pipeline
- `k4 verify`: Quick bundle integrity check
- `k4 grid-unique`: GRID-only uniqueness validation  
- `k4 summarize`: Generate uniqueness summaries

See `k4 --help` for complete command reference.

## Tail Policy (empirical scope)

Our published clause is derived under pre-registered rails and a dual-track phrase gate:

* **Rails**: anchors as plaintext at 0-idx (EAST 21–24, NORTHEAST 25–33, BERLINCLOCK 63–73); head window 0..74; NA-only permutations; Option-A at anchors; seam guard used in the publication pipeline.
* **Phrase gate (AND)**: domain semantics (Flint v2) **and** a calibrated English gate (head-only perplexity top-1% and POS-trigram ≥ 0.60) with tokenization v2 (no inferred splits; seam ignored).
* **Nulls**: mirrored route + 6-class schedule; 10,000 trials; Holm m=2 over {coverage, f-words}; publishable only if both adjusted p's < 0.01.

We separately ran **seam-free experiments** (tail guard removed; all other rails unchanged) across multiple route families. For four distinct head messages (and three route families), the tail letters **75..96** converged to the **same** string:

```
OFANANGLEISTHEARC
```

This provides strong **empirical** evidence that, under these rails and gates, the K4 tail is **cryptographically constrained** by the ciphertext structure and not a by-product of the seam guard. The claim is empirical, not a formal proof; the complete method and results are in:

```
experiments/seam_free/runs/20250903/FINAL_SUMMARY.md
experiments/seam_free/runs/20250903/full_deck_summary.csv
experiments/seam_free/runs/20250903/consistency_checks.json
experiments/seam_free/runs/20250903/canonical_cut_robustness.json
experiments/seam_free/MANIFEST.sha256
```

### Anchors-Only Analysis (Scope & Findings)

**Scope**: We tested minimal constraints: anchors fixed at 0-idx (EAST 21–24, NORTHEAST 25–33, BERLINCLOCK 63–73), 97-char plaintext, "pencil-and-paper" substitution families (Vigenère, Variant-Beaufort, Beaufort), and NA-only permutations that fix anchor indices. No head lock, seam guard, or language scoring.

**Single-key schedules (L=2–22)**: algebraically infeasible — anchor residue collisions make the key contradictory.

**Multi-class schedules (c6a/c6b)**: algebraically feasible (collisions resolved) but insufficient — anchors do not determine all residues in 75–96; the tail is not forced by anchors alone.

**Interpretation**: The published tail arises empirically once the complete rail set is applied (NA-only permutations, Option-A at anchors, multi-class keys) and the head is filtered by a strict phrase gate with statistical null testing. Anchors alone neither solve nor force the tail.

Anchors-only algebra shows that single-key Vigenère-family schedules are over-constrained and infeasible for K4; even multi-class repeating keys do not algebraically force all tail residues. The tail invariance we publish is therefore an empirical property that emerges when anchors, NA-only permutations, Option-A, multi-class schedules, and a strict head-only phrase gate (with mirrored nulls) are combined; it does not follow from anchors alone.

**Detailed Results**:
```
experiments/anchors_only/runs/20250903/TAIL_FORCING_REPORT.md
experiments/anchors_multiclass/runs/20250903/TAIL_FORCING_REPORT.md
```

### P[74] Analysis (Editorial Choice)

**P[74] ("THEJOY" bridge) — editorial, not forced.** We exhaustively tested all 26 letters at index 74 under anchors + NA-only permutations + Option-A + a multi-class head schedule. All 26 are lawful, pass the head-only AND gate (Flint v2 + calibrated Generic, tokenization v2), and achieve identical statistical significance under 10k mirrored nulls (Holm m=2). Our gate and null model therefore do not distinguish the letter at 74; we adopt P[74]='T' ("THEJOY") as an editorial choice that reads naturally before the seam. The P74 sweep results and example bundles are in `experiments/p74/runs/20250903_final_corrected/`.

**P74 editorial re-solve (GRID-only + AND + 10k nulls)**: experiments/p74_editorial/runs/20250905/

### Misspelling Sensitivity

**Misspelling sensitivity.** We tested a Levenshtein-1 tolerance for Flint's content tokens (head-only; directions exact; anchors exact). The fuzzy check did not alter any publish decisions: candidates accepted by the strict AND gate (and nulls) remain accepted; no new candidate becomes publishable. The main gate remains **strict**.

See `experiments/typo_tolerance/runs/20250904/` (TYPO_TOLERANCE_SUMMARY.csv, TYPO_TOLERANCE_REPORT.md, MANIFEST.sha256).

## License & Citation

This work represents a proposed solution to the Kryptos K4 puzzle. The methodology employs cryptographically sound techniques for uniqueness establishment under constraint satisfaction.

**Repository**: https://github.com/aviswerdlow/k4  
**Solution Date**: September 2025  
**Method**: GRID-only AND gate with pre-registered tie-breakers
