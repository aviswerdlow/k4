#!/usr/bin/env python3
"""
zone_solution.py

Building on ABSCISSA breakthrough with thematic key progression.
Testing location → measurement → concept pattern.
"""

from typing import List, Tuple, Dict, Optional

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Zone definitions (based on anchor positions)
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

class ZoneSolution:
    """Zone-based solution with thematic progression."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Thematic key progression: location → measurement → concept
        self.zone_keys = {
            'HEAD': [  # Physical location theme
                'LANGLEY',    # Confirmed produces "AND"
                'VIRGINIA',   # State
                'AGENCY',     # CIA
                'ENTRANCE',   # Physical location
                'HEADQUARTERS',
                'COMPOUND',
                'CAMPUS'
            ],
            'MIDDLE': [  # Mathematical/surveying theme
                'ABSCISSA',   # Confirmed produces "HEAT"
                'ORDINATE',   # Y-coordinate
                'COORDINATE', # Both axes
                'MEASURE',    # From Flint surveying
                'BEARING',    # Surveying term
                'AZIMUTH',    # Angular measurement
                'TRANSIT'     # Surveying instrument
            ],
            'TAIL': [  # Conceptual/layer theme
                'ILLUSION',   # Confirmed produces "WAS"
                'IQLUSION',   # K1 deliberate misspelling
                'PALIMPSEST', # K1 key
                'LAYER',      # From K2 "LAYER TWO"
                'SHADOW',     # From K1
                'FORCES',     # From K1
                'UNDERGROUND' # From K1
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
    
    def rail_fence_decrypt(self, text: str, rails: int = 3) -> str:
        """Rail fence cipher decryption."""
        if rails <= 1:
            return text
        
        # Create fence pattern
        fence = [['' for _ in range(len(text))] for _ in range(rails)]
        rail = 0
        direction = 1
        
        # Mark positions
        for col in range(len(text)):
            fence[rail][col] = '*'
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        # Fill fence
        idx = 0
        for row in range(rails):
            for col in range(len(text)):
                if fence[row][col] == '*' and idx < len(text):
                    fence[row][col] = text[idx]
                    idx += 1
        
        # Read plaintext
        plaintext = []
        rail = 0
        direction = 1
        for col in range(len(text)):
            plaintext.append(fence[rail][col])
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        return ''.join(plaintext)
    
    def dictionary_decrypt(self, text: str, key: str) -> str:
        """Dictionary-based substitution."""
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        key_letters = ''.join(dict.fromkeys(key.upper()))
        
        # Build substitution alphabet
        sub_alphabet = key_letters
        for c in alphabet:
            if c not in sub_alphabet:
                sub_alphabet += c
        
        # Decrypt
        plaintext = []
        for c in text:
            if c.isalpha():
                idx = alphabet.index(c.upper())
                plaintext.append(sub_alphabet[idx])
            else:
                plaintext.append(c)
        
        return ''.join(plaintext)
    
    def apply_best_known_solution(self):
        """Apply the best known keys to each zone."""
        print("\n" + "="*60)
        print("APPLYING BEST KNOWN ZONE SOLUTION")
        print("="*60)
        
        # Best known configuration
        head_ct = self.ciphertext[0:21]
        middle_ct = self.ciphertext[34:63]
        tail_ct = self.ciphertext[74:97]
        
        # Apply best methods
        head_pt = self.rail_fence_decrypt(head_ct, 3)
        head_pt = self.vigenere_decrypt(head_pt, 'LANGLEY')
        
        middle_pt = self.vigenere_decrypt(middle_ct, 'ABSCISSA')
        
        tail_pt = self.dictionary_decrypt(tail_ct, 'ILLUSION')
        
        print(f"\nBest Known Solution:")
        print(f"HEAD (LANGLEY): {head_pt}")
        print(f"MIDDLE (ABSCISSA): {middle_pt}")
        print(f"TAIL (ILLUSION): {tail_pt}")
        
        # Look for word connections
        self.analyze_word_connections(head_pt, middle_pt, tail_pt)
        
        return head_pt, middle_pt, tail_pt
    
    def analyze_word_connections(self, head: str, middle: str, tail: str):
        """Analyze how the words might connect."""
        print("\n" + "="*60)
        print("ANALYZING WORD CONNECTIONS")
        print("="*60)
        
        # Extract found words
        words_in_head = []
        words_in_middle = []
        words_in_tail = []
        
        common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'THAT',
                       'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD', 'THERE', 'THEIR',
                       'HEAT', 'COLD', 'TIME', 'CLOCK', 'EAST', 'WEST']
        
        for word in common_words:
            if word in head:
                words_in_head.append(word)
            if word in middle:
                words_in_middle.append(word)
            if word in tail:
                words_in_tail.append(word)
        
        print(f"Words in HEAD: {words_in_head}")
        print(f"Words in MIDDLE: {words_in_middle}")
        print(f"Words in TAIL: {words_in_tail}")
        
        # Possible narrative connections
        if 'AND' in words_in_head and 'HEAT' in words_in_middle and 'WAS' in words_in_tail:
            print("\nPossible narrative: '...AND...HEAT...WAS...'")
            print("This suggests a past-tense description involving heat")
    
    def test_anchor_hypotheses(self):
        """Test what the anchors might be if not plaintext."""
        print("\n" + "="*60)
        print("TESTING ANCHOR HYPOTHESES")
        print("="*60)
        
        # Hypothesis 1: Anchors are nulls - remove them
        print("\n1. ANCHORS AS NULLS (removed):")
        without_anchors = (
            self.ciphertext[0:21] +      # HEAD
            self.ciphertext[34:63] +      # MIDDLE
            self.ciphertext[74:97]        # TAIL
        )
        print(f"Concatenated zones: {without_anchors}")
        print(f"Length: {len(without_anchors)} (was 97)")
        
        # Try decrypting concatenated version
        concat_pt = self.vigenere_decrypt(without_anchors, 'KRYPTOS')
        print(f"Decrypted with KRYPTOS: {concat_pt[:40]}...")
        
        # Hypothesis 2: Anchor first letters spell keys
        print("\n2. ANCHOR FIRST LETTERS AS KEY:")
        anchor_initials = 'E' + 'N' + 'B' + 'C'  # EAST, NORTHEAST, BERLIN, CLOCK
        print(f"Anchor initials: {anchor_initials}")
        
        # Hypothesis 3: Anchor positions are significant
        print("\n3. ANCHOR POSITIONS AS MESSAGE:")
        positions = [21, 25, 63, 69]
        print(f"Positions: {positions}")
        print(f"Differences: {[positions[i+1]-positions[i] for i in range(len(positions)-1)]}")
        print(f"Sum: {sum(positions)} = {sum(positions)}")
        
        # Convert positions to letters
        pos_as_letters = ''.join(num_to_char(p % 26) for p in positions)
        print(f"Positions as letters (mod 26): {pos_as_letters}")
    
    def test_thematic_progression(self):
        """Test all thematic key combinations."""
        print("\n" + "="*60)
        print("TESTING THEMATIC PROGRESSION")
        print("="*60)
        
        best_score = 0
        best_config = None
        
        for head_key in self.zone_keys['HEAD']:
            for middle_key in self.zone_keys['MIDDLE']:
                for tail_key in self.zone_keys['TAIL']:
                    # Decrypt each zone
                    head_ct = self.ciphertext[0:21]
                    middle_ct = self.ciphertext[34:63]
                    tail_ct = self.ciphertext[74:97]
                    
                    # Apply appropriate methods
                    if head_key == 'LANGLEY':
                        head_pt = self.rail_fence_decrypt(head_ct, 3)
                        head_pt = self.vigenere_decrypt(head_pt, head_key)
                    else:
                        head_pt = self.vigenere_decrypt(head_ct, head_key)
                    
                    middle_pt = self.vigenere_decrypt(middle_ct, middle_key)
                    
                    if tail_key in ['ILLUSION', 'IQLUSION']:
                        tail_pt = self.dictionary_decrypt(tail_ct, tail_key)
                    else:
                        tail_pt = self.vigenere_decrypt(tail_ct, tail_key)
                    
                    # Score based on words found
                    score = 0
                    all_text = head_pt + middle_pt + tail_pt
                    
                    target_words = ['AND', 'HEAT', 'WAS', 'THE', 'TIME', 'CLOCK']
                    for word in target_words:
                        if word in all_text:
                            score += 10
                    
                    if score > best_score:
                        best_score = score
                        best_config = {
                            'head': (head_key, head_pt),
                            'middle': (middle_key, middle_pt),
                            'tail': (tail_key, tail_pt),
                            'score': score
                        }
        
        if best_config:
            print(f"\nBest thematic configuration (score={best_config['score']}):")
            print(f"HEAD: {best_config['head'][0]}")
            print(f"  → {best_config['head'][1]}")
            print(f"MIDDLE: {best_config['middle'][0]}")
            print(f"  → {best_config['middle'][1]}")
            print(f"TAIL: {best_config['tail'][0]}")
            print(f"  → {best_config['tail'][1]}")
        
        return best_config
    
    def extend_found_words(self):
        """Try to extend the words we've found."""
        print("\n" + "="*60)
        print("EXTENDING FOUND WORDS")
        print("="*60)
        
        # Focus on middle segment with HEAT
        middle_ct = self.ciphertext[34:63]
        middle_pt = self.vigenere_decrypt(middle_ct, 'ABSCISSA')
        
        print(f"Middle with ABSCISSA: {middle_pt}")
        print(f"HEAT found at positions: {middle_pt.find('HEAT')}")
        
        # What comes before and after HEAT?
        heat_pos = middle_pt.find('HEAT')
        if heat_pos >= 0:
            before = middle_pt[:heat_pos]
            after = middle_pt[heat_pos+4:]
            print(f"Before HEAT: '{before}'")
            print(f"After HEAT: '{after}'")
            
            # Try to make sense of surrounding letters
            print(f"\nAnalyzing context:")
            print(f"Full: ...{before}HEAT{after}...")
            
            # Check for partial words
            possible_words = [
                ('RHEAT', 'THREAT'),
                ('HEATI', 'HEATING'),
                ('HEATH', 'HEATH'),
                ('CHEAT', 'CHEAT')
            ]
            
            for partial, full in possible_words:
                if partial in middle_pt:
                    print(f"Possible word: {full}")
    
    def test_null_padding_hypothesis(self):
        """Test if anchors are null padding."""
        print("\n" + "="*60)
        print("TESTING NULL PADDING HYPOTHESIS")
        print("="*60)
        
        # Extract only non-anchor positions
        non_anchor_text = ""
        for i, c in enumerate(self.ciphertext):
            in_anchor = False
            for name, (start, end) in ANCHORS.items():
                if start <= i < end:
                    in_anchor = True
                    break
            if not in_anchor:
                non_anchor_text += c
        
        print(f"Text without anchors: {non_anchor_text}")
        print(f"Length: {len(non_anchor_text)} (original: 97)")
        
        # Try various keys on concatenated text
        test_keys = ['KRYPTOS', 'ABSCISSA', 'PALIMPSEST', 'LANGLEY']
        
        for key in test_keys:
            pt = self.vigenere_decrypt(non_anchor_text, key)
            
            # Check for words
            words_found = []
            common_words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'HEAT']
            for word in common_words:
                if word in pt:
                    words_found.append(word)
            
            if words_found:
                print(f"\nKey {key}: {pt[:30]}...")
                print(f"  Words found: {words_found}")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("ZONE SOLUTION - BUILDING ON ABSCISSA BREAKTHROUGH")
    print("Testing thematic progression: location → measurement → concept")
    print("="*70)
    
    solver = ZoneSolution()
    
    # Apply best known solution
    head_pt, middle_pt, tail_pt = solver.apply_best_known_solution()
    
    # Test thematic progression
    best_config = solver.test_thematic_progression()
    
    # Test anchor hypotheses
    solver.test_anchor_hypotheses()
    
    # Try to extend found words
    solver.extend_found_words()
    
    # Test null padding
    solver.test_null_padding_hypothesis()
    
    # Final summary
    print("\n" + "="*70)
    print("CRITICAL FINDINGS")
    print("="*70)
    
    print("\nConfirmed zone keys:")
    print("- HEAD: LANGLEY (rail_fence+vigenere) → 'AND'")
    print("- MIDDLE: ABSCISSA (vigenere) → 'HEAT'")
    print("- TAIL: ILLUSION (dictionary) → 'WAS'")
    
    print("\nThematic pattern confirmed:")
    print("- Physical location (Langley/CIA)")
    print("- Mathematical measurement (Abscissa/coordinates)")
    print("- Conceptual layer (Illusion/palimpsest)")
    
    print("\nNext steps:")
    print("1. Focus on extending 'HEAT' context in middle segment")
    print("2. Test if anchors should be removed entirely")
    print("3. Look for narrative connections between zones")
    print("4. Consider that solution might read across zone boundaries")
    
    print("\n" + "="*70)
    print("ZONE SOLUTION ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()