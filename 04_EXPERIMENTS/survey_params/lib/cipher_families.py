#!/usr/bin/env python3
"""
cipher_families.py

Implementation of various cipher families parameterized by surveying quantities.
All position-changing ciphers include inversion methods to restore original positions.
"""

import math
from typing import List, Tuple, Dict, Optional
from collections import OrderedDict

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class PolyalphabeticCiphers:
    """Position-preserving polyalphabetic ciphers (Vigenère, Beaufort, Variant Beaufort)."""
    
    @staticmethod
    def vigenere_decrypt(ciphertext: str, L: int, phase: int = 0, offset: int = 0) -> str:
        """
        Vigenère decryption: P = (C - K) mod 26
        
        Args:
            ciphertext: Input ciphertext
            L: Key period length
            phase: Starting position in key cycle
            offset: Additional offset to each key value
        """
        plaintext = []
        for i, c in enumerate(ciphertext):
            if c.isalpha():
                # Calculate key value at this position
                k = ((i + phase) % L + offset) % 26
                # Decrypt
                p = (char_to_num(c) - k) % 26
                plaintext.append(num_to_char(p))
            else:
                plaintext.append(c)
        return ''.join(plaintext)
    
    @staticmethod
    def beaufort_decrypt(ciphertext: str, L: int, phase: int = 0, offset: int = 0) -> str:
        """
        Beaufort decryption: P = (K - C) mod 26
        """
        plaintext = []
        for i, c in enumerate(ciphertext):
            if c.isalpha():
                k = ((i + phase) % L + offset) % 26
                p = (k - char_to_num(c)) % 26
                plaintext.append(num_to_char(p))
            else:
                plaintext.append(c)
        return ''.join(plaintext)
    
    @staticmethod
    def variant_beaufort_decrypt(ciphertext: str, L: int, phase: int = 0, offset: int = 0) -> str:
        """
        Variant Beaufort: P = (C + K) mod 26
        """
        plaintext = []
        for i, c in enumerate(ciphertext):
            if c.isalpha():
                k = ((i + phase) % L + offset) % 26
                p = (char_to_num(c) + k) % 26
                plaintext.append(num_to_char(p))
            else:
                plaintext.append(c)
        return ''.join(plaintext)
    
    @staticmethod
    def segmented_polyalphabetic(ciphertext: str, segments: List[Tuple[int, int, Dict]], 
                               variant: str = 'vigenere') -> str:
        """
        Apply different polyalphabetic parameters to different segments.
        
        Args:
            segments: List of (start, end, params_dict) tuples
            variant: Which polyalphabetic variant to use
        """
        result = list(ciphertext)
        
        for start, end, params in segments:
            segment = ciphertext[start:end]
            
            if variant == 'vigenere':
                decrypted = PolyalphabeticCiphers.vigenere_decrypt(
                    segment, params['L'], params.get('phase', 0), params.get('offset', 0))
            elif variant == 'beaufort':
                decrypted = PolyalphabeticCiphers.beaufort_decrypt(
                    segment, params['L'], params.get('phase', 0), params.get('offset', 0))
            else:
                decrypted = PolyalphabeticCiphers.variant_beaufort_decrypt(
                    segment, params['L'], params.get('phase', 0), params.get('offset', 0))
            
            for i, char in enumerate(decrypted):
                if start + i < len(result):
                    result[start + i] = char
        
        return ''.join(result)

