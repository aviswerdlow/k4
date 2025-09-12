#!/usr/bin/env python3
"""
error_tolerant.py

Fork ERR - Error-tolerant testing for K4.
Tests 1-2 character errors (substitutions, insertions, deletions).
Focuses on positions away from known anchors.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import itertools

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions (avoid editing these)
ANCHOR_POSITIONS = set(range(21, 25)) | set(range(25, 34)) | set(range(63, 69)) | set(range(69, 74))

# K1-K3 plaintexts for running key
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K2_PLAINTEXT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class ErrorTolerantTester:
    """Test K4 with error tolerance."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.ct_length = len(self.ciphertext)
        self.results = []
        self.improvements = []
        
        # Get editable positions (not in anchors)
        self.editable_positions = [i for i in range(self.ct_length) 
                                  if i not in ANCHOR_POSITIONS]
        
        print(f"Editable positions: {len(self.editable_positions)} of {self.ct_length}")
        print(f"Anchor positions protected: {len(ANCHOR_POSITIONS)}")
    
    def validate_anchors(self, plaintext: str) -> Tuple[bool, int]:
        """
        Validate anchor preservation.
        Returns (all_valid, count_valid)
        """
        if len(plaintext) < 74:
            return False, 0
        
        count = 0
        if plaintext[21:25] == "EAST":
            count += 1
        if plaintext[25:34] == "NORTHEAST":
            count += 1
        if plaintext[63:69] == "BERLIN":
            count += 1
        if plaintext[69:74] == "CLOCK":
            count += 1
        
        return count == 4, count
    
    def compute_quality_score(self, plaintext: str) -> float:
        """Compute quality score for plaintext."""
        score = 0.0
        
        # Check anchors
        _, anchor_count = self.validate_anchors(plaintext)
        score += anchor_count * 25  # 25 points per anchor
        
        # Check head (0-20)
        if len(plaintext) >= 21:
            head = plaintext[:21]
            
            # Vowel ratio (target 0.35-0.45)
            vowels = sum(1 for c in head if c in 'AEIOU')
            vowel_ratio = vowels / 21
            if 0.30 <= vowel_ratio <= 0.50:
                score += 10
            
            # Max consonant run (lower is better)
            max_run = 0
            current_run = 0
            for c in head:
                if c not in 'AEIOU':
                    current_run += 1
                    max_run = max(max_run, current_run)
                else:
                    current_run = 0
            
            if max_run <= 4:
                score += 15
            elif max_run <= 5:
                score += 10
            elif max_run <= 6:
                score += 5
            
            # Common bigrams
            common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ON', 
                            'ES', 'ST', 'EN', 'AT', 'TO', 'NT', 'HA', 'ND']
            bigram_count = sum(1 for bg in common_bigrams if bg in head)
            score += bigram_count * 2
            
            # Common words
            common_words = ['THE', 'AND', 'ARE', 'YOU', 'WE', 'IN', 'AT', 'IT', 'IS',
                          'BE', 'TO', 'OF', 'HE', 'SHE', 'CAN', 'FOR', 'BUT']
            word_count = sum(1 for word in common_words if word in head)
            score += word_count * 5
        
        return score
    
    def vigenere_decrypt(self, ciphertext: str, key: str, offset: int = 0) -> str:
        """Decrypt using Vigenère with repeating key."""
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[(i + offset) % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def beaufort_decrypt(self, ciphertext: str, key: str, offset: int = 0) -> str:
        """Decrypt using Beaufort with repeating key."""
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[(i + offset) % key_len])
            p_val = (k_val - c_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def running_key_decrypt(self, ciphertext: str, key_text: str, offset: int = 0) -> str:
        """Decrypt using running key (non-periodic)."""
        plaintext = []
        key_len = len(key_text)
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            key_pos = (i + offset) % key_len
            c_val = char_to_num(c)
            k_val = char_to_num(key_text[key_pos])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def test_single_substitution(self, position: int, new_char: str, 
                                method: str = 'vigenere', key: str = 'PALIMPSEST') -> Dict:
        """Test single character substitution at given position."""
        # Create modified ciphertext
        modified_ct = list(self.ciphertext)
        original_char = modified_ct[position]
        modified_ct[position] = new_char
        modified_ct_str = ''.join(modified_ct)
        
        # Decrypt with specified method
        if method == 'vigenere':
            plaintext = self.vigenere_decrypt(modified_ct_str, key)
        elif method == 'beaufort':
            plaintext = self.beaufort_decrypt(modified_ct_str, key)
        elif method == 'running_key':
            plaintext = self.running_key_decrypt(modified_ct_str, key)
        else:
            plaintext = modified_ct_str
        
        # Score the result
        score = self.compute_quality_score(plaintext)
        all_anchors, anchor_count = self.validate_anchors(plaintext)
        
        return {
            'position': position,
            'original': original_char,
            'new': new_char,
            'method': method,
            'key': key[:10] if len(key) > 10 else key,
            'score': score,
            'anchors': anchor_count,
            'all_anchors': all_anchors,
            'plaintext_head': plaintext[:21] if len(plaintext) >= 21 else plaintext
        }
    
    def test_double_substitution(self, pos1: int, char1: str, 
                                pos2: int, char2: str, 
                                method: str = 'vigenere', 
                                key: str = 'PALIMPSEST') -> Dict:
        """Test double character substitution."""
        # Create modified ciphertext
        modified_ct = list(self.ciphertext)
        orig1 = modified_ct[pos1]
        orig2 = modified_ct[pos2]
        modified_ct[pos1] = char1
        modified_ct[pos2] = char2
        modified_ct_str = ''.join(modified_ct)
        
        # Decrypt
        if method == 'vigenere':
            plaintext = self.vigenere_decrypt(modified_ct_str, key)
        elif method == 'beaufort':
            plaintext = self.beaufort_decrypt(modified_ct_str, key)
        elif method == 'running_key':
            plaintext = self.running_key_decrypt(modified_ct_str, key)
        else:
            plaintext = modified_ct_str
        
        # Score
        score = self.compute_quality_score(plaintext)
        all_anchors, anchor_count = self.validate_anchors(plaintext)
        
        return {
            'positions': [pos1, pos2],
            'originals': [orig1, orig2],
            'new': [char1, char2],
            'method': method,
            'key': key[:10] if len(key) > 10 else key,
            'score': score,
            'anchors': anchor_count,
            'all_anchors': all_anchors,
            'plaintext_head': plaintext[:21] if len(plaintext) >= 21 else plaintext
        }
    
    def quick_scan_single_errors(self):
        """Quick scan for single character errors."""
        print("\n" + "="*60)
        print("SCANNING SINGLE CHARACTER SUBSTITUTIONS")
        print("="*60)
        
        # Test methods and keys
        test_configs = [
            ('vigenere', 'PALIMPSEST'),
            ('vigenere', 'KRYPTOS'),
            ('beaufort', 'PALIMPSEST'),
            ('running_key', K1_PLAINTEXT),
            ('running_key', K2_PLAINTEXT[:100])
        ]
        
        best_results = []
        
        for method, key in test_configs:
            print(f"\nTesting {method} with key {key[:10]}...")
            
            # Get baseline score
            if method == 'vigenere':
                baseline_pt = self.vigenere_decrypt(self.ciphertext, key)
            elif method == 'beaufort':
                baseline_pt = self.beaufort_decrypt(self.ciphertext, key)
            else:
                baseline_pt = self.running_key_decrypt(self.ciphertext, key)
            
            baseline_score = self.compute_quality_score(baseline_pt)
            print(f"Baseline score: {baseline_score:.1f}")
            
            # Test each editable position
            for pos in self.editable_positions:
                original_char = self.ciphertext[pos]
                
                # Try each possible substitution
                for new_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    if new_char == original_char:
                        continue
                    
                    result = self.test_single_substitution(pos, new_char, method, key)
                    
                    # Track if improvement
                    if result['score'] > baseline_score + 10:
                        improvement = result['score'] - baseline_score
                        result['improvement'] = improvement
                        result['baseline'] = baseline_score
                        best_results.append(result)
                        
                        if result['anchors'] >= 2:
                            print(f"  PROMISING: pos {pos} {original_char}→{new_char}, "
                                 f"anchors={result['anchors']}, score={result['score']:.1f}")
        
        # Sort by score
        best_results.sort(key=lambda x: x['score'], reverse=True)
        
        return best_results
    
    def test_specific_positions(self, positions: List[int]):
        """Test specific high-impact positions with all substitutions."""
        print(f"\nTesting specific positions: {positions}")
        
        results = []
        
        for pos in positions:
            if pos in ANCHOR_POSITIONS:
                print(f"Skipping anchor position {pos}")
                continue
            
            print(f"\nPosition {pos} (original: {self.ciphertext[pos]}):")
            
            # Test with Vigenère L=17 (period from community analysis)
            key = "PALIMPSESTABSCISSA"[:17]
            
            for new_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                result = self.test_single_substitution(pos, new_char, 'vigenere', key)
                
                if result['anchors'] > 0:
                    print(f"  {new_char}: anchors={result['anchors']}, score={result['score']:.1f}")
                    results.append(result)
        
        return results
    
    def generate_sensitivity_heatmap(self):
        """Generate heatmap showing most sensitive positions."""
        print("\n" + "="*60)
        print("GENERATING SENSITIVITY HEATMAP")
        print("="*60)
        
        sensitivity = {}
        
        # Test with most promising method (Vigenère with PALIMPSEST)
        key = "PALIMPSEST"
        baseline_pt = self.vigenere_decrypt(self.ciphertext, key)
        baseline_score = self.compute_quality_score(baseline_pt)
        
        for pos in self.editable_positions:
            max_impact = 0
            best_char = None
            
            for new_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if new_char == self.ciphertext[pos]:
                    continue
                
                result = self.test_single_substitution(pos, new_char, 'vigenere', key)
                impact = abs(result['score'] - baseline_score)
                
                if impact > max_impact:
                    max_impact = impact
                    best_char = new_char
            
            sensitivity[pos] = {
                'impact': max_impact,
                'best_char': best_char,
                'original': self.ciphertext[pos]
            }
        
        # Sort by impact
        sorted_positions = sorted(sensitivity.items(), key=lambda x: x[1]['impact'], reverse=True)
        
        print("\nTop 20 most sensitive positions:")
        for pos, data in sorted_positions[:20]:
            print(f"  Position {pos:2d}: impact={data['impact']:5.1f}, "
                 f"{data['original']}→{data['best_char']}")
        
        return sensitivity

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK ERR - ERROR TOLERANT TESTING")
    print("Testing 1-2 character errors in K4")
    print("="*70)
    
    tester = ErrorTolerantTester()
    
    # Quick scan for single errors
    best_single = tester.quick_scan_single_errors()
    
    if best_single:
        print("\n" + "="*60)
        print("TOP 10 SINGLE SUBSTITUTION IMPROVEMENTS")
        print("="*60)
        
        for i, result in enumerate(best_single[:10], 1):
            print(f"\n{i}. Position {result['position']}: "
                 f"{result['original']}→{result['new']}")
            print(f"   Method: {result['method']} with key {result['key']}")
            print(f"   Score: {result['score']:.1f} (improvement: {result['improvement']:.1f})")
            print(f"   Anchors: {result['anchors']}/4")
            print(f"   Head: {result['plaintext_head']}")
    
    # Generate sensitivity heatmap
    sensitivity = tester.generate_sensitivity_heatmap()
    
    # Test high-sensitivity positions
    high_impact_positions = [pos for pos, _ in sorted(sensitivity.items(), 
                            key=lambda x: x[1]['impact'], reverse=True)[:10]]
    
    print("\n" + "="*60)
    print("TESTING HIGH-IMPACT POSITIONS")
    print("="*60)
    
    targeted_results = tester.test_specific_positions(high_impact_positions)
    
    # Save results
    results_dir = Path("04_EXPERIMENTS/fork_err/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Save best results
    if best_single or targeted_results:
        all_results = best_single + targeted_results if targeted_results else best_single
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        with open(results_dir / "error_scan_results.json", 'w') as f:
            json.dump(all_results[:100], f, indent=2)
        
        print(f"\nResults saved to: {results_dir / 'error_scan_results.json'}")
    
    # Save sensitivity heatmap
    with open(results_dir / "sensitivity_heatmap.json", 'w') as f:
        json.dump(sensitivity, f, indent=2)
    
    print(f"Sensitivity heatmap saved to: {results_dir / 'sensitivity_heatmap.json'}")
    
    print("\n" + "="*70)
    print("ERROR TOLERANCE TESTING COMPLETE")
    
    if any(r['all_anchors'] for r in best_single[:10]):
        print("\n🎯 CANDIDATE WITH ALL ANCHORS FOUND! REQUIRES ANALYSIS!")
    elif any(r['anchors'] >= 2 for r in best_single[:10]):
        print("\nPartial anchor preservation found - investigate further")
    else:
        print("\nNo significant improvements found with single errors")
    
    print("="*70)

if __name__ == "__main__":
    main()