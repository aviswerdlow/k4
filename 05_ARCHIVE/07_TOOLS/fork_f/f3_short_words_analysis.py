#!/usr/bin/env python3
"""
f3_short_words_analysis.py

Building on the discovery that HEAT might be "HE AT".
Focusing on finding sequences of short (2-4 letter) English words.
"""

from typing import List, Tuple, Dict, Set, Optional

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class ShortWordsAnalyzer:
    """Analyze K4 looking for sequences of short words."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.middle_ct = self.ciphertext[34:63]
        
        # ABSCISSA result
        self.abscissa_pt = "OSERIARQSRMIRHEATISJMLQAWHVDT"
        
        # Comprehensive short word lists
        self.words_1 = {'A', 'I'}
        
        self.words_2 = {'AT', 'BE', 'BY', 'DO', 'GO', 'HE', 'IF', 'IN', 'IS', 'IT',
                        'ME', 'MY', 'NO', 'OF', 'ON', 'OR', 'SO', 'TO', 'UP', 'WE',
                        'AM', 'AN', 'AS', 'US', 'OH', 'OK', 'HI', 'LO'}
        
        self.words_3 = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                        'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS',
                        'HAD', 'HOW', 'MAN', 'OLD', 'SEE', 'GET', 'MAY', 'WAY',
                        'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE',
                        'TOO', 'USE', 'HIM', 'FEW', 'BIG', 'GOD', 'WHY', 'RUN',
                        'HOT', 'EAT', 'FAR', 'FUN', 'BAD', 'BAG', 'YET', 'ARM',
                        'SEA', 'TOP', 'BUY', 'LAW', 'SON', 'CAR', 'EYE', 'CUP',
                        'JOB', 'LOT', 'BED', 'HIT', 'EAR', 'END', 'SIX', 'TEN',
                        'WAR', 'MIR', 'SPY', 'CIA', 'KGB', 'USA', 'RED'}
        
        self.words_4 = {'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM',
                        'THEY', 'BEEN', 'CALL', 'WORD', 'WHAT', 'WERE', 'WHEN',
                        'MAKE', 'LIKE', 'TIME', 'JUST', 'KNOW', 'TAKE', 'YEAR',
                        'WORK', 'BACK', 'GOOD', 'ONLY', 'VERY', 'OVER', 'ALSO',
                        'COME', 'GIVE', 'MOST', 'EVEN', 'FIND', 'MANY', 'SUCH',
                        'LONG', 'DOWN', 'SEND', 'SAFE', 'HEAT', 'COLD', 'WALL',
                        'EAST', 'WEST', 'IRON', 'ATOM', 'BOMB', 'NUKE', 'DEAD'}
    
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
    
    def parse_as_short_words(self, text: str, max_depth: int = 10) -> List[List[str]]:
        """Parse text as sequence of short words using dynamic programming."""
        n = len(text)
        
        # Dynamic programming approach
        # dp[i] = list of possible word sequences ending at position i
        dp = [[] for _ in range(n + 1)]
        dp[0] = [[]]  # Empty sequence at start
        
        for i in range(1, n + 1):
            # Try all possible word lengths ending at position i
            for word_len in [1, 2, 3, 4]:
                if i >= word_len:
                    word = text[i-word_len:i]
                    
                    # Check if it's a valid word
                    is_valid = False
                    if word_len == 1 and word in self.words_1:
                        is_valid = True
                    elif word_len == 2 and word in self.words_2:
                        is_valid = True
                    elif word_len == 3 and word in self.words_3:
                        is_valid = True
                    elif word_len == 4 and word in self.words_4:
                        is_valid = True
                    
                    if is_valid:
                        # Add this word to all sequences ending at i-word_len
                        for seq in dp[i-word_len]:
                            if len(seq) < max_depth:  # Limit depth
                                new_seq = seq + [word]
                                if new_seq not in dp[i]:
                                    dp[i].append(new_seq)
        
        # Return all complete sequences
        complete_sequences = []
        for i in range(max(0, n-3), n+1):  # Allow up to 3 chars unmatched at end
            complete_sequences.extend(dp[i])
        
        return complete_sequences
    
    def analyze_abscissa_segmentation(self):
        """Analyze ABSCISSA result with focus on short words."""
        print("\n" + "="*60)
        print("ANALYZING ABSCISSA AS SHORT WORDS")
        print("="*60)
        
        pt = self.abscissa_pt
        print(f"\nOriginal: {pt}")
        
        # Known segmentation
        print("\nKnown segmentation: ...MIR HE AT IS...")
        print("Position 10-19: MIRHEATIS")
        
        # Try to extend from HE AT IS
        segment = "HEATIS"
        after_segment = pt[16:]  # After "HE AT IS"
        before_segment = pt[:10]  # Before "MIR"
        
        print(f"\nBefore MIR: '{before_segment}'")
        print(f"After IS: '{after_segment}'")
        
        # Parse before segment
        print("\nParsing before MIR as short words:")
        before_parses = self.parse_as_short_words(before_segment)
        for parse in before_parses[:5]:
            if parse:
                print(f"  {' '.join(parse)}")
        
        # Parse after segment
        print("\nParsing after IS as short words:")
        after_parses = self.parse_as_short_words(after_segment)
        for parse in after_parses[:5]:
            if parse:
                print(f"  {' '.join(parse)}")
        
        # Try full sequence parsing
        print("\nFull sequence parsing:")
        full_parses = self.parse_as_short_words(pt)
        
        # Filter for sequences containing HE AT IS
        he_at_is_parses = []
        for parse in full_parses:
            if 'HE' in parse and 'AT' in parse and 'IS' in parse:
                he_idx = parse.index('HE') if 'HE' in parse else -1
                at_idx = parse.index('AT') if 'AT' in parse else -1
                is_idx = parse.index('IS') if 'IS' in parse else -1
                
                if he_idx >= 0 and at_idx == he_idx + 1 and is_idx == at_idx + 1:
                    he_at_is_parses.append(parse)
        
        if he_at_is_parses:
            print("\nSequences containing 'HE AT IS':")
            for parse in he_at_is_parses[:5]:
                print(f"  {' '.join(parse)}")
    
    def test_key_adjustments(self):
        """Test slight adjustments to ABSCISSA key."""
        print("\n" + "="*60)
        print("TESTING KEY ADJUSTMENTS")
        print("="*60)
        
        base_key = 'ABSCISSA'
        
        # Test variations
        variations = [
            base_key,
            base_key[1:] + base_key[0],  # Rotate left
            base_key[-1] + base_key[:-1],  # Rotate right
            base_key[::-1],  # Reverse
            'ABSCISA',  # Single S
            'ABSCISSAE',  # Latin plural
            'ABSCISSAS',  # English plural
            'ABSCISS',  # Truncated
            'XABSCISSA',  # X prefix (x-coordinate)
            'ABSCISSAX'  # X suffix
        ]
        
        print("\nTesting ABSCISSA variations for short word sequences:")
        
        for key in variations:
            pt = self.vigenere_decrypt(self.middle_ct, key)
            
            # Find short words
            words_found = []
            
            # Check all positions for 2-3 letter words
            for i in range(len(pt)-1):
                if pt[i:i+2] in self.words_2:
                    words_found.append((i, pt[i:i+2]))
                if i < len(pt)-2 and pt[i:i+3] in self.words_3:
                    words_found.append((i, pt[i:i+3]))
            
            if len(words_found) >= 4:  # At least 4 short words
                print(f"\n{key}:")
                print(f"  {pt}")
                
                # Check for sequences
                words_found.sort(key=lambda x: x[0])
                sequences = self.find_consecutive_words(words_found)
                if sequences:
                    print(f"  Sequences: {sequences}")
    
    def find_consecutive_words(self, words: List[Tuple[int, str]]) -> List[str]:
        """Find consecutive word sequences."""
        sequences = []
        
        i = 0
        while i < len(words):
            seq = [words[i][1]]
            pos = words[i][0] + len(words[i][1])
            
            j = i + 1
            while j < len(words):
                if words[j][0] == pos:
                    seq.append(words[j][1])
                    pos = words[j][0] + len(words[j][1])
                    j += 1
                else:
                    break
            
            if len(seq) >= 2:
                sequences.append(' '.join(seq))
            
            i = j if j > i + 1 else i + 1
        
        return sequences
    
    def analyze_qsr_pattern(self):
        """Analyze the QSR pattern before MIR."""
        print("\n" + "="*60)
        print("ANALYZING QSR PATTERN")
        print("="*60)
        
        pt = self.abscissa_pt
        qsr_context = pt[7:13]  # RQSRMI
        
        print(f"\nQSR context: {qsr_context}")
        print("Q without U is unusual in English")
        
        # Could QSR be:
        # 1. Initials/abbreviation
        # 2. Foreign word
        # 3. Cipher boundary marker
        # 4. Part of different segmentation
        
        print("\nTesting if different segmentation avoids Q without U:")
        
        # Try parsing around Q differently
        segment = pt[6:14]  # ARQSRMIR
        print(f"Wider segment: {segment}")
        
        # Look for alternative parsings
        alternatives = [
            "AR QSR MIR",  # QSR as unit (abbreviation?)
            "ARQ SR MIR",  # ARQ as unit
            "AR Q SR MIR",  # Q alone
        ]
        
        for alt in alternatives:
            print(f"  {alt}")
    
    def test_progressive_keys(self):
        """Test keys that progress through the alphabet."""
        print("\n" + "="*60)
        print("TESTING PROGRESSIVE KEYS")
        print("="*60)
        
        # Since ABSCISSA works partially, test related progressions
        progressive_keys = [
            'ABCDEFGH',  # Simple progression
            'ABCDABCD',  # Repeating pattern
            'AAAABBBB',  # Grouped pattern
            'ABABABAB',  # Alternating
            'ACEGIKMO',  # Skip pattern
            'ABSCABSC',  # ABSC repeated (from ABSCISSA)
            'ISSAISSA',  # ISSA repeated (from ABSCISSA)
            'HEATISAT',  # Based on HE AT IS AT pattern
        ]
        
        print("\nTesting progressive keys:")
        
        for key in progressive_keys:
            pt = self.vigenere_decrypt(self.middle_ct, key)
            
            # Parse as short words
            parses = self.parse_as_short_words(pt, max_depth=8)
            
            if parses:
                # Find best parse (most coverage)
                best_parse = max(parses, key=lambda p: sum(len(w) for w in p))
                coverage = sum(len(w) for w in best_parse) / len(pt)
                
                if coverage > 0.5:  # At least 50% coverage
                    print(f"\n{key}:")
                    print(f"  {pt}")
                    print(f"  Best parse: {' '.join(best_parse)}")
                    print(f"  Coverage: {coverage:.1%}")
    
    def statistical_short_word_analysis(self):
        """Statistical analysis of short word patterns."""
        print("\n" + "="*60)
        print("STATISTICAL SHORT WORD ANALYSIS")
        print("="*60)
        
        pt = self.abscissa_pt
        
        # Count all possible short words
        word_positions = {}
        
        for length in [2, 3, 4]:
            for i in range(len(pt) - length + 1):
                segment = pt[i:i+length]
                
                is_word = False
                if length == 2 and segment in self.words_2:
                    is_word = True
                elif length == 3 and segment in self.words_3:
                    is_word = True
                elif length == 4 and segment in self.words_4:
                    is_word = True
                
                if is_word:
                    if segment not in word_positions:
                        word_positions[segment] = []
                    word_positions[segment].append(i)
        
        print("\nShort words found in ABSCISSA plaintext:")
        for word, positions in sorted(word_positions.items()):
            print(f"  {word}: positions {positions}")
        
        # Calculate coverage
        covered = set()
        for word, positions in word_positions.items():
            for pos in positions:
                for i in range(pos, pos + len(word)):
                    covered.add(i)
        
        coverage = len(covered) / len(pt)
        print(f"\nTotal coverage by short words: {coverage:.1%}")
        print(f"Positions covered: {sorted(covered)}")
        
        # Find gaps
        uncovered = set(range(len(pt))) - covered
        print(f"Uncovered positions: {sorted(uncovered)}")
        
        if uncovered:
            print("\nUncovered segments:")
            for pos in sorted(uncovered):
                context = pt[max(0, pos-2):min(len(pt), pos+3)]
                print(f"  Position {pos}: ...{context}... ('{pt[pos]}')")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("SHORT WORDS ANALYSIS")
    print("Building on HE AT IS discovery")
    print("="*70)
    
    analyzer = ShortWordsAnalyzer()
    
    # Run analyses
    analyzer.analyze_abscissa_segmentation()
    analyzer.test_key_adjustments()
    analyzer.analyze_qsr_pattern()
    analyzer.test_progressive_keys()
    analyzer.statistical_short_word_analysis()
    
    # Summary
    print("\n" + "="*70)
    print("SHORT WORDS ANALYSIS SUMMARY")
    print("="*70)
    
    print("\nKey findings:")
    print("1. CONFIRMED: 'HE AT IS' is sequence of valid 2-letter words")
    print("2. MIR could be a 3-letter word OR part of different segmentation")
    print("3. QSR pattern remains problematic (Q without U)")
    print("4. Multiple valid short words overlap in the plaintext")
    
    print("\nImplications:")
    print("- Focus should shift to finding short word sequences")
    print("- Word boundaries may not align with our expectations")
    print("- The solution might be simpler than expected")
    print("- Need to test keys that produce common 2-3 letter words")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()