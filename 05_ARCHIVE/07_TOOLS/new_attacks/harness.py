#!/usr/bin/env python3
"""
Fork C - New Attack Vectors Harness
Orchestrates mechanism tests to find constraints that reduce unknowns.
"""

import json
import csv
import sys
import os
import importlib
import hashlib
from datetime import datetime

MASTER_SEED = 1337

class AttackHarness:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.doc_path = os.path.join(self.base_path, '../../06_DOCUMENTATION/NEW_ATTACKS')
        self.data_path = os.path.join(self.base_path, '../../02_DATA')
        
        # Load common data
        self.load_common_data()
        
    def load_common_data(self):
        """Load all common data files"""
        # Load anchors
        with open(f'{self.doc_path}/COMMON/anchors.json', 'r') as f:
            self.anchors_data = json.load(f)
            
        # Load tail
        with open(f'{self.doc_path}/COMMON/tail_23.json', 'r') as f:
            self.tail_data = json.load(f)
            
        # Load baseline unknowns
        with open(f'{self.doc_path}/COMMON/baseline_u50.json', 'r') as f:
            self.baseline_data = json.load(f)
            
        # Load class function
        with open(f'{self.doc_path}/COMMON/class_function.json', 'r') as f:
            self.class_data = json.load(f)
            
        # Load ciphertext
        with open(f'{self.data_path}/ciphertext_97.txt', 'r') as f:
            self.ciphertext = f.read().strip()
            
        # Load canonical plaintext (for validation only)
        with open(os.path.join(self.base_path, '../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt'), 'r') as f:
            self.canonical_pt = f.read().strip()
    
    def compute_class(self, i):
        """Compute class for position i"""
        return ((i % 2) * 3) + (i % 3)
    
    def get_anchor_positions(self):
        """Get all anchor positions"""
        positions = set()
        for anchor in self.anchors_data['anchors']:
            for i in range(anchor['start'], anchor['end'] + 1):
                positions.add(i)
        return positions
    
    def get_tail_positions(self):
        """Get all tail positions"""
        tail = self.tail_data['tail']
        return set(range(tail['start'], tail['end'] + 1))
    
    def build_baseline_wheels(self, use_tail=False):
        """Build L=17 wheels from anchors (+ optional tail)"""
        L = 17
        wheels = {}
        
        # Initialize wheels
        for c in range(6):
            wheels[c] = {
                'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
                'L': L,
                'residues': [None] * L
            }
        
        # Apply anchor constraints
        anchor_positions = self.get_anchor_positions()
        for pos in anchor_positions:
            c = self.compute_class(pos)
            s = pos % L
            
            c_char = self.ciphertext[pos]
            p_char = self.canonical_pt[pos]
            
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            if wheels[c]['family'] == 'vigenere':
                k_val = (c_val - p_val) % 26
            else:
                k_val = (p_val + c_val) % 26
            
            wheels[c]['residues'][s] = k_val
        
        # Optionally apply tail constraints
        if use_tail:
            tail_positions = self.get_tail_positions()
            for pos in tail_positions:
                c = self.compute_class(pos)
                s = pos % L
                
                c_char = self.ciphertext[pos]
                p_char = self.canonical_pt[pos]
                
                c_val = ord(c_char) - ord('A')
                p_val = ord(p_char) - ord('A')
                
                if wheels[c]['family'] == 'vigenere':
                    k_val = (c_val - p_val) % 26
                else:
                    k_val = (p_val + c_val) % 26
                
                wheels[c]['residues'][s] = k_val
        
        return wheels
    
    def derive_plaintext(self, wheels, L=17):
        """Derive plaintext from wheels"""
        derived = []
        derived_count = 0
        unknown_indices = []
        
        for i in range(97):
            c = self.compute_class(i)
            s = i % L
            
            if s < len(wheels[c]['residues']) and wheels[c]['residues'][s] is not None:
                c_char = self.ciphertext[i]
                c_val = ord(c_char) - ord('A')
                k_val = wheels[c]['residues'][s]
                
                if wheels[c]['family'] == 'vigenere':
                    p_val = (c_val - k_val) % 26
                else:
                    p_val = (k_val - c_val) % 26
                
                derived.append(chr(p_val + ord('A')))
                derived_count += 1
            else:
                derived.append('?')
                unknown_indices.append(i)
        
        return ''.join(derived), derived_count, unknown_indices
    
    def validate_anchors(self, plaintext):
        """Check if anchors are preserved"""
        for anchor in self.anchors_data['anchors']:
            for i in range(anchor['start'], anchor['end'] + 1):
                if plaintext[i] != self.canonical_pt[i]:
                    return False
        return True
    
    def validate_known(self, plaintext, original_unknowns):
        """Check if known positions (non-unknowns) are preserved"""
        for i in range(97):
            if i not in original_unknowns and plaintext[i] != '?':
                if plaintext[i] != self.canonical_pt[i]:
                    return False
        return True
    
    def run_mechanism(self, mech_name):
        """Run a specific mechanism test"""
        print(f"\n=== Running Mechanism {mech_name} ===")
        
        # Import mechanism module
        try:
            mech_module = importlib.import_module(f'mech_{mech_name.lower()}')
        except ImportError:
            print(f"Module mech_{mech_name.lower()}.py not found")
            return None
        
        # Create output directory
        output_dir = f"{self.doc_path}/RUNS/{mech_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Get baseline unknowns
        baseline_wheels = self.build_baseline_wheels(use_tail=True)
        _, baseline_derived, baseline_unknowns = self.derive_plaintext(baseline_wheels)
        
        print(f"Baseline: {baseline_derived}/97 derived, {len(baseline_unknowns)} unknowns")
        
        # Run mechanism
        results = mech_module.run_tests(self)
        
        # Save results
        if results:
            # Save CSV
            with open(f"{output_dir}/RESULTS.csv", 'w', newline='') as f:
                if results['tests']:
                    # Get all unique keys from all test results
                    all_keys = set()
                    for test in results['tests']:
                        all_keys.update(test.keys())
                    fieldnames = sorted(all_keys)
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results['tests'])
            
            # Save summary
            with open(f"{output_dir}/SUMMARY.json", 'w') as f:
                json.dump(results['summary'], f, indent=2)
            
            # Generate PDF if module has the function
            if hasattr(mech_module, 'generate_pdf'):
                mech_module.generate_pdf(results, output_dir)
            
            print(f"Results saved to {output_dir}/")
            
            # Report success/failure
            if results['summary']['best_unknown_count'] < len(baseline_unknowns):
                print(f"✓ SUCCESS: Reduced unknowns from {len(baseline_unknowns)} to {results['summary']['best_unknown_count']}")
            else:
                print(f"✗ No reduction: Still {results['summary']['best_unknown_count']} unknowns")
        
        return results

def main():
    """Main entry point"""
    if len(sys.argv) < 3 or sys.argv[1] != '--run':
        print("Usage: python harness.py --run C1|C2|C3|C4|C5|C6|C7")
        sys.exit(1)
    
    mech_name = sys.argv[2]
    harness = AttackHarness()
    harness.run_mechanism(mech_name)

if __name__ == "__main__":
    main()