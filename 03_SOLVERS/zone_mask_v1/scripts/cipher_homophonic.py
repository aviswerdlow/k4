#!/usr/bin/env python3
"""
Homophonic cipher with anchor constraints
Allows many-to-one PT→CT mappings while keeping anchors fixed
"""

from typing import Dict, List, Set, Tuple, Optional
import random
import math

class HomophonicCipher:
    """
    Homophonic substitution cipher with deterministic forward encoding
    """
    
    def __init__(self, homophones: Dict[str, int] = None):
        """
        Initialize with homophone counts per letter
        
        Args:
            homophones: Dict mapping letters to number of CT symbols
                       e.g., {'E': 3, 'T': 3, 'A': 2, ...}
        """
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        # Default homophone distribution (based on English frequency)
        if homophones is None:
            homophones = {
                'E': 3, 'T': 3, 'A': 3, 'O': 3, 'N': 3,
                'R': 2, 'I': 2, 'S': 2, 'H': 2,
                # All others get 1
            }
        
        self.homophones = homophones
        self.ct_to_pt = {}  # CT symbol → PT letter mapping
        self.pt_to_cts = {}  # PT letter → list of CT symbols
        
    def initialize_random_mapping(self):
        """Create a random initial mapping respecting homophone counts"""
        # Create CT alphabet (could be 26-100 symbols depending on homophones)
        ct_symbols = list(self.alphabet)
        symbol_index = 26
        
        # Assign symbols to each PT letter
        for pt_char in self.alphabet:
            num_symbols = self.homophones.get(pt_char, 1)
            assigned_symbols = []
            
            for _ in range(num_symbols):
                if symbol_index < 100:  # Cap at 100 total symbols
                    # Use two-letter codes for extra symbols
                    symbol = f"{self.alphabet[symbol_index // 26]}{self.alphabet[symbol_index % 26]}"
                    symbol_index += 1
                    assigned_symbols.append(symbol)
                else:
                    # Fallback to single symbol
                    assigned_symbols = [pt_char]
                    break
            
            # Store mappings
            self.pt_to_cts[pt_char] = assigned_symbols
            for symbol in assigned_symbols:
                self.ct_to_pt[symbol] = pt_char
    
    def decrypt(self, ciphertext: str, mapping: Dict[str, str] = None) -> str:
        """
        Decrypt ciphertext using provided or current mapping
        
        Args:
            ciphertext: The ciphertext to decrypt
            mapping: Optional CT→PT mapping to use
        
        Returns:
            Decrypted plaintext
        """
        if mapping:
            self.ct_to_pt = mapping
        
        plaintext = []
        i = 0
        while i < len(ciphertext):
            # Try two-char symbol first
            if i + 1 < len(ciphertext):
                two_char = ciphertext[i:i+2]
                if two_char in self.ct_to_pt:
                    plaintext.append(self.ct_to_pt[two_char])
                    i += 2
                    continue
            
            # Single char symbol
            if ciphertext[i] in self.ct_to_pt:
                plaintext.append(self.ct_to_pt[ciphertext[i]])
            else:
                plaintext.append(ciphertext[i])  # Pass through unknown
            i += 1
        
        return ''.join(plaintext)
    
    def encrypt(self, plaintext: str, original_ct: str = None) -> str:
        """
        Deterministic encryption that matches original CT when possible
        
        Args:
            plaintext: The plaintext to encrypt
            original_ct: Original ciphertext to match when possible
        
        Returns:
            Encrypted ciphertext
        """
        if not self.pt_to_cts:
            self.initialize_random_mapping()
        
        ciphertext = []
        ct_index = 0
        
        for i, pt_char in enumerate(plaintext):
            if pt_char not in self.pt_to_cts:
                ciphertext.append(pt_char)  # Pass through
                ct_index += 1
                continue
            
            available_symbols = self.pt_to_cts[pt_char]
            
            # If we have original CT, try to match it
            if original_ct and ct_index < len(original_ct):
                # Check if current CT position matches any available symbol
                for symbol in available_symbols:
                    if original_ct[ct_index:ct_index+len(symbol)] == symbol:
                        ciphertext.append(symbol)
                        ct_index += len(symbol)
                        break
                else:
                    # No match, use first available
                    symbol = available_symbols[0]
                    ciphertext.append(symbol)
                    ct_index += len(symbol)
            else:
                # No original CT, use first symbol
                symbol = available_symbols[0]
                ciphertext.append(symbol)
                ct_index += len(symbol)
        
        return ''.join(ciphertext)


