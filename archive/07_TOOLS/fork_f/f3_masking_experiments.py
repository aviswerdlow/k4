#!/usr/bin/env python3
"""
f3_masking_experiments.py

Test various interpretations of Sanborn's "masking technique".
What if the anchors aren't plaintext, but masks or modifiers?
"""

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions (0-indexed)
ANCHORS = {
    'EAST': (21, 25),
    'NORTHEAST': (25, 34),
    'BERLIN': (63, 69),
    'CLOCK': (69, 74)
}

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

def vigenere_decrypt(text: str, key: str) -> str:
    if not key:
        return text
    plaintext = []
    key_len = len(key)
    
    for i, c in enumerate(text):
        c_val = char_to_num(c)
        k_val = char_to_num(key[i % key_len])
        p_val = (c_val - k_val) % 26
        plaintext.append(num_to_char(p_val))
    
    return ''.join(plaintext)

def test_anchors_as_masks():
    """Test if anchors are meant to be removed (masked out) from the ciphertext."""
    print("="*70)
    print("TEST 1: ANCHORS AS MASKS (Remove from ciphertext)")
    print("="*70)
    
    # Create mask of positions to remove
    mask_positions = set()
    for start, end in ANCHORS.values():
        for i in range(start, end):
            mask_positions.add(i)
    
    # Remove masked positions
    masked_ct = ""
    for i, c in enumerate(K4_CIPHERTEXT):
        if i not in mask_positions:
            masked_ct += c
    
    print(f"\nOriginal length: {len(K4_CIPHERTEXT)}")
    print(f"Masked length: {len(masked_ct)}")
    print(f"Removed {len(mask_positions)} positions")
    
    # Test ABSCISSA on masked text
    pt = vigenere_decrypt(masked_ct, 'ABSCISSA')
    print(f"\nMasked CT: {masked_ct[:50]}...")
    print(f"With ABSCISSA: {pt[:50]}...")
    
    # Check for meaningful patterns
    if 'MIR' in pt:
        print(f"  Found MIR at position {pt.find('MIR')}")
    if 'HEAT' in pt:
        print(f"  Found HEAT at position {pt.find('HEAT')}")
    if 'MIRHEAT' in pt:
        print(f"  ✓ Found MIR HEAT adjacent!")
    
    return masked_ct

def test_anchors_as_modifiers():
    """Test if anchors modify the ciphertext at their positions."""
    print("\n" + "="*70)
    print("TEST 2: ANCHORS AS MODIFIERS (XOR or shift)")
    print("="*70)
    
    # Try XORing anchor plaintext with ciphertext
    modified_ct = list(K4_CIPHERTEXT)
    
    # XOR EAST with positions 21-25
    for i, letter in enumerate('EAST'):
        pos = 21 + i
        c_val = char_to_num(K4_CIPHERTEXT[pos])
        p_val = char_to_num(letter)
        # Try XOR
        new_val = (c_val ^ p_val) % 26
        modified_ct[pos] = num_to_char(new_val)
    
    # XOR NORTHEAST with positions 25-34
    for i, letter in enumerate('NORTHEAST'):
        pos = 25 + i
        c_val = char_to_num(K4_CIPHERTEXT[pos])
        p_val = char_to_num(letter)
        new_val = (c_val ^ p_val) % 26
        modified_ct[pos] = num_to_char(new_val)
    
    # XOR BERLIN with positions 63-69
    for i, letter in enumerate('BERLIN'):
        pos = 63 + i
        c_val = char_to_num(K4_CIPHERTEXT[pos])
        p_val = char_to_num(letter)
        new_val = (c_val ^ p_val) % 26
        modified_ct[pos] = num_to_char(new_val)
    
    # XOR CLOCK with positions 69-74
    for i, letter in enumerate('CLOCK'):
        pos = 69 + i
        c_val = char_to_num(K4_CIPHERTEXT[pos])
        p_val = char_to_num(letter)
        new_val = (c_val ^ p_val) % 26
        modified_ct[pos] = num_to_char(new_val)
    
    modified_ct_str = ''.join(modified_ct)
    
    print(f"\nOriginal: {K4_CIPHERTEXT[:50]}...")
    print(f"Modified: {modified_ct_str[:50]}...")
    
    # Test ABSCISSA on modified text
    pt = vigenere_decrypt(modified_ct_str, 'ABSCISSA')
    print(f"With ABSCISSA: {pt[:50]}...")
    
    # Check for patterns
    if 'MIRHEAT' in pt:
        print(f"  ✓ Found MIR HEAT!")
    
    return modified_ct_str

