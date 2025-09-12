#!/usr/bin/env python3
"""
f3_steganography.py

Testing steganographic approaches - hidden messages using patterns,
acronyms, visual arrangements, or other concealment methods.
"""

from typing import List, Tuple, Dict, Optional
import re

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class SteganographyAnalyzer:
    """Test steganographic patterns in K4."""
    
    def __init__(self):
        self.k4_ct = K4_CIPHERTEXT
        self.length = len(self.k4_ct)
        
        # Known K4 structure
        self.segments = {
            'HEAD': (0, 21),
            'EAST': (21, 25),
            'NORTHEAST': (25, 34),
            'MIDDLE': (34, 63),
            'BERLIN': (63, 69),
            'CLOCK': (69, 74),
            'TAIL': (74, 97)
        }
    
    def test_acronym_patterns(self):
        """Test if segments form acronyms."""
        print("\n" + "="*60)
        print("TESTING ACRONYM PATTERNS")
        print("="*60)
        
        print("\nExtracting first letters of each segment:")
        
        # First letter of each segment
        first_letters = []
        for name, (start, end) in self.segments.items():
            if start < self.length:
                first_letters.append(self.k4_ct[start])
                print(f"  {name}: {self.k4_ct[start]}")
        
        acronym = ''.join(first_letters)
        print(f"\nAcronym: {acronym}")
        
        # Check if it spells something
        if self.has_words(acronym):
            words = self.find_words(acronym)
            print(f"  Words found: {words}")
        
        # Try last letters
        print("\nLast letters of each segment:")
        last_letters = []
        for name, (start, end) in self.segments.items():
            if end <= self.length:
                last_letters.append(self.k4_ct[end-1])
                print(f"  {name}: {self.k4_ct[end-1]}")
        
        last_acronym = ''.join(last_letters)
        print(f"\nLast letter acronym: {last_acronym}")
    
    def test_morse_patterns(self):
        """Test if letter frequencies encode Morse."""
        print("\n" + "="*60)
        print("TESTING MORSE CODE PATTERNS")
        print("="*60)
        
        print("\nAnalyzing letter patterns as Morse code:")
        
        # Look for patterns of repeated letters (could be dots/dashes)
        pattern = re.findall(r'(.)\1+', self.k4_ct)
        if pattern:
            print(f"Repeated letter patterns found: {pattern}")
        
        # Convert vowels/consonants to dots/dashes
        morse_vc = ''
        for c in self.k4_ct:
            if c in 'AEIOU':
                morse_vc += '.'
            else:
                morse_vc += '-'
        
        print(f"\nVowel/Consonant as Morse: {morse_vc[:50]}...")
        
        # Look for SOS pattern
        if 'SOS' in self.k4_ct:
            print(f"  SOS found at position {self.k4_ct.find('SOS')}")
        
        # Check for ... --- ... pattern
        if '...' in morse_vc and '---' in morse_vc:
            print("  Potential SOS pattern in vowel/consonant encoding")
    
    def test_visual_patterns(self):
        """Test visual/shape patterns in the text."""
        print("\n" + "="*60)
        print("TESTING VISUAL PATTERNS")
        print("="*60)
        
        print("\nArranging K4 in different visual patterns:")
        
        # Triangle pattern
        print("\nTriangle arrangement:")
        pos = 0
        for line_len in range(1, 15):
            if pos + line_len <= self.length:
                print(' ' * (14 - line_len) + self.k4_ct[pos:pos+line_len])
                pos += line_len
            else:
                break
        
        # Diamond pattern (abbreviated)
        print("\nDiamond pattern (center):")
        # Just show the middle part
        sizes = [1, 3, 5, 7, 9, 7, 5, 3, 1]
        pos = 40  # Start from middle
        for size in sizes:
            if pos + size <= self.length:
                padding = ' ' * ((9 - size) // 2)
                print(padding + self.k4_ct[pos:pos+size])
                pos += size
    
    def test_binary_encoding(self):
        """Test if characters encode binary messages."""
        print("\n" + "="*60)
        print("TESTING BINARY ENCODING")
        print("="*60)
        
        print("\nConverting to binary patterns:")
        
        # Even/odd position encoding
        binary_eo = ''
        for i, c in enumerate(self.k4_ct):
            if char_to_num(c) % 2 == 0:
                binary_eo += '0'
            else:
                binary_eo += '1'
        
        print(f"Even/Odd values: {binary_eo[:50]}...")
        
        # Convert binary to ASCII (8-bit chunks)
        print("\nConverting 8-bit chunks to ASCII:")
        for i in range(0, min(40, len(binary_eo)), 8):
            chunk = binary_eo[i:i+8]
            if len(chunk) == 8:
                ascii_val = int(chunk, 2)
                if 32 <= ascii_val <= 126:  # Printable ASCII
                    print(f"  {chunk} -> {chr(ascii_val)}")
        
        # First half vs second half of alphabet
        binary_half = ''
        for c in self.k4_ct:
            if char_to_num(c) < 13:  # A-M
                binary_half += '0'
            else:  # N-Z
                binary_half += '1'
        
        print(f"\nFirst/Second half: {binary_half[:50]}...")
    
    def test_chess_notation(self):
        """Test if K4 encodes chess moves."""
        print("\n" + "="*60)
        print("TESTING CHESS NOTATION")
        print("="*60)
        
        print("\nLooking for chess notation patterns:")
        
        # Chess files are A-H, ranks are 1-8
        # Look for patterns like E2E4 (pawn to e4)
        
        chess_patterns = []
        for i in range(len(self.k4_ct) - 3):
            segment = self.k4_ct[i:i+4]
            # Check if it could be chess notation
            if segment[0] in 'ABCDEFGH' and segment[2] in 'ABCDEFGH':
                chess_patterns.append((i, segment))
        
        if chess_patterns:
            print("Potential chess moves:")
            for pos, move in chess_patterns[:10]:
                print(f"  Position {pos}: {move}")
        
        # Look for piece notation (K=King, Q=Queen, R=Rook, B=Bishop, N=Knight)
        pieces = 'KQRBN'
        piece_positions = []
        for i, c in enumerate(self.k4_ct):
            if c in pieces:
                piece_positions.append((i, c))
        
        print(f"\nChess piece letters found: {len(piece_positions)} occurrences")
        if piece_positions:
            print(f"  First few: {piece_positions[:10]}")
    
    def test_coordinate_encoding(self):
        """Test if letters encode coordinates."""
        print("\n" + "="*60)
        print("TESTING COORDINATE ENCODING")
        print("="*60)
        
        print("\nConverting letters to coordinates:")
        
        # Letter pairs as coordinates
        print("\nLetter pairs as (x,y) coordinates:")
        coords = []
        for i in range(0, self.length - 1, 2):
            x = char_to_num(self.k4_ct[i])
            y = char_to_num(self.k4_ct[i+1])
            coords.append((x, y))
        
        print(f"First 10 coordinates: {coords[:10]}")
        
        # Check if coordinates form a pattern
        # Look for straight lines (same x or y)
        vertical = [c for c in coords if c[0] == coords[0][0]]
        horizontal = [c for c in coords if c[1] == coords[0][1]]
        
        if len(vertical) > 3:
            print(f"  Vertical alignment found: {len(vertical)} points")
        if len(horizontal) > 3:
            print(f"  Horizontal alignment found: {len(horizontal)} points")
        
        # Check for coordinates from K2 (38°57'6.5" 77°8'44")
        # These might map to letter positions
        k2_coords = [(38, 57), (77, 8)]
        print("\nK2 coordinates mapped to alphabet positions:")
        for lat, lon in k2_coords:
            lat_letter = num_to_char(lat % 26)
            lon_letter = num_to_char(lon % 26)
            print(f"  ({lat}, {lon}) -> {lat_letter}{lon_letter}")
    
    def test_music_encoding(self):
        """Test if K4 encodes musical notes."""
        print("\n" + "="*60)
        print("TESTING MUSICAL ENCODING")
        print("="*60)
        
        print("\nLooking for musical patterns:")
        
        # Musical notes are A-G
        notes = 'ABCDEFG'
        music_chars = [c for c in self.k4_ct if c in notes]
        
        print(f"Musical notes (A-G): {''.join(music_chars[:30])}...")
        print(f"Total: {len(music_chars)} of {self.length} characters")
        
        # Look for scales or chord progressions
        # C major scale: C D E F G A B C
        scales = ['CDEFGABC', 'DEFGABCD', 'EFGABCDE', 'FGABCDEF', 
                  'GABCDEFG', 'ABCDEFGA', 'BCDEFGAB']
        
        for scale in scales:
            if scale in self.k4_ct:
                print(f"  Scale found: {scale}")
        
        # Look for chord patterns (triads)
        triads = ['CEG', 'DFA', 'EGB', 'FAC', 'GBD', 'ACE', 'BDF']
        for triad in triads:
            if triad in self.k4_ct:
                print(f"  Triad found: {triad}")
    
    def test_book_cipher(self):
        """Test if K4 references other Kryptos sections."""
        print("\n" + "="*60)
        print("TESTING BOOK CIPHER REFERENCES")
        print("="*60)
        
        print("\nTesting if K4 contains position references to K1/K2/K3:")
        
        # Convert letter positions to numbers
        # A=1, B=2, etc.
        references = []
        
        # Look for patterns like "AB" = position 12 (1,2)
        for i in range(len(self.k4_ct) - 1):
            char1 = char_to_num(self.k4_ct[i]) + 1
            char2 = char_to_num(self.k4_ct[i+1]) + 1
            
            # Single digit positions
            if char1 <= 9 and char2 <= 9:
                pos = char1 * 10 + char2
                if pos <= 97:
                    references.append((i, f"{self.k4_ct[i]}{self.k4_ct[i+1]}", pos))
        
        if references:
            print(f"Potential position references found: {len(references)}")
            print("First few:")
            for idx, chars, pos in references[:5]:
                print(f"  {chars} at index {idx} -> position {pos}")
    
    def test_polybius_square(self):
        """Test if K4 uses Polybius square encoding."""
        print("\n" + "="*60)
        print("TESTING POLYBIUS SQUARE")
        print("="*60)
        
        print("\nTesting 5x5 Polybius square patterns:")
        
        # Standard Polybius square (I/J combined)
        square = [
            ['A', 'B', 'C', 'D', 'E'],
            ['F', 'G', 'H', 'I/J', 'K'],
            ['L', 'M', 'N', 'O', 'P'],
            ['Q', 'R', 'S', 'T', 'U'],
            ['V', 'W', 'X', 'Y', 'Z']
        ]
        
        # Convert K4 to coordinates
        print("\nConverting to Polybius coordinates:")
        coords = []
        for c in self.k4_ct[:20]:  # First 20 chars
            for row in range(5):
                for col in range(5):
                    if c in square[row][col]:
                        coords.append(f"{row+1}{col+1}")
                        break
        
        print(f"First 20 as coordinates: {' '.join(coords)}")
        
        # Try reading coordinates as pairs
        print("\nReading coordinate pairs as new letters:")
        result = []
        for i in range(0, len(coords) - 1, 2):
            if i + 1 < len(coords):
                row = int(coords[i][0]) - 1
                col = int(coords[i+1][0]) - 1
                if 0 <= row < 5 and 0 <= col < 5:
                    result.append(square[row][col][0])
        
        if result:
            decoded = ''.join(result)
            print(f"  Decoded: {decoded}")
            if self.has_words(decoded):
                words = self.find_words(decoded)
                print(f"    Words: {words}")
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        if len(text) < 3:
            return False
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'MIR', 'HEAT']
        return any(word in text for word in words)
    
    def find_words(self, text: str) -> List[str]:
        """Find common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS', 'HIS', 'HER',
                 'THAT', 'HAVE', 'FROM', 'HEAT', 'MIR', 'WAR', 'PEACE']
        return [word for word in words if word in text]

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("STEGANOGRAPHY ANALYSIS")
    print("Testing hidden message techniques in K4")
    print("="*70)
    
    analyzer = SteganographyAnalyzer()
    
    # Run all tests
    analyzer.test_acronym_patterns()
    analyzer.test_morse_patterns()
    analyzer.test_visual_patterns()
    analyzer.test_binary_encoding()
    analyzer.test_chess_notation()
    analyzer.test_coordinate_encoding()
    analyzer.test_music_encoding()
    analyzer.test_book_cipher()
    analyzer.test_polybius_square()
    
    # Summary
    print("\n" + "="*70)
    print("STEGANOGRAPHY SUMMARY")
    print("="*70)
    
    print("\nTested steganographic methods:")
    print("- Acronyms from segment first/last letters")
    print("- Morse code patterns")
    print("- Visual arrangements (triangle, diamond)")
    print("- Binary encoding (even/odd, halves)")
    print("- Chess notation")
    print("- Coordinate systems")
    print("- Musical notes")
    print("- Book cipher references")
    print("- Polybius square")
    
    print("\nNo clear steganographic message found,")
    print("suggesting K4 is primarily cryptographic rather than steganographic.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()