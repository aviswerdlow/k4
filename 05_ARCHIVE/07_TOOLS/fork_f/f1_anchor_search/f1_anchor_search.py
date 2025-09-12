#!/usr/bin/env python3
"""
F1 - Systematic Anchor Search
Find additional cribs that increase propagation under cipher families
MASTER_SEED = 1337
"""

import os
import sys
import csv
import json
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

sys.path.append('../../..')

MASTER_SEED = 1337

@dataclass
class AnchorCandidate:
    """Represents a potential anchor/crib"""
    token: str
    start_idx: int
    end_idx: int
    mechanism: str
    period: int
    phase: int
    family: str
    propagation_gain: int
    wheel_slots_forced: int
    conflicts: int


class AnchorSearcher:
    """Systematic search for new anchors/cribs"""
    
    def __init__(self):
        self.seed = MASTER_SEED
        self.load_k4_data()
        self.load_candidate_lists()
        
    def load_k4_data(self):
        """Load K4 ciphertext and known anchors"""
        with open('../../../02_DATA/ciphertext_97.txt', 'r') as f:
            self.ciphertext = f.read().strip()
        
        # Known anchors
        self.known_anchors = {
            21: 'E', 22: 'A', 23: 'S', 24: 'T',  # EAST
            25: 'N', 26: 'O', 27: 'R', 28: 'T',  # NORTHEAST start
            29: 'H', 30: 'E', 31: 'A', 32: 'S', 33: 'T',  # NORTHEAST end
            63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',  # BERLIN
            69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'  # CLOCK
        }
        
        self.anchor_ranges = [
            (21, 24), (25, 33), (63, 68), (69, 73)
        ]
        
        # Unknown positions
        self.unknowns = [i for i in range(97) if i not in self.known_anchors]
        
    def load_candidate_lists(self):
        """Load candidate token lists"""
        self.candidate_lists = {}
        
        list_files = {
            'A_survey': 'A_survey.lst',
            'B_context': 'B_context.lst', 
            'C_function': 'C_function.lst',
            'D_numbers': 'D_numbers.lst'
        }
        
        for list_name, filename in list_files.items():
            filepath = filename
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    tokens = [line.strip().upper() for line in f if line.strip()]
                    # Filter to 3-8 characters
                    tokens = [t for t in tokens if 3 <= len(t) <= 8]
                    self.candidate_lists[list_name] = tokens
                    print(f"Loaded {len(tokens)} tokens from {list_name}")
            else:
                self.candidate_lists[list_name] = []
                print(f"Warning: {filepath} not found")
        
        # Calculate SHA256 for audit
        self.calculate_list_hashes()
    
    def calculate_list_hashes(self):
        """Calculate SHA256 for each list"""
        self.list_hashes = {}
        for list_name, tokens in self.candidate_lists.items():
            content = '\n'.join(tokens)
            sha = hashlib.sha256(content.encode()).hexdigest()
            self.list_hashes[list_name] = sha
        
        # Save hashes
        with open('POLICIES.SHA256', 'w') as f:
            json.dump(self.list_hashes, f, indent=2)
    
    def check_overlap(self, start: int, end: int) -> bool:
        """Check if placement overlaps with known anchors"""
        for anchor_start, anchor_end in self.anchor_ranges:
            if not (end < anchor_start or start > anchor_end):
                return True  # Overlaps
        return False
    
    def compute_class(self, i: int) -> int:
        """Standard class computation"""
        return ((i % 2) * 3) + (i % 3)
    
    def test_polyalphabetic(self, token: str, start_idx: int, 
                           family: str, period: int, phase: int) -> Optional[AnchorCandidate]:
        """Test polyalphabetic cipher feasibility"""
        end_idx = start_idx + len(token) - 1
        
        # Build partial wheels from known anchors + candidate
        wheels = self.build_wheels(family, period, phase, token, start_idx)
        
        if wheels is None:
            return None  # Conflicts detected
        
        # Calculate propagation
        propagation = self.calculate_propagation(wheels, period)
        
        if propagation['conflicts'] > 0:
            return None
        
        if propagation['gain'] > 0:
            return AnchorCandidate(
                token=token,
                start_idx=start_idx,
                end_idx=end_idx,
                mechanism=f"polyalpha_{family}_L{period}_p{phase}",
                period=period,
                phase=phase,
                family=family,
                propagation_gain=propagation['gain'],
                wheel_slots_forced=propagation['slots_forced'],
                conflicts=0
            )
        
        return None
    
    def build_wheels(self, family: str, period: int, phase: int, 
                     token: str, start_idx: int) -> Optional[Dict]:
        """Build wheels with anchors + candidate token"""
        wheels = {}
        
        # Initialize wheels
        for c in range(6):
            wheels[c] = {
                'family': family,
                'residues': [None] * period
            }
        
        # Fill from known anchors
        for pos, plain_char in self.known_anchors.items():
            c = self.compute_class(pos)
            s = (pos + phase) % period
            
            c_char = self.ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(plain_char) - ord('A')
            
            if family == 'vigenere':
                k_val = (c_val - p_val) % 26
            elif family == 'beaufort':
                k_val = (p_val + c_val) % 26
            else:  # variant-beaufort
                k_val = (p_val - c_val) % 26
            
            # Check for conflict
            if wheels[c]['residues'][s] is not None:
                if wheels[c]['residues'][s] != k_val:
                    return None  # Conflict
            wheels[c]['residues'][s] = k_val
        
        # Add candidate token
        for i, char in enumerate(token):
            pos = start_idx + i
            c = self.compute_class(pos)
            s = (pos + phase) % period
            
            c_char = self.ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(char) - ord('A')
            
            if family == 'vigenere':
                k_val = (c_val - p_val) % 26
            elif family == 'beaufort':
                k_val = (p_val + c_val) % 26
            else:  # variant-beaufort
                k_val = (p_val - c_val) % 26
            
            # Check for conflict
            if wheels[c]['residues'][s] is not None:
                if wheels[c]['residues'][s] != k_val:
                    return None  # Conflict
            wheels[c]['residues'][s] = k_val
        
        return wheels
    
    def calculate_propagation(self, wheels: Dict, period: int) -> Dict:
        """Calculate how many positions can be determined"""
        determined = set()
        conflicts = 0
        
        # Check each unknown position
        for pos in self.unknowns:
            c = self.compute_class(pos)
            s = pos % period
            
            if c in wheels and wheels[c]['residues'][s] is not None:
                # This position can be determined
                determined.add(pos)
        
        # Count forced slots
        slots_forced = sum(
            1 for c in wheels
            for r in wheels[c]['residues']
            if r is not None
        )
        
        # Gain is positions beyond the 24 known anchors
        baseline_determined = len([p for p in self.known_anchors if p in range(97)])
        gain = len(determined) - baseline_determined
        
        return {
            'gain': max(0, gain),
            'slots_forced': slots_forced,
            'conflicts': conflicts
        }
    
    def slide_and_test(self, token: str, list_name: str) -> List[AnchorCandidate]:
        """Slide token across all valid positions"""
        candidates = []
        token_len = len(token)
        
        # Test all valid starting positions
        for start_idx in range(97 - token_len + 1):
            end_idx = start_idx + token_len - 1
            
            # Skip if overlaps with known anchors
            if self.check_overlap(start_idx, end_idx):
                continue
            
            # Test polyalphabetic mechanisms
            for family in ['vigenere', 'beaufort', 'variant-beaufort']:
                for period in [11, 15, 17]:
                    for phase in range(period):
                        result = self.test_polyalphabetic(
                            token, start_idx, family, period, phase
                        )
                        if result:
                            candidates.append(result)
        
        return candidates
    
    def run_full_scan(self) -> List[AnchorCandidate]:
        """Run complete anchor search"""
        all_candidates = []
        
        print("\n=== Starting Systematic Anchor Search ===")
        print(f"Unknown positions: {len(self.unknowns)}")
        
        for list_name, tokens in self.candidate_lists.items():
            print(f"\nScanning {list_name} ({len(tokens)} tokens)...")
            
            for token in tokens:
                if len(token) < 3 or len(token) > 8:
                    continue
                
                candidates = self.slide_and_test(token, list_name)
                
                if candidates:
                    print(f"  {token}: {len(candidates)} feasible placements")
                    all_candidates.extend(candidates)
                    
                    # Check for high-value hits
                    best = max(candidates, key=lambda c: c.propagation_gain)
                    if best.propagation_gain >= 3:
                        print(f"  🎯 HIGH VALUE: {token} gains {best.propagation_gain} positions!")
        
        return all_candidates
    
    def save_results(self, candidates: List[AnchorCandidate], output_dir: str = 'output'):
        """Save results to CSV and JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Sort by propagation gain
        candidates.sort(key=lambda c: (-c.propagation_gain, c.period, c.phase))
        
        # Save to CSV
        with open(f'{output_dir}/F1_anchor_hits.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'token', 'start', 'end', 'mechanism_id', 
                'period', 'phase', 'propagation_gain', 
                'wheel_slots_forced', 'conflicts'
            ])
            
            for c in candidates:
                writer.writerow([
                    c.token, c.start_idx, c.end_idx, c.mechanism,
                    c.period, c.phase, c.propagation_gain,
                    c.wheel_slots_forced, c.conflicts
                ])
        
        # Save top 10
        top_10 = candidates[:10] if len(candidates) >= 10 else candidates
        
        with open(f'{output_dir}/F1_top10.json', 'w') as f:
            json.dump([
                {
                    'token': c.token,
                    'position': f"{c.start_idx}-{c.end_idx}",
                    'mechanism': c.mechanism,
                    'gain': c.propagation_gain,
                    'slots_forced': c.wheel_slots_forced
                }
                for c in top_10
            ], f, indent=2)
        
        # Generate result cards
        for i, c in enumerate(candidates[:20]):  # First 20 only
            card = {
                "mechanism": f"F1_anchor/{c.mechanism}",
                "constraints_in": {
                    "anchors": ["EAST@21-24","NORTHEAST@25-33","BERLIN@63-68","CLOCK@69-73"],
                    "extras": [f"{c.token}@{c.start_idx}-{c.end_idx}"]
                },
                "unknowns_before": len(self.unknowns),
                "unknowns_after": len(self.unknowns) - c.propagation_gain,
                "anchors_preserved": True,
                "new_positions_determined": [],  # Would need full calculation
                "parameters": {
                    "family": c.family,
                    "period": c.period,
                    "phase": c.phase,
                    "note": f"deterministic, seed={MASTER_SEED}"
                },
                "receipts": {
                    "ct_sha256": hashlib.sha256(self.ciphertext.encode()).hexdigest()[:16],
                    "policies_sha256": self.list_hashes.get('A_survey', '')[:16],
                    "run_sha256": hashlib.sha256(f"{c.token}{c.start_idx}".encode()).hexdigest()[:16]
                }
            }
            
            with open(f'{output_dir}/card_F1_{i:03d}.json', 'w') as f:
                json.dump(card, f, indent=2)
        
        return len(candidates)


def main():
    """Main execution"""
    print("=== F1: Systematic Anchor Search ===")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    
    searcher = AnchorSearcher()
    
    # Run full scan
    candidates = searcher.run_full_scan()
    
    print(f"\n=== Results ===")
    print(f"Total feasible placements: {len(candidates)}")
    
    if candidates:
        # Save results
        count = searcher.save_results(candidates)
        
        # Report top hits
        top_10 = sorted(candidates, key=lambda c: (-c.propagation_gain, c.period))[:10]
        
        print("\nTop 10 by propagation gain:")
        for i, c in enumerate(top_10, 1):
            print(f"{i:2}. {c.token:10} @ {c.start_idx:2}-{c.end_idx:2} "
                  f"gains {c.propagation_gain} positions "
                  f"({c.family} L={c.period} p={c.phase})")
        
        # Check for breakthrough
        if any(c.propagation_gain >= 3 for c in candidates):
            print("\n🎯 BREAKTHROUGH: Found candidate(s) with gain >= 3!")
            print("Promote to F6 confirmation immediately!")
    else:
        print("No feasible anchor candidates found (clean negative)")
    
    print("\nResults saved to output/")


if __name__ == "__main__":
    main()