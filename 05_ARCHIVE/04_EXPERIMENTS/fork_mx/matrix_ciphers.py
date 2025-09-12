#!/usr/bin/env python3
"""
matrix_ciphers.py

Fork MX - Matrix ciphers (Playfair/Two-square/Four-square/Hill) using Kryptos tableau.
Polygraphic ciphers with tableau-derived keys.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional

# Kryptos tableau (from the sculpture)
KRYPTOS_TABLEAU = [
    "KRYPTOSABCDEFGHIJLMNQUVWXZ",  # Row 0 (I/J merged)
    "PTOSABCDEFGHIJLMNQUVWXZKRY",  # Row 1
    "SABCDEFGHIJLMNQUVWXZKRYPTO",  # Row 2
    "CDEFGHIJLMNQUVWXZKRYPTOSAB",  # Row 3
    "FGHIJLMNQUVWXZKRYPTOSABCDE",  # Row 4
    "IJLMNQUVWXZKRYPTOSABCDEFGH",  # Row 5
    "MNQUVWXZKRYPTOSABCDEFGHIJL",  # Row 6
    "UVWXZKRYPTOSABCDEFGHIJLMNQ",  # Row 7
    "ZKRYPTOSABCDEFGHIJLMNQUVWX",  # Row 8
    "YPTOSABCDEFGHIJLMNQUVWXZKR"   # Row 9
]

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class PlayfairCipher:
    """Playfair cipher using 5x5 grids."""
    
    def __init__(self, key: str, merge_ij: bool = True):
        """
        Initialize Playfair with key.
        
        Args:
            key: Key string for grid generation
            merge_ij: Whether to merge I/J (standard)
        """
        self.key = key.upper()
        self.merge_ij = merge_ij
        self.grid = self._create_grid()
        self.pos_map = self._create_position_map()
    
    def _create_grid(self) -> List[List[str]]:
        """Create 5x5 Playfair grid from key."""
        # Remove duplicates from key
        seen = set()
        key_letters = []
        for c in self.key:
            if c not in seen and c.isalpha():
                if self.merge_ij and c == 'J':
                    c = 'I'
                seen.add(c)
                key_letters.append(c)
        
        # Add remaining alphabet
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ' if self.merge_ij else 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for c in alphabet:
            if c not in seen:
                key_letters.append(c)
        
        # Create 5x5 grid
        grid = []
        for row in range(5):
            grid.append(key_letters[row*5:(row+1)*5])
        
        return grid
    
    def _create_position_map(self) -> Dict[str, Tuple[int, int]]:
        """Create letter to position mapping."""
        pos_map = {}
        for r in range(5):
            for c in range(5):
                letter = self.grid[r][c]
                pos_map[letter] = (r, c)
                if self.merge_ij and letter == 'I':
                    pos_map['J'] = (r, c)
        return pos_map
    
    def _prepare_text(self, text: str) -> List[str]:
        """Prepare text for Playfair encryption/decryption."""
        prepared = []
        text = text.upper()
        
        i = 0
        while i < len(text):
            if not text[i].isalpha():
                i += 1
                continue
            
            c1 = text[i]
            if self.merge_ij and c1 == 'J':
                c1 = 'I'
            
            # Find next letter
            j = i + 1
            while j < len(text) and not text[j].isalpha():
                j += 1
            
            if j < len(text):
                c2 = text[j]
                if self.merge_ij and c2 == 'J':
                    c2 = 'I'
                
                # Handle duplicate letters
                if c1 == c2:
                    prepared.extend([c1, 'X'])
                    i = j  # Only consumed one letter
                else:
                    prepared.extend([c1, c2])
                    i = j + 1
            else:
                # Odd letter at end
                prepared.extend([c1, 'X'])
                i = j
        
        return prepared
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext using Playfair."""
        prepared = self._prepare_text(ciphertext)
        plaintext = []
        
        for i in range(0, len(prepared), 2):
            if i + 1 >= len(prepared):
                break
            
            c1, c2 = prepared[i], prepared[i+1]
            r1, c1_col = self.pos_map[c1]
            r2, c2_col = self.pos_map[c2]
            
            if r1 == r2:
                # Same row - shift left
                p1 = self.grid[r1][(c1_col - 1) % 5]
                p2 = self.grid[r2][(c2_col - 1) % 5]
            elif c1_col == c2_col:
                # Same column - shift up
                p1 = self.grid[(r1 - 1) % 5][c1_col]
                p2 = self.grid[(r2 - 1) % 5][c2_col]
            else:
                # Rectangle - swap columns
                p1 = self.grid[r1][c2_col]
                p2 = self.grid[r2][c1_col]
            
            plaintext.extend([p1, p2])
        
        return ''.join(plaintext)

