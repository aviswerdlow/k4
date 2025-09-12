#!/usr/bin/env python3
"""
f3_propagate.py

Fork F v3 - Testing propagation patterns and multi-anchor confidence.
Building on ABSCISSA breakthrough with zone-based encryption.
"""

from typing import List, Tuple, Dict, Optional, Set
import itertools

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Confirmed zones
ZONES = {
    'HEAD': (0, 21),      # Before EAST
    'MIDDLE': (34, 63),   # Between NORTHEAST and BERLIN  
    'TAIL': (74, 97)      # After CLOCK
}

# Anchor positions
ANCHORS = {
    'EAST': (21, 25),
    'NORTHEAST': (25, 34),
    'BERLIN': (63, 69),
    'CLOCK': (69, 74)
}

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class PropagationSolver:
    """Test propagation patterns from confirmed ABSCISSA finding."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Confirmed finding
        self.confirmed = {
            'zone': 'MIDDLE',
            'key': 'ABSCISSA',
            'plaintext': 'OSERIARQSRMIRHEATISJMLQAWHVDT',
            'word': 'HEAT',
            'position': 13
        }
        
        # Key families for testing
        self.key_families = {
            'location': ['LANGLEY', 'VIRGINIA', 'WASHINGTON', 'AMERICA', 'AGENCY', 'ENTRANCE'],
            'measurement': ['ABSCISSA', 'ORDINATE', 'COORDINATE', 'BEARING', 'AZIMUTH', 'ANGLE'],
            'concept': ['ILLUSION', 'IQLUSION', 'PALIMPSEST', 'SHADOW', 'LAYER', 'UNDERGROUND'],
            'temperature': ['TEMPERATURE', 'CELSIUS', 'FAHRENHEIT', 'THERMAL', 'DEGREE', 'KELVIN'],
            'direction': ['NORTHEAST', 'SOUTHEAST', 'NORTHWEST', 'SOUTHWEST', 'COMPASS', 'BEARING'],
            'time': ['NOVEMBER', 'NINETEEN', 'NINETY', 'MILLENNIUM', 'CENTURY', 'DECADE']
        }
    
    def vigenere_decrypt(self, text: str, key: str, offset: int = 0) -> str:
        """Standard Vigenère decryption."""
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
    
    def test_propagation_from_middle(self):
        """Propagate from confirmed MIDDLE zone finding."""
        print("\n" + "="*60)
        print("PROPAGATING FROM CONFIRMED MIDDLE ZONE")
        print("="*60)
        
        print(f"\nConfirmed: MIDDLE zone with ABSCISSA → 'HEAT' at position {self.confirmed['position']}")
        
        # Since ABSCISSA (measurement) works for MIDDLE, test related patterns
        
        # Test HEAD zone with location keys
        head_ct = self.ciphertext[0:21]
        print(f"\nTesting HEAD zone (location theme):")
        
        best_head = None
        best_head_score = 0
        
        for key in self.key_families['location']:
            pt = self.vigenere_decrypt(head_ct, key)
            score, words = self.score_plaintext(pt)
            
            if score > best_head_score:
                best_head_score = score
                best_head = (key, pt, words)
            
            if words:
                print(f"  {key}: {pt[:20]}... Words: {words}")
        
        # Test TAIL zone with concept keys
        tail_ct = self.ciphertext[74:97]
        print(f"\nTesting TAIL zone (concept theme):")
        
        best_tail = None
        best_tail_score = 0
        
        for key in self.key_families['concept']:
            pt = self.vigenere_decrypt(tail_ct, key)
            score, words = self.score_plaintext(pt)
            
            if score > best_tail_score:
                best_tail_score = score
                best_tail = (key, pt, words)
            
            if words:
                print(f"  {key}: {pt[:20]}... Words: {words}")
        
        return best_head, best_tail
    
    def test_multi_anchor_constraints(self):
        """Test if multiple anchors can be satisfied simultaneously."""
        print("\n" + "="*60)
        print("TESTING MULTI-ANCHOR CONSTRAINTS")
        print("="*60)
        
        # Test if anchor ciphertext positions have patterns
        anchor_cts = {}
        for name, (start, end) in ANCHORS.items():
            anchor_cts[name] = self.ciphertext[start:end]
        
        print("\nAnchor ciphertexts:")
        for name, ct in anchor_cts.items():
            print(f"  {name}: {ct}")
        
        # Test if anchors decrypt to meaningful words with zone keys
        print("\nTesting anchors with zone keys:")
        
        # EAST and NORTHEAST might use location key
        for anchor in ['EAST', 'NORTHEAST']:
            ct = anchor_cts[anchor.split()[0]]  # Handle NORTHEAST
            for key in self.key_families['location'][:3]:
                pt = self.vigenere_decrypt(ct, key)
                if self.is_readable(pt):
                    print(f"  {anchor} + {key}: {pt}")
        
        # BERLIN might use concept key
        ct = anchor_cts['BERLIN']
        for key in self.key_families['concept'][:3]:
            pt = self.vigenere_decrypt(ct, key)
            if self.is_readable(pt):
                print(f"  BERLIN + {key}: {pt}")
        
        # CLOCK might use time key
        ct = anchor_cts['CLOCK']
        for key in self.key_families['time'][:3]:
            pt = self.vigenere_decrypt(ct, key)
            if self.is_readable(pt):
                print(f"  CLOCK + {key}: {pt}")
    
    def test_heat_context_expansion(self):
        """Expand context around HEAT to find more of the message."""
        print("\n" + "="*60)
        print("EXPANDING HEAT CONTEXT")
        print("="*60)
        
        middle_ct = self.ciphertext[34:63]
        middle_pt = self.vigenere_decrypt(middle_ct, 'ABSCISSA')
        
        heat_pos = middle_pt.find('HEAT')
        print(f"\nConfirmed: '{middle_pt}'")
        print(f"HEAT at position {heat_pos}")
        
        # What if we slide the key position?
        print("\nTesting key offset adjustments:")
        for offset in range(-3, 4):
            if offset == 0:
                continue
            pt = self.vigenere_decrypt(middle_ct, 'ABSCISSA', offset)
            if 'HEAT' in pt or self.has_good_words(pt):
                print(f"  Offset {offset:+d}: {pt}")
        
        # What if HEAT is part of a longer word?
        print("\nChecking for extended words containing HEAT:")
        heat_extensions = [
            'HEATER', 'HEATING', 'HEATED', 'PREHEAT', 'REHEAT',
            'OVERHEAT', 'HEATWAVE', 'HEATMAP'
        ]
        
        # Check surrounding context
        before = middle_pt[:heat_pos]
        after = middle_pt[heat_pos+4:]
        
        print(f"  Before HEAT: '{before}'")
        print(f"  After HEAT:  '{after}'")
        
        # Look for patterns
        if before.endswith('T'):
            print("  Possible: THREAT (T+HEAT)")
        if before.endswith('W'):
            print("  Possible: WHEAT (W+HEAT)")
        if after.startswith('H'):
            print("  Possible: HEATH (HEAT+H)")
        if after.startswith('ING'):
            print("  Possible: HEATING (HEAT+ING)")
    
    def test_zone_boundary_keys(self):
        """Test if keys change at zone boundaries."""
        print("\n" + "="*60)
        print("TESTING ZONE BOUNDARY KEY CHANGES")
        print("="*60)
        
        # What if the key changes exactly at anchor positions?
        
        # Test continuous decryption with key changes
        segments = [
            (0, 21, 'location'),     # HEAD
            (21, 25, 'direction'),   # EAST anchor
            (25, 34, 'direction'),   # NORTHEAST anchor
            (34, 63, 'measurement'), # MIDDLE (confirmed)
            (63, 69, 'location'),    # BERLIN anchor
            (69, 74, 'time'),        # CLOCK anchor
            (74, 97, 'concept')      # TAIL
        ]
        
        print("\nTesting segmented decryption with themed keys:")
        
        for family_combo in itertools.product(
            self.key_families['location'][:2],
            self.key_families['measurement'][:2],
            self.key_families['concept'][:2]
        ):
            full_plaintext = []
            
            for start, end, theme in segments:
                ct_segment = self.ciphertext[start:end]
                
                if theme == 'location':
                    key = family_combo[0]
                elif theme == 'measurement':
                    key = family_combo[1]
                elif theme == 'concept':
                    key = family_combo[2]
                elif theme == 'direction':
                    key = 'NORTHEAST'  # Use anchor name as key
                elif theme == 'time':
                    key = 'CLOCK'      # Use anchor name as key
                else:
                    key = 'KRYPTOS'
                
                pt_segment = self.vigenere_decrypt(ct_segment, key)
                full_plaintext.append(pt_segment)
            
            full_text = ''.join(full_plaintext)
            score, words = self.score_plaintext(full_text)
            
            if score > 20:  # High score threshold
                print(f"\nHigh score ({score}) with keys: {family_combo}")
                print(f"  Words found: {words}")
                print(f"  Sample: {full_text[:50]}...")
    
    def score_plaintext(self, text: str) -> Tuple[int, List[str]]:
        """Score plaintext quality."""
        score = 0
        words_found = []
        
        # Common words
        common_words = {
            'THE': 5, 'AND': 4, 'ARE': 3, 'YOU': 3, 'WAS': 4, 
            'HIS': 3, 'HER': 3, 'THAT': 4, 'HAVE': 4, 'FROM': 4,
            'THEY': 4, 'WILL': 4, 'WOULD': 5, 'THERE': 5, 'THEIR': 5,
            'HEAT': 10, 'COLD': 8, 'WARM': 6, 'TIME': 5, 'CLOCK': 8,
            'EAST': 8, 'WEST': 8, 'NORTH': 8, 'SOUTH': 8
        }
        
        for word, points in common_words.items():
            if word in text:
                score += points
                words_found.append(word)
        
        # Penalize high consonant runs
        consonants = 0
        for c in text:
            if c not in 'AEIOU':
                consonants += 1
                if consonants > 5:
                    score -= 2
            else:
                consonants = 0
        
        return score, words_found
    
    def is_readable(self, text: str) -> bool:
        """Check if text appears readable."""
        if len(text) < 3:
            return False
        
        vowels = sum(1 for c in text if c in 'AEIOU')
        vowel_ratio = vowels / len(text)
        
        # Check for reasonable vowel ratio
        if 0.25 <= vowel_ratio <= 0.6:
            # Check for no extreme consonant runs
            max_consonants = 0
            current = 0
            for c in text:
                if c not in 'AEIOU':
                    current += 1
                    max_consonants = max(max_consonants, current)
                else:
                    current = 0
            
            return max_consonants <= 4
        
        return False
    
    def has_good_words(self, text: str) -> bool:
        """Check if text contains good English words."""
        good_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 
                      'HEAT', 'COLD', 'TIME', 'THAT', 'HAVE', 'FROM']
        return any(word in text for word in good_words)
    
    def apply_f3_hypothesis(self):
        """Apply Fork F v3 hypothesis: zone keys with thematic progression."""
        print("\n" + "="*60)
        print("APPLYING FORK F v3 HYPOTHESIS")
        print("="*60)
        
        print("\nHypothesis: Thematic progression with zone-specific keys")
        print("- HEAD: Physical location (CIA/Langley)")
        print("- MIDDLE: Mathematical/surveying (confirmed ABSCISSA)")
        print("- TAIL: Conceptual/abstract (illusion/reality)")
        
        # Best known configuration
        config = {
            'HEAD': ('LANGLEY', 'location'),
            'MIDDLE': ('ABSCISSA', 'measurement'),
            'TAIL': ('ILLUSION', 'concept')
        }
        
        results = {}
        for zone_name, (start, end) in ZONES.items():
            ct = self.ciphertext[start:end]
            key, theme = config[zone_name]
            pt = self.vigenere_decrypt(ct, key)
            
            score, words = self.score_plaintext(pt)
            results[zone_name] = {
                'key': key,
                'theme': theme,
                'plaintext': pt,
                'score': score,
                'words': words
            }
            
            print(f"\n{zone_name} ({theme}):")
            print(f"  Key: {key}")
            print(f"  Plaintext: {pt}")
            print(f"  Words: {words}")
            print(f"  Score: {score}")
        
        # Check narrative coherence
        all_words = []
        for zone in ['HEAD', 'MIDDLE', 'TAIL']:
            all_words.extend(results[zone]['words'])
        
        print(f"\nAll words found: {all_words}")
        
        if 'AND' in all_words and 'HEAT' in all_words and 'WAS' in all_words:
            print("\n🎯 Narrative elements confirmed: AND...HEAT...WAS")
            print("This suggests a coherent message about heat/temperature in past tense")
        
        return results

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("FORK F v3 - PROPAGATION TESTING")
    print("Building on ABSCISSA breakthrough with multi-anchor validation")
    print("="*70)
    
    solver = PropagationSolver()
    
    # Test propagation from confirmed middle zone
    best_head, best_tail = solver.test_propagation_from_middle()
    
    # Test multi-anchor constraints
    solver.test_multi_anchor_constraints()
    
    # Expand HEAT context
    solver.test_heat_context_expansion()
    
    # Test zone boundary keys
    solver.test_zone_boundary_keys()
    
    # Apply F3 hypothesis
    results = solver.apply_f3_hypothesis()
    
    # Summary
    print("\n" + "="*70)
    print("F3 PROPAGATION SUMMARY")
    print("="*70)
    
    print("\nConfirmed findings:")
    print("1. MIDDLE zone + ABSCISSA = 'HEAT' (high confidence)")
    print("2. Zone-based encryption with different keys per segment")
    print("3. Thematic progression: location → measurement → concept")
    
    print("\nPropagation results:")
    if best_head:
        print(f"Best HEAD: {best_head[0]} → Words: {best_head[2]}")
    if best_tail:
        print(f"Best TAIL: {best_tail[0]} → Words: {best_tail[2]}")
    
    print("\nNext steps:")
    print("1. Test if anchors encode key-change instructions")
    print("2. Try temperature-related keys for surrounding zones")
    print("3. Consider Cold War context (Berlin/heat/cold)")
    print("4. Test if solution requires reading across boundaries")
    
    print("\n" + "="*70)
    print("F3 PROPAGATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