class TranspositionCiphers:
    """Transposition ciphers with inversion capability."""
    
    @staticmethod
    def columnar_transposition(text: str, num_cols: int, key_order: List[int] = None) -> Tuple[str, List[int]]:
        """
        Columnar transposition with inversion mapping.
        
        Returns:
            (transposed_text, inverse_mapping)
        """
        # Remove non-alpha for transposition
        clean_text = ''.join(c for c in text if c.isalpha())
        n = len(clean_text)
        
        # Pad if necessary
        if n % num_cols != 0:
            clean_text += 'X' * (num_cols - (n % num_cols))
        
        # Create grid
        grid = []
        for i in range(0, len(clean_text), num_cols):
            grid.append(list(clean_text[i:i+num_cols]))
        
        # Default key order if not provided
        if key_order is None:
            key_order = list(range(num_cols))
        
        # Read columns in key order
        result = []
        inverse_map = []
        
        for col_idx in key_order:
            for row in grid:
                if col_idx < len(row):
                    result.append(row[col_idx])
                    # Track original position
                    orig_pos = grid.index(row) * num_cols + col_idx
                    inverse_map.append(orig_pos)
        
        return ''.join(result), inverse_map
    
    @staticmethod
    def invert_transposition(transposed: str, inverse_map: List[int], original_length: int = None) -> str:
        """
        Invert a transposition using the inverse mapping.
        """
        if original_length is None:
            original_length = len(transposed)
        
        result = [''] * original_length
        for i, char in enumerate(transposed):
            if i < len(inverse_map) and inverse_map[i] < original_length:
                result[inverse_map[i]] = char
        
        return ''.join(result)
    
    @staticmethod
    def rail_fence(text: str, rails: int) -> Tuple[str, List[int]]:
        """
        Rail fence cipher with inversion mapping.
        """
        clean_text = ''.join(c for c in text if c.isalpha())
        n = len(clean_text)
        
        # Create fence pattern
        fence = [['' for _ in range(n)] for _ in range(rails)]
        inverse_map = []
        
        # Fill the fence
        rail = 0
        direction = 1
        for i, char in enumerate(clean_text):
            fence[rail][i] = char
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction = -direction
        
        # Read off the fence
        result = []
        pos = 0
        for row in fence:
            for col, char in enumerate(row):
                if char:
                    result.append(char)
                    inverse_map.append(col)
                    pos += 1
        
        return ''.join(result), inverse_map
    
    @staticmethod
    def route_cipher(text: str, rows: int, cols: int, route: str = 'spiral_in') -> Tuple[str, List[int]]:
        """
        Route cipher with various reading patterns.
        
        Args:
            route: 'spiral_in', 'spiral_out', 'snake', 'diagonal'
        """
        clean_text = ''.join(c for c in text if c.isalpha())
        
        # Pad if necessary
        grid_size = rows * cols
        if len(clean_text) < grid_size:
            clean_text += 'X' * (grid_size - len(clean_text))
        clean_text = clean_text[:grid_size]
        
        # Create grid
        grid = []
        for i in range(rows):
            grid.append(list(clean_text[i*cols:(i+1)*cols]))
        
        result = []
        inverse_map = []
        
        if route == 'spiral_in':
            # Spiral inward from top-left
            top, bottom, left, right = 0, rows-1, 0, cols-1
            while top <= bottom and left <= right:
                # Top row
                for col in range(left, right+1):
                    if top <= bottom and col <= right:
                        result.append(grid[top][col])
                        inverse_map.append(top * cols + col)
                top += 1
                
                # Right column
                for row in range(top, bottom+1):
                    if left <= right and row <= bottom:
                        result.append(grid[row][right])
                        inverse_map.append(row * cols + right)
                right -= 1
                
                # Bottom row
                if top <= bottom:
                    for col in range(right, left-1, -1):
                        if col >= left:
                            result.append(grid[bottom][col])
                            inverse_map.append(bottom * cols + col)
                    bottom -= 1
                
                # Left column
                if left <= right:
                    for row in range(bottom, top-1, -1):
                        if row >= top:
                            result.append(grid[row][left])
                            inverse_map.append(row * cols + left)
                    left += 1
        
        elif route == 'snake':
            # Snake pattern (zigzag rows)
            for i in range(rows):
                if i % 2 == 0:
                    for j in range(cols):
                        result.append(grid[i][j])
                        inverse_map.append(i * cols + j)
                else:
                    for j in range(cols-1, -1, -1):
                        result.append(grid[i][j])
                        inverse_map.append(i * cols + j)
        
        elif route == 'diagonal':
            # Diagonal reading
            for diag_sum in range(rows + cols - 1):
                for row in range(rows):
                    col = diag_sum - row
                    if 0 <= col < cols:
                        result.append(grid[row][col])
                        inverse_map.append(row * cols + col)
        
        else:  # Default to row-major
            for i in range(rows):
                for j in range(cols):
                    result.append(grid[i][j])
                    inverse_map.append(i * cols + j)
        
        return ''.join(result), inverse_map

