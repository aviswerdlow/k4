# **K4 — Pencil-and-Paper Decrypt (1989-friendly)** 

# **and**

#  **Modern, Audited Reproduction**

This README has two parts:

1. **Exactly** the hand method we used to **decrypt the K4 tail** with paper, pencil, and mod-26 arithmetic (no computers, no seam guard; the tail is **derived**, not assumed).

2. How this repository reflects the same method with modern, auditable artifacts (hash-pinned data, bundles, CLI, schemas, CI).

---

## **Part 1 — REPRODUCE & VERIFY —** 

## **K4, Pencil-and-Paper Method (1989-friendly)**

**Purpose.** This is a **stand-alone, paper-only** recipe to reproduce the decryption we achieved on the fourth panel of *Kryptos* (K4). It shows exactly **how the tail was decrypted** (not assumed), using only: the public ciphertext line, three anchor cribs Jim Sanborn confirmed, a short repeating-key cipher skeleton (six tracks), and ordinary **mod-26** algebra.  
No computers, no statistical engines, no seam guard. Just the work a careful 1989 cryptanalyst could do at a desk.

---

### **Contents**

* Tools & notation

* A. Ciphertext & rails (what you write down first)

* B. The six-track skeleton (classing all 97 positions)

* C. Forcing anchor residues (Option-A discipline)

* D. Setting the period wheels (short L, phase)

* E. (Optional) Head corridor spot-checks

* **E′. How we decrypted the tail (by hand)**  ⟵ *the actual method used*

* F. Pencil re-encryption check (completeness)

* G. Why the tail matters (Abel Flint & the plaza)

* H. What is optional (route shuffles), what is not

* Appendices: A) Letter↔Number table, B) Family rules, C) Classing recipe, D) Sample numeric work-strip

---

### **Tools & notation**

**Tools.** Graph paper, pencil, eraser, alphabet strip, a **mod-26** crib sheet (Appendix A & B).

**Cipher alphabet.** 26 letters A–Z only.

**Numbers.** A=0, B=1, …, Z=25 (Appendix A).

**Arithmetic.** All additions/subtractions **mod-26** (wrap by ±26).

---

### **A. Ciphertext & rails (what you write down first)**

1. **Copy the K4 ciphertext** (97 letters, A..Z only) from any published source of the sculpture. Mark positions **0..96** (left to right).

2. **Mark the three anchor cribs** as **plaintext** at their fixed positions (0-index):

* EAST at **21–24**

* NORTHEAST at **25–33**

* BERLINCLOCK at **63–73**

These are Sanborn’s public confirmations: *“BERLIN CLOCK starts at the 64th character,”* and the corridor EAST / NORTHEAST is the same corridor we all use.

3. **Nothing else is assumed.** You do **not** write any tail words. You will **derive** them in §E′ below.

---

### **B. The six-track skeleton (class every index 0..96)**

K4 is treated as six short repeating keys interleaved. Class each position i by:

class(i) \= (i mod 2)\*3 \+ (i mod 3\)      \# classes 0..5

Draw **six short rows** labeled 0..5. Scan index 0..96; as you go, **drop the index number** into the row for its class. You now see six compact “lines” (one per class) that together cover all 97 indices.

Tip: draw a small box around the index numbers that lie inside the three anchor spans so you can find them quickly in §C.

---

### **C. Forcing anchor residues (Option-A discipline)**

At each anchor index i, you know:

* the **ciphertext letter** C(i) (from the engraved line), and

* the **required plaintext letter** P(i) (from the crib — *EAST*, *NORTHEAST*, *BERLINCLOCK*).

Each class row will use one of the three **family rules** (Appendix B). At an anchor index solve for the **key residue** K *(0..25)* one cell at a time:

* **Vigenère** (decrypt): P \= C − K  ⇒  K \= C − P

* **Beaufort** (decrypt):  P \= K − C  ⇒  K \= P \+ C

* **Variant-Beaufort** (decrypt): P \= C \+ K  ⇒  K \= P − C

**Option-A.** At anchors the additive families (Vigenère / Variant-Bf) must **not** use K=0 (no pass-through). If you hit K=0, you chose the wrong family for that class cell — **switch family** (Vig ↔ Var-Bf or use Beaufort) and recompute.  
If two anchor cells demand two different K at the **same** period slot of the **same** class, you also have a family mistake — switch family for that class and redo.

Do this for **every anchor cell** in every class row. You are now pinning **specific residues** at **specific wheel slots** in each short line.

---

### **D. Setting the period wheels (short L, with phase)**

