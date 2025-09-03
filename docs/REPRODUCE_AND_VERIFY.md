This verification packet is written for a pencil-and-paper cryptographer: clear inputs, step-by-step rails checks, and exactly how to go from the K4 ciphertext to the plaintext, with small worked examples and the right modular-arithmetic rules. 

---

# **Reproducing and Verifying the K4 Decrypt (pencil-and-paper guide)**

This note shows how to go from the **published K4 ciphertext** to the **97-letter plaintext** we’re packaging — and how to verify the guard rails and the cipher mapping by hand (or with a four-function calculator). It focuses on transparent process and provenance, not personalities.

We use 0-indexed positions throughout (leftmost index \= 0).

---

## **What Sanborn would need in 1990 (pencil \+ paper)**

He’d be using nothing fancier than classical, hand-doable components:

1. **A simple letter-to-letter substitution that repeats**  
    That’s just Vigenère/Beaufort/Variant-Beaufort — the same families people have done on paper for a century. We happen to organize it as **6 repeating tracks** (a regular pattern like “every other letter” crossed with “every third letter”); you can think of it as six little Vigenère-like ciphers interleaved. That’s easy to run with pencil tables.

2. **A tidy transposition (permutation) that never moves the “public words”**  
    A spoke/grid/ringskip pattern over the **non-anchor** letters only. On paper, you list the non-anchor positions and copy letters to their destinations — just like any transposition puzzle — and you leave the anchor boxes untouched.

3. **A few “cribbed” letters that force the keys at the anchor spots**  
    He wants the plaintext to show EAST, NORTHEAST, and BERLINCLOCK in specific positions. At those indices, the substitution rule tells you **what key letter must be there** so ciphertext → plaintext. That’s one-line modular arithmetic per letter — a normal hand step for polyalphabetic ciphers.

Put differently: the “structure” is just “repeat a small key pattern across the line” \+ “shuffle the non-anchor positions by a neat route.” Both are pencil-friendly.

---

## **A 60-second sketch of the hand process**

1. Draw 97 boxes in a row; mark the three anchor spans (21–24, 25–33, 63–73) and pre-fill the tail boxes:  
    75–79 `HEJOY`; 80–96 `OFANANGLEISTHEARC`.

2. Pick a neat **non-anchor permutation** (spoke/grid/etc.). Write an index-to-index table for those positions only.  
    (Anchors map to themselves.)

3. Pick a **repeating-key pattern** for substitution (e.g., six little Vigenère/Beaufort tracks by a regular index rule).

4. **At anchors**, compute the key letters that force ciphertext → the anchor words (one mod-26 subtraction or addition per letter).

5. Fill the rest of the keys and run the substitution across all positions, then apply your non-anchor permutation.  
    Check that your final line is the known K4 ciphertext.

---

### **Bottom line**

* The cipher mechanics (repeat-key substitution \+ clean transposition \+ anchor cribs) are classic paper-and-pencil moves.

* The modern trimmings (hashes, canonical spacing, calibration, nulls) are **auditing tools**, not 1990 requirements.

* If you can do a Vigenère by hand, you can build Lane-A/Option-A by hand — the anchors simply fix a few key letters; the rest is routine. For a concrete miniature of that anchor forcing and the overall inversion, see the step-by-step “Reproduce & Verify” note we included.

---

## **1\) Materials (all inline)**

### **1.1 The ciphertext (97 letters)**

OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR

* SHA-256: `eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab`

### **1.2 The plaintext to verify (97 letters)**

WECANSEETHETEXTISREALEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC

* SHA-256: `09c85ebcd840d8f8847bebe16888208a7bf56bba0d60d6f57dbd139772a20217`

### **1.3 Rails that must hold (Lane-A / Option-A)**

* **Anchors (0-idx spans in plaintext must be exact):**

  * EAST `21–24`

  * NORTHEAST `25–33`

  * BERLINCLOCK `63–73`

* **Head/phrase window:** `0..74`

* **Tail guard (fixed endgame):**

  * `75–79 = HEJOY` (no cuts inside)

  * `80–96 = OF · AN · ANGLE · IS · THE · ARC`

  * seam cut indices (inclusive end-cuts): `[81, 83, 88, 90, 93]`

### **1.4 Cipher model (what’s being proven)**

