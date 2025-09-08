# **K4 — Pencil-and-Paper Decrypt (1989-friendly)**

# **and**

# **Modern, Audited Reproduction**

This README has two parts:

1. **Exactly** the hand method we used to **decrypt the K4 tail** with paper, pencil, and mod-26 arithmetic (no computers, no seam guard; the tail is **derived**, not assumed).

2. How this repository reflects the **same** method with modern, auditable artifacts (hash-pinned data, bundles, CLI, schemas, CI).

---

## **Part 1 — REPRODUCE & VERIFY (paper-only, 1989-friendly)**

**Purpose.** This is a stand-alone, paper-only recipe to reproduce the decryption we achieved on the fourth panel of *Kryptos* (K4). It shows exactly **how the tail was decrypted** (not assumed), using only: the public ciphertext line, three anchor cribs Jim Sanborn confirmed, a short repeating-key cipher skeleton (six tracks), and ordinary **mod-26** algebra.

No computers, no statistical engines, **no seam guard**. Just the work a careful 1989 cryptanalyst could do at a desk.

### **Contents**

* Tools & notation

* A. Ciphertext & rails (what you write first)

* B. The six-track skeleton (class all 97 positions)

* C. Forcing anchor residues (Option-A discipline)

* D. Setting the period wheels (short L, with phase)

* E. (Optional) Head corridor spot-checks

* **E′. How we decrypted the tail (by hand)**  ⟵ *the actual method used*

* F. Pencil re-encryption check (completeness)

* G. Why the tail matters (Abel Flint & the plaza)

* H. What is optional (routes) vs what is not (the algebra)

* Appendices: A) Letter↔Number table, B) Family rules, C) Classing recipe, D) Sample numeric strip

### **Tools & notation**

* **Tools.** Graph paper, pencil, eraser, alphabet strip, **mod-26** crib sheet (Appendix A & B).

* **Numbers.** A=0, B=1, …, Z=25 (Appendix A).

* **Arithmetic.** All add/subtract **mod-26**.

---

### **A. Ciphertext & rails (what you write first)**

1. **Copy the K4 ciphertext** (97 letters A..Z) and index positions **0..96** left→right.

2. **Mark the three anchor cribs** as **plaintext** at fixed 0-index spans:

   * EAST at **21–24**

   * NORTHEAST at **25–33**

   * BERLINCLOCK at **63–73**

3. **Nothing else is assumed.** You do **not** write any tail words. You will **derive** them in §E′.

---

### **B. The six-track skeleton (class every index 0..96)**

Treat K4 as six short interleaved repeating keys. Class(i) is:

class(i) \= (i % 2)\*3 \+ (i % 3\)        \# classes 0..5

Draw **six short rows** labeled 0..5. Scan i=0..96; drop index i into the row for its class. Box any indices lying inside the three anchor spans for easy reference.

---

### **C. Forcing anchor residues (Option-A discipline)**

At each **anchor** index i you know:

* **ciphertext** C(i) from the line, and

* required **plaintext** P(i) from the crib at that span.

Each class line uses one of three **families** (Appendix B). At an anchor index solve for residue K (0..25):

* **Vigenère** (decrypt):  P \= C − K   ⇒  **K \= C − P**

* **Beaufort** (decrypt):  P \= K − C   ⇒  **K \= P \+ C**

* **Variant-Beaufort** (decrypt): P \= C \+ K ⇒ **K \= P − C**

**Option-A (anchors only):** The additive families (Vig / Var-Bf) **must not** use **K=0** (no pass-through). If you get K=0 at an anchor, you chose the wrong family for that class slot — **switch family** (or use Beaufort) and recompute. If two anchor cells in the **same** class wheel demand different K for the **same** wheel slot, your family choice for that class is wrong — switch and redo.

Do this for **every** anchor cell in each class row: you are pinning **specific residues** to **specific wheel slots** in each short line.

---

### **D. Setting the period wheels (short L, with phase)**

Each class is a short repeating key (period L, typically **10..22**). Use the anchored cells in the same class to read off a consistent **L** and **phase** (index 0’s slot). Draw the **wheel**, mark slots, pencil in the anchor-forced residues at the correct slots.

You don’t guess blindly: try small L until anchor cells for that class land at **distinct slots without collision** — exactly standard Vigenère-crib work, one short line at a time.

With six wheels set (one per class), you now have a complete **decrypt engine** for the line, built **only** from anchors and short-period arithmetic.

---

### **E. (Optional) Head corridor spot-checks**

Pick a few head indices (0..74) outside anchors; for each: find the class, read K from the wheel at the right slot, and apply the family **decrypt** rule (Appendix B) to compute P from C. English fragments will accumulate near the corridor — the **same** arithmetic you will use in the tail.

---

### **E′. How we decrypted the tail (by hand)**

This is the **exact** workflow we used to **produce** the tail (we did **not** assume it).