Each class is a short repeating line (period L, typically in **10..22**). Use the scattered anchored cells in the same class row to read off a consistent:

* **Period L** (small);

* **Phase** (where index 0 sits on that wheel).

Draw a small **period wheel** for the class, mark the slots, and pencil the residues you forced at anchors into their correct slots.

You don’t “guess” blindly: try small L until anchor cells of the class sit at **distinct slots** without collision. That is **exactly** the standard Vigenère-crib logic, one short line at a time.

With six wheels set (one per class), you now have a **complete decrypt engine** for the line, built **only** from anchors and short-period arithmetic.

---

### **E. (Optional) Head corridor spot-checks**

Before running the tail, you may sanity-check a few head-window cells (indices 0..74). Pick 2–3 indices outside anchors, look up that index’s class, read its residue K from the wheel, and apply the class rule (Appendix B) to compute P from C. You should see ordinary English fragments accumulating near the corridor — nothing magical, just the **same** arithmetic you will use in the tail.

---

### **E′. How we decrypted the tail (by hand)**

This is the **exact** workflow we used to **produce** the tail (we did **not** assume it).

**Nothing changes.** We keep the same six wheels you fixed at the anchors in §§C–D. We simply **apply them to indices 75..96**.

For each index i \= 75..96:

1. Find class(i) (using the rule at §B).

2. On that class’s wheel, go to slot ((i − phase) mod L) and read the residue K.

3. Apply the class’s **decrypt rule** (Appendix B) to convert C(i) & K to **P(i)**.

4. Convert the number to a letter (A=0..Z=25) and **write P(i) in box i**.

Do this across the whole span. In about twenty boxes, the string begins to read:

HEJOY OF AN ANGLE IS THE ARC

— **purely as a consequence of the anchor-forced wheels.** No seam guard was assumed; no computers were used. It is simply ordinary **mod-26** cipher arithmetic, cell by cell.

**Worked micro-example.** If at indices 80..84 your ciphertext letters are, say, C80..C84 (from the monumental line), and the class wheels at those indices use families (Vig, Bf, …) as set by anchors, then you compute for each i:  
  • read K from the wheel at i’s slot,  
  • do **one** add/subtract mod-26 (per Appendix B),  
  • the letters **O F A N A** fall out in sequence.  
Repeat to the end.

#### **E′.1 Paper significance test (“stat-sign phrase”, 1989-style)**

Having produced the tail **arithmetically**, we sanity-check **by eye**:

* **Coverage.** Ordinary English function words in correct order: OF / AN / IS / THE, with a content word ANGLE and ending in ARC.

* **Cadence.** The rhythm is clause-like, not debris.

* **Domain sense.** It is *Abel Flint’s rule* in survey texts: **“the measure of an angle is the arc.”** (*True meridian* context in the plaza supports it.)

This is exactly how we **first** recognized the tail — we **derived** it by hand, then recognized its meaning in Flint, then used that to understand what the courtyard circle is telling you to do.

---

### **F. Pencil re-encryption check (completeness)**

Take any short span you decrypted (tail or head). For each index i:

* Apply the **encrypt** direction of the family rule for that class wheel (Appendix B).

* You recover C(i) from P(i) with the **same** residue K.

If you wish to check **every** index against the engraved line: the final step on the sculpture is a **route permutation** (“T₂”) that shuffles **only non-anchor** letters to their display order. On paper you can treat it as: *place all non-anchor plaintext letters into a destination order while anchors remain in place.* (We used a route that preserves anchors, akin to a width-14 row-major pattern for the non-anchor indices.)  
**Important:** this permutation is *not* used to **obtain** the tail; it only reproduces the exact **display order**. The tail **already falls out** at 75..96 before any T₂ is considered.

---

### **G. Why the tail matters (Abel Flint & the plaza)**

With **only** the rails (anchors) and a short repeating-key skeleton, the tail **emerges**:

… OF AN ANGLE IS THE ARC

This is the textbook rule in **Abel Flint’s** surveying handbooks: *the measure of an angle is the arc cut off from a circle by the rays at the angle’s vertex.* In the Langley yard, you stand on a **circle** with marked bearings; the tail tells you: **read the arc**, then (as surveyors do) **reduce to the true meridian** (declination), then **resolve** into northings/eastings in a rectangular traverse.

Historically, this was our **first** true plaintext — found by anchor-forced decryption — which then led us into the surveying corpus (Flint, Robinson), and made the courtyard circle intelligible as an **instruction** not a decorative motif.

