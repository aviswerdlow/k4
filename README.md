# **K4 — Pencil-and-Paper Decrypt (1989-friendly)**

**and**

# **Modern, Audited Reproduction**

This README has two jobs:

1. teach a careful 1989 cryptanalyst exactly how to **decrypt the whole K4 line by hand** (no computers, no seam/tail guard), and

2. show how this repository mirrors the same method with **hash-pinned, schema-validated** artifacts you can verify in minutes.

---

## **Part 1 —** 

## **REPRODUCE & VERIFY (paper-only, 1989-friendly)**

**Goal.** Decrypt the **entire** 97-letter line on *Kryptos* panel K4 with paper & pencil. You will use only:

* the engraved **ciphertext** (97 letters A..Z),

* the four **anchors as plaintext at fixed indices** (public confirmations),

* a short **six-track repeating-key** skeleton, and

* ordinary **mod-26** algebra (Vigenère / Beaufort / Variant-Beaufort).

**No seam/tail guard.** The tail is **derived by propagation**, not assumed.

### **Tools & notation**

* Graph paper, pencil, eraser, alphabet strip.

* Numbers: **A=0, …, Z=25** (all work **mod-26**).

* Three family rules (decrypt direction):

  * **Vigenère**: P \= C − K

  * **Beaufort**: P \= K − C

  * **Variant-Beaufort**: P \= C \+ K

* **Option-A at anchors:** for additive families (Vig / Var-Bf) **forbid K=0** (no pass-through). If K=0 at an anchor, you picked the wrong family for that class — flip family and recompute.

---

### **A. Ciphertext & rails (what you write first)**

1. Copy the 97-letter ciphertext and index positions **0..96** left→right.

2. Mark **four** plaintext anchors (0-indexed, inclusive ends):

   * EAST **21–24**

   * NORTHEAST **25–33**

   * BERLIN **63–68**

   * CLOCK **69–73**

3. Nothing else is assumed (especially not the tail).

---

### **B. Six-track skeleton (class every index)**

Treat K4 as six interleaved short keys (classes **0..5**):

class(i) \= ((i % 2\) \* 3\) \+ (i % 3\)

Draw six short rows labeled 0..5. For each index **i** (0..96) drop **i** into its class row. Box the indices that lie inside the four anchor spans.

---

### **C. Force residues at anchors (Option-A)**

At each anchor index **i** you know **C(i)** (cipher) and **P(i)** (anchor word). For that class’s family, solve **K** in **mod-26** (see rules above). Enforce:

* **No K=0** in additive families at anchors (Option-A).

* No residue collisions at the **same wheel slot** inside a class; if a collision appears, you chose the wrong family — flip and recompute.

This pins **specific residues K** into **specific wheel slots** for each class.

---

### **D. Set the period wheels (short** 

### **L**

### **, with phase)**

Each class is a short repeating key of period **L** (typically **10..22**) and **phase** (which wheel slot index 0 maps to). Choose **L, phase** per class so that all its anchored indices land on **distinct slots** (no collisions). Draw a small wheel per class and pencil the forced residues into the correct slots.

You now have a complete **decrypt engine**: six short wheels, residues pinned at some slots, families fixed.

---

### **E. Optional head spot-checks**

Pick a few indices in **0..74** outside anchors. For each index **i**:

1. compute the class, 2\) find the wheel slot for **i**, 3\) read **K**, 4\) apply the class decrypt rule to **C(i)** → **P(i)**. You’ll see plain English accumulating.

---

### **E′.** 

### **Derive the tail by propagation (no guard)**

Apply the six wheels to **indices 75..96** exactly the same way:

1. class(i) \= ((i % 2)\*3) \+ (i % 3\)

2. slot s \= (i − phase) % L in that class

3. read residue **K** at slot **s**

4. apply that class’s decrypt rule to **C(i)** and **K** → **P(i)**

5. map number→letter (A=0..Z=25) and write **P(i)** at index **i**

Going across the span, the phrase appears:

HEJOY · OF · AN · ANGLE · IS · THE · ARC

It falls out **purely** from the anchor-forced wheels. **No seam/tail guard** is used or needed.

---

### **F. Pencil re-encryption (quick completeness check)**

