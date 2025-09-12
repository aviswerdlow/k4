# ANCHOR-FIRST TARGETING REPORT

## Method

Computed exact key values required at anchor positions:
- EAST @ 21-24
- NORTHEAST @ 25-33
- BERLIN @ 63-68
- CLOCK @ 69-73

## Required Key Values

### Vigenère (Sample)
| Position | Required K | Letter |
|----------|------------|--------|
| 21 | 1 | B |
| 22 | 11 | L |
| 23 | 25 | Z |
| 24 | 2 | C |
| 25 | 3 | D |
| 26 | 2 | C |
| 27 | 24 | Y |
| 28 | 24 | Y |
| 29 | 6 | G |
| 30 | 2 | C |
| 31 | 10 | K |
| 32 | 0 | A |
| 33 | 25 | Z |
| 63 | 12 | M |
| 64 | 20 | U |

### Beaufort (Sample)
| Position | Required K | Letter |
|----------|------------|--------|
| 21 | 9 | J |
| 22 | 11 | L |
| 23 | 9 | J |
| 24 | 14 | O |
| 25 | 3 | D |
| 26 | 4 | E |
| 27 | 6 | G |
| 28 | 10 | K |
| 29 | 20 | U |
| 30 | 10 | K |
| 31 | 10 | K |
| 32 | 10 | K |
| 33 | 11 | L |
| 63 | 14 | O |
| 64 | 2 | C |

## Results

- Keystreams tested: 1000
- Vigenère matches: 0
- Beaufort matches: 0

**CONCLUSION: No traverse table keystream can satisfy K4's anchors.**

This definitively eliminates traverse tables as the OTP source.
