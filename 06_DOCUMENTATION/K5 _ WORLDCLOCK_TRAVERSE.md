This document shows how to use a round dial (e.g., the **Urania World Clock** at Alexanderplatz, a.k.a. the “Berlin world clock”) as your surveying circle to go from **ciphertext → plaintext instruction → bearing → rectangular reduction**. 

---

# **From “World Clock” to Traverse: a pencil-and-paper guide**

**TL;DR**  
 Treat a round plaza dial (e.g., the Urania World Clock) as your **surveying circle**.

1. Read a **direction as an arc** in the named sector (e.g., EAST NORTHEAST).

2. Correct that direction to **true** with magnetic **declination** (δ).

3. Choose or measure a **distance** `d`.

4. Reduce to rectangular components:  
    ΔN=d⋅cos⁡(θtrue),ΔE=d⋅sin⁡(θtrue)\\Delta N \= d\\cdot \\cos(\\theta\_{\\text{true}}),\\quad \\Delta E \= d\\cdot \\sin(\\theta\_{\\text{true}})

That’s the entire traverse step.

This note assumes you already verified the 97-character plaintext instruction under rails (anchors fixed; tail locked) and now want to carry out the **surveying interpretation** by hand.

---

## **0\) Inputs you’ll need**

* **Plaintext (97 letters; A..Z)** you’ve verified under rails — example:  
   `WECANSEETHETEXTISREALEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC`

* **Direction phrase** in the head (0..74) — example: `EAST NORTHEAST` (ENE sector implied).

* **Declination** δ at your location/epoch (east positive, west negative). If you don’t have a specific date, you can use the illustrative value **\+16.6959°** that we’ve logged previously.

* **A distance** `d`. The text doesn’t encode one; you either:

  * adopt a **unit** distance (d \= 1\) to get a direction vector, or

  * **measure** a yard length (pace it or use a plan scale), or

  * choose a conventional demo number (e.g., d \= 5).

Optional: a printed overhead photo of the **Urania World Clock** (or any clear round dial), a square, a protractor, and a pencil.

---

## **1\) Read the direction as an arc on the circle**

1. Draw or print a circle with **north** at the top (0°/360°), **east** at 90°, **south** at 180°, **west** at 270°.  
    A 16-point wind rose divides the circle every 22.5°:

| Point | Deg | Point | Deg | Point | Deg | Point | Deg |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| N | 0.0 | ENE | 67.5 | S | 180.0 | WNW | 292.5 |
| NNE | 22.5 | E | 90.0 | SSW | 202.5 | W | 270.0 |
| NE | 45.0 | ESE | 112.5 | SW | 225.0 | WSW | 247.5 |
| NEE \= NE | 45.0 (alias) | SE | 135.0 | WSW | 247.5 | NW | 315.0 |
| NEE/ENE pair | 45–67.5 |  |  |  |  |  |  |

2.   
   Locate the **named sector**.

   * If the line says **EAST NORTHEAST**, read the arc in/near **ENE \= 67.5°**.

   * If it says **NORTHEAST**, read near **45.0°**.  
      Use the dial’s tick marks or a protractor on your printout.

**Arc, not words.** The plaza dial is a surveying limb. You **read an arc** (degrees on the circle), then convert that into a bearing.

---

## **2\) Correct to the true meridian (declination δ)**

Take your dial reading `θ_dial` and apply local **declination** (east positive):

 θtrue=θdial+δ \\boxed{\\ \\theta\_{\\text{true}} \= \\theta\_{\\text{dial}} \+ \\delta\\ }

* Example A (NE): `θ_dial = 45.0°`, `δ = +16.6959°` → `θ_true ≈ 61.6959°`

* Example B (ENE): `θ_dial = 67.5°`, `δ = +16.6959°` → `θ_true ≈ 84.1959°`

If you don’t have a dated δ, pick the one you’re using elsewhere and **record it**; this is an audit step, not a trick.

---

## **3\) Pick a distance `d` and reduce to ΔN/ΔE**

Rectangular reduction (Robinson/Flint):

ΔN=d⋅cos⁡(θtrue),ΔE=d⋅sin⁡(θtrue)\\Delta N \= d\\cdot \\cos(\\theta\_{\\text{true}}),\\quad \\Delta E \= d\\cdot \\sin(\\theta\_{\\text{true}})

Two standard choices:

* **Unit course** (d \= 1): gives a **direction vector** you can scale later.