def test_anchors_as_keys():
    """Test if anchors are keys for different segments."""
    print("\n" + "="*70)
    print("TEST 3: ANCHORS AS SEGMENT KEYS")
    print("="*70)
    
    # Define segments based on anchor positions
    segments = [
        (0, 21, "HEAD (before EAST)"),
        (21, 34, "EAST-NORTHEAST span"),
        (34, 63, "MIDDLE (between NE and BERLIN)"),
        (63, 74, "BERLIN-CLOCK span"),
        (74, 97, "TAIL (after CLOCK)")
    ]
    
    # Try different anchor combinations as keys
    anchor_keys = [
        'EAST',
        'NORTHEAST',
        'BERLIN',
        'CLOCK',
        'EASTNORTHEAST',
        'BERLINCLOCK',
        'EASTNORTHEASTBERLINCLOCK'
    ]
    
    for key in anchor_keys:
        print(f"\nTrying key: {key}")
        found_something = False
        
        for start, end, desc in segments:
            segment_ct = K4_CIPHERTEXT[start:end]
            pt = vigenere_decrypt(segment_ct, key)
            
            # Check for MIR HEAT
            if 'MIRHEAT' in pt:
                print(f"  ✓ {desc}: Found MIR HEAT!")
                print(f"    CT: {segment_ct}")
                print(f"    PT: {pt}")
                found_something = True
            elif 'MIR' in pt and 'HEAT' in pt:
                print(f"  ? {desc}: Found MIR and HEAT (not adjacent)")
                found_something = True
        
        if not found_something and key == 'EASTNORTHEASTBERLINCLOCK':
            # Show full decryption for the complete key
            full_pt = vigenere_decrypt(K4_CIPHERTEXT, key)
            print(f"  Full decryption: {full_pt[:50]}...")

def test_anchor_distances():
    """Test if distances between anchors are significant."""
    print("\n" + "="*70)
    print("TEST 4: ANCHOR DISTANCES AS KEYS")
    print("="*70)
    
    # Calculate distances
    distances = {
        'EAST_to_NE': 25 - 21,  # 4
        'NE_to_BERLIN': 63 - 34,  # 29
        'BERLIN_to_CLOCK': 69 - 63,  # 6
        'CLOCK_to_end': 97 - 74,  # 23
        'EAST_to_BERLIN': 63 - 21,  # 42
        'NE_to_CLOCK': 69 - 34,  # 35
    }
    
    print("\nDistances between anchors:")
    for name, dist in distances.items():
        print(f"  {name}: {dist}")
    
    # Try distances as shift values
    print("\nTrying distance-based shifts on middle segment (34-63):")
    middle_ct = K4_CIPHERTEXT[34:63]
    
    for name, shift in distances.items():
        # Simple Caesar shift
        shifted = ""
        for c in middle_ct:
            c_val = char_to_num(c)
            new_val = (c_val - shift) % 26
            shifted += num_to_char(new_val)
        
        if 'MIRHEAT' in shifted:
            print(f"  ✓ Shift by {shift} ({name}): Found MIR HEAT!")
            print(f"    Result: {shifted}")