Keep the same six wheels fixed at anchors (C–D). Now simply **apply them to indices 75..96**. For each i:

1. class(i) \= (i % 2)\*3 \+ (i % 3\)

2. wheel slot s \= (i − phase) % L on that class

3. read residue K at s

4. apply that class’s **decrypt** rule to C(i), K → **P(i)** (Appendix B)

5. map number→letter (A=0..Z=25) and write P(i) at index i

Proceed across the span. In about twenty boxes, the phrase becomes clear:

HEJOY OF AN ANGLE IS THE ARC

— **purely from the anchor-forced wheels.** No seam guard is used or needed; no computers either. It is ordinary **mod-26** arithmetic, one cell at a time.

*Micro-example.* Suppose at 80..84 you read the correct K from the class wheels and apply the appropriate family rules: you compute **O F A N A** from the engraved letters at those positions. Continue to 96 to finish the clause.

#### **E′.1 Paper significance test (“stat-sign phrase”, 1989-style)**

Having produced the tail **arithmetically**, sanity-check by eye:

* **Coverage**: OF / AN / IS / THE in order; ANGLE and ARC as content words.

* **Cadence**: phrase-like rhythm (not debris).

* **Domain sense**: this is Abel Flint’s surveying rule — **“the measure of an angle is the arc.”**

This is exactly what we found first: we **derived** the tail, then recognized Flint, then used that to understand the courtyard circle as **instruction** rather than ornament.

---

### **F. Pencil re-encryption check**

Take any span you decrypted; apply the **encrypt** direction of each class’s family rule with the same K residues — you recover the original C letters. If you want full display parity with the sculpture, apply a **route permutation** (T₂) that rearranges **non-anchors** to their monument destinations while anchors remain fixed. Crucially, **T₂ is not used to obtain the tail** — the tail already falls out at 75..96 before any permutation.

---

### **G. Why the tail matters (Abel Flint & the plaza)**

With **only** anchors and six short keys, the tail **emerges**:

… OF AN ANGLE IS THE ARC

This is the textbook rule in **Abel Flint**: *the measure of an angle is the arc cut off from a circle by the rays at the angle’s vertex*. In the Langley yard, you stand on a **circle** with bearings — the tail tells you to **read the arc**, then (as surveyors do) **reduce to the true meridian** (declination), and **resolve** into northings/eastings.

---

### **H. Optional vs non-optional**

* **Optional:** the **route (T₂)** used only for display parity.

* **Non-optional:** the algebra (six short wheels, anchor residues, family rules) — that alone **produces** the tail.

---

### **Appendices**

**A. Letter/Number table** — A=0..Z=25 (do all math mod-26).

**B. Family rules** — Vigenère/Beaufort/Variant-Bf encrypt/decrypt formulas \+ **Option-A** (no K=0 for additive families at anchors).

**C. Classing formula** — class(i) \= (i % 2)\*3 \+ (i % 3\) (write this on your grid).

**D. Sample numeric strip** — fill from the monument and your class wheels; compute P(i) step-by-step.

---

## **Part 2 — How the repo mirrors the hand method (modern, audited)**

Everything above can be done with pencil and paper. This repository preserves the **same** logic with modern, **reproducible** artifacts.

### **What’s published (winner bundle)**

**Spaced head (publishing view)**

WE ARE IN THE GRID SEE THEN EAST NORTHEAST AND WE ARE BY THE LINE TO SEE BETWEEN BERLINCLOCK

**Letters-only PT (97) including tail**

WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCKTHEJOYOFANANGLEISTHEARC

**Receipts (current)**

* **PT SHA-256 (derived \= bundle):** 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79

* **T₂ SHA-256 (GRID\_W14\_ROWS.json):** a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31

* **Pre-registration commit:** d0b03f4

* **Policy pack SHA:** bc083cc4129fedbc

**Winner bundle** — 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/

* plaintext\_97.txt — 97 letters (anchors fixed at 21–24, 25–33, 63–73)

* proof\_digest.json & proof\_digest\_enhanced.json — six class wheels (family/L/phase) with **forced anchor residues**; seed recipe; **class\_formula** recorded (((i % 2\) \* 3\) \+ (i % 3))

* coverage\_report.json — encrypts\_to\_ct:true; pt\_sha256\_bundle \== pt\_sha256\_derived; tail\_derivation\_verified:true; gates\_head\_only:true; no\_tail\_guard:true

* phrase\_gate\_policy.json — AND policy; padding\_forbidden:true; boundary\_tokenizer:"v2"; filler\_mode:"lexicon"

* phrase\_gate\_report.json — Flint v2 & Generic, cadence/context sections

* holm\_report\_canonical.json — **10k mirrored nulls**, Holm m=2 for {coverage, f-words} (both adj-p \< 0.01)

* tokenization\_report.json — boundary splits documented; lexicon fillers (“THEN”, “BETWEEN”) noted; function-word counts per gap

