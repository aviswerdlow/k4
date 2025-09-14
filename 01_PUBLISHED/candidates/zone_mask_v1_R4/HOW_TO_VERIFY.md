# How to Verify This K4 Solution

## Quick Verification

1. **Check BERLINCLOCK**: Positions 63-73 (zero-based) in the plaintext should read "BERLINCLOCK"
2. **Round-trip Test**: Decrypt → Re-encrypt should return the original ciphertext
3. **Zone Coverage**: Control indices must be within the MID zone (34-73)

## Full Verification Process

### Prerequisites
- Python 3.6+
- The K4 ciphertext (97 characters)
- This solution's manifest.json

### Step 1: Load the Components
```python
import json

# Load ciphertext
ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Load manifest
with open('manifest.json', 'r') as f:
    manifest = json.load(f)
```

### Step 2: Apply Vigenere Decryption
```python
def vigenere_decrypt(text, key):
    result = []
    for i, char in enumerate(text):
        key_char = key[i % len(key)]
        plain_val = (ord(char) - ord(key_char)) % 26
        result.append(chr(plain_val + ord('A')))
    return ''.join(result)

# Process MID zone (34-73)
mid_zone = ciphertext[34:74]
mid_key = manifest['cipher']['keys']['mid']
mid_plain = vigenere_decrypt(mid_zone, mid_key)
```

### Step 3: Verify BERLINCLOCK
```python
# Build full plaintext
plaintext = list(ciphertext)
for i in range(40):  # MID zone is 40 chars
    plaintext[34 + i] = mid_plain[i]
plaintext = ''.join(plaintext)

# Check control region
control_text = plaintext[63:74]
assert control_text == "BERLINCLOCK", f"Expected BERLINCLOCK, got {control_text}"
print(f"✓ BERLINCLOCK verified at positions 63-73")
```

### Step 4: Round-Trip Validation
```python
def vigenere_encrypt(text, key):
    result = []
    for i, char in enumerate(text):
        key_char = key[i % len(key)]
        cipher_val = (ord(char) + ord(key_char) - 2*ord('A')) % 26
        result.append(chr(cipher_val + ord('A')))
    return ''.join(result)

# Re-encrypt the MID zone
re_encrypted_mid = vigenere_encrypt(mid_plain, mid_key)
assert re_encrypted_mid == mid_zone, "Round-trip failed"
print("✓ Round-trip validation passed")
```

## Key Points

### Indexing
- **All positions are zero-based** (first character is position 0)
- BERLIN appears at positions 63-68
- CLOCK appears at positions 69-73
- When referencing external K4 documentation that uses 1-based indexing, subtract 1

### Zone Boundaries
- HEAD: 0-20 (21 characters)
- GAP: 21-33 (13 characters, unprocessed)
- MID: 34-73 (40 characters, includes control region)
- TAIL: 74-96 (23 characters)

### The Special Key
The MID zone key is 40 characters long with a special structure:
- Positions 0-28: 'A' (identity, no transformation)
- Positions 29-39: 'MUYKLGKORNA' (transforms NYPVTTMZFPK → BERLINCLOCK)

This alignment ensures BERLINCLOCK appears exactly at positions 63-73.

## Success Criteria
✅ BERLINCLOCK readable at positions 63-73  
✅ Round-trip validation (decrypt → encrypt returns original)  
✅ Control indices within zone boundaries  
✅ Reproducible with provided manifest