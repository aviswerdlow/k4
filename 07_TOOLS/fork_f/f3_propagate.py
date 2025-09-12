#!/usr/bin/env python3
"""
Fork F v3: Deepening & Synthesis - Full Propagation
Turn top candidates into actual letters on the line
MASTER_SEED = 1337
"""

import os
import sys
import json
import csv
import random
import hashlib
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict

# Add path for imports
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'f1_anchor_search'))

from f1_anchor_search_v2 import AnchorSearcherV2, PlacementResult

MASTER_SEED = 1337
random.seed(MASTER_SEED)

@dataclass
class PropagatedPlacement:
    """Full propagation result with actual letters"""
    token: str
    start: int
    span: List[int]
    L11_gains: int
    L11_unknown_before: int
    L11_unknown_after: int
    L11_new_letters: Dict[int, str]  # position -> letter
    L11_new_slots: List[Tuple[int, int, int]]  # (class, slot, residue)
    L17_projection_confirmed: bool
    L17_conflicts: List[str]
    L17_new_letters_confirmed: int
    indices_written: List[int]
    sha_plaintext: str


class FullPropagator:
    """System for full letter propagation"""
    
    def __init__(self):
        self.searcher = AnchorSearcherV2()
        self.setup_baseline()
        
    def setup_baseline(self):
        """Setup baseline wheels and unknown positions"""
        # Load ciphertext
        data_path = os.path.join(script_dir, '../../02_DATA/ciphertext_97.txt')
        with open(data_path, 'r') as f:
            self.ciphertext = f.read().strip()
            
        # Known anchors
        self.anchors = self.searcher.anchors
        
        # Unknown positions
        self.unknowns = [i for i in range(97) if i not in self.anchors]
        
        # Build baseline wheels for L=11 and L=17
        self.baseline_L11 = self.searcher.build_baseline_wheels(L=11, phase=0)
        self.baseline_L17 = self.searcher.build_baseline_wheels(L=17, phase=0)
        
    def propagate_single(self, placement: PlacementResult) -> PropagatedPlacement:
        """
        Fully propagate a single placement to derive new letters
        """
        token = placement.token
        start = placement.start_index
        L = placement.L
        phase = placement.phase
        
        # Get span
        span = list(range(start, start + len(token)))
        
        # Build merged wheels (baseline + new constraints)
        merged_wheels = self.merge_wheels(self.baseline_L11, placement.forced_slots_added)
        
        # Derive plaintext from merged wheels
        plaintext = ['?'] * 97
        new_letters = {}
        indices_written = []
        
        # First, place known anchors
        for pos, letter in self.anchors.items():
            plaintext[pos] = letter
            
        # Place the candidate token
        for i, char in enumerate(token):
            pos = start + i
            if pos not in self.anchors:  # Don't overwrite anchors
                plaintext[pos] = char
                new_letters[pos] = char
                indices_written.append(pos)
        
        # Now propagate using merged wheels
        for pos in range(97):
            if plaintext[pos] == '?':  # Unknown position
                # Try to derive from wheels
                letter = self.derive_letter(pos, merged_wheels, L, phase)
                if letter:
                    plaintext[pos] = letter
                    new_letters[pos] = letter
                    indices_written.append(pos)
        
        # Count unknowns after propagation
        unknown_after = sum(1 for c in plaintext if c == '?')
        
        # Test L=17 projection
        l17_confirmed, l17_conflicts = self.test_l17_projection(token, start, new_letters)
        
        # Generate SHA of derived plaintext
        pt_str = ''.join(plaintext)
        sha_pt = hashlib.sha256(pt_str.encode()).hexdigest()[:16]
        
        return PropagatedPlacement(
            token=token,
            start=start,
            span=span,
            L11_gains=placement.gains,
            L11_unknown_before=len(self.unknowns),
            L11_unknown_after=unknown_after,
            L11_new_letters=new_letters,
            L11_new_slots=placement.forced_slots_added,
            L17_projection_confirmed=l17_confirmed,
            L17_conflicts=l17_conflicts,
            L17_new_letters_confirmed=len([p for p in new_letters if not l17_conflicts]),
            indices_written=indices_written,
            sha_plaintext=sha_pt
        )
    
    def merge_wheels(self, baseline: Dict, new_slots: List[Tuple]) -> Dict:
        """
        Merge baseline wheels with new slot constraints
        """
        merged = {}
        for c in range(6):
            merged[c] = {
                'family': baseline[c]['family'],
                'slots': baseline[c]['slots'].copy()
            }
        
        # Add new constraints
        for c, s, k in new_slots:
            merged[c]['slots'][s] = k
            
        return merged
    
    def derive_letter(self, pos: int, wheels: Dict, L: int, phase: int) -> Optional[str]:
        """
        Derive plaintext letter at position using wheels
        """
        c = self.searcher.compute_class(pos)
        s = (pos - phase) % L
        
        if s not in wheels[c]['slots']:
            return None
            
        k_val = wheels[c]['slots'][s]
        ct_char = self.ciphertext[pos]
        c_val = ord(ct_char) - ord('A')
        
        family = wheels[c]['family']
        
        if family == 'vigenere':
            p_val = (c_val - k_val) % 26
        elif family == 'beaufort':
            p_val = (k_val - c_val) % 26
        elif family == 'variant-beaufort':
            p_val = (k_val - c_val) % 26  # Same as beaufort
        else:
            return None
            
        return chr(p_val + ord('A'))
    
    def test_l17_projection(self, token: str, start: int, 
                           new_letters: Dict[int, str]) -> Tuple[bool, List[str]]:
        """
        Test if placement is compatible when projected to L=17
        """
        conflicts = []
        
        # Try different phases with L=17
        for phase in range(17):
            result = self.searcher.test_placement(token, start, L=17, phase=phase)
            if not result.rejected:
                # Found compatible configuration
                return True, []
        
        # If we get here, all phases rejected
        return False, ['all_phases_rejected']
    
    def select_top_candidates(self, n: int = 50) -> List[Dict]:
        """
        Select top N candidates from triage results
        """
        # Load the crosscheck summary
        summary_path = os.path.join(script_dir, 'f1_anchor_search/crosscheck/CROSSCHECK_SUMMARY.csv')
        
        candidates = []
        seen_spans = set()
        
        with open(summary_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                token = row['token']
                start = int(row['start'])
                gains = int(row['L11_gains'])
                
                # Check non-overlapping spans
                span = (start, start + len(token))
                overlap = False
                for existing_span in seen_spans:
                    if not (span[1] <= existing_span[0] or span[0] >= existing_span[1]):
                        overlap = True
                        break
                
                if not overlap and gains >= 3:
                    candidates.append({
                        'token': token,
                        'start': start,
                        'gains': gains,
                        'L': 11,
                        'phase': 0
                    })
                    seen_spans.add(span)
                    
                    if len(candidates) >= n:
                        break
        
        return candidates
    
    def sanity_ablation(self, token: str, start: int) -> Dict:
        """
        Test with random token of same length for sanity check
        """
        # Generate random token with same letter distribution
        letters = list(token)
        random.shuffle(letters)
        random_token = ''.join(letters)
        
        # Test placement
        result = self.searcher.test_placement(random_token, start, L=11, phase=0)
        
        return {
            'original_token': token,
            'random_token': random_token,
            'start': start,
            'random_gains': result.gains if not result.rejected else 0,
            'random_rejected': result.rejected,
            'reject_reasons': result.reject_reasons[:3] if result.rejected else []
        }
    
    def run_single_propagations(self):
        """
        Run full propagation on top candidates
        """
        print("=== F3 Single Propagations ===")
        print(f"MASTER_SEED: {MASTER_SEED}\n")
        
        # Select top candidates
        candidates = self.select_top_candidates(50)
        print(f"Selected {len(candidates)} non-overlapping candidates\n")
        
        results = []
        
        for i, cand in enumerate(candidates[:20], 1):  # Start with top 20
            print(f"Processing {i}/{min(20, len(candidates))}: {cand['token']}@{cand['start']}...")
            
            # Get placement result
            placement = self.searcher.test_placement(
                cand['token'], cand['start'], cand['L'], cand['phase']
            )
            
            if not placement.rejected:
                # Full propagation
                propagated = self.propagate_single(placement)
                results.append(propagated)
                
                # Save card
                self.save_propagation_card(propagated, i)
                
                print(f"  ✓ Gains: {propagated.L11_gains}, "
                      f"New letters: {len(propagated.L11_new_letters)}, "
                      f"L17 OK: {propagated.L17_projection_confirmed}")
                
                # Sanity ablation for top 5
                if i <= 5:
                    ablation = self.sanity_ablation(cand['token'], cand['start'])
                    print(f"  Ablation: random gains = {ablation['random_gains']} "
                          f"(original = {propagated.L11_gains})")
        
        return results
    
    def save_propagation_card(self, propagated: PropagatedPlacement, rank: int):
        """
        Save detailed propagation card
        """
        card = {
            "mechanism": "F3-propagation",
            "rank": rank,
            "token": propagated.token,
            "start": propagated.start,
            "span": propagated.span,
            "L11_gains": propagated.L11_gains,
            "L11_unknown_before": propagated.L11_unknown_before,
            "L11_unknown_after": propagated.L11_unknown_after,
            "L11_new_letters": propagated.L11_new_letters,
            "L11_new_slots": [
                {"class": c, "slot": s, "residue": k}
                for c, s, k in propagated.L11_new_slots
            ],
            "L17_projection_confirmed": propagated.L17_projection_confirmed,
            "L17_conflicts": propagated.L17_conflicts,
            "L17_new_letters_confirmed": propagated.L17_new_letters_confirmed,
            "indices_written": propagated.indices_written,
            "sha_plaintext": propagated.sha_plaintext,
            "master_seed": MASTER_SEED
        }
        
        filename = os.path.join(script_dir, f"F3_cards/single/{propagated.token}_{propagated.start:02d}.json")
        with open(filename, 'w') as f:
            json.dump(card, f, indent=2)


def main():
    """Main execution"""
    propagator = FullPropagator()
    results = propagator.run_single_propagations()
    
    print(f"\n=== Summary ===")
    print(f"Total propagated: {len(results)}")
    
    # Show top 5 by new letters written
    by_letters = sorted(results, key=lambda r: -len(r.L11_new_letters))[:5]
    
    print("\nTop 5 by letters written:")
    for r in by_letters:
        print(f"  {r.token}@{r.start}: {len(r.L11_new_letters)} letters, "
              f"L17 OK: {r.L17_projection_confirmed}")
    
    print("\nCards saved to F3_cards/single/")


if __name__ == "__main__":
    main()