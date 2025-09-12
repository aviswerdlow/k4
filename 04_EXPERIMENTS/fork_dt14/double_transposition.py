#!/usr/bin/env python3
"""
double_transposition.py

Fork DT14 - Double-Transposition with L=14.
Anchor-aware chaining with columnar transposition.
"""

import math
from typing import List, Tuple, Dict, Optional

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

class ColumnarTransposition:
    """Columnar transposition cipher with anchor awareness."""
    
    def __init__(self, key: str, num_columns: Optional[int] = None):
        """
        Initialize with key and optional column count.
        
        Args:
            key: Key string for column ordering
            num_columns: Force specific number of columns
        """
        self.key = key.upper()
        self.num_columns = num_columns if num_columns else len(self.key)
        self.column_order = self._compute_column_order()
    
    def _compute_column_order(self) -> List[int]:
        """Compute column read order from key."""
        # Alphabetical ranking
        key_letters = list(self.key[:self.num_columns])
        
        # Create (letter, original_position) pairs
        indexed = [(letter, i) for i, letter in enumerate(key_letters)]
        
        # Sort alphabetically, then by original position for ties
        indexed.sort(key=lambda x: (x[0], x[1]))
        
        # Create order array
        order = [0] * self.num_columns
        for rank, (_, orig_pos) in enumerate(indexed):
            order[orig_pos] = rank
        
        return order
    
    def _compute_numeric_order(self) -> List[int]:
        """Compute column order using A1Z26 numeric values."""
        # A=1, B=2, ..., Z=26
        key_values = [char_to_num(c) + 1 for c in self.key[:self.num_columns]]
        
        # Create (value, original_position) pairs
        indexed = [(val, i) for i, val in enumerate(key_values)]
        
        # Sort by value, then by position
        indexed.sort(key=lambda x: (x[0], x[1]))
        
        # Create order array
        order = [0] * self.num_columns
        for rank, (_, orig_pos) in enumerate(indexed):
            order[orig_pos] = rank
        
        return order
    
    def encrypt(self, plaintext: str) -> Tuple[str, List[int]]:
        """
        Encrypt plaintext and return position mapping.
        
        Returns:
            (ciphertext, position_map) where position_map[i] = original position of char i
        """
        text = plaintext.upper()
        n = len(text)
        
        # Calculate grid dimensions
        num_rows = math.ceil(n / self.num_columns)
        
        # Pad if necessary
        padding_needed = (num_rows * self.num_columns) - n
        if padding_needed > 0:
            text += 'X' * padding_needed
        
        # Fill grid row by row
        grid = []
        for row in range(num_rows):
            start = row * self.num_columns
            end = start + self.num_columns
            grid.append(list(text[start:end]))
        
        # Read columns in key order
        ciphertext = []
        position_map = []
        
        # Get column indices in read order
        read_order = sorted(range(self.num_columns), key=lambda i: self.column_order[i])
        
        for col_idx in read_order:
            for row in range(num_rows):
                if row * self.num_columns + col_idx < n:  # Skip padding
                    char = grid[row][col_idx]
                    orig_pos = row * self.num_columns + col_idx
                    ciphertext.append(char)
                    position_map.append(orig_pos)
        
        return ''.join(ciphertext), position_map
    
    def decrypt(self, ciphertext: str) -> Tuple[str, List[int]]:
        """
        Decrypt ciphertext and return position mapping.
        
        Returns:
            (plaintext, position_map) where position_map[i] = where char i should go
        """
        text = ciphertext.upper()
        n = len(text)
        
        # Calculate grid dimensions
        num_rows = math.ceil(n / self.num_columns)
        total_cells = num_rows * self.num_columns
        padding = total_cells - n
        
        # Initialize grid
        grid = [['' for _ in range(self.num_columns)] for _ in range(num_rows)]
        
        # Calculate how many chars go in each column
        chars_per_col = [num_rows] * self.num_columns
        
        # Last columns might have one less if there's padding
        if padding > 0:
            for i in range(self.num_columns - padding, self.num_columns):
                chars_per_col[i] -= 1
        
        # Get column indices in read order
        read_order = sorted(range(self.num_columns), key=lambda i: self.column_order[i])
        
        # Fill columns in key order
        char_idx = 0
        for col_idx in read_order:
            for row in range(chars_per_col[col_idx]):
                if char_idx < n:
                    grid[row][col_idx] = text[char_idx]
                    char_idx += 1
        
        # Read grid row by row
        plaintext = []
        position_map = []
        
        for row in range(num_rows):
            for col in range(self.num_columns):
                if grid[row][col]:  # Skip empty cells
                    plaintext.append(grid[row][col])
                    # This character should go at position row*num_columns + col
                    position_map.append(row * self.num_columns + col)
        
        return ''.join(plaintext)[:n], position_map

