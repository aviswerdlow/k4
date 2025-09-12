#!/usr/bin/env python3
"""
Berlin Clock (Mengenlehreuhr) Simulator
Deterministic implementation with frozen constants
MASTER_SEED = 1337
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple

MASTER_SEED = 1337

class BerlinClockSimulator:
    """
    Berlin Clock simulator providing deterministic time-to-state conversion
    """
    
    def __init__(self):
        self.seed = MASTER_SEED
        
    def time_to_state(self, hour: int, minute: int) -> Dict:
        """
        Convert 24h time to Berlin Clock state
        
        Args:
            hour: 0-23
            minute: 0-59
            
        Returns:
            Dictionary with:
            - row1_5h: list[4] bool (5-hour blocks)
            - row2_1h: list[4] bool (1-hour blocks)
            - row3_5m: list[11] enum {0=off, 1=yellow, 2=red} (5-min blocks, 3/6/9 are red)
            - row4_1m: list[4] bool (1-minute blocks)
        """
        # Row 1: 5-hour blocks
        row1_5h = [i < (hour // 5) for i in range(4)]
        
        # Row 2: 1-hour blocks
        row2_1h = [i < (hour % 5) for i in range(4)]
        
        # Row 3: 5-minute blocks (11 lamps)
        # Positions 2, 5, 8 (0-indexed) are red quarter-hour markers
        five_min_count = minute // 5
        row3_5m = []
        for i in range(11):
            if i < five_min_count:
                # Check if quarter-hour position (3rd, 6th, 9th lamp = indices 2, 5, 8)
                if i in [2, 5, 8]:
                    row3_5m.append(2)  # Red
                else:
                    row3_5m.append(1)  # Yellow
            else:
                row3_5m.append(0)  # Off
        
        # Row 4: 1-minute blocks
        row4_1m = [i < (minute % 5) for i in range(4)]
        
        return {
            'row1_5h': row1_5h,
            'row2_1h': row2_1h,
            'row3_5m': row3_5m,
            'row4_1m': row4_1m
        }
    
    def state_to_keystream(self, state: Dict, method: str) -> List[int]:
        """
        Convert Berlin Clock state to 26-length keystream
        
        Args:
            state: Clock state from time_to_state
            method: Mapping method name
            
        Returns:
            List of 26 integers (0-25)
        """
        if method == 'on_off_count_per_row':
            return self._on_off_count_keystream(state)
        elif method == 'base5_vector':
            return self._base5_vector_keystream(state)
        elif method == 'pattern_signature':
            return self._pattern_signature_keystream(state)
        elif method == 'row3_triplet_marks':
            return self._row3_triplet_keystream(state)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _on_off_count_keystream(self, state: Dict) -> List[int]:
        """
        Map each row's count of lit lamps to keystream
        Frozen constants: repeat_factor=7, offset=3
        """
        counts = [
            sum(state['row1_5h']),  # 0-4
            sum(state['row2_1h']),  # 0-4
            sum(1 if x > 0 else 0 for x in state['row3_5m']),  # 0-11
            sum(state['row4_1m'])   # 0-4
        ]
        
        # Build 26-long keystream by repeating pattern
        # Frozen rule: k[i] = counts[i % 4] * 7 + i * 3
        keystream = []
        for i in range(26):
            row_idx = i % 4
            k_val = (counts[row_idx] * 7 + i * 3) % 26
            keystream.append(k_val)
        
        return keystream
    
    def _base5_vector_keystream(self, state: Dict) -> List[int]:
        """
        Interpret rows as base-5 digits, hash into 26 positions
        Frozen constants: a=11, b=7, c=13
        """
        # Convert to base-5 values
        values = [
            sum(state['row1_5h']),  # 0-4
            sum(state['row2_1h']),  # 0-4
            min(sum(1 if x > 0 else 0 for x in state['row3_5m']) // 2, 4),  # Scale to 0-4
            sum(state['row4_1m'])   # 0-4
        ]
        
        # Compute base-5 number
        base5_num = values[0] * 125 + values[1] * 25 + values[2] * 5 + values[3]
        
        # Hash into 26 positions with frozen constants
        a, b, c = 11, 7, 13
        keystream = []
        for i in range(26):
            k_val = (a * base5_num + b * i + c) % 26
            keystream.append(k_val)
        
        return keystream
    
    def _pattern_signature_keystream(self, state: Dict) -> List[int]:
        """
        Stable hash of on/off pattern per row
        Using FNV-1a hash with frozen prime
        """
        # Create binary signature
        sig_parts = []
        
        # Row 1 binary
        sig_parts.append(''.join('1' if x else '0' for x in state['row1_5h']))
        
        # Row 2 binary
        sig_parts.append(''.join('1' if x else '0' for x in state['row2_1h']))
        
        # Row 3 ternary (0=off, 1=yellow, 2=red)
        sig_parts.append(''.join(str(x) for x in state['row3_5m']))
        
        # Row 4 binary
        sig_parts.append(''.join('1' if x else '0' for x in state['row4_1m']))
        
        # Combine signature
        full_sig = '|'.join(sig_parts)
        
        # FNV-1a hash
        fnv_prime = 16777619
        fnv_offset = 2166136261
        
        hash_val = fnv_offset
        for byte in full_sig.encode():
            hash_val ^= byte
            hash_val = (hash_val * fnv_prime) & 0xFFFFFFFF
        
        # Generate keystream from hash
        keystream = []
        for i in range(26):
            # Use different byte positions from hash
            byte_val = (hash_val >> ((i % 4) * 8)) & 0xFF
            k_val = (byte_val + i) % 26
            keystream.append(k_val)
        
        return keystream
    
    def _row3_triplet_keystream(self, state: Dict) -> List[int]:
        """
        Use row3 quarter-hour markers (positions 3,6,9) for sparse keystream
        Non-zero only at specific steps
        """
        # Check which quarter-hour markers are lit (indices 2, 5, 8)
        quarter_marks = []
        for idx in [2, 5, 8]:
            if idx < len(state['row3_5m']) and state['row3_5m'][idx] == 2:  # Red
                quarter_marks.append(1)
            else:
                quarter_marks.append(0)
        
        # Build sparse keystream
        # Frozen rule: activate at positions 0, 8, 16 if corresponding quarter is lit
        # Fill others with pattern based on lit quarters
        keystream = []
        num_quarters = sum(quarter_marks)
        
        for i in range(26):
            if i == 0 and quarter_marks[0]:
                k_val = 15  # First quarter marker value
            elif i == 8 and quarter_marks[1]:
                k_val = 30 % 26  # Second quarter marker value
            elif i == 16 and quarter_marks[2]:
                k_val = 45 % 26  # Third quarter marker value
            else:
                # Fill with pattern based on number of lit quarters
                k_val = (num_quarters * 5 + i * 2) % 26
            
            keystream.append(k_val)
        
        return keystream


def generate_methods_manifest():
    """
    Generate frozen constants manifest
    """
    manifest = {
        "seed": MASTER_SEED,
        "methods": {
            "on_off_count_per_row": {
                "description": "Map row counts to keystream",
                "constants": {
                    "repeat_factor": 7,
                    "position_offset": 3,
                    "formula": "k[i] = (counts[i%4] * 7 + i * 3) % 26"
                }
            },
            "base5_vector": {
                "description": "Interpret as base-5, hash to keystream",
                "constants": {
                    "a": 11,
                    "b": 7,
                    "c": 13,
                    "formula": "k[i] = (11 * base5_num + 7 * i + 13) % 26"
                }
            },
            "pattern_signature": {
                "description": "FNV-1a hash of pattern",
                "constants": {
                    "fnv_prime": 16777619,
                    "fnv_offset": 2166136261,
                    "extraction": "byte-wise from hash"
                }
            },
            "row3_triplet_marks": {
                "description": "Quarter-hour markers drive sparse keystream",
                "constants": {
                    "marker_positions": [0, 8, 16],
                    "marker_values": [15, 4, 19],  # 30%26=4, 45%26=19
                    "fill_formula": "k[i] = (num_quarters * 5 + i * 2) % 26"
                }
            }
        }
    }
    
    return manifest


if __name__ == "__main__":
    # Test the simulator
    clock = BerlinClockSimulator()
    
    # Test time: 14:35 (2:35 PM)
    state = clock.time_to_state(14, 35)
    print("Berlin Clock state for 14:35:")
    print(json.dumps(state, indent=2))
    
    # Test all methods
    print("\nKeystreams:")
    for method in ['on_off_count_per_row', 'base5_vector', 'pattern_signature', 'row3_triplet_marks']:
        keystream = clock.state_to_keystream(state, method)
        print(f"{method}: {keystream[:10]}... (first 10 of 26)")
    
    # Save manifest
    manifest = generate_methods_manifest()
    with open('METHODS_MANIFEST.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    print("\nMETHODS_MANIFEST.json generated")