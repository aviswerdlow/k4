#!/usr/bin/env python3
"""
abscissa_zones.py

Fork ABSC - Deep dive on ABSCISSA finding from Fork ERR.
Testing multi-zone hypothesis with different keys per segment.
"""

from typing import List, Tuple, Dict, Optional
import itertools

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions
ANCHORS = {
    'EAST': (21, 25),
    'NORTHEAST': (25, 34),
    'BERLIN': (63, 69),
    'CLOCK': (69, 74)
}

# Zone definitions based on anchors
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

class MultiZoneCipher:
    """Multi-zone cipher with different keys/methods per segment."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Key variations to test
        self.key_families = {
            'ABSCISSA': ['ABSCISSA', 'ABSCISSAE', 'ABSCISSE', 'ABCISSA'],
            'ORDINATE': ['ORDINATE', 'ORDINATES', 'COORDINATE', 'YARD'],
            'KRYPTOS': ['KRYPTOS', 'PALIMPSEST', 'KRYPTOSABSCISSA', 'KRYPTOSYARD'],
            'BERLIN': ['BERLIN', 'CLOCK', 'BERLINCLOCK', 'NORTHEAST'],
            'GEOMETRIC': ['ANGLE', 'DEGREE', 'RADIAN', 'TANGENT', 'COSINE'],
            'SURVEYING': ['BEARING', 'AZIMUTH', 'TRANSIT', 'THEODOLITE', 'COMPASS']
        }
    
    def vigenere_decrypt(self, text: str, key: str, offset: int = 0) -> str:
        """Vigenère decryption with optional offset."""
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
        """Beaufort decryption with optional offset."""
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
    
    def variant_beaufort_decrypt(self, text: str, key: str, offset: int = 0) -> str:
        """Variant Beaufort decryption."""
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[(i + offset) % key_len])
            p_val = (c_val + k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def extract_zones(self) -> Dict[str, str]:
        """Extract zone segments from ciphertext."""
        zones = {}
        for zone_name, (start, end) in ZONES.items():
            zones[zone_name] = self.ciphertext[start:end]
        return zones
    
    def decrypt_multi_zone(self, zone_keys: Dict[str, Tuple[str, str, int]]) -> str:
        """
        Decrypt using different keys/methods per zone.
        
        Args:
            zone_keys: Dict of zone_name -> (key, method, offset)
                      method can be 'vigenere', 'beaufort', 'variant'
        """
        plaintext = list(self.ciphertext)
        
        for zone_name, (start, end) in ZONES.items():
            if zone_name not in zone_keys:
                continue
            
            key, method, offset = zone_keys[zone_name]
            zone_ct = self.ciphertext[start:end]
            
            if method == 'vigenere':
                zone_pt = self.vigenere_decrypt(zone_ct, key, offset)
            elif method == 'beaufort':
                zone_pt = self.beaufort_decrypt(zone_ct, key, offset)
            elif method == 'variant':
                zone_pt = self.variant_beaufort_decrypt(zone_ct, key, offset)
            else:
                continue
            
            # Replace zone in plaintext
            for i, c in enumerate(zone_pt):
                plaintext[start + i] = c
        
        return ''.join(plaintext)
    
    def check_anchors(self, plaintext: str) -> int:
        """Check how many anchors are preserved."""
        count = 0
        expected = {
            21: 'EAST',
            25: 'NORTHEAST',
            63: 'BERLIN',
            69: 'CLOCK'
        }
        
        for pos, word in expected.items():
            if plaintext[pos:pos+len(word)] == word:
                count += 1
        
        return count
    
    def score_plaintext(self, plaintext: str) -> Dict:
        """Score plaintext quality."""
        # Check vowel ratio
        vowels = sum(1 for c in plaintext if c in 'AEIOU')
        vowel_ratio = vowels / len(plaintext) if len(plaintext) > 0 else 0
        
        # Check for common words
        words_found = []
        common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'THAT', 
                       'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD', 'THERE', 'THEIR',
                       'WHAT', 'BEEN', 'THIS', 'OTHER', 'WERE', 'WHICH', 'AFTER',
                       'HEAT', 'EAST', 'NORTH', 'SOUTH', 'WEST', 'TIME', 'CLOCK']
        
        for word in common_words:
            if word in plaintext:
                words_found.append(word)
        
        # Check consonant runs
        max_consonant_run = 0
        current_run = 0
        for c in plaintext:
            if c not in 'AEIOU':
                current_run += 1
                max_consonant_run = max(max_consonant_run, current_run)
            else:
                current_run = 0
        
        # Calculate score
        score = 0
        score += len(words_found) * 10
        if 0.35 <= vowel_ratio <= 0.45:
            score += 5
        if max_consonant_run <= 4:
            score += 5
        
        anchors = self.check_anchors(plaintext)
        score += anchors * 20
        
        return {
            'score': score,
            'vowel_ratio': round(vowel_ratio, 3),
            'words': words_found,
            'max_consonants': max_consonant_run,
            'anchors': anchors,
            'plaintext': plaintext
        }
    
    def test_abscissa_variations(self):
        """Test variations of ABSCISSA on middle segment."""
        print("\n" + "="*60)
        print("TESTING ABSCISSA VARIATIONS ON MIDDLE SEGMENT")
        print("="*60)
        
        zones = self.extract_zones()
        middle_ct = zones['MIDDLE']
        
        results = []
        
        # Test all ABSCISSA-like keys
        for key in self.key_families['ABSCISSA'] + self.key_families['ORDINATE']:
            for method in ['vigenere', 'beaufort', 'variant']:
                for offset in range(0, min(10, len(key))):
                    if method == 'vigenere':
                        pt = self.vigenere_decrypt(middle_ct, key, offset)
                    elif method == 'beaufort':
                        pt = self.beaufort_decrypt(middle_ct, key, offset)
                    else:
                        pt = self.variant_beaufort_decrypt(middle_ct, key, offset)
                    
                    # Score this segment
                    score_data = self.score_plaintext(pt)
                    
                    if score_data['score'] > 10 or len(score_data['words']) > 0:
                        results.append({
                            'key': key,
                            'method': method,
                            'offset': offset,
                            'score': score_data['score'],
                            'words': score_data['words'],
                            'sample': pt[:30]
                        })
        
        # Sort and display results
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\nTop 5 results for middle segment:")
        for i, res in enumerate(results[:5]):
            print(f"\n{i+1}. {res['method']} with {res['key']} (offset={res['offset']})")
            print(f"   Score: {res['score']}")
            print(f"   Words: {res['words']}")
            print(f"   Sample: {res['sample']}...")
        
        return results
    
    def test_multi_zone_combinations(self):
        """Test different key combinations across zones."""
        print("\n" + "="*60)
        print("TESTING MULTI-ZONE COMBINATIONS")
        print("="*60)
        
        best_results = []
        
        # Based on ABSCISSA finding, use it for middle
        middle_configs = [
            ('ABSCISSA', 'vigenere', 0),
            ('ABSCISSAE', 'vigenere', 0),
            ('ORDINATE', 'vigenere', 0)
        ]
        
        # Try different keys for head and tail
        head_keys = ['KRYPTOS', 'PALIMPSEST', 'YARD', 'BERLIN']
        tail_keys = ['CLOCK', 'BERLIN', 'KRYPTOS', 'NORTHEAST']
        
        for middle_cfg in middle_configs:
            for h_key in head_keys:
                for t_key in tail_keys:
                    for h_method in ['vigenere', 'beaufort']:
                        for t_method in ['vigenere', 'beaufort']:
                            zone_keys = {
                                'HEAD': (h_key, h_method, 0),
                                'MIDDLE': middle_cfg,
                                'TAIL': (t_key, t_method, 0)
                            }
                            
                            plaintext = self.decrypt_multi_zone(zone_keys)
                            score_data = self.score_plaintext(plaintext)
                            
                            if score_data['anchors'] > 0 or score_data['score'] > 30:
                                best_results.append({
                                    'config': zone_keys,
                                    'score': score_data['score'],
                                    'anchors': score_data['anchors'],
                                    'words': score_data['words'],
                                    'plaintext': plaintext
                                })
        
        # Sort by score
        best_results.sort(key=lambda x: (x['anchors'], x['score']), reverse=True)
        
        print(f"\nTested {len(middle_configs) * len(head_keys) * len(tail_keys) * 4} combinations")
        
        if best_results:
            print(f"\nTop 3 multi-zone results:")
            for i, res in enumerate(best_results[:3]):
                print(f"\n{i+1}. Score: {res['score']}, Anchors: {res['anchors']}")
                print(f"   Configuration:")
                for zone, (key, method, offset) in res['config'].items():
                    print(f"     {zone}: {method} with {key}")
                print(f"   Words found: {res['words']}")
                print(f"   Head: {res['plaintext'][:21]}")
                print(f"   Middle: {res['plaintext'][34:63]}")
                print(f"   Tail: {res['plaintext'][74:]}")
        else:
            print("No promising multi-zone combinations found")
        
        return best_results
    
    def test_geometric_keys(self):
        """Test geometric/mathematical keys based on sculpture context."""
        print("\n" + "="*60)
        print("TESTING GEOMETRIC/SURVEYING KEYS")
        print("="*60)
        
        zones = self.extract_zones()
        
        all_keys = []
        for family_keys in [self.key_families['GEOMETRIC'], self.key_families['SURVEYING']]:
            all_keys.extend(family_keys)
        
        results = []
        
        for zone_name, zone_ct in zones.items():
            for key in all_keys:
                for method in ['vigenere', 'beaufort']:
                    pt = self.vigenere_decrypt(zone_ct, key) if method == 'vigenere' else self.beaufort_decrypt(zone_ct, key)
                    
                    score_data = self.score_plaintext(pt)
                    
                    if score_data['score'] > 15 or len(score_data['words']) > 0:
                        results.append({
                            'zone': zone_name,
                            'key': key,
                            'method': method,
                            'score': score_data['score'],
                            'words': score_data['words'],
                            'sample': pt[:30]
                        })
        
        # Group by zone
        by_zone = {}
        for res in results:
            zone = res['zone']
            if zone not in by_zone:
                by_zone[zone] = []
            by_zone[zone].append(res)
        
        for zone in ['HEAD', 'MIDDLE', 'TAIL']:
            if zone in by_zone:
                by_zone[zone].sort(key=lambda x: x['score'], reverse=True)
                print(f"\nBest geometric/surveying key for {zone}:")
                if by_zone[zone]:
                    best = by_zone[zone][0]
                    print(f"  {best['method']} with {best['key']}: score={best['score']}")
                    print(f"  Words: {best['words']}")
                    print(f"  Sample: {best['sample']}...")
        
        return results

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK ABSC - DEEP ABSCISSA INVESTIGATION")
    print("Following up on Fork ERR finding: Middle segment + ABSCISSA")
    print("="*70)
    
    cipher = MultiZoneCipher()
    
    # Test 1: ABSCISSA variations
    absc_results = cipher.test_abscissa_variations()
    
    # Test 2: Multi-zone combinations
    multi_results = cipher.test_multi_zone_combinations()
    
    # Test 3: Geometric/surveying keys
    geo_results = cipher.test_geometric_keys()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if multi_results and multi_results[0]['anchors'] > 0:
        print(f"\n🎯 ANCHOR-PRESERVING SOLUTION FOUND!")
        print(f"Anchors preserved: {multi_results[0]['anchors']}")
        print(f"Configuration: {multi_results[0]['config']}")
    else:
        print(f"\nNo anchor-preserving solutions found")
        print(f"Best score achieved: {multi_results[0]['score'] if multi_results else 0}")
        
        if absc_results:
            print(f"\nMost promising middle segment key: {absc_results[0]['key']}")
            print(f"Method: {absc_results[0]['method']}")
            print(f"Words found: {absc_results[0]['words']}")
    
    print("\n" + "="*70)
    print("FORK ABSC COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()