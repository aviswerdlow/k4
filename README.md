# K4 Audit CLI

A small, self-contained tool for **verifying rails**, **rendering readable spacings**, and **packaging audit bundles** for K4 submissions.

This repo documents **process and provenance** — not identities.

---

## Publish gate (process we enforce)

0) **Rails (never change)**  
   - **Anchors (0-idx):** `EAST 21–24`, `NORTHEAST 25–33`, `BERLINCLOCK 63–73`.  
   - **Head lock:** we check/readability on `0..74`.  
   - **Tail guard:** `75–79 = HEJOY` (no cuts inside) and `80–96 = OF · AN · ANGLE · IS · THE · ARC` with seam cuts `[81,83,88,90,93]`.  
   - **T₂ policy:** NA-only permutations; anchors map to self.  
   - **Reproducibility:** SHA-256 for every file + your seed recipe string.

1) **Near-gate** (canonical spacing; neutral scorer)  
   Coverage ≥ 0.85; function words ≥ 8; has verb = true.

2) **Phrase gate** (head+middle only, `0..74`; seam ignored)  
   We accept if **either** track passes:

   - **Generic English:** top-5% perplexity vs a pinned 97-char calibration + POS-trigram well-formedness ≥ T + content ≥ 6 + no repeats > 2.  
   - **Abel-Flint semantics (v2):** checks the *concept* of declination correction and surveying tokens (not an exact phrase):
     - a **declination-correction expression** appears (e.g., "set … course … true (meridian)", "correct … bearing … to true", "reduce … course … to the true line", "apply declination / bring to true meridian"),  
     - **after** that expression, an **instrument verb** occurs (READ / SEE / NOTE / SIGHT / OBSERVE),  
     - **direction tokens** EAST and NORTHEAST present,  
     - **instrument noun** whitelisted (BERLIN / CLOCK / BERLINCLOCK / DIAL),  
     - **clause health:** content ≥ 6; no non-anchor content token repeats > 2.

   **Policy:** accept **Flint OR Generic** (recommended for surveying lanes).

   The **Generic** track uses the included calibration assets:
   - `examples/calibration/calib_97_perplexity.json` (97-char perplexity summary)  
   - `examples/calibration/pos_trigrams.json` (POS trigrams)  
   - `examples/calibration/pos_threshold.txt` (threshold T)

3) **Nulls (10,000 mirrored trials)** — significance  
   Mirror the exact T₂ route + repeating-key class schedule; randomize only **free residues**.  
   Compute one-sided p for {coverage, f-words}, apply **Holm m = 2**.  
   **Publish only if Holm adj-p < 0.01.**

> The CLI validates rails, renders spacing from a ledger, and bundles your audit files. It does not perform cryptanalysis or generate nulls.

---

## Provenance: why Abel Flint matters (tail-first → plaza → method)

I decrypted the tail — `… OF AN ANGLE IS THE ARC` — which is the textbook rule for reading a surveying circle. That led to Abel Flint and to treating the plaza like a 19th-century surveying plate: **read a direction as an arc**, then do what field books prescribe:

- **Circle and arcs** → *the measure of an angle is the arc*.  
- **"EAST NORTHEAST"** → a bearing sector (stand on the meridian; take the arc into ENE).  
- **From bearing to coordinates** → rectangular surveying: ΔN = d·cos(θ_true), ΔE = d·sin(θ_true).  
- **Correct the needle** → account for **declination** (and local attraction) before trusting the bearing.  
- **If you can't go straight** → offsets & intersections; reduce back to the meridian.

Because that tail is literal textbook language, we lock it and require every candidate to keep it byte-exact.

See `docs/ABEL_FLINT.md` for a compact mapping.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Rails verification (anchors, head lock, seam)
python cli.py verify \
  --pt examples/plaintext_97.txt \
  --ct examples/ciphertext_97.txt \
  --anchors examples/anchors_ledger.csv \
  --seam examples/seam_guard_proof.json \
  --expect-p74 T

# Render a readable line from a fixed ledger (0-idx inclusive end-cuts)
python cli.py render \
  --pt examples/plaintext_97.txt \
  --ledger examples/spacing_ledger.json \
  --out readable.txt

# Show calibration pins (top-5% perplexity cutoff and POS threshold)
python cli.py calib show \
  --perp examples/calibration/calib_97_perplexity.json \
  --pos examples/calibration/pos_trigrams.json \
  --th examples/calibration/pos_threshold.txt

# Create an audit bundle (zips files + hashes + your reports)
python cli.py bundle \
  --pt examples/plaintext_97.txt \
  --ct examples/ciphertext_97.txt \
  --proof examples/proof_digest.json \
  --anchors examples/anchors_ledger.csv \
  --seam examples/seam_guard_proof.json \
  --near examples/near_gate_report.json \
  --phrase examples/phrase_gate_report.json \
  --holm examples/holm_report_canonical.json \
  --out ./dist/k4_audit_bundle
```

## Files of interest (examples included)

* `examples/ciphertext_97.txt` — canonical K4 CT (sha `eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab`)
* `examples/anchors_ledger.csv` — `EAST 21–24`, `NORTHEAST 25–33`, `BERLINCLOCK 63–73`
* `examples/seam_guard_proof.json` — tail guard with dotted seam `[81,83,88,90,93]`
* `examples/plaintext_97.txt` — sample PT (sha `09c85ebcd840d8f8847bebe16888208a7bf56bba0d60d6f57dbd139772a20217`)
* `examples/calibration/*` — Hermes's phrase-gate calibration files (perplexity, POS threshold, POS trigrams)

## Security

No internal names or codenames; this repo focuses on **rails, process, and provenance**.
Hash everything, record `hashes.txt`, and ship a top-level `coverage_report.json` in every bundle.

License: MIT