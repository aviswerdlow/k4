# Flint & Gillet — Author's Style Guide (for Cover Text Construction)
*Prepared: 2025-08-28*

This guide distills the idiom, cadence, and sentence mechanics of **Abel Flint & George Gillet** so the Architect can compose cover text that reads as authentic nineteenth‑century prose while naturally housing our anchors and recovered seam clause.

---

## 1) Voice & Register
- **Formal textbook diction**, impersonal narrator (“Let one leg be made radius…”; “Hence the following rule.”).
- **Imperative procedures** for surveying steps (“Assume a meridian… compute latitude and departure.”).
- Frequent **discourse particles**: *hence, therefore, whence, thus, from the preceding*.
- **Cadenced repetition** in instructions: “In like manner… Continue the operation…”
- **Quarter‑mark regularity** and **table language** (quarter degrees; traverse table).

## 2) Sentence Patterns
- **Definition form**: “The [measure/term] is the [geometric object] …”  
  e.g., “The measure of an angle is the arc of a circle.”
- **Construction form**: “Let [part] be made radius; then [consequence].”
- **Rule form**: “When [condition], take the complement/supplement as the rules direct.”
- **Surveying cadence**: “Assume a meridian; from each bearing and distance compute [ΔLat, ΔDep].”
- **Observation form**: “As the magnetic needle now points, the variation must be applied …”

## 3) Vocabulary & Collocations
Core terms: *angle, arc, chord, radius, degree, sine, cosine, tangent, secant, complement, supplement, quadrant, meridian, bearing, course, traverse, difference of latitude, departure, scale of chords, protractor*.

Linkers: *hence, therefore, whence, thence, having, from the preceding, in like manner*.  
Time/table: *at each quarter, proceed by equal intervals, to quarter degrees*.

## 4) Anchor Weaving (target order & locations in the 97‑char string)
- `EAST` @ 21–24  
- `NORTHEAST` @ 25–33  
- `BERLIN` @ 63–68  
- `CLOCK` @ 69–73  
- Seam clause `OF AN ANGLE IS THE ARC` @ 80–96

### Bridging strategy
- **Before EAST**: use a procedural lead‑in (“Assume a meridian; proceed …”).  
- **EAST → NORTHEAST**: treat as a single navigational phrase (“EAST NORTHEAST”).  
- **NORTHEAST → BERLIN**: survey cadence (“… set your course; thence to the BERLIN …”).  
- **BERLIN → CLOCK**: preface with an article (“the BERLIN CLOCK”).  
- **CLOCK → seam**: definition cadence (“… the measure of an angle is the arc”).

## 5) Phrase Book (selected)
See `flint_gillet_phrasebook.csv` (generated with ≤25‑word snippets and idioms). Use these units to assemble cover text.

## 6) Ready‑to‑use Scaffolds
Authentic‑sounding sentences that include all anchors in order and dovetail into the seam clause are provided in `anchor_scaffolds.csv`.

**Example**  
“Proceed EAST NORTHEAST; at the BERLIN CLOCK the measure of an angle is the arc.”

## 7) Style Do/Don't
- **Do** prefer semicolons over commas when linking independent clauses.  
- **Do** front‑load conditions with *when/if/having*.  
- **Don’t** use modern idioms (*due to*, *utilize*, *parameter*).  
- **Don’t** switch to first person.

---

## 8) Canonical 97‑char baseline (for alignment reference)
```
QVIHUPXCMJKAVIAUVFCCXEASTNORTHEASTOHCVGHDGEBRKAAXZIKIISFKUUYNGBBERLINCLOCKXHEJOYOFANANGLEISTHEARC
```

Use this guide to craft coherent Flint‑&‑Gillet prose that can house the fixed anchors and our seam while leaving room for the Rule Engine–driven micro‑keys.