class DoubleTransposition:
    """Double transposition with anchor preservation checking."""
    
    def __init__(self, key1: str, key2: str, cols1: Optional[int] = None, cols2: Optional[int] = None):
        """
        Initialize double transposition.
        
        Args:
            key1: First transposition key
            key2: Second transposition key
            cols1: Column count for first transposition
            cols2: Column count for second transposition
        """
        self.trans1 = ColumnarTransposition(key1, cols1)
        self.trans2 = ColumnarTransposition(key2, cols2)
    
    def check_anchor_feasibility(self, anchors: Dict[str, List[int]]) -> bool:
        """
        Check if this DT configuration can preserve anchors.
        
        Args:
            anchors: Dictionary of anchor text to [start, end] positions
        
        Returns:
            True if anchors can potentially be preserved
        """
        # For now, we'll do a simplified check
        # A more complete check would trace through both transpositions
        
        # Check if column counts are compatible with anchor lengths
        anchor_lengths = {
            'EAST': 4,
            'NORTHEAST': 9,
            'BERLIN': 6,
            'CLOCK': 5
        }
        
        # Basic feasibility: columns shouldn't split short anchors badly
        for anchor, length in anchor_lengths.items():
            if self.trans1.num_columns > 1 and length < self.trans1.num_columns:
                # Short anchor might get split
                if length < self.trans1.num_columns // 2:
                    return False
        
        return True
    
    def decrypt_with_inverse(self, ciphertext: str) -> str:
        """
        Decrypt using (DT^-1) - inverse double transposition.
        
        Apply two transposition decryptions in sequence.
        """
        # First transposition decryption
        intermediate, _ = self.trans1.decrypt(ciphertext)
        
        # Second transposition decryption  
        plaintext, _ = self.trans2.decrypt(intermediate)
        
        return plaintext
    
    def decrypt_chained_vigenere(self, ciphertext: str, vigenere_key: str, 
                                order: str = 'dt_first') -> str:
        """
        Decrypt with chained Vigenère.
        
        Args:
            ciphertext: Input ciphertext
            vigenere_key: Key for Vigenère component
            order: 'dt_first' for (DT^-1) ∘ VIG, 'vig_first' for VIG ∘ (DT^-1)
        """
        if order == 'dt_first':
            # First apply double transposition inverse
            intermediate = self.decrypt_with_inverse(ciphertext)
            # Then apply Vigenère decryption
            plaintext = self._vigenere_decrypt(intermediate, vigenere_key)
        else:  # vig_first
            # First apply Vigenère decryption
            intermediate = self._vigenere_decrypt(ciphertext, vigenere_key)
            # Then apply double transposition inverse
            plaintext = self.decrypt_with_inverse(intermediate)
        
        return plaintext
    
    def decrypt_chained_beaufort(self, ciphertext: str, beaufort_key: str,
                                 order: str = 'dt_first') -> str:
        """
        Decrypt with chained Beaufort.
        
        Args:
            ciphertext: Input ciphertext
            beaufort_key: Key for Beaufort component
            order: 'dt_first' for (DT^-1) ∘ BEAU, 'beau_first' for BEAU ∘ (DT^-1)
        """
        if order == 'dt_first':
            # First apply double transposition inverse
            intermediate = self.decrypt_with_inverse(ciphertext)
            # Then apply Beaufort decryption
            plaintext = self._beaufort_decrypt(intermediate, beaufort_key)
        else:  # beau_first
            # First apply Beaufort decryption
            intermediate = self._beaufort_decrypt(ciphertext, beaufort_key)
            # Then apply double transposition inverse
            plaintext = self.decrypt_with_inverse(intermediate)
        
        return plaintext
    
    def _vigenere_decrypt(self, text: str, key: str) -> str:
        """Simple Vigenère decryption."""
        plaintext = []
        key_len = len(key)
        
        for i, c in enumerate(text):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            c_val = char_to_num(c)
            k_val = char_to_num(key[i % key_len])
            p_val = (c_val - k_val) % 26
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def _beaufort_decrypt(self, text: str, key: str) -> str:
        """Simple Beaufort decryption."""
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

