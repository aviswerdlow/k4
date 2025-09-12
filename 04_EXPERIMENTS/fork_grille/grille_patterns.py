#!/usr/bin/env python3
"""
grille_patterns.py

Fork GRILLE - Testing physical mask/grille patterns for K4.
Exploring non-contiguous letter extraction patterns.
"""

from typing import List, Tuple, Dict, Optional
import math

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class GrilleCipher:
    """Cipher using physical grille/mask patterns."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.length = len(K4_CIPHERTEXT)
        
        # Common grille patterns
        self.patterns = self.generate_patterns()
    
    def generate_patterns(self) -> Dict[str, List[int]]:
        """Generate various grille extraction patterns."""
        patterns = {}
        
        # Every nth letter patterns
        for n in range(2, 11):
            patterns[f'every_{n}'] = list(range(0, self.length, n))
        
        # Fibonacci sequence positions
        fib = [1, 1]
        while fib[-1] < self.length:
            fib.append(fib[-1] + fib[-2])
        patterns['fibonacci'] = [f - 1 for f in fib if f <= self.length]
        
        # Prime number positions
        patterns['primes'] = self.get_prime_positions()
        
        # Spiral patterns (imagine text in grid)
        patterns['spiral_7x14'] = self.spiral_pattern(7, 14)
        patterns['spiral_14x7'] = self.spiral_pattern(14, 7)
        
        # Diagonal patterns
        patterns['diagonal_7'] = self.diagonal_pattern(7)
        patterns['diagonal_14'] = self.diagonal_pattern(14)
        
        # Chess knight moves
        patterns['knight'] = self.knight_pattern()
        
        # Morse-like patterns (dots and dashes)
        patterns['morse_sos'] = self.morse_pattern('... --- ...')
        
        # Physical sculpture patterns
        patterns['copper_sheet_1'] = list(range(0, 48))  # First half
        patterns['copper_sheet_2'] = list(range(49, 97))  # Second half
        
        # Anchor-based selections
        patterns['between_anchors'] = list(range(34, 63))  # Between NORTHEAST and BERLIN
        patterns['avoid_anchors'] = [i for i in range(self.length) 
                                    if i not in range(21, 34) and i not in range(63, 74)]
        
        # Mathematical sequences
        patterns['squares'] = [i*i for i in range(10) if i*i < self.length]
        patterns['triangular'] = [i*(i+1)//2 for i in range(15) if i*(i+1)//2 < self.length]
        
        # Viewing angle patterns (every row if arranged in grid)
        for width in [7, 10, 14, 21]:
            patterns[f'row_skip_{width}'] = self.row_skip_pattern(width)
        
        return patterns
    
    def get_prime_positions(self) -> List[int]:
        """Get prime number positions."""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True
        
        return [i for i in range(self.length) if is_prime(i + 1)]
    
    def spiral_pattern(self, rows: int, cols: int) -> List[int]:
        """Generate spiral reading pattern."""
        if rows * cols != self.length:
            return []
        
        positions = []
        grid = [[0] * cols for _ in range(rows)]
        
        # Fill grid with positions
        for i in range(rows):
            for j in range(cols):
                grid[i][j] = i * cols + j
        
        # Read in spiral
        top, bottom, left, right = 0, rows - 1, 0, cols - 1
        
        while top <= bottom and left <= right:
            # Right
            for j in range(left, right + 1):
                positions.append(grid[top][j])
            top += 1
            
            # Down
            for i in range(top, bottom + 1):
                positions.append(grid[i][right])
            right -= 1
            
            # Left
            if top <= bottom:
                for j in range(right, left - 1, -1):
                    positions.append(grid[bottom][j])
                bottom -= 1
            
            # Up
            if left <= right:
                for i in range(bottom, top - 1, -1):
                    positions.append(grid[i][left])
                left += 1
        
        return positions[:self.length]
    
    def diagonal_pattern(self, width: int) -> List[int]:
        """Generate diagonal reading pattern."""
        positions = []
        height = (self.length + width - 1) // width
        
        # Main diagonals
        for d in range(width + height - 1):
            for row in range(max(0, d - width + 1), min(height, d + 1)):
                col = d - row
                pos = row * width + col
                if pos < self.length:
                    positions.append(pos)
        
        return positions
    
    def knight_pattern(self) -> List[int]:
        """Chess knight move pattern."""
        positions = [0]  # Start at position 0
        visited = {0}
        current = 0
        
        # Knight moves in 1D (treating as wrapped grid)
        moves = [6, 10, 15, 17, -6, -10, -15, -17]  # Approximating on linear text
        
        while len(positions) < min(50, self.length):
            found = False
            for move in moves:
                next_pos = (current + move) % self.length
                if next_pos not in visited and 0 <= next_pos < self.length:
                    positions.append(next_pos)
                    visited.add(next_pos)
                    current = next_pos
                    found = True
                    break
            
            if not found:
                # Jump to next unvisited
                for i in range(self.length):
                    if i not in visited:
                        positions.append(i)
                        visited.add(i)
                        current = i
                        break
                else:
                    break
        
        return positions
    
    def morse_pattern(self, morse: str) -> List[int]:
        """Extract based on Morse code pattern."""
        positions = []
        idx = 0
        
        for char in morse:
            if char == '.':
                if idx < self.length:
                    positions.append(idx)
                idx += 1
            elif char == '-':
                if idx < self.length:
                    positions.append(idx)
                idx += 3
            else:  # Space
                idx += 2
        
        return positions
    
    def row_skip_pattern(self, width: int) -> List[int]:
        """Select every other row when arranged in grid."""
        positions = []
        for row in range(0, self.length // width, 2):
            for col in range(width):
                pos = row * width + col
                if pos < self.length:
                    positions.append(pos)
        return positions
    
    def apply_grille(self, pattern: List[int]) -> str:
        """Apply grille pattern to extract letters."""
        return ''.join(self.ciphertext[i] for i in pattern if i < self.length)
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Standard Vigenère decryption."""
        if not key:
            return text
            
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def score_plaintext(self, text: str) -> Dict:
        """Score plaintext quality."""
        if len(text) < 4:
            return {'score': 0, 'words': [], 'text': text}
        
        # Common words
        words_found = []
        common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'THAT',
                       'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD', 'THERE', 'THEIR',
                       'HEAT', 'COLD', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TIME',
                       'SECRET', 'CODE', 'CIPHER', 'MESSAGE', 'HIDDEN', 'TRUTH']
        
        for word in common_words:
            if len(word) <= len(text) and word in text:
                words_found.append(word)
        
        # Vowel ratio
        vowels = sum(1 for c in text if c in 'AEIOU')
        vowel_ratio = vowels / len(text) if len(text) > 0 else 0
        
        # Score
        score = len(words_found) * 10
        if 0.3 <= vowel_ratio <= 0.5:
            score += 5
        
        # Bonus for multiple words
        if len(words_found) >= 3:
            score += 10
        
        return {
            'score': score,
            'words': words_found,
            'vowel_ratio': round(vowel_ratio, 3),
            'text': text
        }
    
    def test_grille_patterns(self):
        """Test all grille patterns."""
        print("\n" + "="*60)
        print("TESTING GRILLE EXTRACTION PATTERNS")
        print("="*60)
        
        best_results = []
        
        for pattern_name, positions in self.patterns.items():
            if not positions:
                continue
            
            extracted = self.apply_grille(positions)
            
            # Test raw extraction
            score_data = self.score_plaintext(extracted)
            
            if score_data['score'] > 0:
                best_results.append({
                    'pattern': pattern_name,
                    'method': 'raw',
                    'score': score_data['score'],
                    'words': score_data['words'],
                    'length': len(extracted),
                    'text': extracted[:40] if len(extracted) > 40 else extracted
                })
            
            # Test with common keys
            test_keys = ['KRYPTOS', 'ABSCISSA', 'PALIMPSEST', 'BERLIN', 'YARD']
            
            for key in test_keys:
                decrypted = self.vigenere_decrypt(extracted, key)
                score_data = self.score_plaintext(decrypted)
                
                if score_data['score'] > 10:
                    best_results.append({
                        'pattern': pattern_name,
                        'method': f'vigenere+{key}',
                        'score': score_data['score'],
                        'words': score_data['words'],
                        'length': len(decrypted),
                        'text': decrypted[:40] if len(decrypted) > 40 else decrypted
                    })
        
        # Sort by score
        best_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\nTop 10 grille results:")
        for i, res in enumerate(best_results[:10]):
            print(f"\n{i+1}. Pattern: {res['pattern']} ({res['method']})")
            print(f"   Score: {res['score']}, Length: {res['length']}")
            print(f"   Words: {res['words']}")
            print(f"   Text: {res['text']}...")
        
        return best_results
    
    def test_physical_sculpture_patterns(self):
        """Test patterns based on physical sculpture properties."""
        print("\n" + "="*60)
        print("TESTING PHYSICAL SCULPTURE PATTERNS")
        print("="*60)
        
        # Kryptos has specific physical properties
        patterns = {
            # Two copper sheets
            'left_sheet': list(range(0, 49)),
            'right_sheet': list(range(49, 97)),
            
            # Four sections on sculpture
            'section_1': list(range(0, 24)),
            'section_2': list(range(24, 48)),
            'section_3': list(range(48, 72)),
            'section_4': list(range(72, 97)),
            
            # Visible from different angles
            'front_view': [i for i in range(self.length) if i % 3 == 0],
            'side_view': [i for i in range(self.length) if i % 3 == 1],
            'angle_view': [i for i in range(self.length) if i % 3 == 2],
            
            # Based on sculpture curves
            'curve_peaks': [5, 12, 21, 34, 47, 63, 74, 85],
            'curve_valleys': [0, 8, 17, 28, 40, 55, 69, 80, 92]
        }
        
        results = []
        
        for pattern_name, positions in patterns.items():
            extracted = self.apply_grille(positions)
            
            # Test with ABSCISSA (our confirmed key)
            decrypted = self.vigenere_decrypt(extracted, 'ABSCISSA')
            score_data = self.score_plaintext(decrypted)
            
            if score_data['score'] > 0 or score_data['words']:
                results.append({
                    'pattern': pattern_name,
                    'score': score_data['score'],
                    'words': score_data['words'],
                    'text': decrypted[:30] if len(decrypted) > 30 else decrypted
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        
        if results:
            print("\nBest physical pattern results:")
            for res in results[:5]:
                print(f"\n{res['pattern']}:")
                print(f"  Score: {res['score']}")
                print(f"  Words: {res['words']}")
                print(f"  Text: {res['text']}...")
        
        return results

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK GRILLE - PHYSICAL MASK/GRILLE PATTERN TESTING")
    print("Exploring non-contiguous letter extraction")
    print("="*70)
    
    cipher = GrilleCipher()
    
    # Test 1: Mathematical grille patterns
    grille_results = cipher.test_grille_patterns()
    
    # Test 2: Physical sculpture patterns
    physical_results = cipher.test_physical_sculpture_patterns()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if grille_results:
        best = grille_results[0]
        print(f"\nBest grille pattern: {best['pattern']} ({best['method']})")
        print(f"Score: {best['score']}")
        print(f"Words found: {best['words']}")
        
        if best['score'] > 30:
            print("\n🎯 PROMISING GRILLE PATTERN FOUND!")
    else:
        print("\nNo significant grille patterns found")
    
    print("\n" + "="*70)
    print("FORK GRILLE COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()