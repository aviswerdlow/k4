# Minimum Constraints Proof for L=17

## Mathematical Proof

### 1. One-to-One Mapping Property
With L=17 and 97 positions:
- Each position i maps to (class(i), i mod 17)
- This creates 97 unique (class, slot) pairs
- Each pair appears exactly 1 time

### 2. Constraint Propagation
Under one-to-one mapping:
- Each constrained position determines exactly one wheel slot
- Each wheel slot determines at most one position
- No constraint can 'cover' multiple unknowns

### 3. Set-Cover Reduction
- Universe U = 50 unknown positions
- Each constraint covers exactly 1 element of U
- Minimum cover size = |U| = 50

## Empirical Confirmation

| Test | Additional Constraints | Result |
|------|------------------------|--------|
| all_50_unknowns | 50 | ✓ Closed |
| random_49_trial_1 | 49 | 96/97 |
| random_49_trial_2 | 49 | 96/97 |
| random_49_trial_3 | 49 | 96/97 |
| random_45_trial_1 | 45 | 92/97 |
| random_45_trial_2 | 45 | 92/97 |
| random_45_trial_3 | 45 | 92/97 |

## Conclusion

**Minimum additional constraints required: 50**

This is mathematically necessary and empirically confirmed.
