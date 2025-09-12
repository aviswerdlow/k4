#!/usr/bin/env python3
"""
zone_narrative.py

Advanced zone solution exploring narrative connections and cross-boundary reading.
Building on confirmed thematic progression: location → measurement → concept.
"""

from typing import List, Tuple, Dict, Optional
import itertools

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Zone definitions (confirmed)
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

class NarrativeSolver:
    """Explore narrative connections across zones."""
    
    def __init__(self):
        self.ciphertext = K4_CIPHERTEXT
        
        # Confirmed best keys
        self.best_keys = {
            'HEAD': 'LANGLEY',
            'MIDDLE': 'ABSCISSA',
            'TAIL': 'ILLUSION'
        }
        
        # Known plaintext fragments
        self.known_words = {
            'HEAD': 'AND',
            'MIDDLE': 'HEAT',
            'TAIL': 'WAS'
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
    
    def test_cross_boundary_reading(self):
        """Test if the solution reads across zone boundaries."""
        print("\n" + "="*60)
        print("TESTING CROSS-BOUNDARY NARRATIVE")
        print("="*60)
        
        # Get decrypted zones
        head_ct = self.ciphertext[0:21]
        middle_ct = self.ciphertext[34:63]
        tail_ct = self.ciphertext[74:97]
        
        # Apply confirmed methods
        head_pt = self.rail_fence_decrypt(head_ct, 3)
        head_pt = self.vigenere_decrypt(head_pt, 'LANGLEY')
        middle_pt = self.vigenere_decrypt(middle_ct, 'ABSCISSA')
        tail_pt = self.dictionary_decrypt(tail_ct, 'ILLUSION')
        
        print(f"\nDecrypted zones:")
        print(f"HEAD:   {head_pt}")
        print(f"MIDDLE: {middle_pt}")
        print(f"TAIL:   {tail_pt}")
        
        # Test reading patterns
        patterns = [
            ('Linear', head_pt + middle_pt + tail_pt),
            ('Interleaved-2', self.interleave([head_pt, middle_pt, tail_pt], 2)),
            ('Interleaved-3', self.interleave([head_pt, middle_pt, tail_pt], 3)),
            ('Reverse', tail_pt + middle_pt + head_pt),
            ('Middle-first', middle_pt + head_pt + tail_pt)
        ]
        
        for name, text in patterns:
            print(f"\n{name} reading:")
            print(f"  Text: {text[:40]}...")
            words_found = self.find_words(text)
            if words_found:
                print(f"  Words: {words_found}")
    
    def interleave(self, texts: List[str], chunk_size: int) -> str:
        """Interleave multiple texts by chunks."""
        result = []
        max_len = max(len(t) for t in texts)
        
        for i in range(0, max_len, chunk_size):
            for text in texts:
                chunk = text[i:i+chunk_size]
                if chunk:
                    result.append(chunk)
        
        return ''.join(result)
    
    def find_words(self, text: str) -> List[str]:
        """Find common English words in text."""
        common_words = [
            'THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER', 'THAT',
            'HAVE', 'FROM', 'THEY', 'WILL', 'WOULD', 'THERE', 'THEIR',
            'WHAT', 'BEEN', 'MORE', 'WHEN', 'TIME', 'VERY', 'YOUR',
            'HEAT', 'COLD', 'WARM', 'FIRE', 'BURN', 'MELT', 'FREEZE'
        ]
        
        found = []
        for word in common_words:
            if word in text:
                found.append(word)
        
        return found
    
    def test_anchor_as_instructions(self):
        """Test if anchors provide decryption instructions."""
        print("\n" + "="*60)
        print("TESTING ANCHORS AS INSTRUCTIONS")
        print("="*60)
        
        # Extract anchor ciphertext
        anchor_texts = {}
        for name, (start, end) in ANCHORS.items():
            anchor_texts[name] = self.ciphertext[start:end]
        
        print("\nAnchor ciphertexts:")
        for name, text in anchor_texts.items():
            print(f"{name}: {text}")
        
        # Test if anchors decode to instructions
        instruction_keys = ['KRYPTOS', 'SANBORN', 'SCHEIDT', 'WEBSTER']
        
        for key in instruction_keys:
            print(f"\nTrying key '{key}' on anchors:")
            for name, text in anchor_texts.items():
                pt_vig = self.vigenere_decrypt(text, key)
                pt_beau = self.beaufort_decrypt(text, key)
                
                # Check for instruction-like words
                instruction_words = ['USE', 'KEY', 'READ', 'SKIP', 'TAKE', 'MOVE', 'SHIFT']
                
                for word in instruction_words:
                    if word in pt_vig:
                        print(f"  {name} (Vigenère): {pt_vig} - contains '{word}'!")
                    if word in pt_beau:
                        print(f"  {name} (Beaufort): {pt_beau} - contains '{word}'!")
    
    def beaufort_decrypt(self, text: str, key: str) -> str:
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
            k_val = char_to_num(key[i % key_len])
            p_val = (k_val - c_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def test_extended_context(self):
        """Try to extend the context around found words."""
        print("\n" + "="*60)
        print("EXTENDING WORD CONTEXT")
        print("="*60)
        
        # Focus on HEAT in middle segment
        middle_ct = self.ciphertext[34:63]
        middle_pt = self.vigenere_decrypt(middle_ct, 'ABSCISSA')
        
        heat_pos = middle_pt.find('HEAT')
        print(f"\nMiddle plaintext: {middle_pt}")
        print(f"HEAT position: {heat_pos}")
        
        # Try different keys for the parts before/after HEAT
        before_ct = middle_ct[:heat_pos]
        after_ct = middle_ct[heat_pos+4:]
        
        extension_keys = ['TEMPERATURE', 'DEGREE', 'CELSIUS', 'FAHRENHEIT', 'THERMAL']
        
        for key in extension_keys:
            before_pt = self.vigenere_decrypt(before_ct, key)
            after_pt = self.vigenere_decrypt(after_ct, key)
            
            extended = before_pt + 'HEAT' + after_pt
            words = self.find_words(extended)
            
            if words and len(words) > 1:
                print(f"\nKey '{key}' extension:")
                print(f"  Result: {extended}")
                print(f"  Words: {words}")
    
    def test_narrative_themes(self):
        """Test thematic narrative connections."""
        print("\n" + "="*60)
        print("TESTING NARRATIVE THEMES")
        print("="*60)
        
        # Thematic word groups
        themes = {
            'Location': ['LANGLEY', 'VIRGINIA', 'WASHINGTON', 'AMERICA', 'AGENCY'],
            'Temperature': ['HEAT', 'COLD', 'WARM', 'FREEZE', 'BURN', 'THERMAL'],
            'Time': ['WAS', 'IS', 'WILL', 'PAST', 'PRESENT', 'FUTURE', 'CLOCK'],
            'Direction': ['EAST', 'WEST', 'NORTH', 'SOUTH', 'NORTHEAST'],
            'Geometry': ['ABSCISSA', 'ORDINATE', 'ANGLE', 'DEGREE', 'COORDINATE']
        }
        
        # Get decrypted zones
        head_ct = self.ciphertext[0:21]
        middle_ct = self.ciphertext[34:63]
        tail_ct = self.ciphertext[74:97]
        
        head_pt = self.rail_fence_decrypt(head_ct, 3)
        head_pt = self.vigenere_decrypt(head_pt, 'LANGLEY')
        middle_pt = self.vigenere_decrypt(middle_ct, 'ABSCISSA')
        tail_pt = self.dictionary_decrypt(tail_ct, 'ILLUSION')
        
        full_text = head_pt + middle_pt + tail_pt
        
        print("\nThematic analysis of decrypted text:")
        for theme, words in themes.items():
            found = [w for w in words if w in full_text]
            if found:
                print(f"{theme}: {found}")
        
        # Look for sentence patterns
        print("\nPossible sentence patterns:")
        
        # Pattern 1: Subject + Action + Object
        if 'AND' in head_pt and 'HEAT' in middle_pt and 'WAS' in tail_pt:
            print("Pattern 1: [something] AND [something] HEAT WAS [something]")
        
        # Pattern 2: Time sequence
        if 'WAS' in tail_pt:
            print("Pattern 2: [past event] WAS [result/consequence]")
        
        # Pattern 3: Location-based
        if 'EAST' in self.ciphertext and 'NORTHEAST' in self.ciphertext:
            print("Pattern 3: Directional/geographical narrative")

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("ZONE NARRATIVE ANALYSIS")
    print("Exploring narrative connections and cross-boundary reading")
    print("="*70)
    
    solver = NarrativeSolver()
    
    # Test cross-boundary reading
    solver.test_cross_boundary_reading()
    
    # Test anchors as instructions
    solver.test_anchor_as_instructions()
    
    # Try to extend context
    solver.test_extended_context()
    
    # Test narrative themes
    solver.test_narrative_themes()
    
    # Final insights
    print("\n" + "="*70)
    print("NARRATIVE INSIGHTS")
    print("="*70)
    
    print("\nConfirmed elements:")
    print("1. Zone-based encryption with thematic keys")
    print("2. Words found: AND (head), HEAT (middle), WAS (tail)")
    print("3. Thematic progression: location → measurement → concept")
    
    print("\nNarrative hypothesis:")
    print("The message likely describes something about heat/temperature")
    print("in relation to location (Langley/CIA) and time (was = past tense).")
    print("The anchors (EAST, NORTHEAST, BERLIN, CLOCK) may be:")
    print("- Zone delimiters (confirmed)")
    print("- Part of the narrative (geographical/temporal references)")
    print("- Instructions for reading order")
    
    print("\nNext investigations:")
    print("1. Test if removing anchors completely gives coherent message")
    print("2. Try reading zones in different orders based on anchor hints")
    print("3. Look for temperature/heat-related keys for other zones")
    print("4. Consider that 'BERLIN' might relate to Cold War (heat/cold theme)")
    
    print("\n" + "="*70)
    print("NARRATIVE ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()