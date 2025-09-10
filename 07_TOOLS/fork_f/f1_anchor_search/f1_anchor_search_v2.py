#!/usr/bin/env python3
"""
F1 - Systematic Anchor Search v2 (FIXED)
Proper conflict validation and wheel consistency checking
MASTER_SEED = 1337
"""

import os
import sys
import csv
import json
import yaml
import hashlib
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict

MASTER_SEED = 1337

@dataclass
class PlacementResult:
    """Result of testing a token placement"""
    token: str
    start_index: int
    family_vector: str
    L: int
    phase: int
    unknown_before: int
    unknown_after: int
    gains: int
    forced_slots_added: List[Tuple[int, int, int]]  # (class, slot, residue)
    rejected: bool
    reject_reasons: List[str]
    anchors_preserved: bool
    sha_ct: str
    sha_forced_wheels_before: str
    sha_forced_wheels_after: str


class AnchorSearcherV2:
    """Fixed anchor search with proper validation"""
    
    def __init__(self):
        self.seed = MASTER_SEED
        self.load_k4_data()
        self.load_candidates()
        self.setup_baseline_families()
        
    def load_k4_data(self):
        """Load K4 ciphertext and known anchors"""
        with open('../../../02_DATA/ciphertext_97.txt', 'r') as f:
            self.ciphertext = f.read().strip()
            self.ct_sha = hashlib.sha256(self.ciphertext.encode()).hexdigest()
        
        # Known anchors (frozen)
        self.anchors = {
            21: 'E', 22: 'A', 23: 'S', 24: 'T',  # EAST
            25: 'N', 26: 'O', 27: 'R', 28: 'T',  # NORTHEAST start
            29: 'H', 30: 'E', 31: 'A', 32: 'S', 33: 'T',  # NORTHEAST end
            63: 'B', 64: 'E', 65: 'R', 66: 'L', 67: 'I', 68: 'N',  # BERLIN
            69: 'C', 70: 'L', 71: 'O', 72: 'C', 73: 'K'  # CLOCK
        }
        
        # Unknown positions
        self.unknowns = [i for i in range(97) if i not in self.anchors]
        
    def load_candidates(self):
        """Load candidate tokens from YAML"""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates_path = os.path.join(script_dir, 'candidates.yaml')
        
        with open(candidates_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.candidates = []
        for category_name, category_data in data.items():
            for token in category_data['tokens']:
                # Ensure token is a string and handle YAML boolean conversion
                if isinstance(token, bool):
                    # YAML converts TRUE/FALSE to booleans
                    token_str = "TRUE" if token else "FALSE"
                else:
                    token_str = str(token).upper()  # Ensure all tokens are uppercase
                
                if category_data['min_len'] <= len(token_str) <= category_data['max_len']:
                    self.candidates.append({
                        'token': token_str,
                        'category': category_name
                    })
        
        print(f"Loaded {len(self.candidates)} candidate tokens")
    
    def setup_baseline_families(self):
        """Setup frozen family assignments per class"""
        # Baseline: V,V,B,V,B,V
        self.family_by_class = {
            0: 'beaufort',     # Class 0: B
            1: 'vigenere',     # Class 1: V  
            2: 'beaufort',     # Class 2: B
            3: 'vigenere',     # Class 3: V
            4: 'beaufort',     # Class 4: B
            5: 'vigenere'      # Class 5: V
        }
    
    def compute_class(self, i: int) -> int:
        """Compute class for position i (frozen formula)"""
        return ((i % 2) * 3) + (i % 3)
    
    def compute_residue(self, c_val: int, p_val: int, family: str) -> int:
        """Compute required key residue for given cipher/plain pair"""
        if family == 'vigenere':
            return (c_val - p_val) % 26
        elif family == 'beaufort':
            return (p_val - c_val) % 26
        elif family == 'variant-beaufort':
            return (c_val + p_val) % 26
        else:
            raise ValueError(f"Unknown family: {family}")
    
    def build_baseline_wheels(self, L: int, phase: int) -> Dict:
        """Build baseline wheel constraints from known anchors"""
        wheels = {}
        
        # Initialize empty wheels for each class
        for c in range(6):
            wheels[c] = {
                'family': self.family_by_class[c],
                'slots': {}  # slot -> residue mapping
            }
        
        # Add constraints from known anchors
        for pos, pt_char in self.anchors.items():
            c = self.compute_class(pos)
            s = (pos - phase) % L
            
            ct_char = self.ciphertext[pos]
            c_val = ord(ct_char) - ord('A')
            p_val = ord(pt_char) - ord('A')
            
            k_req = self.compute_residue(c_val, p_val, wheels[c]['family'])
            
            # Check for Option-A violation at anchors
            if wheels[c]['family'] in ['vigenere', 'variant-beaufort'] and k_req == 0:
                # This configuration violates Option-A
                return None
            
            # Check for conflicts
            if s in wheels[c]['slots']:
                if wheels[c]['slots'][s] != k_req:
                    # Conflict in baseline - this L/phase is invalid
                    return None
            else:
                wheels[c]['slots'][s] = k_req
        
        return wheels
    
    def test_placement(self, token: str, start_idx: int, L: int, phase: int) -> PlacementResult:
        """Test a specific token placement with full validation"""
        token_len = len(token)
        end_idx = start_idx + token_len - 1
        
        # Check bounds
        if end_idx >= 97:
            return PlacementResult(
                token=token, start_index=start_idx,
                family_vector=','.join(self.family_by_class[c] for c in range(6)),
                L=L, phase=phase,
                unknown_before=len(self.unknowns),
                unknown_after=len(self.unknowns),
                gains=0,
                forced_slots_added=[],
                rejected=True,
                reject_reasons=['out_of_bounds'],
                anchors_preserved=True,
                sha_ct=self.ct_sha[:16],
                sha_forced_wheels_before='',
                sha_forced_wheels_after=''
            )
        
        # Build baseline wheels
        baseline_wheels = self.build_baseline_wheels(L, phase)
        if baseline_wheels is None:
            return PlacementResult(
                token=token, start_index=start_idx,
                family_vector=','.join(self.family_by_class[c][0].upper() for c in range(6)),
                L=L, phase=phase,
                unknown_before=len(self.unknowns),
                unknown_after=len(self.unknowns),
                gains=0,
                forced_slots_added=[],
                rejected=True,
                reject_reasons=['baseline_invalid'],
                anchors_preserved=True,
                sha_ct=self.ct_sha[:16],
                sha_forced_wheels_before='',
                sha_forced_wheels_after=''
            )
        
        # Hash baseline
        baseline_hash = hashlib.sha256(
            json.dumps(baseline_wheels, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        # Test the placement
        reject_reasons = []
        new_constraints = {}  # (class, slot) -> residue
        
        for i in range(token_len):
            pos = start_idx + i
            pt_char = token[i]
            
            # Check anchor protection
            if pos in self.anchors:
                if self.anchors[pos] != pt_char:
                    reject_reasons.append(f'anchor_mismatch@{pos}')
                    continue
                else:
                    # Token matches anchor - no new constraint
                    continue
            
            # Compute requirements
            c = self.compute_class(pos)
            s = (pos - phase) % L
            
            ct_char = self.ciphertext[pos]
            c_val = ord(ct_char) - ord('A')
            p_val = ord(pt_char) - ord('A')
            
            k_req = self.compute_residue(c_val, p_val, baseline_wheels[c]['family'])
            
            # Check Option-A for non-anchor positions
            if baseline_wheels[c]['family'] in ['vigenere', 'variant-beaufort'] and k_req == 0:
                reject_reasons.append(f'optionA_violation@{pos}')
                continue
            
            # Check consistency with baseline
            if s in baseline_wheels[c]['slots']:
                if baseline_wheels[c]['slots'][s] != k_req:
                    reject_reasons.append(f'slot_conflict(c={c},s={s})')
                    continue
            
            # Check self-consistency within this placement
            key = (c, s)
            if key in new_constraints:
                if new_constraints[key] != k_req:
                    reject_reasons.append(f'self_conflict(c={c},s={s})')
                    continue
            else:
                new_constraints[key] = k_req
        
        # If rejected, return early
        if reject_reasons:
            return PlacementResult(
                token=token, start_index=start_idx,
                family_vector=','.join(self.family_by_class[c][0].upper() for c in range(6)),
                L=L, phase=phase,
                unknown_before=len(self.unknowns),
                unknown_after=len(self.unknowns),
                gains=0,
                forced_slots_added=[],
                rejected=True,
                reject_reasons=reject_reasons,
                anchors_preserved=True,
                sha_ct=self.ct_sha[:16],
                sha_forced_wheels_before=baseline_hash,
                sha_forced_wheels_after=baseline_hash
            )
        
        # Build updated wheels
        updated_wheels = {}
        for c in range(6):
            updated_wheels[c] = {
                'family': baseline_wheels[c]['family'],
                'slots': baseline_wheels[c]['slots'].copy()
            }
        
        forced_slots_added = []
        for (c, s), k_val in new_constraints.items():
            updated_wheels[c]['slots'][s] = k_val
            forced_slots_added.append((c, s, k_val))
        
        # Hash updated wheels
        updated_hash = hashlib.sha256(
            json.dumps(updated_wheels, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        # Compute propagation
        unknown_after = 0
        for pos in range(97):
            if pos in self.anchors:
                continue
            
            c = self.compute_class(pos)
            s = (pos - phase) % L
            
            if s not in updated_wheels[c]['slots']:
                unknown_after += 1
        
        gains = len(self.unknowns) - unknown_after
        
        return PlacementResult(
            token=token, start_index=start_idx,
            family_vector=','.join(self.family_by_class[c][0].upper() for c in range(6)),
            L=L, phase=phase,
            unknown_before=len(self.unknowns),
            unknown_after=unknown_after,
            gains=gains,
            forced_slots_added=forced_slots_added,
            rejected=False,
            reject_reasons=[],
            anchors_preserved=True,
            sha_ct=self.ct_sha[:16],
            sha_forced_wheels_before=baseline_hash,
            sha_forced_wheels_after=updated_hash
        )
    
    def run_search(self) -> List[PlacementResult]:
        """Run complete anchor search with proper validation"""
        results = []
        periods = [11, 15, 17]
        
        print(f"\n=== Starting Systematic Anchor Search v2 ===")
        print(f"Candidates: {len(self.candidates)}")
        print(f"Periods: {periods}")
        print(f"Unknown positions: {len(self.unknowns)}\n")
        
        for candidate_data in self.candidates:
            token = candidate_data['token']
            
            for L in periods:
                for phase in range(L):
                    # Test all valid starting positions
                    for start_idx in range(97 - len(token) + 1):
                        result = self.test_placement(token, start_idx, L, phase)
                        results.append(result)
                        
                        # Report significant findings
                        if not result.rejected and result.gains > 0:
                            print(f"✓ {token}@{start_idx} L={L} p={phase}: "
                                  f"gains {result.gains} positions")
                        elif not result.rejected and result.gains == 0:
                            # Valid but no gain (matches existing constraints)
                            pass
        
        return results
    
    def save_results(self, results: List[PlacementResult], output_dir: str = 'results'):
        """Save results with proper formatting"""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f'{output_dir}/cards', exist_ok=True)
        
        # Filter to meaningful results
        accepted = [r for r in results if not r.rejected]
        with_gains = [r for r in accepted if r.gains > 0]
        
        # Save CSV summary
        with open(f'{output_dir}/RESULTS.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['token', 'start', 'L', 'phase', 'gains', 'status', 'reject_reasons'])
            
            for r in results[:1000]:  # Limit output
                status = 'accepted' if not r.rejected else 'rejected'
                reasons = '|'.join(r.reject_reasons) if r.reject_reasons else 'none'
                writer.writerow([
                    r.token, r.start_index, r.L, r.phase,
                    r.gains, status, reasons
                ])
        
        # Save cards for accepted placements
        for i, r in enumerate(accepted[:100]):
            card = {
                "mechanism": "F1-anchor-search",
                "token": r.token,
                "start_index": r.start_index,
                "family_vector": r.family_vector,
                "L": r.L,
                "phase": r.phase,
                "unknown_before": r.unknown_before,
                "unknown_after": r.unknown_after,
                "gains": r.gains,
                "forced_slots_added": [
                    {"class": c, "slot": s, "residue": k}
                    for c, s, k in r.forced_slots_added
                ],
                "rejected": r.rejected,
                "reject_reasons": r.reject_reasons,
                "anchors_preserved": r.anchors_preserved,
                "sha_ct": r.sha_ct,
                "sha_forced_wheels_before": r.sha_forced_wheels_before,
                "sha_forced_wheels_after": r.sha_forced_wheels_after
            }
            
            with open(f'{output_dir}/cards/result_{i:04d}.json', 'w') as f:
                json.dump(card, f, indent=2)
        
        # Save summary
        with open(f'{output_dir}/SUMMARY.md', 'w') as f:
            f.write("# F1 Anchor Search Results (v2 - Fixed)\n\n")
            f.write(f"Total placements tested: {len(results)}\n")
            f.write(f"Accepted (no conflicts): {len(accepted)}\n")
            f.write(f"With gains > 0: {len(with_gains)}\n\n")
            
            if with_gains:
                f.write("## Top 10 by Gains\n\n")
                f.write("| Token | Start | L | Phase | Gains |\n")
                f.write("|-------|-------|---|-------|-------|\n")
                
                top_10 = sorted(with_gains, key=lambda r: -r.gains)[:10]
                for r in top_10:
                    f.write(f"| {r.token} | {r.start_index} | {r.L} | {r.phase} | {r.gains} |\n")
            else:
                f.write("## No Placements with Gains > 0\n\n")
                f.write("All tested placements either conflicted with existing constraints ")
                f.write("or provided no additional information.\n")
        
        return len(accepted), len(with_gains)


def main():
    """Main execution"""
    print("=== F1: Systematic Anchor Search v2 (FIXED) ===")
    print(f"MASTER_SEED: {MASTER_SEED}\n")
    
    searcher = AnchorSearcherV2()
    
    # Run search
    results = searcher.run_search()
    
    # Save results
    accepted_count, gains_count = searcher.save_results(results)
    
    print(f"\n=== Summary ===")
    print(f"Total placements tested: {len(results)}")
    print(f"Accepted (no conflicts): {accepted_count}")
    print(f"With gains > 0: {gains_count}")
    
    if gains_count > 0:
        print("\n✓ Found valid placements with gains!")
    else:
        print("\n✗ No placements provided additional constraints (clean negative)")
    
    print("\nResults saved to results/")


if __name__ == "__main__":
    main()