# Alternates Exploration

## Overview

This experiment explores alternate K4 candidates within and adjacent to the published claim boundary (GRID-only + AND gate + head-only + nulls).

## Structure

```
experiments/alternates/
├── data/               # Input data files
│   ├── K4_ct.txt      # K4 ciphertext
│   ├── canonical_cuts.json
│   ├── function_words.txt
│   └── permutations.txt
├── policies/          # Frame configuration files  
│   ├── POLICY.seamfree.and.json       # Baseline (published)
│   ├── POLICY.seamfree.and_pos080.json # Stricter POS
│   ├── POLICY.seamfree.full_deck.json  # All routes
│   └── POLICY.seamfree.or_strict.json  # OR gate
├── scripts/           # Analysis scripts
│   ├── generate_candidates.py  # Create alternates
│   ├── confirm_and_nulls.py   # Test gates and nulls
│   ├── scan_within_frame.py   # Within-frame orchestrator
│   └── run_frame_variant.py   # Adjacent frame tester
├── runs/              # Results by date
│   └── 2025-09-05/
│       ├── frame_and/         # Within-frame results
│       ├── frame_pos080/      # POS 0.80 variant
│       ├── frame_full_deck/   # Full deck variant
│       └── frame_or_strict/   # OR strict variant
└── docs/              # Documentation
    └── ALTERNATES_SUMMARY.md

```

## Quick Start

### Within-Frame Exploration
```bash
# Test surveying-equivalent imperatives
python3 scripts/scan_within_frame.py \
    --policy policies/POLICY.seamfree.and.json \
    --output_dir runs/2025-09-05/frame_and/
```

### Adjacent Frames
```bash
# Test all frame variants
python3 scripts/run_frame_variant.py \
    --all \
    --output_dir runs/2025-09-05/
```

## Key Findings

1. **No alternates within frame**: The published result is unique within GRID-only + AND
2. **OR gate admits more candidates**: 6 pass gate vs 0 for AND, but all fail nulls
3. **Stricter thresholds eliminate all**: POS 0.80 filters everything
4. **Route expansion doesn't matter**: Full deck behaves like GRID-only

## Reproducibility

- Seed: 1337 (deterministic)
- Bootstrap: K=10000 nulls
- Holm correction: m=2
- All results verifiable via SHA-256 manifests

## Claim Boundary

The published result operates within:
- Routes: GRID-only (W14_ROWS, W10_NW)
- Gate: AND (Flint v2 ∧ Generic)
- Decision: Head-only (0-74)
- Validation: Nulls with Holm

This exploration confirms no equivalents exist within this boundary.