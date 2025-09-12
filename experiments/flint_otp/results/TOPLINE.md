# FLINT AS OTP KEY - TOPLINE RESULTS

## Summary

**RESULT: All candidates FAILED anchor constraints.**

| Candidate | Page | Vigenère | Beaufort | Notes |
|-----------|------|----------|----------|-------|
| A | 59 | ✗ FAIL | ✗ FAIL | Anchors fail |
| B | 59 | ✗ FAIL | ✗ FAIL | Anchors fail |
| C | 61 | ✗ FAIL | ✗ FAIL | Anchors fail |
| D | 18 | ✗ FAIL | ✗ FAIL | Anchors fail |
| E | 52 | ✗ FAIL | ✗ FAIL | Anchors fail |

## Conclusion

All five hand-picked 97-character Flint keys fail to satisfy the hard anchor constraints (EAST @ 21-24, NORTHEAST @ 25-33, BERLIN @ 63-68, CLOCK @ 69-73) under both Vigenère (P = C - K) and Beaufort (P = K - C) decoding.

This definitively rules out these specific Flint passages as direct OTP key material for K4.
