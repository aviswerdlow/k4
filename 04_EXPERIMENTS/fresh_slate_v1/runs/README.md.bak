# Fresh-Slate Run Results

## Summary of Baseline Runs

All runs use the baseline classing: `class(i) = ((i % 2) * 3) + (i % 3)`

### baseline_four_anchors
- **Cribs**: EAST, NORTHEAST, BERLIN, CLOCK  
- **Derived**: 71 letters
- **Undetermined**: 26 positions
- **Key insight**: Maximum information from all 4 known cribs

### baseline_three_no_berlin
- **Cribs**: EAST, NORTHEAST, CLOCK
- **Derived**: 58 letters  
- **Undetermined**: 39 positions
- **Key insight**: Dropping BERLIN loses 13 derivable positions

### baseline_three_no_clock
- **Cribs**: EAST, NORTHEAST, BERLIN
- **Derived**: 57 letters
- **Undetermined**: 40 positions  
- **Key insight**: Dropping CLOCK loses 14 derivable positions

### baseline_two_east_ne
- **Cribs**: EAST, NORTHEAST only
- **Derived**: 43 letters
- **Undetermined**: 54 positions
- **Key insight**: With only 2 cribs, over half the plaintext is undetermined

## What This Shows

The derivation is **strictly deterministic** based on cribs provided:
- No hypothesis scaffolding
- No phrase guessing
- No AI involvement
- Unknown positions remain "?" 

Each additional crib adds ~14-15 derivable positions through the wheel slots it determines.