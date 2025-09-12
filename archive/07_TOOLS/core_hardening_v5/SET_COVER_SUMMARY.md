# Set-Cover Analysis Summary

## Key Findings

- **Anchors determine**: 24/97 positions
- **Slots forced by anchors**: 24
- **Slots still needed**: 73
- **Minimal additional positions required**: **73**
- **Tail region (74-96)**: 23 positions
- **Tail coverage**: 23/73 slots (31.5%)

⚠ The 23-position tail may not be sufficient (minimal requirement is 73)

## Interpretation

The set-cover analysis shows that beyond the 4 anchors, at least 73 additional plaintext positions must be constrained to algebraically determine all 97 positions under the L=17 mechanism.

This is a hard mathematical lower bound - no amount of algebraic manipulation can reduce it without additional information.
