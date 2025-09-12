#!/usr/bin/env python3
"""
f3_null_cipher.py

Testing if K4 uses a null cipher where only certain positions matter.
The rest might be meaningless filler or decoys.
"""

from typing import List, Tuple, Dict, Optional
import math

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class NullCipherAnalyzer:
    """Test null cipher patterns in K4."""
    
    def __init__(self):
        self.k4_ct = K4_CIPHERTEXT
        self.length = len(self.k4_ct)
        
        # Prime numbers up to 97
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        
        # Fibonacci sequence
        self.fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        
        # Perfect squares
        self.squares = [1, 4, 9, 16, 25, 36, 49, 64, 81]
    
    def test_every_nth(self):
        """Test taking every Nth character."""
        print("\n" + "="*60)
        print("TESTING EVERY NTH CHARACTER")
        print("="*60)
        
        print("\nExtracting every Nth character:")
        
        for n in range(2, 11):
            extracted = self.k4_ct[::n]
            print(f"\nEvery {n}th char: {extracted}")
            
            # Check for words
            if self.has_words(extracted):
                words = self.find_words(extracted)
                print(f"  Words found: {words}")
            
            # Try with ABSCISSA
            if len(extracted) >= 8:
                pt = self.vigenere_decrypt(extracted, 'ABSCISSA')
                if 'MIR' in pt or 'HEAT' in pt:
                    print(f"  With ABSCISSA: {pt[:30]}...")
                    print(f"    Contains MIR/HEAT!")
    
    def test_prime_positions(self):
        """Test characters at prime positions."""
        print("\n" + "="*60)
        print("TESTING PRIME POSITIONS")
        print("="*60)
        
        print("\nExtracting characters at prime number positions:")
        
        # Extract at prime positions (0-indexed)
        prime_chars = []
        for p in self.primes:
            if p - 1 < self.length:  # Convert to 0-index
                prime_chars.append(self.k4_ct[p - 1])
        
        extracted = ''.join(prime_chars)
        print(f"Prime positions: {extracted}")
        
        # Check for patterns
        if self.has_words(extracted):
            words = self.find_words(extracted)
            print(f"  Words found: {words}")
        
        # Try decrypting
        pt = self.vigenere_decrypt(extracted, 'ABSCISSA')
        if self.has_words(pt):
            print(f"  With ABSCISSA: {pt}")
            words = self.find_words(pt)
            if words:
                print(f"    Words: {words}")
    
    def test_fibonacci_positions(self):
        """Test Fibonacci sequence positions."""
        print("\n" + "="*60)
        print("TESTING FIBONACCI POSITIONS")
        print("="*60)
        
        print("\nExtracting at Fibonacci positions:")
        
        fib_chars = []
        for f in self.fibonacci:
            if f - 1 < self.length:  # Convert to 0-index
                fib_chars.append(self.k4_ct[f - 1])
        
        extracted = ''.join(fib_chars)
        print(f"Fibonacci positions: {extracted}")
        
        if self.has_words(extracted):
            words = self.find_words(extracted)
            print(f"  Words found: {words}")
    
    def test_diagonal_patterns(self):
        """Test diagonal reading patterns."""
        print("\n" + "="*60)
        print("TESTING DIAGONAL PATTERNS")
        print("="*60)
        
        print("\nReading diagonally through different grid sizes:")
        
        # Try different grid sizes
        for width in [7, 8, 9, 10, 11, 12]:
            if self.length % width == 0 or width * width >= self.length:
                # Create grid
                grid = []
                padded = self.k4_ct + 'X' * (width * width - self.length)
                
                for i in range(0, len(padded), width):
                    if i + width <= len(padded):
                        grid.append(padded[i:i+width])
                
                if len(grid) > 0:
                    # Main diagonal
                    diagonal = ''
                    for i in range(min(len(grid), width)):
                        if i < len(grid) and i < len(grid[i]):
                            diagonal += grid[i][i]
                    
                    if len(diagonal) >= 5:
                        print(f"\n{width}x{len(grid)} grid diagonal: {diagonal}")
                        
                        if self.has_words(diagonal):
                            words = self.find_words(diagonal)
                            print(f"  Words: {words}")
    
    def test_first_letters(self):
        """Test first letters of words/segments."""
        print("\n" + "="*60)
        print("TESTING FIRST LETTERS")
        print("="*60)
        
        print("\nExtracting first letter of each N-character segment:")
        
        for segment_size in [3, 4, 5, 6, 7, 8]:
            first_letters = []
            for i in range(0, self.length, segment_size):
                if i < self.length:
                    first_letters.append(self.k4_ct[i])
            
            extracted = ''.join(first_letters)
            print(f"\nFirst of every {segment_size}: {extracted}")
            
            if self.has_words(extracted):
                words = self.find_words(extracted)
                print(f"  Words found: {words}")
    
    def test_anchor_positions(self):
        """Test positions related to known anchors."""
        print("\n" + "="*60)
        print("TESTING ANCHOR-BASED POSITIONS")
        print("="*60)
        
        # Positions where anchors supposedly are
        anchor_positions = [
            (21, 25),   # EAST
            (25, 34),   # NORTHEAST
            (63, 69),   # BERLIN
            (69, 74)    # CLOCK
        ]
        
        print("\nExtracting at anchor boundaries:")
        
        # Extract at boundaries
        boundary_chars = []
        for start, end in anchor_positions:
            if start < self.length:
                boundary_chars.append(self.k4_ct[start])
            if end < self.length:
                boundary_chars.append(self.k4_ct[end])
        
        extracted = ''.join(boundary_chars)
        print(f"Anchor boundaries: {extracted}")
        
        # Extract between anchors
        print("\nExtracting between anchor positions:")
        
        between = []
        between.append(self.k4_ct[0:21])     # Before EAST
        between.append(self.k4_ct[34:63])    # Between NORTHEAST and BERLIN
        between.append(self.k4_ct[74:97])    # After CLOCK
        
        for i, segment in enumerate(between):
            print(f"\nSegment {i}: {segment}")
            
            # Try with ABSCISSA
            pt = self.vigenere_decrypt(segment, 'ABSCISSA')
            if 'MIR' in pt or 'HEAT' in pt or self.has_words(pt):
                print(f"  With ABSCISSA: {pt}")
                if 'MIR' in pt:
                    print(f"    Contains MIR!")
                if 'HEAT' in pt:
                    print(f"    Contains HEAT!")
    
    def test_pattern_based_extraction(self):
        """Test extraction based on letter patterns."""
        print("\n" + "="*60)
        print("TESTING PATTERN-BASED EXTRACTION")
        print("="*60)
        
        print("\nExtracting based on letter patterns:")
        
        # Extract vowels only
        vowels = ''.join([c for c in self.k4_ct if c in 'AEIOU'])
        print(f"\nVowels only: {vowels}")
        
        # Extract consonants only
        consonants = ''.join([c for c in self.k4_ct if c not in 'AEIOU'])
        print(f"\nConsonants only: {consonants[:50]}...")
        
        # Extract letters that appear exactly once
        from collections import Counter
        freq = Counter(self.k4_ct)
        unique = ''.join([c for c in self.k4_ct if freq[c] == 1])
        print(f"\nUnique letters: {unique}")
        
        # Extract repeated letters
        repeated = ''.join([c for c in self.k4_ct if freq[c] > 1])
        print(f"\nRepeated letters: {repeated[:50]}...")
        
        # Check for patterns
        for name, text in [('Vowels', vowels), ('Unique', unique)]:
            if len(text) >= 10 and self.has_words(text):
                print(f"\n{name} contains words:")
                words = self.find_words(text)
                print(f"  {words}")
    
    def test_mathematical_sequences(self):
        """Test various mathematical sequences."""
        print("\n" + "="*60)
        print("TESTING MATHEMATICAL SEQUENCES")
        print("="*60)
        
        print("\nExtracting at positions from mathematical sequences:")
        
        # Triangular numbers
        triangular = [n * (n + 1) // 2 for n in range(1, 15)]
        tri_chars = []
        for t in triangular:
            if t - 1 < self.length:
                tri_chars.append(self.k4_ct[t - 1])
        
        extracted = ''.join(tri_chars)
        print(f"\nTriangular numbers: {extracted}")
        
        # Powers of 2
        powers_of_2 = [2**n for n in range(7)]  # Up to 64
        pow2_chars = []
        for p in powers_of_2:
            if p - 1 < self.length:
                pow2_chars.append(self.k4_ct[p - 1])
        
        extracted = ''.join(pow2_chars)
        print(f"\nPowers of 2: {extracted}")
        
        # Check if any produce MIR or HEAT
        for seq_name, seq_chars in [('Triangular', ''.join(tri_chars)), 
                                     ('Powers of 2', ''.join(pow2_chars))]:
            if 'MIR' in seq_chars or 'HEAT' in seq_chars:
                print(f"  {seq_name} contains MIR/HEAT!")
    
    def test_skip_patterns(self):
        """Test various skip patterns."""
        print("\n" + "="*60)
        print("TESTING SKIP PATTERNS")
        print("="*60)
        
        print("\nTesting progressive skip patterns:")
        
        # Progressive skip (1st char, skip 1, take 1, skip 2, take 1, skip 3...)
        extracted = []
        pos = 0
        skip = 0
        while pos < self.length:
            extracted.append(self.k4_ct[pos])
            pos += skip + 1
            skip += 1
        
        result = ''.join(extracted)
        print(f"Progressive skip: {result}")
        
        # Alternating skip pattern
        extracted = []
        pos = 0
        pattern = [1, 2, 3, 2, 1]  # Skip pattern
        pattern_idx = 0
        
        while pos < self.length:
            extracted.append(self.k4_ct[pos])
            pos += pattern[pattern_idx % len(pattern)]
            pattern_idx += 1
        
        result = ''.join(extracted)
        print(f"Alternating skip: {result}")
        
        # Check for words
        if self.has_words(result):
            words = self.find_words(result)
            print(f"  Words: {words}")
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Standard Vigenere decryption."""
        if not key or not text:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        if len(text) < 3:
            return False
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'MIR', 'HEAT']
        return any(word in text for word in words)
    
    def find_words(self, text: str) -> List[str]:
        """Find common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'HEAT', 'MIR', 'WAR', 'PEACE',
                 'BERLIN', 'CLOCK', 'EAST', 'WEST']
        return [word for word in words if word in text]

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("NULL CIPHER ANALYSIS")
    print("Testing if only certain positions in K4 matter")
    print("="*70)
    
    analyzer = NullCipherAnalyzer()
    
    # Run all tests
    analyzer.test_every_nth()
    analyzer.test_prime_positions()
    analyzer.test_fibonacci_positions()
    analyzer.test_diagonal_patterns()
    analyzer.test_first_letters()
    analyzer.test_anchor_positions()
    analyzer.test_pattern_based_extraction()
    analyzer.test_mathematical_sequences()
    analyzer.test_skip_patterns()
    
    # Summary
    print("\n" + "="*70)
    print("NULL CIPHER SUMMARY")
    print("="*70)
    
    print("\nNull cipher hypothesis: Only certain positions contain")
    print("the real message, the rest is filler/decoy.")
    
    print("\nTested extraction patterns:")
    print("- Every Nth character")
    print("- Prime number positions")
    print("- Fibonacci positions")
    print("- Diagonal patterns")
    print("- First letters of segments")
    print("- Mathematical sequences")
    
    print("\nNo clear message emerged from selective extraction,")
    print("suggesting K4 likely uses all characters meaningfully.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()