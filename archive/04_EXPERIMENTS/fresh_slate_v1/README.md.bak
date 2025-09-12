# Fresh-Slate K4 Derivation

This derives K4 from **ciphertext + cribs only**. No AI. No guessing. Just math.

## How It Works

### 6-Track Class System
```
Class 0: 0  6  12 18 24 30 36 42 48 54 60 66 72 78 84 90 96
Class 1:    7  13 19 25 31 37 43 49 55 61 67 73 79 85 91
Class 2: 2  8  14 20 26 32 38 44 50 56 62 68 74 80 86 92
Class 3: 3     15 21 27 33 39 45 51 57 63 69 75 81 87 93
Class 4: 4  10 16 22 28 34 40 46 52 58 64 70 76 82 88 94
Class 5: 5  11 17 23 29 35 41 47 53 59 65 71 77 83 89 95
```
Each position 0-96 goes to one class using: `class = ((i % 2) * 3) + (i % 3)`

### Wheel Example (Class 3)
```
Slot:  0  1  2  3  4  5  6  7  8  9  10 11 12 13
Key:   Q  D  ?  M  ?  ?  H  ?  ?  ?  ?  ?  ?  E
       ↑        ↑        ↑                    ↑
      i=21    i=15     i=63                 i=81
     (EAST)           (BERLIN)               (?)
```
Only crib positions fill slots. Others stay "?".

### Decrypt Rules
- **Vigenère**: P = C - K (mod 26)
- **Beaufort**: P = K - C (mod 26)  
- **Variant**: P = C + K (mod 26)

### Tail Grid (75-96)
```
Position: 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96
Derived:  ?  ?  ?  ?  R  ?  ?  G  X  U  T  ?  J  O  Y  ?  Q  ?  G  M  I  C  H
```
With 4 cribs, ~26 positions remain unknown ("?").

## Results

| Cribs Used | Derived | Unknown |
|------------|---------|---------|
| 4 anchors (EAST, NE, BERLIN, CLOCK) | 71 | 26 |
| 3 anchors (no BERLIN) | 58 | 39 |
| 3 anchors (no CLOCK) | 57 | 40 |
| 2 anchors (EAST, NE) | 43 | 54 |

## Running

```bash
# Derive with 4 anchors
make fresh-baseline-four

# Explain single position
make fresh-explain
```

## What This Proves

The system derives ~71 letters from 4 cribs alone. No phrase guessing. No AI. Just fixed rules applied to ciphertext + declared cribs. The remaining 26 positions stay "?" because their wheel slots weren't touched by the cribs.

This is the "fresh slate" experiment: derive what you can from cribs, leave the rest unknown.