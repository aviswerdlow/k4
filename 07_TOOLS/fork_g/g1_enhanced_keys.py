#!/usr/bin/env python3
"""
Fork G v2 - Enhanced Key Generation for L=14 DT
Based on community IC findings showing L=14 promise
"""

import json
import os
from typing import List, Dict, Tuple
from itertools import combinations, permutations

class EnhancedKeyGenerator:
    def __init__(self):
        self.load_tableau()
        
    def load_tableau(self):
        """Load tableau from shared prep"""
        tableau_path = os.path.join(os.path.dirname(__file__), 'tableau_matrix.json')
        with open(tableau_path, 'r') as f:
            self.tableau = json.load(f)
    
    def generate_all_keys(self) -> Dict[str, List[Tuple[str, List[int]]]]:
        """Generate comprehensive set of L=14 keys from multiple sources"""
        
        all_keys = {
            'tableau_rows': [],
            'tableau_cols': [],
            'keywords': [],
            'patterns': [],
            'anchors': [],
            'numeric': []
        }
        
        # 1. Tableau row-based keys
        # K-R-Y-P-T-O-S pattern
        kryptos_key = self._word_to_key("KRYPTOSABCDEFG", 14)
        all_keys['tableau_rows'].append(("KRYPTOS_row", kryptos_key))
        
        # Y-A-R raised letters emphasis
        yar_key = self._word_to_key("YARABCDEFGHIJK", 14)
        all_keys['tableau_rows'].append(("YAR_emphasis", yar_key))
        
        # Extra L row special
        l_row_key = self._word_to_key("LABCDEFGHIJKMN", 14)
        all_keys['tableau_rows'].append(("L_row_special", l_row_key))
        
        # 2. Keywords from known K4 context
        # BERLIN CLOCK as key
        berlin_clock_key = self._word_to_key("BERLINCLOCK", 14)
        all_keys['keywords'].append(("BERLIN_CLOCK", berlin_clock_key))
        
        # NORTHEAST as key
        northeast_key = self._word_to_key("NORTHEAST", 14)
        all_keys['keywords'].append(("NORTHEAST", northeast_key))
        
        # Combined anchors
        combined_key = self._word_to_key("EASTNORTHEASTB", 14)
        all_keys['keywords'].append(("COMBINED_ANCHORS", combined_key))
        
        # 3. Pattern-based keys (IC-optimized)
        # Alternating pattern for high IC
        pattern1 = [1, 14, 2, 13, 3, 12, 4, 11, 5, 10, 6, 9, 7, 8]
        all_keys['patterns'].append(("ALTERNATING", pattern1))
        
        # Spiral pattern
        spiral = [7, 8, 6, 9, 5, 10, 4, 11, 3, 12, 2, 13, 1, 14]
        all_keys['patterns'].append(("SPIRAL", spiral))
        
        # Two-block pattern (7+7)
        two_block = [1, 2, 3, 4, 5, 6, 7, 14, 13, 12, 11, 10, 9, 8]
        all_keys['patterns'].append(("TWO_BLOCK", two_block))
        
        # 4. Anchor-position based
        # Positions 21-24 (EAST)
        east_pos = self._positions_to_key([21, 22, 23, 24], 14)
        all_keys['anchors'].append(("EAST_POS", east_pos))
        
        # Positions 63-68 (BERLIN)
        berlin_pos = self._positions_to_key([63, 64, 65, 66, 67, 68], 14)
        all_keys['anchors'].append(("BERLIN_POS", berlin_pos))
        
        # 5. Numeric sequences
        # Fibonacci mod 14
        fib = [1, 1, 2, 3, 5, 8, 13, 7, 6, 13, 5, 4, 9, 13]
        fib_key = [(f % 14) + 1 for f in fib][:14]
        all_keys['numeric'].append(("FIBONACCI", self._normalize_key(fib_key)))
        
        # Prime positions
        primes = [2, 3, 5, 7, 11, 13, 1, 4, 6, 8, 9, 10, 12, 14]
        all_keys['numeric'].append(("PRIMES", primes))
        
        return all_keys
    
    def _word_to_key(self, word: str, length: int) -> List[int]:
        """Convert word to columnar key of given length"""
        # Remove duplicates, preserve order
        seen = set()
        unique = []
        for char in word.upper():
            if char not in seen and char.isalpha():
                seen.add(char)
                unique.append(char)
        
        # Fill to length with remaining alphabet
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if len(unique) >= length:
                break
            if char not in seen:
                unique.append(char)
                seen.add(char)
        
        # Truncate to length
        unique = unique[:length]
        
        # Convert to column order
        sorted_chars = sorted(enumerate(unique), key=lambda x: x[1])
        key = [0] * length
        for rank, (pos, _) in enumerate(sorted_chars, 1):
            key[pos] = rank
        
        return key
    
    def _positions_to_key(self, positions: List[int], length: int) -> List[int]:
        """Convert K4 positions to a key"""
        # Use positions mod 14 as starting ranks
        key = []
        used = set()
        
        for pos in positions:
            rank = (pos % length) + 1
            while rank in used:
                rank = (rank % length) + 1
            key.append(rank)
            used.add(rank)
        
        # Fill remaining
        for i in range(1, length + 1):
            if len(key) >= length:
                break
            if i not in used:
                key.append(i)
        
        return key[:length]
    
    def _normalize_key(self, key: List[int]) -> List[int]:
        """Ensure key contains 1..14 exactly once"""
        # Create mapping from values to ranks
        sorted_vals = sorted(enumerate(key), key=lambda x: x[1])
        normalized = [0] * len(key)
        
        for rank, (pos, _) in enumerate(sorted_vals, 1):
            normalized[pos] = rank
        
        return normalized
    
    def test_key_pair(self, key1: List[int], key2: List[int], 
                     ct: str = None) -> Dict:
        """Test a key pair for basic statistics"""
        if ct is None:
            ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        # Import DT engine
        from g1_double_transposition import DoubleTransposition
        dt = DoubleTransposition()
        
        # Decrypt
        plaintext = dt.double_columnar_decrypt(ct, key1, key2)
        
        if not plaintext:
            return {'valid': False}
        
        # Check anchors
        anchors_ok = dt.check_anchors(plaintext)
        
        # Check head
        head_ok, head_info = dt.check_head_sanity(plaintext)
        
        return {
            'valid': True,
            'plaintext': plaintext,
            'anchors_ok': anchors_ok,
            'head_ok': head_ok,
            'head_info': head_info,
            'head': plaintext[:20] if plaintext else None
        }
    
    def find_promising_pairs(self, max_tests: int = 1000) -> List[Dict]:
        """Find promising key pairs"""
        all_keys = self.generate_all_keys()
        
        results = []
        tests = 0
        
        # Flatten all keys
        flat_keys = []
        for category, key_list in all_keys.items():
            for name, key in key_list:
                flat_keys.append((category, name, key))
        
        print(f"Testing {len(flat_keys)} unique keys in pairs...")
        
        # Test combinations
        for i, (cat1, name1, key1) in enumerate(flat_keys):
            for cat2, name2, key2 in flat_keys[i:]:  # Include same key twice
                if tests >= max_tests:
                    break
                
                result = self.test_key_pair(key1, key2)
                tests += 1
                
                if result['valid'] and result['anchors_ok']:
                    result['key1_name'] = f"{cat1}/{name1}"
                    result['key2_name'] = f"{cat2}/{name2}"
                    result['key1'] = key1
                    result['key2'] = key2
                    results.append(result)
                    
                    print(f"FOUND: {name1} x {name2}")
                    print(f"  Head: {result['head']}")
                    print(f"  Head OK: {result['head_ok']}")
                    if result['head_ok']:
                        print(f"  Words: {result['head_info']['words']}")
                
                if tests % 100 == 0:
                    print(f"Tested {tests} pairs...")
        
        return results


def main():
    print("=== Enhanced L=14 Key Generation ===")
    
    gen = EnhancedKeyGenerator()
    
    # Generate all keys
    all_keys = gen.generate_all_keys()
    
    print("\nGenerated keys by category:")
    for category, key_list in all_keys.items():
        print(f"  {category}: {len(key_list)} keys")
        for name, key in key_list[:3]:  # Show first 3
            print(f"    {name}: {key[:7]}...")
    
    # Find promising pairs
    print("\nSearching for promising key pairs...")
    results = gen.find_promising_pairs(max_tests=500)
    
    print(f"\nFound {len(results)} valid pairs with correct anchors")
    
    # Save results
    if results:
        output_path = os.path.join(os.path.dirname(__file__), 'enhanced_dt_results.json')
        with open(output_path, 'w') as f:
            # Remove plaintext for space
            save_results = []
            for r in results:
                save_r = r.copy()
                save_r.pop('plaintext', None)
                save_results.append(save_r)
            json.dump(save_results, f, indent=2)
        print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()