# k4_cli_plus_v2

Deterministic command‑line verifier for the Kryptos tail. It prints the vetted 97‑character plaintext and, optionally, the “go‑to‑point” vector computed from the Stage‑1 text that contains the ROD/RODS tokens.

## Quick start

```bash
python3 k4_cli.py
python3 k4_cli.py --emit-vector
python3 k4_cli.py --emit-vector --vector-source stage1   # force Stage‑1 parsing
```

## What changed in v2 (fix for `--emit-vector`)

The previous build attempted to parse unit tokens (ROD/RODS/LINK/S) from the **final** plaintext, which — by design — no longer contains those tokens, so the vector collapsed to **0 rods / N 0° E**.  
This version defaults `--vector-source` to **auto**, which falls back to the Stage‑1 string **with units** whenever the final plaintext has no units. Result:

```
HAVINGSETYOURCOURSEGOEASTNORTHEASTTHENPROCEEDDIRECTTOTHEOLDSITEBERLINCLOCKXHENCEOFANANGLEISTHEARC
Go 5.0000 rods on bearing N 61.6959° E
```

## Sources (included in `docs/`)

- K4_Intermediate_String_Selection_v1.md
- K4_Stage_2_Decryption_Protocol.md
- The_Survey_Traverse_Algorithm.md
- Key_Dossier_Function_of_the_Angle.md
- Interpretation_Brief_EAST_NORTHEAST.md
- K4_Endgame_Cryptography_Addendum.md
- Authors_Style_Guide.md
- anchor_scaffolds.txt
- PROVENANCE.md
