# **K5 — From “World Clock” to Traverse (pencil-and-paper)**

**How to use a round dial (e.g., the Urania World Clock at Alexanderplatz) as your surveying circle to go from ciphertext → plaintext instruction → bearing → rectangular reduction.**

---

## **TL;DR**

Treat the plaza’s round dial as a **surveying circle** (a limb). The text’s **direction words** (e.g., **EAST NORTHEAST**) tell you **which arc** to read on the circle; the **tail** you’ve already decrypted tells you **how** to interpret it:

**“… OF AN ANGLE IS THE ARC.”**  
*Read the angle as an arc on the circle; then act as a surveyor.*

Then:

1. Read the arc \\theta\_{\\text{dial}} in the named sector (NE, ENE, etc.).

2. Correct to **true** with declination \\delta:

    \\boxed{\\ \\theta\_{\\text{true}} \= \\theta\_{\\text{dial}} \+ \\delta\\ }

3. Choose or measure a **distance** d.

4. Reduce to rectangular components (true meridian basis):

    \\Delta N \= d \\cos \\theta\_{\\text{true}},\\qquad \\Delta E \= d \\sin \\theta\_{\\text{true}}

That’s one traverse leg.

**Assumptions:** You’ve already verified the **97-character** plaintext under rails (anchors at 21–24, 25–33, 63–73; tail **derived**, not assumed). This note is **surveying-only**: how to turn the words into a direction and a traverse row using paper tools.

---

## **0\) What you need**

* **Plaintext (97 letters, A..Z)** you have verified under rails.

   Example head tokens: … EAST NORTHEAST …

   Example tail (derived arithmetically): … THE JOY OF AN ANGLE IS THE ARC.

* **Declination** \\delta for location/epoch (east **\+**, west **−**).

   If you lack a date, you may use the illustrative value \\delta \= \+16.6959^\\circ (document your choice).

* **Distance** d. Either:

  * adopt a **unit** distance ( d \= 1 ) for a direction vector,

  * **measure** on site or from a plan (paces, meters, etc.), or

  * pick a demo value (e.g., d \= 5 ).

**Paper kit:** protractor (or ticked printout), ruler, pencil, a square or straightedge.

---

## **1\) Read the direction as an arc (not as a word)**

Draw/print a circle with **north** at the top (0°/360°), **east** at 90°, **south** at 180°, **west** at 270°. A **16-point wind rose** divides the circle every **22.5°**:

| Point | Deg | Point | Deg | Point | Deg | Point | Deg |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| N | 0.0 | ENE | 67.5 | S | 180.0 | WNW | 292.5 |
| NNE | 22.5 | E | 90.0 | SSW | 202.5 | W | 270.0 |
| NE | 45.0 | ESE | 112.5 | SW | 225.0 | WSW | 247.5 |
| NEE (alias NE) | 45.0 | SE | 135.0 | NW | 315.0 | NNW | 337.5 |

**Locate the named sector** in your head clause:

* **NORTHEAST** → read near **45.0°**.

* **EAST NORTHEAST** → read near **67.5°** (ENE).

* **EAST** → read at **90.0°**.

**Why “arc”?** The plaza’s circular limb is a surveying circle. Per your decrypted tail (Flint’s rule), *the measure of an angle is the arc*. You read the **degrees** on the circle, not do wordplay.

Call your reading \\theta\_{\\text{dial}}.

---

## **2\) Correct to the true meridian (declination)**

Apply local **magnetic declination** \\delta to obtain the **true-meridian** azimuth:

\\boxed{\\ \\theta\_{\\text{true}} \= \\theta\_{\\text{dial}} \+ \\delta\\ } \\quad \\text{(east \\(+\\), west \\(−\\))}

**Examples (using** \\delta \= \+16.6959^\\circ**):**

* NE case: \\theta\_{\\text{dial}} \= 45.0^\\circ \\Rightarrow \\theta\_{\\text{true}} \\approx 61.6959^\\circ

* ENE case: \\theta\_{\\text{dial}} \= 67.5^\\circ \\Rightarrow \\theta\_{\\text{true}} \\approx 84.1959^\\circ

**Note:** Record the source/epoch of \\delta. This is a normal audit step in field books.

---

## **3\) Pick distance d and reduce to \\Delta N, \\Delta E**

Use Robinson/Flint rectangular reduction:

\\Delta N \= d \\cos \\theta\_{\\text{true}},\\qquad \\Delta E \= d \\sin \\theta\_{\\text{true}}

Two common choices:

* **Unit course** (d \= 1): yields a **direction vector** you can scale later.

