# K4 (GRID-only + AND) — scope, tail behavior, P74, and style panel

## Abstract for groups.io Peer Review

We evaluated K4 under a pre-registered, reproducible frame (anchors fixed; NA-only permutations; Option-A; six-class repeating schedule; head gate = Flint v2 AND calibrated Generic with tokenization v2; 10k mirrored nulls, Holm m=2). Within this frame, one head survives (GRID family) by quantified tie-breakers. Outside this frame (full deck or OR policy), multiple readings remain; we state this explicitly.

Seam-free runs under the frame observe the same tail letters 75..96 ("OF AN ANGLE IS THE ARC") across route families; anchors alone do not force the tail (single-key infeasible; multi-class feasible but under-determined).

We also tested P[74] ("THE JOY" bridge): cryptography and structure admit all 26 letters; the null model does not discriminate at that single position, so 74 is editorial when metrics tie. A misspelling tolerance audit (Levenshtein-1 for content tokens) does not alter any publish decisions.

As a report-only panel, we compare candidate heads to K1–K3 style (lexical overlap, function-word rhythm, letter n-grams, word-length distribution, V/C cadence). This does not change gating; it's there for discussion. We welcome critique and alternate bars; we'll pre-register any new thresholds and return numbers under that bar.

---

## Key Claims and Boundaries

1. **Uniqueness Claim**: Single winner WITHIN GRID-only + AND policy frame
2. **Tail Observation**: Empirical invariance under tested conditions (not a mathematical proof)
3. **P[74] Position**: Editorial choice supported by cryptographic flexibility
4. **Style Panel**: Report-only comparison to K1-K3, no gating impact

## Repository and Verification

Full code, data, and reproducibility instructions available at: [repository link]

To verify our claims:
```bash
k4 confirm --ct data/ciphertext_97.txt --pt results/GRID_ONLY/cand_005/plaintext_97.txt [...]
```

## Reproduction Pack

For complete verification and sensitivity analysis:
- **Quick Results**: `experiments/cadence_panel/runs/2025-09-05/QUICK_READ.md`
- **Comprehensive Report**: `experiments/cadence_panel/runs/2025-09-05/CADENCE_PANEL_REPORT_COMPREHENSIVE.md`
- **Exact Commands**: `experiments/cadence_panel/runs/2025-09-05/REPRO_STEPS.md`
- **File Integrity**: `experiments/cadence_panel/runs/2025-09-05/MANIFEST.sha256`

Key finding: Winner maintains higher CCS than runner across all 6 sensitivity configurations (token windows, character windows, declarative reference, and 3 weight variants). Ordering is robust.

## Alternates Exploration

We also tested **equivalent surveying imperatives** ('SET THE BEARING TRUE', 'CORRECT THE BEARING TO TRUE', 'REDUCE THE COURSE TO THE TRUE MERIDIAN', 'BRING THE LINE TO TRUE MERIDIAN', 'APPLY DECLINATION', 'READ/SEE/NOTE/SIGHT/OBSERVE THE BERLIN/CLOCK') under GRID-only + AND + nulls (seam-free). **No alternates** passed. Adjacent frames (AND POS ≥ 0.80; full-deck AND; OR with top-0.5%) behaved as expected (either eliminated by stricter bars, or filtered by nulls after gate). One-page summaries and SHA manifests live in `experiments/alternates/runs/2025-09-05/`.

### Alternates Reproduction Pack
- **Within-frame summary**: `experiments/alternates/runs/2025-09-05/within_frame/ALTERNATES_SUMMARY.md`
- **Adjacent frames**: `experiments/alternates/runs/2025-09-05/{and_pos080,full_deck,or_strict}/SUMMARY.md`
- **Reproduction steps**: `experiments/alternates/runs/2025-09-05/REPRO_STEPS.md`
- **File integrity**: `experiments/alternates/runs/2025-09-05/MANIFEST.sha256`

## Invitation for Review

We explicitly invite:
- Alternative framing suggestions
- Different statistical bars or thresholds
- Critique of our tie-breaker methodology
- Additional style metrics for the cadence panel
- Discussion of the tail invariance observation
- Review of alternate imperatives testing

Please respond with specific, testable alternatives that we can implement and evaluate under controlled conditions.