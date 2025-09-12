#!/usr/bin/env python3
"""
f3_word_boundary_analysis.py

Testing if "HEAT" is actually a word boundary artifact (e.g., "HE AT").
Reanalyzing ABSCISSA result with different word segmentations.
"""

from typing import List, Tuple, Dict, Set
import itertools

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class WordBoundaryAnalyzer:
    """Analyze word boundaries in ABSCISSA decryption."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.middle_ct = self.ciphertext[34:63]
        
        # Original ABSCISSA result
        self.abscissa_pt = "OSERIARQSRMIRHEATISJMLQAWHVDT"
        
        # Common 2-letter words
        self.words_2 = {'AT', 'BE', 'BY', 'DO', 'GO', 'HE', 'IF', 'IN', 'IS', 'IT', 
                        'ME', 'MY', 'NO', 'OF', 'ON', 'OR', 'SO', 'TO', 'UP', 'WE'}
        
        # Common 3-letter words
        self.words_3 = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 
                        'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS',
                        'HAD', 'HOW', 'MAN', 'OLD', 'SEE', 'GET', 'MAY', 'WAY'}
        
        # Common 4-letter words
        self.words_4 = {'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM',
                        'THEY', 'BEEN', 'CALL', 'WORD', 'WHAT', 'WERE', 'WHEN',
                        'MAKE', 'LIKE', 'TIME', 'JUST', 'KNOW', 'TAKE', 'YEAR'}
        
        # Common word patterns
        self.common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO',
                               'EN', 'ES', 'OF', 'TE', 'EA', 'OU', 'IT', 'HA',
                               'ET', 'IS', 'AT', 'ON', 'AS', 'OR', 'AR', 'RE']
    
    def vigenere_decrypt(self, text: str, key: str, offset: int = 0) -> str:
        if not key:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            c_val = char_to_num(c)
            k_val = char_to_num(key[(i + offset) % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def analyze_heat_boundary(self):
        """Analyze if HEAT is actually multiple words."""
        print("\n" + "="*60)
        print("ANALYZING 'HEAT' AS WORD BOUNDARY")
        print("="*60)
        
        pt = self.abscissa_pt
        
        # Find HEAT position
        heat_start = pt.find('HEAT')
        print(f"\nOriginal: {pt}")
        print(f"HEAT at position {heat_start}: ...{pt[heat_start-3:heat_start+7]}...")
        
        # Test different segmentations
        print("\nPossible word boundaries:")
        
        # HE AT
        if heat_start >= 0:
            he_at = pt[heat_start:heat_start+2] + ' ' + pt[heat_start+2:heat_start+4]
            print(f"1. HE AT: ...{pt[heat_start-3:heat_start]}{he_at}{pt[heat_start+4:heat_start+7]}...")
            if 'HE' in self.words_2 and 'AT' in self.words_2:
                print("   ✓ Both are common 2-letter words!")
            
            # Check what comes before and after
            before_he = pt[heat_start-3:heat_start] if heat_start >= 3 else pt[:heat_start]
            after_at = pt[heat_start+4:heat_start+7] if heat_start+7 <= len(pt) else pt[heat_start+4:]
            print(f"   Before HE: '{before_he}'")
            print(f"   After AT: '{after_at}'")
            
            # Check if IS follows AT
            if after_at.startswith('IS'):
                print("   ✓ 'IS' follows 'AT' - 'HE AT IS'")
        
        # THE AT (requires shift)
        print("\n2. Testing if shift produces THE AT:")
        for offset in range(-2, 3):
            shifted = self.vigenere_decrypt(self.middle_ct, 'ABSCISSA', offset)
            if 'THEAT' in shifted:
                pos = shifted.find('THEAT')
                print(f"   Offset {offset}: THE AT found at position {pos}")
                print(f"   Context: ...{shifted[max(0,pos-5):min(len(shifted),pos+10)]}...")
    
    def test_offset_variations(self):
        """Test ABSCISSA with different offsets."""
        print("\n" + "="*60)
        print("TESTING ABSCISSA WITH OFFSETS")
        print("="*60)
        
        print("\nTesting offsets -3 to +3:")
        
        for offset in range(-3, 4):
            pt = self.vigenere_decrypt(self.middle_ct, 'ABSCISSA', offset)
            
            # Find all 2-letter words
            words_2_found = []
            for i in range(len(pt)-1):
                bigram = pt[i:i+2]
                if bigram in self.words_2:
                    words_2_found.append((i, bigram))
            
            # Find all 3-letter words
            words_3_found = []
            for i in range(len(pt)-2):
                trigram = pt[i:i+3]
                if trigram in self.words_3:
                    words_3_found.append((i, trigram))
            
            if words_2_found or words_3_found:
                print(f"\nOffset {offset}:")
                print(f"  Plaintext: {pt}")
                if words_2_found:
                    print(f"  2-letter words: {[w for _, w in words_2_found]}")
                if words_3_found:
                    print(f"  3-letter words: {[w for _, w in words_3_found]}")
                
                # Check for adjacent common words
                self.check_adjacent_words(pt, words_2_found, words_3_found)
    
    def segment_analysis(self):
        """Analyze all possible segmentations."""
        print("\n" + "="*60)
        print("COMPREHENSIVE SEGMENTATION ANALYSIS")
        print("="*60)
        
        pt = self.abscissa_pt
        
        # Analyze as pairs
        print("\nAs 2-letter segments:")
        pairs = [pt[i:i+2] for i in range(0, len(pt)-1, 2)]
        print(f"  {' '.join(pairs)}")
        
        common_pairs = [p for p in pairs if p in self.words_2]
        if common_pairs:
            print(f"  Common 2-letter words: {common_pairs}")
        
        # Analyze as triplets
        print("\nAs 3-letter segments:")
        triplets = [pt[i:i+3] for i in range(0, len(pt)-2, 3)]
        print(f"  {' '.join(triplets)}")
        
        common_triplets = [t for t in triplets if t in self.words_3]
        if common_triplets:
            print(f"  Common 3-letter words: {common_triplets}")
        
        # Find all valid word sequences
        print("\nSearching for word sequences:")
        self.find_word_sequences(pt)
    
    def find_word_sequences(self, text: str):
        """Find sequences of valid words in text."""
        sequences = []
        
        # Try to parse text as sequence of words
        def parse_from(start: int, words_so_far: List[str]) -> List[List[str]]:
            if start >= len(text):
                return [words_so_far] if words_so_far else []
            
            results = []
            
            # Try 2-letter word
            if start + 2 <= len(text):
                word = text[start:start+2]
                if word in self.words_2:
                    results.extend(parse_from(start+2, words_so_far + [word]))
            
            # Try 3-letter word
            if start + 3 <= len(text):
                word = text[start:start+3]
                if word in self.words_3:
                    results.extend(parse_from(start+3, words_so_far + [word]))
            
            # Try 4-letter word
            if start + 4 <= len(text):
                word = text[start:start+4]
                if word in self.words_4:
                    results.extend(parse_from(start+4, words_so_far + [word]))
            
            return results
        
        # Start from different positions
        for start in range(min(5, len(text))):
            seqs = parse_from(start, [])
            for seq in seqs:
                if len(seq) >= 3:  # At least 3 words
                    sequences.append((start, seq))
        
        if sequences:
            print("\nFound word sequences:")
            for start, seq in sequences[:5]:  # Show top 5
                print(f"  Starting at {start}: {' '.join(seq)}")
    
    def analyze_mir_context(self):
        """Analyze MIR in context of word boundaries."""
        print("\n" + "="*60)
        print("ANALYZING MIR WITH WORD BOUNDARIES")
        print("="*60)
        
        pt = self.abscissa_pt
        mir_pos = pt.find('MIR')
        
        print(f"\nMIR at position {mir_pos}")
        
        # What if MIR is split?
        print("\nTesting if MIR could be split:")
        
        # M IR? 
        print(f"1. M IR: Single letter M + IR")
        
        # MI R?
        print(f"2. MI R: MI (my in some languages) + R")
        
        # Or part of larger word?
        context = pt[max(0, mir_pos-5):min(len(pt), mir_pos+8)]
        print(f"\nContext around MIR: {context}")
        
        # Check common patterns around MIR
        before_mir = pt[max(0, mir_pos-3):mir_pos]
        after_mir = pt[mir_pos+3:min(len(pt), mir_pos+6)]
        
        print(f"Before MIR: '{before_mir}'")
        print(f"After MIR: '{after_mir}'")
        
        # Could MIRHE be something?
        if mir_pos + 5 <= len(pt):
            mirhe = pt[mir_pos:mir_pos+5]
            print(f"\nMIRHE as unit: '{mirhe}'")
        
        # Could RMIR be something?
        if mir_pos >= 1:
            rmir = pt[mir_pos-1:mir_pos+3]
            print(f"RMIR as unit: '{rmir}'")
    
    def test_different_keys_for_boundaries(self):
        """Test keys that might produce common word boundaries."""
        print("\n" + "="*60)
        print("TESTING KEYS FOR WORD BOUNDARIES")
        print("="*60)
        
        # Keys that might produce THE, AND, etc.
        test_keys = [
            'THEAND', 'ANDTHE', 'FORTHEAT', 'HEATFOR',
            'ISTHE', 'THEIS', 'ATTHE', 'THEAT',
            'COORDINATE', 'ORDINATE', 'LATITUDE'
        ]
        
        print("\nTesting keys for common word patterns:")
        
        for key in test_keys:
            pt = self.vigenere_decrypt(self.middle_ct, key)
            
            # Count common words
            words_found = []
            
            # Check 2-letter words
            for i in range(len(pt)-1):
                if pt[i:i+2] in self.words_2:
                    words_found.append(pt[i:i+2])
            
            # Check 3-letter words
            for i in range(len(pt)-2):
                if pt[i:i+3] in self.words_3:
                    words_found.append(pt[i:i+3])
            
            if len(words_found) >= 3:
                print(f"\n{key}:")
                print(f"  {pt}")
                print(f"  Words: {words_found[:10]}")  # Show first 10
    
    def check_adjacent_words(self, text: str, words_2: List[Tuple[int, str]], 
                            words_3: List[Tuple[int, str]]):
        """Check for adjacent common words."""
        # Check if any 2-letter words are adjacent
        for i in range(len(words_2)-1):
            pos1, word1 = words_2[i]
            pos2, word2 = words_2[i+1]
            if pos2 == pos1 + 2:
                print(f"    Adjacent 2-letter: {word1} {word2}")
        
        # Check if 3-letter word follows 2-letter word
        for pos2, word2 in words_2:
            for pos3, word3 in words_3:
                if pos3 == pos2 + 2:
                    print(f"    Adjacent 2+3: {word2} {word3}")
    
    def statistical_analysis(self):
        """Statistical analysis of word boundaries."""
        print("\n" + "="*60)
        print("STATISTICAL WORD BOUNDARY ANALYSIS")
        print("="*60)
        
        pt = self.abscissa_pt
        
        # Count bigrams
        bigram_counts = {}
        for i in range(len(pt)-1):
            bigram = pt[i:i+2]
            bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1
        
        print("\nMost common bigrams in plaintext:")
        sorted_bigrams = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)
        for bigram, count in sorted_bigrams[:10]:
            english_rank = self.common_bigrams.index(bigram) + 1 if bigram in self.common_bigrams else 'N/A'
            print(f"  {bigram}: {count} (English rank: {english_rank})")
        
        # Check trigram frequencies
        trigram_counts = {}
        for i in range(len(pt)-2):
            trigram = pt[i:i+3]
            trigram_counts[trigram] = trigram_counts.get(trigram, 0) + 1
        
        print("\nTrigrams that are common words:")
        for trigram, count in trigram_counts.items():
            if trigram in self.words_3:
                print(f"  {trigram}: {count} occurrences")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("WORD BOUNDARY ANALYSIS - HEAT AS ARTIFACT")
    print("Testing if HEAT is actually HE AT or similar")
    print("="*70)
    
    analyzer = WordBoundaryAnalyzer()
    
    # Run analyses
    analyzer.analyze_heat_boundary()
    analyzer.test_offset_variations()
    analyzer.segment_analysis()
    analyzer.analyze_mir_context()
    analyzer.test_different_keys_for_boundaries()
    analyzer.statistical_analysis()
    
    # Summary
    print("\n" + "="*70)
    print("WORD BOUNDARY ANALYSIS SUMMARY")
    print("="*70)
    
    print("\nKey findings:")
    print("1. HEAT could be 'HE AT' - both common 2-letter words")
    print("2. This gives us: '...MIR HE AT IS...'")
    print("3. MIR might also be split or part of larger pattern")
    print("4. Need to reconsider entire segmentation")
    
    print("\nImplications:")
    print("- We may be looking for multiple short words, not long ones")
    print("- Word boundaries might not align with our assumptions")
    print("- The 'gibberish' might be readable with correct segmentation")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()