* **Measured/scaled**: pick any d to get a concrete traverse leg.

**Worked example (NE with** \\delta**)**

\\theta\_{\\text{true}} \= 61.6959^\\circ

* d \= 1: \\Delta N \\approx 0.474151,\\ \\Delta E \\approx 0.880443

* d \= 5: \\Delta N \\approx 2.370756,\\ \\Delta E \\approx 4.402217

**Worked example (ENE with** \\delta**)**

\\theta\_{\\text{true}} \= 84.1959^\\circ

* d \= 1: \\Delta N \\approx 0.0999,\\ \\Delta E \\approx 0.9950

* d \= 5: \\Delta N \\approx 0.4995,\\ \\Delta E \\approx 4.9751

**No calculator?** Use a printed trig table (5-place is plenty). Lookup \\cos and \\sin for your \\theta\_{\\text{true}}.

---

## **4\) Write a one-row traverse table**

| Leg | Bearing (true) | Distance d | \\Delta N \= d \\cos \\theta | \\Delta E \= d \\sin \\theta |
| ----- | ----- | ----- | ----- | ----- |
| 1 | N 61.6959^\\circ E | 1 | 0.474151 | 0.880443 |

To re-use this bearing at a different length, scale \\Delta N, \\Delta E by that d.

---

## **5\) Sanity checks & pitfalls**

* **Tail vs head.** The **tail** you decrypted is the **rule**: “*… OF AN ANGLE IS THE ARC*.” The **head** gives a **sector** (NE/ENE/etc.). You **read degrees** from the circle, then compute.

* **Declination sign.** East declination **adds**; west **subtracts**.

* **Sector ≠ exactness.** The sector points you near 45°/67.5°/90°; the **dial** gives the numeric arc you actually use.

* **Units.** Any length unit works; only direction is fixed by the angle.

---

## **6\) Minimal worksheet (printable)**

**PLAZA CIRCLE — WORLD CLOCK WORKSHEET**

Head sector (NE/ENE/E):  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Dial reading θ\_dial (deg):  \_\_\_\_\_\_\_\_.\_\_\_\_

Declination δ (deg, \+E/−W):  \_\_\_\_\_\_\_\_.\_\_\_\_

θ\_true \= θ\_dial \+ δ \=  \_\_\_\_\_\_\_\_.\_\_\_\_  deg

Distance d (units):  \_\_\_\_\_\_\_\_.\_\_\_\_

ΔN \= d·cos(θ\_true) \=  \_\_\_\_\_\_\_\_\_\_\_\_\_

ΔE \= d·sin(θ\_true) \=  \_\_\_\_\_\_\_\_\_\_\_\_\_

Notes: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## **7\) Why this matches the text**

* Your **anchor-driven decryption** produced the tail: **“… OF AN ANGLE IS THE ARC.”**

   That’s **Abel Flint’s** rule: *the measure of an angle is the arc cut off by the rays on a circle*.

* The **head** supplies the **sector** (NE/ENE/E). The **circle** supplies the **degrees**.

   The **field work** is classical: correct to **true**, then **rectangular reduction** (\\Delta N,\\Delta E).

* The **plaza** (circle, meridian, quadrants) is a **surveying plate**. The instruction is operational, not decorative.

---

## **Appendix A — 16-point wind rose (degrees from true north)**

N 0° • NNE 22.5° • NE 45° • ENE 67.5° • E 90° • ESE 112.5° • SE 135° • SSE 157.5° •

S 180° • SSW 202.5° • SW 225° • WSW 247.5° • W 270° • WNW 292.5° • NW 315° • NNW 337.5°

---

## **Appendix B — Using a photo of the Urania World Clock**

1. Print a clear **overhead** (or perfectly level oblique).

2. Draw the **true meridian** (N–S) through the center.

3. Mark the 16-point **tick marks** (22.5° spacing).

4. Read the **NE/ENE** arc for \\theta\_{\\text{dial}}.

5. Compute \\theta\_{\\text{true}} \= \\theta\_{\\text{dial}} \+ \\delta.

6. Reduce: \\Delta N \= d \\cos \\theta\_{\\text{true}},\\ \\Delta E \= d \\sin \\theta\_{\\text{true}}.

On site: stand on the meridian, sight ENE, read the arc, then do the table work.

---

### **Historical note (why K5 matters)**

K4’s cryptography (anchors → six short wheels) produced the **tail** arithmetically. **K5** is “what you do next”: interpret the **head’s sector** on a **real circle**, correct for declination, and run a **rectangular traverse**. This document is deliberately **pencil-friendly** so a 1989 cryptographer can complete the operation without any digital tools.