For any decrypted span, apply the **encrypt** direction of each family with the same residues to get back **C(i)**. If you want monument display parity, apply the **route** permutation **after** decryption to shuffle **non-anchors** into display order. (Route is not used to obtain the tail.)

---

### **G. Why the tail matters (Abel Flint & the plaza)**

**Abel Flint** (19th-century surveying manuals) states:

“**The measure of an angle is the arc** cut off from a circle by the two rays whose vertex is the center.”

The Langley yard presents a **surveying circle**. The tail instructs you to **read an arc** (direction on the circle), **correct to true** with **declination**, then **reduce to rectangulars**:

ΔN \= d · cos(θ\_true)   ,   ΔE \= d · sin(θ\_true)

A printable K5 worksheet (world-clock traverse) is included in the docs.

---

### **H. Optional vs non-optional**

* **Optional:** the last-stage **route** permutation (display order only).

* **Non-optional:** anchors → six short wheels → family rules → cell-by-cell propagation. That’s what **produces** the plaintext.

---

### **Full plaintext (for hand check)**

**Letters-only (97)**

WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCKTHEJOYOFANANGLEISTHEARC

**Spaced with anchors marked**

WE ARE IN THE GRID SEE THEN \[EAST\] \[NORTHEAST\] AND WE ARE BY THE LINE TO SEE BETWEEN \[BERLIN\] \[CLOCK\] THE JOY OF AN ANGLE IS THE ARC

---

## **Part 2 —** 

## **Modern, audited reproduction**

##  **(hash-pinned)**

Everything above can be done on paper. The repo mirrors the same logic with **receipts, schemas, and CI** so anyone can re-run the checks.

### **What’s published (winner bundle)**

* **Spaced head (publishing view)**

   WE ARE IN THE GRID SEE THEN EAST NORTHEAST AND WE ARE BY THE LINE TO SEE BETWEEN BERLINCLOCK

* **Letters-only PT (97) including tail**

   WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCKTHEJOYOFANANGLEISTHEARC

**Receipts**

* **PT SHA-256 (bundle \= derived):** 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79

* **T₂ SHA-256 (GRID\_W14\_ROWS.json):** a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31

* **Pre-registration commit:** d0b03f4

* **Policy pack SHA:** bc083cc4129fedbc

**Bundle path** → 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/

Contains:

* plaintext\_97.txt — 97 letters (anchors fixed at 21–24, 25–33, 63–73)

* proof\_digest.json & proof\_digest\_enhanced.json — six class wheels (**family/L/phase**) with **forced anchor residues**; class\_formula: "((i%2)\*3)+(i%3)"; Option-A enforced

* coverage\_report.json — encrypts\_to\_ct:true; pt\_sha256\_bundle \== pt\_sha256\_derived; tail\_derivation\_verified:true; gates\_head\_only:true; no\_tail\_guard:true

* phrase\_gate\_policy.json — AND policy; padding\_forbidden:true; boundary\_tokenizer:"v2"; filler\_mode:"lexicon"

* phrase\_gate\_report.json — Flint v2 & Generic with cadence/context sections

* holm\_report\_canonical.json — **10k mirrored nulls**, Holm m=2 for {coverage, f-words} (both adj-p \< 0.01)

* tokenization\_report.json — boundary splits documented; lexicon fillers (“THEN”, “BETWEEN”) noted; function-word counts per gap

* hashes.txt, MANIFEST.sha256, RECEIPTS.json

---

### **Core-Hardening Studies**

We ran three adversarial studies to test the algebraic robustness of the cipher core:

* **Skeleton uniqueness**: 24 alternative periodic classing schemes tested; **only the baseline** six-track `class(i)=((i%2)*3)+(i%3)` re-derives the 97-char plaintext from CT under the four anchors (**1/24 feasible**; [proof](04_EXPERIMENTS/core_hardening/skeleton_survey/PROOFS/skeleton_S0_BASELINE.json) included). → [Results](04_EXPERIMENTS/core_hardening/skeleton_survey/RESULTS.csv) | [Analysis](04_EXPERIMENTS/core_hardening/skeleton_survey/README.md)