* **Measured/scaled course**: choose any d to get a concrete traverse row.

**Worked example (NE \+ δ):**  
 Use `θ_true = 61.6959°`.

* Unit course:  
   `ΔN_unit ≈ cos(61.6959°) ≈ 0.474151`  
   `ΔE_unit ≈ sin(61.6959°) ≈ 0.880443`

* For **d \= 5** (demo distance):  
   `ΔN ≈ 5 × 0.474151 = 2.370756`  
   `ΔE ≈ 5 × 0.880443 = 4.402217`

**Worked example (ENE \+ δ):**  
 Use `θ_true = 84.1959°`.

* Unit course: `ΔN_unit ≈ 0.0999`, `ΔE_unit ≈ 0.9950`

* For **d \= 5**: `ΔN ≈ 0.4995`, `ΔE ≈ 4.9751`

Both are correct **methods**; your `θ_true` depends on the sector you read (NE vs ENE) and the δ you chose.

---

## **4\) Write a one-row “traverse table”**

| Leg | Bearing (true) | Distance d | ΔN \= d·cosθ | ΔE \= d·sinθ |
| ----- | ----- | ----- | ----- | ----- |
| 1 | N 61.6959° E | 1 | 0.474151 | 0.880443 |

To use a **different** distance, just multiply ΔN/ΔE by that d.

---

## **5\) Sanity checks & common pitfalls**

* **Head vs tail.** The **tail** is already the textbook rule: “**… OF AN ANGLE IS THE ARC**.” You act on it by reading the arc on the circle; you don’t need a distance word in the head.

* **Declination sign.** East declination **adds**; west **subtracts**. Note epoch & location.

* **Sector vs exact degree.** The words (NE, ENE, EAST) pick a **sector**. The **circle** gives you the numeric arc.

* **Units.** Any distance unit works (pace, meters, rods) — the **direction** is the point, the traverse just scales it.

---

## **6\) Minimal worksheet (printable)**

PLAZA CIRCLE — WORLD CLOCK WORKSHEET

\------------------------------------

Head sector (circle):  \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_   (e.g., NE, ENE)

Dial reading θ\_dial:   \_\_\_\_\_\_\_.\_\_\_\_   degrees

Declination δ (epoch): \_\_\_\_\_\_\_.\_\_\_\_   degrees   (+E / \-W)

θ\_true \= θ\_dial \+ δ \=  \_\_\_\_\_\_\_.\_\_\_\_   degrees

Distance d (unit):     \_\_\_\_\_\_\_.\_\_\_\_

ΔN \= d·cos(θ\_true) \=   \_\_\_\_\_\_\_.\_\_\_\_\_\_   (northings)

ΔE \= d·sin(θ\_true) \=   \_\_\_\_\_\_\_.\_\_\_\_\_\_   (eastings)

Notes: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## **7\) Why this matches the text**

* The instruction **tells you to read an arc** (“the measure of an angle is the arc”).

* Direction tokens like **EAST NORTHEAST** refer to **sectors on the circle**, not wordplay.

* The plaza’s form is a **surveying plate**: circle/meridian/quadrants. After reading the arc, you do what a 19th-century field book says:

  * correct to **true** (declination),

  * reduce to **ΔN/ΔE** (rectangular surveying),

  * and proceed (offsets/intersections as needed) — all without needing the word “ROD.”

---

### **Appendix A — 16-point wind rose (degrees from true north)**

N 0° • NNE 22.5° • NE 45° • ENE 67.5° • E 90° • ESE 112.5° • SE 135° • SSE 157.5° •  
 S 180° • SSW 202.5° • SW 225° • WSW 247.5° • W 270° • WNW 292.5° • NW 315° • NNW 337.5°

---

### **Appendix B — If you’re using a photo of the Urania World Clock**

1. Print a clear, overhead view (or a perfectly level oblique).

2. Draw the **meridian** (north–south line) through the center.

3. Mark the 16-point ticks (every 22.5°).

4. Read **NE** or **ENE** arc as needed; measure `θ_dial`.

5. Apply `θ_true = θ_dial + δ`, then reduce.

If you can get an on-site reading, you can literally stand on the meridian line, sight the ENE sector, and read the arc from the dial.

---

That’s all a pencil-and-paper cryptographer needs: a circle, a declination, a distance, and the two lines of trigonometry. The cryptography proved the **letters**; the plaza (plus Flint) tells you **what to do** with them.

