#!/usr/bin/env python3
"""
zone_polyalpha.py

Zone-driven cipher with operation switching for Fork S-ShadowΔ.
Different cipher operations in different zones (Vigenère ↔ Beaufort).
"""

import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

def clamp(value: int, min_val: int = 2, max_val: int = 97) -> int:
    """Clamp value to valid range."""
    return max(min_val, min(max_val, value))

def bearing_to_params(bearing_deg: float, dms: Optional[Dict] = None) -> List[Dict]:
    """
    Convert bearing to cipher parameters.
    
    Args:
        bearing_deg: Bearing in degrees
        dms: Optional DMS dict with 'D', 'M', 'S' keys
    
    Returns:
        List of parameter variants
    """
    L_int = clamp(int(bearing_deg))
    L_round = clamp(round(bearing_deg))
    
    frac = bearing_deg - int(bearing_deg)
    off_f = int(frac * 26) % 26          # Floor
    off_r = int(round(frac * 26)) % 26   # Round
    
    phase = dms['M'] if dms else 0
    
    return [
        {'L': L_int, 'phase': phase, 'offset': off_f, 'variant': 'int_floor'},
        {'L': L_round, 'phase': phase, 'offset': off_r, 'variant': 'round_round'}
    ]

class OperationProfile:
    """Base class for operation profiles."""
    
    def get_operation(self, zone_state: int, shadow_angle: float, 
                      base_offset: int) -> Tuple[str, int]:
        """
        Get cipher operation and offset for given zone state.
        
        Returns:
            (family, adjusted_offset)
        """
        raise NotImplementedError

class ProfilePLight(OperationProfile):
    """
    P-Light: Simplest profile.
    - light (0) → Vigenère
    - shadow (1,2) → Beaufort
    """
    
    def get_operation(self, zone_state: int, shadow_angle: float,
                      base_offset: int) -> Tuple[str, int]:
        if zone_state == 0:
            return 'vigenere', base_offset
        else:
            return 'beaufort', base_offset

class ProfilePTri(OperationProfile):
    """
    P-Tri: Three-state profile.
    - light (0) → Vigenère
    - mid (1) → Beaufort with offset adjustment
    - deep (2) → Variant-Beaufort with larger offset adjustment
    """
    
    def get_operation(self, zone_state: int, shadow_angle: float,
                      base_offset: int) -> Tuple[str, int]:
        if zone_state == 0:
            return 'vigenere', base_offset
        elif zone_state == 1:
            # Mid: Beaufort with k=1 offset adjustment
            adjusted_offset = (base_offset + int(shadow_angle)) % 26
            return 'beaufort', adjusted_offset
        else:  # zone_state == 2
            # Deep: Variant-Beaufort with k=2 offset adjustment
            adjusted_offset = (base_offset + 2 * int(shadow_angle)) % 26
            return 'variant_beaufort', adjusted_offset

class ProfilePFlip(OperationProfile):
    """
    P-Flip: Operation toggles at anchor boundaries.
    - Anchor spans [21-33, 63-73] → Beaufort
    - Outside anchors → Vigenère
    """
    
    ANCHOR_RANGES = [(21, 33), (63, 73)]
    
    def get_operation(self, zone_state: int, shadow_angle: float,
                      base_offset: int) -> Tuple[str, int]:
        # This is handled per-index in the cipher, not by zone_state
        # Return default based on zone_state
        if zone_state > 0:
            return 'beaufort', base_offset
        else:
            return 'vigenere', base_offset

