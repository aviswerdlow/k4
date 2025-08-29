
# K4 Endgame Cryptography — Addendum to *Mathematical Spec*

**Author:** Junior  
**Purpose:** Formal, testable hypotheses for how the traverse outputs (ΔN, ΔE, r) are used as a *cryptographic key* to complete K4.

---

## 0) Known quantitative outputs from the Master Algorithm

- Net latitude (ΔN) = **2.370756** rods  
- Net departure (ΔE) = **4.402217** rods  
- Distance **r** = √(ΔN²+ΔE²) = **5.000000** rods  
- Bearing (true, quadrantal) **N 61.6959° E**  

These are strict consequences of the Survey Traverse Algorithm applied to the certified plaintext and the Explorer’s rotation key (+16.6959°).

---

## 1) Operating constraints (from the Unified Model)

- 28‑tick clock; 90° = 7 ticks; quadrant boundaries therefore sit at ticks 0,7,14,21 (± phase after applying the +16.6959° rotation).  
- Sparse “process overlays” act as micro‑keys atop the Δ(t) backbone. Empirically, the **first pass** is a cluster of ±7 flips (the “meridian‑flip comb”); the **second pass** contains small interior nudges {±1, ±2, ±3, ±4, ±6}.  
- Two passes produce the verified seam **…OF AN ANGLE IS THE ARC** in the tail window [80..96].

These facts constrain what a viable endgame key may do: it must deterministically regenerate a short sequence of heavy ±7s and a short sequence of smaller interior steps, aligned to rotated quadrant crossings.

---

## 2) Primary Proposal — **NE→Two‑Pass Micro‑Key Generator**

Use the traverse outputs themselves as the *seed material* that generates the two passes of the micro‑key, independent of any ad hoc choices.

### 2.1 Pre‑processing (deterministic, pencil‑and‑paper)
- Write ΔN and ΔE to 6 fractional digits:  
  N = 2.**370756**, E = 4.**402217**.  
- Drop decimal points and interleave starting with **N** → digit stream **D** of length 14:  
  D = (2,4,3,4,7,0,0,2,7,2,5,1,6,7).  
- Compute the **phase tick** of the closing course (true):  
  φ = atan2(E, N) = 61.6959°; map to ticks:  
  τ = 28·φ/360 ≈ **4.79857** ticks.  
- Global rotation (Explorer): α = +16.6959° → α\_ticks = 28·α/360 ≈ **1.29859** ticks.

### 2.2 Pass‑1 (±7 comb = “meridian‑flip” layer)
- **Amplitude map A₁(d):** {0→0, 1→0, 2→0, 3→0, 4→0, 5→6, 6→7, 7→7, 8→6, 9→4}.  
  *(Rationale: large values only when a digit is ≥6; matches the observed ±7 palette.)*
- **Sign gate S₁(t):** `sign(sin(2π·((t − τ − α_ticks)/7)))`.  
  *(Rationale: sign toggles at rotated quadrant lines; this reproduces the “flip on boundary crossing” behavior of the meridian‑flip rule.)*
- **Emission:** repeat D until the gated window length **L** (e.g., L=22 for the tail) is filled, map each digit through A₁, then apply ± via S₁ to get a length‑L integer sequence with magnitudes in {0,6,7}.

### 2.3 Pass‑2 (contained‑angle layer)
- **Amplitude map A₂(d):** {0→0, 1→1, 2→2, 3→3, 4→4, 5→6, 6→2, 7→1, 8→4, 9→3}.  
  *(Rationale: small interior trims distributed across 0..6, with symmetry.)*
- **Operator selector O(d):** { (0,2,4,8) → **add courses**, (1,3,9) → **subtract sum from 180°**, (5) → **co‑function swap**, (6,7) → **supplement‑of‑greater** }.  
  *(Rationale: ties digits to the book’s four contained‑angle prescriptions.)*
- **Sign gate S₂(t):** `sign(cos(2π·((t − τ − α_ticks)/7)))` (quadrature to S₁ so the small nudges tend to land *between* the heavy ±7s).  
- **Emission:** repeat D to length L; map through A₂ and S₂ (and apply the chosen operator O at that index when interpreting the shift as a rule, not just a number).

> **Acceptance test (tail window):** With L=22, gate start=80, radius r=7, quarters (15,30,45), Pass‑1 + Pass‑2 must match the recorded two‑pass solution bit‑for‑bit in the HEJOY→OF AN ANGLE IS THE ARC seam.  

