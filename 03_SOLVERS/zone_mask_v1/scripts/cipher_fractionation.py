#!/usr/bin/env python3
"""
Fractionation cipher systems: Bifid, Trifid, and Four-Square
Plan G: Testing fractionation methods against K4 anchors
"""

from typing import Dict, List, Tuple, Optional, Any
import math


def create_polybius_square(keyword: str = "KRYPTOS") -> Dict[str, Tuple[int, int]]:
    """
    Create a 5x5 Polybius square with I/J merged
    
    Args:
        keyword: Keyword for keyed alphabet
        
    Returns:
        Dictionary mapping letters to (row, col) coordinates
    """
    # Build keyed alphabet
    alphabet = []
    used = set()
    
    # Add keyword letters (merge I/J)
    for char in keyword.upper():
        if char == 'J':
            char = 'I'
        if char not in used and char.isalpha():
            alphabet.append(char)
            used.add(char)
    
    # Add remaining letters (skip J)
    for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":  # Note: J omitted
        if char not in used:
            alphabet.append(char)
    
    # Create 5x5 grid mapping
    square = {}
    reverse_square = {}
    for idx, char in enumerate(alphabet[:25]):  # Only 25 positions
        row = idx // 5
        col = idx % 5
        square[char] = (row, col)
        reverse_square[(row, col)] = char
    
    # J maps to I's position
    if 'I' in square:
        square['J'] = square['I']
    
    return square, reverse_square


def create_trifid_cube(keyword: str = "KRYPTOS") -> Dict[str, Tuple[int, int, int]]:
    """
    Create a 3x3x3 Trifid cube (27 positions)
    
    Args:
        keyword: Keyword for keyed alphabet
        
    Returns:
        Dictionary mapping letters to (layer, row, col) coordinates
    """
    # Build keyed alphabet for 27 positions
    alphabet = []
    used = set()
    
    # Add keyword letters
    for char in keyword.upper():
        if char not in used and char.isalpha():
            alphabet.append(char)
            used.add(char)
    
    # Add remaining letters
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if char not in used:
            alphabet.append(char)
    
    # Add a 27th character (duplicate X or use space)
    if len(alphabet) < 27:
        alphabet.append('X')  # Duplicate X for 27th position
    
    # Create 3x3x3 cube mapping
    cube = {}
    reverse_cube = {}
    for idx, char in enumerate(alphabet[:27]):
        layer = idx // 9
        row = (idx % 9) // 3
        col = idx % 3
        cube[char] = (layer, row, col)
        reverse_cube[(layer, row, col)] = char
    
    return cube, reverse_cube


class BifidCipher:
    """Bifid cipher with configurable Polybius square and period"""
    
    def __init__(self, polybius: str = "kryptos", period: int = 5):
        """
        Initialize Bifid cipher
        
        Args:
            polybius: Keyword for Polybius square or "kryptos"
            period: Fractionation period
        """
        if isinstance(polybius, dict):
            keyword = polybius.get('keyword', 'KRYPTOS')
        elif polybius == 'kryptos':
            keyword = 'KRYPTOS'
        else:
            keyword = polybius
            
        self.square, self.reverse_square = create_polybius_square(keyword)
        self.period = period
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt using Bifid cipher"""
        plaintext = plaintext.upper().replace('J', 'I')
        
        # Remove non-alphabetic characters for fractionation
        clean_text = ''.join(c for c in plaintext if c.isalpha())
        
        # Convert to coordinates
        coords = []
        for char in clean_text:
            if char in self.square:
                coords.append(self.square[char])
        
        # Process in periods
        result = []
        for i in range(0, len(coords), self.period):
            block = coords[i:i+self.period]
            
            # Extract rows and columns
            rows = [coord[0] for coord in block]
            cols = [coord[1] for coord in block]
            
            # Recombine (read rows then columns)
            combined = rows + cols
            
            # Convert back to letters
            for j in range(0, len(combined), 2):
                if j+1 < len(combined):
                    row = combined[j]
                    col = combined[j+1]
                    if (row, col) in self.reverse_square:
                        result.append(self.reverse_square[(row, col)])
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt using Bifid cipher"""
        ciphertext = ciphertext.upper().replace('J', 'I')
        
        # Remove non-alphabetic characters
        clean_text = ''.join(c for c in ciphertext if c.isalpha())
        
        result = []
        
        # Process in periods
        for i in range(0, len(clean_text), self.period):
            block = clean_text[i:i+self.period]
            
            # Convert block to coordinates
            coords = []
            for char in block:
                if char in self.square:
                    row, col = self.square[char]
                    coords.extend([row, col])
            
            # Split coordinates back into rows and columns
            mid = len(coords) // 2
            rows = coords[:mid]
            cols = coords[mid:]
            
            # Reconstruct original coordinates
            for j in range(len(rows)):
                if j < len(cols):
                    row = rows[j]
                    col = cols[j]
                    if (row, col) in self.reverse_square:
                        result.append(self.reverse_square[(row, col)])
        
        return ''.join(result)


