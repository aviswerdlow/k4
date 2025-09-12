# Adjacent Frame Variants Analysis

**Date**: 2025-09-04
**Seed**: 1337

## Variants Tested

| Variant | Description | Status |
|---------|-------------|--------|
| AND with POS 0.80 | Stricter Generic threshold (0.80 vs 0.60) | ✓ |
| Full Deck with AND | All routes enabled (GRID + SPOKE + RAILFENCE + HALF) | ✓ |
| OR with Strict Generic | OR gate with top-0.5% perplexity | ✓ |

## Claim Boundary

The published result uses:
- GRID-only routes (W14_ROWS, W10_NW)
- AND gate (Flint v2 ∧ Generic)
- Head-only decision (positions 0-74)
- Null hypothesis testing with Holm correction

These adjacent frames test variations outside this boundary.
