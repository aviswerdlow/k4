#!/usr/bin/env python3
"""
f3_anchors_as_keys.py

Testing the hypothesis that the "known" anchors are actually keys, not plaintext.
What if BERLIN, CLOCK, EAST, NORTHEAST are the keys to decrypt their zones?
"""

from typing import List, Tuple, Dict, Optional

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Traditional anchor positions (what everyone assumes)
ASSUMED_ANCHORS = {
    'EAST': (21, 25),      # FLRV
    'NORTHEAST': (25, 34), # QQPRNGKSS
    'BERLIN': (63, 69),    # NYPVTT
    'CLOCK': (69, 74)      # MZFPK
}

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class AnchorKeyAnalyzer:
    """Test if anchors are keys, not plaintext."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Zone definitions based on anchor positions
        self.zones = {
            'HEAD': (0, 21),       # Before EAST
            'MIDDLE': (34, 63),    # After NORTHEAST, before BERLIN
            'TAIL': (74, 97)       # After CLOCK
        }
        
        # What if the anchor positions contain ciphertext that should be decrypted?
        self.anchor_zones = {
            'EAST_ZONE': (21, 25),      # FLRV
            'NORTHEAST_ZONE': (25, 34), # QQPRNGKSS
            'BERLIN_ZONE': (63, 69),    # NYPVTT
            'CLOCK_ZONE': (69, 74)      # MZFPK
        }
    
    def vigenere_encrypt(self, text: str, key: str) -> str:
        """Encrypt to verify our hypothesis."""
        if not key:
            return text
        ciphertext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            p_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            c_val = (p_val + k_val) % 26
            ciphertext.append(num_to_char(c_val))
        
        return ''.join(ciphertext)
    
    def vigenere_decrypt(self, text: str, key: str) -> str:
        """Standard Vigenere decryption."""
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
    
    def test_anchors_as_zone_keys(self):
        """Test if anchor words are keys for their adjacent zones."""
        print("\n" + "="*60)
        print("TESTING ANCHORS AS KEYS FOR ZONES")
        print("="*60)
        
        # Test each combination
        tests = [
            # Use anchor as key for the zone before it
            ('EAST', self.ciphertext[0:21], "HEAD zone with EAST key"),
            ('NORTHEAST', self.ciphertext[21:34], "EAST+NORTHEAST zones with NORTHEAST key"),
            ('BERLIN', self.ciphertext[34:63], "MIDDLE zone with BERLIN key"),
            ('CLOCK', self.ciphertext[63:74], "BERLIN+CLOCK zones with CLOCK key"),
            
            # Use anchor as key for the zone after it
            ('EAST', self.ciphertext[25:34], "NORTHEAST zone with EAST key"),
            ('NORTHEAST', self.ciphertext[34:63], "MIDDLE zone with NORTHEAST key"),
            ('BERLIN', self.ciphertext[69:74], "CLOCK zone with BERLIN key"),
            ('CLOCK', self.ciphertext[74:97], "TAIL zone with CLOCK key"),
            
            # Combined keys
            ('EASTWEST', self.ciphertext[0:21], "HEAD with EASTWEST"),
            ('BERLINWALL', self.ciphertext[34:63], "MIDDLE with BERLINWALL"),
            ('BERLINWALL', self.ciphertext[63:74], "BERLIN+CLOCK zones with BERLINWALL"),
            ('DOOMSDAYCLOCK', self.ciphertext[69:97], "CLOCK+TAIL with DOOMSDAYCLOCK"),
        ]
        
        print("\nTesting anchor words as Vigenere keys:")
        
        for key, zone_ct, description in tests:
            pt = self.vigenere_decrypt(zone_ct, key)
            
            # Check for readable text
            if self.has_words(pt) or self.is_readable(pt):
                print(f"\n{description}:")
                print(f"  Key: {key}")
                print(f"  Result: {pt}")
                
                words = self.find_words(pt)
                if words:
                    print(f"  Words found: {words}")
    
    def test_reverse_hypothesis(self):
        """What if we encrypt known words with zone ciphertext as key?"""
        print("\n" + "="*60)
        print("REVERSE HYPOTHESIS TEST")
        print("="*60)
        
        print("\nWhat if the ciphertext at anchor positions is the key?")
        
        # Get ciphertext at anchor positions
        anchor_cts = {
            'FLRV': (21, 25),      # Where EAST should be
            'QQPRNGKSS': (25, 34), # Where NORTHEAST should be
            'NYPVTT': (63, 69),    # Where BERLIN should be
            'MZFPK': (69, 74)      # Where CLOCK should be
        }
        
        # Test using anchor ciphertext as keys
        for ct_key, (start, end) in anchor_cts.items():
            print(f"\nUsing '{ct_key}' as key:")
            
            # Try on different zones
            for zone_name, (z_start, z_end) in self.zones.items():
                zone_ct = self.ciphertext[z_start:z_end]
                pt = self.vigenere_decrypt(zone_ct, ct_key)
                
                if self.has_words(pt):
                    print(f"  {zone_name}: {pt[:40]}...")
                    words = self.find_words(pt)
                    if words:
                        print(f"    Words: {words}")
    
    def test_key_derivation(self):
        """Test if anchors generate keys through some transformation."""
        print("\n" + "="*60)
        print("KEY DERIVATION FROM ANCHORS")
        print("="*60)
        
        # Maybe the anchors undergo transformation to become keys
        anchors = ['EAST', 'NORTHEAST', 'BERLIN', 'CLOCK']
        
        print("\nTesting transformations of anchor words:")
        
        for anchor in anchors:
            # Various transformations
            keys = [
                anchor,                          # Direct
                anchor[::-1],                    # Reversed
                anchor + anchor,                 # Doubled
                anchor[1:] + anchor[0],         # Caesar shift
                ''.join(chr((ord(c) - ord('A') + 13) % 26 + ord('A')) for c in anchor),  # ROT13
            ]
            
            # Add numeric/date variants for BERLIN and CLOCK
            if anchor == 'BERLIN':
                keys.extend(['BERLIN1989', 'NOVEMBER', 'WALLFALL', 'DIVIDED'])
            elif anchor == 'CLOCK':
                keys.extend(['MIDNIGHT', 'DOOMSDAY', 'ATOMIC', 'NUCLEAR'])
            
            for key in keys:
                # Test on middle zone (where we found MIR HEAT)
                pt = self.vigenere_decrypt(self.ciphertext[34:63], key)
                
                if 'MIR' in pt or 'HEAT' in pt or self.has_words(pt):
                    print(f"\n{anchor} → {key}:")
                    print(f"  Middle zone: {pt}")
                    if 'MIR' in pt:
                        print(f"    Contains MIR at position {pt.find('MIR')}")
                    if 'HEAT' in pt:
                        print(f"    Contains HEAT at position {pt.find('HEAT')}")
    
    def test_progressive_anchors(self):
        """Test if anchors work progressively through the cipher."""
        print("\n" + "="*60)
        print("PROGRESSIVE ANCHOR APPLICATION")
        print("="*60)
        
        print("\nWhat if anchors are applied sequentially?")
        
        # Progressive decryption
        text = self.ciphertext
        
        # Apply EAST
        text1 = self.vigenere_decrypt(text[:25], 'EAST')
        remainder1 = text[25:]
        stage1 = text1 + remainder1
        
        # Apply NORTHEAST
        text2 = self.vigenere_decrypt(stage1[25:34], 'NORTHEAST')
        stage2 = stage1[:25] + text2 + stage1[34:]
        
        # Apply BERLIN
        text3 = self.vigenere_decrypt(stage2[34:69], 'BERLIN')
        stage3 = stage2[:34] + text3 + stage2[69:]
        
        # Apply CLOCK
        text4 = self.vigenere_decrypt(stage3[69:], 'CLOCK')
        final = stage3[:69] + text4
        
        print(f"After EAST: {stage1[:40]}...")
        print(f"After NORTHEAST: {stage2[:40]}...")
        print(f"After BERLIN: {stage3[:40]}...")
        print(f"After CLOCK: {final[:40]}...")
        
        # Check for improvements
        words = self.find_words(final)
        if words:
            print(f"\nWords found in final: {words}")
    
    def test_anchor_interactions(self):
        """Test if anchors interact with each other."""
        print("\n" + "="*60)
        print("ANCHOR INTERACTIONS")
        print("="*60)
        
        # Maybe anchors combine or interact
        print("\nTesting anchor combinations:")
        
        combinations = [
            ('EAST', 'WEST'),
            ('NORTHEAST', 'SOUTHWEST'),
            ('BERLIN', 'WALL'),
            ('BERLIN', 'CLOCK'),
            ('CLOCK', 'TOWER'),
            ('ATOMIC', 'CLOCK'),
            ('DOOMSDAY', 'CLOCK')
        ]
        
        for word1, word2 in combinations:
            # Try as combined key
            combined_key = word1 + word2
            
            # Test on middle zone
            pt = self.vigenere_decrypt(self.ciphertext[34:63], combined_key)
            
            if self.has_words(pt) or 'MIR' in pt or 'HEAT' in pt:
                print(f"\n{word1} + {word2} = {combined_key}:")
                print(f"  {pt}")
                
                words = self.find_words(pt)
                if words:
                    print(f"  Words: {words}")
    
    def verify_anchor_positions(self):
        """Verify what's actually at the assumed anchor positions."""
        print("\n" + "="*60)
        print("VERIFYING ANCHOR POSITIONS")
        print("="*60)
        
        print("\nWhat's actually at the anchor positions:")
        
        for anchor, (start, end) in ASSUMED_ANCHORS.items():
            actual_ct = self.ciphertext[start:end]
            print(f"\n{anchor} should be at {start}-{end}")
            print(f"  Actual ciphertext: {actual_ct}")
            
            # What key would produce this anchor from this ciphertext?
            # If BERLIN encrypts to NYPVTT, what's the key?
            if anchor == 'BERLIN' and actual_ct == 'NYPVTT':
                # Calculate key
                key_chars = []
                for i in range(len(anchor)):
                    p_val = char_to_num(anchor[i])
                    c_val = char_to_num(actual_ct[i])
                    k_val = (c_val - p_val) % 26
                    key_chars.append(num_to_char(k_val))
                derived_key = ''.join(key_chars)
                print(f"  Key to get {anchor} from {actual_ct}: {derived_key}")
                
                # Test this key elsewhere
                test_pt = self.vigenere_decrypt(self.ciphertext[34:63], derived_key)
                if self.has_words(test_pt):
                    print(f"  Using {derived_key} on middle zone: {test_pt[:30]}...")
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'HEAT', 'MIR', 'WAR', 'PEACE']
        return any(word in text for word in words)
    
    def find_words(self, text: str) -> List[str]:
        """Find common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD',
                 'HEAT', 'MIR', 'WAR', 'PEACE', 'WALL', 'BERLIN']
        return [word for word in words if word in text]
    
    def is_readable(self, text: str) -> bool:
        """Check if text is readable."""
        if len(text) < 3:
            return False
        
        vowels = sum(1 for c in text if c in 'AEIOU')
        ratio = vowels / len(text)
        
        if not (0.30 <= ratio <= 0.50):
            return False
        
        # Check for Q without U
        for i in range(len(text)-1):
            if text[i] == 'Q' and text[i+1] != 'U':
                return False
        
        return True

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("ANCHORS AS KEYS ANALYSIS")
    print("Testing if BERLIN, CLOCK, etc. are keys, not plaintext")
    print("="*70)
    
    analyzer = AnchorKeyAnalyzer()
    
    # Run all tests
    analyzer.verify_anchor_positions()
    analyzer.test_anchors_as_zone_keys()
    analyzer.test_reverse_hypothesis()
    analyzer.test_key_derivation()
    analyzer.test_progressive_anchors()
    analyzer.test_anchor_interactions()
    
    # Summary
    print("\n" + "="*70)
    print("ANCHORS AS KEYS SUMMARY")
    print("="*70)
    
    print("\nKey question:")
    print("For 20+ years, everyone assumed BERLIN, CLOCK, etc.")
    print("appear as plaintext in K4. But what if they're actually")
    print("the KEYS to decrypt K4, not part of the message?")
    
    print("\nThis would explain:")
    print("1. Why no polyalphabetic cipher preserves them")
    print("2. Why the solution has remained elusive")
    print("3. Why Sanborn said the solution is 'simple'")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()