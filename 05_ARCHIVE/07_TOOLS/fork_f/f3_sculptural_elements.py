#!/usr/bin/env python3
"""
f3_sculptural_elements.py

Testing if K4 requires information from the physical Kryptos sculpture.
The sculpture has visual elements that might be keys or instructions.
"""

from typing import List, Tuple, Dict, Optional

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class SculpturalAnalyzer:
    """Analyze K4 using known sculptural elements."""
    
    def __init__(self):
        self.k4_ct = K4_CIPHERTEXT
        
        # Known sculptural elements
        self.sculptural_elements = {
            # The sculpture has deliberate errors/anomalies
            'ERRORS': {
                'IQLUSION': 'Deliberate misspelling of ILLUSION in K1',
                'UNDERGRUUND': 'Possible misspelling in early transcriptions',
                'X_MARKS': 'X used as separator in K2 and K3',
                'Q_MARK': 'Question mark at end of K3'
            },
            
            # Physical features
            'PHYSICAL': {
                'COPPER_SHEETS': 'Four copper sheets with text',
                'PETRIFIED_WOOD': 'Piece of petrified wood',
                'GRANITE_SLABS': 'Granite with Morse code',
                'LODESTONE': 'Magnetic stone (compass)',
                'WATER_POOL': 'Reflecting pool beneath'
            },
            
            # Morse code on other side
            'MORSE': {
                'VIRTUALLY': 'Word in Morse on granite',
                'INVISIBLE': 'Word in Morse on granite',
                'SHADOW_FORCES': 'Phrase in Morse',
                'LUCID_MEMORY': 'Phrase in Morse',
                'T_IS_YOUR_POSITION': 'Fragment in Morse'
            },
            
            # Compass and magnetic references
            'COMPASS': {
                'NORTH': 'Compass direction',
                'SOUTH': 'Compass direction',
                'EAST': 'Compass direction (in K4 anchors)',
                'WEST': 'Compass direction',
                'NORTHEAST': 'In K4 anchors',
                'NORTHWEST': 'Implied quadrant',
                'SOUTHEAST': 'Implied quadrant',
                'SOUTHWEST': 'Implied quadrant'
            }
        }
        
        # Visual patterns on sculpture
        self.visual_patterns = {
            'VIGENERE_TABLEAU': 'Visible on copper sheets',
            'MATRIX_LAYOUT': 'Text arranged in matrix form',
            'CUT_OUT_LETTERS': 'Letters are cut through copper',
            'LIGHT_PROJECTION': 'Light passes through cut letters',
            'SHADOW_PATTERNS': 'Shadows form patterns at different times'
        }
    
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
    
    def test_morse_keys(self):
        """Test Morse code words as keys."""
        print("\n" + "="*60)
        print("TESTING MORSE CODE ELEMENTS")
        print("="*60)
        
        morse_keys = [
            'VIRTUALLY', 'INVISIBLE', 'SHADOW', 'FORCES',
            'LUCID', 'MEMORY', 'SHADOWFORCES', 'LUCIDMEMORY',
            'VIRTUALLYINVISIBLE', 'TISYOURPOSITION'
        ]
        
        print("\nMorse code appears on the granite slabs.")
        print("Testing these words as keys:")
        
        for key in morse_keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if 'MIR' in pt or 'HEAT' in pt or self.has_meaningful_words(pt):
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
                
                if 'MIR' in pt:
                    print(f"    Contains MIR at {pt.find('MIR')}")
                if 'HEAT' in pt:
                    print(f"    Contains HEAT at {pt.find('HEAT')}")
                
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
    
    def test_iqlusion_pattern(self):
        """Test the IQLUSION misspelling pattern."""
        print("\n" + "="*60)
        print("TESTING IQLUSION PATTERN")
        print("="*60)
        
        print("\nK1 deliberately uses IQLUSION instead of ILLUSION.")
        print("Testing if this substitution pattern applies to K4:")
        
        # Apply LL→QL substitution
        modified_ct = self.k4_ct.replace('LL', 'QL')
        print(f"After LL→QL: {modified_ct[:50]}...")
        
        # Try IQLUSION as key
        pt = self.vigenere_decrypt(self.k4_ct, 'IQLUSION')
        if self.has_words(pt):
            print(f"\nIQLUSION as key: {pt[:50]}...")
            words = self.find_words(pt)
            if words:
                print(f"  Words: {words}")
        
        # Try ILLUSION for comparison
        pt2 = self.vigenere_decrypt(self.k4_ct, 'ILLUSION')
        if self.has_words(pt2):
            print(f"\nILLUSION as key: {pt2[:50]}...")
            words = self.find_words(pt2)
            if words:
                print(f"  Words: {words}")
    
    def test_compass_directions(self):
        """Test compass directions as keys."""
        print("\n" + "="*60)
        print("TESTING COMPASS DIRECTIONS")
        print("="*60)
        
        print("\nThe sculpture includes compass/magnetic elements.")
        print("Testing directional keys:")
        
        # Single directions
        directions = ['NORTH', 'SOUTH', 'EAST', 'WEST',
                     'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST']
        
        for direction in directions:
            pt = self.vigenere_decrypt(self.k4_ct, direction)
            
            if 'MIR' in pt or 'HEAT' in pt or self.has_meaningful_words(pt):
                print(f"\n{direction}:")
                print(f"  {pt[:50]}...")
                
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
        
        # Combined directions (following a path)
        paths = [
            'NORTHEASTSOUTHWEST',  # Diagonal
            'EASTWESTNORTHSOUTH',  # Cross pattern
            'NESENWSW',            # Abbreviated clockwise
            'NEWSNSEW'             # Cardinal spiral
        ]
        
        for path in paths:
            pt = self.vigenere_decrypt(self.k4_ct, path)
            
            if self.has_meaningful_words(pt):
                print(f"\n{path}:")
                print(f"  {pt[:50]}...")
    
    def test_light_shadow_patterns(self):
        """Test patterns based on light and shadow."""
        print("\n" + "="*60)
        print("TESTING LIGHT/SHADOW PATTERNS")
        print("="*60)
        
        print("\nThe sculpture creates patterns with light and shadow.")
        print("Testing related keys:")
        
        # Light/shadow related keys
        keys = [
            'LIGHT', 'SHADOW', 'LIGHTSHADOW', 'SHADOWLIGHT',
            'ILLUMINATED', 'DARKNESS', 'PROJECTION', 'REFLECTION'
        ]
        
        for key in keys:
            pt = self.vigenere_decrypt(self.k4_ct, key)
            
            if 'MIR' in pt or 'HEAT' in pt:
                print(f"\n{key}:")
                print(f"  {pt[:50]}...")
                print(f"    Contains MIR/HEAT!")
    
    def test_x_separator_pattern(self):
        """Test if X marks separate segments."""
        print("\n" + "="*60)
        print("TESTING X SEPARATOR PATTERN")
        print("="*60)
        
        print("\nK2 and K3 use X as separator. Testing if K4 has hidden Xs:")
        
        # Look for patterns that might be X
        # In K4, positions where X appears
        x_positions = [i for i, c in enumerate(self.k4_ct) if c == 'X']
        print(f"X appears at positions: {x_positions}")
        
        if x_positions:
            # Split at X positions
            segments = []
            last_pos = 0
            for x_pos in x_positions:
                segments.append(self.k4_ct[last_pos:x_pos])
                last_pos = x_pos + 1
            segments.append(self.k4_ct[last_pos:])
            
            print(f"\nSegments split by X:")
            for i, seg in enumerate(segments):
                if len(seg) > 0:
                    print(f"  Segment {i}: {seg[:30]}... (length {len(seg)})")
            
            # Try decrypting each segment separately
            for i, seg in enumerate(segments):
                if len(seg) > 10:  # Only meaningful segments
                    pt = self.vigenere_decrypt(seg, 'ABSCISSA')
                    if 'MIR' in pt or 'HEAT' in pt or self.has_words(pt):
                        print(f"\n  Segment {i} with ABSCISSA: {pt[:30]}...")
    
    def test_physical_materials(self):
        """Test keys based on physical materials."""
        print("\n" + "="*60)
        print("TESTING PHYSICAL MATERIALS")
        print("="*60)
        
        print("\nThe sculpture uses specific materials:")
        
        materials = [
            'COPPER', 'GRANITE', 'LODESTONE', 'PETRIFIED',
            'WOOD', 'STONE', 'MAGNETIC', 'WATER'
        ]
        
        for material in materials:
            pt = self.vigenere_decrypt(self.k4_ct, material)
            
            if self.has_meaningful_words(pt):
                print(f"\n{material}:")
                print(f"  {pt[:50]}...")
                words = self.find_words(pt)
                if words:
                    print(f"    Words: {words}")
    
    def test_matrix_reading(self):
        """Test reading K4 as a matrix (as displayed on sculpture)."""
        print("\n" + "="*60)
        print("TESTING MATRIX READING PATTERNS")
        print("="*60)
        
        print("\nOn the sculpture, text appears in matrix form.")
        print("Testing different matrix reading patterns:")
        
        # K4 is 97 chars, close to 10x10 (100)
        # Pad to 100 for 10x10 matrix
        padded = self.k4_ct + 'XXX'
        
        # Create matrix
        matrix = []
        for i in range(10):
            matrix.append(padded[i*10:(i+1)*10])
        
        print("\n10x10 Matrix:")
        for row in matrix:
            print(f"  {row}")
        
        # Read by columns
        by_columns = ''
        for col in range(10):
            for row in range(10):
                by_columns += matrix[row][col]
        
        print(f"\nBy columns: {by_columns[:50]}...")
        
        # Decrypt with ABSCISSA
        pt = self.vigenere_decrypt(by_columns[:97], 'ABSCISSA')
        if 'MIR' in pt or 'HEAT' in pt:
            print(f"  With ABSCISSA: {pt[:50]}...")
            print(f"    Contains MIR/HEAT!")
        
        # Diagonal reading
        diagonal = ''
        for i in range(10):
            diagonal += matrix[i][i]
        for i in range(1, 10):
            diagonal += matrix[i][10-1-i]
        
        print(f"\nDiagonal: {diagonal}")
        pt = self.vigenere_decrypt(diagonal, 'ABSCISSA')
        if self.has_words(pt):
            print(f"  With ABSCISSA: {pt}")
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS']
        return any(word in text for word in words)
    
    def has_meaningful_words(self, text: str) -> bool:
        """Check for meaningful words."""
        words = ['THE', 'AND', 'HEAT', 'MIR', 'BERLIN', 'CLOCK', 'WAR', 'PEACE']
        count = sum(1 for word in words if word in text)
        return count >= 2
    
    def find_words(self, text: str) -> List[str]:
        """Find common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'HEAT', 'MIR', 'WAR', 'PEACE']
        return [word for word in words if word in text]

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("SCULPTURAL ELEMENTS ANALYSIS")
    print("Testing elements from the physical Kryptos sculpture")
    print("="*70)
    
    analyzer = SculpturalAnalyzer()
    
    # Run all tests
    analyzer.test_morse_keys()
    analyzer.test_iqlusion_pattern()
    analyzer.test_compass_directions()
    analyzer.test_light_shadow_patterns()
    analyzer.test_x_separator_pattern()
    analyzer.test_physical_materials()
    analyzer.test_matrix_reading()
    
    # Summary
    print("\n" + "="*70)
    print("SCULPTURAL ELEMENTS SUMMARY")
    print("="*70)
    
    print("\nThe Kryptos sculpture contains many elements beyond the text:")
    print("- Morse code on granite (VIRTUALLY INVISIBLE, etc.)")
    print("- Deliberate misspellings (IQLUSION)")
    print("- Physical materials (copper, lodestone, water)")
    print("- Light/shadow projections through cut letters")
    print("- Compass and magnetic references")
    
    print("\nThese elements might be keys or provide instructions")
    print("for solving K4, but no clear solution emerged from testing.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()