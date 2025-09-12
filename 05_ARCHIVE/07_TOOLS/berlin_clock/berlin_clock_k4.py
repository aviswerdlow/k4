#!/usr/bin/env python3
"""
Berlin Clock K4 Application
Tests Berlin Clock keystreams against K4 unknown positions
Generates result cards with strict schema compliance
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

class BerlinClockK4:
    """Apply Berlin Clock keystreams to K4 unknowns"""
    
    def __init__(self):
        self.seed = MASTER_SEED
        self.clock = BerlinClockSimulator()
        self.load_k4_data()
        
    def load_k4_data(self):
        """Load K4 ciphertext and build canonical plaintext with only known anchors"""
        with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
            self.ciphertext = f.read().strip()
        
        # Build canonical plaintext with ONLY known anchors
        # Start with all unknowns
        self.canonical_pt = ['?'] * 97
        
        # Fill in ONLY the known anchors
        known_anchors = {
            21: 'E', 22: 'A', 23: 'S', 24: 'T',  # EAST
            25: 'N', 26: 'O', 27: 'R', 28: 'T',  # NORTHEAST start
            29: 'H', 30: 'E', 31: 'A', 32: 'S', 33: 'T',  # NORTHEAST end
            63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',  # BERLIN
            69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'  # CLOCK
        }
        
        for pos, letter in known_anchors.items():
            self.canonical_pt[pos] = letter
        
        # NO TAIL PLAINTEXT - tail positions 74-96 remain unknown
        self.canonical_pt = ''.join(self.canonical_pt)
            
        # Define anchors
        self.anchors = []
        for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
            for i in range(start, end + 1):
                self.anchors.append(i)
        
        # Define tail (positions 74-96) - but we don't know their plaintext!
        self.tail = list(range(74, 97))
        
        # Only anchors are constrained (known plaintext)
        # Tail is NOT constrained for our purposes
        self.constrained = set(self.anchors)  # Only anchors, not tail
        
        # Unknown positions (73 total: 50 head + 23 tail)
        self.unknowns = [i for i in range(97) if i not in self.constrained]
        
    def compute_class(self, i: int) -> int:
        """Compute class for position i using baseline formula"""
        return ((i % 2) * 3) + (i % 3)
    
    def build_baseline_wheels(self) -> Dict:
        """Build L=17 baseline wheels from anchors and tail"""
        L = 17
        wheels = {}
        
        # Initialize 6 wheels
        for c in range(6):
            wheels[c] = {
                'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
                'L': L,
                'residues': [None] * L
            }
        
        # Fill ONLY from anchors (we don't know tail plaintext)
        for pos in self.anchors:
            c = self.compute_class(pos)
            s = pos % L
            
            c_char = self.ciphertext[pos]
            p_char = self.canonical_pt[pos] if pos < len(self.canonical_pt) else '?'
            
            if p_char != '?':
                c_val = ord(c_char) - ord('A')
                p_val = ord(p_char) - ord('A')
                
                if wheels[c]['family'] == 'vigenere':
                    k_val = (c_val - p_val) % 26
                else:  # beaufort
                    k_val = (p_val + c_val) % 26
                
                wheels[c]['residues'][s] = k_val
        
        return wheels
    
    def apply_keystream(self, keystream: List[int], wheels: Dict) -> Tuple[List[Optional[str]], bool]:
        """
        Apply keystream to unknown positions
        Returns: (derived_letters, anchors_preserved)
        """
        L = 17
        test_wheels = {}
        
        # Deep copy wheels
        for c in wheels:
            test_wheels[c] = {
                'family': wheels[c]['family'],
                'L': wheels[c]['L'],
                'residues': wheels[c]['residues'].copy()
            }
        
        # Apply keystream to unknowns
        for idx in self.unknowns:
            c = self.compute_class(idx)
            s = idx % L
            
            if test_wheels[c]['residues'][s] is None:
                # Use keystream value
                k_idx = idx % 26  # Map position to keystream index
                test_wheels[c]['residues'][s] = keystream[k_idx]
        
        # Derive plaintext
        derived = []
        for i in range(97):
            c = self.compute_class(i)
            s = i % L
            
            if test_wheels[c]['residues'][s] is not None:
                c_char = self.ciphertext[i]
                c_val = ord(c_char) - ord('A')
                k_val = test_wheels[c]['residues'][s]
                
                if test_wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:  # beaufort
                    p_val = (k_val - c_val) % 26
                
                derived.append(chr(p_val + ord('A')))
            else:
                derived.append(None)
        
        # Check anchor preservation
        anchors_preserved = True
        for pos in self.anchors:
            if derived[pos] is None or self.canonical_pt[pos] == '?':
                continue
            if derived[pos] != self.canonical_pt[pos]:
                anchors_preserved = False
                break
        
        return derived, anchors_preserved
    
    def test_wheel_families(self, keystream: List[int]) -> Dict:
        """
        Test keystream with all three wheel family interpretations
        Returns info about any newly determined positions
        """
        wheels = self.build_baseline_wheels()
        
        # Test with baseline (mixed) families
        derived_mixed, anchors_ok_mixed = self.apply_keystream(keystream, wheels)
        
        # Test with all Vigenère
        wheels_vig = {}
        for c in range(6):
            wheels_vig[c] = {
                'family': 'vigenere',
                'L': 17,
                'residues': wheels[c]['residues'].copy()
            }
        derived_vig, anchors_ok_vig = self.apply_keystream(keystream, wheels_vig)
        
        # Test with all Beaufort
        wheels_beau = {}
        for c in range(6):
            wheels_beau[c] = {
                'family': 'beaufort',
                'L': 17,
                'residues': wheels[c]['residues'].copy()
            }
        derived_beau, anchors_ok_beau = self.apply_keystream(keystream, wheels_beau)
        
        # Analyze results
        new_positions = []
        
        for idx in self.unknowns:
            # Check if position determined consistently
            vals = []
            if anchors_ok_mixed and derived_mixed[idx]:
                vals.append(('mixed', derived_mixed[idx]))
            if anchors_ok_vig and derived_vig[idx]:
                vals.append(('vigenere', derived_vig[idx]))
            if anchors_ok_beau and derived_beau[idx]:
                vals.append(('beaufort', derived_beau[idx]))
            
            # If all valid interpretations agree on a value
            if vals and all(v[1] == vals[0][1] for v in vals):
                new_positions.append({
                    'index': idx,
                    'value': vals[0][1],
                    'families': [v[0] for v in vals]
                })
        
        return {
            'new_positions': new_positions,
            'anchors_preserved': anchors_ok_mixed or anchors_ok_vig or anchors_ok_beau,
            'unknowns_after': len(self.unknowns) - len(new_positions)
        }
    
    def test_timestamp(self, dt: datetime, method: str) -> Dict:
        """Test a specific timestamp with given method"""
        # Get clock state
        state = self.clock.time_to_state(dt.hour, dt.minute)
        
        # Generate keystream
        keystream = self.clock.state_to_keystream(state, method)
        
        # Test against K4
        result = self.test_wheel_families(keystream)
        
        # Build result card
        mechanism_str = f"BerlinClock@{dt.isoformat()}/{method}"
        
        result_card = {
            "mechanism": mechanism_str,
            "unknowns_before": len(self.unknowns),
            "unknowns_after": result['unknowns_after'],
            "anchors_preserved": result['anchors_preserved'],
            "new_positions_determined": [p['index'] for p in result['new_positions']],
            "indices_before": self.unknowns.copy(),
            "indices_after": [i for i in self.unknowns if i not in [p['index'] for p in result['new_positions']]],
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
        
        # Define fixed timestamps (UTC)
        fixed_times = [
            # Kryptos dedication window
            datetime(1990, 11, 3, 14, 0, tzinfo=timezone.utc),
            
            # Berlin Wall opening
            datetime(1989, 11, 9, 18, 53, tzinfo=timezone.utc),
            
            # Every hour on the hour
            *[datetime(2024, 1, 1, h, 0, tzinfo=timezone.utc) for h in range(24)],
            
            # Clock quadrants
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 15, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 18, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 21, 0, tzinfo=timezone.utc),
        ]
        
        # Test all methods
        methods = ['on_off_count_per_row', 'base5_vector', 'pattern_signature', 'row3_triplet_marks']
        
        all_results = []
        hits = []
        
        for dt in fixed_times:
            for method in methods:
                result = self.test_timestamp(dt, method)
                all_results.append(result)
                
                # Save individual result card
                filename = f"{output_dir}/result_{dt.strftime('%Y%m%d_%H%M')}_{method}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Check for hits
                if result['unknowns_after'] < result['unknowns_before'] and result['anchors_preserved']:
                    hits.append(result)
                    print(f"HIT: {result['mechanism']} reduced unknowns from {result['unknowns_before']} to {result['unknowns_after']}")
        
        # Generate summary CSV
        with open(f"{output_dir}/RUN_SUMMARY.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'mechanism', 'timestamp', 'method', 
                'unknowns_before', 'unknowns_after', 
                'reduction', 'anchors_preserved', 'new_positions'
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
                    'anchors_preserved': r['anchors_preserved'],
                    'new_positions': len(r['new_positions_determined'])
                })
        
        # Save hits separately
        if hits:
            with open(f"{output_dir}/HITS.json", 'w') as f:
                json.dump(hits, f, indent=2)
        
        return len(hits) > 0
    
    def run_sweep(self, output_dir: str, start_dt: datetime, end_dt: datetime, interval_minutes: int):
        """Run sweep test over time range"""
        sweep_dir = f"{output_dir}/sweep_{start_dt.strftime('%Y%m%d_%H%M')}_{end_dt.strftime('%H%M')}"
        os.makedirs(sweep_dir, exist_ok=True)
        
        current = start_dt
        sweep_results = []
        
        while current <= end_dt:
            for method in ['on_off_count_per_row', 'base5_vector']:  # Sample methods for sweep
                result = self.test_timestamp(current, method)
                sweep_results.append({
                    'time': current.strftime('%H:%M'),
                    'method': method,
                    'reduction': result['unknowns_before'] - result['unknowns_after'],
                    'valid': result['anchors_preserved']
                })
            
            current += timedelta(minutes=interval_minutes)
        
        # Save sweep summary
        with open(f"{sweep_dir}/sweep_summary.json", 'w') as f:
            json.dump(sweep_results, f, indent=2)
        
        return sweep_results


def main():
    """Main execution"""
    print("=== Berlin Clock K4 Application ===")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    
    app = BerlinClockK4()
    
    print(f"K4 Configuration:")
    print(f"  Unknowns: {len(app.unknowns)} positions")
    print(f"  Anchors: {len(app.anchors)} positions")
    print(f"  Tail: {len(app.tail)} positions\n")
    
    # Run fixed timestamp tests
    print("Running fixed timestamp tests...")
    has_hits = app.run_fixed_timestamps('runs/fixed_timestamps')
    
    if has_hits:
        print("\n🎯 BREAKTHROUGH: Found configurations that reduce unknowns!")
        print("Check runs/fixed_timestamps/HITS.json for details")
    else:
        print("\nNo hits found in fixed timestamps (clean negative)")
    
    # Run hour sweep
    print("\nRunning hour sweep (00:00-00:59 every 5 min)...")
    start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, 0, 59, tzinfo=timezone.utc)
    app.run_sweep('runs', start, end, 5)
    
    print("\nResults saved to runs/")
    print("Check RUN_SUMMARY.csv for overview")


if __name__ == "__main__":
    main()