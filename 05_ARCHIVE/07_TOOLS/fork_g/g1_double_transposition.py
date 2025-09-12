#!/usr/bin/env python3
"""
Fork G v2 - G.1 Double-Transposition Engine
Priority 1: L=14 double columnar transposition with anchor-aware pruning
"""

import json
import os
import random
from typing import Dict, List, Tuple, Optional
from itertools import permutations, product
import hashlib

class DoubleTransposition:
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
        
        # Load tableau for key generation
        self.tableau = self._load_tableau()
        
        # Hard bigram blacklist
        self.bigram_blacklist = {'JQ', 'QZ', 'ZX', 'XJ', 'QX', 'JX', 'VQ', 'QV', 'JZ', 'ZJ'}
        
        # Common English words for validation
        self.english_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'WITH', 
                              'HAVE', 'THIS', 'FROM', 'THEY', 'BEEN', 'MORE', 'WHEN',
                              'WILL', 'WOULD', 'THERE', 'THEIR', 'WHAT', 'ABOUT', 'WHICH'}
    
    def _load_tableau(self) -> Dict:
        """Load the tableau matrix from shared prep"""
        tableau_path = os.path.join(os.path.dirname(__file__), 'tableau_matrix.json')
        if os.path.exists(tableau_path):
            with open(tableau_path, 'r') as f:
                return json.load(f)
        return None
    
    def double_columnar_decrypt(self, ciphertext: str, key1: List[int], key2: List[int], 
                                route: str = 'standard') -> str:
        """
        Perform double columnar transposition decryption
        CT -> intermediate -> PT
        
        Args:
            ciphertext: The ciphertext string
            key1: First transposition key (column order)
            key2: Second transposition key (column order)
            route: Reading route ('standard', 'boustrophedon', 'spiral')
        """
        n = len(ciphertext)
        cols1 = len(key1)
        cols2 = len(key2)
        
        # For 97 chars with 14 columns: 6 rows of 14 + 1 row of 13
        # This gives us 7 rows total, with the last row incomplete
        
        # Stage 1: Undo second transposition (applied last during encryption)
        rows2 = (n + cols2 - 1) // cols2  # Ceiling division
        intermediate = self._columnar_decrypt(ciphertext, key2, rows2, route)
        if not intermediate:
            return None
        
        # Stage 2: Undo first transposition (applied first during encryption)
        rows1 = (n + cols1 - 1) // cols1  # Ceiling division  
        plaintext = self._columnar_decrypt(intermediate, key1, rows1, route)
        
        return plaintext
    
    def _columnar_decrypt(self, text: str, key: List[int], rows: int, 
                          route: str) -> str:
        """Single columnar transposition decryption"""
        cols = len(key)
        n = len(text)
        
        # Build grid
        grid = [['' for _ in range(cols)] for _ in range(rows)]
        
        # Calculate column heights (some columns may be shorter if n doesn't divide evenly)
        full_cols = n % cols if n % cols != 0 else cols
        col_heights = [rows if i < full_cols else rows - 1 for i in range(cols)]
        
        # Fill grid by reading columns in key order
        pos = 0
        for col_num in key:
            height = col_heights[col_num - 1]  # key is 1-indexed
            for row in range(height):
                if pos < n:
                    grid[row][col_num - 1] = text[pos]
                    pos += 1
        
        # Read out by rows according to route
        result = []
        if route == 'standard':
            for row in grid:
                result.extend([c for c in row if c])
        elif route == 'boustrophedon':
            for i, row in enumerate(grid):
                if i % 2 == 0:
                    result.extend([c for c in row if c])
                else:
                    result.extend([c for c in reversed(row) if c])
        elif route == 'spiral':
            result = self._read_spiral(grid)
        
        return ''.join(result)
    
    def _read_spiral(self, grid: List[List[str]]) -> List[str]:
        """Read grid in spiral pattern"""
        result = []
        if not grid:
            return result
        
        rows, cols = len(grid), len(grid[0])
        top, bottom, left, right = 0, rows - 1, 0, cols - 1
        
        while top <= bottom and left <= right:
            # Right
            for i in range(left, right + 1):
                if grid[top][i]:
                    result.append(grid[top][i])
            top += 1
            
            # Down
            for i in range(top, bottom + 1):
                if grid[i][right]:
                    result.append(grid[i][right])
            right -= 1
            
            # Left
            if top <= bottom:
                for i in range(right, left - 1, -1):
                    if grid[bottom][i]:
                        result.append(grid[bottom][i])
                bottom -= 1
            
            # Up
            if left <= right:
                for i in range(bottom, top - 1, -1):
                    if grid[i][left]:
                        result.append(grid[i][left])
                left += 1
        
        return result
    
    def generate_tableau_keys(self, length: int = 14) -> Dict[str, List[List[int]]]:
        """Generate key orders from tableau using explicit recipes"""
        if not self.tableau:
            return {}
        
        keys = {
            'row_based': [],
            'column_based': [],
            'diagonal': [],
            'spiral': []
        }
        
        # R1: K row (KRYPTOS row)
        k_row = self.tableau['tableau'].get('K', [])
        if k_row:
            key_str = self._dedupe_fill(''.join(k_row[:length]), length)
            keys['row_based'].append(self._string_to_order(key_str))
        
        # R2: Y, A, R rows concatenated
        y_row = self.tableau['tableau'].get('Y', [])
        a_row = self.tableau['tableau'].get('A', [])
        r_row = self.tableau['tableau'].get('R', [])
        if y_row and a_row and r_row:
            yar_str = ''.join(y_row[:5] + a_row[:5] + r_row[:4])
            key_str = self._dedupe_fill(yar_str, length)
            keys['row_based'].append(self._string_to_order(key_str))
        
        # R3: Extra-L row emphasized
        l_row = self.tableau['tableau'].get('L', [])
        if l_row:
            key_str = self._dedupe_fill(''.join(l_row[:length]), length)
            keys['row_based'].append(self._string_to_order(key_str))
        
        # C1: Column under first 'T'
        for col_idx, col_label in enumerate(self.tableau['col_labels']):
            if col_label == 'T':
                col_chars = [self.tableau['tableau'][row][col_idx] 
                            for row in self.tableau['row_labels'][:length]]
                key_str = self._dedupe_fill(''.join(col_chars), length)
                keys['column_based'].append(self._string_to_order(key_str))
                break
        
        # C2: Column 7 and adjacents
        if len(self.tableau['col_labels']) > 7:
            col_chars = []
            indices = [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12, 1, 13, 0]
            for idx in indices[:length]:
                if idx < len(self.tableau['col_labels']):
                    col_chars.append(self.tableau['col_labels'][idx])
            key_str = self._dedupe_fill(''.join(col_chars), length)
            keys['column_based'].append(self._string_to_order(key_str))
        
        # D1: Main diagonal from (K, K)
        diag_chars = []
        for i in range(length):
            row_idx = i % len(self.tableau['row_labels'])
            col_idx = i % len(self.tableau['col_labels'])
            row_label = self.tableau['row_labels'][row_idx]
            diag_chars.append(self.tableau['tableau'][row_label][col_idx])
        key_str = self._dedupe_fill(''.join(diag_chars), length)
        keys['diagonal'].append(self._string_to_order(key_str))
        
        return keys
    
    def _dedupe_fill(self, s: str, target_len: int) -> str:
        """Remove duplicates, preserve order, fill to target length"""
        seen = set()
        result = []
        
        for char in s:
            if char not in seen and char.isalpha():
                result.append(char.upper())
                seen.add(char.upper())
        
        # Fill with remaining alphabet
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if len(result) >= target_len:
                break
            if char not in seen:
                result.append(char)
                seen.add(char)
        
        return ''.join(result[:target_len])
    
    def _string_to_order(self, s: str) -> List[int]:
        """Convert string to column order by alphabetical rank"""
        # Create (char, original_position) pairs
        pairs = [(char, i) for i, char in enumerate(s)]
        # Sort by char, then by original position for stability
        pairs.sort(key=lambda x: (x[0], x[1]))
        
        # Create order array
        order = [0] * len(s)
        for rank, (_, orig_pos) in enumerate(pairs, 1):
            order[orig_pos] = rank
        
        return order
    
    def check_anchors(self, plaintext: str) -> bool:
        """Check if all anchors appear at correct positions"""
        if len(plaintext) != 97:
            return False
        
        for anchor_text, (start, end) in self.anchors.items():
            if plaintext[start:end+1] != anchor_text:
                return False
        
        return True
    
    def check_head_sanity(self, plaintext: str) -> Tuple[bool, Dict]:
        """Check head (0-20) for English sanity"""
        head = plaintext[:20]
        
        # Check for bigram blacklist
        for i in range(len(head) - 1):
            bigram = head[i:i+2]
            if bigram in self.bigram_blacklist:
                return False, {'failed': 'bigram_blacklist', 'bigram': bigram}
        
        # Check for 6+ consonant runs
        consonants = 'BCDFGHJKLMNPQRSTVWXYZ'
        consonant_run = 0
        max_run = 0
        for char in head:
            if char in consonants:
                consonant_run += 1
                max_run = max(max_run, consonant_run)
            else:
                consonant_run = 0
        
        if max_run >= 6:
            return False, {'failed': 'consonant_run', 'length': max_run}
        
        # Check for at least one 4+ letter word
        words_found = []
        for word in self.english_words:
            if len(word) >= 4 and word in head:
                words_found.append(word)
        
        if not words_found:
            return False, {'failed': 'no_words'}
        
        return True, {'words': words_found, 'max_consonant_run': max_run}
    
    def run_with_controls(self, key1: List[int], key2: List[int], 
                          route: str = 'standard') -> Dict:
        """Run decryption with negative controls and null model"""
        
        # Main decryption
        plaintext = self.double_columnar_decrypt(self.k4_ct, key1, key2, route)
        if not plaintext:
            return {'status': 'failed', 'reason': 'decryption_failed'}
        
        # Gate A: Check anchors
        if not self.check_anchors(plaintext):
            return {'status': 'failed', 'reason': 'anchors_incorrect'}
        
        # Gate B & C: Check head sanity
        head_ok, head_info = self.check_head_sanity(plaintext)
        if not head_ok:
            return {'status': 'failed', 'reason': 'head_sanity', 'details': head_info}
        
        # Negative control: Scrambled anchors
        scrambled_ct = list(self.k4_ct)
        for anchor_text, (start, end) in self.anchors.items():
            # Replace with random 4-letter string
            random_anchor = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 
                                                  k=len(anchor_text)))
            for i, char in enumerate(random_anchor):
                if start + i <= end:
                    scrambled_ct[start + i] = char
        
        scrambled_ct = ''.join(scrambled_ct)
        scrambled_pt = self.double_columnar_decrypt(scrambled_ct, key1, key2, route)
        
        if scrambled_pt and self.check_anchors(scrambled_pt):
            return {'status': 'failed', 'reason': 'passed_negative_control'}
        
        # Null model: Random key pairs
        null_scores = []
        for _ in range(100):
            random_key1 = random.sample(range(1, len(key1) + 1), len(key1))
            random_key2 = random.sample(range(1, len(key2) + 1), len(key2))
            
            null_pt = self.double_columnar_decrypt(self.k4_ct, random_key1, random_key2, route)
            if null_pt:
                null_ok, _ = self.check_head_sanity(null_pt[:20] if len(null_pt) >= 20 else null_pt)
                null_scores.append(1 if null_ok else 0)
        
        # Must beat 95th percentile
        null_threshold = sorted(null_scores)[94] if len(null_scores) >= 95 else 0
        if sum(null_scores) / len(null_scores) >= 0.05:  # Too many random keys work
            return {'status': 'failed', 'reason': 'failed_null_model'}
        
        # Success!
        result = {
            'status': 'success',
            'plaintext': plaintext,
            'head': plaintext[:20],
            'key1': key1,
            'key2': key2,
            'route': route,
            'head_info': head_info,
            'hash': hashlib.sha256(plaintext.encode()).hexdigest()[:16]
        }
        
        return result
    
    def run_battery(self, max_per_family: int = 100) -> List[Dict]:
        """Run full battery of L=14 double transposition tests"""
        results = []
        
        # Generate tableau keys
        all_keys = self.generate_tableau_keys(14)
        
        routes = ['standard', 'boustrophedon', 'spiral']
        
        # Test key pairs from same family
        for family, key_list in all_keys.items():
            if not key_list:
                continue
                
            tested = 0
            for key1, key2 in product(key_list, repeat=2):
                if tested >= max_per_family:
                    break
                
                for route in routes:
                    result = self.run_with_controls(key1, key2, route)
                    result['family'] = family
                    result['tested'] = tested
                    
                    if result['status'] == 'success':
                        results.append(result)
                        print(f"SUCCESS: {family} with route {route}")
                        print(f"  Head: {result['head']}")
                        print(f"  Words: {result['head_info']['words']}")
                    
                    tested += 1
                    
                    if tested >= max_per_family:
                        break
        
        return results
    
    def save_results(self, results: List[Dict]):
        """Save results to files"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Save successful results
        if results:
            results_path = os.path.join(output_dir, 'dt_results.json')
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Saved {len(results)} results to {results_path}")
            
            # Create explain file for top results
            explain_path = os.path.join(output_dir, 'DT_EXPLAIN.txt')
            with open(explain_path, 'w') as f:
                f.write("=== Fork G v2 - Double Transposition Results ===\n\n")
                
                for i, result in enumerate(results[:20], 1):
                    f.write(f"Result #{i}\n")
                    f.write(f"Family: {result['family']}\n")
                    f.write(f"Route: {result['route']}\n")
                    f.write(f"Key1: {result['key1']}\n")
                    f.write(f"Key2: {result['key2']}\n")
                    f.write(f"Head: {result['head']}\n")
                    f.write(f"Words found: {result['head_info']['words']}\n")
                    f.write(f"Hash: {result['hash']}\n")
                    f.write("-" * 50 + "\n\n")
            
            print(f"Saved explanations to {explain_path}")


def main():
    print("=== Fork G v2 - G.1 Double Transposition ===")
    print("Testing L=14 with tableau-derived keys...")
    
    dt = DoubleTransposition()
    
    # First test with a simple known transposition
    print("\nTesting basic transposition...")
    test_key1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    test_key2 = [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    test_result = dt.double_columnar_decrypt(dt.k4_ct, test_key1, test_key2)
    if test_result:
        print(f"Test decrypt successful, length: {len(test_result)}")
        print(f"First 20 chars: {test_result[:20]}")
        anchors_ok = dt.check_anchors(test_result)
        print(f"Anchors correct: {anchors_ok}")
    else:
        print("Test decrypt failed")
    
    # Run battery
    print("\nRunning full battery...")
    results = dt.run_battery(max_per_family=50)
    
    # Save results
    dt.save_results(results)
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Total successful candidates: {len(results)}")
    if results:
        print("Top candidates by family:")
        by_family = {}
        for r in results:
            family = r['family']
            if family not in by_family:
                by_family[family] = []
            by_family[family].append(r)
        
        for family, family_results in by_family.items():
            print(f"  {family}: {len(family_results)} successful")


if __name__ == "__main__":
    main()