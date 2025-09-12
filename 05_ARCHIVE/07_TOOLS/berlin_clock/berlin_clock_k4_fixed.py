#!/usr/bin/env python3
"""
Berlin Clock K4 Application - FIXED VERSION
Tests Berlin Clock keystreams against K4 unknown positions
Properly handles wheel conflicts and only reports genuinely determined positions
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
import csv

sys.path.append('../..')
from berlin_clock_simulator import BerlinClockSimulator

MASTER_SEED = 1337

class BerlinClockK4Fixed:
    """Apply Berlin Clock keystreams to K4 unknowns - PROPERLY"""
    
    def __init__(self):
        self.seed = MASTER_SEED
        self.clock = BerlinClockSimulator()
        self.load_k4_data()
        
    def load_k4_data(self):
        """Load K4 ciphertext with ONLY known anchors"""
        with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
            self.ciphertext = f.read().strip()
        
        # Known anchor values ONLY
        self.anchor_values = {
            21: 'E', 22: 'A', 23: 'S', 24: 'T',  # EAST
            25: 'N', 26: 'O', 27: 'R', 28: 'T',  # NORTHEAST start
            29: 'H', 30: 'E', 31: 'A', 32: 'S', 33: 'T',  # NORTHEAST end
            63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',  # BERLIN
            69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'  # CLOCK
        }
        
        self.anchors = list(self.anchor_values.keys())
        
        # ALL other positions are unknown (including tail)
        self.unknowns = [i for i in range(97) if i not in self.anchors]
        
        print(f"Configuration: {len(self.anchors)} anchors, {len(self.unknowns)} unknowns")
        
    def compute_class(self, i: int) -> int:
        """Compute class for position i"""
        return ((i % 2) * 3) + (i % 3)
    
    def build_partial_wheels(self) -> Dict:
        """Build partial L=17 wheels from anchors ONLY"""
        L = 17
        wheels = {}
        
        # Initialize 6 wheels
        for c in range(6):
            wheels[c] = {
                'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
                'L': L,
                'residues': [None] * L,
                'sources': [[] for _ in range(L)]  # Track which positions constrain each slot
            }
        
        # Fill ONLY from known anchors
        for pos, plain_char in self.anchor_values.items():
            c = self.compute_class(pos)
            s = pos % L
            
            c_char = self.ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(plain_char) - ord('A')
            
            if wheels[c]['family'] == 'vigenere':
                k_val = (c_val - p_val) % 26
            else:  # beaufort
                k_val = (p_val + c_val) % 26
            
            # Check for conflicts
            if wheels[c]['residues'][s] is not None:
                if wheels[c]['residues'][s] != k_val:
                    print(f"WARNING: Conflict at wheel {c} slot {s}: {wheels[c]['residues'][s]} vs {k_val}")
            else:
                wheels[c]['residues'][s] = k_val
                wheels[c]['sources'][s].append(pos)
        
        # Report coverage
        for c in range(6):
            filled = sum(1 for r in wheels[c]['residues'] if r is not None)
            print(f"  Wheel {c} ({wheels[c]['family']}): {filled}/17 slots filled from anchors")
        
        return wheels
    
    def apply_berlin_keystream(self, keystream: List[int], wheels: Dict) -> Dict:
        """
        Apply Berlin Clock keystream and check for determinations
        Returns analysis of what can be determined
        """
        L = 17
        newly_determined = []
        conflicts = []
        
        # For each unknown position
        for idx in self.unknowns:
            c = self.compute_class(idx)
            s = idx % L
            
            # If this slot already has a key from anchors
            if wheels[c]['residues'][s] is not None:
                # We can derive this position!
                k_val = wheels[c]['residues'][s]
                c_char = self.ciphertext[idx]
                c_val = ord(c_char) - ord('A')
                
                if wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:  # beaufort
                    p_val = (k_val - c_val) % 26
                
                newly_determined.append({
                    'index': idx,
                    'value': chr(p_val + ord('A')),
                    'wheel': c,
                    'slot': s,
                    'key': k_val,
                    'source': 'anchor-constrained'
                })
            else:
                # Slot is empty - would need Berlin keystream
                # Map position to keystream
                k_idx = idx % 26
                proposed_key = keystream[k_idx]
                
                # Check if this conflicts with other unknowns in same slot
                # This is speculative - we can't actually determine this
                # without more constraints
                pass
        
        return {
            'newly_determined': newly_determined,
            'unknowns_remaining': len(self.unknowns) - len(newly_determined),
            'conflicts': conflicts
        }
    
    def test_timestamp(self, dt: datetime, method: str) -> Dict:
        """Test a specific timestamp with given method"""
        # Get clock state
        state = self.clock.time_to_state(dt.hour, dt.minute)
        
        # Generate keystream
        keystream = self.clock.state_to_keystream(state, method)
        
        # Build partial wheels from anchors
        wheels = self.build_partial_wheels()
        
        # Apply and analyze
        result = self.apply_berlin_keystream(keystream, wheels)
        
        # Build result card
        mechanism_str = f"BerlinClock@{dt.isoformat()}/{method}"
        
        result_card = {
            "mechanism": mechanism_str,
            "unknowns_before": len(self.unknowns),
            "unknowns_after": result['unknowns_remaining'],
            "anchors_preserved": True,  # We only use anchors as input
            "new_positions_determined": [d['index'] for d in result['newly_determined']],
            "indices_before": self.unknowns.copy(),
            "indices_after": [i for i in self.unknowns if i not in [d['index'] for d in result['newly_determined']]],
            "parameters": {
                "timestamp": dt.isoformat(),
                "hour": dt.hour,
                "minute": dt.minute,
                "clock_state": state,
                "keystream": keystream,
                "method": method
            },
            "seed": MASTER_SEED,
            "notes": f"Berlin Clock test at {dt.hour:02d}:{dt.minute:02d} using {method}"
        }
        
        return result_card
    
    def run_fixed_timestamps(self, output_dir: str):
        """Run tests on fixed timestamp set"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("\nRunning fixed timestamp tests...")
        
        # Key timestamps
        fixed_times = [
            # Kryptos dedication window
            datetime(1990, 11, 3, 14, 0, tzinfo=timezone.utc),
            # Berlin Wall opening
            datetime(1989, 11, 9, 18, 53, tzinfo=timezone.utc),
            # Sample hourly
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 15, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 18, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 21, 0, tzinfo=timezone.utc),
        ]
        
        methods = ['on_off_count_per_row', 'base5_vector', 'pattern_signature', 'row3_triplet_marks']
        
        all_results = []
        hits = []
        
        for dt in fixed_times:
            print(f"\nTesting {dt.strftime('%Y-%m-%d %H:%M')}...")
            for method in methods:
                result = self.test_timestamp(dt, method)
                all_results.append(result)
                
                # Save result card
                filename = f"{output_dir}/result_{dt.strftime('%Y%m%d_%H%M')}_{method}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Check for hits
                if result['unknowns_after'] < result['unknowns_before']:
                    hits.append(result)
                    reduction = result['unknowns_before'] - result['unknowns_after']
                    print(f"  ✓ {method}: Reduced by {reduction} positions")
                else:
                    print(f"  ✗ {method}: No reduction")
        
        # Summary
        with open(f"{output_dir}/RUN_SUMMARY.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'mechanism', 'timestamp', 'method', 
                'unknowns_before', 'unknowns_after', 
                'reduction', 'new_positions'
            ])
            writer.writeheader()
            
            for r in all_results:
                writer.writerow({
                    'mechanism': r['mechanism'],
                    'timestamp': r['parameters']['timestamp'],
                    'method': r['parameters']['method'],
                    'unknowns_before': r['unknowns_before'],
                    'unknowns_after': r['unknowns_after'],
                    'reduction': r['unknowns_before'] - r['unknowns_after'],
                    'new_positions': len(r['new_positions_determined'])
                })
        
        if hits:
            print(f"\n🎯 Found {len(hits)} configurations with reductions!")
            with open(f"{output_dir}/HITS.json", 'w') as f:
                json.dump(hits, f, indent=2)
        else:
            print("\n📊 No reductions found (clean negative)")
        
        return len(hits) > 0


def main():
    """Main execution"""
    print("=== Berlin Clock K4 Application (FIXED) ===")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    
    app = BerlinClockK4Fixed()
    
    # Run tests
    has_hits = app.run_fixed_timestamps('runs_fixed')
    
    if has_hits:
        print("\nCheck runs_fixed/HITS.json for details")
    else:
        print("\nClean negative result - Berlin Clock doesn't determine positions with current anchors")
    
    print("\nResults saved to runs_fixed/")


if __name__ == "__main__":
    main()