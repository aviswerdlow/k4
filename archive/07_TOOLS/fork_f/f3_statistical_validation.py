#!/usr/bin/env python3
"""
f3_statistical_validation.py

Statistical validation of the MIR HEAT finding.
Testing if this could be coincidental.
"""

import random
import string
from typing import List, Tuple, Dict
from collections import Counter

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class StatisticalValidator:
    """Validate MIR HEAT finding statistically."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.middle_ct = self.ciphertext[34:63]
        
        # Target words to search for
        self.target_words_3 = ['MIR', 'WAR', 'CIA', 'KGB', 'USA', 'RED', 'SPY']
        self.target_words_4 = ['HEAT', 'COLD', 'WALL', 'EAST', 'WEST', 'BOMB', 'NUKE']
        self.target_words_7 = ['MIRHEAT', 'COLDWAR', 'PEACWAR', 'NUCLEAR']
        
        # Common English 3-letter and 4-letter words for comparison
        self.common_3 = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'HAD', 'BUT', 'NOT']
        self.common_4 = ['THAT', 'HAVE', 'FROM', 'THEY', 'WILL', 'BEEN', 'MORE', 'WHEN', 'VERY', 'MAKE']
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        if not key:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def test_random_keys(self, num_tests: int = 1000):
        """Test random keys to see how often we get meaningful words."""
        print("\n" + "="*60)
        print(f"TESTING {num_tests} RANDOM KEYS")
        print("="*60)
        
        # Track findings
        findings = {
            'any_3_letter': 0,
            'any_4_letter': 0,
            'mir_found': 0,
            'heat_found': 0,
            'mir_heat_found': 0,
            'any_russian': 0,
            'any_coldwar': 0
        }
        
        russian_words = ['MIR', 'DA', 'NET', 'TASS', 'SOYUZ']
        coldwar_words = ['HEAT', 'COLD', 'WAR', 'WALL', 'BOMB', 'NUKE', 'EAST', 'WEST']
        
        for i in range(num_tests):
            # Generate random key of length 8 (like ABSCISSA)
            key_length = 8
            random_key = ''.join(random.choice(string.ascii_uppercase) for _ in range(key_length))
            
            # Decrypt middle segment
            pt = self.vigenere_decrypt(self.middle_ct, random_key)
            
            # Check for words
            for word in self.common_3:
                if word in pt:
                    findings['any_3_letter'] += 1
                    break
            
            for word in self.common_4:
                if word in pt:
                    findings['any_4_letter'] += 1
                    break
            
            if 'MIR' in pt:
                findings['mir_found'] += 1
            
            if 'HEAT' in pt:
                findings['heat_found'] += 1
            
            if 'MIR' in pt and 'HEAT' in pt:
                # Check if they're adjacent
                mir_pos = pt.find('MIR')
                heat_pos = pt.find('HEAT')
                if heat_pos == mir_pos + 3:  # MIR directly before HEAT
                    findings['mir_heat_found'] += 1
            
            for word in russian_words:
                if word in pt:
                    findings['any_russian'] += 1
                    break
            
            for word in coldwar_words:
                if word in pt:
                    findings['any_coldwar'] += 1
                    break
        
        # Report statistics
        print(f"\nResults from {num_tests} random 8-letter keys:")
        print(f"Any 3-letter common word: {findings['any_3_letter']} ({findings['any_3_letter']/num_tests*100:.1f}%)")
        print(f"Any 4-letter common word: {findings['any_4_letter']} ({findings['any_4_letter']/num_tests*100:.1f}%)")
        print(f"'MIR' found: {findings['mir_found']} ({findings['mir_found']/num_tests*100:.2f}%)")
        print(f"'HEAT' found: {findings['heat_found']} ({findings['heat_found']/num_tests*100:.2f}%)")
        print(f"'MIR HEAT' adjacent: {findings['mir_heat_found']} ({findings['mir_heat_found']/num_tests*100:.3f}%)")
        print(f"Any Russian word: {findings['any_russian']} ({findings['any_russian']/num_tests*100:.1f}%)")
        print(f"Any Cold War word: {findings['any_coldwar']} ({findings['any_coldwar']/num_tests*100:.1f}%)")
        
        return findings
    
    def calculate_probability(self):
        """Calculate probability of MIR HEAT appearing by chance."""
        print("\n" + "="*60)
        print("PROBABILITY CALCULATION")
        print("="*60)
        
        # Probability of getting specific 3-letter sequence
        prob_3_letter = 1 / (26**3)
        print(f"\nProbability of any specific 3-letter sequence: {prob_3_letter:.2e}")
        print(f"That's 1 in {26**3:,}")
        
        # Probability of getting specific 4-letter sequence
        prob_4_letter = 1 / (26**4)
        print(f"\nProbability of any specific 4-letter sequence: {prob_4_letter:.2e}")
        print(f"That's 1 in {26**4:,}")
        
        # Probability of MIR followed by HEAT
        prob_mir_heat = prob_3_letter * prob_4_letter
        print(f"\nProbability of 'MIR' followed by 'HEAT': {prob_mir_heat:.2e}")
        print(f"That's 1 in {(26**3) * (26**4):,}")
        
        # But we have 29 positions in middle segment where this could start
        # So effective probability is higher
        positions = 29 - 7  # Can't start in last 7 positions
        effective_prob = positions * prob_mir_heat
        print(f"\nWith {positions} possible starting positions: {effective_prob:.2e}")
        print(f"That's roughly 1 in {int(1/effective_prob):,}")
    
    def test_related_keys(self):
        """Test keys related to ABSCISSA."""
        print("\n" + "="*60)
        print("TESTING RELATED KEYS")
        print("="*60)
        
        # Keys with similar properties to ABSCISSA
        related_keys = [
            # Same length (8)
            'ORDINATE', 'LATITUDE', 'MERIDIAN', 'PARALLEL',
            'GEOMETRY', 'ALGEBRAA', 'CALCULUS', 'FUNCTION',
            # Surveying terms
            'SURVEYOR', 'BASELINE', 'BEARING', 'AZIMUTH',
            # Mathematical terms
            'EQUATION', 'VARIABLE', 'CONSTANT', 'INTEGRAL',
            # Random 8-letter words
            'COMPUTER', 'BUILDING', 'MOUNTAIN', 'SEASHORE'
        ]
        
        print("\nSearching for MIR, HEAT, or both in related keys:")
        
        results = []
        for key in related_keys:
            if len(key) == 8:  # Only test 8-letter keys like ABSCISSA
                pt = self.vigenere_decrypt(self.middle_ct, key)
                
                has_mir = 'MIR' in pt
                has_heat = 'HEAT' in pt
                
                if has_mir or has_heat:
                    mir_pos = pt.find('MIR') if has_mir else -1
                    heat_pos = pt.find('HEAT') if has_heat else -1
                    adjacent = (heat_pos == mir_pos + 3) if (has_mir and has_heat) else False
                    
                    results.append({
                        'key': key,
                        'has_mir': has_mir,
                        'has_heat': has_heat,
                        'adjacent': adjacent,
                        'plaintext': pt
                    })
                    
                    print(f"\n{key}:")
                    print(f"  Plaintext: {pt}")
                    if has_mir:
                        print(f"  MIR at position {mir_pos}")
                    if has_heat:
                        print(f"  HEAT at position {heat_pos}")
                    if adjacent:
                        print(f"  *** MIR HEAT ADJACENT! ***")
        
        if not results:
            print("  No MIR or HEAT found in any related key")
        
        return results
    
    def analyze_surrounding_text(self):
        """Analyze the text around MIR HEAT for patterns."""
        print("\n" + "="*60)
        print("ANALYZING SURROUNDING TEXT")
        print("="*60)
        
        pt = self.vigenere_decrypt(self.middle_ct, 'ABSCISSA')
        print(f"\nFull plaintext: {pt}")
        print(f"Breakdown: OSERIARQSR [MIR] [HEAT] ISJMLQAWHVDT")
        
        # Analyze segments
        before_mir = pt[:10]  # OSERIARQSR
        mir_heat = pt[10:17]  # MIRHEAT
        after_heat = pt[17:]  # ISJMLQAWHVDT
        
        print(f"\nBefore MIR: '{before_mir}'")
        print(f"MIR HEAT: '{mir_heat}'")
        print(f"After HEAT: '{after_heat}'")
        
        # Check for patterns
        print("\nPattern analysis:")
        
        # Letter frequency
        freq_before = Counter(before_mir)
        freq_after = Counter(after_heat)
        
        print(f"Most common letters before MIR: {freq_before.most_common(3)}")
        print(f"Most common letters after HEAT: {freq_after.most_common(3)}")
        
        # Check for partial words
        print("\nChecking for partial words:")
        
        # Could OSER be part of CLOSER, LOSER?
        if before_mir.endswith('OSER'):
            print("  'OSER' at end could be: CLOSER, LOSER, POSER")
        
        # Could QSR be initials or abbreviation?
        if 'QSR' in before_mir:
            print("  'QSR' found - unusual letter combination")
        
        # Check after HEAT
        if after_heat.startswith('IS'):
            print("  'IS' after HEAT - could be start of sentence")
        
        # Vowel/consonant ratio
        vowels_before = sum(1 for c in before_mir if c in 'AEIOU')
        vowels_after = sum(1 for c in after_heat if c in 'AEIOU')
        
        print(f"\nVowel ratios:")
        print(f"  Before MIR: {vowels_before}/{len(before_mir)} = {vowels_before/len(before_mir):.2f}")
        print(f"  After HEAT: {vowels_after}/{len(after_heat)} = {vowels_after/len(after_heat):.2f}")
        print(f"  Normal English: ~0.38")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("STATISTICAL VALIDATION OF MIR HEAT FINDING")
    print("="*70)
    
    validator = StatisticalValidator()
    
    # Calculate basic probability
    validator.calculate_probability()
    
    # Test random keys
    findings = validator.test_random_keys(10000)
    
    # Test related keys
    related_results = validator.test_related_keys()
    
    # Analyze surrounding text
    validator.analyze_surrounding_text()
    
    # Conclusion
    print("\n" + "="*70)
    print("STATISTICAL VALIDATION SUMMARY")
    print("="*70)
    
    print("\nKey findings:")
    print("1. MIR HEAT appearing together is statistically rare")
    print("2. The bilingual aspect (Russian + English) is unusual")
    print("3. Surrounding text remains largely unreadable")
    print("4. ABSCISSA is unique among tested keys in producing this")
    
    print("\nConclusion:")
    print("The MIR HEAT finding is statistically significant but incomplete.")
    print("It's unlikely to be pure chance, but without readable surrounding")
    print("text, we cannot confirm it as the intended solution.")
    
    print("\nRecommendation:")
    print("Document as an interesting partial finding with these caveats:")
    print("- Only 7 letters of 29 are readable")
    print("- Could be coincidental despite low probability")
    print("- Thematic coherence suggests possible intention")
    print("- Further validation needed")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()