class ZoneDrivenCipher:
    """
    Zone-driven cipher with per-index operation switching.
    """
    
    def __init__(self, mask: List[Tuple[int, int, int]], 
                 base_params: Dict, shadow_params: Dict,
                 profile: OperationProfile):
        """
        Args:
            mask: Zone mask as list of (start, end, state) tuples
            base_params: Base cipher parameters (L, phase, offset)
            shadow_params: Shadow calculation results
            profile: Operation profile to use
        """
        self.mask = mask
        self.base_params = base_params
        self.shadow_params = shadow_params
        self.profile = profile
        
        # Build per-index state map
        self.index_states = self._build_index_states()
        
        # Track applied operations for logging
        self.per_index_log = []
    
    def _build_index_states(self) -> List[int]:
        """Build per-index state array from mask."""
        states = [0] * 97
        
        for start, end, state in self.mask:
            for i in range(start, min(end + 1, 97)):
                states[i] = state
        
        return states
    
    def _is_in_anchor(self, index: int) -> bool:
        """Check if index is in an anchor region (for P-Flip)."""
        anchor_ranges = [(21, 33), (63, 73)]
        for start, end in anchor_ranges:
            if start <= index <= end:
                return True
        return False
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext using zone-driven operations.
        
        Args:
            ciphertext: Input ciphertext (97 chars)
        
        Returns:
            Decrypted plaintext
        """
        if len(ciphertext) != 97:
            raise ValueError(f"Ciphertext must be 97 characters, got {len(ciphertext)}")
        
        plaintext = []
        self.per_index_log = []
        
        L = self.base_params['L']
        phase = self.base_params['phase']
        base_offset = self.base_params['offset']
        shadow_angle = self.shadow_params.get('shadow_angle', 0)
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                self.per_index_log.append({'index': i, 'char': c, 'family': 'none'})
                continue
            
            # Get zone state for this index
            zone_state = self.index_states[i]
            
            # Special handling for P-Flip profile
            if isinstance(self.profile, ProfilePFlip):
                if self._is_in_anchor(i):
                    family = 'beaufort'
                    offset = base_offset
                else:
                    family = 'vigenere'
                    offset = base_offset
            else:
                # Get operation from profile
                family, offset = self.profile.get_operation(zone_state, shadow_angle, base_offset)
            
            # Calculate key value
            k = (i - phase) % L
            key_val = (k + offset) % 26
            
            # Apply cipher family
            c_val = char_to_num(c)
            
            if family == 'vigenere':
                # P = (C - K) mod 26
                p_val = (c_val - key_val) % 26
            elif family == 'beaufort':
                # P = (K - C) mod 26
                p_val = (key_val - c_val) % 26
            elif family == 'variant_beaufort':
                # P = (C + K) mod 26
                p_val = (c_val + key_val) % 26
            else:
                raise ValueError(f"Unknown cipher family: {family}")
            
            plaintext.append(num_to_char(p_val))
            
            # Log the operation
            self.per_index_log.append({
                'index': i,
                'zone_state': zone_state,
                'family': family,
                'L': L,
                'phase': phase,
                'offset': offset,
                'key_val': key_val
            })
        
        return ''.join(plaintext)
    
    def save_per_index_log(self, filepath: Path):
        """Save per-index operation log."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.per_index_log, f, indent=2)
    
    def get_operation_summary(self) -> Dict:
        """Get summary of operations used."""
        summary = {
            'vigenere_count': 0,
            'beaufort_count': 0,
            'variant_beaufort_count': 0,
            'zone_distribution': {0: 0, 1: 0, 2: 0}
        }
        
        for entry in self.per_index_log:
            if 'family' in entry:
                family = entry['family']
                if family == 'vigenere':
                    summary['vigenere_count'] += 1
                elif family == 'beaufort':
                    summary['beaufort_count'] += 1
                elif family == 'variant_beaufort':
                    summary['variant_beaufort_count'] += 1
                
                if 'zone_state' in entry:
                    state = entry['zone_state']
                    summary['zone_distribution'][state] += 1
        
        return summary

def test_zone_cipher():
    """Test zone-driven cipher."""
    print("Testing Zone-Driven Cipher")
    print("-" * 50)
    
    # Test ciphertext (sample)
    test_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # Test mask (anchor regions in shadow)
    test_mask = [
        (0, 20, 0),    # Head: light
        (21, 33, 2),   # EAST+NORTHEAST: deep shadow
        (34, 62, 0),   # Mid: light
        (63, 73, 2),   # BERLIN+CLOCK: deep shadow
        (74, 96, 0)    # Tail: light
    ]
    
    # Test parameters
    base_params = {
        'L': 62,
        'phase': 41,
        'offset': 19
    }
    
    shadow_params = {
        'shadow_angle': 30.0
    }
    
    # Test each profile
    profiles = {
        'P-Light': ProfilePLight(),
        'P-Tri': ProfilePTri(),
        'P-Flip': ProfilePFlip()
    }
    
    for profile_name, profile in profiles.items():
        cipher = ZoneDrivenCipher(test_mask, base_params, shadow_params, profile)
        plaintext = cipher.decrypt(test_ct)
        
        print(f"\n{profile_name}:")
        print(f"  Head (0-20): {plaintext[:21]}")
        print(f"  EAST region: {plaintext[21:34]}")
        print(f"  BERLIN region: {plaintext[63:74]}")
        
        summary = cipher.get_operation_summary()
        print(f"  Operations: Vig={summary['vigenere_count']}, "
              f"Beau={summary['beaufort_count']}, "
              f"Var={summary['variant_beaufort_count']}")

if __name__ == "__main__":
    test_zone_cipher()