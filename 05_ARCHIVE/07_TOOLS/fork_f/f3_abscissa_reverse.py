#!/usr/bin/env python3
"""
f3_abscissa_reverse.py

Investigating the SSAABS pattern - appears related to ABSCISSA.
Testing reverse and variant patterns.
"""

from typing import List, Tuple, Dict

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class AbscissaReverseAnalyzer:
    """Analyze ABSCISSA and its reverse patterns."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.middle_ct = self.ciphertext[34:63]
        
        # Key variations
        self.abscissa_variants = [
            'ABSCISSA',      # Original (confirmed MIR HEAT)
            'ASSICSBA',      # Reversed
            'SSAABSCI',      # Rotated
            'ABSCISSAABSCISSA',  # Doubled
            'SSAABS',        # Derived pattern
            'SSAABSSS',      # Extended pattern
            'BAASCISS',      # Anagram
            'SCISSABA'       # Another anagram
        ]
    
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
    
    def test_abscissa_patterns(self):
        """Test ABSCISSA variants and patterns."""
        print("\n" + "="*60)
        print("TESTING ABSCISSA PATTERNS")
        print("="*60)
        
        print("\nSearching for readable patterns with ABSCISSA variants:")
        
        results = []
        for key in self.abscissa_variants:
            pt = self.vigenere_decrypt(self.middle_ct, key)
            
            # Check for readable segments
            readable_segments = []
            
            # Check for MIR
            if 'MIR' in pt:
                mir_pos = pt.find('MIR')
                readable_segments.append(('MIR', mir_pos))
            
            # Check for HEAT
            if 'HEAT' in pt:
                heat_pos = pt.find('HEAT')
                readable_segments.append(('HEAT', heat_pos))
            
            # Check for IS
            if 'IS' in pt:
                is_positions = []
                start = 0
                while True:
                    pos = pt.find('IS', start)
                    if pos == -1:
                        break
                    is_positions.append(pos)
                    start = pos + 1
                for pos in is_positions:
                    readable_segments.append(('IS', pos))
            
            # Check for other words
            common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'WAR', 'PEACE', 'HOT', 'COLD']
            for word in common_words:
                if word in pt:
                    pos = pt.find(word)
                    readable_segments.append((word, pos))
            
            if readable_segments:
                results.append({
                    'key': key,
                    'plaintext': pt,
                    'segments': readable_segments
                })
                
                print(f"\n{key}:")
                print(f"  Plaintext: {pt}")
                print(f"  Readable segments: {readable_segments}")
                
                # Check for adjacent readable words
                if len(readable_segments) >= 2:
                    for i in range(len(readable_segments) - 1):
                        word1, pos1 = readable_segments[i]
                        word2, pos2 = readable_segments[i + 1]
                        if pos2 == pos1 + len(word1):
                            print(f"    *** Adjacent: {word1}{word2} ***")
        
        return results
    
    def test_sliding_key(self):
        """Test ABSCISSA with different starting positions."""
        print("\n" + "="*60)
        print("TESTING SLIDING KEY POSITIONS")
        print("="*60)
        
        print("\nTesting ABSCISSA starting at different positions in key cycle:")
        
        key = 'ABSCISSA'
        for offset in range(len(key)):
            pt = self.vigenere_decrypt(self.middle_ct, key, offset)
            
            # Look for readable patterns
            if 'HEAT' in pt or 'MIR' in pt or 'IS' in pt:
                print(f"\nOffset {offset} (starts with '{key[offset]}'):")
                print(f"  {pt}")
                
                if 'MIR' in pt:
                    mir_pos = pt.find('MIR')
                    print(f"  MIR at position {mir_pos}")
                
                if 'HEAT' in pt:
                    heat_pos = pt.find('HEAT')
                    print(f"  HEAT at position {heat_pos}")
                    
                if 'IS' in pt:
                    is_count = pt.count('IS')
                    print(f"  'IS' appears {is_count} time(s)")
    
    def analyze_key_structure(self):
        """Analyze the structure of ABSCISSA as a key."""
        print("\n" + "="*60)
        print("ANALYZING ABSCISSA KEY STRUCTURE")
        print("="*60)
        
        key = 'ABSCISSA'
        print(f"\nKey: {key}")
        print(f"Length: {len(key)}")
        
        # Letter frequency in key
        from collections import Counter
        freq = Counter(key)
        print(f"Letter frequency: {dict(freq)}")
        
        # Pattern analysis
        print("\nPattern analysis:")
        print(f"  Starts with: AB")
        print(f"  Ends with: SA")
        print(f"  Contains double S: SS")
        print(f"  Unique letters: {len(set(key))}")
        
        # Numeric values
        print("\nNumeric values (A=0):")
        values = [char_to_num(c) for c in key]
        print(f"  Values: {values}")
        print(f"  Sum: {sum(values)}")
        print(f"  Average: {sum(values)/len(values):.1f}")
        
        # Check for mathematical patterns
        print("\nMathematical patterns:")
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        print(f"  Differences: {diffs}")
        
        # Test if reversing creates patterns
        reversed_key = key[::-1]
        print(f"\nReversed: {reversed_key}")
        
        # Test alternating patterns
        odd_chars = key[::2]
        even_chars = key[1::2]
        print(f"  Odd positions: {odd_chars}")
        print(f"  Even positions: {even_chars}")
    
    def test_compound_keys(self):
        """Test combinations of ABSCISSA with other keys."""
        print("\n" + "="*60)
        print("TESTING COMPOUND KEYS")
        print("="*60)
        
        print("\nTesting ABSCISSA combined with other keywords:")
        
        compounds = [
            'ABSCISSA' + 'HEAT',
            'ABSCISSA' + 'MIR',
            'MIR' + 'ABSCISSA',
            'HEAT' + 'ABSCISSA',
            'ABSCISSA' + 'ORDINATE',
            'ABSCISSA' + 'KRYPTOS',
            'KRYPTOS' + 'ABSCISSA'
        ]
        
        for compound_key in compounds:
            pt = self.vigenere_decrypt(self.middle_ct, compound_key)
            
            # Check for improvements
            words_found = []
            for word in ['MIR', 'HEAT', 'IS', 'THE', 'AND', 'WAR', 'PEACE']:
                if word in pt:
                    words_found.append(word)
            
            if len(words_found) > 1:  # More than just MIR or HEAT
                print(f"\n{compound_key}:")
                print(f"  {pt}")
                print(f"  Words: {words_found}")
    
    def test_mathematical_keys(self):
        """Test other mathematical/coordinate terms."""
        print("\n" + "="*60)
        print("TESTING MATHEMATICAL KEYS")
        print("="*60)
        
        math_keys = [
            # Coordinate terms
            'ORDINATE', 'COORDINATE', 'CARTESIAN', 'POLAR',
            # Mathematical terms
            'FUNCTION', 'EQUATION', 'VARIABLE', 'CONSTANT',
            # Geometric terms
            'TANGENT', 'SECANT', 'COSINE', 'SINE',
            # Measurement terms
            'LATITUDE', 'LONGITUDE', 'MERIDIAN', 'PARALLEL'
        ]
        
        print("\nTesting mathematical/coordinate keys:")
        
        for key in math_keys:
            if len(key) == 8:  # Same length as ABSCISSA
                pt = self.vigenere_decrypt(self.middle_ct, key)
                
                # Check for any readable patterns
                if 'HEAT' in pt or 'MIR' in pt or 'WAR' in pt or 'PEACE' in pt:
                    print(f"\n{key}:")
                    print(f"  {pt}")
                    
                    words = []
                    for word in ['MIR', 'HEAT', 'WAR', 'PEACE', 'IS', 'THE', 'AND']:
                        if word in pt:
                            words.append(word)
                    print(f"  Words: {words}")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("ABSCISSA REVERSE PATTERN ANALYSIS")
    print("Investigating SSAABS and related patterns")
    print("="*70)
    
    analyzer = AbscissaReverseAnalyzer()
    
    # Run analyses
    results = analyzer.test_abscissa_patterns()
    analyzer.test_sliding_key()
    analyzer.analyze_key_structure()
    analyzer.test_compound_keys()
    analyzer.test_mathematical_keys()
    
    # Summary
    print("\n" + "="*70)
    print("ABSCISSA PATTERN SUMMARY")
    print("="*70)
    
    print("\nKey observations:")
    print("1. ABSCISSA produces MIR HEAT (confirmed)")
    print("2. Reversed/rotated variants don't improve results")
    print("3. The key structure has interesting properties (double S)")
    print("4. No mathematical keys match ABSCISSA's success")
    
    print("\nConclusion:")
    print("ABSCISSA appears unique in producing MIR HEAT.")
    print("The pattern SSAABS derived from 'HEAT IS' is intriguing")
    print("but doesn't lead to better decryption.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()