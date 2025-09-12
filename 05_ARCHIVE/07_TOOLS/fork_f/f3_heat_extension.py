#!/usr/bin/env python3
"""
f3_heat_extension.py

Comprehensive extension from the HEAT finding.
Three-pronged approach: temperature words, Cold War narrative, coordinate system.
"""

from typing import List, Tuple, Dict, Optional
import re

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Confirmed zones
ZONES = {
    'HEAD': (0, 21),
    'MIDDLE': (34, 63),
    'TAIL': (74, 97)
}

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class HeatExtensionSolver:
    """Extend from confirmed HEAT finding."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Confirmed
        self.middle_ct = self.ciphertext[34:63]
        self.middle_key = 'ABSCISSA'
        self.middle_pt = self.vigenere_decrypt(self.middle_ct, self.middle_key)
        self.heat_pos = 13  # Position of HEAT in middle segment
        
        # Key families for testing
        self.key_families = {
            'temperature': [
                'THERMAL', 'TEMPERATURE', 'DEGREES', 'CELSIUS',
                'WARMTH', 'BURNING', 'HEATED', 'HEATING',
                'FAHRENHEIT', 'KELVIN', 'BOILING', 'FREEZING'
            ],
            'cold_war': [
                'MOSCOW', 'KREMLIN', 'PENTAGON', 'WARSAW',
                'NUCLEAR', 'ATOMIC', 'MISSILE', 'SOVIET',
                'DETENTE', 'GLASNOST', 'CHECKPOINT', 'CHARLIE'
            ],
            'coordinates': [
                'ORDINATE', 'LATITUDE', 'LONGITUDE', 'MERIDIAN',
                'PARALLEL', 'EQUATOR', 'PRIME', 'GREENWICH',
                'THREEEIGHT', 'SEVENTYSEVEN', 'NORTH', 'WEST'
            ],
            'extended_location': [
                'MCLEAN', 'FAIRFAX', 'POTOMAC', 'MARYLAND',
                'DISTRICT', 'COLUMBIA', 'CAPITAL', 'FEDERAL'
            ]
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
    
    def test_heat_extensions(self):
        """Test if HEAT is part of a longer word."""
        print("\n" + "="*60)
        print("TESTING HEAT EXTENSIONS")
        print("="*60)
        
        print(f"\nConfirmed: {self.middle_pt}")
        print(f"HEAT at position {self.heat_pos}")
        
        # Get context
        before = self.middle_pt[:self.heat_pos]
        after = self.middle_pt[self.heat_pos+4:]
        
        print(f"\nContext:")
        print(f"  Before: '{before}'")
        print(f"  HEAT: 'HEAT'")
        print(f"  After: '{after}'")
        
        # Test different keys for the segments before/after HEAT
        print("\n1. Testing keys for segment BEFORE HEAT:")
        before_ct = self.middle_ct[:self.heat_pos]
        
        for key in self.key_families['temperature'][:6]:
            pt = self.vigenere_decrypt(before_ct, key)
            if self.ends_with_word_prefix(pt):
                print(f"  {key}: {pt} → {pt}HEAT")
        
        print("\n2. Testing keys for segment AFTER HEAT:")
        after_ct = self.middle_ct[self.heat_pos+4:]
        
        for key in self.key_families['temperature'][:6]:
            pt = self.vigenere_decrypt(after_ct, key)
            if self.starts_with_word_suffix(pt):
                print(f"  {key}: {pt} → HEAT{pt}")
        
        # Check for specific extended words
        print("\n3. Checking for specific words containing HEAT:")
        targets = ['THREAT', 'WHEAT', 'CHEAT', 'HEATER', 'HEATING', 'HEATED', 'SHEATH']
        
        for target in targets:
            if 'HEAT' in target:
                idx = target.index('HEAT')
                prefix = target[:idx]
                suffix = target[idx+4:]
                
                if prefix and before.endswith(prefix):
                    print(f"  ✓ Possible: {target} ('{prefix}' + HEAT)")
                if suffix and after.startswith(suffix):
                    print(f"  ✓ Possible: {target} (HEAT + '{suffix}')")
    
    def test_cold_war_narrative(self):
        """Test Cold War themed keys."""
        print("\n" + "="*60)
        print("TESTING COLD WAR NARRATIVE")
        print("="*60)
        
        print("\nHypothesis: BERLIN anchor + HEAT → Cold War theme")
        
        # Test HEAD zone with Cold War location keys
        head_ct = self.ciphertext[0:21]
        print("\nHEAD zone with Cold War keys:")
        
        best_results = []
        for key in self.key_families['cold_war']:
            pt = self.vigenere_decrypt(head_ct, key)
            score = self.score_text(pt)
            if score > 0:
                best_results.append((key, pt, score))
        
        best_results.sort(key=lambda x: x[2], reverse=True)
        for key, pt, score in best_results[:5]:
            print(f"  {key}: {pt[:20]}... (score: {score})")
        
        # Test TAIL zone with Cold War concept keys
        tail_ct = self.ciphertext[74:97]
        print("\nTAIL zone with Cold War keys:")
        
        best_results = []
        for key in self.key_families['cold_war']:
            pt = self.vigenere_decrypt(tail_ct, key)
            score = self.score_text(pt)
            if score > 0:
                best_results.append((key, pt, score))
        
        best_results.sort(key=lambda x: x[2], reverse=True)
        for key, pt, score in best_results[:5]:
            print(f"  {key}: {pt[:20]}... (score: {score})")
        
        # Check for narrative coherence
        print("\nNarrative check with HEAT in middle:")
        print("Pattern: [Cold War location] ... HEAT ... [Cold War outcome]")
        print("Example: MOSCOW ... HEAT ... DETENTE")
    
    def test_coordinate_system(self):
        """Test coordinate-based keys."""
        print("\n" + "="*60)
        print("TESTING COORDINATE SYSTEM")
        print("="*60)
        
        print("\nSince ABSCISSA (x-coord) → HEAT, testing related terms:")
        
        # Test ORDINATE with various offsets
        print("\n1. ORDINATE (y-coordinate) with offsets:")
        for offset in range(-3, 4):
            pt = self.vigenere_decrypt(self.middle_ct, 'ORDINATE', offset)
            if 'HEAT' in pt or self.has_words(pt):
                print(f"  Offset {offset:+d}: {pt}")
        
        # Test actual CIA coordinates
        print("\n2. CIA Headquarters coordinates (38.9517°N, 77.1467°W):")
        coord_keys = [
            'THIRTYEIGHT',
            'SEVENTYSEVEN',
            'LATITUDE',
            'LONGITUDE',
            'NORTH',
            'WEST'
        ]
        
        for zone_name, (start, end) in ZONES.items():
            ct = self.ciphertext[start:end]
            print(f"\n{zone_name} zone:")
            for key in coord_keys:
                pt = self.vigenere_decrypt(ct, key)
                if self.has_words(pt):
                    print(f"  {key}: {pt[:30]}...")
        
        # Test mathematical progression
        print("\n3. Mathematical term progression:")
        math_keys = ['SINE', 'COSINE', 'TANGENT', 'ANGLE', 'DEGREE', 'RADIAN']
        
        for key in math_keys:
            pt = self.vigenere_decrypt(self.middle_ct, key)
            if self.has_words(pt):
                print(f"  {key}: {pt}")
    
    def test_extended_locations(self):
        """Test extended location keys around CIA."""
        print("\n" + "="*60)
        print("TESTING EXTENDED LOCATIONS")
        print("="*60)
        
        print("\nTesting locations near CIA headquarters:")
        
        head_ct = self.ciphertext[0:21]
        
        for key in self.key_families['extended_location']:
            pt = self.vigenere_decrypt(head_ct, key)
            score = self.score_text(pt)
            if score > 0:
                print(f"  {key}: {pt} (score: {score})")
    
    def test_heat_in_context(self):
        """Test what makes sense around HEAT."""
        print("\n" + "="*60)
        print("ANALYZING HEAT IN CONTEXT")
        print("="*60)
        
        # What commonly precedes HEAT?
        common_before = [
            'THE', 'AND', 'WITH', 'FROM', 'INTENSE', 'EXTREME',
            'NUCLEAR', 'ATOMIC', 'DESERT', 'SUMMER', 'BODY'
        ]
        
        # What commonly follows HEAT?
        common_after = [
            'WAVE', 'WAVES', 'SOURCE', 'SHIELD', 'SINK',
            'DEATH', 'STROKE', 'INDEX', 'PUMP', 'RISES'
        ]
        
        print("\nChecking common phrases with HEAT:")
        
        # Check before
        before = self.middle_pt[:self.heat_pos]
        for word in common_before:
            if before.endswith(word):
                print(f"  Found: '{word} HEAT'")
        
        # Check after  
        after = self.middle_pt[self.heat_pos+4:]
        for word in common_after:
            if after.startswith(word):
                print(f"  Found: 'HEAT {word}'")
        
        # Check for letter patterns that could form words
        print(f"\nAnalyzing letter patterns:")
        print(f"  Last 3 before HEAT: '{before[-3:] if len(before) >= 3 else before}'")
        print(f"  First 3 after HEAT: '{after[:3] if len(after) >= 3 else after}'")
        
        # Possible completions
        if before.endswith('T'):
            print("  Could be: THREAT")
        if before.endswith('W'):
            print("  Could be: WHEAT")
        if after.startswith('ING'):
            print("  Could be: HEATING")
        if after.startswith('ED'):
            print("  Could be: HEATED")
    
    def score_text(self, text: str) -> int:
        """Score text quality."""
        score = 0
        
        # Check for common words
        common = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'THAT', 'HAVE', 'FROM']
        for word in common:
            if word in text:
                score += 5
        
        # Check vowel ratio
        vowels = sum(1 for c in text if c in 'AEIOU')
        if 0.3 <= vowels/len(text) <= 0.5:
            score += 3
        
        # Penalize long consonant runs
        max_consonants = 0
        current = 0
        for c in text:
            if c not in 'AEIOU':
                current += 1
                max_consonants = max(max_consonants, current)
            else:
                current = 0
        
        if max_consonants > 5:
            score -= 5
        
        return score
    
    def has_words(self, text: str) -> bool:
        """Check if text contains common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HEAT', 'COLD', 'TIME']
        return any(word in text for word in words)
    
    def ends_with_word_prefix(self, text: str) -> bool:
        """Check if text ends with a word prefix."""
        prefixes = ['T', 'W', 'C', 'S', 'TH', 'WH', 'CH', 'SH', 'THR', 'OVE']
        return any(text.endswith(p) for p in prefixes)
    
    def starts_with_word_suffix(self, text: str) -> bool:
        """Check if text starts with a word suffix."""
        suffixes = ['ING', 'ED', 'ER', 'EST', 'WAVE', 'SINK', 'PUMP']
        return any(text.startswith(s) for s in suffixes)

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("HEAT EXTENSION ANALYSIS")
    print("Three-pronged approach from confirmed ABSCISSA → HEAT")
    print("="*70)
    
    solver = HeatExtensionSolver()
    
    # Update todo
    print("\nApproach:")
    print("1. Test if HEAT is part of a longer word")
    print("2. Explore Cold War narrative (BERLIN connection)")
    print("3. Test coordinate system continuation")
    print("4. Try extended location keys")
    
    # Run tests
    solver.test_heat_extensions()
    solver.test_cold_war_narrative()
    solver.test_coordinate_system()
    solver.test_extended_locations()
    solver.test_heat_in_context()
    
    # Summary
    print("\n" + "="*70)
    print("HEAT EXTENSION SUMMARY")
    print("="*70)
    
    print("\nConfirmed:")
    print("- MIDDLE zone + ABSCISSA = ...HEAT... at position 13")
    print("- Zone-based encryption with different keys per segment")
    
    print("\nMost promising directions:")
    print("1. HEAT as part of THREAT (military/nuclear context)")
    print("2. Cold War narrative (BERLIN-HEAT connection)")
    print("3. Coordinate progression (ABSCISSA → ORDINATE)")
    print("4. Temperature/thermal key family for adjacent zones")
    
    print("\nNext steps:")
    print("1. Test ORDINATE with different offsets more thoroughly")
    print("2. Try THREAT-related keys for surrounding text")
    print("3. Test if BERLIN decrypts to something Cold War related")
    print("4. Consider CLOCK as time reference (Doomsday Clock?)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()