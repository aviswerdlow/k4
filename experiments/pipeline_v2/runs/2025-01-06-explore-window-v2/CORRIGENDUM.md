# Corrigendum: Window Sweep v2

## Issue Fixed

Windowed anchor scoring was previously a no-op (blinding occurred without window search).
This run implements position/typo-aware windowed scoring per policy (see anchor_score.py).

## Changes Made

1. Implemented `anchor_score.py` with proper window search
2. Created `compute_score_v2.py` that scores anchors BEFORE blinding
3. Updated policies with `anchor_scoring` configuration
4. Unit tests pass (see `test_anchor_score.py`)

## Impact

All windowed results in prior runs are superseded by this folder's artifacts.
Deltas should now be non-zero when anchors shift position.

Generated: 2025-09-05T23:16:55.551441
