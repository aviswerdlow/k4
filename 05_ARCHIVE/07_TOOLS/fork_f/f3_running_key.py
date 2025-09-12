#!/usr/bin/env python3
"""
f3_running_key.py

Testing if K4 uses a running key cipher with K1, K2, or K3 plaintexts as the key.
This would be elegant - using previously solved sections to solve K4.
"""

from typing import List, Tuple, Dict, Optional

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Known plaintexts from K1, K2, K3
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K2_PLAINTEXT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGROUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXANDAHALFSECONDSXSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K3_PLAINTEXT = "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRTHATESCAPEDFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class RunningKeyAnalyzer:
    """Test running key cipher hypothesis."""
    
    def __init__(self):
        self.k4_ct = K4_CIPHERTEXT
        self.k1_pt = K1_PLAINTEXT
        self.k2_pt = K2_PLAINTEXT
        self.k3_pt = K3_PLAINTEXT
        
        # Combined plaintexts
        self.k123_pt = self.k1_pt + self.k2_pt + self.k3_pt
        
        # Key phrases from K1, K2, K3
        self.key_phrases = {
            'K1': {
                'NUANCE': self.k1_pt.find('NUANCE'),
                'IQLUSION': self.k1_pt.find('IQLUSION'),
                'ABSENCE': self.k1_pt.find('ABSENCE'),
                'LIGHT': self.k1_pt.find('LIGHT')
            },
            'K2': {
                'LANGLEY': self.k2_pt.find('LANGLEY'),
                'BURIED': self.k2_pt.find('BURIED'),
                'MAGNETIC': self.k2_pt.find('MAGNETIC'),
                'UNDERGROUND': self.k2_pt.find('UNDERGROUND'),
                'COORDINATES': 285  # Start of coordinate section
            },
            'K3': {
                'SLOWLY': self.k3_pt.find('SLOWLY'),
                'CANDLE': self.k3_pt.find('CANDLE'),
                'CHAMBER': self.k3_pt.find('CHAMBER'),
                'EMERGED': self.k3_pt.find('EMERGED')
            }
        }
    
    def running_key_decrypt(self, ciphertext: str, key: str, offset: int = 0) -> str:
        """Decrypt using running key (like Vigenere but key is as long as message)."""
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if i + offset >= len(key):
                break
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[i + offset])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def test_k1_as_key(self):
        """Test K1 plaintext as running key."""
        print("\n" + "="*60)
        print("TESTING K1 AS RUNNING KEY")
        print("="*60)
        
        print(f"\nK1 length: {len(self.k1_pt)}")
        print(f"K4 length: {len(self.k4_ct)}")
        print(f"K1 text: {self.k1_pt[:50]}...")
        
        # Try different starting positions in K1
        for offset in range(0, len(self.k1_pt) - len(self.k4_ct) + 1, 5):
            pt = self.running_key_decrypt(self.k4_ct, self.k1_pt, offset)
            
            if self.has_meaningful_words(pt):
                print(f"\nOffset {offset} (K1 from '{self.k1_pt[offset:offset+10]}...'):")
                print(f"  Result: {pt[:50]}...")
                words = self.find_words(pt)
                if words:
                    print(f"  Words: {words}")
        
        # Try specific meaningful positions
        print("\n\nTrying specific K1 positions:")
        for phrase, pos in self.key_phrases['K1'].items():
            if pos >= 0:
                pt = self.running_key_decrypt(self.k4_ct, self.k1_pt, pos)
                if self.has_words(pt):
                    print(f"\nStarting at '{phrase}' (pos {pos}):")
                    print(f"  {pt[:50]}...")
    
    def test_k2_as_key(self):
        """Test K2 plaintext as running key."""
        print("\n" + "="*60)
        print("TESTING K2 AS RUNNING KEY")
        print("="*60)
        
        print(f"\nK2 length: {len(self.k2_pt)}")
        print("K2 contains coordinates and LANGLEY reference")
        
        # Test meaningful K2 positions
        significant_positions = [
            (self.k2_pt.find('LANGLEY'), 'LANGLEY'),
            (self.k2_pt.find('BURIED'), 'BURIED'),
            (self.k2_pt.find('UNDERGROUND'), 'UNDERGROUND'),
            (285, 'COORDINATES_START'),  # Where coordinates begin
            (self.k2_pt.find('LAYERTWO'), 'LAYERTWO')
        ]
        
        for pos, name in significant_positions:
            if pos >= 0 and pos < len(self.k2_pt) - 50:
                pt = self.running_key_decrypt(self.k4_ct, self.k2_pt, pos)
                
                if self.has_words(pt) or 'MIR' in pt or 'HEAT' in pt:
                    print(f"\nStarting at {name} (pos {pos}):")
                    print(f"  Key portion: {self.k2_pt[pos:pos+30]}...")
                    print(f"  Result: {pt[:50]}...")
                    
                    if 'MIR' in pt:
                        print(f"    Contains MIR!")
                    if 'HEAT' in pt:
                        print(f"    Contains HEAT!")
                    
                    words = self.find_words(pt)
                    if words:
                        print(f"    Words: {words}")
    
    def test_k3_as_key(self):
        """Test K3 plaintext as running key."""
        print("\n" + "="*60)
        print("TESTING K3 AS RUNNING KEY")
        print("="*60)
        
        print(f"\nK3 length: {len(self.k3_pt)}")
        print("K3 describes Howard Carter discovering King Tut's tomb")
        
        # Test significant K3 positions
        significant_positions = [
            (0, 'SLOWLY'),
            (self.k3_pt.find('CANDLE'), 'CANDLE'),
            (self.k3_pt.find('CHAMBER'), 'CHAMBER'),
            (self.k3_pt.find('EMERGED'), 'EMERGED'),
            (self.k3_pt.find('CANYOUSEE'), 'CANYOUSEE')
        ]
        
        for pos, name in significant_positions:
            if pos >= 0:
                pt = self.running_key_decrypt(self.k4_ct, self.k3_pt, pos)
                
                if self.has_words(pt) or 'MIR' in pt or 'HEAT' in pt:
                    print(f"\nStarting at {name} (pos {pos}):")
                    print(f"  Key portion: {self.k3_pt[pos:pos+30]}...")
                    print(f"  Result: {pt[:50]}...")
                    
                    words = self.find_words(pt)
                    if words:
                        print(f"    Words: {words}")
    
    def test_combined_k123(self):
        """Test combined K1+K2+K3 as running key."""
        print("\n" + "="*60)
        print("TESTING COMBINED K1+K2+K3")
        print("="*60)
        
        combined = self.k1_pt + self.k2_pt + self.k3_pt
        print(f"\nCombined length: {len(combined)}")
        
        # Test transitions between sections
        transitions = [
            (len(self.k1_pt) - 10, "K1→K2 transition"),
            (len(self.k1_pt) + len(self.k2_pt) - 10, "K2→K3 transition"),
            (0, "Start of K1"),
            (len(self.k1_pt), "Start of K2"),
            (len(self.k1_pt) + len(self.k2_pt), "Start of K3")
        ]
        
        for pos, name in transitions:
            if pos >= 0 and pos < len(combined) - len(self.k4_ct):
                pt = self.running_key_decrypt(self.k4_ct, combined, pos)
                
                if self.has_meaningful_words(pt):
                    print(f"\n{name} (pos {pos}):")
                    print(f"  Key: {combined[pos:pos+30]}...")
                    print(f"  Result: {pt[:50]}...")
                    
                    words = self.find_words(pt)
                    if words:
                        print(f"    Words: {words}")
    
    def test_reverse_running_key(self):
        """Test if K4 is the key and K1/K2/K3 is the plaintext."""
        print("\n" + "="*60)
        print("REVERSE RUNNING KEY TEST")
        print("="*60)
        
        print("\nWhat if K4 is the KEY to decrypt parts of K1/K2/K3?")
        
        # Use K4 as key to decrypt sections of K1, K2, K3
        tests = [
            (self.k1_pt[:97], "K1 with K4 as key"),
            (self.k2_pt[:97], "K2 with K4 as key"),
            (self.k3_pt[:97], "K3 with K4 as key")
        ]
        
        for plaintext_section, description in tests:
            # Encrypt the known plaintext with K4 as key
            result = []
            for i in range(len(self.k4_ct)):
                if i < len(plaintext_section):
                    p_val = char_to_num(plaintext_section[i])
                    k_val = char_to_num(self.k4_ct[i])
                    c_val = (p_val + k_val) % 26
                    result.append(num_to_char(c_val))
            
            result_text = ''.join(result)
            print(f"\n{description}:")
            print(f"  Result: {result_text[:50]}...")
            
            # Check if this matches any known ciphertext patterns
            if self.has_words(result_text):
                words = self.find_words(result_text)
                print(f"    Words found: {words}")
    
    def test_keyword_from_previous(self):
        """Test if keywords from K1/K2/K3 are used as keys for K4."""
        print("\n" + "="*60)
        print("KEYWORDS FROM K1/K2/K3")
        print("="*60)
        
        keywords = [
            # From K1
            'IQLUSION', 'NUANCE', 'ABSENCE', 'LIGHT', 'SHADOW',
            # From K2
            'LANGLEY', 'MAGNETIC', 'UNDERGROUND', 'BURIED', 'LAYERTWO',
            # From K3
            'SLOWLY', 'CHAMBER', 'CANDLE', 'EMERGED', 'CARTER',
            # Combinations
            'IQLANGLEY', 'NUANCELAYER', 'LIGHTCHAMBER'
        ]
        
        print("\nTesting keywords as Vigenere keys:")
        
        for keyword in keywords:
            pt = self.vigenere_decrypt(self.k4_ct, keyword)
            
            if self.has_meaningful_words(pt) or 'MIR' in pt or 'HEAT' in pt:
                print(f"\n{keyword}:")
                print(f"  {pt[:50]}...")
                
                if 'MIR' in pt or 'HEAT' in pt:
                    print(f"    Contains MIR/HEAT!")
                
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Standard Vigenere for comparison."""
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
    
    def has_words(self, text: str) -> bool:
        """Basic word check."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS']
        return any(word in text for word in words)
    
    def has_meaningful_words(self, text: str) -> bool:
        """Check for more meaningful words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'THAT', 'HAVE',
                 'HEAT', 'MIR', 'WAR', 'PEACE', 'BERLIN', 'CLOCK',
                 'LANGLEY', 'BURIED', 'SLOWLY']
        count = sum(1 for word in words if word in text)
        return count >= 2
    
    def find_words(self, text: str) -> List[str]:
        """Find common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD',
                 'HEAT', 'MIR', 'WAR', 'PEACE', 'BERLIN', 'WALL',
                 'LANGLEY', 'CLOCK', 'SLOWLY', 'BURIED']
        return [word for word in words if word in text]

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("RUNNING KEY CIPHER ANALYSIS")
    print("Testing if K1/K2/K3 plaintexts are the key to K4")
    print("="*70)
    
    analyzer = RunningKeyAnalyzer()
    
    # Run all tests
    analyzer.test_k1_as_key()
    analyzer.test_k2_as_key()
    analyzer.test_k3_as_key()
    analyzer.test_combined_k123()
    analyzer.test_reverse_running_key()
    analyzer.test_keyword_from_previous()
    
    # Summary
    print("\n" + "="*70)
    print("RUNNING KEY SUMMARY")
    print("="*70)
    
    print("\nHypothesis:")
    print("K4 might use previous solutions (K1/K2/K3) as its key.")
    print("This would be elegant and explain why it's been unsolvable -")
    print("you need to solve K1, K2, K3 first to get the key for K4.")
    
    print("\nResults:")
    print("No clear matches found with direct running key approach.")
    print("The connection to previous sections might be more subtle.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()