class SubstitutionCiphers:
    """Various substitution ciphers."""
    
    @staticmethod
    def caesar_shift(text: str, shift: int) -> str:
        """Simple Caesar shift."""
        result = []
        for c in text:
            if c.isalpha():
                result.append(num_to_char((char_to_num(c) - shift) % 26))
            else:
                result.append(c)
        return ''.join(result)
    
    @staticmethod
    def affine_decrypt(ciphertext: str, a: int, b: int) -> str:
        """
        Affine decryption: P = a^(-1) * (C - b) mod 26
        
        Args:
            a: Multiplicative key (must be coprime with 26)
            b: Additive key
        """
        # Find modular inverse of a
        a_inv = SubstitutionCiphers._mod_inverse(a, 26)
        if a_inv is None:
            raise ValueError(f"a={a} is not coprime with 26")
        
        result = []
        for c in ciphertext:
            if c.isalpha():
                p = (a_inv * (char_to_num(c) - b)) % 26
                result.append(num_to_char(p))
            else:
                result.append(c)
        return ''.join(result)
    
    @staticmethod
    def periodic_affine(ciphertext: str, a: int, b: int, period: int) -> str:
        """
        Affine cipher that resets every 'period' characters.
        """
        a_inv = SubstitutionCiphers._mod_inverse(a, 26)
        if a_inv is None:
            raise ValueError(f"a={a} is not coprime with 26")
        
        result = []
        pos = 0
        for c in ciphertext:
            if c.isalpha():
                # Reset affine parameters at period boundaries
                if pos > 0 and pos % period == 0:
                    # Could modify a, b here based on position
                    pass
                p = (a_inv * (char_to_num(c) - b)) % 26
                result.append(num_to_char(p))
                pos += 1
            else:
                result.append(c)
        return ''.join(result)
    
    @staticmethod
    def _mod_inverse(a: int, m: int) -> Optional[int]:
        """Find modular inverse of a mod m using extended Euclidean algorithm."""
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            return None  # No inverse exists
        return (x % m + m) % m
    
    @staticmethod
    def _is_coprime(a: int, b: int) -> bool:
        """Check if a and b are coprime."""
        return math.gcd(a, b) == 1
    
    @staticmethod
    def make_coprime(n: int, m: int = 26) -> int:
        """Find nearest coprime to n with respect to m."""
        if SubstitutionCiphers._is_coprime(n % m, m):
            return n % m
        
        # Try adjacent values
        for delta in range(1, m):
            if SubstitutionCiphers._is_coprime((n + delta) % m, m):
                return (n + delta) % m
            if SubstitutionCiphers._is_coprime((n - delta) % m, m):
                return (n - delta) % m
        
        return 1  # Fallback to 1 (always coprime with any m)

class MatrixCiphers:
    """Matrix-based polygraphic ciphers."""
    
    @staticmethod
    def hill_2x2_decrypt(ciphertext: str, key_matrix: List[List[int]]) -> str:
        """
        Hill cipher decryption with 2x2 matrix.
        """
        # Check matrix is invertible mod 26
        det = (key_matrix[0][0] * key_matrix[1][1] - key_matrix[0][1] * key_matrix[1][0]) % 26
        det_inv = SubstitutionCiphers._mod_inverse(det, 26)
        
        if det_inv is None:
            raise ValueError("Key matrix is not invertible mod 26")
        
        # Calculate inverse matrix
        inv_matrix = [
            [(key_matrix[1][1] * det_inv) % 26, (-key_matrix[0][1] * det_inv) % 26],
            [(-key_matrix[1][0] * det_inv) % 26, (key_matrix[0][0] * det_inv) % 26]
        ]
        
        # Process digraphs
        clean_text = ''.join(c for c in ciphertext if c.isalpha())
        if len(clean_text) % 2 != 0:
            clean_text += 'X'
        
        result = []
        for i in range(0, len(clean_text), 2):
            c1, c2 = char_to_num(clean_text[i]), char_to_num(clean_text[i+1])
            
            # Matrix multiplication
            p1 = (inv_matrix[0][0] * c1 + inv_matrix[0][1] * c2) % 26
            p2 = (inv_matrix[1][0] * c1 + inv_matrix[1][1] * c2) % 26
            
            result.append(num_to_char(p1))
            result.append(num_to_char(p2))
        
        return ''.join(result)
    
    @staticmethod
    def playfair_decrypt(ciphertext: str, keyword: str) -> str:
        """
        Playfair cipher decryption.
        """
        # Build 5x5 grid (I/J combined)
        grid = MatrixCiphers._build_playfair_grid(keyword)
        grid_pos = {}
        for i in range(5):
            for j in range(5):
                grid_pos[grid[i][j]] = (i, j)
                if grid[i][j] == 'I':
                    grid_pos['J'] = (i, j)
        
        # Process digraphs
        clean_text = ''.join(c.upper() for c in ciphertext if c.isalpha())
        clean_text = clean_text.replace('J', 'I')
        
        result = []
        i = 0
        while i < len(clean_text):
            if i + 1 < len(clean_text):
                c1, c2 = clean_text[i], clean_text[i+1]
                
                if c1 == c2:
                    c2 = 'X'
                    i += 1
                else:
                    i += 2
                
                r1, c1_pos = grid_pos[c1]
                r2, c2_pos = grid_pos[c2]
                
                if r1 == r2:  # Same row
                    result.append(grid[r1][(c1_pos - 1) % 5])
                    result.append(grid[r2][(c2_pos - 1) % 5])
                elif c1_pos == c2_pos:  # Same column
                    result.append(grid[(r1 - 1) % 5][c1_pos])
                    result.append(grid[(r2 - 1) % 5][c2_pos])
                else:  # Rectangle
                    result.append(grid[r1][c2_pos])
                    result.append(grid[r2][c1_pos])
            else:
                result.append(clean_text[i])
                i += 1
        
        return ''.join(result)
    
    @staticmethod
    def _build_playfair_grid(keyword: str) -> List[List[str]]:
        """Build 5x5 Playfair grid from keyword."""
        # Remove duplicates from keyword
        seen = set()
        key_letters = []
        for c in keyword.upper():
            if c.isalpha() and c not in seen and c != 'J':
                seen.add(c)
                key_letters.append(c)
        
        # Add remaining letters
        for c in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
            if c not in seen:
                key_letters.append(c)
        
        # Build grid
        grid = []
        for i in range(5):
            grid.append(key_letters[i*5:(i+1)*5])
        
        return grid