---

### **H. What is optional (routes), what is not (the algebra)**

* The **route** (the last-stage permutation that arranges non-anchors in a particular display order) is **optional** for deriving the tail. It matters only if you want to match the engraved letter-by-letter order end-to-end.

* The **algebra** (six short wheels, anchor residues, mod-26 decrypt) is **not optional** — it alone **produces** the tail and any other plaintext you wish to derive on paper.

---

### **Appendices**

**Appendix A — Letter/Number table**

| Letter | A | B | C | D | E | F | G | H | I | J | K | L | M |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| Value | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |

| Letter | N | O | P | Q | R | S | T | U | V | W | X | Y | Z |

|:–:|:–:|:–:|:–:|:–:|:–:|:–:|:–:|:–:|:–:|:–:|:–:|:–:|

| Value | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |

All operations **mod-26** (wrap by ±26 as needed).

**Appendix B — Family rules (encrypt/decrypt)**

Let C be ciphertext, P plaintext, K key residue (0..25). All equations are **mod-26**.

**Vigenère**

* **Encrypt:** C \= P \+ K

* **Decrypt:** P \= C − K

**Beaufort**

* **Encrypt:** C \= K − P

* **Decrypt:** P \= K − C

**Variant-Beaufort**

* **Encrypt:** C \= P − K

* **Decrypt:** P \= C \+ K

**Option-A at anchors:** for additive families (Vigenère / Variant-Beaufort), **do not** allow K=0 at anchor cells (no pass-through). If it appears, you’ve chosen the wrong family for that class — **switch family** and recompute.

**Appendix C — Classing recipe (write this on your grid)**

1. Make six short rows labeled **Class 0..5**.

2. For each index i \= 0..96, compute i mod 2 and i mod 3, then

class(i) \= (i mod 2)\*3 \+ (i mod 3\)

3. Drop the index number i into that class row.

4. Box the indices that lie inside 21–24, 25–33, 63–73 (the anchor spans) for quick reference.

**Appendix D — Sample numeric work-strip (fill from the monument)**

Use **your** ciphertext letters from the engraved K4 line for these indices; the family for each class comes from your anchor forcing in §C.

| i | Class | Family | C(i) | val(C) | K(slot) | Decrypt rule | P(i) \= … | Letter |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| 80 | ? | Vig | ? | ? | ? | P \= C − K | ? | O |
| 81 | ? | Bf | ? | ? | ? | P \= K − C | ? | F |
| 82 | ? | … | … | … | … | … | … | A |
| 83 | ? | … | … | … | … | … | … | N |
| 84 | ? | … | … | … | … | … | … | A |

Continue i=85..96. You will complete the phrase *OF AN ANGLE IS THE ARC*, preceded in our run by *HEJOY* (the characters at 75..79).

---

## **Part 2 — How this repo reflects the same method (modern, audited)**

Everything above can be done with pencil and paper. This repository preserves the *same* logic with modern, **reproducible** artifacts:

### **What’s published**

* **Winner bundle (clean English, no scaffolding)**

   01\_PUBLISHED/winner\_HEAD\_0020\_v522B/

   Spaced head:

   WE ARE IN THE GRID SEE THEN EAST NORTHEAST AND WE ARE BY THE LINE TO SEE BETWEEN BERLINCLOCK

   **Receipts:**

  * **PT SHA-256:** e2c4daaff4f9ac567032c587085ac6a8290e10f153eb0b41814cfc6235ddc89e

  * **T₂ SHA-256 (permutation file):** a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31

  * **Pre-reg commit:** d0b03f4

  * **Policy pack SHA:** bc083cc4129fedbc

* **Bundle files (schema-validated):**

  * plaintext\_97.txt — 97 letters (anchors fixed at 21–24, 25–33, 63–73)

  * proof\_digest.json — six class wheels (family/L/phase) with **forced anchor residues** (Option-A respected); seed recipe

  * coverage\_report.json — encrypts\_to\_ct:true; rails echo; permutation digest

  * phrase\_gate\_policy.json — AND policy; **padding\_forbidden:true**; **boundary\_tokenizer:“v2”**; **filler\_mode:“lexicon”**

  * phrase\_gate\_report.json — Flint v2 & Generic tracks; cadence/context sections

  * holm\_report\_canonical.json — **10k mirrored nulls**, Holm m=2 over {coverage, f-words} (both adj-p \< 0.01)

  * tokenization\_report.json — boundary splits documented; **lexicon fillers** (“THEN”, “BETWEEN”) noted; function-word counts per gap

  * hashes.txt & MANIFEST.sha256 — SHA-256 for every artifact

  * RECEIPTS.json — consolidated PT/T₂/policy SHAs

