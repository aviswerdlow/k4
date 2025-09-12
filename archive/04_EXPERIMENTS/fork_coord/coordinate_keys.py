#!/usr/bin/env python3
"""
coordinate_keys.py

Fork COORD - Testing coordinate-derived keys for K4.
Based on ABSCISSA success, exploring geometric/coordinate keys.
"""

from typing import List, Tuple, Dict, Optional
import math
from datetime import datetime

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Zone definitions
ZONES = {
    'HEAD': (0, 21),      # Before EAST
    'MIDDLE': (34, 63),   # Between NORTHEAST and BERLIN  
    'TAIL': (74, 97)      # After CLOCK
}

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class CoordinateCipher:
    """Cipher using coordinate-derived keys."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # CIA Headquarters coordinates
        self.cia_lat = 38.9517
        self.cia_lon = -77.1467
        
        # Kryptos dedication date
        self.dedication_date = datetime(1990, 11, 3)
        
        # Generate coordinate-based keys
        self.coord_keys = self.generate_coordinate_keys()
    
    def generate_coordinate_keys(self) -> Dict[str, str]:
        """Generate keys from coordinates and dates."""
        keys = {}
        
        # Direct coordinate strings
        keys['LAT'] = self.coord_to_key(self.cia_lat)
        keys['LON'] = self.coord_to_key(abs(self.cia_lon))
        keys['LATLON'] = keys['LAT'] + keys['LON']
        
        # Mathematical terms with coordinates
        keys['ABSCISSA'] = 'ABSCISSA'  # Confirmed working
        keys['ORDINATE'] = 'ORDINATE'  # Y-coordinate
        keys['COORDINATE'] = 'COORDINATE'
        keys['LATITUDE'] = 'LATITUDE'
        keys['LONGITUDE'] = 'LONGITUDE'
        
        # Date-based keys
        keys['DATE_MDY'] = 'NOVEMBER'  # Month name
        keys['DATE_NUM'] = self.date_to_key(self.dedication_date)
        keys['YEAR'] = 'MCMXC'  # 1990 in Roman numerals
        
        # Location-based
        keys['LANGLEY'] = 'LANGLEY'
        keys['VIRGINIA'] = 'VIRGINIA'
        keys['CIA'] = 'CIA'
        keys['CENTRAINTELLIGENCEAGENCY'] = 'CENTRALINTELLIGENCEAGENCY'
        
        # Compass directions at location
        keys['NORTHWEST'] = 'NORTHWEST'  # CIA is in NW quadrant
        keys['COMPASS'] = 'COMPASS'
        
        # Sculpture-specific
        keys['COPPER'] = 'COPPER'
        keys['GRANITE'] = 'GRANITE'
        keys['PETRIFIED'] = 'PETRIFIED'
        keys['WOOD'] = 'WOOD'
        
        # Mathematical combinations
        keys['THIRTYEIGHT'] = 'THIRTYEIGHT'  # Latitude degrees
        keys['SEVENTYSEVEN'] = 'SEVENTYSEVEN'  # Longitude degrees
        
        return keys
    
    def coord_to_key(self, coord: float) -> str:
        """Convert coordinate to alphabetic key."""
        # Method 1: Digits to letters (3=C, 8=H, etc.)
        coord_str = str(abs(coord)).replace('.', '')
        key = ''
        for digit in coord_str[:8]:  # Limit length
            if digit.isdigit():
                # Map 0-9 to A-J or use modulo for A-Z
                key += chr(ord('A') + (int(digit) % 26))
        return key
    
    def date_to_key(self, date: datetime) -> str:
        """Convert date to key."""
        # Method 1: MMDDYY format
        return f"{date.month:02d}{date.day:02d}{date.year % 100:02d}"
    
    def vigenere_decrypt(self, text: str, key: str, offset: int = 0) -> str:
        """Vigenère decryption."""
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
    
    def beaufort_decrypt(self, text: str, key: str, offset: int = 0) -> str:
        """Beaufort decryption."""
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
            p_val = (k_val - c_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def autokey_decrypt(self, text: str, key: str) -> str:
        """Autokey cipher decryption."""
        if not key:
            return text
            
        plaintext = []
        extended_key = key
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            if i < len(extended_key):
                k_val = char_to_num(extended_key[i])
            else:
                # Use previously decrypted plaintext as key
                k_val = char_to_num(plaintext[i - len(key)])
            
            c_val = char_to_num(c)
            p_val = (c_val - k_val) % 26
            p_char = num_to_char(p_val)
            plaintext.append(p_char)
            
            # Extend key with plaintext
            if i >= len(key):
                extended_key += p_char
        
        return ''.join(plaintext)
    
    def score_plaintext(self, text: str) -> Dict:
        """Score plaintext quality."""
        # Vowel ratio
        vowels = sum(1 for c in text if c in 'AEIOU')
        vowel_ratio = vowels / len(text) if len(text) > 0 else 0
        
        # Common words
        words_found = []
        common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'THAT',
                       'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD', 'THERE', 'THEIR',
                       'HEAT', 'COLD', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TIME',
                       'LANGLEY', 'VIRGINIA', 'CIA', 'AGENT', 'SECRET', 'CODE']
        
        for word in common_words:
            if word in text:
                words_found.append(word)
        
        # Consonant runs
        max_consonant_run = 0
        current_run = 0
        for c in text:
            if c not in 'AEIOU':
                current_run += 1
                max_consonant_run = max(max_consonant_run, current_run)
            else:
                current_run = 0
        
        # Score
        score = len(words_found) * 10
        if 0.35 <= vowel_ratio <= 0.45:
            score += 5
        if max_consonant_run <= 4:
            score += 5
        
        return {
            'score': score,
            'vowel_ratio': round(vowel_ratio, 3),
            'words': words_found,
            'max_consonants': max_consonant_run,
            'text': text
        }
    
    def test_coordinate_keys(self):
        """Test coordinate-derived keys on all zones."""
        print("\n" + "="*60)
        print("TESTING COORDINATE-DERIVED KEYS")
        print("="*60)
        
        print(f"\nCIA Coordinates: {self.cia_lat}°N, {self.cia_lon}°W")
        print(f"Dedication Date: {self.dedication_date.strftime('%B %d, %Y')}")
        
        best_results = {'HEAD': None, 'MIDDLE': None, 'TAIL': None}
        
        for zone_name, (start, end) in ZONES.items():
            zone_ct = self.ciphertext[start:end]
            zone_best_score = 0
            
            print(f"\n{zone_name} Zone (positions {start}-{end}):")
            
            for key_name, key in self.coord_keys.items():
                if not key:
                    continue
                    
                for method in ['vigenere', 'beaufort', 'autokey']:
                    if method == 'vigenere':
                        pt = self.vigenere_decrypt(zone_ct, key)
                    elif method == 'beaufort':
                        pt = self.beaufort_decrypt(zone_ct, key)
                    else:
                        pt = self.autokey_decrypt(zone_ct, key)
                    
                    score_data = self.score_plaintext(pt)
                    
                    if score_data['score'] > zone_best_score:
                        zone_best_score = score_data['score']
                        best_results[zone_name] = {
                            'key': key_name,
                            'key_value': key,
                            'method': method,
                            'score': score_data['score'],
                            'words': score_data['words'],
                            'text': pt[:30]
                        }
            
            if best_results[zone_name]:
                res = best_results[zone_name]
                print(f"  Best: {res['method']} with {res['key']}")
                print(f"    Key value: {res['key_value'][:20]}...")
                print(f"    Score: {res['score']}")
                print(f"    Words: {res['words']}")
                print(f"    Sample: {res['text']}...")
        
        return best_results
    
    def test_multi_zone_coordinates(self):
        """Test different coordinate components for different zones."""
        print("\n" + "="*60)
        print("MULTI-ZONE COORDINATE TESTING")
        print("="*60)
        
        # Based on ABSCISSA for middle, try logical pairings
        zone_configs = [
            {
                'HEAD': ('ORDINATE', 'vigenere'),      # Y-coordinate
                'MIDDLE': ('ABSCISSA', 'vigenere'),    # X-coordinate (confirmed)
                'TAIL': ('LATITUDE', 'vigenere')       # Geographic
            },
            {
                'HEAD': ('LONGITUDE', 'vigenere'),
                'MIDDLE': ('ABSCISSA', 'vigenere'),
                'TAIL': ('LATITUDE', 'vigenere')
            },
            {
                'HEAD': ('THIRTYEIGHT', 'beaufort'),   # Lat degrees
                'MIDDLE': ('ABSCISSA', 'vigenere'),
                'TAIL': ('SEVENTYSEVEN', 'beaufort')   # Lon degrees
            },
            {
                'HEAD': ('LANGLEY', 'vigenere'),
                'MIDDLE': ('ABSCISSA', 'vigenere'),
                'TAIL': ('VIRGINIA', 'vigenere')
            }
        ]
        
        best_score = 0
        best_config = None
        
        for config in zone_configs:
            full_plaintext = list(self.ciphertext)
            total_score = 0
            
            for zone_name, (start, end) in ZONES.items():
                if zone_name in config:
                    key_name, method = config[zone_name]
                    key = self.coord_keys.get(key_name, key_name)
                    zone_ct = self.ciphertext[start:end]
                    
                    if method == 'vigenere':
                        pt = self.vigenere_decrypt(zone_ct, key)
                    elif method == 'beaufort':
                        pt = self.beaufort_decrypt(zone_ct, key)
                    else:
                        pt = self.autokey_decrypt(zone_ct, key)
                    
                    # Replace in full plaintext
                    for i, c in enumerate(pt):
                        full_plaintext[start + i] = c
                    
                    score_data = self.score_plaintext(pt)
                    total_score += score_data['score']
            
            if total_score > best_score:
                best_score = total_score
                best_config = {
                    'config': config,
                    'score': total_score,
                    'plaintext': ''.join(full_plaintext)
                }
        
        if best_config:
            print(f"\nBest multi-zone configuration (score={best_config['score']}):")
            for zone, (key, method) in best_config['config'].items():
                print(f"  {zone}: {method} with {key}")
            
            print(f"\nResulting plaintext segments:")
            pt = best_config['plaintext']
            print(f"  HEAD: {pt[0:21]}")
            print(f"  MIDDLE: {pt[34:63]}")
            print(f"  TAIL: {pt[74:97]}")
        
        return best_config

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK COORD - COORDINATE-BASED KEY TESTING")
    print("Following ABSCISSA success with geometric/coordinate keys")
    print("="*70)
    
    cipher = CoordinateCipher()
    
    # Test 1: Individual coordinate keys
    coord_results = cipher.test_coordinate_keys()
    
    # Test 2: Multi-zone coordinate combinations
    multi_results = cipher.test_multi_zone_coordinates()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print("\nBest keys by zone:")
    for zone in ['HEAD', 'MIDDLE', 'TAIL']:
        if coord_results[zone]:
            res = coord_results[zone]
            print(f"{zone}: {res['key']} ({res['method']}) - Score: {res['score']}")
            if res['words']:
                print(f"  Words: {res['words']}")
    
    if multi_results and multi_results['score'] > 50:
        print(f"\n🎯 PROMISING MULTI-ZONE RESULT!")
        print(f"Combined score: {multi_results['score']}")
    
    print("\n" + "="*70)
    print("FORK COORD COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()