class HybridPipeline:
    """Two-stage hybrid cipher pipeline with position restoration."""
    
    @staticmethod
    def surveying_chain(ciphertext: str, stage1_params: Dict, stage2_params: Dict) -> str:
        """
        Two-stage cipher chain with position restoration.
        
        Stage 1: Position-changing cipher (transposition, matrix, etc.)
        Stage 2: Position-preserving cipher (polyalphabetic, affine)
        
        Returns plaintext with original position alignment.
        """
        # Stage 1: Position-changing transformation
        stage1_type = stage1_params.get('type', 'none')
        
        if stage1_type == 'columnar':
            temp, inv_map = TranspositionCiphers.columnar_transposition(
                ciphertext, 
                stage1_params['columns'],
                stage1_params.get('key_order')
            )
        elif stage1_type == 'rail_fence':
            temp, inv_map = TranspositionCiphers.rail_fence(
                ciphertext,
                stage1_params['rails']
            )
        elif stage1_type == 'route':
            temp, inv_map = TranspositionCiphers.route_cipher(
                ciphertext,
                stage1_params['rows'],
                stage1_params['cols'],
                stage1_params.get('route', 'spiral_in')
            )
        elif stage1_type == 'hill':
            temp = MatrixCiphers.hill_2x2_decrypt(
                ciphertext,
                stage1_params['matrix']
            )
            inv_map = list(range(len(temp)))  # Identity mapping for now
        elif stage1_type == 'playfair':
            temp = MatrixCiphers.playfair_decrypt(
                ciphertext,
                stage1_params['keyword']
            )
            inv_map = list(range(len(temp)))
        else:
            temp = ciphertext
            inv_map = list(range(len(ciphertext)))
        
        # Stage 2: Position-preserving transformation
        stage2_type = stage2_params.get('type', 'vigenere')
        
        if stage2_type == 'vigenere':
            temp2 = PolyalphabeticCiphers.vigenere_decrypt(
                temp,
                stage2_params['L'],
                stage2_params.get('phase', 0),
                stage2_params.get('offset', 0)
            )
        elif stage2_type == 'beaufort':
            temp2 = PolyalphabeticCiphers.beaufort_decrypt(
                temp,
                stage2_params['L'],
                stage2_params.get('phase', 0),
                stage2_params.get('offset', 0)
            )
        elif stage2_type == 'affine':
            temp2 = SubstitutionCiphers.affine_decrypt(
                temp,
                stage2_params['a'],
                stage2_params['b']
            )
        elif stage2_type == 'caesar':
            temp2 = SubstitutionCiphers.caesar_shift(
                temp,
                stage2_params['shift']
            )
        else:
            temp2 = temp
        
        # Restore original positions if Stage 1 changed them
        if stage1_type in ['columnar', 'rail_fence', 'route']:
            # Invert the transposition
            restored = TranspositionCiphers.invert_transposition(
                temp2, inv_map, len(ciphertext)
            )
        else:
            restored = temp2
        
        # Ensure we have exactly the original length
        if len(restored) < len(ciphertext):
            restored += 'X' * (len(ciphertext) - len(restored))
        elif len(restored) > len(ciphertext):
            restored = restored[:len(ciphertext)]
        
        return restored