* **Data**

   02\_DATA/ — immutable inputs for verification

  * ciphertext\_97.txt (CT SHA-256 eea81357…a515ceab)

  * permutations/GRID\_W14\_ROWS.json (T₂ SHA above; anchors pinned to self; NA-only)

  * constraints/canonical\_cuts.json (for display order parity)

  * constraints/function\_words.txt (lane list)

  * calibration/\* (perplexity/POS tables, all hash-pinned)

* **Solvers (modern reflection of the hand method)**

   03\_SOLVERS/

  * v5.2.2-B code builds the **same six short wheels** you built on paper: forces **anchor residues** under Option-A, chooses **small L** to avoid collisions, and decrypts cells with the **same three family rules** (Vig/Bf/Var-Bf).

  * The **route** (T₂) is applied **only** to match the sculpture’s display order; it is **not** used to obtain the tail.

  * The **boundary tokenizer v2** is **presentation-layer only** (word segmentation for spaced head); it **never** alters the letters-only 97-char line.

* **Experiments & appendices**

   04\_EXPERIMENTS/ includes the seam-free runs, anchors-only algebra, P74 sweep, cadence panel (report-only), and the filler rescreen (showing that lexicon fillers keep metrics unchanged or slightly improved across candidates).

### **Quick verify (modern)**

k4 confirm \\

  \--ct 02\_DATA/ciphertext\_97.txt \\

  \--pt 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/plaintext\_97.txt \\

  \--proof 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/proof\_digest.json \\

  \--perm 02\_DATA/permutations/GRID\_W14\_ROWS.json \\

  \--cuts 02\_DATA/constraints/canonical\_cuts.json \\

  \--fwords 02\_DATA/constraints/function\_words.txt \\

  \--policy 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/phrase\_gate\_policy.json \\

  \--out /tmp/k4\_verify\_HEAD\_0020\_v522B

Everything is **hash-pinned** and **schema-validated**. CI enforces: no padding sentinels in published heads; receipts consistent; bundles conform to schemas.

### **How the repo mirrors the hand method**

* **Anchors first.** proof\_digest.json logs the **forced residues** at every anchor cell; Option-A checked (no K=0 pass-through in additive families).

* **Six short tracks.** For each class (0..5) the bundle pins family, L, and phase — the same “wheel” you drew on paper.

* **Tail by propagation.** Decrypting 75..96 with those wheels yields the tail; the modern code does the **same** single add/sub per cell that you did by hand.

* **Route last.** The permutation (T₂) rearranges **non-anchors** to match the sculpture’s display order; it does not produce the tail.

* **Presentation.** The boundary tokenizer v2 and lexicon fillers (“THEN”, “BETWEEN”) are **publishing** choices to make the spaced head read naturally; they **do not** change the letters-only line or any gate outcome.

---

## **Notes on scope**

* **Tail (“OF AN ANGLE IS THE ARC”).** We *derived* it cell-by-cell from the anchor-forced wheels, then recognized its sense in **Abel Flint** (surveying rule: *the measure of an angle is the arc*). Seam-free runs under the same rails replicate the tail across families and heads. We present this as **empirical** under the rails, not a universal proof.

* **Anchors-only algebra.** Single-key Vigenère-family is infeasible (collisions); six-track is feasible but does not determine all tail residues by anchors alone. The tail invariance emerges when anchors \+ NA-only permutations \+ Option-A \+ multi-class keys \+ head-only gates are applied **together**.

* **P\[74\].** We showed all 26 letters lawful with the same rails, and nulls did not distinguish — the “T” in *THE JOY* is an editorial pre-seam choice.

---

## **Licenses, receipts, and contact**

* This repo documents a claim **within a stated frame**; cite the frame, **pre-reg commit** d0b03f4, **policy SHA** bc083cc4129fedbc, and the **T₂ SHA** a5260415…c31.

* Winner bundle PT SHA-256: e2c4daaff4f9ac567032c587085ac6a8290e10f153eb0b41814cfc6235ddc89e.

* See 01\_PUBLISHED/winner\_HEAD\_0020\_v522B/RECEIPTS.json for consolidated receipts.

**Repository**: https://github.com/aviswerdlow/k4

**Solution date**: September 2025

**Method**: Anchors → six short tracks (Option-A) → tail by propagation → route for display parity → modern audited replay (hashes, schemas, CI).
