#!/usr/bin/env python3
"""
Fork F v3: Multi-anchor Synthesis (Greedy Packer)
Combine multiple non-conflicting placements
MASTER_SEED = 1337
"""

import os
import json
import csv
from typing import List, Dict, Tuple, Set

MASTER_SEED = 1337

class MultiAnchorSynthesis:
    """Greedy packing of multiple candidates"""
    
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
        
        # Family assignment
        self.family_by_class = {
            0: 'beaufort', 1: 'vigenere', 2: 'beaufort',
            3: 'vigenere', 4: 'beaufort', 5: 'vigenere'
        }
        
        # Load top candidates from crosscheck
        self.candidates = self.load_candidates()
        
    def load_ciphertext(self) -> str:
        """Load K4 ciphertext"""
        path = '../../02_DATA/ciphertext_97.txt'
        with open(path, 'r') as f:
            return f.read().strip()
    
    def load_candidates(self) -> List[Dict]:
        """Load top candidates from crosscheck summary"""
        candidates = []
        
        # Top candidates we know work well
        top_list = [
            ('MERIDIAN', 8, 34),
            ('MERIDIAN', 9, 34),
            ('MERIDIAN', 10, 34),
            ('MERIDIAN', 12, 34),
            ('MERIDIAN', 74, 34),
            ('MERIDIAN', 75, 34),
            ('MERIDIAN', 76, 34),
            ('MERIDIAN', 77, 34),
            ('MERIDIAN', 78, 34),
            ('COURSE', 8, 30),  # Expected from triage
            ('COURSE', 9, 30),
            ('BEARING', 8, 30),
            ('TRUE', 9, 26),
            ('TRUE', 10, 26),
            ('LINE', 8, 26),
        ]
        
        for token, start, gains in top_list:
            candidates.append({
                'token': token,
                'start': start,
                'gains': gains,
                'span': (start, start + len(token))
            })
        
        return candidates
    
    def compute_class(self, i: int) -> int:
        """Compute class for position"""
        return ((i % 2) * 3) + (i % 3)
    
    def get_slot_footprint(self, token: str, start: int, L: int = 11, phase: int = 0) -> Set[Tuple[int, int]]:
        """Get (class, slot) footprint for a placement"""
        footprint = set()
        
        for i, char in enumerate(token):
            pos = start + i
            if pos not in self.anchors:  # Only count non-anchor positions
                c = self.compute_class(pos)
                s = (pos - phase) % L
                footprint.add((c, s))
        
        return footprint
    
    def check_span_overlap(self, span1: Tuple[int, int], span2: Tuple[int, int]) -> bool:
        """Check if two spans overlap"""
        return not (span1[1] <= span2[0] or span1[0] >= span2[1])
    
    def greedy_combine(self, L: int = 11, phase: int = 0):
        """
        Greedy algorithm to combine non-conflicting placements
        """
        print("=== Multi-Anchor Synthesis (Greedy) ===")
        print(f"MASTER_SEED: {MASTER_SEED}")
        print(f"L={L}, phase={phase}\n")
        
        # Track selected candidates and their footprints
        selected = []
        used_slots = set()
        used_spans = []
        cumulative_gains = 0
        
        # Sort candidates by gains (descending)
        sorted_candidates = sorted(self.candidates, key=lambda x: -x['gains'])
        
        for cand in sorted_candidates:
            token = cand['token']
            start = cand['start']
            span = cand['span']
            gains = cand['gains']
            
            # Check span overlap
            overlap = False
            for used_span in used_spans:
                if self.check_span_overlap(span, used_span):
                    overlap = True
                    break
            
            if overlap:
                continue
            
            # Check slot conflicts
            footprint = self.get_slot_footprint(token, start, L, phase)
            conflicts = footprint & used_slots
            
            if conflicts:
                continue
            
            # No conflicts - add this candidate
            selected.append(cand)
            used_slots.update(footprint)
            used_spans.append(span)
            cumulative_gains += gains
            
            print(f"Added: {token}@{start} (gains={gains})")
            print(f"  Cumulative gains: {cumulative_gains}")
            print(f"  Slots used: {len(used_slots)}/66")
            
            # Stop if we've used most slots or have enough candidates
            if len(used_slots) > 50 or len(selected) >= 10:
                break
        
        print(f"\n=== Summary ===")
        print(f"Selected {len(selected)} candidates")
        print(f"Total gains: {cumulative_gains}")
        print(f"Slots used: {len(used_slots)}/66")
        
        # Build merged plaintext
        plaintext = ['?'] * 97
        
        # Place anchors
        for pos, letter in self.anchors.items():
            plaintext[pos] = letter
        
        # Place selected tokens
        indices_written = {}
        for cand in selected:
            token = cand['token']
            start = cand['start']
            for i, char in enumerate(token):
                pos = start + i
                if pos not in self.anchors:
                    plaintext[pos] = char
                    indices_written[pos] = f"{token}@{start}"
        
        pt_str = ''.join(plaintext)
        unknown_after = pt_str.count('?')
        
        print(f"\nDerived plaintext (first 74 chars):")
        print(pt_str[:74])
        print(f"\nUnknown before: 73")
        print(f"Unknown after: {unknown_after}")
        print(f"Total reduction: {73 - unknown_after}")
        
        # Save combo result
        result = {
            "mechanism": "F3-multi-anchor",
            "selected_candidates": [
                {"token": c['token'], "start": c['start'], "gains": c['gains']}
                for c in selected
            ],
            "cumulative_L11_unknown_after": unknown_after,
            "cumulative_gains": cumulative_gains,
            "slots_used": len(used_slots),
            "indices_written": indices_written,
            "plaintext_head": pt_str[:74],
            "plaintext_tail": pt_str[74:],
            "master_seed": MASTER_SEED
        }
        
        filename = "F3_combine/COMBO_RUN_01.json"
        os.makedirs("F3_combine", exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Save CSV companion
        csv_filename = "F3_combine/COMBO_RUN_01.csv"
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['token', 'start', 'gains', 'cumulative_gains'])
            cum = 0
            for c in selected:
                cum += c['gains']
                writer.writerow([c['token'], c['start'], c['gains'], cum])
        
        print(f"\nSaved to {filename} and {csv_filename}")
        
        return result


def main():
    """Main execution"""
    synthesizer = MultiAnchorSynthesis()
    result = synthesizer.greedy_combine()


if __name__ == "__main__":
    main()