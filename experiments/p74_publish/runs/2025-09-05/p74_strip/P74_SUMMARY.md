# P[74] Strip Analysis

**Date**: 2025-09-05
**Seed**: 1337
**Position tested**: 74 (0-indexed)
**Context**: ...HIAP[74]THEJOY...

## Results Table

| Letter | Gate | Nulls | Publishable | Tail (75-96) |
|--------|------|-------|-------------|--------------|
| A | ✗ | ✗ | no | GOBEYORHIAATHEJOYOFANA |
| B | ✗ | ✗ | no | GOBEYORHIABTHEJOYOFANA |
| C | ✗ | ✗ | no | GOBEYORHIACTHEJOYOFANA |
| D | ✗ | ✗ | no | GOBEYORHIADTHEJOYOFANA |
| E | ✗ | ✗ | no | GOBEYORHIAETHEJOYOFANA |
| F | ✗ | ✗ | no | GOBEYORHIAFTHEJOYOFANA |
| G | ✗ | ✗ | no | GOBEYORHIAGTHEJOYOFANA |
| H | ✓ | ✗ | no | GOBEYORHIAHTHEJOYOFANA |
| I | ✗ | ✗ | no | GOBEYORHIAITHEJOYOFANA |
| J | ✗ | ✗ | no | GOBEYORHIAJTHEJOYOFANA |
| **K** | **✓** | **✓** | ****YES**** | **GOBEYORHIAKTHEJOYOFANA** |
| L | ✗ | ✗ | no | GOBEYORHIALTHEJOYOFANA |
| M | ✗ | ✗ | no | GOBEYORHIAMTHEJOYOFANA |
| N | ✗ | ✗ | no | GOBEYORHIANTHEJOYOFANA |
| O | ✗ | ✗ | no | GOBEYORHIAOTHEJOYOFANA |
| P | ✗ | ✗ | no | GOBEYORHIAPTHEJOYOFANA |
| Q | ✗ | ✗ | no | GOBEYORHIAQTHEJOYOFANA |
| R | ✗ | ✗ | no | GOBEYORHIARTHEJOYOFANA |
| S | ✗ | ✗ | no | GOBEYORHIASTHEJOYOFANA |
| T | ✓ | ✗ | no | GOBEYORHIATTHEJOYOFANA |
| U | ✗ | ✗ | no | GOBEYORHIAUTHEJOYOFANA |
| V | ✗ | ✗ | no | GOBEYORHIAVTHEJOYOFANA |
| W | ✗ | ✗ | no | GOBEYORHIAWTHEJOYOFANA |
| X | ✗ | ✗ | no | GOBEYORHIAXTHEJOYOFANA |
| Y | ✗ | ✗ | no | GOBEYORHIAYTHEJOYOFANA |
| Z | ✗ | ✗ | no | GOBEYORHIAZTHEJOYOFANA |

## Summary Statistics

- Letters tested: 26 (A-Z)
- Passing phrase gate: 3/26
- Passing nulls: 1/26
- **Publishable letters: K**

## Key Findings

1. **Only 'K' at position 74 yields a publishable result**
2. This confirms the published plaintext uses P[74] = 'K'
3. The boundary word 'THEJOY' is split as THE|JOY in tokenization v2.1
4. Alternative letters either fail the phrase gate or null hypothesis tests

## Interpretation

The P[74] strip analysis confirms that the published solution's use of 'K' at position 74
is **cryptographically forced** rather than an editorial choice. No other letter at this
position produces a plaintext that passes both the phrase gate and null hypothesis tests.

**Report-only analysis; confirms published P[74] = 'K' is unique.**