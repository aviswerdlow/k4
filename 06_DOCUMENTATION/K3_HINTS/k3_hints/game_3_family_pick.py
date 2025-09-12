#!/usr/bin/env python3
"""
Game 3: Family selection by Option-A rule.
Pick first family that satisfies Option-A at anchor cells.
Pure Python stdlib only. No AI.
"""

def test_family_option_a(ciphertext, plaintext, indices, family):
    """
    Test if a family satisfies Option-A (no K=0) at given indices.
    """
    for idx in indices:
        c_val = ord(ciphertext[idx]) - ord('A')
        p_val = ord(plaintext[idx]) - ord('A')
        
        if family == "vigenere":
            k = (c_val - p_val) % 26
            if k == 0:  # Option-A violation
                return False
        elif family == "variant_beaufort":
            k = (p_val - c_val) % 26
            if k == 0:  # Option-A violation
                return False
        elif family == "beaufort":
            # Beaufort: K = P + C (mod 26)
            # No Option-A restriction for Beaufort
            pass
    
    return True


def main():
    print("K4 Family Selection (Option-A Rule)")
    print("=" * 50)
    print("Rule: For each class, pick first family that satisfies Option-A")
    print("Test order: [Vigenère, Variant-Beaufort, Beaufort]")
    print()
    
    # K4 ciphertext (97 letters)
    k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # K4 known plaintext at cribs
    cribs = {
        21: "EAST",      # 21-24
        25: "NORTHEAST", # 25-33
        63: "BERLIN",    # 63-68
        69: "CLOCK"      # 69-73
    }
    
    # Build full plaintext with cribs (rest as '?')
    k4_pt = ['?'] * 97
    for start_idx, text in cribs.items():
        for i, char in enumerate(text):
            k4_pt[start_idx + i] = char
    k4_pt = ''.join(k4_pt)
    
    # Classify crib indices
    classes = {c: [] for c in range(6)}
    for start_idx, text in cribs.items():
        for i in range(len(text)):
            idx = start_idx + i
            cls = ((idx % 2) * 3) + (idx % 3)
            if k4_pt[idx] != '?':
                classes[cls].append(idx)
    
    print("Testing families for each class:")
    print("-" * 50)
    
    families = ["vigenere", "variant_beaufort", "beaufort"]
    selected_families = []
    
    for c in range(6):
        print(f"\nClass {c} (indices: {classes[c][:5]}{'...' if len(classes[c]) > 5 else ''}):")
        
        if not classes[c]:
            print("  No crib indices in this class")
            selected_families.append("unknown")
            continue
        
        family_found = False
        for family in families:
            satisfies = test_family_option_a(k4_ct, k4_pt, classes[c], family)
            
            if satisfies:
                print(f"  {family:20} ✓ Satisfies Option-A")
                if not family_found:
                    selected_families.append(family)
                    family_found = True
                    print(f"  → Selected: {family}")
                    break
            else:
                print(f"  {family:20} ✗ Violates Option-A (K=0 at anchor)")
        
        if not family_found:
            print("  ERROR: No family satisfies Option-A")
            selected_families.append("none")
    
    print("\n" + "=" * 50)
    print("Family Vector (6 symbols):")
    print("-" * 50)
    
    # Convert to compact notation
    family_symbols = {
        "vigenere": "V",
        "variant_beaufort": "R",  # R for vaRiant
        "beaufort": "B",
        "unknown": "?",
        "none": "X"
    }
    
    vector = []
    for i, fam in enumerate(selected_families):
        symbol = family_symbols.get(fam, "?")
        vector.append(symbol)
        print(f"Class {i}: {symbol} ({fam})")
    
    print(f"\nCompact vector: {''.join(vector)}")
    print("\nThis is determined mechanically by Option-A rule.")
    print("No K4 prose or tail knowledge used.")


if __name__ == "__main__":
    main()