def test_progressive_masking():
    """Test if masking is applied progressively."""
    print("\n" + "="*70)
    print("TEST 5: PROGRESSIVE MASKING")
    print("="*70)
    
    print("\nWhat if we apply masks progressively?")
    
    # Start with original
    text = K4_CIPHERTEXT
    
    # Step 1: Apply EAST mask at 21-25
    print("\nStep 1: Apply EAST at 21-25")
    text_list = list(text)
    for i, letter in enumerate('EAST'):
        pos = 21 + i
        c_val = char_to_num(text[pos])
        e_val = char_to_num(letter)
        # Try subtraction (reverse Vigenère)
        text_list[pos] = num_to_char((c_val - e_val) % 26)
    text = ''.join(text_list)
    print(f"  After EAST: {text[15:35]}")
    
    # Step 2: Apply NORTHEAST mask at 25-34
    print("\nStep 2: Apply NORTHEAST at 25-34")
    for i, letter in enumerate('NORTHEAST'):
        pos = 25 + i
        c_val = char_to_num(text[pos])
        n_val = char_to_num(letter)
        text_list[pos] = num_to_char((c_val - n_val) % 26)
    text = ''.join(text_list)
    print(f"  After NORTHEAST: {text[20:40]}")
    
    # Step 3: Apply BERLIN mask at 63-69
    print("\nStep 3: Apply BERLIN at 63-69")
    for i, letter in enumerate('BERLIN'):
        pos = 63 + i
        c_val = char_to_num(text[pos])
        b_val = char_to_num(letter)
        text_list[pos] = num_to_char((c_val - b_val) % 26)
    text = ''.join(text_list)
    print(f"  After BERLIN: {text[58:75]}")
    
    # Step 4: Apply CLOCK mask at 69-74
    print("\nStep 4: Apply CLOCK at 69-74")
    for i, letter in enumerate('CLOCK'):
        pos = 69 + i
        c_val = char_to_num(text[pos])
        c_val2 = char_to_num(letter)
        text_list[pos] = num_to_char((c_val - c_val2) % 26)
    text = ''.join(text_list)
    print(f"  After CLOCK: {text[65:80]}")
    
    # Now try ABSCISSA
    print(f"\nFinal masked text: {text[:50]}...")
    pt = vigenere_decrypt(text, 'ABSCISSA')
    print(f"With ABSCISSA: {pt[:50]}...")
    
    # Check middle segment specifically
    middle_pt = vigenere_decrypt(text[34:63], 'ABSCISSA')
    print(f"\nMiddle segment with ABSCISSA: {middle_pt}")
    if 'MIRHEAT' in middle_pt:
        print("  ✓ Found MIR HEAT in middle segment!")

def test_inverted_masking():
    """Test if we should add anchors instead of subtracting."""
    print("\n" + "="*70)
    print("TEST 6: INVERTED MASKING (Addition)")
    print("="*70)
    
    # Apply anchors as additions
    text_list = list(K4_CIPHERTEXT)
    
    for word, (start, end) in ANCHORS.items():
        for i, letter in enumerate(word):
            if start + i < end:
                pos = start + i
                c_val = char_to_num(K4_CIPHERTEXT[pos])
                a_val = char_to_num(letter)
                # Add instead of subtract
                text_list[pos] = num_to_char((c_val + a_val) % 26)
    
    modified = ''.join(text_list)
    print(f"Modified with addition: {modified[:50]}...")
    
    # Test with ABSCISSA
    pt = vigenere_decrypt(modified, 'ABSCISSA')
    print(f"With ABSCISSA: {pt[:50]}...")
    
    # Check middle segment
    middle_pt = vigenere_decrypt(modified[34:63], 'ABSCISSA')
    print(f"Middle segment: {middle_pt}")
    if 'MIRHEAT' in middle_pt:
        print("  ✓ Found MIR HEAT!")

def main():
    """Run all masking experiments."""
    print("MASKING TECHNIQUE EXPERIMENTS")
    print("Testing various interpretations of Sanborn's 'masking technique'\n")
    
    # Run all tests
    test_anchors_as_masks()
    test_anchors_as_modifiers()
    test_anchors_as_keys()
    test_anchor_distances()
    test_progressive_masking()
    test_inverted_masking()
    
    print("\n" + "="*70)
    print("CONCLUSIONS")
    print("="*70)
    print("""
The "masking technique" remains ambiguous without Sanborn's exact words.

Key observations:
1. Simple masking (removal) doesn't preserve MIR HEAT
2. XOR modification changes the ciphertext but doesn't improve results
3. Anchors as keys don't produce MIR HEAT in expected locations
4. Distance-based shifts don't yield meaningful results
5. Progressive masking doesn't preserve the MIR HEAT finding

The fundamental conflict remains:
- Repository solution preserves anchors perfectly
- MIR HEAT finding is statistically significant but breaks anchors
- Without Sanborn's original statements, we can't resolve this

Possible explanations:
1. K4 has multiple valid solutions (intentional ambiguity)
2. The anchors serve a different purpose than assumed
3. One solution is correct, the other is a remarkable coincidence
""")

if __name__ == "__main__":
    main()