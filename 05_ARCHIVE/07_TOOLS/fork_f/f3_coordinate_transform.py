#!/usr/bin/env python3
"""
f3_coordinate_transform.py

Since ABSCISSA (x-coordinate) produces MIR HEAT, test coordinate-based transformations.
What if K4 uses mathematical/geometric transformations?
"""

import math
from typing import List, Tuple, Dict, Optional

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def char_to_num(c: str) -> int:
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    return chr((n % 26) + ord('A'))

class CoordinateTransformAnalyzer:
    """Test coordinate and mathematical transformations."""
    
    def __init__(self):
        self.k4_ct = K4_CIPHERTEXT
        self.length = len(self.k4_ct)
        
        # Grid dimensions that work with 97
        self.grids = [
            (97, 1),  # Linear
            (1, 97),  # Column
        ]
        
        # Near-square grids (with padding)
        self.approx_grids = [
            (10, 10),  # 100 (pad 3)
            (9, 11),   # 99 (pad 2)
            (11, 9),   # 99 (pad 2)
            (8, 12),   # 96 (truncate 1)
            (12, 8),   # 96 (truncate 1)
        ]
        
        # Mathematical constants (scaled to 0-25)
        self.constants = {
            'PI': [int((math.sin(i * math.pi / 48) + 1) * 12.5) % 26 for i in range(97)],
            'E': [int((math.exp(i/97) - 1) * 10) % 26 for i in range(97)],
            'PHI': [int((1.618 ** (i/10)) * 10) % 26 for i in range(97)],
            'SQRT2': [int((math.sqrt(2) ** (i/10)) * 10) % 26 for i in range(97)]
        }
    
    def test_grid_transformations(self):
        """Test various grid-based transformations."""
        print("\n" + "="*60)
        print("GRID TRANSFORMATIONS")
        print("="*60)
        
        # Test spiral reading
        print("\nSpiral reading patterns:")
        
        # Create 10x10 grid with padding
        padded = self.k4_ct + 'XXX'  # Pad to 100
        grid = []
        for i in range(10):
            grid.append(padded[i*10:(i+1)*10])
        
        # Read in spiral
        spiral = self.spiral_read(grid)
        print(f"Spiral: {spiral[:50]}...")
        
        # Decrypt with ABSCISSA
        pt = self.vigenere_decrypt(spiral[:97], 'ABSCISSA')
        if 'MIR' in pt or 'HEAT' in pt or self.has_words(pt):
            print(f"  With ABSCISSA: {pt[:50]}...")
            if 'MIR' in pt:
                print(f"    Contains MIR at {pt.find('MIR')}")
    
    def test_coordinate_shifts(self):
        """Test shifting based on coordinates."""
        print("\n" + "="*60)
        print("COORDINATE-BASED SHIFTS")
        print("="*60)
        
        print("\nShifting each character by its position:")
        
        # Shift by position (like autokey)
        shifted = []
        for i, c in enumerate(self.k4_ct):
            shift = i % 26
            new_val = (char_to_num(c) - shift) % 26
            shifted.append(num_to_char(new_val))
        
        result = ''.join(shifted)
        print(f"Position shift: {result[:50]}...")
        
        if self.has_words(result):
            words = self.find_words(result)
            print(f"  Words: {words}")
        
        # Now try with ABSCISSA
        pt = self.vigenere_decrypt(result, 'ABSCISSA')
        if 'MIR' in pt or 'HEAT' in pt:
            print(f"  With ABSCISSA: {pt[:50]}...")
            print(f"    Found MIR/HEAT!")
    
    def test_mathematical_functions(self):
        """Test mathematical function-based transformations."""
        print("\n" + "="*60)
        print("MATHEMATICAL FUNCTIONS")
        print("="*60)
        
        print("\nApplying mathematical functions as keys:")
        
        for name, key_sequence in self.constants.items():
            # Use mathematical sequence as key
            result = []
            for i, c in enumerate(self.k4_ct):
                c_val = char_to_num(c)
                k_val = key_sequence[i]
                p_val = (c_val - k_val) % 26
                result.append(num_to_char(p_val))
            
            plaintext = ''.join(result)
            
            if self.has_words(plaintext):
                print(f"\n{name} function:")
                print(f"  Result: {plaintext[:50]}...")
                words = self.find_words(plaintext)
                if words:
                    print(f"  Words: {words}")
            
            # Try combining with ABSCISSA
            pt2 = self.vigenere_decrypt(plaintext, 'ABSCISSA')
            if 'MIR' in pt2 or 'HEAT' in pt2:
                print(f"\n{name} + ABSCISSA:")
                print(f"  {pt2[:50]}...")
                print(f"  Contains MIR/HEAT!")
    
    def test_coordinate_pairs(self):
        """Test using coordinate pairs from K2."""
        print("\n" + "="*60)
        print("COORDINATE PAIRS FROM K2")
        print("="*60)
        
        # Coordinates from K2
        coords = [
            (38, 57, 6.5),   # 38°57'6.5"
            (77, 8, 44)       # 77°8'44"
        ]
        
        print("\nUsing K2 coordinates as transformation keys:")
        
        # Create key from coordinates
        coord_key = []
        for lat_deg, lat_min, lat_sec in [coords[0]]:
            # Various ways to combine
            coord_key.extend([
                lat_deg % 26,
                lat_min % 26,
                int(lat_sec) % 26
            ])
        
        for lon_deg, lon_min, lon_sec in [coords[1]]:
            coord_key.extend([
                lon_deg % 26,
                lon_min % 26,
                lon_sec % 26
            ])
        
        # Extend pattern
        full_key = coord_key * (97 // len(coord_key) + 1)
        
        result = []
        for i, c in enumerate(self.k4_ct):
            c_val = char_to_num(c)
            k_val = full_key[i]
            p_val = (c_val - k_val) % 26
            result.append(num_to_char(p_val))
        
        plaintext = ''.join(result)
        print(f"Coordinate key: {plaintext[:50]}...")
        
        if self.has_words(plaintext):
            words = self.find_words(plaintext)
            print(f"  Words: {words}")
    
    def test_abscissa_ordinate(self):
        """Test ABSCISSA with ORDINATE (y-coordinate)."""
        print("\n" + "="*60)
        print("ABSCISSA + ORDINATE")
        print("="*60)
        
        print("\nSince ABSCISSA (x) works partially, test with ORDINATE (y):")
        
        # Try different combinations
        combinations = [
            ('ABSCISSA', 'ORDINATE'),
            ('ORDINATE', 'ABSCISSA'),
            ('ABSCISSAORDINATE', None),
            ('ORDINATEABSCISSA', None),
            ('XYXYXYXY', None),
            ('ABSCISSA', 'ABSCISSA'),  # Double ABSCISSA
        ]
        
        for key1, key2 in combinations:
            if key2:
                # Two-stage decryption
                temp = self.vigenere_decrypt(self.k4_ct, key1)
                result = self.vigenere_decrypt(temp, key2)
                desc = f"{key1} then {key2}"
            else:
                # Single key
                result = self.vigenere_decrypt(self.k4_ct, key1)
                desc = key1
            
            if 'MIR' in result or 'HEAT' in result or self.has_meaningful_words(result):
                print(f"\n{desc}:")
                print(f"  {result[:50]}...")
                
                if 'MIR' in result:
                    mir_pos = result.find('MIR')
                    print(f"  MIR at position {mir_pos}")
                if 'HEAT' in result:
                    heat_pos = result.find('HEAT')
                    print(f"  HEAT at position {heat_pos}")
                
                words = self.find_words(result)
                if words:
                    print(f"  Words: {words}")
    
    def test_rotation_cipher(self):
        """Test rotation-based transformations."""
        print("\n" + "="*60)
        print("ROTATION TRANSFORMATIONS")
        print("="*60)
        
        print("\nRotating text in various ways:")
        
        # Rotate entire text
        for rotation in [1, 3, 7, 13, 25, 48, 49]:
            rotated = self.k4_ct[rotation:] + self.k4_ct[:rotation]
            
            # Try with ABSCISSA
            pt = self.vigenere_decrypt(rotated, 'ABSCISSA')
            
            if 'MIR' in pt or 'HEAT' in pt:
                print(f"\nRotation by {rotation}:")
                print(f"  {pt[:50]}...")
                print(f"  Contains MIR/HEAT!")
        
        # Progressive rotation (each char rotated more)
        progressive = []
        for i, c in enumerate(self.k4_ct):
            rot = i % 26
            new_val = (char_to_num(c) + rot) % 26
            progressive.append(num_to_char(new_val))
        
        prog_text = ''.join(progressive)
        pt = self.vigenere_decrypt(prog_text, 'ABSCISSA')
        
        if 'MIR' in pt or 'HEAT' in pt:
            print(f"\nProgressive rotation + ABSCISSA:")
            print(f"  {pt[:50]}...")
    
    def spiral_read(self, grid: List[str]) -> str:
        """Read grid in spiral pattern."""
        result = []
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        
        top, bottom, left, right = 0, rows-1, 0, cols-1
        
        while top <= bottom and left <= right:
            # Right
            for i in range(left, right+1):
                if top <= bottom:
                    result.append(grid[top][i])
            top += 1
            
            # Down
            for i in range(top, bottom+1):
                if left <= right:
                    result.append(grid[i][right])
            right -= 1
            
            # Left
            if top <= bottom:
                for i in range(right, left-1, -1):
                    result.append(grid[bottom][i])
                bottom -= 1
            
            # Up
            if left <= right:
                for i in range(bottom, top-1, -1):
                    result.append(grid[i][left])
                left += 1
        
        return ''.join(result)
    
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
    
    def has_words(self, text: str) -> bool:
        """Check for common words."""
        words = ['THE', 'AND', 'ARE', 'YOU', 'WAS']
        return any(word in text for word in words)
    
    def has_meaningful_words(self, text: str) -> bool:
        """Check for meaningful words."""
        words = ['THE', 'AND', 'HEAT', 'MIR', 'BERLIN', 'CLOCK']
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
    print("COORDINATE TRANSFORMATION ANALYSIS")
    print("Testing mathematical and geometric transformations")
    print("="*70)
    
    analyzer = CoordinateTransformAnalyzer()
    
    # Run tests
    analyzer.test_grid_transformations()
    analyzer.test_coordinate_shifts()
    analyzer.test_mathematical_functions()
    analyzer.test_coordinate_pairs()
    analyzer.test_abscissa_ordinate()
    analyzer.test_rotation_cipher()
    
    # Summary
    print("\n" + "="*70)
    print("COORDINATE TRANSFORMATION SUMMARY")
    print("="*70)
    
    print("\nSince ABSCISSA (x-coordinate) produces MIR HEAT,")
    print("we tested various mathematical/geometric transformations.")
    print("The coordinate theme suggests K4 might use:")
    print("- Grid-based reading patterns")
    print("- Mathematical functions as keys")
    print("- Coordinate pairs from K2")
    print("- Combination of ABSCISSA and ORDINATE")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()