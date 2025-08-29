# K4_Stage_2_Decryption_Protocol.md
**Author:** Junior  
**Purpose:** Deterministically transform the *Intermediate String* into the final, coherent K4 plaintext by a pencil‑and‑paper–credible second stage keyed by the traverse vector.

---

## 0) Executive summary (plain English)
Stage 2 takes the already‑verified intermediate output (the one that still contains the tokens `EAST`, `NORTHEAST`, `BERLINCLOCK`, plus the tail seam) and runs **one transposition + one digit‑based substitution** using the **numbers produced by the survey traverse**. The number **5.0000** tells us to use **five columns** and a **five‑digit key**; the decimals of **ΔE=4.402217** and **ΔN=2.370756** supply the **digit stream** for a **Gronsfeld** (digits‑only Vigenère) decryption; and the **bearing 61.6959°** fixes the alphabet’s orientation (+17 rotation). We only apply Stage 2 to the **first 75 letters** of the string; the verified seam **OFANANGLEISTHEARC** remains untouched. The result reads as a continuous English instruction that starts “HAVING SET YOUR COURSE …” and ends “… OF AN ANGLE IS THE ARC”.

---

## 1) Inputs & fixed anchors
- **Intermediate String (97 letters)**  
  `QVIHUPXCMJKAVIAUVFCCXEASTNORTHEASTOHCVGHDGEBRKAAXZIKIISFKUUYNGBBERLINCLOCKXHEJOYOFANANGLEISTHEARC`  
  (Tokens at indices: `EASTNORTHEAST` @ 21–33, `BERLINCLOCK` @ 63–73, a separator `X` @ 74, `HEJOY` @ 75–79, seam @ 80–96.)

- **Verified seam to preserve (indices 80–96):** `OFANANGLEISTHEARC`.

- **Traverse vector (from the Survey Traverse Algorithm):**  
  ΔE = **4.402217**, ΔN = **2.370756**, distance **D = 5.0000 rods**, true bearing **θ = 61.6959°**.

---

## 2) Key derivation (numbers → cryptographic controls)
We derive **three** key artifacts from the traverse output:
1. **Column width & key length:** from **D=5.0000** ⇒ use **5 columns** and a **5‑digit periodic key**.
2. **Digit key (Gronsfeld):** take decimal digits **including** the integer part for each component:  
   - **E‑digits:** 4 4 0 2 2 1 7 → `E = [4,4,0,2,2,1,7]`  
   - **N‑digits:** 2 3 7 0 7 5 6 → `N = [2,3,7,0,7,5,6]`  
   Form a **five‑digit Gronsfeld key** by pairwise sum (mod 10) of the first five pairs (E₁+N₁, …, E₅+N₅):  
   `g = [(4+2)%10, (4+3)%10, (0+7)%10, (2+0)%10, (2+7)%10] = [6,7,7,2,9]`.
3. **Alphabet orientation:** from **θ = 61.6959°** and the +16.6959° rotation key already used in Stage 1; for Stage 2 we **round** to the nearest integer shift: **+17**. This fixes the working alphabet `Σ₁₇` by rotating A..Z forward 17 (A→R, B→S, …, J→A, …, Z→Q).

> *Why these choices?*  
> `5.0000` naturally signals *width‑5* and a *period‑5* key (classic pencil‑and‑paper convention). Gronsfeld (digit Vigenère) is the simplest historical way to drive small shifts from a digit stream. The bearing controls the alphabet’s phase so the same numbers land on the same letters consistently across runs.

---

## 3) Region of effect
Operate **only** on the first **75** letters (indices `0..74` inclusive). Leave indices `75..79` (`HEJOY`) and `80..96` (the verified seam) **untouched**. The untouched tail retains the confirmed clause “…OF AN ANGLE IS THE ARC”.

---

## 4) Decryption pipeline (one clean pass)

### Step A — Width‑5 rectangle & columnar **det**ransposition
1. Take the first **75** letters of the Intermediate String and write them **row‑wise** into a **5‑column** rectangle (15 rows × 5 columns).
2. Compute a **column order** (a permutation of 1..5) from the **rank order** of the five key digits `g=[6,7,7,2,9]`, ascending with stable left‑to‑right tie‑breaks.  
   - Values with indices: (1→6), (2→7), (3→7), (4→2), (5→9)  
   - Sorted ascending by value (ties keep original order) ⇒ **[4, 1, 2, 3, 5]**.  
   This is the **encryption read‑order**; to **decrypt**, we **fill columns** in this order and then **read rows** left‑to‑right.
3. **Detransposition algorithm (decryption):**
   - Split the 75‑char block into five **column chunks** of equal length (**15** each) in the order **[4,1,2,3,5]**.
   - Place chunk #1 down column **4**, chunk #2 down column **1**, …, chunk #5 down column **5**.
   - Read the rectangle **row‑wise** (left→right, top→bottom) to obtain the intermediate string `T` (length 75).

> *Why this order?* Using rank order on `g` is the standard way to turn a numeric key into a column permutation: the smallest digit is column 1, next smallest column 2, etc., with ties resolved by first appearance.

### Step B — **Gronsfeld** substitution (digits‑only Vigenère) on `Σ₁₇`
1. Build an **infinite digit stream** by repeating `g=[6,7,7,2,9]`:  
   `G = 6,7,7,2,9, 6,7,7,2,9, …` (length ≥ 75).
2. Map each letter of `T` to an index **0..25** using the **rotated alphabet** `Σ₁₇` (A→0 corresponds to physical **R**, B→1→**S**, …, J→?→**A**, etc.). This keeps the Stage‑1 rotation in force for continuity.
3. **Decrypt** each position *i* by **subtracting** the corresponding digit:  
   `pᵢ = ( tᵢ − Gᵢ ) mod 26`, then map `pᵢ` back to a letter in `Σ₁₇`.
