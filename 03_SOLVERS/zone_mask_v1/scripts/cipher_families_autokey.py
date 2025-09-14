#!/usr/bin/env python3
"""
Autokey cipher systems for K4 cryptanalysis
Plan F: PT-autokey and CT-autokey variants with KRYPTOS tableau
"""

from typing import List, Optional, Dict, Any


def create_keyed_alphabet(keyword: str = "KRYPTOS") -> str:
    """Create a keyed alphabet"""
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
    
    return ''.join(alphabet)


class AutokeyVigenere:
    """Vigenere autokey cipher with plaintext or ciphertext feedback"""
    
    def __init__(self, seed_key: str, mode: str = 'pt', tableau: str = 'kryptos'):
        """
        Initialize autokey cipher
        
        Args:
            seed_key: Initial key seed
            mode: 'pt' for plaintext autokey, 'ct' for ciphertext autokey
            tableau: 'standard' or 'kryptos' for tableau type
        """
        self.seed_key = seed_key.upper()
        self.mode = mode
        
        # Build tableau
        if tableau == 'kryptos':
            self.alphabet = create_keyed_alphabet('KRYPTOS')
        else:
            self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt using autokey"""
        plaintext = plaintext.upper()
        result = []
        
        # Build initial keystream
        if self.mode == 'pt':
            # PT-autokey: keystream = seed + plaintext
            # We only need seed length characters from plaintext
            keystream = self.seed_key + plaintext
        else:
            # CT-autokey: keystream starts with seed, extended by ciphertext
            keystream = list(self.seed_key)
        
        key_idx = 0
        
        for char in plaintext:
            if char.isalpha():
                # For CT-autokey, extend keystream with previous ciphertext
                if self.mode == 'ct' and key_idx >= len(keystream):
                    # Use the last generated ciphertext character
                    keystream.append(result[-1])
                
                key_char = keystream[key_idx]
                key_idx += 1
                
                # Get positions in alphabet
                pt_pos = self.alphabet.index(char)
                key_pos = self.alphabet.index(key_char)
                
                # Encrypt (Vigenere: C = P + K mod 26)
                ct_pos = (pt_pos + key_pos) % 26
                ct_char = self.alphabet[ct_pos]
                
                result.append(ct_char)
            else:
                result.append(char)
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt using autokey"""
        ciphertext = ciphertext.upper()
        result = []
        
        # Start with seed key
        keystream = list(self.seed_key)
        key_idx = 0
        
        for char in ciphertext:
            if char.isalpha():
                # Get key character for this position
                key_char = keystream[key_idx]
                key_idx += 1
                
                # Get positions in alphabet
                ct_pos = self.alphabet.index(char)
                key_pos = self.alphabet.index(key_char)
                
                # Decrypt (Vigenere: P = C - K mod 26)
                pt_pos = (ct_pos - key_pos) % 26
                pt_char = self.alphabet[pt_pos]
                
                result.append(pt_char)
                
                # Extend keystream based on mode
                if key_idx >= len(self.seed_key):
                    if self.mode == 'pt':
                        # PT-autokey: add recovered plaintext to keystream
                        keystream.append(pt_char)
                    else:
                        # CT-autokey: add ciphertext to keystream
                        keystream.append(char)
            else:
                result.append(char)
        
        return ''.join(result)