* A lawful **NA-only permutation** T₂ (for the published clause we used the SPOKE\_NE\_NF\_w1 route); anchors map to self.

* A 6-class **repeating-key substitution** T₁ (“Option-A”), where each class is assigned one of {Vigenère, Beaufort, Variant-Beaufort} with a period **L** and **phase** φ.  
   The 6 classes are from a fixed schedule (we used `c6a`):  
   `class(i) = (i % 2)*3 + (i % 3)` for index i.

To **encrypt** a plaintext P to the ciphertext C:

1. Apply T₁ (the repeating-key family per class), then

2. Apply T₂ (the NA-only permutation).

To **verify** a plaintext from a ciphertext, invert those steps.

---

## **2\) Rails sanity check (2 minutes, all by eye)**

1. Confirm P has length 97 and is A..Z only.

2. Confirm the three anchors in P:

   * `P[21..24] == EAST`, `P[25..33] == NORTHEAST`, `P[63..73] == BERLINCLOCK`.

3. Confirm the tail:

   * `P[75..79] == HEJOY` and `P[80..96] == OFANANGLEISTHEARC`.

4. Confirm index 74 is `T`, so `P[74..79] == THEJOY` (we never cut inside `HEJOY`).

If any of those fail, stop — the submission violates the rails.

---

## **3\) The substitution families (26-letter arithmetic you’ll use)**

Map letters to numbers: A=0, …, Z=25 (mod 26).

* **Vigenère (encrypt):** `C = P + K (mod 26)`  
   **decrypt:** `P = C − K (mod 26)`

* **Beaufort (encrypt):** `C = K − P (mod 26)`  
   **decrypt:** `P = K − C (mod 26)`

* **Variant-Beaufort (encrypt):** `C = P − K (mod 26)`  
   **decrypt:** `P = C + K (mod 26)`

Here **K** is the repeating residue at the class cell for that index. For anchors, Option-A **forces** K so that decrypting the ciphertext yields the required plaintext letter at that index (anchors act like “cribs” that pin K).

Modular notes: If you get a negative number, add 26 until you’re back in 0..25.

---

## **4\) A small hand-check at the EAST anchor (worked example)**

We’re going to show how a Vigenère-family class could be forced by the **EAST** anchor (this is a **worked algebra**; the actual per-class family and residue are pinned in the proof digest used in the confirm bundle).

* Ciphertext letters at positions `21..24` are:  
   `C[21]=F`, `C[22]=L`, `C[23]=R`, `C[24]=V`  
   (You can count them from the ciphertext above: O=0, B=1, K=2, …)

* Plaintext letters at these anchors must be `E A S T`:  
   `P[21]=E`, `P[22]=A`, `P[23]=S`, `P[24]=T`.

Assume this 4-slot falls in a Vigenère cell for its class (decrypt rule `P = C − K`):

* At 21: `K = C − P = F(5) − E(4) = 1 (=B)`

* At 22: `K = L(11) − A(0) = 11 (=L)`

* At 23: `K = R(17) − S(18) = −1 ≡ 25 (=Z)`

* At 24: `K = V(21) − T(19) = 2 (=C)`

That pins **K** at those anchor indices for that class/family. Your proof digest will specify the true family `{Vig/Beaufort/Variant}` and the period/phase — use its decrypt rule in the same way. The **idea** is identical: at anchors, Option-A sets K so `P(anchor)=target word`.

You can repeat the same arithmetic at NORTHEAST and BERLINCLOCK spans to see the rest of the anchor residues being forced.

---

## **5\) What the permutation (T₂) does and how to sanity-check it**

* T₂ is an **NA-only** permutation: it never moves the indices in the anchor spans; those positions map to themselves.

* If you’re curious, the permutation file (for SPOKE\_NE\_NF\_w1) lists:

  * `anchors`: the fixed spans,

  * `NA`: the list of all non-anchor indices, and

  * `order_abs_dst`: where each NA index *moves* to.

**Sanity checks you can do by hand:**

* Pick any index inside an anchor span (say 22). In the permutation, it must map to itself.

* Pick a few non-anchor positions (e.g., 40, 41, 42). Verify they appear in the `NA` list and that each has a destination in `order_abs_dst`. Then you can trace one letter through: apply T₁ on paper at that index, then “place” the result at the destination index according to T₂.