class TrifidCipher:
    """Trifid cipher with configurable cube and period"""
    
    def __init__(self, alphabet: str = "kryptos27", period: int = 5):
        """
        Initialize Trifid cipher
        
        Args:
            alphabet: Keyword for cube or "kryptos27"
            period: Fractionation period
        """
        if alphabet == "kryptos27":
            keyword = "KRYPTOS"
        else:
            keyword = alphabet
            
        self.cube, self.reverse_cube = create_trifid_cube(keyword)
        self.period = period
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt using Trifid cipher"""
        plaintext = plaintext.upper()
        
        # Remove non-alphabetic characters
        clean_text = ''.join(c for c in plaintext if c.isalpha())
        
        # Convert to coordinates
        coords = []
        for char in clean_text:
            if char in self.cube:
                coords.append(self.cube[char])
        
        # Process in periods
        result = []
        for i in range(0, len(coords), self.period):
            block = coords[i:i+self.period]
            
            # Extract layers, rows, and columns
            layers = [coord[0] for coord in block]
            rows = [coord[1] for coord in block]
            cols = [coord[2] for coord in block]
            
            # Recombine (read layers, then rows, then columns)
            combined = layers + rows + cols
            
            # Convert back to letters
            for j in range(0, len(combined), 3):
                if j+2 < len(combined):
                    layer = combined[j]
                    row = combined[j+1]
                    col = combined[j+2]
                    if (layer, row, col) in self.reverse_cube:
                        result.append(self.reverse_cube[(layer, row, col)])
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt using Trifid cipher"""
        ciphertext = ciphertext.upper()
        
        # Remove non-alphabetic characters
        clean_text = ''.join(c for c in ciphertext if c.isalpha())
        
        result = []
        
        # Process in periods
        for i in range(0, len(clean_text), self.period):
            block = clean_text[i:i+self.period]
            
            # Convert block to coordinates
            coords = []
            for char in block:
                if char in self.cube:
                    layer, row, col = self.cube[char]
                    coords.extend([layer, row, col])
            
            # Split coordinates back into layers, rows, and columns
            third = len(coords) // 3
            layers = coords[:third]
            rows = coords[third:2*third]
            cols = coords[2*third:]
            
            # Reconstruct original coordinates
            for j in range(len(layers)):
                if j < len(rows) and j < len(cols):
                    layer = layers[j]
                    row = rows[j]
                    col = cols[j]
                    if (layer, row, col) in self.reverse_cube:
                        result.append(self.reverse_cube[(layer, row, col)])
        
        return ''.join(result)