### 2.4 Why this is faithful to the book
- **Phase and boundaries** come from the course itself (φ) and the declination correction (α).  
- **Heavy vs. light edits** correspond to **meridian flip** (signing change) vs. **contained‑angle rules** (add/subtract/supplement), exactly mirroring Flint & Gillet’s control‑flow.  
- **Digit use** is strictly mechanical and pencil‑and‑paper: write the numbers, interleave, threshold by magnitude, and read off signs from a simple sine/cosine gate in tick‑space.

---

## 3) Secondary, quick‑to‑test models (keep if Pass‑1/2 ever fails)

### B) **Vigenère‑style running key from digits**
- Key stream K from the 14‑digit D (interleaved N/E) mapped mod 26 by `k = d (0..9) → (0,1,2,3,4,6,7,7,6,4)`.  
- Apply keyed Caesar at the **opportunity windows** only (per the rule engine), not globally.  
- Expectation: reproduces the same sparse corrections; reject if it spills good anchors.

### C) **5×5 Polybius control word**
- Use r = **5.0000** to select a 5×5 Polybius square; seed the order by sorting the 14‑digit D; use square to encode two‑letter edits (“IN/AT/OF/IS”) at flagged windows.  
- Expectation: fast wins on short function words only; if it outperforms random at windows with high route score, keep as a fallback micro‑operator.

### D) **Index‑into‑source‑text**
- Treat 2370756/4402217 as page/line/word indices in Flint & Gillet; harvest the *first letters* as tiny keys applied only where the route engine allows.  
- Expectation: probably weaker than A, but trivial to falsify.

---

## 4) The “5.0000” constraint (why the five matters)

- **Geometry meaning:** with ΔN/5 = cos φ and ΔE/5 = sin φ, the decimals (0.474151, 0.880443) are the unit circle coordinates of the *closing* course.  
- **Cryptography meaning:** **5** partitions both digits into 6‑tuples and naturally yields a 14‑digit stream when interleaved; it also licenses Polybius‑style 5×5 operations for two‑letter fixes.  
- **Operational use:** in §2 above, **5** is the normalizing radius that makes the gating purely angular (phase) and the digit pool stable across units.

---

## 5) Minimal pseudocode (sufficient for The Architect)

```text
# Inputs: N=2.370756, E=4.402217, alpha_deg=16.6959, L, start, gate
D = interleave(digits("2370756"), digits("4402217"))   # length 14
tau = 28*(atan2(E,N)*180/pi)/360
alpha_ticks = 28*alpha_deg/360

# Pass 1 amplitudes
A1 = {0:0,1:0,2:0,3:0,4:0,5:6,6:7,7:7,8:6,9:4}
S1(t) = sign(sin(2*pi*((t - tau - alpha_ticks)/7)))

# Pass 2 amplitudes
A2 = {0:0,1:1,2:2,3:3,4:4,5:6,6:2,7:1,8:4,9:3}
S2(t) = sign(cos(2*pi*((t - tau - alpha_ticks)/7)))

emit(seq, A, S):
  out = []
  for t in 0..L-1:
    d = D[t mod 14]
    out.append(S(t) * A[d])
  return out

seq1 = emit(D, A1, S1)   # ±7 comb
seq2 = emit(D, A2, S2)   # interior trims
```

Implement the two sequences only inside the route‑gated windows. Reject the model if it alters anchors or fails to equal the recorded two‑pass in the tail.

---

## 6) Test Plan

1. **Tail replication:** Use L=22, start=80, r=7; confirm seq1/seq2 reproduce the canonical HEJOY→OF AN ANGLE IS THE ARC seam exactly.  
2. **LINK@36–39:** Apply the same generator; accept only if it produces the exact two‑letter fix without collateral damage.  
3. **Opportunity map (35 new targets):** run Pass‑1/2 at each and record win‑loss. A single rule family winning across multiple windows with no anchor damage is sufficient to elevate this to the canonical endgame mechanism.

---

## 7) What to hand The Architect

- This document + the exact pseudocode above are enough to wire a “NE→two‑pass” module into the decryptor.  
- If Model A fails any of the checks, fall back to Models B/C for those specific windows, but keep Model A as the default.

---

*Prepared for immediate implementation and falsification.*
