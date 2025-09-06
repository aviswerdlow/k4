# FROZEN SCHEDULE FOR BLINDED_CH00_I003

## Route
- **File**: GRID_W14_ROWS.json
- **SHA-256**: a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31
- **Type**: NA-only permutation with fixed anchors

## Classing
- **Method**: c6a
- **Formula**: class_id(i) = ((i % 2) * 3) + (i % 3) for i ∈ [0..96]

## Schedule (FROZEN)
| Class | Family | Period (L) | Phase |
|-------|--------|------------|-------|
| 0 | vigenere | 17 | 0 |
| 1 | vigenere | 16 | 0 |
| 2 | beaufort | 16 | 0 |
| 3 | vigenere | 16 | 0 |
| 4 | **beaufort** | 19 | 0 |
| 5 | beaufort | 20 | 0 |

**Critical**: Class 4 is Beaufort (not Vigenère) to avoid K=0 at position 73

## Anchors (Option-A verified)
- **EAST**: positions [21:25]
- **NORTHEAST**: positions [25:34]
- **BERLINCLOCK**: positions [63:74]

## Plaintext
- **SHA-256**: cfa9d8b879ede8f99574d41d541f6abe53387df984c9e9c802be066a9ce885f6
- **Length**: 97 chars
- **Head**: [0:75] with anchors embedded
- **Tail**: [75:97] with 'A' placeholders

## Ciphertext
- **K4 CT SHA-256**: eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab
- **Verified**: encrypts_to_ct = TRUE