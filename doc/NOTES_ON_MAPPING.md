# Notes on Mapping: R27-31 Convention

## The Critical Discovery

When implementing Hörenberg's 5-bit XOR, we discovered that values 27-31 require special handling:

```python
def xor5_hoerenberg(ct_letter, key_letter):
    r = ct_code ^ key_code  # 5-bit XOR

    if r == 0:
        return ct_letter  # Standard pass-through
    elif 1 <= r <= 26:
        return code5_to_letter(r)  # Normal letter
    else:  # r in 27-31
        return ct_letter  # SPECIAL pass-through!
```

## Why This Matters

### Initial Assumption (WRONG)
We first tried cyclic mapping: `(r - 1) % 26 + 1`
- This would map 27→1 (A), 28→2 (B), etc.
- Result: IoC mismatch, P string incorrect

### Actual Convention (CORRECT)
Values 27-31 are treated as pass-through (output C)
- This creates additional pass-through positions beyond r=0
- Result: EXACT match with Hörenberg's P and IoC

## Evidence

Position-by-position comparison showed mismatches that resolved when treating 27-31 as pass-through:

```
Position 5: C='U', K='N'
  U(21) ⊕ N(14) = 27
  Cyclic: 27→A  ✗ (Hörenberg has 'U')
  Pass-through: 27→U  ✓ (Matches!)
```

## Keystream Summary

The keystream isn't algorithmically generated but uses three fixed segments:

1. **Segment 1 (0-30)**: `FGHIJLMNQUVWXZKRYPTOSABCDEFGHIN`
2. **Segment 2 (31-61)**: `GHIJLMNQUVWXZKRYPTOSABCDEFGHIJL`
3. **Segment 3 (62-92)**: `OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL`

These appear to be modified KRYPTOS tableau rows with specific letter injections.

## Validation

The R27-31 convention is validated by:
- Exact P string reproduction
- Exact IoC match (0.06077606)
- Consistent behavior across all test positions

This convention is now encoded in `xor5_hoerenberg.py` and tested in `test_exact_convention.py`.