# Undetermined Positions Map

## Overview

This visualization shows which positions in the K4 plaintext are determined by anchors alone (green) versus which remain undetermined (red) without the tail.

## Key Findings

- **Total positions**: 97
- **Anchor-constrained**: 24 positions
- **Undetermined**: 73 positions
- **Tail region (75-96)**: 22 undetermined positions

## Visualization

The UND_MAP.svg shows:
- X-axis: Position indices (0-96)
- Y-axis: Classes (0-5) based on baseline skeleton formula
- Green circles: Positions constrained by anchors
- Red circles: Undetermined positions requiring tail
- Light blue background: Tail region (positions 75-96)

## Key Insight

Undetermined positions are distributed evenly across all 6 classes, with concentration in the gaps between anchor spans. The tail region (75-96) is entirely undetermined under anchors-only constraints, confirming the algebraic necessity of the tail for unique solution determination.
