#!/usr/bin/env python3
"""
Fork F v3: Standalone Propagation
Turn MERIDIAN and top candidates into actual letters
MASTER_SEED = 1337
"""

import os
import json
import csv
import random
import hashlib
from typing import List, Dict, Tuple, Optional

MASTER_SEED = 1337
random.seed(MASTER_SEED)

class StandalonePropagator:
    """Simplified propagator without import dependencies"""
    
    def __init__(self):
        # Load ciphertext
        self.ciphertext = self.load_ciphertext()
        
        # Known anchors
        self.anchors = {
            21: 'E', 22: 'A', 23: 'S', 24: 'T',
            25: 'N', 26: 'O', 27: 'R', 28: 'T',
            29: 'H', 30: 'E', 31: 'A', 32: 'S', 33: 'T',
            63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',
            69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'
        }
        
        # Unknown positions
        self.unknowns = [i for i in range(97) if i not in self.anchors]
        
        # Family assignment
        self.family_by_class = {
            0: 'beaufort',
            1: 'vigenere',
            2: 'beaufort',
            3: 'vigenere',
            4: 'beaufort',
            5: 'vigenere'
        }
        
    def load_ciphertext(self) -> str:
        """Load K4 ciphertext"""
        path = '../../02_DATA/ciphertext_97.txt'
        with open(path, 'r') as f:
            return f.read().strip()
    
    def compute_class(self, i: int) -> int:
        """Compute class for position"""
        return ((i % 2) * 3) + (i % 3)
    
    def compute_residue(self, c_val: int, p_val: int, family: str) -> int:
        """Compute key residue"""
        if family == 'vigenere':
            return (c_val - p_val) % 26
        elif family == 'beaufort':
            return (p_val - c_val) % 26
        else:
            return (c_val + p_val) % 26
    
    def propagate_meridian(self, start: int = 8, L: int = 11, phase: int = 0):
        """
        Propagate MERIDIAN placement to derive new letters
        """
        token = "MERIDIAN"
        
        print(f"\n=== Propagating {token}@{start} L={L} phase={phase} ===\n")
        
        # Build baseline wheels from anchors
        wheels = {}
        for c in range(6):
            wheels[c] = {
                'family': self.family_by_class[c],
                'slots': {}
            }
        
        # Add anchor constraints
        for pos, pt_char in self.anchors.items():
            c = self.compute_class(pos)
            s = (pos - phase) % L
            
            ct_char = self.ciphertext[pos]
            c_val = ord(ct_char) - ord('A')
            p_val = ord(pt_char) - ord('A')
            
            k_req = self.compute_residue(c_val, p_val, wheels[c]['family'])
            
            if s not in wheels[c]['slots']:
                wheels[c]['slots'][s] = k_req
        
        print(f"Baseline: {sum(len(w['slots']) for w in wheels.values())} constraints from anchors")
        
        # Add MERIDIAN constraints
        new_constraints = []
        for i, pt_char in enumerate(token):
            pos = start + i
            
            # Skip if it's an anchor
            if pos in self.anchors:
                continue
                
            c = self.compute_class(pos)
            s = (pos - phase) % L
            
            ct_char = self.ciphertext[pos]
            c_val = ord(ct_char) - ord('A')
            p_val = ord(pt_char) - ord('A')
            
            k_req = self.compute_residue(c_val, p_val, wheels[c]['family'])
            
            # Check for conflicts
            if s in wheels[c]['slots']:
                if wheels[c]['slots'][s] != k_req:
                    print(f"  CONFLICT at pos {pos}: slot {s} has {wheels[c]['slots'][s]}, needs {k_req}")
                    return None
            else:
                wheels[c]['slots'][s] = k_req
                new_constraints.append((c, s, k_req))
        
        print(f"Added {len(new_constraints)} new constraints from {token}")
        print(f"Total: {sum(len(w['slots']) for w in wheels.values())} constraints\n")
        
        # Now derive plaintext
        plaintext = ['?'] * 97
        
        # Place anchors
        for pos, letter in self.anchors.items():
            plaintext[pos] = letter
        
        # Place MERIDIAN
        for i, char in enumerate(token):
            plaintext[start + i] = char
        
        # Propagate using wheels
        new_letters = {}
        for pos in range(97):
            if plaintext[pos] == '?':
                c = self.compute_class(pos)
                s = (pos - phase) % L
                
                if s in wheels[c]['slots']:
                    k_val = wheels[c]['slots'][s]
                    ct_char = self.ciphertext[pos]
                    c_val = ord(ct_char) - ord('A')
                    
                    family = wheels[c]['family']
                    
                    if family == 'vigenere':
                        p_val = (c_val - k_val) % 26
                    elif family == 'beaufort':
                        p_val = (k_val - c_val) % 26
                    else:
                        p_val = (k_val - c_val) % 26
                    
                    letter = chr(p_val + ord('A'))
                    plaintext[pos] = letter
                    new_letters[pos] = letter
        
        # Show results
        pt_str = ''.join(plaintext)
        unknown_after = pt_str.count('?')
        
        print("Derived plaintext (first 74 chars):")
        print(pt_str[:74])
        print()
        
        print(f"Statistics:")
        print(f"  Unknown before: {len(self.unknowns)}")
        print(f"  Unknown after: {unknown_after}")
        print(f"  Letters derived: {len(new_letters)}")
        print(f"  Gains: {len(self.unknowns) - unknown_after}")
        
        # Show some newly derived positions
        if new_letters:
            print(f"\nSample of newly derived letters:")
            for pos in sorted(new_letters.keys())[:10]:
                print(f"  Position {pos}: {new_letters[pos]}")
        
        # Save result
        result = {
            "token": token,
            "start": start,
            "L": L,
            "phase": phase,
            "unknown_before": len(self.unknowns),
            "unknown_after": unknown_after,
            "gains": len(self.unknowns) - unknown_after,
            "new_letters_count": len(new_letters),
            "plaintext_head": pt_str[:74],
            "plaintext_tail": pt_str[74:],
            "sha_plaintext": hashlib.sha256(pt_str.encode()).hexdigest()[:16],
            "new_constraints": new_constraints,
            "master_seed": MASTER_SEED
        }
        
        filename = f"F3_cards/single/MERIDIAN_{start:02d}_standalone.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nSaved to {filename}")
        
        return result
    
    def test_multiple_meridians(self):
        """Test MERIDIAN at different positions"""
        positions = [8, 9, 10, 12, 74, 75, 76, 77, 78]
        
        print("=== Testing MERIDIAN at Multiple Positions ===")
        
        results = []
        for pos in positions[:5]:  # Test first 5
            result = self.propagate_meridian(start=pos)
            if result:
                results.append(result)
                print(f"\n{'='*60}\n")
        
        # Summary
        print("\n=== Summary ===")
        for r in results:
            print(f"MERIDIAN@{r['start']}: {r['gains']} gains, "
                  f"{r['new_letters_count']} new letters")
        
        return results


def main():
    """Main execution"""
    propagator = StandalonePropagator()
    
    # Test MERIDIAN at position 8 (top candidate)
    result = propagator.propagate_meridian(start=8, L=11, phase=0)
    
    # Test multiple positions
    print("\n" + "="*60)
    results = propagator.test_multiple_meridians()


if __name__ == "__main__":
    main()