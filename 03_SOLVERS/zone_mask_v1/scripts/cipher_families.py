"""
Cipher Families - Vigenere and Beaufort with key schedules
"""

from typing import List, Dict, Any, Tuple


class CipherBase:
    """Base class for cipher operations"""
    
    def encrypt(self, plaintext: str, key: str) -> str:
        """Encrypt plaintext with key"""
        raise NotImplementedError
    
    def decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt ciphertext with key"""
        raise NotImplementedError


class VigenereCipher(CipherBase):
    """Standard Vigenere cipher"""
    
    def __init__(self, tableau: str = 'standard'):
        """
        Initialize Vigenere cipher with specified tableau
        
        Args:
            tableau: 'standard' for A-Z or 'kryptos' for KRYPTOS-keyed tableau
        """
        self.tableau_type = tableau
        self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        if tableau == 'kryptos':
            # Build KRYPTOS-keyed alphabet
            keyword = 'KRYPTOS'
            keyed_alphabet = []
            used = set()
            
            # Add keyword letters
            for char in keyword:
                if char not in used:
                    keyed_alphabet.append(char)
                    used.add(char)
            
            # Add remaining letters
            for char in self.alphabet:
                if char not in used:
                    keyed_alphabet.append(char)
            
            # Build the full 26x26 tableau
            self.tableau = []
            for i in range(26):
                row = keyed_alphabet[i:] + keyed_alphabet[:i]
                self.tableau.append(''.join(row))
        else:
            # Standard A-Z tableau
            self.tableau = []
            for i in range(26):
                row = self.alphabet[i:] + self.alphabet[:i]
                self.tableau.append(row)
    
    def encrypt(self, plaintext: str, key: str) -> str:
        """Encrypt using Vigenere cipher with tableau"""
        result = []
        key = key.upper()
        plaintext = plaintext.upper()
        key_index = 0
        
        for char in plaintext:
            if char in self.alphabet:
                # Find row based on key letter
                key_char = key[key_index % len(key)]
                row_index = self.alphabet.index(key_char)
                
                # Find column based on plaintext letter
                col_index = self.alphabet.index(char)
                
                # Get cipher character from tableau
                cipher_char = self.tableau[row_index][col_index]
                result.append(cipher_char)
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt using Vigenere cipher with tableau"""
        result = []
        key = key.upper()
        ciphertext = ciphertext.upper()
        key_index = 0
        
        for char in ciphertext:
            if char in self.alphabet:
                # Find row based on key letter
                key_char = key[key_index % len(key)]
                row_index = self.alphabet.index(key_char)
                
                # Find the cipher character in the tableau row
                tableau_row = self.tableau[row_index]
                col_index = tableau_row.index(char)
                
                # The column index gives us the plaintext letter
                plain_char = self.alphabet[col_index]
                result.append(plain_char)
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)