class AutokeyBeaufort:
    """Beaufort autokey cipher with plaintext or ciphertext feedback"""
    
    def __init__(self, seed_key: str, mode: str = 'pt', tableau: str = 'kryptos'):
        """
        Initialize autokey cipher
        
        Args:
            seed_key: Initial key seed
            mode: 'pt' for plaintext autokey, 'ct' for ciphertext autokey
            tableau: 'standard' or 'kryptos' for tableau type
        """
        self.seed_key = seed_key.upper()
        self.mode = mode
        
        # Build tableau
        if tableau == 'kryptos':
            self.alphabet = create_keyed_alphabet('KRYPTOS')
        else:
            self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt using Beaufort autokey"""
        plaintext = plaintext.upper()
        result = []
        
        # Build initial keystream
        if self.mode == 'pt':
            # PT-autokey: keystream = seed + plaintext
            keystream = self.seed_key + plaintext
        else:
            # CT-autokey: keystream starts with seed, extended by ciphertext
            keystream = list(self.seed_key)
        
        key_idx = 0
        
        for char in plaintext:
            if char.isalpha():
                # For CT-autokey, extend keystream with previous ciphertext
                if self.mode == 'ct' and key_idx >= len(keystream):
                    # Use the last generated ciphertext character
                    keystream.append(result[-1])
                
                key_char = keystream[key_idx]
                key_idx += 1
                
                # Get positions in alphabet
                pt_pos = self.alphabet.index(char)
                key_pos = self.alphabet.index(key_char)
                
                # Encrypt (Beaufort: C = K - P mod 26)
                ct_pos = (key_pos - pt_pos) % 26
                ct_char = self.alphabet[ct_pos]
                
                result.append(ct_char)
            else:
                result.append(char)
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt using Beaufort autokey"""
        ciphertext = ciphertext.upper()
        result = []
        
        # Start with seed key
        keystream = list(self.seed_key)
        key_idx = 0
        
        for char in ciphertext:
            if char.isalpha():
                # Get key character for this position
                key_char = keystream[key_idx]
                key_idx += 1
                
                # Get positions in alphabet
                ct_pos = self.alphabet.index(char)
                key_pos = self.alphabet.index(key_char)
                
                # Decrypt (Beaufort: P = K - C mod 26)
                pt_pos = (key_pos - ct_pos) % 26
                pt_char = self.alphabet[pt_pos]
                
                result.append(pt_char)
                
                # Extend keystream based on mode
                if key_idx >= len(self.seed_key):
                    if self.mode == 'pt':
                        # PT-autokey: add recovered plaintext to keystream
                        keystream.append(pt_char)
                    else:
                        # CT-autokey: add ciphertext to keystream
                        keystream.append(char)
            else:
                result.append(char)
        
        return ''.join(result)


def create_autokey_cipher(config: Dict[str, Any]):
    """
    Factory function to create autokey ciphers
    
    Args:
        config: Configuration with:
            - family: 'vigenere' or 'beaufort'
            - mode: 'pt' or 'ct'
            - seed_key: Initial key seed
            - tableau: 'standard' or 'kryptos'
    """
    family = config.get('family', 'vigenere')
    mode = config.get('mode', 'pt')
    seed_key = config.get('seed_key', 'KEY')
    tableau = config.get('tableau', 'kryptos')
    
    if family == 'vigenere':
        return AutokeyVigenere(seed_key, mode, tableau)
    elif family == 'beaufort':
        return AutokeyBeaufort(seed_key, mode, tableau)
    else:
        raise ValueError(f"Unknown family: {family}")


def encode(plaintext: str, config: Dict[str, Any]) -> str:
    """Encode using autokey cipher"""
    cipher = create_autokey_cipher(config)
    return cipher.encrypt(plaintext)


def decode(ciphertext: str, config: Dict[str, Any]) -> str:
    """Decode using autokey cipher"""
    cipher = create_autokey_cipher(config)
    return cipher.decrypt(ciphertext)


def vigenere_autokey_pt(plaintext: str, seed_key: str, tableau: str = 'kryptos') -> str:
    """Shorthand for Vigenere PT-autokey encryption"""
    cipher = AutokeyVigenere(seed_key, 'pt', tableau)
    return cipher.encrypt(plaintext)


def vigenere_autokey_ct(plaintext: str, seed_key: str, tableau: str = 'kryptos') -> str:
    """Shorthand for Vigenere CT-autokey encryption"""
    cipher = AutokeyVigenere(seed_key, 'ct', tableau)
    return cipher.encrypt(plaintext)


def beaufort_autokey_pt(plaintext: str, seed_key: str, tableau: str = 'kryptos') -> str:
    """Shorthand for Beaufort PT-autokey encryption"""
    cipher = AutokeyBeaufort(seed_key, 'pt', tableau)
    return cipher.encrypt(plaintext)


def beaufort_autokey_ct(plaintext: str, seed_key: str, tableau: str = 'kryptos') -> str:
    """Shorthand for Beaufort CT-autokey encryption"""
    cipher = AutokeyBeaufort(seed_key, 'ct', tableau)
    return cipher.encrypt(plaintext)