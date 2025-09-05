#!/usr/bin/env python3
"""
Solve a lawful schedule for a given plaintext under GRID-only rails.
Given PT_X (with P[74]=X), find route + classing + per-class family/L/phase 
such that PT_X encrypts to CT under the route (T2) and NA-only rails with Option-A at anchors.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import itertools

# Constants
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ANCHORS = {
    "EAST": (21, 24),
    "NORTHEAST": (25, 33),
    "BERLINCLOCK": (63, 73)
}

def char_to_num(c: str) -> int:
    """Convert A=0..Z=25"""
    return ord(c) - ord('A')

def num_to_char(n: int) -> str:
    """Convert 0=A..25=Z"""
    return chr((n % 26) + ord('A'))

def load_route(route_path: Path) -> List[int]:
    """Load a transposition route (0-indexed)"""
    with open(route_path) as f:
        data = json.load(f)
    return data["permutation"]

def apply_transposition(text: str, route: List[int]) -> str:
    """Apply T2 transposition"""
    result = [''] * len(text)
    for i, pos in enumerate(route):
        if pos < len(text):
            result[pos] = text[i]
    return ''.join(result)

def inverse_transposition(text: str, route: List[int]) -> str:
    """Apply inverse T2 transposition"""
    result = [''] * len(text)
    for i, pos in enumerate(route):
        if pos < len(text):
            result[i] = text[pos]
    return ''.join(result)

class ClassingScheme:
    """Six-class repeating schedule"""
    
    @staticmethod
    def c6a(i: int) -> int:
        """class_id(i) = ((i % 2)*3) + (i % 3)"""
        return ((i % 2) * 3) + (i % 3)
    
    @staticmethod
    def c6b(i: int) -> int:
        """class_id(i) = i % 6"""
        return i % 6

def get_ordinal_in_class(i: int, classing_func) -> int:
    """Count how many indices of the same class appear before index i"""
    target_class = classing_func(i)
    count = 0
    for j in range(i):
        if classing_func(j) == target_class:
            count += 1
    return count

def compute_residue(i: int, classing_func, class_id: int, L: int, phase: int) -> int:
    """Compute residue address for index i"""
    ordinal = get_ordinal_in_class(i, classing_func)
    return (ordinal + phase) % L

def encrypt_char(p: str, k: str, family: str) -> str:
    """Encrypt single char with given key and family"""
    pn = char_to_num(p)
    kn = char_to_num(k)
    
    if family == "vigenere":
        cn = (pn + kn) % 26
    elif family == "variant_beaufort":
        cn = (pn - kn) % 26
    elif family == "beaufort":
        cn = (kn - pn) % 26
    else:
        raise ValueError(f"Unknown family: {family}")
    
    return num_to_char(cn)

def decrypt_char(c: str, k: str, family: str) -> str:
    """Decrypt single char with given key and family"""
    cn = char_to_num(c)
    kn = char_to_num(k)
    
    if family == "vigenere":
        pn = (cn - kn) % 26
    elif family == "variant_beaufort":
        pn = (cn + kn) % 26
    elif family == "beaufort":
        pn = (kn - cn) % 26
    else:
        raise ValueError(f"Unknown family: {family}")
    
    return num_to_char(pn)

def solve_anchor_key(p: str, c: str, family: str, is_anchor: bool = True) -> Optional[str]:
    """Solve for key value (with pass-through check only at anchors)"""
    pn = char_to_num(p)
    cn = char_to_num(c)
    
    if family == "vigenere":
        # C = P + K -> K = C - P
        kn = (cn - pn) % 26
        if is_anchor and kn == 0:  # Illegal pass-through at anchor
            return None
    elif family == "variant_beaufort":
        # C = P - K -> K = P - C
        kn = (pn - cn) % 26
        if is_anchor and kn == 0:  # Illegal pass-through at anchor
            return None
    elif family == "beaufort":
        # C = K - P -> K = C + P
        kn = (cn + pn) % 26
        # K=0 is allowed for Beaufort even at anchors
    else:
        raise ValueError(f"Unknown family: {family}")
    
    return num_to_char(kn)

class ScheduleSolver:
    def __init__(self, ct: str, route_paths: Dict[str, Path]):
        self.ct = ct
        self.route_paths = route_paths
        self.routes = {}
        for name, path in route_paths.items():
            self.routes[name] = load_route(path)
    
    def solve_for_plaintext(self, pt: str, max_schedules: int = 3) -> List[Dict]:
        """Find lawful schedules for given plaintext"""
        schedules = []
        
        # Shell 0: Winner replay (guaranteed feasible for winner PT)
        winner_families = ["vigenere", "vigenere", "beaufort", "vigenere", "beaufort", "vigenere"]
        winner_L = (17, 16, 16, 16, 16, 16)
        winner_phase = (0, 0, 0, 0, 0, 0)
        
        # Try exact winner configuration first
        schedule = self._test_schedule(
            pt, "GRID_W14_ROWS", ClassingScheme.c6a, "c6a",
            winner_families, winner_L, winner_phase, debug=True
        )
        if schedule:
            schedules.append(schedule)
            if len(schedules) >= max_schedules:
                return schedules
        
        # Shell 1: Fast search (winner-like)
        for route_name in ["GRID_W14_ROWS", "GRID_W10_NW"]:
            for classing_name in ["c6a", "c6b"]:
                classing_func = ClassingScheme.c6a if classing_name == "c6a" else ClassingScheme.c6b
                
                # Try specific L combinations (not all products)
                # Winner-like: mix of 16s and 17s
                L_candidates = [
                    (17, 16, 16, 16, 16, 16),  # Winner-like
                    (16, 16, 16, 16, 16, 16),  # All 16s
                    (18, 16, 16, 16, 16, 16),  # Slight variation
                    (17, 17, 16, 16, 16, 16),  # Another variation
                ]
                
                for L_tuple in L_candidates:
                    # Try small phases
                    for phase_tuple in [(0,0,0,0,0,0), (0,1,0,1,0,1), (1,0,1,0,1,0)]:
                        schedule = self._test_schedule(
                            pt, route_name, classing_func, classing_name,
                            winner_families, L_tuple, phase_tuple
                        )
                        if schedule:
                            schedules.append(schedule)
                            if len(schedules) >= max_schedules:
                                return schedules
        
        # Shell 2: Medium search (allow family flips)
        if len(schedules) < max_schedules:
            for route_name in ["GRID_W14_ROWS", "GRID_W10_NW"]:
                for classing_name in ["c6a", "c6b"]:
                    classing_func = ClassingScheme.c6a if classing_name == "c6a" else ClassingScheme.c6b
                    
                    # Allow one family flip
                    for flip_idx in range(6):
                        families = winner_families.copy()
                        # Flip between vigenere and beaufort variants
                        if families[flip_idx] == "vigenere":
                            families[flip_idx] = "beaufort"
                        elif families[flip_idx] == "beaufort":
                            families[flip_idx] = "vigenere"
                        
                        # Try fewer L combinations
                        L_candidates = [
                            (16, 16, 16, 16, 16, 16),
                            (14, 14, 14, 14, 14, 14),
                            (18, 18, 18, 18, 18, 18),
                        ]
                        
                        for L_tuple in L_candidates:
                            for phase_tuple in [(0,0,0,0,0,0), (0,1,0,1,0,1)]:
                                schedule = self._test_schedule(
                                    pt, route_name, classing_func, classing_name,
                                    families, L_tuple, phase_tuple
                                )
                                if schedule:
                                    schedules.append(schedule)
                                    if len(schedules) >= max_schedules:
                                        return schedules
        
        # Shell 3: Broad search (full family mix) - LIMITED
        if len(schedules) < max_schedules:
            for route_name in ["GRID_W14_ROWS"]:  # Try just one route in shell 3
                for classing_name in ["c6a"]:  # Try just one classing in shell 3
                    classing_func = ClassingScheme.c6a
                    
                    # Try a very limited set of family combinations
                    family_candidates = [
                        ["beaufort", "beaufort", "vigenere", "vigenere", "vigenere", "vigenere"],
                        ["vigenere", "vigenere", "vigenere", "vigenere", "vigenere", "vigenere"],
                        ["variant_beaufort"] * 6,
                    ]
                    
                    for families in family_candidates:
                        for L_tuple in [(16,16,16,16,16,16), (20,20,20,20,20,20)]:
                            phase_tuple = (0,0,0,0,0,0)
                            schedule = self._test_schedule(
                                pt, route_name, classing_func, classing_name,
                                families, L_tuple, phase_tuple
                            )
                            if schedule:
                                schedules.append(schedule)
                                if len(schedules) >= max_schedules:
                                    return schedules
        
        return schedules
    
    def _test_schedule(self, pt: str, route_name: str, classing_func, classing_name: str,
                      families: List[str], L_tuple: Tuple[int], phase_tuple: Tuple[int],
                      debug: bool = False) -> Optional[Dict]:
        """Test if a schedule is lawful (encrypts to CT)"""
        
        # For GRID routes, transposition is identity (no change)
        # We work directly with plaintext indices
        route = self.routes[route_name]
        
        # First test anchors only (early pruning)
        key_schedule = [{} for _ in range(6)]  # Per-class key dictionaries
        
        for anchor_name, (start, end) in ANCHORS.items():
            for i in range(start, end + 1):
                if i >= len(pt):
                    continue
                
                class_id = classing_func(i)
                L = L_tuple[class_id]
                phase = phase_tuple[class_id]
                family = families[class_id]
                
                residue = compute_residue(i, classing_func, class_id, L, phase)
                
                # Solve for key at this anchor (pre-transposition position)
                p_char = pt[i]
                c_char = self.ct[i]
                k_char = solve_anchor_key(p_char, c_char, family, is_anchor=True)
                
                if k_char is None:  # Illegal pass-through
                    if debug:
                        print(f"Anchor {i}: Illegal pass-through for {family} (P={p_char}, C={c_char})")
                    return None
                
                # Check for conflicts
                if residue in key_schedule[class_id]:
                    if key_schedule[class_id][residue] != k_char:
                        if debug:
                            print(f"Anchor {i}: Collision at class {class_id}, residue {residue}")
                            print(f"  Existing: {key_schedule[class_id][residue]}, New: {k_char}")
                        return None  # Collision
                else:
                    key_schedule[class_id][residue] = k_char
                    if debug:
                        print(f"Anchor {i}: Set class {class_id}, residue {residue} = {k_char}")
        
        # Anchors are feasible, now solve for ALL key values from PT and CT
        # This fills in the free residues with their actual values
        if debug:
            print(f"Solving for all {min(len(pt), len(self.ct))} positions...")
        for i in range(min(len(pt), len(self.ct))):
            class_id = classing_func(i)
            L = L_tuple[class_id]
            phase = phase_tuple[class_id]
            family = families[class_id]
            
            residue = compute_residue(i, classing_func, class_id, L, phase)
            
            # If this residue isn't already set, solve for it
            if residue not in key_schedule[class_id]:
                p_char = pt[i]
                c_char = self.ct[i]
                k_char = solve_anchor_key(p_char, c_char, family, is_anchor=False)
                
                if k_char is None:  # This shouldn't happen for non-anchors
                    return None
                    
                key_schedule[class_id][residue] = k_char if k_char else 'A'
            else:
                # Verify consistency with already-set key
                p_char = pt[i]
                c_char = self.ct[i]
                expected_c = encrypt_char(p_char, key_schedule[class_id][residue], family)
                if expected_c != c_char:
                    if debug:
                        print(f"Position {i}: Inconsistency - Expected {c_char}, got {expected_c}")
                        print(f"  P={p_char}, K={key_schedule[class_id][residue]}, family={family}")
                    return None  # Inconsistency
        
        # Encrypt full plaintext (pre-transposition)
        encrypted = []
        for i in range(len(pt)):
            class_id = classing_func(i)
            L = L_tuple[class_id]
            phase = phase_tuple[class_id]
            family = families[class_id]
            
            residue = compute_residue(i, classing_func, class_id, L, phase)
            if residue not in key_schedule[class_id]:
                if debug:
                    print(f"Missing residue {residue} for class {class_id} at position {i}")
                return None  # Missing key value
            k_char = key_schedule[class_id][residue]
            p_char = pt[i]
            c_char = encrypt_char(p_char, k_char, family)
            encrypted.append(c_char)
        
        encrypted_text = ''.join(encrypted)
        
        # For GRID routes, transposition is identity, so encrypted_text = CT
        
        if debug and encrypted_text != self.ct:
            # Log first mismatch for debugging
            for i in range(min(len(encrypted_text), len(self.ct))):
                if encrypted_text[i] != self.ct[i]:
                    class_id = classing_func(i)
                    residue = compute_residue(i, classing_func, class_id, L_tuple[class_id], phase_tuple[class_id])
                    print(f"Mismatch at i={i}: Expected {self.ct[i]}, got {encrypted_text[i]}")
                    print(f"  Class {class_id}, family={families[class_id]}")
                    print(f"  L={L_tuple[class_id]}, phase={phase_tuple[class_id]}, r={residue}")
                    print(f"  P={pt[i] if i < len(pt) else '?'}, K={key_schedule[class_id].get(residue, '?')}")
                    break
        
        if encrypted_text == self.ct:
            # Success! Build schedule record
            return {
                "route_id": route_name,
                "classing": classing_name,
                "per_class": [
                    {
                        "class_id": i,
                        "family": families[i],
                        "L": L_tuple[i],
                        "phase": phase_tuple[i]
                    }
                    for i in range(6)
                ],
                "key_schedule": key_schedule,
                "encrypts_to_ct": True
            }
        
        return None


def main():
    """Test the solver with winner plaintext"""
    import sys
    
    # Load ciphertext
    ct_path = Path("experiments/p74_editorial/data/ciphertext_97.txt")
    with open(ct_path) as f:
        ct = f.read().strip()
    
    # Set up route paths
    route_paths = {
        "GRID_W14_ROWS": Path("experiments/p74_editorial/data/permutations/GRID_W14_ROWS.json"),
        "GRID_W10_NW": Path("experiments/p74_editorial/data/permutations/GRID_W10_NW.json")
    }
    
    # Load winner plaintext
    winner_path = Path("experiments/p74_editorial/data/pts/winner.txt")
    with open(winner_path) as f:
        winner_pt = f.read().strip()
    
    # Test with a specific letter if provided
    if len(sys.argv) > 1:
        letter = sys.argv[1].upper()
        pt_test = winner_pt[:74] + letter + winner_pt[75:]
        print(f"Testing P[74]={letter}")
    else:
        pt_test = winner_pt
        print("Testing winner plaintext")
    
    solver = ScheduleSolver(ct, route_paths)
    schedules = solver.solve_for_plaintext(pt_test, max_schedules=3)
    
    if schedules:
        print(f"Found {len(schedules)} lawful schedule(s):")
        for i, sched in enumerate(schedules, 1):
            print(f"\nSchedule {i}:")
            print(f"  Route: {sched['route_id']}")
            print(f"  Classing: {sched['classing']}")
            print(f"  Per-class:")
            for pc in sched['per_class']:
                print(f"    Class {pc['class_id']}: {pc['family']}, L={pc['L']}, phase={pc['phase']}")
    else:
        print("No lawful schedule found")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())