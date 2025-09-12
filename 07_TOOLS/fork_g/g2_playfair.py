#!/usr/bin/env python3
"""
Fork G v2 - G.2 Playfair/Two-square/Four-square Implementation
Matrix digraph ciphers with tableau-derived keys
"""

import json
import os
import random
from typing import Dict, List, Tuple, Optional

class PlayfairCipher:
    def __init__(self, master_seed: int = 1337):
        self.k4_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        self.master_seed = master_seed
        random.seed(master_seed)
        
        # Known anchors
        self.anchors = {
            'EAST': (21, 24),
            'NORTHEAST': (25, 33),
            'BERLIN': (63, 68),
            'CLOCK': (69, 73)
        }
        
        # Load tableau
        self.tableau = self._load_tableau()
        
        # English validation
        self.bigram_blacklist = {'JQ', 'QZ', 'ZX', 'XJ', 'QX', 'JX', 'VQ', 'QV', 'JZ', 'ZJ'}
        self.english_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'WITH',
                              'HAVE', 'THIS', 'FROM', 'THEY', 'BEEN', 'MORE', 'WHEN'}
    
    def _load_tableau(self) -> Dict:
        """Load tableau from shared prep"""
        tableau_path = os.path.join(os.path.dirname(__file__), 'tableau_matrix.json')
        if os.path.exists(tableau_path):
            with open(tableau_path, 'r') as f:
                return json.load(f)
        return None
    
    def create_playfair_square(self, keyword: str, omit: str = 'J') -> List[List[str]]:
        """Create 5x5 Playfair square from keyword"""
        # Remove duplicates from keyword, preserve order
        seen = set()
        key_chars = []
        
        for char in keyword.upper():
            if char.isalpha() and char not in seen and char != omit:
                seen.add(char)
                key_chars.append(char)
        
        # Add remaining alphabet
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if char not in seen and char != omit:
                key_chars.append(char)
                seen.add(char)
        
        # Build 5x5 grid
        square = []
        for i in range(5):
            row = key_chars[i*5:(i+1)*5]
            square.append(row)
        
        return square
    
    def playfair_decrypt(self, ciphertext: str, square: List[List[str]], 
                        variant: str = 'standard') -> str:
        """Decrypt using Playfair cipher"""
        # Handle I/J substitution
        if 'J' not in [c for row in square for c in row]:
            ciphertext = ciphertext.replace('J', 'I')
        elif 'I' not in [c for row in square for c in row]:
            ciphertext = ciphertext.replace('I', 'J')
        
        # Create position lookup
        pos_lookup = {}
        for i, row in enumerate(square):
            for j, char in enumerate(row):
                pos_lookup[char] = (i, j)
        
        # Process digraphs
        plaintext = []
        i = 0
        
        while i < len(ciphertext):
            if i + 1 >= len(ciphertext):
                # Handle odd length
                plaintext.append(ciphertext[i])
                break
            
            c1, c2 = ciphertext[i], ciphertext[i+1]
            
            # Skip if not in square
            if c1 not in pos_lookup or c2 not in pos_lookup:
                plaintext.append(c1)
                plaintext.append(c2)
                i += 2
                continue
            
            r1, c1_col = pos_lookup[c1]
            r2, c2_col = pos_lookup[c2]
            
            # Apply Playfair rules
            if r1 == r2:  # Same row
                p1 = square[r1][(c1_col - 1) % 5]
                p2 = square[r2][(c2_col - 1) % 5]
            elif c1_col == c2_col:  # Same column
                p1 = square[(r1 - 1) % 5][c1_col]
                p2 = square[(r2 - 1) % 5][c2_col]
            else:  # Rectangle
                p1 = square[r1][c2_col]
                p2 = square[r2][c1_col]
            
            plaintext.append(p1)
            plaintext.append(p2)
            i += 2
        
        return ''.join(plaintext)
    
    def two_square_decrypt(self, ciphertext: str, square1: List[List[str]], 
                           square2: List[List[str]]) -> str:
        """Decrypt using Two-square cipher"""
        # Create position lookups
        pos1 = {}
        pos2 = {}
        
        for i, row in enumerate(square1):
            for j, char in enumerate(row):
                pos1[char] = (i, j)
        
        for i, row in enumerate(square2):
            for j, char in enumerate(row):
                pos2[char] = (i, j)
        
        plaintext = []
        i = 0
        
        while i < len(ciphertext) - 1:
            c1, c2 = ciphertext[i], ciphertext[i+1]
            
            # Check if both chars are in opposite squares
            if c1 in pos1 and c2 in pos2:
                r1, c1_col = pos1[c1]
                r2, c2_col = pos2[c2]
                
                # Rectangle swap
                p1 = square1[r1][c2_col] if c2_col < 5 else c1
                p2 = square2[r2][c1_col] if c1_col < 5 else c2
                
                plaintext.append(p1)
                plaintext.append(p2)
            elif c1 in pos2 and c2 in pos1:
                r1, c1_col = pos2[c1]
                r2, c2_col = pos1[c2]
                
                # Rectangle swap (reverse)
                p1 = square2[r1][c2_col] if c2_col < 5 else c1
                p2 = square1[r2][c1_col] if c1_col < 5 else c2
                
                plaintext.append(p1)
                plaintext.append(p2)
            else:
                # No transformation
                plaintext.append(c1)
                plaintext.append(c2)
            
            i += 2
        
        # Handle odd length
        if i < len(ciphertext):
            plaintext.append(ciphertext[i])
        
        return ''.join(plaintext)
    
    def generate_tableau_squares(self) -> Dict[str, List[Tuple[str, List[List[str]]]]]:
        """Generate Playfair squares from tableau"""
        if not self.tableau:
            return {}
        
        squares = {
            'single': [],
            'two_square': [],
            'four_square': []
        }
        
        # Single squares from tableau rows
        # PF-K: KRYPTOS row
        k_row = ''.join(self.tableau['tableau']['K'])
        k_square = self.create_playfair_square(k_row)
        squares['single'].append(('PF-K', k_square))
        
        # PF-YAR: Y, A, R rows combined
        if 'Y' in self.tableau['tableau'] and 'A' in self.tableau['tableau']:
            yar = ''.join(self.tableau['tableau']['Y'][:8]) + \
                  ''.join(self.tableau['tableau']['A'][:8]) + \
                  ''.join(self.tableau['tableau'].get('R', [])[:8])
            yar_square = self.create_playfair_square(yar)
            squares['single'].append(('PF-YAR', yar_square))
        
        # PF-L: Extra L row
        if 'L' in self.tableau['tableau']:
            l_row = ''.join(self.tableau['tableau']['L'])
            l_square = self.create_playfair_square(l_row)
            squares['single'].append(('PF-L', l_square))
        
        # Two-square combinations
        # TS-(K,Y): K row and Y row
        if 'Y' in self.tableau['tableau']:
            y_row = ''.join(self.tableau['tableau']['Y'])
            y_square = self.create_playfair_square(y_row)
            squares['two_square'].append(('TS-KY', (k_square, y_square)))
        
        # TS-(K,L): K row and L row
        if 'L' in self.tableau['tableau']:
            squares['two_square'].append(('TS-KL', (k_square, l_square)))
        
        # Keywords from K4 context
        berlin_square = self.create_playfair_square("BERLINCLOCK")
        squares['single'].append(('PF-BERLIN', berlin_square))
        
        northeast_square = self.create_playfair_square("NORTHEAST")
        squares['single'].append(('PF-NORTHEAST', northeast_square))
        
        # Two-square with keywords
        squares['two_square'].append(('TS-K-BERLIN', (k_square, berlin_square)))
        
        return squares
    
    def check_anchors(self, plaintext: str) -> bool:
        """Check if anchors are correct"""
        if len(plaintext) != 97:
            return False
        
        for anchor_text, (start, end) in self.anchors.items():
            if plaintext[start:end+1] != anchor_text:
                return False
        return True
    
    def check_head_sanity(self, plaintext: str) -> Tuple[bool, Dict]:
        """Check head sanity"""
        head = plaintext[:20] if len(plaintext) >= 20 else plaintext
        
        # Check bigram blacklist
        for i in range(len(head) - 1):
            if head[i:i+2] in self.bigram_blacklist:
                return False, {'failed': 'bigram_blacklist'}
        
        # Check consonant runs
        consonants = 'BCDFGHJKLMNPQRSTVWXYZ'
        max_run = 0
        current_run = 0
        
        for char in head:
            if char in consonants:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        
        if max_run >= 6:
            return False, {'failed': 'consonant_run', 'length': max_run}
        
        # Check for words
        words_found = []
        for word in self.english_words:
            if len(word) >= 4 and word in head:
                words_found.append(word)
        
        if not words_found:
            return False, {'failed': 'no_words'}
        
        return True, {'words': words_found}
    
    def test_all_squares(self) -> List[Dict]:
        """Test all generated squares"""
        squares = self.generate_tableau_squares()
        results = []
        
        print(f"Testing {len(squares['single'])} single squares...")
        
        # Test single Playfair squares
        for name, square in squares['single']:
            plaintext = self.playfair_decrypt(self.k4_ct, square)
            
            if self.check_anchors(plaintext):
                head_ok, head_info = self.check_head_sanity(plaintext)
                
                result = {
                    'type': 'playfair',
                    'name': name,
                    'plaintext': plaintext,
                    'head': plaintext[:20],
                    'anchors_ok': True,
                    'head_ok': head_ok,
                    'head_info': head_info
                }
                results.append(result)
                
                print(f"FOUND: {name}")
                print(f"  Head: {plaintext[:20]}")
                if head_ok:
                    print(f"  Words: {head_info['words']}")
        
        print(f"\nTesting {len(squares['two_square'])} two-square combinations...")
        
        # Test two-square combinations
        for name, (sq1, sq2) in squares['two_square']:
            plaintext = self.two_square_decrypt(self.k4_ct, sq1, sq2)
            
            if self.check_anchors(plaintext):
                head_ok, head_info = self.check_head_sanity(plaintext)
                
                result = {
                    'type': 'two_square',
                    'name': name,
                    'plaintext': plaintext,
                    'head': plaintext[:20],
                    'anchors_ok': True,
                    'head_ok': head_ok,
                    'head_info': head_info
                }
                results.append(result)
                
                print(f"FOUND: {name}")
                print(f"  Head: {plaintext[:20]}")
                if head_ok:
                    print(f"  Words: {head_info['words']}")
        
        return results
    
    def save_results(self, results: List[Dict]):
        """Save results"""
        if results:
            output_path = os.path.join(os.path.dirname(__file__), 'playfair_results.json')
            
            # Remove full plaintext for space
            save_results = []
            for r in results:
                save_r = r.copy()
                save_r.pop('plaintext', None)
                save_results.append(save_r)
            
            with open(output_path, 'w') as f:
                json.dump(save_results, f, indent=2)
            
            print(f"\nSaved {len(results)} results to {output_path}")


def main():
    print("=== Fork G v2 - G.2 Playfair/Digraph Ciphers ===")
    
    pf = PlayfairCipher()
    
    # Test all squares
    results = pf.test_all_squares()
    
    # Save results
    pf.save_results(results)
    
    print(f"\n=== Summary ===")
    print(f"Total candidates with correct anchors: {len(results)}")
    head_ok_count = sum(1 for r in results if r['head_ok'])
    print(f"Candidates with valid head: {head_ok_count}")


if __name__ == "__main__":
    main()