class FourSquareCipher:
    """Four-Square cipher with two keyed squares"""
    
    def __init__(self, square_tr: str = "kryptos", square_bl: str = "kryptos"):
        """
        Initialize Four-Square cipher
        
        Args:
            square_tr: Top-right square keyword
            square_bl: Bottom-left square keyword
        """
        # Top-left and bottom-right are plain alphabets
        self.square_tl, self.reverse_tl = create_polybius_square("")  # Plain
        self.square_br, self.reverse_br = create_polybius_square("")  # Plain
        
        # Top-right and bottom-left are keyed
        if isinstance(square_tr, dict):
            tr_keyword = square_tr.get('keyword', 'KRYPTOS')
        else:
            tr_keyword = square_tr if square_tr != "kryptos" else "KRYPTOS"
            
        if isinstance(square_bl, dict):
            bl_keyword = square_bl.get('keyword', 'KRYPTOS')
        else:
            bl_keyword = square_bl if square_bl != "kryptos" else "KRYPTOS"
            
        self.square_tr, self.reverse_tr = create_polybius_square(tr_keyword)
        self.square_bl, self.reverse_bl = create_polybius_square(bl_keyword)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt using Four-Square cipher"""
        plaintext = plaintext.upper().replace('J', 'I')
        
        # Remove non-alphabetic and pad if odd length
        clean_text = ''.join(c for c in plaintext if c.isalpha())
        if len(clean_text) % 2 == 1:
            clean_text += 'X'
        
        result = []
        
        # Process digrams
        for i in range(0, len(clean_text), 2):
            char1 = clean_text[i]
            char2 = clean_text[i+1]
            
            # Get positions in plain squares
            if char1 in self.square_tl and char2 in self.square_br:
                row1, col1 = self.square_tl[char1]
                row2, col2 = self.square_br[char2]
                
                # Get ciphertext from keyed squares
                if (row1, col2) in self.reverse_tr and (row2, col1) in self.reverse_bl:
                    result.append(self.reverse_tr[(row1, col2)])
                    result.append(self.reverse_bl[(row2, col1)])
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt using Four-Square cipher"""
        ciphertext = ciphertext.upper().replace('J', 'I')
        
        # Remove non-alphabetic
        clean_text = ''.join(c for c in ciphertext if c.isalpha())
        
        result = []
        
        # Process digrams
        for i in range(0, len(clean_text), 2):
            if i+1 < len(clean_text):
                char1 = clean_text[i]
                char2 = clean_text[i+1]
                
                # Get positions in keyed squares
                if char1 in self.square_tr and char2 in self.square_bl:
                    row1, col1 = self.square_tr[char1]
                    row2, col2 = self.square_bl[char2]
                    
                    # Get plaintext from plain squares
                    if (row1, col2) in self.reverse_tl and (row2, col1) in self.reverse_br:
                        result.append(self.reverse_tl[(row1, col2)])
                        result.append(self.reverse_br[(row2, col1)])
        
        return ''.join(result)


def create_fractionation_cipher(config: Dict[str, Any]):
    """
    Factory function to create fractionation ciphers
    
    Args:
        config: Configuration dictionary with:
            - family: 'bifid', 'trifid', or 'foursquare'
            - polybius/alphabet: Square/cube configuration
            - period: Fractionation period (Bifid/Trifid)
            - square_tr/square_bl: Four-Square keys
    """
    family = config.get('family', 'bifid')
    
    if family == 'bifid':
        polybius = config.get('polybius', 'kryptos')
        period = config.get('period', 5)
        return BifidCipher(polybius, period)
    
    elif family == 'trifid':
        alphabet = config.get('alphabet', 'kryptos27')
        period = config.get('period', 5)
        return TrifidCipher(alphabet, period)
    
    elif family == 'foursquare':
        square_tr = config.get('square_tr', 'kryptos')
        square_bl = config.get('square_bl', 'kryptos')
        return FourSquareCipher(square_tr, square_bl)
    
    else:
        raise ValueError(f"Unknown fractionation family: {family}")


def encode(plaintext: str, config: Dict[str, Any]) -> str:
    """Encode using fractionation cipher"""
    cipher = create_fractionation_cipher(config)
    return cipher.encrypt(plaintext)


def decode(ciphertext: str, config: Dict[str, Any]) -> str:
    """Decode using fractionation cipher"""
    cipher = create_fractionation_cipher(config)
    direction = config.get('cipher_direction', 'decrypt')
    
    if direction == 'decrypt':
        return cipher.decrypt(ciphertext)
    else:
        return cipher.encrypt(ciphertext)  # For testing round-trip