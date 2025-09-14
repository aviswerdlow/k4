#!/usr/bin/env python3
"""
Paired-alphabet cipher systems: Porta and Quagmire variants
"""

from typing import Dict, List, Any, Optional


class KeyedAlphabet:
    """Generate keyed alphabets for cipher construction"""
    
    @staticmethod
    def create(keyword: str = None, alphabet_type: str = 'standard') -> str:
        """
        Create a keyed alphabet
        
        Args:
            keyword: Keyword to use (removes duplicates)
            alphabet_type: 'standard' or 'kryptos'
        
        Returns:
            26-letter keyed alphabet
        """
        if alphabet_type == 'kryptos':
            keyword = 'KRYPTOS'
        elif keyword:
            keyword = keyword.upper()
        else:
            return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        # Build keyed alphabet
        used = set()
        result = []
        
        # Add keyword letters
        for char in keyword:
            if char not in used and char.isalpha():
                result.append(char)
                used.add(char)
        
        # Add remaining letters
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if char not in used:
                result.append(char)
        
        return ''.join(result)


class PortaCipher:
    """
    Porta cipher - reciprocal with 13 paired alphabets
    """
    
    def __init__(self, row_alphabet: str = None, indicator_key: str = None):
        """
        Initialize Porta cipher
        
        Args:
            row_alphabet: Keyed alphabet for rows (or 'kryptos')
            indicator_key: Key controlling alphabet switching
        """
        # Build row alphabet
        if row_alphabet == 'kryptos':
            self.row_alphabet = KeyedAlphabet.create(alphabet_type='kryptos')
        elif isinstance(row_alphabet, dict):
            self.row_alphabet = KeyedAlphabet.create(row_alphabet.get('keyword', ''))
        else:
            self.row_alphabet = KeyedAlphabet.create(row_alphabet)
        
        self.indicator_key = indicator_key.upper() if indicator_key else 'A'
        
        # Build Porta tableau (13 alphabets, each is reciprocal)
        self.tableau = self._build_porta_tableau()
    
    def _build_porta_tableau(self) -> Dict[int, Dict[str, str]]:
        """Build the 13 Porta alphabets as reciprocal mappings"""
        # Porta uses reciprocal substitution alphabets
        tableau = {}
        
        for i in range(13):
            mapping = {}
            # Create reciprocal pairs
            # First half maps to second half and vice versa
            for j in range(13):
                char1 = self.row_alphabet[j]
                char2 = self.row_alphabet[(j + 13 + i) % 26]
                mapping[char1] = char2
                mapping[char2] = char1
            tableau[i] = mapping
        
        return tableau
    
    def _get_tableau_row(self, key_char: str) -> int:
        """Get tableau row index from key character"""
        # In Porta, pairs of letters use same alphabet
        # A,B -> 0; C,D -> 1; etc.
        pos = ord(key_char.upper()) - ord('A')
        return pos // 2
    
    def encrypt(self, plaintext: str, indicator_config: Dict = None) -> str:
        """Encrypt using Porta cipher"""
        plaintext = plaintext.upper()
        result = []
        
        # Handle indicator configuration
        if indicator_config and indicator_config.get('type') == 'periodic':
            indicator = indicator_config.get('key', 'A')
            phase = indicator_config.get('phase', 0)
        else:
            indicator = self.indicator_key
            phase = 0
        
        for i, char in enumerate(plaintext):
            if char.isalpha():
                # Get indicator character for this position
                ind_char = indicator[(i + phase) % len(indicator)]
                row_idx = self._get_tableau_row(ind_char)
                
                # Get mapping for this position
                mapping = self.tableau[row_idx % 13]
                
                # Get cipher character from mapping
                cipher_char = mapping.get(char, char)
                result.append(cipher_char)
            else:
                result.append(char)
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str, indicator_config: Dict = None) -> str:
        """Decrypt using Porta cipher (reciprocal)"""
        # Porta is reciprocal, so decrypt = encrypt
        return self.encrypt(ciphertext, indicator_config)


