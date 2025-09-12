#!/usr/bin/env python3
"""
shadow_polyalpha.py

Shadow-modified polyalphabetic cipher implementation.
Zone-based parameter modifications driven by shadow geometry.
"""

import math
from typing import Dict, List, Tuple, Optional

# Survey bearing constants
BEARINGS = {
    'ENE': 67.5,
    'true_ne_plus': 61.6959,
    'true_ene_minus': 50.8041,
    'mag_ne_plus_1989': 59.5959,
    'mag_ene_minus_1989': 48.7041,
    'offset_only': 16.6959
}

# Declination constants
LANGLEY_1990_DECLINATION = 9.5  # degrees West
BERLIN_1989_DECLINATION = -2.0  # degrees East

def char_to_num(c: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(c.upper()) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr((n % 26) + ord('A'))

def clamp(value: int, min_val: int = 2, max_val: int = 97) -> int:
    """Clamp value to valid range."""
    return max(min_val, min(max_val, value))

def bearing_to_L_phase_offset(bearing_deg: float) -> Dict:
    """
    Convert bearing to cipher parameters.
    
    Returns:
        Dictionary with L, phase, and offset variants
    """
    L_int = clamp(int(bearing_deg))
    L_round = clamp(round(bearing_deg))
    
    # Fractional part to alphabet offset
    frac = bearing_deg - int(bearing_deg)
    off_alpha_floor = int(frac * 26) % 26
    off_alpha_round = int(round(frac * 26)) % 26
    
    return {
        'L_int': L_int,
        'L_round': L_round,
        'off_alpha_floor': off_alpha_floor,
        'off_alpha_round': off_alpha_round,
        'bearing_deg': bearing_deg
    }

def dms_variants(D: int, M: int, S: int) -> List[Dict]:
    """
    Generate DMS-based configurations.
    """
    configs = []
    
    # Config 1: L=D, phase=M, offset=S%26
    configs.append({
        'L': clamp(D),
        'phase': M,
        'offset': S % 26,
        'source': f'DMS({D},{M},{S})'
    })
    
    # Config 2: L=D+M, phase=S, offset=D%26
    configs.append({
        'L': clamp(D + M),
        'phase': S,
        'offset': D % 26,
        'source': f'DMS_sum({D},{M},{S})'
    })
    
    # Config 3: L=S, phase=M, offset=D%26 (if S valid)
    if S >= 2:
        configs.append({
            'L': clamp(S),
            'phase': M,
            'offset': D % 26,
            'source': f'DMS_S_as_L({D},{M},{S})'
        })
    
    return configs

def zone_params(base_L: int, base_phase: int, base_offset: int,
               shadow_angle: float, shadow_state: int, 
               source: str = 'bearing') -> Dict:
    """
    Calculate zone-specific parameters based on shadow state.
    
    Args:
        base_L: Base period length
        base_phase: Base phase
        base_offset: Base offset
        shadow_angle: Shadow angle in degrees
        shadow_state: 0=light, 1=shadow, 2=deep_shadow
        source: Parameter source description
    
    Returns:
        Dictionary with zone-specific parameters and family
    """
    if shadow_state == 0:
        # Light zone: use base parameters
        L = base_L
        phase = base_phase
        offset = base_offset
        family = 'vigenere'
    
    elif shadow_state == 1:
        # Shadow/mid-shadow zone: modify parameters
        L = clamp(base_L - int(round(shadow_angle / 3)))
        offset = (base_offset + int(shadow_angle) % 26) % 26
        phase = base_phase
        family = 'beaufort'
    
    else:  # shadow_state == 2
        # Deep shadow zone: stronger modifications
        L = clamp(base_L - int(round(shadow_angle / 2)))
        offset = (base_offset + 2 * int(shadow_angle) % 26) % 26
        phase = (base_phase + int(shadow_angle / 4)) % 26
        family = 'variant_beaufort'
    
    return {
        'L': L,
        'phase': phase,
        'offset': offset,
        'family': family,
        'state': shadow_state,
        'source': source,
        'shadow_angle': shadow_angle
    }

class ShadowModifiedCipher:
    """
    Shadow-modified polyalphabetic cipher with per-zone parameters.
    """
    
    def __init__(self, mask: List[Tuple[int, int, int]], 
                base_params: Dict, shadow_params: Dict):
        """
        Args:
            mask: Zone mask as list of (start, end, state) tuples
            base_params: Base cipher parameters
            shadow_params: Shadow calculation results
        """
        self.mask = mask
        self.base_params = base_params
        self.shadow_params = shadow_params
        
        # Build per-index parameter map
        self.index_params = self._build_index_params()
    
    def _build_index_params(self) -> List[Dict]:
        """Build per-index parameter map from zone mask."""
        params = [None] * 97
        
        shadow_angle = self.shadow_params.get('shadow_angle', 0)
        
        for start, end, state in self.mask:
            # Get zone-specific parameters
            zone_p = zone_params(
                self.base_params['L'],
                self.base_params.get('phase', 0),
                self.base_params.get('offset', 0),
                shadow_angle,
                state,
                self.base_params.get('source', 'unknown')
            )
            
            # Apply to indices in zone
            for i in range(start, min(end + 1, 97)):
                params[i] = zone_p
        
        return params
    
    def decrypt(self, ciphertext: str, config: str = 'S-Light') -> str:
        """
        Decrypt ciphertext using shadow-modified parameters.
        
        Args:
            ciphertext: Input ciphertext
            config: Configuration variant
                'S-Light': light→Vigenere, shadow→Beaufort
                'S-Swap': light→Beaufort, shadow→Vigenere
                'S-Tri': light→Vig, mid→Beaufort, deep→Variant
        
        Returns:
            Decrypted plaintext (position-preserving)
        """
        if len(ciphertext) != 97:
            raise ValueError(f"Ciphertext must be 97 characters, got {len(ciphertext)}")
        
        plaintext = []
        
        for i, c in enumerate(ciphertext):
            if not c.isalpha():
                plaintext.append(c)
                continue
            
            # Get parameters for this index
            params = self.index_params[i]
            if params is None:
                plaintext.append(c)  # No change if no params
                continue
            
            # Determine cipher family based on config
            if config == 'S-Swap':
                # Swap light and shadow families
                if params['family'] == 'vigenere':
                    family = 'beaufort'
                elif params['family'] == 'beaufort':
                    family = 'vigenere'
                else:
                    family = params['family']
            else:
                family = params['family']
            
            # Calculate key value for this position
            # Each zone maintains its own key schedule
            zone_L = params['L']
            zone_phase = params['phase']
            zone_offset = params['offset']
            
            # Key index within this zone's cycle
            key_idx = (i + zone_phase) % zone_L
            key_val = (key_idx + zone_offset) % 26
            
            # Apply appropriate cipher family
            c_val = char_to_num(c)
            
            if family == 'vigenere':
                # P = (C - K) mod 26
                p_val = (c_val - key_val) % 26
            elif family == 'beaufort':
                # P = (K - C) mod 26
                p_val = (key_val - c_val) % 26
            else:  # variant_beaufort
                # P = (C + K) mod 26
                p_val = (c_val + key_val) % 26
            
            plaintext.append(num_to_char(p_val))
        
        return ''.join(plaintext)
    
    def get_zone_profiles(self) -> List[Dict]:
        """Get unique zone profiles for reporting."""
        profiles = []
        seen = set()
        
        for start, end, state in self.mask:
            # Get representative params for this zone
            if start < len(self.index_params) and self.index_params[start]:
                params = self.index_params[start]
                key = (params['state'], params['family'], params['L'], params['offset'])
                
                if key not in seen:
                    seen.add(key)
                    profiles.append({
                        'state': ['light', 'shadow', 'deep_shadow'][params['state']],
                        'family': params['family'],
                        'L': params['L'],
                        'offset': params['offset'],
                        'phase': params.get('phase', 0)
                    })
        
        return profiles

def apply_declination_shift(text: str, declination: float, 
                           pre: bool = True) -> str:
    """
    Apply Caesar shift based on magnetic declination.
    
    Args:
        text: Input text
        declination: Magnetic declination in degrees
        pre: True for pre-shift, False for post-shift
    
    Returns:
        Shifted text
    """
    if pre:
        shift = int(round(declination)) % 26
    else:
        shift = (-int(round(declination))) % 26
    
    result = []
    for c in text:
        if c.isalpha():
            result.append(num_to_char((char_to_num(c) - shift) % 26))
        else:
            result.append(c)
    
    return ''.join(result)

def test_shadow_cipher():
    """Test shadow-modified cipher."""
    print("Testing Shadow-Modified Cipher")
    print("-" * 50)
    
    # Test ciphertext (sample)
    test_ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    # Test mask (anchors in shadow)
    test_mask = [
        (0, 20, 0),    # Head: light
        (21, 33, 1),   # EAST+NORTHEAST: shadow
        (34, 62, 0),   # Mid: light
        (63, 73, 1),   # BERLIN+CLOCK: shadow
        (74, 96, 0)    # Tail: light
    ]
    
    # Test shadow parameters
    test_shadow = {
        'shadow_angle': 35.0,
        'shadow_bearing': 210.0
    }
    
    # Test base parameters
    test_base = bearing_to_L_phase_offset(61.6959)
    test_base['phase'] = 41  # From DMS
    test_base['offset'] = test_base['off_alpha_round']
    
    # Create cipher
    cipher = ShadowModifiedCipher(test_mask, test_base, test_shadow)
    
    # Test decryption
    for config in ['S-Light', 'S-Swap', 'S-Tri']:
        plaintext = cipher.decrypt(test_ct, config)
        print(f"\n{config}:")
        print(f"  Head: {plaintext[:20]}")
        print(f"  EAST region: {plaintext[21:34]}")
    
    # Show zone profiles
    print("\nZone Profiles:")
    for profile in cipher.get_zone_profiles():
        print(f"  {profile}")

if __name__ == "__main__":
    test_shadow_cipher()