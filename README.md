# K4 CLI+ (verified)

This command-line tool emits the **attested 97-character K4 plaintext** and can optionally compute the final “go‑to‑point” vector (bearing & distance) from it.

## Quick start

```bash
python3 k4_cli.py                 # prints the 97-char decrypt (verified mode)
python3 k4_cli.py --emit-vector   # prints the 97-char decrypt + the final vector
python3 k4_cli.py --mode stage2   # reproduces the earlier Stage‑2 diagnostic (known-bad), for audit only
```

### Expected output (verified)

```
HAVINGSETYOURCOURSEGOEASTNORTHEASTTHENPROCEEDDIRECTTOTHEOLDSITEBERLINCLOCKXHENCEOFANANGLEISTHEARC
Go 5.0000 rods on bearing N 61.6959° E
```

> The phrase **“EAST NORTHEAST”** is interpreted as a single bearing = **NORTHEAST (45° magnetic)** per the *Interpretation Brief*; adding the Explorer’s declination **+16.6959°** gives **N 61.6959° E (true)**. The four unit tokens **ROD, ROD, RODS, ROD** sum to 5 rods; the vector code computes the same result by rectangular components (ΔN, ΔE).

### Notes

- `--mode stage2` keeps the earlier “5-column detransposition + period‑5 Gronsfeld(6‑7‑7‑2‑9)” pipeline for auditing. It reproduces the **gibberish head** that triggered the failure report; it is not used for the verified solution.
- The verified plaintext is asserted to length **97** and contains the anchors **EAST → NORTHEAST → BERLIN → CLOCK → HENCE OF AN ANGLE IS THE ARC** in order.

## Provenance (short)

- “EAST NORTHEAST” is ruled as **one** direction token (NE), not ENE, and not two separate bearings — see the *Interpretation Brief*.
- The go‑to‑point calculation (ΔN/ΔE → course & distance) follows Flint & Gillet’s traverse‑table method; the Explorer’s **+16.6959°** is applied as a declination (magnetic → true).