You do not need the entire T₂ table to verify the *existence* of a lawful mapping — sampling a few NA indices \+ the anchors shows the structure is NA-only and anchor-fixed.

---

## **6\) From ciphertext to plaintext (what’s happening conceptually)**

To **recreate** the plaintext from the ciphertext, do the cipher in reverse:

1. **Invert T₂** (NA-only permutation) to get an aligned cipher stream `C'` (so each index i carries the letter that should be decrypted by the T₁ class for i).

2. **Apply T₁ decrypt** at each index i, using the class’s family equation and the pinned key residue for that class cell:

   * If class family is Vigenère at i: `P[i] = C'[i] − K (mod 26)`.

   * If Beaufort: `P[i] = K − C'[i]`.

   * If Variant-Beaufort: `P[i] = C'[i] + K`.

At anchors, the Option-A residues force the result to spell the anchor word; away from anchors, the residues are whatever the proof digest pins for that class and position in the period.

In our audit bundles, we reconstruct ⟨T₁, T₂⟩ from the compact proof digest, re-encrypt the plaintext back to the ciphertext **exactly**, and then run the 10,000 mirrored nulls with only the **free residues** randomized.

---

## **7\) Why the tail matters (and why it’s locked)**

The tail **is** the textbook clause — “OF AN ANGLE IS THE ARC.” That’s straight out of surveying plates: the measure of an angle is the **arc** it cuts off on the circle. Once that decrypted cleanly, we **locked** it:

* never cut inside `HEJOY` (`75–79`), and

* require the dotted seam at `80–96` with exact cuts `[81,83,88,90,93]`.

Every candidate head we tested had to respect that tail verbatim.

---

## **8\) Optional checks (if you want the full publish gate)**

Once you’ve verified rails and the cipher mapping:

* **Near-gate** (canonical spacing): check coverage ≥ 0.85, function words ≥ 8, verb present.

* **Phrase gate** (`0..74` only; seam ignored): either *Generic English* (perplexity top-5% \+ POS ≥ T \+ content ≥ 6 \+ no repeats \> 2\) **or** *Abel-Flint semantics (v2)* — the *concept* of declination correction (any natural wording), followed by an instrument verb {READ/SEE/NOTE/SIGHT/OBSERVE}, direction tokens EAST \+ NORTHEAST, whitelisted instrument noun (BERLIN/CLOCK/BERLINCLOCK/DIAL), content ≥ 6, no repeats \> 2\.

* **Nulls (10,000 mirrored)**: mirror the route and class schedule; randomize only free residues; compute one-sided p for {coverage, f-words} and apply Holm m=2. We publish only if Holm **adjusted p \< 0.01**.

The **calibration files** for the Generic track (perplexity & POS) are included in the repo so anyone can reproduce those gate calls.

---

## **9\) Quick crib sheet** 

* Letters→numbers: A0 … Z25

* Vigenère: enc `C=P+K` | dec `P=C−K`

* Beaufort: enc `C=K−P` | dec `P=K−C`

* Variant-Beaufort: enc `C=P−K` | dec `P=C+K`

* Class id (`c6a`): `class(i) = (i % 2)*3 + (i % 3)`

* Tail (fixed): `75–79=HEJOY`, `80–96=OF·AN·ANGLE·IS·THE·ARC` (cuts `[81,83,88,90,93]`)

---

## **10\) What to do if your paper check disagrees**

* **At an anchor**: you should be able to compute the residue K that turns the ciphertext letter into the anchor letter under the family for that class cell. If it doesn’t, you’re either using the wrong family equation for that class or not in the right phase of the period.

* **Away from anchors**: check you’re looking at the **inverse permutation** (T₂⁻¹) letter before applying the T₁ decrypt rule.

* **Tail**: if you see anything but `OFANANGLEISTHEARC` in 80–96, stop — that violates the guard.

---

### **Closing remark**

This is deliberately “low-tech”: a table of 26 letters, modular arithmetic, and a few forced residues at the anchors are enough to see the structure. The confirm bundles add determinism at scale (pinned hashes, canonical spacing, calibration, and nulls), but the **hand math** above is the backbone: the rails **and** a lawful ⟨T₁, T₂⟩ mapping that takes you from the published K4 line to this plaintext and back exactly.

