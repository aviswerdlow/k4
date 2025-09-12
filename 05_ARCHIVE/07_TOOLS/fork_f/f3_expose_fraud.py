#!/usr/bin/env python3
"""
f3_expose_fraud.py

Demonstrates why the repository's "solution" is fraudulent by showing
how trivial it is to create a lookup table for ANY desired plaintext.
"""

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

def create_fraudulent_solution(desired_plaintext: str):
    """
    Demonstrates the repository's method: create a lookup table 
    that produces any desired plaintext. This is NOT cryptanalysis!
    """
    print("="*70)
    print(f"CREATING FRAUDULENT 'SOLUTION' FOR ARBITRARY TEXT")
    print("="*70)
    
    # Ensure plaintext is same length as ciphertext
    if len(desired_plaintext) != 97:
        print(f"Padding/truncating plaintext to 97 chars")
        if len(desired_plaintext) < 97:
            desired_plaintext = desired_plaintext + 'X' * (97 - len(desired_plaintext))
        else:
            desired_plaintext = desired_plaintext[:97]
    
    print(f"\nDesired plaintext: {desired_plaintext[:50]}...")
    
    # Create lookup table using repository's 6-track system
    # Formula: class(i) = ((i % 2) * 3) + (i % 3)
    def compute_class(i: int) -> int:
        return ((i % 2) * 3) + (i % 3)
    
    # Initialize 6 "wheels" with period 17 (matching repository)
    wheels = {
        0: {'family': 'vigenere', 'residues': [None] * 17},
        1: {'family': 'vigenere', 'residues': [None] * 17},
        2: {'family': 'beaufort', 'residues': [None] * 17},
        3: {'family': 'vigenere', 'residues': [None] * 17},
        4: {'family': 'beaufort', 'residues': [None] * 17},
        5: {'family': 'vigenere', 'residues': [None] * 17}
    }
    
    # Calculate required "residues" (shifts) for each position
    print("\nCalculating lookup table (fraudulent 'wheels')...")
    
    for i in range(97):
        c_val = char_to_num(K4_CIPHERTEXT[i])
        p_val = char_to_num(desired_plaintext[i])
        
        class_id = compute_class(i)
        slot = i % 17  # Using period 17 like repository
        
        # Calculate required shift based on "family"
        family = wheels[class_id]['family']
        if family == 'vigenere':
            # P = C - K, so K = C - P
            k_val = (c_val - p_val) % 26
        elif family == 'beaufort':
            # P = K - C, so K = P + C
            k_val = (p_val + c_val) % 26
        else:
            k_val = 0
        
        # Store in wheel (this is the fraud - we're encoding the answer!)
        if wheels[class_id]['residues'][slot] is None:
            wheels[class_id]['residues'][slot] = k_val
        elif wheels[class_id]['residues'][slot] != k_val:
            print(f"  Collision at class {class_id}, slot {slot}!")
    
    # Display the fraudulent lookup table
    print("\nFraudulent lookup table (17x6):")
    for class_id in range(6):
        residue_chars = []
        for r in wheels[class_id]['residues']:
            if r is not None:
                residue_chars.append(num_to_char(r))
            else:
                residue_chars.append('?')
        print(f"  Class {class_id} ({wheels[class_id]['family']:8}): {','.join(residue_chars)}")
    
    # Now "decrypt" using our fraudulent table (circular logic!)
    print("\n'Decrypting' with fraudulent table (circular logic):")
    decrypted = []
    
    for i in range(97):
        c_val = char_to_num(K4_CIPHERTEXT[i])
        class_id = compute_class(i)
        slot = i % 17
        
        k_val = wheels[class_id]['residues'][slot]
        if k_val is None:
            decrypted.append('?')
            continue
        
        family = wheels[class_id]['family']
        if family == 'vigenere':
            p_val = (c_val - k_val) % 26
        elif family == 'beaufort':
            p_val = (k_val - c_val) % 26
        else:
            p_val = c_val
        
        decrypted.append(num_to_char(p_val))
    
    result = ''.join(decrypted)
    print(f"  Result: {result[:50]}...")
    
    if result == desired_plaintext:
        print("\n✓ SUCCESS! We 'solved' K4 with our arbitrary text!")
        print("  (But this is FRAUD, not cryptanalysis)")
    
    return wheels

def expose_the_scam():
    """Show how ANY text can be made to 'solve' K4 using this method."""
    
    print("\nDEMONSTRATING THE FRAUD")
    print("="*70)
    print("\nThe repository's method can make K4 say ANYTHING:")
    print("This is not solving K4 - it's encoding a desired answer!\n")
    
    # Example 1: Repository's claimed text
    print("\n1. Repository's claimed solution:")
    repo_text = "WEAREINTHEGRIDSEETHENEASTNORTHEASTANDWEAREBYTHELINETOSEEBETWEENBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
    create_fraudulent_solution(repo_text)
    
    # Example 2: Completely different text
    print("\n2. Making K4 say something completely different:")
    alt_text = "THISISAFRAUDULENTSOLUTIONNOTREALANYCRYPTANALYSISJUSTLOOKUPTABLESANYONECANMAKEKTOSAYWHATEVERTHEYWANT"
    create_fraudulent_solution(alt_text)
    
    # Example 3: Nonsense
    print("\n3. Making K4 say nonsense:")
    nonsense = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQ"
    create_fraudulent_solution(nonsense)
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("""
As demonstrated, the repository's method can make K4 "decrypt" to ANY text.
This is because it's not actually decrypting anything - it's just creating
a lookup table that produces whatever output you want.

REAL CRYPTANALYSIS: Find the key/method that Sanborn used
FRAUD: Create a table that produces your desired text

The repository's complex terminology ("wheels", "residues", "families") is
just obfuscation. At its core, it's a simple lookup table that encodes the
answer, not a method that discovers it.

The forum community correctly identified this as fraud.
K4 remains unsolved.
""")

if __name__ == "__main__":
    expose_the_scam()