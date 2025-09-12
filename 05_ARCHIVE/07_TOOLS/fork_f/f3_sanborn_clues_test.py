#!/usr/bin/env python3
"""
f3_sanborn_clues_test.py

Testing different interpretations of Sanborn's clues.
There's confusion about what he actually said.
"""

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

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

def test_sanborn_interpretations():
    """Test different interpretations of Sanborn's clues."""
    
    print("="*70)
    print("TESTING SANBORN CLUE INTERPRETATIONS")
    print("="*70)
    
    # Different position interpretations
    interpretations = [
        {
            'name': 'Repository claim (0-indexed)',
            'EAST': (21, 25),
            'NORTHEAST': (25, 34),
            'BERLIN': (63, 69),
            'CLOCK': (69, 74)
        },
        {
            'name': 'Common interpretation (1-indexed, 64-69 for BERLIN)',
            'EAST': (20, 24),
            'NORTHEAST': (24, 33),
            'BERLIN': (63, 69),  # 64-69 in 1-indexed
            'CLOCK': (69, 74)    # 70-74 in 1-indexed
        },
        {
            'name': 'Alternative (BERLIN at 64-74 inclusive)',
            'EAST': (20, 24),
            'NORTHEAST': (24, 33),
            'BERLINCLOCK': (63, 74)  # Combined
        }
    ]
    
    for interp in interpretations:
        print(f"\n{interp['name']}:")
        print("-" * 50)
        
        # Check what's actually at these positions
        for word, positions in interp.items():
            if word not in ['name']:
                start, end = positions
                actual = K4_CIPHERTEXT[start:end]
                print(f"  {word} at {start}-{end}: {actual}")
        
        # Check if these could be plaintext
        print("\n  Testing as plaintext anchors:")
        works = True
        for word, positions in interp.items():
            if word not in ['name']:
                start, end = positions
                expected_len = end - start
                actual_word = word if word != 'BERLINCLOCK' else 'BERLINCLOCK'
                if len(actual_word) != expected_len:
                    print(f"    ❌ {word}: Length mismatch ({len(actual_word)} vs {expected_len})")
                    works = False
                else:
                    print(f"    ✓ {word}: Length matches")
        
        if works:
            print("    Could be valid anchor positions")
    
    # Test the "masking technique" interpretation
    print("\n" + "="*70)
    print("TESTING MASKING TECHNIQUE")
    print("="*70)
    
    print("\nSanborn mentioned using a 'masking technique'.")
    print("What if this means:")
    
    # 1. Anchors are masks to be removed
    print("\n1. Remove anchor positions from ciphertext:")
    masked = ""
    anchor_positions = set()
    for i in range(21, 25): anchor_positions.add(i)
    for i in range(25, 34): anchor_positions.add(i)
    for i in range(63, 69): anchor_positions.add(i)
    for i in range(69, 74): anchor_positions.add(i)
    
    for i, c in enumerate(K4_CIPHERTEXT):
        if i not in anchor_positions:
            masked += c
    
    print(f"   Original length: {len(K4_CIPHERTEXT)}")
    print(f"   Masked length: {len(masked)}")
    print(f"   Masked text: {masked[:50]}...")
    
    # Test ABSCISSA on masked
    pt = vigenere_decrypt(masked, 'ABSCISSA')
    if 'MIR' in pt or 'HEAT' in pt:
        print(f"   With ABSCISSA: {pt[:50]}...")
        if 'MIR' in pt:
            print(f"     Contains MIR!")
        if 'HEAT' in pt:
            print(f"     Contains HEAT!")
    
    # 2. Anchors are the key
    print("\n2. Use anchors as Vigenere key:")
    keys_to_test = [
        'EASTNORTHEASTBERLINCLOCK',
        'BERLINCLOCK',
        'BERLINCLOCKEASTNORTHEAST',
        'CLOCKBERLINEASTNORTHEAST'
    ]
    
    for key in keys_to_test:
        pt = vigenere_decrypt(K4_CIPHERTEXT, key)
        # Look for common words
        common = ['THE', 'AND', 'ARE', 'WAS', 'MIR', 'HEAT']
        found = [w for w in common if w in pt]
        if found:
            print(f"   Key '{key[:20]}...':")
            print(f"     {pt[:50]}...")
            print(f"     Words found: {found}")
    
    # 3. XOR masking
    print("\n3. XOR the anchors with their positions:")
    print("   (This would require the plaintext at those positions)")
    
    # Test ABSCISSA on middle segment only
    print("\n" + "="*70)
    print("CONFIRMING MIR HEAT FINDING")
    print("="*70)
    
    middle_segment = K4_CIPHERTEXT[34:63]
    print(f"\nMiddle segment (34-63): {middle_segment}")
    
    pt = vigenere_decrypt(middle_segment, 'ABSCISSA')
    print(f"With ABSCISSA: {pt}")
    
    if 'MIR' in pt:
        pos = pt.find('MIR')
        print(f"  MIR found at position {pos} (absolute: {34 + pos})")
    if 'HEAT' in pt:
        pos = pt.find('HEAT')
        print(f"  HEAT found at position {pos} (absolute: {34 + pos})")
    
    # Check repository's claimed solution
    print("\n" + "="*70)
    print("REPOSITORY'S CLAIMED SOLUTION")
    print("="*70)
    
    claimed = "WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
    print(f"\nClaimed plaintext: {claimed}")
    print(f"\nChecking anchors:")
    print(f"  EAST at 21-25: '{claimed[21:25]}' ✓" if claimed[21:25] == 'EAST' else f"  EAST at 21-25: '{claimed[21:25]}' ✗")
    print(f"  NORTHEAST at 25-34: '{claimed[25:34]}' ✓" if claimed[25:34] == 'NORTHEAST' else f"  NORTHEAST at 25-34: '{claimed[25:34]}' ✗")
    print(f"  BERLIN at 63-69: '{claimed[63:69]}' ✓" if claimed[63:69] == 'BERLIN' else f"  BERLIN at 63-69: '{claimed[63:69]}' ✗")
    print(f"  CLOCK at 69-74: '{claimed[69:74]}' ✓" if claimed[69:74] == 'CLOCK' else f"  CLOCK at 69-74: '{claimed[69:74]}' ✗")
    
    print("\nTheir solution DOES preserve the anchors.")
    print("But it uses a complex 6-track system, not simple Vigenere.")
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    
    print("""
Two possibilities:

1. REPOSITORY IS CORRECT:
   - Full solution that preserves Sanborn's anchors
   - Uses complex 6-track cipher system
   - Message about geometry/surveying

2. MIR HEAT IS A CLUE:
   - ABSCISSA produces statistically significant "MIR HEAT"
   - Doesn't preserve anchors (maybe they're not meant to be?)
   - 93% remains unsolved

The key question: What EXACTLY did Sanborn say about:
- The positions (0-indexed vs 1-indexed?)
- "BERLIN" vs "BERLINCLOCK" 
- The "masking technique"

Without access to original source material (interviews, etc.),
we can't definitively resolve this conflict.
""")

if __name__ == "__main__":
    test_sanborn_interpretations()