#!/usr/bin/env python3
"""
f3_heat_is_extension.py

Deep investigation of "HEAT IS" and attempting to extend the readable portion.
Building on confirmed MIR HEAT finding.
"""

from typing import List, Tuple, Dict, Optional
import itertools

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class HeatIsAnalyzer:
    """Analyze and extend the HEAT IS pattern."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.middle_ct = self.ciphertext[34:63]
        
        # Confirmed with ABSCISSA
        self.middle_pt = "OSERIARQSRMIRHEATISJMLQAWHVDT"
        
        # Key segments
        self.before_mir = self.middle_pt[:10]  # OSERIARQSR
        self.mir_heat = self.middle_pt[10:17]  # MIRHEAT
        self.after_heat = self.middle_pt[17:]  # ISJMLQAWHVDT
        
        # Common words that could follow "HEAT IS"
        self.heat_is_continuations = [
            # States
            'RISING', 'FALLING', 'SPREADING', 'BUILDING', 'FADING',
            'INCREASING', 'DECREASING', 'CRITICAL', 'DANGEROUS', 'INTENSE',
            # Descriptors  
            'REAL', 'DEADLY', 'NUCLEAR', 'ATOMIC', 'GLOBAL', 'LOCAL',
            'EXTREME', 'SEVERE', 'MODERATE', 'MINIMAL', 'MAXIMUM',
            # Actions
            'COMING', 'GOING', 'HERE', 'THERE', 'EVERYWHERE',
            'MEASURED', 'DETECTED', 'CONFIRMED', 'DENIED', 'HIDDEN',
            # Cold War specific
            'WAR', 'PEACE', 'TENSION', 'ESCALATING', 'ENDING'
        ]
        
        # Keys to test for the "IS" portion
        self.is_keys = [
            # Single words
            'THE', 'AND', 'WAR', 'PEACE', 'END', 'NEAR', 'HERE',
            # Cold War terms
            'MOSCOW', 'BERLIN', 'NUCLEAR', 'ATOMIC', 'SOVIET',
            # Mathematical/surveying
            'DEGREE', 'ANGLE', 'MEASURE', 'COORDINATE', 'POSITION',
            # Temperature
            'CELSIUS', 'FAHRENHEIT', 'KELVIN', 'THERMAL', 'BURNING'
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
    
    def analyze_is_pattern(self):
        """Analyze the IS pattern after HEAT."""
        print("\n" + "="*60)
        print("ANALYZING 'HEAT IS' PATTERN")
        print("="*60)
        
        print(f"\nConfirmed: MIR HEAT IS...")
        print(f"After HEAT: '{self.after_heat}'")
        print(f"Starts with: 'IS'")
        print(f"Followed by: 'JMLQAWHVDT'")
        
        # What could JMLQAWHVDT decrypt to?
        after_is = self.after_heat[2:]  # JMLQAWHVDT
        after_is_ct = self.middle_ct[19:]  # Corresponding ciphertext
        
        print(f"\nTesting what comes after 'IS':")
        print(f"Ciphertext after IS: {after_is_ct}")
        print(f"Current plaintext: {after_is}")
        
        # Test different keys for the portion after IS
        results = []
        for key in self.heat_is_continuations[:20]:  # Test first 20
            # Try different starting positions for the key
            for offset in range(len(key)):
                pt = self.vigenere_decrypt(after_is_ct, key, offset)
                
                # Check if it produces readable text
                if self.is_readable(pt):
                    results.append((key, offset, pt))
                    print(f"\n  {key} (offset {offset}): {pt}")
                    
                    # Check for common words
                    words = self.find_words(pt)
                    if words:
                        print(f"    Words found: {words}")
        
        return results
    
    def test_full_phrase_keys(self):
        """Test keys that might work for 'HEAT IS [something]'."""
        print("\n" + "="*60)
        print("TESTING FULL PHRASE KEYS")
        print("="*60)
        
        # The segment containing "HEAT IS"
        heat_is_start = 13  # Position of HEAT in middle segment
        heat_is_ct = self.middle_ct[heat_is_start:]
        
        print(f"\nTesting keys for 'HEAT IS...' segment:")
        print(f"Ciphertext: {heat_is_ct}")
        
        # Test Cold War phrases
        cold_war_phrases = [
            'COLDWAR', 'NUCLEAR', 'ATOMIC', 'SOVIET', 'AMERICA',
            'DETENTE', 'GLASNOST', 'PEACE', 'TREATY', 'MISSILE'
        ]
        
        for key in cold_war_phrases:
            pt = self.vigenere_decrypt(heat_is_ct, key)
            if 'HEAT' in pt or 'IS' in pt or self.has_words(pt):
                print(f"\n  {key}: {pt[:20]}...")
                if 'HEATIS' in pt:
                    print(f"    *** Preserves HEAT IS! ***")
    
    def reverse_engineer_key(self):
        """Try to figure out what key would produce 'HEAT IS [word]'."""
        print("\n" + "="*60)
        print("REVERSE ENGINEERING KEY FROM 'HEAT IS'")
        print("="*60)
        
        # We know positions 13-18 should be "HEATIS"
        target = "HEATIS"
        actual_ct = self.middle_ct[13:19]
        
        print(f"\nTarget plaintext: {target}")
        print(f"Actual ciphertext: {actual_ct}")
        
        # Calculate what key would produce this
        key_chars = []
        for i in range(len(target)):
            p_val = char_to_num(target[i])
            c_val = char_to_num(actual_ct[i])
            k_val = (c_val - p_val) % 26
            key_chars.append(num_to_char(k_val))
        
        derived_key = ''.join(key_chars)
        print(f"Derived key segment: {derived_key}")
        
        # Test if this key pattern extends
        print("\nTesting if this key pattern extends:")
        
        # Try repeating the pattern
        for repeat in range(1, 4):
            test_key = derived_key * repeat
            pt = self.vigenere_decrypt(self.middle_ct, test_key)
            if 'HEATIS' in pt:
                print(f"\n  Key '{test_key}' (repeat {repeat}):")
                print(f"    {pt}")
                heat_pos = pt.find('HEAT')
                if heat_pos >= 0:
                    context = pt[max(0, heat_pos-5):min(len(pt), heat_pos+15)]
                    print(f"    Context: ...{context}...")
    
    def test_qsr_pattern(self):
        """Analyze the QSR pattern before MIR."""
        print("\n" + "="*60)
        print("ANALYZING QSR PATTERN")
        print("="*60)
        
        print(f"\nBefore MIR: '{self.before_mir}'")
        print(f"Contains: RQSR (unusual Q without U)")
        
        # QSR could be:
        # 1. Abbreviation
        # 2. Cipher boundary
        # 3. Different cipher method needed
        
        print("\nPossible interpretations:")
        print("1. QSR as abbreviation (military/technical)")
        print("2. Q as separator/null character")
        print("3. Different cipher for this section")
        
        # Test if different cipher method works better
        before_mir_ct = self.middle_ct[:10]
        
        print(f"\nTesting alternative decryptions for pre-MIR section:")
        print(f"Ciphertext: {before_mir_ct}")
        
        # Test simple substitution
        print("\n  Simple substitution patterns:")
        # ROT13
        rot13 = ''.join(chr((ord(c) - ord('A') + 13) % 26 + ord('A')) for c in before_mir_ct)
        print(f"    ROT13: {rot13}")
        
        # Atbash
        atbash = ''.join(chr(ord('Z') - (ord(c) - ord('A'))) for c in before_mir_ct)
        print(f"    Atbash: {atbash}")
    
    def test_zone_synchronization(self):
        """Test if zones work together narratively."""
        print("\n" + "="*60)
        print("TESTING ZONE SYNCHRONIZATION")
        print("="*60)
        
        print("\nHypothesis: Zones tell connected story")
        print("MIDDLE confirmed: ...MIR HEAT IS...")
        
        # Test HEAD zone with complementary keys
        head_ct = self.ciphertext[0:21]
        tail_ct = self.ciphertext[74:97]
        
        narratives = [
            # (HEAD key, TAIL key, narrative theme)
            ('BERLIN', 'FALLING', 'Berlin Wall falling'),
            ('SOVIET', 'ENDING', 'Soviet Union ending'),
            ('NUCLEAR', 'TREATY', 'Nuclear treaty'),
            ('MOSCOW', 'PEACE', 'Moscow peace talks'),
            ('COLDWAR', 'OVER', 'Cold War ending')
        ]
        
        print("\nTesting narrative combinations:")
        for head_key, tail_key, theme in narratives:
            head_pt = self.vigenere_decrypt(head_ct, head_key)
            tail_pt = self.vigenere_decrypt(tail_ct, tail_key)
            
            head_words = self.find_words(head_pt)
            tail_words = self.find_words(tail_pt)
            
            if head_words or tail_words:
                print(f"\n  {theme}:")
                print(f"    HEAD ({head_key}): {head_pt[:20]}... Words: {head_words}")
                print(f"    MIDDLE: ...MIR HEAT IS...")
                print(f"    TAIL ({tail_key}): {tail_pt[:20]}... Words: {tail_words}")
    
    def test_mixed_ciphers(self):
        """Test if different zones use different cipher types."""
        print("\n" + "="*60)
        print("TESTING MIXED CIPHER METHODS")
        print("="*60)
        
        print("\nHypothesis: Different zones use different ciphers")
        print("MIDDLE: Confirmed Vigenère with ABSCISSA")
        
        # Test HEAD with transposition
        head_ct = self.ciphertext[0:21]
        
        print("\nHEAD zone - testing transposition:")
        # Simple columnar transposition with different column counts
        for cols in [3, 4, 5, 7]:
            if 21 % cols == 0:
                rows = 21 // cols
                # Read by columns
                transposed = ''
                for c in range(cols):
                    for r in range(rows):
                        transposed += head_ct[r * cols + c]
                
                print(f"  {cols} columns: {transposed}")
                if self.has_words(transposed):
                    print(f"    *** Contains words! ***")
        
        # Test TAIL with simple substitution
        tail_ct = self.ciphertext[74:97]
        
        print("\nTAIL zone - testing substitution:")
        # Frequency analysis
        from collections import Counter
        freq = Counter(tail_ct)
        print(f"  Most common: {freq.most_common(5)}")
        
        # Try mapping most common to E, T, A
        most_common_ct = freq.most_common(1)[0][0]
        for common_pt in ['E', 'T', 'A', 'O', 'I']:
            shift = (ord(most_common_ct) - ord(common_pt)) % 26
            shifted = ''.join(chr((ord(c) - ord('A') - shift) % 26 + ord('A')) for c in tail_ct)
            if self.has_words(shifted):
                print(f"  Mapping {most_common_ct}->{common_pt}: {shifted[:30]}...")
                words = self.find_words(shifted)
                if words:
                    print(f"    Words: {words}")
    
    def is_readable(self, text: str) -> bool:
        """Check if text is readable."""
        if len(text) < 3:
            return False
        
        vowels = sum(1 for c in text if c in 'AEIOU')
        if len(text) == 0:
            return False
        ratio = vowels / len(text)
        
        if not (0.25 <= ratio <= 0.55):
            return False
        
        # Check consonant runs
        max_cons = 0
        current = 0
        for c in text:
            if c not in 'AEIOU':
                current += 1
                max_cons = max(max_cons, current)
            else:
                current = 0
        
        return max_cons <= 5
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'HEAT', 'IS', 'WAR', 'PEACE']
        return any(word in text for word in words)
    
    def find_words(self, text: str) -> List[str]:
        """Find all common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD',
                 'HEAT', 'IS', 'WAR', 'PEACE', 'END', 'COLD', 'HOT']
        found = []
        for word in words:
            if word in text:
                found.append(word)
        return found

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("HEAT IS EXTENSION ANALYSIS")
    print("Deep dive into extending the readable portion")
    print("="*70)
    
    analyzer = HeatIsAnalyzer()
    
    # Run analyses
    analyzer.analyze_is_pattern()
    analyzer.test_full_phrase_keys()
    analyzer.reverse_engineer_key()
    analyzer.test_qsr_pattern()
    analyzer.test_zone_synchronization()
    analyzer.test_mixed_ciphers()
    
    # Summary
    print("\n" + "="*70)
    print("HEAT IS ANALYSIS SUMMARY")
    print("="*70)
    
    print("\nKey findings:")
    print("1. 'HEAT IS' forms a grammatical phrase")
    print("2. 'JMLQAWHVDT' after IS remains unreadable")
    print("3. QSR pattern before MIR is unusual (Q without U)")
    print("4. Different cipher methods per zone worth exploring")
    
    print("\nNext steps:")
    print("1. Focus on mixed cipher hypothesis")
    print("2. Test transposition for HEAD zone")
    print("3. Test substitution for TAIL zone")
    print("4. Consider that IS might not be English 'is'")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()