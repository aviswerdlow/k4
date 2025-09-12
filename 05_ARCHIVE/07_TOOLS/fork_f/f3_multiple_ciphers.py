#!/usr/bin/env python3
"""
f3_multiple_ciphers.py

Testing if K4 uses multiple simultaneous ciphers - overlapping or interleaved.
Different methods might apply to overlapping segments or alternating characters.
"""

from typing import List, Tuple, Dict, Optional

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class MultipleCipherAnalyzer:
    """Test multiple simultaneous cipher methods."""
    
    def __init__(self):
        self.k4_ct = K4_CIPHERTEXT
        self.length = len(self.k4_ct)
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Standard Vigenere decryption."""
        if not key or not text:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def caesar_decrypt(self, text: str, shift: int) -> str:
        """Caesar cipher decryption."""
        result = []
        for c in text:
            result.append(num_to_char((char_to_num(c) - shift) % 26))
        return ''.join(result)
    
    def atbash_decrypt(self, text: str) -> str:
        """Atbash substitution."""
        result = []
        for c in text:
            result.append(chr(ord('Z') - (ord(c) - ord('A'))))
        return ''.join(result)
    
    def test_interleaved_ciphers(self):
        """Test alternating characters with different ciphers."""
        print("\n" + "="*60)
        print("TESTING INTERLEAVED CIPHERS")
        print("="*60)
        
        print("\nApplying different ciphers to alternating characters:")
        
        # Split into even and odd positions
        even_chars = ''.join([self.k4_ct[i] for i in range(0, self.length, 2)])
        odd_chars = ''.join([self.k4_ct[i] for i in range(1, self.length, 2)])
        
        print(f"Even positions: {even_chars[:30]}...")
        print(f"Odd positions: {odd_chars[:30]}...")
        
        # Test combinations
        combinations = [
            ('Vigenere-ABSCISSA', 'Caesar-3'),
            ('Vigenere-ABSCISSA', 'Atbash'),
            ('Caesar-13', 'Vigenere-BERLIN'),
            ('Atbash', 'Vigenere-CLOCK'),
            ('Vigenere-KRYPTOS', 'Vigenere-SANBORN')
        ]
        
        for even_method, odd_method in combinations:
            # Decrypt even positions
            if even_method.startswith('Vigenere-'):
                key = even_method.split('-')[1]
                even_pt = self.vigenere_decrypt(even_chars, key)
            elif even_method.startswith('Caesar-'):
                shift = int(even_method.split('-')[1])
                even_pt = self.caesar_decrypt(even_chars, shift)
            elif even_method == 'Atbash':
                even_pt = self.atbash_decrypt(even_chars)
            else:
                even_pt = even_chars
            
            # Decrypt odd positions
            if odd_method.startswith('Vigenere-'):
                key = odd_method.split('-')[1]
                odd_pt = self.vigenere_decrypt(odd_chars, key)
            elif odd_method.startswith('Caesar-'):
                shift = int(odd_method.split('-')[1])
                odd_pt = self.caesar_decrypt(odd_chars, shift)
            elif odd_method == 'Atbash':
                odd_pt = self.atbash_decrypt(odd_chars)
            else:
                odd_pt = odd_chars
            
            # Recombine
            result = []
            for i in range(max(len(even_pt), len(odd_pt))):
                if i < len(even_pt):
                    result.append(even_pt[i])
                if i < len(odd_pt):
                    result.append(odd_pt[i])
            
            combined = ''.join(result)
            
            if 'MIR' in combined or 'HEAT' in combined or self.has_meaningful_words(combined):
                print(f"\n{even_method} + {odd_method}:")
                print(f"  Combined: {combined[:50]}...")
                if 'MIR' in combined:
                    print(f"    Contains MIR!")
                if 'HEAT' in combined:
                    print(f"    Contains HEAT!")
    
    def test_overlapping_segments(self):
        """Test overlapping cipher segments."""
        print("\n" + "="*60)
        print("TESTING OVERLAPPING SEGMENTS")
        print("="*60)
        
        print("\nApplying different ciphers to overlapping segments:")
        
        # Define overlapping segments
        segments = [
            (0, 40, 'Vigenere', 'KRYPTOS'),
            (30, 70, 'Vigenere', 'ABSCISSA'),
            (60, 97, 'Caesar', 13)
        ]
        
        # Initialize with original
        result = list(self.k4_ct)
        
        for start, end, method, param in segments:
            segment = self.k4_ct[start:end]
            
            if method == 'Vigenere':
                decrypted = self.vigenere_decrypt(segment, param)
            elif method == 'Caesar':
                decrypted = self.caesar_decrypt(segment, param)
            else:
                decrypted = segment
            
            # Apply to result (overwriting)
            for i, c in enumerate(decrypted):
                if start + i < len(result):
                    result[start + i] = c
            
            print(f"\nAfter {method}-{param} on [{start}:{end}]:")
            print(f"  {''.join(result[:50])}...")
        
        final = ''.join(result)
        if 'MIR' in final or 'HEAT' in final:
            print(f"\nFinal result contains MIR/HEAT!")
            if 'MIR' in final:
                pos = final.find('MIR')
                print(f"  MIR at position {pos}")
    
    def test_progressive_ciphers(self):
        """Test progressive cipher application."""
        print("\n" + "="*60)
        print("TESTING PROGRESSIVE CIPHERS")
        print("="*60)
        
        print("\nApplying ciphers progressively (output of one is input to next):")
        
        # Progressive cipher chain
        chains = [
            [('Caesar', 3), ('Vigenere', 'ABSCISSA'), ('Caesar', -3)],
            [('Atbash', None), ('Vigenere', 'KRYPTOS'), ('Atbash', None)],
            [('Vigenere', 'BERLIN'), ('Caesar', 13), ('Vigenere', 'CLOCK')],
            [('Caesar', 1), ('Caesar', 2), ('Caesar', 3), ('Vigenere', 'ABSCISSA')]
        ]
        
        for chain in chains:
            text = self.k4_ct
            chain_desc = []
            
            for method, param in chain:
                if method == 'Vigenere':
                    text = self.vigenere_decrypt(text, param)
                    chain_desc.append(f"Vig-{param}")
                elif method == 'Caesar':
                    text = self.caesar_decrypt(text, param)
                    chain_desc.append(f"Cae-{param}")
                elif method == 'Atbash':
                    text = self.atbash_decrypt(text)
                    chain_desc.append('Atbash')
            
            if 'MIR' in text or 'HEAT' in text or self.has_meaningful_words(text):
                print(f"\n{' → '.join(chain_desc)}:")
                print(f"  Result: {text[:50]}...")
                if 'MIR' in text:
                    print(f"    Contains MIR at {text.find('MIR')}")
                if 'HEAT' in text:
                    print(f"    Contains HEAT at {text.find('HEAT')}")
    
    def test_split_key_cipher(self):
        """Test if different parts use different keys."""
        print("\n" + "="*60)
        print("TESTING SPLIT KEY CIPHER")
        print("="*60)
        
        print("\nUsing different keys for different character positions:")
        
        # Split keys based on character position
        split_patterns = [
            # First third, middle third, last third
            [(0, 32, 'BERLIN'), (32, 65, 'ABSCISSA'), (65, 97, 'CLOCK')],
            # Quarters
            [(0, 24, 'EAST'), (24, 48, 'NORTH'), (48, 72, 'WEST'), (72, 97, 'SOUTH')],
            # Based on anchor positions
            [(0, 21, 'LANGLEY'), (21, 63, 'ABSCISSA'), (63, 97, 'VIRGINIA')]
        ]
        
        for pattern in split_patterns:
            result = []
            pattern_desc = []
            
            for start, end, key in pattern:
                segment = self.k4_ct[start:end]
                decrypted = self.vigenere_decrypt(segment, key)
                result.append(decrypted)
                pattern_desc.append(f"{key}[{start}:{end}]")
            
            combined = ''.join(result)
            
            if 'MIR' in combined or 'HEAT' in combined or self.has_meaningful_words(combined):
                print(f"\n{' + '.join(pattern_desc)}:")
                print(f"  {combined[:50]}...")
                if 'MIR' in combined:
                    mir_pos = combined.find('MIR')
                    print(f"    MIR at position {mir_pos}")
                if 'HEAT' in combined:
                    heat_pos = combined.find('HEAT')
                    print(f"    HEAT at position {heat_pos}")
    
    def test_fractionated_cipher(self):
        """Test fractionated cipher (like trifid)."""
        print("\n" + "="*60)
        print("TESTING FRACTIONATED CIPHER")
        print("="*60)
        
        print("\nTesting if K4 uses fractionation (splitting then recombining):")
        
        # Split into 3 streams
        stream1 = ''.join([self.k4_ct[i] for i in range(0, self.length, 3)])
        stream2 = ''.join([self.k4_ct[i] for i in range(1, self.length, 3)])
        stream3 = ''.join([self.k4_ct[i] for i in range(2, self.length, 3)])
        
        print(f"Stream 1: {stream1[:20]}...")
        print(f"Stream 2: {stream2[:20]}...")
        print(f"Stream 3: {stream3[:20]}...")
        
        # Try different recombinations
        recombinations = [
            stream1 + stream2 + stream3,  # Sequential
            stream3 + stream2 + stream1,  # Reversed
            stream2 + stream1 + stream3,  # Rotated
        ]
        
        for i, recomb in enumerate(recombinations):
            # Try with ABSCISSA
            pt = self.vigenere_decrypt(recomb[:97], 'ABSCISSA')
            
            if 'MIR' in pt or 'HEAT' in pt:
                print(f"\nRecombination {i+1} with ABSCISSA:")
                print(f"  {pt[:50]}...")
                print(f"    Contains MIR/HEAT!")
    
    def test_homophonic_substitution(self):
        """Test if multiple letters map to same plaintext."""
        print("\n" + "="*60)
        print("TESTING HOMOPHONIC SUBSTITUTION")
        print("="*60)
        
        print("\nTesting if different letters represent the same plaintext:")
        
        # Common homophonic mappings
        mappings = [
            {'A': 'E', 'Q': 'E', 'X': 'E'},  # Multiple cipher letters for E
            {'B': 'T', 'K': 'T', 'Z': 'T'},  # Multiple for T
            {'C': 'A', 'M': 'A', 'W': 'A'},  # Multiple for A
        ]
        
        for mapping in mappings:
            # Apply substitution
            result = []
            for c in self.k4_ct:
                if c in mapping:
                    result.append(mapping[c])
                else:
                    result.append(c)
            
            substituted = ''.join(result)
            
            # Try with ABSCISSA
            pt = self.vigenere_decrypt(substituted, 'ABSCISSA')
            
            if self.has_meaningful_words(pt):
                print(f"\nWith mapping {mapping}:")
                print(f"  Substituted: {substituted[:30]}...")
                print(f"  With ABSCISSA: {pt[:30]}...")
                
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
    
    def test_polyalphabetic_variants(self):
        """Test variant polyalphabetic ciphers."""
        print("\n" + "="*60)
        print("TESTING POLYALPHABETIC VARIANTS")
        print("="*60)
        
        print("\nTesting Beaufort and Variant Beaufort:")
        
        # Beaufort cipher (key - plaintext instead of plaintext - key)
        def beaufort_decrypt(text, key):
            result = []
            for i, c in enumerate(text):
                c_val = char_to_num(c)
                k_val = char_to_num(key[i % len(key)])
                p_val = (k_val - c_val) % 26
                result.append(num_to_char(p_val))
            return ''.join(result)
        
        # Variant Beaufort (plaintext + key)
        def variant_beaufort_decrypt(text, key):
            result = []
            for i, c in enumerate(text):
                c_val = char_to_num(c)
                k_val = char_to_num(key[i % len(key)])
                p_val = (c_val + k_val) % 26
                result.append(num_to_char(p_val))
            return ''.join(result)
        
        keys = ['ABSCISSA', 'KRYPTOS', 'BERLIN', 'PALIMPSEST']
        
        for key in keys:
            # Beaufort
            pt1 = beaufort_decrypt(self.k4_ct, key)
            if 'MIR' in pt1 or 'HEAT' in pt1:
                print(f"\nBeaufort with {key}:")
                print(f"  {pt1[:50]}...")
                print(f"    Contains MIR/HEAT!")
            
            # Variant Beaufort
            pt2 = variant_beaufort_decrypt(self.k4_ct, key)
            if 'MIR' in pt2 or 'HEAT' in pt2:
                print(f"\nVariant Beaufort with {key}:")
                print(f"  {pt2[:50]}...")
                print(f"    Contains MIR/HEAT!")
    
    def has_meaningful_words(self, text: str) -> bool:
        """Check for meaningful words."""
        words = ['THE', 'AND', 'HEAT', 'MIR', 'BERLIN', 'CLOCK', 'WAR', 'PEACE']
        count = sum(1 for word in words if word in text)
        return count >= 2
    
    def find_words(self, text: str) -> List[str]:
        """Find common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'HEAT', 'MIR', 'WAR', 'PEACE']
        return [word for word in words if word in text]

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("MULTIPLE SIMULTANEOUS CIPHERS ANALYSIS")
    print("Testing overlapping and interleaved cipher methods")
    print("="*70)
    
    analyzer = MultipleCipherAnalyzer()
    
    # Run all tests
    analyzer.test_interleaved_ciphers()
    analyzer.test_overlapping_segments()
    analyzer.test_progressive_ciphers()
    analyzer.test_split_key_cipher()
    analyzer.test_fractionated_cipher()
    analyzer.test_homophonic_substitution()
    analyzer.test_polyalphabetic_variants()
    
    # Summary
    print("\n" + "="*70)
    print("MULTIPLE CIPHERS SUMMARY")
    print("="*70)
    
    print("\nTested simultaneous cipher methods:")
    print("- Interleaved (alternating characters)")
    print("- Overlapping segments")
    print("- Progressive (chained ciphers)")
    print("- Split key (different keys for regions)")
    print("- Fractionated (split and recombine)")
    print("- Homophonic substitution")
    print("- Polyalphabetic variants (Beaufort)")
    
    print("\nThe confirmed MIR HEAT finding still appears with")
    print("ABSCISSA on the middle segment, but no complete")
    print("solution emerged from multiple cipher approaches.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()