* **Tail necessity**: 550 single-letter tail mutations tested (22 positions × 25 letters); **0/550 feasible**—tail is algebraically locked, not assumed. → [Results](04_EXPERIMENTS/core_hardening/tail_necessity/RESULTS.csv) | [Analysis](04_EXPERIMENTS/core_hardening/tail_necessity/README.md)

* **Anchor exactness**: ±1 index shifts and BERLIN/CLOCK split/combined modes tested (27 cases); **0/27 feasible** under the same CT→PT solve—anchors are exact. → [Results](04_EXPERIMENTS/core_hardening/anchor_perturbations/RESULTS.csv) | [Analysis](04_EXPERIMENTS/core_hardening/anchor_perturbations/README.md)

**Claim map**: CT + four anchors + six-track classing → wheels (Option-A) → PT97; route (T₂) for display only.

**How to re-run**:
```bash
make core-harden           # all three studies
make core-harden-skeletons # study A
make core-harden-tail      # study B
make core-harden-anchors   # study C
make core-harden-validate  # validate results
```

See [04_EXPERIMENTS/core_hardening/](04_EXPERIMENTS/core_hardening/) for full details.

---

**Immutable inputs** → 02\_DATA/

* ciphertext\_97.txt (CT SHA-256 eea81357…a515ceab)

* permutations/GRID\_W14\_ROWS.json (T₂ SHA above; NA-only; anchors map to self)

* constraints/canonical\_cuts.json , constraints/function\_words.txt

* calibration/\* (perplexity/POS tables; all hash-pinned)

**Solvers that reflect the hand method** → 03\_SOLVERS/

* build the **same six wheels** you drew on paper (anchors → residues → short **L** → phase → family rules)

* apply the **route** only for display parity

* **boundary tokenizer v2** is presentation-layer only (spaced head), never changes the 97-letter line

---

### **Quick verify (modern)**

k4 confirm \\

  \--ct 02\_DATA/ciphertext\_97.txt \\

  \--pt 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/plaintext\_97.txt \\

  \--proof 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/proof\_digest\_enhanced.json \\

  \--perm 02\_DATA/permutations/GRID\_W14\_ROWS.json \\

  \--cuts 02\_DATA/constraints/canonical\_cuts.json \\

  \--fwords 02\_DATA/constraints/function\_words.txt \\

  \--policy 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/phrase\_gate\_policy.json \\

  \--out /tmp/k4\_verify\_HEAD\_0020\_v522B

### **Derivation parity check (tail is derived, not assumed)**

python3 07\_TOOLS/validation/rederive\_plaintext.py \\

  \--ct 02\_DATA/ciphertext\_97.txt \\

  \--proof 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/proof\_digest\_enhanced.json \\

  \--out /tmp/derived\_pt\_97.txt

shasum \-a 256 \\

  /tmp/derived\_pt\_97.txt \\

  01\_PUBLISHED/winner\_HEAD\_0020\_v522B/plaintext\_97.txt

\# \-\> 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79 (both)

---

## **Notes on scope**

* **Tail (“OF AN ANGLE IS THE ARC”).** We *derived* it cell-by-cell from anchor-forced wheels; we then recognized its meaning in **Abel Flint**. Seam-free runs under the same rails replicate the tail across route families and heads. We present this as **empirical** under the rails, not a universal proof.

* **Anchors-only algebra.** Single-key Vigenère family is infeasible (collisions); six-track is feasible but anchors alone don’t fix all tail residues. The tail invariance emerges when **anchors \+ NA-only permutation \+ Option-A \+ multi-class keys \+ head-only gates** act together.

* **P\[74\].** All 26 letters are lawful under the same rails; the null model does not distinguish — the “T” in **THE JOY** is an editorial pre-seam choice.

---

## **Licenses, receipts, and contact**

This repo documents a claim **within a stated frame**; please cite the frame, **pre-reg commit** d0b03f4, **policy SHA** bc083cc4129fedbc, and the **T₂ SHA** a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31.

* Winner PT SHA-256: 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79 (bundle \= derived).

* See 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/RECEIPTS.json for consolidated receipts.

**Repository:** https://github.com/aviswerdlow/k4

**Solution date:** September 2025

**Method:** Anchors → six short tracks (Option-A) → cell-by-cell propagation (tail derived) → route for display parity → modern audited replay (hashes, schemas, CI)
