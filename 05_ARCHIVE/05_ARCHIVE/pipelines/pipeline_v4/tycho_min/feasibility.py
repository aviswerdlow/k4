#!/usr/bin/env python3
"""
Minimal Tycho solver for Option-A feasibility testing.
Tests if plaintext can encrypt to K4 ciphertext under given route and schedule.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# K4 ciphertext (97 chars)
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions
ANCHOR_INDICES = list(range(21, 25)) + list(range(25, 34)) + list(range(63, 74))


class MinimalTychoSolver:
    """Minimal Option-A key solver for feasibility testing."""
    
    def __init__(self):
        self.k4_ct = K4_CT
        
    def load_route(self, route_file: str) -> Dict:
        """Load route permutation from JSON file."""
        with open(route_file, 'r') as f:
            route_data = json.load(f)
        
        # The permutation is stored in 'order_abs_dst' for NA indices only
        if 'order_abs_dst' not in route_data or 'NA' not in route_data:
            raise ValueError(f"Route file missing required fields")
        
        # Build full 97-element permutation
        # order_abs_dst maps NA positions to their destinations
        full_perm = list(range(97))  # Start with identity
        
        na_indices = route_data['NA']  # Which indices are NA
        na_order = route_data['order_abs_dst']  # Where NA indices go
        
        # For each NA index, set where it goes
        for i in range(len(na_order)):
            src_idx = na_indices[i]  # Source position
            dst_idx = na_order[i]     # Destination position  
            full_perm[src_idx] = dst_idx
        
        route_data['permutation'] = full_perm
        
        return route_data
    
    def class_id_c6a(self, i: int) -> int:
        """Compute class ID for index i using c6a classing."""
        return ((i % 2) * 3) + (i % 3)
    
    def compute_ordinal(self, i: int, class_assignments: List[int]) -> int:
        """Compute ordinal of index i within its class."""
        k = class_assignments[i]
        ordinal = sum(1 for j in range(i) if class_assignments[j] == k)
        return ordinal
    
    def compute_residue_address(self, i: int, class_assignments: List[int], 
                               periods: List[int], phases: List[int]) -> int:
        """Compute residue address for index i."""
        k = class_assignments[i]
        ordinal = self.compute_ordinal(i, class_assignments)
        r = (ordinal + phases[k]) % periods[k]
        return r
    
    def solve_key(self, pt_char: str, ct_char: str, family: str) -> int:
        """Solve for key value given PT, CT, and cipher family."""
        p = ord(pt_char) - ord('A')
        c = ord(ct_char) - ord('A')
        
        if family == 'vigenere':
            # C = P + K => K = C - P (mod 26)
            k = (c - p) % 26
        elif family == 'variant_beaufort':
            # C = P - K => K = P - C (mod 26)
            k = (p - c) % 26
        elif family == 'beaufort':
            # P = K - C => K = P + C (mod 26)
            k = (p + c) % 26
        else:
            raise ValueError(f"Unknown family: {family}")
        
        return k
    
    def encrypt_char(self, pt_char: str, key_val: int, family: str) -> str:
        """Encrypt a single character."""
        p = ord(pt_char) - ord('A')
        
        if family == 'vigenere':
            c = (p + key_val) % 26
        elif family == 'variant_beaufort':
            c = (p - key_val) % 26
        elif family == 'beaufort':
            c = (key_val - p) % 26
        else:
            raise ValueError(f"Unknown family: {family}")
        
        return chr(c + ord('A'))
    
    def apply_inverse_permutation(self, text: str, permutation: List[int]) -> str:
        """Apply inverse permutation to text."""
        # Build inverse
        inverse = [0] * len(permutation)
        for i, p in enumerate(permutation):
            if p < len(inverse):
                inverse[p] = i
        
        # Apply to text
        result = [''] * len(text)
        for i, char in enumerate(text):
            if i < len(inverse):
                result[inverse[i]] = char
        
        return ''.join(result)
    
    def apply_permutation(self, text: str, permutation: List[int]) -> str:
        """Apply permutation to text."""
        result = [''] * len(text)
        for i, p in enumerate(permutation):
            if i < len(text) and p < len(result):
                result[p] = text[i]
        
        return ''.join(result)
    
    def test_feasibility(self, plaintext: str, route_file: str,
                        families: List[str], periods: List[int], 
                        phases: List[int]) -> Dict:
        """Test if plaintext can encrypt to K4 CT with given route and schedule."""
        
        # Load route
        route_data = self.load_route(route_file)
        permutation = route_data['permutation']
        route_id = Path(route_file).stem
        
        print(f"\nTesting feasibility with route: {route_id}")
        print(f"Families: {families}")
        print(f"Periods: {periods}")
        print(f"Phases: {phases}")
        
        # Verify lengths
        if len(plaintext) != 97 or len(self.k4_ct) != 97:
            return {
                "feasible": False,
                "reason": "Length mismatch"
            }
        
        # Compute class assignments for all indices
        class_assignments = [self.class_id_c6a(i) for i in range(97)]
        
        # Apply inverse permutation to CT to get CT_pre
        ct_pre = self.apply_inverse_permutation(self.k4_ct, permutation)
        
        # Initialize key tables (one per class)
        key_tables = {k: {} for k in range(6)}
        
        # First pass: solve keys at anchor positions
        anchor_violations = []
        
        for i in ANCHOR_INDICES:
            k = class_assignments[i]
            r = self.compute_residue_address(i, class_assignments, periods, phases)
            
            # Solve for key
            key_val = self.solve_key(plaintext[i], ct_pre[i], families[k])
            
            # Check Option-A constraints
            if families[k] in ['vigenere', 'variant_beaufort'] and key_val == 0:
                anchor_violations.append({
                    "index": i,
                    "reason": "pass-through (K=0) at anchor",
                    "family": families[k],
                    "key": key_val
                })
                continue
            
            # Check for collision consistency
            if r in key_tables[k]:
                if key_tables[k][r] != key_val:
                    anchor_violations.append({
                        "index": i,
                        "reason": "collision inconsistency",
                        "class": k,
                        "residue": r,
                        "existing_key": key_tables[k][r],
                        "new_key": key_val
                    })
                    continue
            else:
                key_tables[k][r] = key_val
        
        if anchor_violations:
            print(f"\n❌ Option-A violations at anchors:")
            for v in anchor_violations[:3]:  # Show first 3
                print(f"  - {v}")
            
            return {
                "feasible": False,
                "reason": "Option-A violations",
                "violations": anchor_violations
            }
        
        print("✅ Anchors pass Option-A constraints")
        
        # Second pass: solve remaining keys and encrypt
        c_pre = [''] * 97
        
        for i in range(97):
            k = class_assignments[i]
            r = self.compute_residue_address(i, class_assignments, periods, phases)
            
            # Get or solve key
            if r not in key_tables[k]:
                # Solve from this position
                key_tables[k][r] = self.solve_key(plaintext[i], ct_pre[i], families[k])
            
            # Encrypt
            c_pre[i] = self.encrypt_char(plaintext[i], key_tables[k][r], families[k])
        
        # Apply permutation to get final CT
        c_post = self.apply_permutation(''.join(c_pre), permutation)
        
        # Check if it matches K4 CT
        if c_post == self.k4_ct:
            print("✅ ENCRYPTS TO K4 CT!")
            
            # Collect forced anchor residues
            forced_residues = []
            for i in ANCHOR_INDICES:
                k = class_assignments[i]
                r = self.compute_residue_address(i, class_assignments, periods, phases)
                forced_residues.append({
                    "index": i,
                    "class": k,
                    "residue": r,
                    "key": key_tables[k][r],
                    "char": plaintext[i]
                })
            
            return {
                "feasible": True,
                "encrypts_to_ct": True,
                "route_id": route_id,
                "t2_sha256": hashlib.sha256(json.dumps(permutation).encode()).hexdigest(),
                "families": families,
                "periods": periods,
                "phases": phases,
                "forced_anchor_residues": forced_residues,
                "key_tables": {k: list(v.values()) for k, v in key_tables.items()}
            }
        else:
            # Find first mismatch
            for i in range(97):
                if c_post[i] != self.k4_ct[i]:
                    print(f"\n❌ Encryption mismatch at position {i}")
                    print(f"  Expected: {self.k4_ct[i]}")
                    print(f"  Got: {c_post[i]}")
                    
                    return {
                        "feasible": False,
                        "reason": "Encryption mismatch",
                        "first_mismatch": {
                            "position": i,
                            "expected": self.k4_ct[i],
                            "got": c_post[i]
                        }
                    }
            
            return {
                "feasible": False,
                "reason": "Unknown encryption failure"
            }


def run_quick_feasibility():
    """Run quick feasibility test with known schedule."""
    
    # Load plaintext
    pt_file = Path("runs/confirm/BLINDED_CH00_I003/plaintext_97.txt")
    with open(pt_file, 'r') as f:
        plaintext = f.read().strip()
    
    print("=" * 60)
    print("QUICK FEASIBILITY TEST")
    print("=" * 60)
    print(f"Plaintext: {plaintext[:50]}...")
    
    # Known schedule from prior work
    families = ['vigenere', 'vigenere', 'beaufort', 'vigenere', 'vigenere', 'beaufort']
    periods = [17, 16, 16, 16, 19, 20]
    phases = [0, 0, 0, 0, 0, 0]
    
    # Test with GRID route
    solver = MinimalTychoSolver()
    route_file = "routes/permutations/GRID_W14_ROWS.json"
    
    result = solver.test_feasibility(plaintext, route_file, families, periods, phases)
    
    # Save result
    output_dir = Path("runs/confirm/BLINDED_CH00_I003")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if result["feasible"]:
        # Save proof digest
        proof = {
            "feasible": True,
            "route_id": result["route_id"],
            "t2_sha256": result["t2_sha256"],
            "classing": "c6a",
            "per_class": [
                {"class_id": k, "family": families[k], "L": periods[k], "phase": phases[k]}
                for k in range(6)
            ],
            "forced_anchor_residues": result["forced_anchor_residues"],
            "ct_sha256": hashlib.sha256(K4_CT.encode()).hexdigest(),
            "pt_sha256": hashlib.sha256(plaintext.encode()).hexdigest(),
            "encrypts_to_ct": True,
            "notes": "Option-A enforced; quick feasibility passed"
        }
        
        proof_file = output_dir / "proof_digest.json"
        with open(proof_file, 'w') as f:
            json.dump(proof, f, indent=2)
        
        # Save coverage report
        coverage = {
            "encrypts_to_ct": True,
            "route_id": result["route_id"],
            "t2_sha256": result["t2_sha256"],
            "class_schedule": {
                "families": families,
                "periods": periods,
                "phases": phases
            },
            "anchors": {
                "EAST": "[21:25]",
                "NORTHEAST": "[25:34]",
                "BERLINCLOCK": "[63:74]"
            },
            "pt_sha256": hashlib.sha256(plaintext.encode()).hexdigest(),
            "ct_sha256": hashlib.sha256(K4_CT.encode()).hexdigest()
        }
        
        coverage_file = output_dir / "coverage_report.json"
        with open(coverage_file, 'w') as f:
            json.dump(coverage, f, indent=2)
        
        print(f"\n✅ Saved proof to {proof_file}")
        print(f"✅ Saved coverage to {coverage_file}")
        
    else:
        # Save failure report
        proof = {
            "feasible": False,
            "reason": result["reason"],
            "details": result
        }
        
        proof_file = output_dir / "proof_digest.json"
        with open(proof_file, 'w') as f:
            json.dump(proof, f, indent=2)
        
        print(f"\n❌ Feasibility failed: {result['reason']}")
        print(f"Saved failure report to {proof_file}")
    
    return result


if __name__ == "__main__":
    result = run_quick_feasibility()
    
    if result["feasible"]:
        print("\n" + "=" * 60)
        print("✅ FEASIBILITY PASSED - READY FOR CONFIRM")
        print("=" * 60)
        print("Next steps:")
        print("1. Run near-gate and phrase gate")
        print("2. Execute 10k mirrored nulls")
        print("3. Create Confirm bundle")
    else:
        print("\n" + "=" * 60)
        print("❌ FEASIBILITY FAILED")
        print("=" * 60)
        print("Will try alternate schedules or routes...")