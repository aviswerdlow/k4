# How Abel Flint ties into the K4 decrypt (tail-first → plaza → method)

**TL;DR:** The tail `… OF AN ANGLE IS THE ARC` is the textbook rule for reading a surveying circle. That revealed the yard as a worked plate from a 19th-century surveying book: read a **direction as an arc**, then do what field books prescribe next.

## First principles mapping

- **Circle & arcs** → "*the measure of an angle is the arc*" (Robinson/Flint).  
- **"EAST NORTHEAST"** → a bearing sector: stand on the meridian; take the arc into ENE.  
- **Bearing → coordinates** → rectangular surveying: ΔN = d·cos(θ_true), ΔE = d·sin(θ_true).  
- **Declination** → correct the magnetic needle (and local attraction) before trusting a compass bearing.  
- **Offsets & intersections** → keep geometry honest when the straight path is blocked; reduce back to the meridian.

## Why we locked the tail
Once the tail decrypted to the literal textbook clause, we locked:
- `75–79 = HEJOY` (no inner cuts)  
- `80–96 = OF · AN · ANGLE · IS · THE · ARC` with seam cuts `[81,83,88,90,93]`.

These constraints apply to every subsequent candidate.

## The Abel-Flint gate (v2): semantics, not fixed strings

We don't require an exact phrase like "SET THE COURSE TRUE." We look for:

1) A **declination-correction idea** (any of: "set … course … true (meridian)", "correct … bearing … to true", "reduce … course … to the true line", "apply declination / bring to true meridian") in **0..74**.

2) **Then** an **instrument action** (READ / SEE / NOTE / SIGHT / OBSERVE) occurs **after** that expression.

3) **Direction tokens** EAST and NORTHEAST appear.

4) An **instrument noun** is whitelisted (BERLIN / CLOCK / BERLINCLOCK / DIAL).

5) Clause health: content ≥ 6; no non-anchor content token repeats > 2.

We accept a submission if **this gate OR the generic English gate** passes; a publishable result must still beat 10k mirrored nulls (Holm adj-p < 0.01).