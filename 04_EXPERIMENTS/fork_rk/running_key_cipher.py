#!/usr/bin/env python3
"""
running_key_cipher.py

Fork RK - Running-Key cipher from K1-K3 plaintexts.
Non-periodic, position-preserving approach.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# K1-K3 plaintexts (known solutions)
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K2_PLAINTEXT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K3_PLAINTEXT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDHISCANDLEANDPEEREDINTHEHOTAIRCSCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEE"

# Misspellings from K1-K3
MISSPELLINGS = ["IQLUSION", "UNDERGRUUND", "DESPARATLY"]

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class RunningKeyCipher:
    """Running-key cipher using K1-K3 plaintexts as key material."""
    
    def __init__(self, key_text: str, offset: int = 0):
        """
        Initialize with key text and offset.
        
        Args:
            key_text: The running key text
            offset: Starting offset into the key
        """
        self.key_text = key_text.upper()
        self.offset = offset
        self.key_length = len(self.key_text)
    
    def _get_key_char(self, position: int) -> str:
        """Get key character for given position."""
        if self.key_length == 0:
            return 'A'  # Default if no key
        
        # Calculate actual position with offset and wrapping
        key_pos = (position + self.offset) % self.key_length
        return self.key_text[key_pos]
    
    def decrypt_vigenere(self, ciphertext: str) -> str:
        """Decrypt using Vigenère with running key."""
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            key_char = self._get_key_char(i)
            c_val = char_to_num(c)
            k_val = char_to_num(key_char)
            
            # Vigenère: P = (C - K) mod 26
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def decrypt_beaufort(self, ciphertext: str) -> str:
        """Decrypt using Beaufort with running key."""
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            key_char = self._get_key_char(i)
            c_val = char_to_num(c)
            k_val = char_to_num(key_char)
            
            # Beaufort: P = (K - C) mod 26
            p_val = (k_val - c_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def decrypt_variant_beaufort(self, ciphertext: str) -> str:
        """Decrypt using Variant Beaufort with running key."""
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            key_char = self._get_key_char(i)
            c_val = char_to_num(c)
            k_val = char_to_num(key_char)
            
            # Variant Beaufort: P = (C + K) mod 26
            p_val = (c_val + k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)

class SegmentedRunningKey:
    """Segmented running key using different K texts for different zones."""
    
    def __init__(self, zone_keys: List[Tuple[int, int, str, int]]):
        """
        Initialize with zone-specific keys.
        
        Args:
            zone_keys: List of (start, end, key_text, offset) tuples
        """
        self.zone_keys = zone_keys
        self.key_map = self._build_key_map()
    
    def _build_key_map(self) -> Dict[int, Tuple[str, int]]:
        """Build per-index key mapping."""
        key_map = {}
        
        for start, end, key_text, offset in self.zone_keys:
            for i in range(start, min(end + 1, 97)):
                # Store the key character for this position
                key_pos = (i - start + offset) % len(key_text)
                key_map[i] = (key_text[key_pos], i)
        
        return key_map
    
    def decrypt_vigenere(self, ciphertext: str) -> str:
        """Decrypt using segmented Vigenère."""
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            if i in self.key_map:
                key_char = self.key_map[i][0]
            else:
                key_char = 'A'  # Default
            
            c_val = char_to_num(c)
            k_val = char_to_num(key_char)
            
            # Vigenère: P = (C - K) mod 26
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def decrypt_beaufort(self, ciphertext: str) -> str:
        """Decrypt using segmented Beaufort."""
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            if i in self.key_map:
                key_char = self.key_map[i][0]
            else:
                key_char = 'A'  # Default
            
            c_val = char_to_num(c)
            k_val = char_to_num(key_char)
            
            # Beaufort: P = (K - C) mod 26
            p_val = (k_val - c_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def decrypt_variant_beaufort(self, ciphertext: str) -> str:
        """Decrypt using segmented Variant Beaufort."""
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            if i in self.key_map:
                key_char = self.key_map[i][0]
            else:
                key_char = 'A'  # Default
            
            c_val = char_to_num(c)
            k_val = char_to_num(key_char)
            
            # Variant Beaufort: P = (C + K) mod 26
            p_val = (c_val + k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)

def generate_running_keys() -> Dict[str, str]:
    """Generate all running key variants."""
    keys = {
        'RK1': K1_PLAINTEXT,
        'RK2': K2_PLAINTEXT,
        'RK3': K3_PLAINTEXT,
        'RK123': K1_PLAINTEXT + K2_PLAINTEXT + K3_PLAINTEXT,
        'RK_MISSPELL': ''.join(MISSPELLINGS * 20)[:97],  # Repeated misspellings
        'RK2_INVISIBLE': K2_PLAINTEXT[:47],  # "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSED"
        'RK2_COORDINATES': K2_PLAINTEXT[217:],  # The coordinate section
    }
    
    return keys

def generate_segmented_keys() -> List[Dict]:
    """Generate segmented key configurations."""
    configs = []
    
    # RKmix: Different K texts for different zones
    # Zone 1: 0-20 use K1
    # Zone 2: 21-73 use K2  
    # Zone 3: 74-96 use K3
    
    for offset in range(0, 16):  # Offset grid 0..15
        config = {
            'name': f'RKmix_offset{offset}',
            'zones': [
                (0, 20, K1_PLAINTEXT, offset),
                (21, 73, K2_PLAINTEXT, offset),
                (74, 96, K3_PLAINTEXT, offset)
            ]
        }
        configs.append(config)
    
    # Alternative segmentation: anchors get special treatment
    for offset in range(0, 8):
        config = {
            'name': f'RKanchor_offset{offset}',
            'zones': [
                (0, 20, K1_PLAINTEXT, offset),      # Head
                (21, 33, K3_PLAINTEXT, offset),      # EAST+NORTHEAST (use K3)
                (34, 62, K2_PLAINTEXT, offset),      # Mid
                (63, 73, K3_PLAINTEXT, offset + 20), # BERLIN+CLOCK (use K3 with offset)
                (74, 96, K1_PLAINTEXT, offset + 40)  # Tail (use K1 with offset)
            ]
        }
        configs.append(config)
    
    return configs

def test_running_key():
    """Test running key cipher."""
    print("Testing Running Key Cipher")
    print("-" * 50)
    
    # Test ciphertext (K4)
    test_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # Test RK1 with different offsets
    print("\nTesting RK1 (K1 plaintext):")
    for offset in [0, 10, 20]:
        cipher = RunningKeyCipher(K1_PLAINTEXT, offset)
        plaintext = cipher.decrypt_vigenere(test_ct)
        print(f"  Offset {offset:2d}: {plaintext[:30]}...")
    
    # Test segmented key
    print("\nTesting Segmented Key (RKmix):")
    zones = [
        (0, 20, K1_PLAINTEXT, 0),
        (21, 73, K2_PLAINTEXT, 0),
        (74, 96, K3_PLAINTEXT, 0)
    ]
    seg_cipher = SegmentedRunningKey(zones)
    plaintext = seg_cipher.decrypt_vigenere(test_ct)
    print(f"  Head (0-20): {plaintext[:21]}")
    print(f"  EAST region: {plaintext[21:34]}")
    print(f"  BERLIN region: {plaintext[63:74]}")

if __name__ == "__main__":
    test_running_key()