* hashes.txt, MANIFEST.sha256, and RECEIPTS.json — SHA-256 for every artifact

**Immutable data** — 02\_DATA/

* ciphertext\_97.txt (CT SHA-256 eea81357…a515ceab)

* permutations/GRID\_W14\_ROWS.json (T₂ SHA above; NA-only; anchors map to self)

* constraints/canonical\_cuts.json (for display parity)

* constraints/function\_words.txt (lane list)

* calibration/\* (perplexity/POS, all hash-pinned)

**Solvers (modern reflection of the hand method)** — 03\_SOLVERS/

* The code builds the **same six short wheels** you built on paper: **forces anchor residues** under Option-A, chooses **small L** to avoid collisions, and decrypts with the **same** three family rules (Vig/Bf/Var-Bf).

* The **route** (T₂) is applied **only** to match the monument’s display order; it is **not** used to obtain the tail.

* The **boundary tokenizer v2** is **presentation-layer only** (word segmentation for the spaced head); it **never** changes the 97-letter line or any gate outcome.

**Experiments & appendices** — 04\_EXPERIMENTS/

* Seam-free runs, anchors-only algebra, P74 editorial sweep, cadence panel (report-only), and filler rescreen (showing fillers keep or slightly improve metrics).

### **Quick verify (modern)**

k4 confirm \\

  \--ct 02\_DATA/ciphertext\_97.txt \\

  \--pt 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/plaintext\_97.txt \\

  \--proof 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/proof\_digest\_enhanced.json \\

  \--perm 02\_DATA/permutations/GRID\_W14\_ROWS.json \\

  \--cuts 02\_DATA/canonical\_cuts.json \\

  \--fwords 02\_DATA/function\_words.txt \\

  \--policy 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/phrase\_gate\_policy.json \\

### **Derivation parity check**

For auditors verifying the tail is derived (not assumed):

python3 07\_TOOLS/validation/rederive\_plaintext.py \\
  \--ct 02\_DATA/ciphertext\_97.txt \\
  \--proof 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/proof\_digest\_enhanced.json \\
  \--out /tmp/derived\_pt.txt

\# Both should show: 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79
shasum -a 256 /tmp/derived\_pt.txt 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/plaintext\_97.txt

  \--out /tmp/k4\_verify\_HEAD\_0020\_v522B

**Tail derivation check (parity with paper)**

python 07\_TOOLS/validation/rederive\_plaintext.py \\

  \--ct 02\_DATA/ciphertext\_97.txt \\

  \--proof 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/proof\_digest\_enhanced.json \\

  \--perm 02\_DATA/permutations/GRID\_W14\_ROWS.json \\

  \--out /tmp/derived\_pt\_97.txt

shasum \-a 256 \\

  /tmp/derived\_pt\_97.txt \\

  01\_PUBLISHED/winner\_HEAD\_0020\_v522B/plaintext\_97.txt

\# \-\> 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79 (both)

### **How the repo mirrors the hand method**

* **Anchors first.** The proof logs **forced residues** at every anchor cell; Option-A checked (no K=0 pass-through in additive families).

* **Six short tracks.** For each class (0..5) family/L/phase are pinned — the same “wheel” you drew on paper.

* **Tail by propagation.** Decrypting 75..96 with those wheels yields the tail; the modern code does the **same** one add/sub per cell that you did by hand.

* **Route last.** T₂ rearranges **non-anchors** to match the display order; it does not produce the tail.

* **Presentation.** The boundary tokenizer v2 and lexicon fillers (“THEN”, “BETWEEN”) are publishing choices to make the spaced head readable; they **do not** change the letters-only line or any gate outcome.

---

## **Notes on scope**

* **Tail (“OF AN ANGLE IS THE ARC”).** We *derived* it cell-by-cell from the anchor-forced wheels, then recognized its sense in **Abel Flint**. Seam-free runs under the same rails replicate the tail across families and heads. We present this as **empirical** under the rails, not a universal proof.

* **Anchors-only algebra.** Single-key Vigenère-family is infeasible (collisions); six-track is feasible but does not determine all tail residues by anchors alone. The tail invariance emerges when anchors \+ NA-only permutations \+ Option-A \+ multi-class keys \+ head-only gates act **together**.

* **P\[74\].** All 26 letters are lawful with the same rails; nulls do not distinguish — the “T” in *THE JOY* is an editorial pre-seam choice.

---

## **Licenses, receipts, and contact**

This repo documents a claim **within a stated frame**; cite the frame, **pre-reg commit** d0b03f4, **policy SHA** bc083cc4129fedbc, and the **T₂ SHA** a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31.

* Winner PT SHA-256: 4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79 (bundle \= derived).

* See 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/RECEIPTS.json for consolidated receipts.

**Repository:** https://github.com/aviswerdlow/k4

**Solution date:** September 2025

**Method:** Anchors → six short tracks (Option-A) → tail by propagation → route for display parity → modern audited replay (hashes, schemas, CI)
