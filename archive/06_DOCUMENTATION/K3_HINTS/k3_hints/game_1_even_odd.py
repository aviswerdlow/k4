#!/usr/bin/env python3
"""
Game 1: Even/Odd index analysis of K3.
Shows how a 2/3 interleave naturally yields six tracks.
Pure Python stdlib only. No AI.
"""

def analyze_even_odd(plaintext):
    """Analyze even/odd patterns in K3 plaintext."""
    
    print("K3 Even/Odd Index Analysis")
    print("=" * 50)
    print(f"K3 length: {len(plaintext)} characters")
    print()
    
    # Count characters at even vs odd indices
    even_chars = []
    odd_chars = []
    
    for i, char in enumerate(plaintext):
        if i % 2 == 0:
            even_chars.append((i, char))
        else:
            odd_chars.append((i, char))
    
    print(f"Even indices (0,2,4...): {len(even_chars)} characters")
    print(f"Odd indices (1,3,5...):  {len(odd_chars)} characters")
    print()
    
    # Show the 2/3 split idea
    print("2/3 Interleave Pattern:")
    print("-" * 50)
    print("If we apply ((i % 2) * 3) + (i % 3) to indices:")
    print()
    
    # Demonstrate the pattern for first 24 indices
    classes = {}
    for i in range(24):
        cls = ((i % 2) * 3) + (i % 3)
        if cls not in classes:
            classes[cls] = []
        classes[cls].append(i)
    
    print("First 24 indices distributed into classes:")
    for c in sorted(classes.keys()):
        print(f"Class {c}: {classes[c]}")
    
    print()
    print("This creates 6 interleaved tracks from the 2/3 pattern.")
    print("Each track gets ~16-17 indices out of 97 total.")
    
    # Show distribution for all 97 indices
    full_classes = {c: [] for c in range(6)}
    for i in range(97):
        cls = ((i % 2) * 3) + (i % 3)
        full_classes[cls].append(i)
    
    print("\nFull distribution (0-96):")
    for c in range(6):
        print(f"Class {c}: {len(full_classes[c])} indices")
    
    return full_classes


def main():
    # Read K3 plaintext
    with open("K3_plaintext.txt", "r") as f:
        k3_text = f.read().strip().upper()
    
    classes = analyze_even_odd(k3_text)
    
    print("\n" + "=" * 50)
    print("Result: The formula class(i) = ((i % 2) * 3) + (i % 3)")
    print("creates 6 tracks, which matches K4's expected structure.")
    print("\nNote: This is a plausible pattern, not proof.")
    print("A hand cryptanalyst could test this simple split.")


if __name__ == "__main__":
    main()