class AnchorConstrainedHomophonic:
    """
    Homophonic cipher with anchors locked to specific values
    """
    
    def __init__(self, anchor_positions: Dict[str, Tuple[int, int]]):
        """
        Initialize with anchor constraints
        
        Args:
            anchor_positions: Dict of anchor text to (start, end) positions
        """
        self.anchor_positions = anchor_positions
        self.locked_positions = set()
        
        # Build set of all locked positions
        for anchor_text, (start, end) in anchor_positions.items():
            for i in range(start, end + 1):
                self.locked_positions.add(i)
    
    def is_locked(self, position: int) -> bool:
        """Check if a position is locked by anchor constraints"""
        return position in self.locked_positions
    
    def decrypt_with_anchors(self, ciphertext: str, mapping: Dict[str, str]) -> str:
        """
        Decrypt with anchor constraints enforced
        
        Args:
            ciphertext: The ciphertext to decrypt
            mapping: CT→PT mapping for non-anchor positions
        
        Returns:
            Plaintext with anchors at correct positions
        """
        plaintext = list(ciphertext)  # Start with CT as base
        
        # Apply anchors
        for anchor_text, (start, end) in self.anchor_positions.items():
            for i, char in enumerate(anchor_text):
                if start + i <= end and start + i < len(plaintext):
                    plaintext[start + i] = char
        
        # Apply mapping to non-anchor positions
        for i in range(len(ciphertext)):
            if not self.is_locked(i):
                ct_char = ciphertext[i]
                if ct_char in mapping:
                    plaintext[i] = mapping[ct_char]
        
        return ''.join(plaintext)
    
    def score_plaintext(self, plaintext: str, scorer) -> float:
        """
        Score plaintext quality, excluding anchor regions
        
        Args:
            plaintext: The plaintext to score
            scorer: Language scoring function
        
        Returns:
            Score value (higher is better)
        """
        # Extract non-anchor text for scoring
        non_anchor_text = []
        for i, char in enumerate(plaintext):
            if not self.is_locked(i):
                non_anchor_text.append(char)
        
        if not non_anchor_text:
            return 0.0
        
        return scorer(''.join(non_anchor_text))
    
    def simulated_annealing(self, ciphertext: str, scorer, 
                           max_iterations: int = 100000,
                           initial_temp: float = 1.0,
                           cooling_rate: float = 0.9999) -> Tuple[str, Dict[str, str]]:
        """
        Find optimal mapping using simulated annealing
        
        Args:
            ciphertext: The ciphertext to decrypt
            scorer: Language scoring function
            max_iterations: Maximum iterations
            initial_temp: Starting temperature
            cooling_rate: Temperature decay rate
        
        Returns:
            Best plaintext and mapping found
        """
        # Initialize random mapping
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        current_mapping = {c: c for c in alphabet}
        
        # Shuffle initial mapping
        values = list(current_mapping.values())
        random.shuffle(values)
        current_mapping = dict(zip(alphabet, values))
        
        # Get initial plaintext and score
        current_pt = self.decrypt_with_anchors(ciphertext, current_mapping)
        current_score = self.score_plaintext(current_pt, scorer)
        
        best_pt = current_pt
        best_mapping = current_mapping.copy()
        best_score = current_score
        
        temperature = initial_temp
        
        for iteration in range(max_iterations):
            # Make a random swap in mapping
            keys = list(current_mapping.keys())
            k1, k2 = random.sample(keys, 2)
            
            # Swap mapping
            new_mapping = current_mapping.copy()
            new_mapping[k1], new_mapping[k2] = new_mapping[k2], new_mapping[k1]
            
            # Get new plaintext and score
            new_pt = self.decrypt_with_anchors(ciphertext, new_mapping)
            new_score = self.score_plaintext(new_pt, scorer)
            
            # Accept or reject
            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / temperature):
                current_mapping = new_mapping
                current_pt = new_pt
                current_score = new_score
                
                if current_score > best_score:
                    best_score = current_score
                    best_mapping = current_mapping.copy()
                    best_pt = current_pt
            
            # Cool down
            temperature *= cooling_rate
            
            # Progress report
            if iteration % 10000 == 0:
                print(f"  Iteration {iteration}: Best score = {best_score:.3f}")
        
        return best_pt, best_mapping