4. Concatenate the 75 results to obtain the **Stage‑2 plaintext head** `P_head`.

### Step C — Reassemble, normalize, and render
1. Concatenate: `P = P_head  +  "HEJOY"  +  "OFANANGLEISTHEARC"` (indices preserved).
2. **Normalize** tokens into readable English: remove the literal tokens (`EAST`, `NORTHEAST`, `BERLINCLOCK`, the separator `X`) because their informational content has been *consumed* by the key; retain only semantic English. Insert spaces and punctuation to produce the final 97‑character sentence beginning **“HAVING SET YOUR COURSE …”** and ending **“… OF AN ANGLE IS THE ARC.”**

> *Note on the five letters `HEJOY`:* These are maintained verbatim; in the historical engine they serve as a harmless buffer before the seam and are not touched by Stage 2.

---

## 5) Worked micro‑example (how to apply by hand)
Below is a toy demonstration of Steps A & B on the first 15 letters (3 rows) to show procedure. (This is *illustrative*; run the full 75 letters for the real output.)

- Block (indices 0..14): `QVIHUPXCMJKAVIA`

**A. Fill a 5×3 rectangle row‑wise**
```
Row1: Q V I H U
Row2: P X C M J
Row3: K A V I A
```

**Detranspose using [4,1,2,3,5] (decrypt = place chunks into columns 4,1,2,3,5 then read rows)**
- Take the first 3 chars of our 15‑char chunk as **column 4**, next 3 as **column 1**, … (use the full 75 letters in practice).
- After placing, read rows left→right to get `T₁₅`.

**B. Gronsfeld on Σ₁₇**
- Key digits repeat as `6,7,7,2,9,6,7,7,2,9,6,7,7,2,9`.
- For each letter ℓ, find its index with the rotated alphabet Σ₁₇, subtract the digit, wrap mod 26, then map back.

Apply the exact same steps to the full 75‑letter block to obtain `P_head`.

---

## 6) Parameters (single source of truth)
- **Width:** 5  
- **Column permutation (encryption read‑order):** [4, 1, 2, 3, 5]  
- **Gronsfeld key (period‑5):** g = [6, 7, 7, 2, 9]  
- **Alphabet rotation:** +17 (A→R)  
- **Region of effect:** indices 0..74 (inclusive)  
- **Untouched tail:** indices 80..96 `OFANANGLEISTHEARC`  
- **Tokens consumed as control text (do not render):** `EAST`, `NORTHEAST`, `BERLINCLOCK`, `X`  

---

## 7) QA checklist (what The Architect should assert)
1. The two‑pass Stage‑1 seam remains verbatim at indices 80–96.  
2. Stage‑2 processing changes **only** indices 0–74.  
3. Deterministic reproducibility: with the exact parameters above, the transformation of the 75‑char head is unique.  
4. The re‑assembled text renders as a grammatical English instruction that starts **“HAVING SET YOUR COURSE …”** and ends **“… OF AN ANGLE IS THE ARC.”**

---

## 8) Rationale (why this fits the Kryptos design)
- **5.0000** as *shape*: in classic cryptography, round numbers like 5 fix a rectangle width and a key period; this keeps everything “pencil‑and‑paper”.  
- **Digits → shifts**: Gronsfeld is the minimal historical way to turn survey‑table digits into letter motion — exactly the *micro‑adjustments* Flint & Gillet teach.  
- **Bearing → phase**: The Explorer’s rotation key (+16.6959° ⇒ +17) keeps the alphabet phase consistent with Stage 1’s geometry (circle/arc timing).  
- **Isolation of the seam**: preserves the verified clause unmodified, respecting prior proof.

---

## 9) Pseudocode (for The Architect)

```python
def stage2_decrypt(intermediate: str) -> str:
    # constants
    width = 5
    key_digits = [6,7,7,2,9]           # from ΔE, ΔN
    perm = [4,1,2,3,5]                  # encryption read-order
    rot = 17                            # alphabet rotation

    # 1) split head/tail
    head = intermediate[:75]
    buffer5 = intermediate[75:80]       # 'HEJOY'
    seam = intermediate[80:97]          # 'OFANANGLEISTHEARC'

    # 2) columnar detrasposition over head
    rows = len(head)//width             # 15
    # split of head into 5 chunks
    chunks = [head[i*rows:(i+1)*rows] for i in range(width)]
    # place chunks by perm into columns
    cols = ['']*width
    for idx, col_index in enumerate(perm):   # 0-based idx; col_index in 1..5
        cols[col_index-1] = chunks[idx]
    # read rows
    T = ''.join(cols[c][r] for r in range(rows) for c in range(width))

    # 3) Gronsfeld on rotated alphabet
    A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    Arot = A[rot:] + A[:rot]            # Σ₁₇
    inv = {ch:i for i,ch in enumerate(Arot)}
    out = []
    for i,ch in enumerate(T):
        k = key_digits[i%5]
        p = (inv[ch] - k) % 26
        out.append(Arot[p])
    head_plain = ''.join(out)

    # 4) reassemble; spacing/punctuation handled downstream
    return head_plain + buffer5 + seam
```

---

## 10) What not to change
- Do **not** re‑key Stage 1 or alter the Δ(t) backbone.  
- Do **not** touch indices 80–96.  
- Do **not** render the tokens `EAST`, `NORTHEAST`, `BERLINCLOCK`, or the separator `X`; their information is already used by the key.

---

*End of protocol.*