def generate_dt_keys() -> List[Dict]:
    """Generate double transposition key configurations."""
    configs = []
    
    # Base keys to test
    base_keys = [
        "KRYPTOS",
        "WEBSTER", 
        "BERLINCLOCK",
        "NORTHEAST",
        "YARD",
        "PALIMPSEST",
        "ABSCISSA"
    ]
    
    # Column counts around 14 (IC signal)
    column_counts = [7, 14, 21]  # Factors and multiples of 7
    
    # Also test specific column counts
    special_counts = [11, 13, 14, 15, 17]  # Around 14
    
    for key1 in base_keys:
        for key2 in base_keys:
            # Test with column counts
            for cols in column_counts:
                configs.append({
                    'key1': key1,
                    'key2': key2,
                    'cols1': cols,
                    'cols2': cols,
                    'name': f"{key1[:4]}-{key2[:4]}-{cols}"
                })
            
            # Test with mixed column counts
            if key1 != key2:
                configs.append({
                    'key1': key1,
                    'key2': key2,
                    'cols1': 14,
                    'cols2': 7,
                    'name': f"{key1[:4]}-{key2[:4]}-14x7"
                })
    
    # Special L=14 configurations
    for cols in special_counts:
        configs.append({
            'key1': "KRYPTOS",
            'key2': "PALIMPSEST",
            'cols1': cols,
            'cols2': cols,
            'name': f"KRYP-PALI-{cols}"
        })
    
    return configs

def test_double_transposition():
    """Test double transposition."""
    print("Testing Double Transposition")
    print("-" * 50)
    
    # Test ciphertext (K4)
    test_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # Test with KRYPTOS key, 14 columns
    dt = DoubleTransposition("KRYPTOS", "PALIMPSEST", 14, 14)
    
    # Test basic decryption
    plaintext = dt.decrypt_with_inverse(test_ct)
    print(f"DT^-1 only: {plaintext[:30]}...")
    
    # Test with Vigenère chain
    plaintext = dt.decrypt_chained_vigenere(test_ct, "KRYPTOS", 'dt_first')
    print(f"(DT^-1) ∘ VIG: {plaintext[:30]}...")
    
    # Test with Beaufort chain
    plaintext = dt.decrypt_chained_beaufort(test_ct, "PALIMPSEST", 'dt_first')
    print(f"(DT^-1) ∘ BEAU: {plaintext[:30]}...")
    
    # Check anchor feasibility
    anchors = {
        'EAST': [21, 24],
        'NORTHEAST': [25, 33],
        'BERLIN': [63, 68],
        'CLOCK': [69, 73]
    }
    
    feasible = dt.check_anchor_feasibility(anchors)
    print(f"\nAnchor feasibility with 14 columns: {feasible}")

if __name__ == "__main__":
    test_double_transposition()