class BeaufortCipher(CipherBase):
    """Beaufort cipher (reciprocal cipher)"""
    
    def __init__(self, tableau: str = 'standard'):
        """
        Initialize Beaufort cipher with specified tableau
        
        Args:
            tableau: 'standard' for A-Z or 'kryptos' for KRYPTOS-keyed tableau
        """
        self.tableau_type = tableau
        self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        if tableau == 'kryptos':
            # Build KRYPTOS-keyed alphabet
            keyword = 'KRYPTOS'
            keyed_alphabet = []
            used = set()
            
            # Add keyword letters
            for char in keyword:
                if char not in used:
                    keyed_alphabet.append(char)
                    used.add(char)
            
            # Add remaining letters
            for char in self.alphabet:
                if char not in used:
                    keyed_alphabet.append(char)
            
            # Build the full 26x26 tableau
            self.tableau = []
            for i in range(26):
                row = keyed_alphabet[i:] + keyed_alphabet[:i]
                self.tableau.append(''.join(row))
        else:
            # Standard A-Z tableau
            self.tableau = []
            for i in range(26):
                row = self.alphabet[i:] + self.alphabet[:i]
                self.tableau.append(row)
    
    def encrypt(self, plaintext: str, key: str) -> str:
        """Encrypt using Beaufort cipher with tableau"""
        result = []
        key = key.upper()
        plaintext = plaintext.upper()
        key_index = 0
        
        for char in plaintext:
            if char in self.alphabet:
                # Find column based on plaintext letter
                col_index = self.alphabet.index(char)
                
                # Find key character
                key_char = key[key_index % len(key)]
                
                # Find which row contains key_char at col_index position
                for row_index, row in enumerate(self.tableau):
                    if row[col_index] == key_char:
                        # The row index gives us the cipher character
                        cipher_char = self.alphabet[row_index]
                        result.append(cipher_char)
                        break
                
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt using Beaufort cipher (self-reciprocal)"""
        # Beaufort is self-reciprocal
        return self.encrypt(ciphertext, key)


class KeyScheduler:
    """Handle key scheduling and rotation"""
    
    def __init__(self, keys: Dict[str, str], schedule: str, schedule_params: Dict[str, Any] = None):
        """
        Initialize key scheduler
        
        Args:
            keys: Dictionary of zone keys {'head': 'KEY1', 'mid': 'KEY2', 'tail': 'KEY3'}
            schedule: Schedule type ('static', 'rotate_on_class', 'rotate_on_control')
            schedule_params: Additional parameters for scheduling
        """
        self.keys = keys
        self.schedule = schedule
        self.schedule_params = schedule_params or {}
        self.current_keys = keys.copy()
        self.rotation_count = {'head': 0, 'mid': 0, 'tail': 0}
    
    def get_key(self, zone: str, position: int = 0) -> str:
        """Get the current key for a zone"""
        if self.schedule == 'static':
            return self.keys[zone]
        
        elif self.schedule == 'rotate_on_class':
            # Rotate key at class boundaries
            class_size = self.schedule_params.get('class_size', 10)
            rotation = (position // class_size) % len(self.keys[zone])
            return self.keys[zone][rotation:] + self.keys[zone][:rotation]
        
        elif self.schedule == 'rotate_on_control':
            # Rotate key at specific control indices
            control_indices = self.schedule_params.get('indices', [])
            rotations = sum(1 for idx in control_indices if idx <= position)
            rotation = rotations % len(self.keys[zone])
            return self.keys[zone][rotation:] + self.keys[zone][:rotation]
        
        else:
            return self.keys[zone]
    
    def rotate_key(self, zone: str, amount: int = 1):
        """Manually rotate a key"""
        key = self.current_keys[zone]
        rotation = amount % len(key)
        self.current_keys[zone] = key[rotation:] + key[:rotation]
        self.rotation_count[zone] += amount
    
    def reset(self):
        """Reset all keys to original state"""
        self.current_keys = self.keys.copy()
        self.rotation_count = {'head': 0, 'mid': 0, 'tail': 0}


class CipherEngine:
    """Main cipher engine for processing with key schedules"""
    
    def __init__(self, family: str, keys: Dict[str, str], schedule: str = 'static', 
                 schedule_params: Dict[str, Any] = None, tableau: str = 'kryptos'):
        """
        Initialize cipher engine
        
        Args:
            family: Cipher family ('vigenere' or 'beaufort')
            keys: Zone keys dictionary
            schedule: Key schedule type
            schedule_params: Schedule parameters
            tableau: Tableau type ('standard' or 'kryptos')
        """
        self.family = family
        self.tableau = tableau
        self.scheduler = KeyScheduler(keys, schedule, schedule_params)
        
        if family == 'vigenere':
            self.cipher = VigenereCipher(tableau=tableau)
        elif family == 'beaufort':
            self.cipher = BeaufortCipher(tableau=tableau)
        else:
            raise ValueError(f"Unknown cipher family: {family}")
    
    def encrypt_zone(self, text: str, zone: str, start_position: int = 0) -> str:
        """Encrypt text for a specific zone"""
        result = []
        
        for i, char in enumerate(text):
            key = self.scheduler.get_key(zone, start_position + i)
            encrypted_char = self.cipher.encrypt(char, key[i % len(key)])
            result.append(encrypted_char)
        
        return ''.join(result)
    
    def decrypt_zone(self, text: str, zone: str, start_position: int = 0) -> str:
        """Decrypt text for a specific zone"""
        result = []
        
        for i, char in enumerate(text):
            key = self.scheduler.get_key(zone, start_position + i)
            decrypted_char = self.cipher.decrypt(char, key[i % len(key)])
            result.append(decrypted_char)
        
        return ''.join(result)
    
    def process_full_text(self, text: str, zones: Dict[str, Tuple[int, int]], 
                         operation: str = 'decrypt') -> str:
        """
        Process full text with zone-based encryption/decryption
        
        Args:
            text: Full text to process
            zones: Zone definitions {'head': (start, end), 'mid': (start, end), 'tail': (start, end)}
            operation: 'encrypt' or 'decrypt'
        """
        result = list(text)
        
        for zone_name, (start, end) in zones.items():
            zone_text = text[start:end+1]
            
            if operation == 'encrypt':
                processed = self.encrypt_zone(zone_text, zone_name, start)
            else:
                processed = self.decrypt_zone(zone_text, zone_name, start)
            
            for i, char in enumerate(processed):
                result[start + i] = char
        
        return ''.join(result)


# Helper functions
def create_cipher_engine(config: Dict[str, Any]) -> CipherEngine:
    """Create cipher engine from configuration"""
    family = config.get('family', 'vigenere')
    keys = config.get('keys', {})
    schedule = config.get('schedule', 'static')
    schedule_params = config.get('schedule_params', {})
    tableau = config.get('tableau', 'kryptos')  # Default to KRYPTOS tableau
    
    return CipherEngine(family, keys, schedule, schedule_params, tableau)


def apply_cipher(text: str, cipher_config: Dict[str, Any], zones: Dict[str, Tuple[int, int]], 
                operation: str = 'decrypt') -> str:
    """Apply cipher based on configuration"""
    engine = create_cipher_engine(cipher_config)
    return engine.process_full_text(text, zones, operation)


# Key set definitions
KEY_SETS = {
    'surveying': {
        'LATITUDE': 'LATITUDE',
        'LONGITUDE': 'LONGITUDE',
        'AZIMUTH': 'AZIMUTH',
        'BEARING': 'BEARING'
    },
    'geometry': {
        'ABSCISSA': 'ABSCISSA',
        'ORDINATE': 'ORDINATE',
        'TANGENT': 'TANGENT',
        'SECANT': 'SECANT',
        'RADIAN': 'RADIAN',
        'DEGREE': 'DEGREE'
    },
    'artistic': {
        'SHADOW': 'SHADOW',
        'LIGHT': 'LIGHT',
        'LODESTONE': 'LODESTONE',
        'GIRASOL': 'GIRASOL'
    },
    'compound': {
        'ABSCISSAORDINATE': 'ABSCISSAORDINATE'
    }
}