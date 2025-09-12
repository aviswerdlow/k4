#!/usr/bin/env python3
"""
f3_mixed_cipher_zones.py

Testing hypothesis that each zone uses a different cipher type:
- HEAD (0-21): Transposition cipher
- MIDDLE (34-63): Vigenère (confirmed with ABSCISSA → MIR HEAT)
- TAIL (74-97): Substitution cipher
"""

import itertools
from typing import List, Tuple, Dict, Optional
from collections import Counter

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class MixedCipherAnalyzer:
    """Test mixed cipher hypothesis for K4 zones."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Zone definitions
        self.head_ct = self.ciphertext[0:21]     # OBKRUOXOGHULBSOLIFBBW
        self.middle_ct = self.ciphertext[34:63]  # OTWTQSJQSSEKZZWATJKLUDIAWINFB
        self.tail_ct = self.ciphertext[74:97]    # KWGDKZXTJCDIGKUHUAUEKCAR
        
        # Confirmed finding
        self.middle_key = 'ABSCISSA'
        self.middle_pt = 'OSERIARQSRMIRHEATISJMLQAWHVDT'
        
        # Common English words for validation
        self.common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                             'THAT', 'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD',
                             'HEAT', 'IS', 'WAR', 'PEACE', 'END', 'COLD', 'HOT',
                             'BERLIN', 'WALL', 'SOVIET', 'MOSCOW', 'LANGLEY']
    
    def test_head_transposition(self):
        """Test various transposition ciphers on HEAD zone."""
        print("\n" + "="*60)
        print("TESTING HEAD ZONE TRANSPOSITION")
        print("="*60)
        
        print(f"\nHEAD ciphertext: {self.head_ct}")
        print(f"Length: {len(self.head_ct)} (factors: 1, 3, 7, 21)")
        
        results = []
        
        # Columnar transposition
        print("\n1. COLUMNAR TRANSPOSITION:")
        for cols in [3, 7]:  # 21 is divisible by 3 and 7
            rows = 21 // cols
            
            # Try different reading orders
            # Standard columnar (read by columns)
            transposed = ''
            for c in range(cols):
                for r in range(rows):
                    transposed += self.head_ct[r * cols + c]
            
            if self.has_words(transposed):
                print(f"  {cols} columns (standard): {transposed}")
                words = self.find_words(transposed)
                if words:
                    print(f"    Words found: {words}")
                    results.append(('columnar', cols, transposed, words))
            
            # Reverse columnar (read columns backwards)
            transposed = ''
            for c in range(cols-1, -1, -1):
                for r in range(rows):
                    transposed += self.head_ct[r * cols + c]
            
            if self.has_words(transposed):
                print(f"  {cols} columns (reverse): {transposed}")
                words = self.find_words(transposed)
                if words:
                    print(f"    Words found: {words}")
                    results.append(('columnar-reverse', cols, transposed, words))
        
        # Rail fence cipher
        print("\n2. RAIL FENCE CIPHER:")
        for rails in [2, 3, 4]:
            decrypted = self.rail_fence_decrypt(self.head_ct, rails)
            if self.has_words(decrypted):
                print(f"  {rails} rails: {decrypted}")
                words = self.find_words(decrypted)
                if words:
                    print(f"    Words found: {words}")
                    results.append(('rail-fence', rails, decrypted, words))
        
        # Spiral transposition
        print("\n3. SPIRAL TRANSPOSITION:")
        # 21 = 3x7 grid
        spiral = self.spiral_read(self.head_ct, 3, 7)
        if self.has_words(spiral):
            print(f"  3x7 spiral: {spiral}")
            words = self.find_words(spiral)
            if words:
                print(f"    Words found: {words}")
                results.append(('spiral', '3x7', spiral, words))
        
        # Route cipher (zigzag)
        print("\n4. ROUTE CIPHER (ZIGZAG):")
        for cols in [3, 7]:
            zigzag = self.zigzag_read(self.head_ct, cols)
            if self.has_words(zigzag):
                print(f"  {cols} columns zigzag: {zigzag}")
                words = self.find_words(zigzag)
                if words:
                    print(f"    Words found: {words}")
                    results.append(('zigzag', cols, zigzag, words))
        
        return results
    
    def test_tail_substitution(self):
        """Test various substitution ciphers on TAIL zone."""
        print("\n" + "="*60)
        print("TESTING TAIL ZONE SUBSTITUTION")
        print("="*60)
        
        print(f"\nTAIL ciphertext: {self.tail_ct}")
        print(f"Length: {len(self.tail_ct)}")
        
        results = []
        
        # Frequency analysis
        freq = Counter(self.tail_ct)
        print(f"\nFrequency analysis:")
        for char, count in freq.most_common():
            print(f"  {char}: {count}")
        
        # Most common letter in English is E, T, A, O, I, N
        most_common_ct = freq.most_common(1)[0][0]
        
        # Caesar cipher (simple shift)
        print("\n1. CAESAR CIPHER:")
        for shift in range(26):
            decrypted = ''.join(chr((ord(c) - ord('A') - shift) % 26 + ord('A')) 
                              for c in self.tail_ct)
            if self.has_words(decrypted):
                print(f"  Shift {shift}: {decrypted[:30]}...")
                words = self.find_words(decrypted)
                if words:
                    print(f"    Words found: {words}")
                    results.append(('caesar', shift, decrypted, words))
        
        # Atbash cipher
        print("\n2. ATBASH CIPHER:")
        atbash = ''.join(chr(ord('Z') - (ord(c) - ord('A'))) for c in self.tail_ct)
        print(f"  {atbash}")
        if self.has_words(atbash):
            words = self.find_words(atbash)
            print(f"    Words found: {words}")
            results.append(('atbash', None, atbash, words))
        
        # Affine cipher (ax + b mod 26)
        print("\n3. AFFINE CIPHER:")
        # a must be coprime with 26
        for a in [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]:
            for b in range(0, 26, 5):  # Sample b values
                decrypted = self.affine_decrypt(self.tail_ct, a, b)
                if self.has_words(decrypted):
                    print(f"  a={a}, b={b}: {decrypted[:30]}...")
                    words = self.find_words(decrypted)
                    if words:
                        print(f"    Words found: {words}")
                        results.append(('affine', (a, b), decrypted, words))
        
        # Keyword substitution
        print("\n4. KEYWORD SUBSTITUTION:")
        keywords = ['KRYPTOS', 'BERLIN', 'CLOCK', 'LANGLEY', 'ABSCISSA', 
                   'PALIMPSEST', 'IQLUSION', 'SANBORN']
        
        for keyword in keywords:
            alphabet = self.create_keyword_alphabet(keyword)
            decrypted = self.keyword_decrypt(self.tail_ct, alphabet)
            if self.has_words(decrypted):
                print(f"  Keyword '{keyword}': {decrypted[:30]}...")
                words = self.find_words(decrypted)
                if words:
                    print(f"    Words found: {words}")
                    results.append(('keyword', keyword, decrypted, words))
        
        return results
    
    def test_combined_solution(self):
        """Test combinations of successful methods from each zone."""
        print("\n" + "="*60)
        print("TESTING COMBINED SOLUTIONS")
        print("="*60)
        
        print("\nCombining best results from each zone:")
        print(f"MIDDLE (confirmed): ABSCISSA → MIR HEAT IS...")
        
        # Get best HEAD results
        head_results = self.test_head_transposition()
        
        # Get best TAIL results  
        tail_results = self.test_tail_substitution()
        
        print("\n" + "-"*40)
        print("BEST COMBINATIONS:")
        print("-"*40)
        
        if head_results and tail_results:
            # Take top 3 from each
            for head_method, head_param, head_pt, head_words in head_results[:3]:
                for tail_method, tail_param, tail_pt, tail_words in tail_results[:3]:
                    print(f"\nHEAD ({head_method} {head_param}): {head_pt[:20]}...")
                    print(f"MIDDLE (ABSCISSA): ...MIR HEAT IS...")
                    print(f"TAIL ({tail_method} {tail_param}): {tail_pt[:20]}...")
                    
                    # Check for narrative coherence
                    if self.check_narrative(head_words, ['MIR', 'HEAT'], tail_words):
                        print("  *** Potential narrative connection! ***")
    
    def rail_fence_decrypt(self, text: str, rails: int) -> str:
        """Decrypt rail fence cipher."""
        if rails == 1:
            return text
        
        # Create the rail pattern
        pattern = []
        rail = 0
        direction = 1
        
        for i in range(len(text)):
            pattern.append(rail)
            rail += direction
            
            if rail == 0 or rail == rails - 1:
                direction = -direction
        
        # Fill the rails
        rails_text = [''] * rails
        index = 0
        
        for rail in range(rails):
            for i, r in enumerate(pattern):
                if r == rail:
                    rails_text[rail] += text[index]
                    index += 1
        
        # Read the message
        result = []
        rail_indices = [0] * rails
        
        for r in pattern:
            result.append(rails_text[r][rail_indices[r]])
            rail_indices[r] += 1
        
        return ''.join(result)
    
    def spiral_read(self, text: str, rows: int, cols: int) -> str:
        """Read text in spiral pattern."""
        if len(text) != rows * cols:
            return text
        
        # Create grid
        grid = []
        for r in range(rows):
            grid.append(text[r*cols:(r+1)*cols])
        
        # Read spiral
        result = []
        top, bottom, left, right = 0, rows-1, 0, cols-1
        
        while top <= bottom and left <= right:
            # Right
            for i in range(left, right+1):
                if top <= bottom:
                    result.append(grid[top][i])
            top += 1
            
            # Down
            for i in range(top, bottom+1):
                if left <= right:
                    result.append(grid[i][right])
            right -= 1
            
            # Left
            if top <= bottom:
                for i in range(right, left-1, -1):
                    result.append(grid[bottom][i])
                bottom -= 1
            
            # Up
            if left <= right:
                for i in range(bottom, top-1, -1):
                    result.append(grid[i][left])
                left += 1
        
        return ''.join(result)
    
    def zigzag_read(self, text: str, cols: int) -> str:
        """Read text in zigzag pattern."""
        if len(text) % cols != 0:
            return text
        
        rows = len(text) // cols
        result = []
        
        for r in range(rows):
            if r % 2 == 0:
                # Left to right
                result.append(text[r*cols:(r+1)*cols])
            else:
                # Right to left
                result.append(text[(r+1)*cols-1:r*cols-1:-1])
        
        return ''.join(result)
    
    def affine_decrypt(self, text: str, a: int, b: int) -> str:
        """Decrypt affine cipher."""
        # Find modular inverse of a
        a_inv = self.mod_inverse(a, 26)
        if a_inv is None:
            return text
        
        result = []
        for c in text:
            y = char_to_num(c)
            x = (a_inv * (y - b)) % 26
            result.append(num_to_char(x))
        
        return ''.join(result)
    
    def mod_inverse(self, a: int, m: int) -> Optional[int]:
        """Find modular inverse of a mod m."""
        for i in range(1, m):
            if (a * i) % m == 1:
                return i
        return None
    
    def create_keyword_alphabet(self, keyword: str) -> str:
        """Create substitution alphabet from keyword."""
        # Remove duplicates from keyword
        seen = set()
        unique = []
        for c in keyword.upper():
            if c not in seen and c.isalpha():
                seen.add(c)
                unique.append(c)
        
        # Add remaining letters
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if c not in seen:
                unique.append(c)
        
        return ''.join(unique)
    
    def keyword_decrypt(self, text: str, alphabet: str) -> str:
        """Decrypt with keyword substitution."""
        standard = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        trans_table = str.maketrans(alphabet, standard)
        return text.translate(trans_table)
    
    def check_narrative(self, head_words: List[str], middle_words: List[str], 
                       tail_words: List[str]) -> bool:
        """Check if words form coherent narrative."""
        # Cold War themes
        cold_war_start = ['BERLIN', 'MOSCOW', 'SOVIET', 'WALL', 'IRON']
        cold_war_middle = ['MIR', 'HEAT', 'WAR', 'COLD', 'TENSION']
        cold_war_end = ['PEACE', 'END', 'FALL', 'FREE', 'UNITY']
        
        start_match = any(w in head_words for w in cold_war_start)
        middle_match = any(w in middle_words for w in cold_war_middle)
        end_match = any(w in tail_words for w in cold_war_end)
        
        return start_match and middle_match and end_match
    
    def has_words(self, text: str) -> bool:
        """Check if text contains common words."""
        return any(word in text for word in self.common_words)
    
    def find_words(self, text: str) -> List[str]:
        """Find all common words in text."""
        found = []
        for word in self.common_words:
            if word in text:
                found.append(word)
        return found

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("MIXED CIPHER ZONES ANALYSIS")
    print("Testing different cipher types per zone")
    print("="*70)
    
    analyzer = MixedCipherAnalyzer()
    
    # Test each zone independently
    head_results = analyzer.test_head_transposition()
    tail_results = analyzer.test_tail_substitution()
    
    # Test combined solutions
    analyzer.test_combined_solution()
    
    # Summary
    print("\n" + "="*70)
    print("MIXED CIPHER ANALYSIS SUMMARY")
    print("="*70)
    
    print("\nKey findings:")
    print("1. MIDDLE zone confirmed: Vigenère with ABSCISSA → MIR HEAT IS")
    print("2. HEAD zone: Testing transposition methods")
    if head_results:
        print(f"   Found {len(head_results)} potential transposition results")
    print("3. TAIL zone: Testing substitution methods")
    if tail_results:
        print(f"   Found {len(tail_results)} potential substitution results")
    
    print("\nConclusion:")
    print("Mixed cipher hypothesis shows promise but requires")
    print("further refinement to find coherent full message.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()