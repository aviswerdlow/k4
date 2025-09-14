# Notes on Hörenberg K4 Mapping Conventions

## Critical Discovery: R27-31 Pass-Through Convention

The key to exact reproduction of Hörenberg's Layer 2 was discovering that XOR results in the range 27-31 are treated as **pass-through** (outputting the cipher letter C), not cyclically mapped as initially assumed.

### Why This Matters

Standard 5-bit XOR can produce values 0-31:
- 0: Traditional pass-through (discriminator)
- 1-26: Map to letters A-Z
- 27-31: **Ambiguous range** - no standard letters

Hörenberg's solution: Treat 27-31 like pass-through, outputting C.

### Evidence

All 17 "mismatches" in initial recovery showed:
- Our recovery: Pass-through (K=C, r=0)
- Hörenberg's K: Different letter producing r∈{27,28,29,30,31}
- Hörenberg's P: Shows cipher letter (confirming pass-through behavior)

Example at position 11:
- C = L, K_published = W
- r = L⊕W = 12⊕23 = 27
- P = L (cipher letter output, not A which would be cyclic)

## Layer 2 XOR Mapping (Confirmed)

```python
def xor5_hoerenberg(C, K):
    r = code5(C) ^ code5(K)  # A=1..Z=26

    if r == 0:
        return C  # Standard pass-through
    elif 1 <= r <= 26:
        return letter(r)  # Normal letter
    else:  # r in {27,28,29,30,31}
        return C  # SPECIAL: Also pass-through!
```

## Layer 1 Base-5 Mapping (Partially Confirmed)

### CIAW Example (Confirmed)
- Alphabet: DROP-X (no X)
- Operation: **Addition** modulo 5 per digit
- Formula: `P_digit = (C_digit + K_digit) % 5`

### CIAX Example (Cannot Reproduce)
- Claimed: Drop-J alphabet with OBKR key
- Reality: No configuration produces CIAX
- Conclusion: Idealized or different data

### CULDWW Example (Cannot Reproduce)
- Claimed: MDXBSF - CIAXCI
- Reality: No configuration found
- Conclusion: Idealized or different data

## Keystream Structure

Hörenberg's K is **manually constructed**, not algorithmic:

1. **Segment 1** (chars 0-30, 31 total)
   - Starts at F in tableau
   - Ends with ...HIN

2. **Segment 2** (chars 31-62, 32 total)
   - Starts with G (jump from N)
   - Contains extra L at position 61
   - Ends with ...LO

3. **Segment 3** (chars 63-92, 30 total)
   - Starts with H (jump from O)
   - Ends with ...JL

The irregular jumps (N→G, O→H) and specific L placement indicate manual selection to create R27-31 values at specific positions.

## Implementation Notes

### Correct Implementation
```python
# Layer 2 XOR
from xor5_hoerenberg import xor5_string_hoerenberg
p = xor5_string_hoerenberg(c, k)  # Uses R27-31 pass-through

# Layer 1 Base-5 (CIAW only)
# Use drop-X alphabet with addition
```

### Common Mistakes
1. **Wrong R27-31 handling**: Cyclic mapping gives wrong P
2. **Wrong Layer 1 operation**: Subtraction doesn't work for CIAW
3. **Wrong alphabet**: Drop-J makes CIAX impossible (no X)

## Validation Metrics

| Layer | Metric | Target | Status |
|-------|--------|--------|--------|
| Layer 2 | P string | Exact match | ✅ |
| Layer 2 | IoC | 0.06077606 | ✅ |
| Layer 2 | Pass-throughs | 19 (2+17) | ✅ |
| Layer 1 | CIAW | Exact match | ✅ |
| Layer 1 | CIAX | Cannot reproduce | ❌ |
| Layer 1 | CULDWW | Cannot reproduce | ❌ |

## Conclusion

The Hörenberg approach is partially reproducible:
- **Layer 2**: 100% exact with R27-31 pass-through convention
- **Layer 1**: 33% (only CIAW works)

The approach demonstrates IoC improvement but uses manual construction and idealized examples rather than a complete algorithmic K4 solution.