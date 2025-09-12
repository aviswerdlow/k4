#!/usr/bin/env python3
"""
Fork H3 - Running Key Cipher Engines
Vigenère, Beaufort, and Variant-Beaufort with running keys
"""

from typing import Dict, List, Tuple, Optional
from keysources import KeySources
from utils_h import UtilsH

class RunningKeyCipher:
    def __init__(self, master_seed: int = 1337):
        self.utils = UtilsH(master_seed)
        self.key_sources = KeySources()
        self.master_seed = master_seed
        
        # Zone definitions for segmented mode
        self.zones = {
            'Z0': {'start': 0, 'end': 20},     # Head
            'Z1': {'start': 21, 'end': 24},    # EAST
            'Z2': {'start': 25, 'end': 33},    # NORTHEAST
            'Z3': {'start': 34, 'end': 62},    # Between anchors
            'Z4': {'start': 63, 'end': 68},    # BERLIN
            'Z5': {'start': 69, 'end': 73},    # CLOCK
            'Z6': {'start': 74, 'end': 96}     # Tail
        }
    
    def apply_running_key(self, mode: str, config: Dict) -> Tuple[str, List[Dict], bool]:
        """
        Apply running key cipher in specified mode
        
        Args:
            mode: 'global', 'segmented', or 'hybrid_reset'
            config: Configuration dict with keysource, family, offsets
        
        Returns:
            (plaintext, derivations, option_a_ok)
        """
        plaintext = ['?'] * 97
        derivations = []
        option_a_ok = True
        
        if mode == 'global':
            result = self._apply_global(config)
        elif mode == 'segmented':
            result = self._apply_segmented(config)
        elif mode == 'hybrid_reset':
            result = self._apply_hybrid_reset(config)
        else:
            return None, [], False
        
        return result
    
    def _apply_global(self, config: Dict) -> Tuple[str, List[Dict], bool]:
        """Apply with single key source and offset globally"""
        keysource = config.get('keysource', 'K1K2K3')
        family = config.get('family', 'vigenere')
        offset = config.get('offset', 0)
        
        plaintext = ['?'] * 97
        derivations = []
        
        # First verify anchors are consistent
        for anchor_name, anchor_data in self.utils.anchors.items():
            start = anchor_data['start']
            end = anchor_data['end']
            expected = anchor_data['text']
            
            for i, p_char in enumerate(expected):
                global_idx = start + i
                c_char = self.utils.k4_ct[global_idx]
                
                # Get key from source
                k_char = self.key_sources.get_key_at(keysource, global_idx, offset)
                if k_char == '?':
                    return None, [], False
                
                # Verify this produces correct plaintext
                p_derived = self.utils.family_apply(family, c_char, k_char)
                
                if p_derived != p_char:
                    # Key source doesn't produce correct anchor
                    return None, [], False
                
                # Check Option A
                if not self.utils.option_a_enforce(family, c_char, p_char):
                    return None, [], False
                
                plaintext[global_idx] = p_char
        
        # Now derive non-anchor positions
        for idx in range(97):
            if plaintext[idx] != '?':
                continue
            
            c_char = self.utils.k4_ct[idx]
            k_char = self.key_sources.get_key_at(keysource, idx, offset)
            
            if k_char == '?':
                continue
            
            p_char = self.utils.family_apply(family, c_char, k_char)
            plaintext[idx] = p_char
            
            # Record derivation for head and key positions
            if idx <= 20 or (34 <= idx <= 62):
                derivations.append({
                    'index': idx,
                    'c': c_char,
                    'family': family,
                    'k_source': f"{keysource}+{offset}",
                    'k': k_char,
                    'p': p_char,
                    'notes': 'global'
                })
        
        return ''.join(plaintext), derivations, True
    
    def _apply_segmented(self, config: Dict) -> Tuple[str, List[Dict], bool]:
        """Apply with different parameters per zone"""
        plaintext = ['?'] * 97
        derivations = []
        
        # Get zone configurations
        zone_configs = config.get('zones', {})
        
        # First pass: verify anchors
        for anchor_name, anchor_data in self.utils.anchors.items():
            start = anchor_data['start']
            end = anchor_data['end']
            expected = anchor_data['text']
            
            # Find which zone contains this anchor
            zone_name = None
            for zn, zinfo in self.zones.items():
                if start >= zinfo['start'] and start <= zinfo['end']:
                    zone_name = zn
                    break
            
            if not zone_name or zone_name not in zone_configs:
                return None, [], False
            
            zconfig = zone_configs[zone_name]
            keysource = zconfig.get('keysource', 'K1K2K3')
            family = zconfig.get('family', 'vigenere')
            offset = zconfig.get('offset', 0)
            
            for i, p_char in enumerate(expected):
                global_idx = start + i
                c_char = self.utils.k4_ct[global_idx]
                
                # Position within zone
                zone_start = self.zones[zone_name]['start']
                local_idx = global_idx - zone_start
                
                # Get key from source
                k_char = self.key_sources.get_key_at(keysource, local_idx, offset)
                if k_char == '?':
                    return None, [], False
                
                # Verify this produces correct plaintext
                p_derived = self.utils.family_apply(family, c_char, k_char)
                
                if p_derived != p_char:
                    return None, [], False
                
                # Check Option A
                if not self.utils.option_a_enforce(family, c_char, p_char):
                    return None, [], False
                
                plaintext[global_idx] = p_char
        
        # Second pass: derive non-anchor positions
        for zone_name, zinfo in self.zones.items():
            if zone_name not in zone_configs:
                continue
            
            zconfig = zone_configs[zone_name]
            keysource = zconfig.get('keysource', 'K1K2K3')
            family = zconfig.get('family', 'vigenere')
            offset = zconfig.get('offset', 0)
            
            for local_idx in range(zinfo['end'] - zinfo['start'] + 1):
                global_idx = zinfo['start'] + local_idx
                
                if plaintext[global_idx] != '?':
                    continue
                
                c_char = self.utils.k4_ct[global_idx]
                k_char = self.key_sources.get_key_at(keysource, local_idx, offset)
                
                if k_char == '?':
                    continue
                
                p_char = self.utils.family_apply(family, c_char, k_char)
                plaintext[global_idx] = p_char
                
                # Record derivation
                if global_idx <= 20 or (34 <= global_idx <= 62):
                    derivations.append({
                        'index': global_idx,
                        'c': c_char,
                        'family': family,
                        'k_source': f"{keysource}+{offset}",
                        'k': k_char,
                        'p': p_char,
                        'notes': f'zone_{zone_name}'
                    })
        
        return ''.join(plaintext), derivations, True
    
    def _apply_hybrid_reset(self, config: Dict) -> Tuple[str, List[Dict], bool]:
        """Same keysource/family but reset offset at zone boundaries"""
        keysource = config.get('keysource', 'K1K2K3')
        family = config.get('family', 'vigenere')
        
        # Build zone configs with offset=0 at each boundary
        zone_configs = {}
        for zone_name in self.zones:
            zone_configs[zone_name] = {
                'keysource': keysource,
                'family': family,
                'offset': 0  # Reset at each zone
            }
        
        # Use segmented application with reset offsets
        config_with_zones = {
            'zones': zone_configs
        }
        
        return self._apply_segmented(config_with_zones)
    
    def test_configuration(self, mode: str, config: Dict) -> Dict:
        """Test a running key configuration"""
        # Apply cipher
        plaintext, derivations, option_a_ok = self.apply_running_key(mode, config)
        
        if plaintext is None or not option_a_ok:
            return {'status': 'failed', 'reason': 'anchor_mismatch_or_option_a'}
        
        # Check anchors (should already be correct but verify)
        if not self.utils.check_anchors(plaintext):
            return {'status': 'failed', 'reason': 'anchors_incorrect'}
        
        # Count unknowns
        unknowns_before = 50  # Non-anchor positions
        unknowns_after = self.utils.count_unknowns(plaintext)
        
        # Check head sanity
        head = plaintext[:21]
        head_sanity = self.utils.english_sanity(head)
        
        # Build result
        result = {
            'status': 'success',
            'mode': mode,
            'config': config,
            'plaintext': plaintext,
            'head': head,
            'unknowns_before': unknowns_before,
            'unknowns_after': unknowns_after,
            'reduction': unknowns_before - unknowns_after,
            'head_sanity': head_sanity,
            'derivations': derivations[:30]  # Limit for space
        }
        
        return result


def main():
    """Test running key engines"""
    rk = RunningKeyCipher()
    
    print("=== Fork H3 - Running Key Engines Test ===\n")
    
    # Test global mode
    print("Testing global mode with K1K2K3...")
    config = {
        'keysource': 'K1K2K3',
        'family': 'vigenere',
        'offset': 0
    }
    
    result = rk.test_configuration('global', config)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Unknowns: {result['unknowns_before']} -> {result['unknowns_after']}")
        print(f"Head: {result['head']}")
        print(f"Head OK: {result['head_sanity']['ok']}")
        if result['head_sanity']['words_found']:
            print(f"Words: {result['head_sanity']['words_found']}")
    else:
        print(f"Reason: {result['reason']}")
    
    # Test with different offset
    print("\nTesting with offset=100...")
    config['offset'] = 100
    result = rk.test_configuration('global', config)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Head: {result['head']}")


if __name__ == "__main__":
    main()