class QuagmireCipher:
    """
    Quagmire cipher variants (II, III, IV)
    """
    
    def __init__(self, variant: int, row_alphabet: str = None, 
                 col_alphabet: str = None, indicator_key: str = None):
        """
        Initialize Quagmire cipher
        
        Args:
            variant: 2, 3, or 4 (Quagmire type)
            row_alphabet: Keyed alphabet for rows
            col_alphabet: Keyed alphabet for columns
            indicator_key: Key controlling row/column selection
        """
        self.variant = variant
        
        # Build alphabets
        if row_alphabet == 'kryptos':
            self.row_alphabet = KeyedAlphabet.create(alphabet_type='kryptos')
        elif isinstance(row_alphabet, dict):
            self.row_alphabet = KeyedAlphabet.create(row_alphabet.get('keyword', ''))
        else:
            self.row_alphabet = KeyedAlphabet.create(row_alphabet)
        
        if col_alphabet == 'kryptos':
            self.col_alphabet = KeyedAlphabet.create(alphabet_type='kryptos')
        elif isinstance(col_alphabet, dict):
            self.col_alphabet = KeyedAlphabet.create(col_alphabet.get('keyword', ''))
        else:
            self.col_alphabet = KeyedAlphabet.create(col_alphabet)
        
        self.indicator_key = indicator_key.upper() if indicator_key else 'A'
        
        # Build tableau
        self.tableau = self._build_quagmire_tableau()
    
    def _build_quagmire_tableau(self) -> List[str]:
        """Build Quagmire tableau based on variant"""
        tableau = []
        
        if self.variant == 2:
            # Quagmire II: Plain alphabet in rows, keyed in columns
            for i in range(26):
                row = self.col_alphabet[i:] + self.col_alphabet[:i]
                tableau.append(row)
        
        elif self.variant == 3:
            # Quagmire III: Keyed alphabet in rows, plain in columns
            for i in range(26):
                row = self.row_alphabet[i:] + self.row_alphabet[:i]
                tableau.append(row)
        
        elif self.variant == 4:
            # Quagmire IV: Both keyed
            for i in range(26):
                # Use row alphabet as base, shift by position
                row = self.row_alphabet[i:] + self.row_alphabet[:i]
                # Then apply column alphabet mapping
                mapped_row = []
                for char in row:
                    pos = ord(char) - ord('A')
                    mapped_row.append(self.col_alphabet[pos])
                tableau.append(''.join(mapped_row))
        
        return tableau
    
    def encrypt(self, plaintext: str, indicator_config: Dict = None) -> str:
        """Encrypt using Quagmire cipher"""
        plaintext = plaintext.upper()
        result = []
        
        # Handle indicator configuration
        if indicator_config and indicator_config.get('type') == 'periodic':
            indicator = indicator_config.get('key', 'A')
            phase = indicator_config.get('phase', 0)
        else:
            indicator = self.indicator_key
            phase = 0
        
        for i, char in enumerate(plaintext):
            if char.isalpha():
                # Get indicator character
                ind_char = indicator[(i + phase) % len(indicator)]
                
                # Get row index from indicator
                if self.variant == 2:
                    row_idx = ord(ind_char) - ord('A')  # Plain rows
                else:
                    row_idx = self.row_alphabet.index(ind_char)  # Keyed rows
                
                # Get column index from plaintext
                if self.variant in [2, 4]:
                    col_idx = self.col_alphabet.index(char)  # Keyed columns
                else:
                    col_idx = ord(char) - ord('A')  # Plain columns
                
                # Get cipher character
                cipher_char = self.tableau[row_idx][col_idx]
                result.append(cipher_char)
            else:
                result.append(char)
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str, indicator_config: Dict = None) -> str:
        """Decrypt using Quagmire cipher"""
        ciphertext = ciphertext.upper()
        result = []
        
        # Handle indicator configuration
        if indicator_config and indicator_config.get('type') == 'periodic':
            indicator = indicator_config.get('key', 'A')
            phase = indicator_config.get('phase', 0)
        else:
            indicator = self.indicator_key
            phase = 0
        
        for i, char in enumerate(ciphertext):
            if char.isalpha():
                # Get indicator character
                ind_char = indicator[(i + phase) % len(indicator)]
                
                # Get row index from indicator
                if self.variant == 2:
                    row_idx = ord(ind_char) - ord('A')
                else:
                    row_idx = self.row_alphabet.index(ind_char)
                
                # Find plaintext character
                row = self.tableau[row_idx]
                col_idx = row.index(char)
                
                # Get plaintext from column index
                if self.variant in [2, 4]:
                    plain_char = self.col_alphabet[col_idx]
                else:
                    plain_char = chr(ord('A') + col_idx)
                
                result.append(plain_char)
            else:
                result.append(char)
        
        return ''.join(result)


def create_paired_cipher(config: Dict[str, Any]):
    """
    Factory function to create paired alphabet ciphers
    
    Args:
        config: Configuration dictionary with:
            - family: 'porta', 'quag2', 'quag3', 'quag4'
            - alph_row: Row alphabet specification
            - alph_col: Column alphabet specification (Quagmire only)
            - indicator: Indicator configuration
    
    Returns:
        Cipher instance
    """
    family = config.get('family', 'porta')
    
    if family == 'porta':
        return PortaCipher(
            row_alphabet=config.get('alph_row', 'kryptos'),
            indicator_key=config.get('indicator', {}).get('key', 'A')
        )
    
    elif family.startswith('quag'):
        variant = int(family[-1])
        return QuagmireCipher(
            variant=variant,
            row_alphabet=config.get('alph_row', 'kryptos'),
            col_alphabet=config.get('alph_col', 'kryptos'),
            indicator_key=config.get('indicator', {}).get('key', 'A')
        )
    
    else:
        raise ValueError(f"Unknown cipher family: {family}")


def encode(plaintext: str, config: Dict[str, Any]) -> str:
    """Encode plaintext using paired alphabet cipher"""
    cipher = create_paired_cipher(config)
    return cipher.encrypt(plaintext, config.get('indicator'))


def decode(ciphertext: str, config: Dict[str, Any]) -> str:
    """Decode ciphertext using paired alphabet cipher"""
    cipher = create_paired_cipher(config)
    return cipher.decrypt(ciphertext, config.get('indicator'))