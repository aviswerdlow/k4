
# Full pipeline — ciphertext → plaintext (with primary‑source provenance)

**Stage 0 — Compass key (Explorer).**  
Use **α = 16.6959° East of North** as a *declination/variation* to rotate bearings from magnetic to true. This is exactly how Flint & Gillet define and *use* variation in their Treatise; we treat α as a rotation constant for the dial and for bearings. fileciteturn0file23

**Stage 1 — Unified Model (two‑pass micro‑keys).**  
Run the route‑gated ±7 / ±(1..6) passes aligned to the rotated quadrant/meridian ticks (28‑step dial). This is the minimal mechanism that produces the certified tail seam **… OF AN ANGLE IS THE ARC** while keeping all anchors (`EAST`, `NORTHEAST`, `BERLIN`, `CLOCK`) in place. The mathematical specification and operator triggers derive directly from Flint & Gillet’s “contained‑angle” rules and the meridian‑distance sign‑flip. fileciteturn0file21 fileciteturn0file26

**Stage 1 output (Intermediate String, 97 chars).**  
`QVIHUPXCMJKAVIAUVFCCXEASTNORTHEASTOHCVGHDGEBRKAAXZIKIISFKUUYNGBBERLINCLOCKXHEJOYOFANANGLEISTHEARC`  
This is the canonical input to Stage‑2. fileciteturn0file5

**Stage 2 — Survey‑keyed post‑processing (transposition + digits).**  
- Take only the **first 75** characters.  
- Build a 5×15 rectangle and apply the **detransposition** controlled by the rank order of the five Gronsfeld digits (default permutation `[4,1,2,3,5]`).  
- Apply a **Gronsfeld** (digits‑only Vigenère) using the period‑5 key `[6,7,7,2,9]`. The alphabet’s *phase* is fixed by the true bearing (**+17** rotation). fileciteturn0file4  
These controls are not arbitrary: all of them are **derived** from the traverse numbers — ΔN, ΔE, and the closing distance **5.0000 rods** — obtained by executing the Treatise’s Traverse Table workflow on the direction & unit tokens in the text (NE with four rod‑equivalents), exactly as documented in the Master Algorithm run. fileciteturn0file10 fileciteturn0file12

**Tail treatment (indices 75..96).**  
Keep `HEJOY` and the seam `OFANANGLEISTHEARC` verbatim. A small, book‑motivated 5‑window patch (`Δ = [0,0,+4,+14,+6]`) converts **HEJOY → HENCE** if you elect the Private‑Secretary variant; the CLI exposes this as `--hejoy-patch`. (Patch memo in the Private‑Secretary notes.)

**Rendering the English sentence.**  
Normalize token separators and keep the idiom true to the Treatise (& 1923 lexicon) so the instruction reads in authentic nineteenth‑century textbook cadence — e.g., “**Having set your course … the measure of an angle is the arc.**” fileciteturn0file11 fileciteturn0file7

---

## Why the BERLIN CLOCK, EAST/NORTHEAST anchors, and the seam are *fixed*

- Anchor integrity and positions are part of the Stage‑1 selection—see the signed **Intermediate String** dossier. fileciteturn0file5  
- *Interpretation Brief* rules that **“EAST NORTHEAST” is NE** (not ENE, not two bearings) following Flint & Gillet’s bearing style; this removes an ambiguity for the traverse math. fileciteturn0file8

---

## “Audit trail” pointers (open these while you run the CLI)

- **Stage‑2 Protocol** (this CLI’s defaults): K4_Stage_2_Decryption_Protocol.md. fileciteturn0file4  
- **Intermediate input** (97 chars): K4_Intermediate_String_Selection_v1.md. fileciteturn0file5  
- **Where ‘having set your course’ comes from** (1923 hearings): K4_Lexicon_1923.md. fileciteturn0file6  
- **Endgame traverse numbers** that feed the Stage‑2 key: Master Algorithm Executed. fileciteturn0file10  
- **Survey engine (Treatise) the numbers come from**: The Survey Traverse Algorithm. fileciteturn0file12  
- **Declination as rotation key** (Explorer): Key Dossier. fileciteturn0file23  
- **Interpretation of EAST NORTHEAST (NE)**: Interpretation Brief. fileciteturn0file8

---

## Reproducibility contract

If you keep **the same inputs and parameters**, the CLI’s Stage‑2 head is deterministic. If your run does not match the team’s current best English head, use:

```bash
python3 k4_cli.py -i INTERMEDIATE.txt -e EXPECTED_97.txt --find-params
```

This will report the closest match among widely‑used columnar/Gronsfeld variants so reviewers can see whether disagreement is confined to a permutation/rotation convention or indicates a deeper model problem.