class TwoSquareCipher:
    """Two-square cipher using two 5x5 grids."""
    
    def __init__(self, key1: str, key2: str):
        """Initialize with two keys."""
        self.square1 = PlayfairCipher(key1)
        self.square2 = PlayfairCipher(key2)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt using two-square."""
        prepared = self.square1._prepare_text(ciphertext)
        plaintext = []
        
        for i in range(0, len(prepared), 2):
            if i + 1 >= len(prepared):
                break
            
            c1, c2 = prepared[i], prepared[i+1]
            
            # Find positions in respective squares
            if c1 in self.square1.pos_map:
                r1, c1_col = self.square1.pos_map[c1]
                grid1 = self.square1.grid
            else:
                continue
            
            if c2 in self.square2.pos_map:
                r2, c2_col = self.square2.pos_map[c2]
                grid2 = self.square2.grid
            else:
                continue
            
            # Decrypt by swapping columns between squares
            if r1 == r2:
                # Same row - use opposite square columns
                p1 = grid2[r1][c1_col]
                p2 = grid1[r2][c2_col]
            else:
                # Different rows - form rectangle
                p1 = grid2[r1][c2_col]
                p2 = grid1[r2][c1_col]
            
            plaintext.extend([p1, p2])
        
        return ''.join(plaintext)

class HillCipher:
    """Hill cipher with 2x2 or 3x3 matrices."""
    
    def __init__(self, matrix: np.ndarray):
        """
        Initialize with key matrix.
        
        Args:
            matrix: 2x2 or 3x3 numpy array
        """
        self.matrix = matrix
        self.size = matrix.shape[0]
        
        # Check if matrix is invertible mod 26
        det = int(round(np.linalg.det(matrix))) % 26
        if det == 0 or self._gcd(det, 26) != 1:
            raise ValueError("Matrix is not invertible mod 26")
        
        # Compute inverse matrix mod 26
        self.inv_matrix = self._matrix_inverse_mod26(matrix)
    
    def _gcd(self, a: int, b: int) -> int:
        """Compute GCD."""
        while b:
            a, b = b, a % b
        return a
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """Compute modular inverse of a mod m."""
        for i in range(1, m):
            if (a * i) % m == 1:
                return i
        return None
    
    def _matrix_inverse_mod26(self, matrix: np.ndarray) -> np.ndarray:
        """Compute matrix inverse mod 26."""
        det = int(round(np.linalg.det(matrix))) % 26
        det_inv = self._mod_inverse(det, 26)
        
        if self.size == 2:
            # 2x2 inverse formula
            adj = np.array([
                [matrix[1, 1], -matrix[0, 1]],
                [-matrix[1, 0], matrix[0, 0]]
            ])
        else:
            # 3x3 would need cofactor matrix
            # Simplified for now
            raise NotImplementedError("3x3 inverse not fully implemented")
        
        inv_matrix = (det_inv * adj) % 26
        return inv_matrix.astype(int)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt using Hill cipher."""
        text = ''.join(c for c in ciphertext.upper() if c.isalpha())
        
        # Pad if necessary
        if len(text) % self.size != 0:
            text += 'X' * (self.size - len(text) % self.size)
        
        plaintext = []
        
        for i in range(0, len(text), self.size):
            # Get block
            block = text[i:i+self.size]
            vec = np.array([char_to_num(c) for c in block])
            
            # Decrypt: P = inv(K) * C mod 26
            p_vec = np.dot(self.inv_matrix, vec) % 26
            
            # Convert back to letters
            for val in p_vec:
                plaintext.append(num_to_char(int(val)))
        
        return ''.join(plaintext)

def generate_tableau_keys() -> List[Dict]:
    """Generate keys from Kryptos tableau."""
    keys = []
    
    # Use KRYPTOS itself
    keys.append({
        'name': 'KRYPTOS',
        'key': 'KRYPTOS',
        'source': 'base'
    })
    
    # Use YARD (from raised letters)
    keys.append({
        'name': 'YARD',
        'key': 'YARD',
        'source': 'raised'
    })
    
    # Combine KRYPTOS + YARD
    keys.append({
        'name': 'KRYPTOS_YARD',
        'key': 'KRYPTOSYARD',
        'source': 'combined'
    })
    
    # Use BERLINCLOCK
    keys.append({
        'name': 'BERLINCLOCK',
        'key': 'BERLINCLOCK',
        'source': 'anchor'
    })
    
    # Use PALIMPSEST
    keys.append({
        'name': 'PALIMPSEST',
        'key': 'PALIMPSEST',
        'source': 'keyword'
    })
    
    # Tableau row-derived (using first letters of each row)
    tableau_key = ''.join(row[0] for row in KRYPTOS_TABLEAU)
    keys.append({
        'name': 'TABLEAU_ROWS',
        'key': tableau_key,
        'source': 'tableau'
    })
    
    return keys

def generate_hill_matrices() -> List[np.ndarray]:
    """Generate Hill cipher matrices."""
    matrices = []
    
    # From YARD positions (Y=24, A=0, R=17, D=3)
    matrices.append(np.array([
        [24, 0],
        [17, 3]
    ]))
    
    # Simple invertible matrices
    matrices.append(np.array([
        [3, 2],
        [5, 7]
    ]))
    
    matrices.append(np.array([
        [11, 8],
        [3, 7]
    ]))
    
    # From anchor positions
    matrices.append(np.array([
        [21, 25],  # EAST, NORTHEAST starts
        [63, 69]   # BERLIN, CLOCK starts
    ]))
    
    return matrices

def test_matrix_ciphers():
    """Test matrix ciphers."""
    print("Testing Matrix Ciphers")
    print("-" * 50)
    
    # Test ciphertext (K4)
    test_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # Test Playfair
    pf = PlayfairCipher("KRYPTOS")
    plaintext = pf.decrypt(test_ct)
    print(f"Playfair (KRYPTOS): {plaintext[:30]}...")
    
    # Test Two-square
    ts = TwoSquareCipher("KRYPTOS", "BERLINCLOCK")
    plaintext = ts.decrypt(test_ct)
    print(f"Two-square: {plaintext[:30]}...")
    
    # Test Hill 2x2
    try:
        hill_matrix = np.array([[3, 2], [5, 7]])
        hill = HillCipher(hill_matrix)
        plaintext = hill.decrypt(test_ct)
        print(f"Hill 2x2: {plaintext[:30]}...")
    except Exception as e:
        print(f"Hill error: {e}")

if __name__ == "__main__":
    test_matrix_ciphers()