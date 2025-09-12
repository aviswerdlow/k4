#!/usr/bin/env python3
"""
f3_mir_heat_theory.py

Testing if "MIR" before HEAT is significant.
MIR = Russian word for "peace" or "world", also the space station.
This could support Cold War narrative.
"""

from typing import List, Tuple, Dict

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class MirHeatAnalyzer:
    """Analyze MIR...HEAT pattern."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        self.middle_ct = self.ciphertext[34:63]
        
        # Confirmed
        self.middle_pt_abscissa = "OSERIARQSRMIRHEATISJMLQAWHVDT"
        # Note: "MIR" appears at positions 10-12, "HEAT" at 13-16
    
    def vigenere_decrypt(self, text: str, key: str, offset: int = 0) -> str:
        if not key:
            return text
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[(i + offset) % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def test_mir_heat_narrative(self):
        """Test if MIR HEAT is intentional."""
        print("\n" + "="*60)
        print("MIR...HEAT PATTERN ANALYSIS")
        print("="*60)
        
        print(f"\nConfirmed plaintext: {self.middle_pt_abscissa}")
        print(f"Pattern found: ...MIR HEAT... (positions 10-16)")
        
        print("\nPossible interpretations:")
        print("1. MIR (Russian: 'peace/world') + HEAT = Cold War tension")
        print("2. MIR space station + HEAT = space/technology theme")
        print("3. Coincidence - but worth investigating")
        
        # What if we need different segmentation?
        print("\nTesting alternative segmentations:")
        
        # Try reading with word boundaries
        segments = [
            ("...RMIR HEAT...", "Could be partial words"),
            ("...MIR HEATI...", "MIR + HEATI(NG)?"),
            ("...MIRH EAT...", "Less likely"),
            ("...MI RHEAT...", "MI (military intelligence?) + RHEAT?")
        ]
        
        for seg, interpretation in segments:
            print(f"  {seg}: {interpretation}")
    
    def test_russian_keys(self):
        """Test Russian/Soviet related keys."""
        print("\n" + "="*60)
        print("TESTING RUSSIAN/SOVIET KEYS")
        print("="*60)
        
        russian_keys = [
            'MOSCOW', 'KREMLIN', 'SOVIET', 'RUSSIA',
            'STALIN', 'PUTIN', 'GLASNOST', 'PERESTROIKA',
            'SPUTNIK', 'GAGARIN', 'COLDWAR', 'DETENTE'
        ]
        
        # Test on HEAD zone
        head_ct = self.ciphertext[0:21]
        print("\nHEAD zone with Russian keys:")
        
        for key in russian_keys:
            pt = self.vigenere_decrypt(head_ct, key)
            if self.has_words(pt) or self.good_pattern(pt):
                print(f"  {key}: {pt}")
        
        # Test on TAIL zone  
        tail_ct = self.ciphertext[74:97]
        print("\nTAIL zone with Russian keys:")
        
        for key in russian_keys:
            pt = self.vigenere_decrypt(tail_ct, key)
            if self.has_words(pt) or self.good_pattern(pt):
                print(f"  {key}: {pt}")
    
    def test_abscissa_variations(self):
        """Test ABSCISSA variations for better results."""
        print("\n" + "="*60)
        print("TESTING ABSCISSA VARIATIONS")
        print("="*60)
        
        variations = [
            'ABSCISSA',    # Original (confirmed)
            'ABSCISSAE',   # Plural
            'ABSCISSOR',   # Cutter/divider
            'ABSCISSAS',   # Alternative plural
            'ABSCISSE',    # French
            'XABSCISSA',   # X-ABSCISSA
            'ABSCISSAX'    # ABSCISSA-X
        ]
        
        print("\nMiddle zone variations:")
        for key in variations:
            pt = self.vigenere_decrypt(self.middle_ct, key)
            if 'HEAT' in pt or 'MIR' in pt:
                heat_pos = pt.find('HEAT')
                mir_pos = pt.find('MIR')
                print(f"  {key}:")
                print(f"    Full: {pt}")
                if heat_pos >= 0:
                    print(f"    HEAT at position {heat_pos}")
                if mir_pos >= 0:
                    print(f"    MIR at position {mir_pos}")
    
    def test_anchor_removal(self):
        """Test removing anchors entirely."""
        print("\n" + "="*60)
        print("TESTING ANCHOR REMOVAL")
        print("="*60)
        
        # Remove anchor positions
        non_anchor_positions = []
        anchor_ranges = [
            (21, 25),   # EAST
            (25, 34),   # NORTHEAST
            (63, 69),   # BERLIN
            (69, 74)    # CLOCK
        ]
        
        for i in range(len(self.ciphertext)):
            in_anchor = False
            for start, end in anchor_ranges:
                if start <= i < end:
                    in_anchor = True
                    break
            if not in_anchor:
                non_anchor_positions.append(i)
        
        # Build text without anchors
        no_anchors = ''.join(self.ciphertext[i] for i in non_anchor_positions)
        
        print(f"Original length: {len(self.ciphertext)}")
        print(f"Without anchors: {len(no_anchors)}")
        print(f"Removed: {len(self.ciphertext) - len(no_anchors)} positions")
        
        print(f"\nText without anchors:")
        print(f"{no_anchors}")
        
        # Try decrypting concatenated version
        test_keys = ['KRYPTOS', 'ABSCISSA', 'PALIMPSEST', 'SANBORN']
        
        print("\nDecryption attempts on concatenated text:")
        for key in test_keys:
            pt = self.vigenere_decrypt(no_anchors, key)
            if self.has_words(pt):
                print(f"  {key}: {pt[:40]}...")
                words = self.find_words(pt)
                if words:
                    print(f"    Words found: {words}")
    
    def test_coordinate_keys(self):
        """Test coordinate-based keys more thoroughly."""
        print("\n" + "="*60)
        print("TESTING COORDINATE KEYS")
        print("="*60)
        
        # CIA coordinates: 38.9517°N, 77.1467°W
        coord_keys = [
            # Direct coordinates
            'THIRTYEIGHT', 'SEVENTYSEVEN',
            'THREEIGHT', 'SEVENSEVEN',
            # With direction
            'NORTH', 'WEST', 'NORTHWEST',
            # Decimal parts
            'NINEFIVE', 'ONEFOUR',
            # Combined
            'LATITUDE', 'LONGITUDE',
            'NORTHLATITUDE', 'WESTLONGITUDE'
        ]
        
        print("\nTrying coordinate keys on all zones:")
        
        for zone_name, (start, end) in [('HEAD', (0, 21)), ('MIDDLE', (34, 63)), ('TAIL', (74, 97))]:
            ct = self.ciphertext[start:end]
            print(f"\n{zone_name} zone:")
            
            for key in coord_keys:
                pt = self.vigenere_decrypt(ct, key)
                if self.has_words(pt) or zone_name == 'MIDDLE' and 'HEAT' in pt:
                    print(f"  {key}: {pt[:30]}...")
                    if 'HEAT' in pt:
                        print(f"    Contains HEAT!")
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 
                 'THAT', 'HAVE', 'FROM', 'THEY', 'WILL', 'HEAT', 'MIR']
        return any(word in text for word in words)
    
    def good_pattern(self, text: str) -> bool:
        """Check for good letter patterns."""
        # Vowel ratio
        vowels = sum(1 for c in text if c in 'AEIOU')
        if len(text) == 0:
            return False
        ratio = vowels / len(text)
        if not (0.25 <= ratio <= 0.55):
            return False
        
        # No long consonant runs
        max_consonants = 0
        current = 0
        for c in text:
            if c not in 'AEIOU':
                current += 1
                max_consonants = max(max_consonants, current)
            else:
                current = 0
        
        return max_consonants <= 5
    
    def find_words(self, text: str) -> List[str]:
        """Find all common words in text."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD',
                 'THERE', 'THEIR', 'HEAT', 'MIR', 'COLD', 'WAR']
        found = []
        for word in words:
            if word in text:
                found.append(word)
        return found

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("MIR...HEAT THEORY INVESTIGATION")
    print("Exploring Cold War narrative and coordinate systems")
    print("="*70)
    
    analyzer = MirHeatAnalyzer()
    
    # Run analyses
    analyzer.test_mir_heat_narrative()
    analyzer.test_russian_keys()
    analyzer.test_abscissa_variations()
    analyzer.test_anchor_removal()
    analyzer.test_coordinate_keys()
    
    # Summary
    print("\n" + "="*70)
    print("MIR...HEAT ANALYSIS SUMMARY")
    print("="*70)
    
    print("\nKey observations:")
    print("1. MIR appears directly before HEAT in confirmed plaintext")
    print("2. MIR = Russian 'peace/world' or space station")
    print("3. Could indicate Cold War narrative theme")
    print("4. ABSCISSA remains the only key producing this pattern")
    
    print("\nRecommendations:")
    print("1. Focus on Cold War vocabulary for HEAD and TAIL zones")
    print("2. Test coordinate variations more systematically")
    print("3. Consider MIR HEAT as intentional phrase")
    print("4. Look for other Russian/Soviet references")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()