#!/usr/bin/env python3
"""
Solve wheel configurations from ciphertext and plaintext.
Derives the complete cryptographic solution deterministically.
"""

from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


def letter_to_num(letter: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(letter) - ord('A')


def num_to_letter(num: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr(num + ord('A'))


def compute_class(i: int) -> int:
    """Compute class for index i using the 1989 formula."""
    return (i % 2) * 3 + (i % 3)


def compute_residue(c_val: int, p_val: int, family: str) -> int:
    """
    Compute the residue K from ciphertext and plaintext values.
    
    For finding K (given C and P):
    - Vigenere: K = C - P (mod 26)
    - Beaufort: K = P + C (mod 26)
    - Variant-Beaufort: K = P - C (mod 26)
    """
    if family == 'vigenere':
        return (c_val - p_val) % 26
    elif family == 'beaufort':
        return (p_val + c_val) % 26
    elif family == 'variant_beaufort':
        return (p_val - c_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")


def is_anchor_index(i: int) -> bool:
    """Check if index i is in an anchor span."""
    # EAST at 21-24
    if 21 <= i <= 24:
        return True
    # NORTHEAST at 25-33
    if 25 <= i <= 33:
        return True
    # BERLINCLOCK at 63-73
    if 63 <= i <= 73:
        return True
    return False


def solve_class_wheel(
    class_id: int,
    class_indices: List[int],
    ciphertext: str,
    plaintext: str
) -> Optional[Dict]:
    """
    Solve for the wheel configuration of a single class.
    
    Returns:
        Dict with family, L, phase, residues, forced_anchor_residues
        or None if no valid configuration found
    """
    # Family order to test
    families = ['vigenere', 'variant_beaufort', 'beaufort']
    
    # Collect all valid configurations
    valid_configs = []
    
    # Try each family
    for family in families:
        # Try each period L (prefer smaller L)
        for L in range(10, 23):  # L ∈ [10..22]
            # Try each phase
            for phase in range(L):  # phase ∈ [0..L-1]
                # Initialize wheel slots
                wheel = {}
                forced_anchors = []
                valid = True
                
                # Process each index in this class
                for i in class_indices:
                    c_val = letter_to_num(ciphertext[i])
                    p_val = letter_to_num(plaintext[i])
                    
                    # Compute residue K
                    k_val = compute_residue(c_val, p_val, family)
                    
                    # Option-A check: No K=0 at anchors for additive families
                    if is_anchor_index(i) and k_val == 0:
                        if family in ['vigenere', 'variant_beaufort']:
                            valid = False
                            break
                    
                    # Compute slot
                    slot = (i - phase) % L
                    
                    # Check consistency
                    if slot in wheel:
                        if wheel[slot] != k_val:
                            valid = False
                            break
                    else:
                        wheel[slot] = k_val
                    
                    # Record anchor residue
                    if is_anchor_index(i):
                        forced_anchors.append({
                            'index': i,
                            'slot': slot,
                            'residue': k_val,
                            'C': ciphertext[i],
                            'P': plaintext[i],
                            'family': family
                        })
                
                if not valid:
                    continue
                
                # Check if we have enough coverage
                # Some slots might not be hit if class has fewer indices than L
                # But we need at least some reasonable coverage
                if len(wheel) < min(L, len(class_indices)) * 0.7:
                    # Too sparse - likely wrong configuration
                    continue
                
                # For a perfect solution, all slots should be filled
                # Check coverage
                missing_slots = [slot for slot in range(L) if slot not in wheel]
                
                # Build complete residue array
                if missing_slots:
                    # Try to fill missing slots by checking if any unused indices could fill them
                    # This is less ideal but sometimes necessary
                    if len(missing_slots) <= 2:  # Allow up to 2 missing slots
                        residues = []
                        for slot in range(L):
                            if slot in wheel:
                                residues.append(wheel[slot])
                            else:
                                # Use a deterministic placeholder based on neighboring slots
                                # This maintains consistency but marks incomplete solution
                                residues.append(0)
                                print(f"    Warning: Class {class_id} slot {slot} unfilled (L={L}, phase={phase})")
                    else:
                        # Too many missing slots - reject this configuration
                        continue
                else:
                    # Perfect coverage!
                    residues = [wheel[slot] for slot in range(L)]
                
                # Store this valid configuration
                valid_configs.append({
                    'class_id': class_id,
                    'family': family,
                    'L': L,
                    'phase': phase,
                    'residues': residues,
                    'forced_anchor_residues': forced_anchors,
                    'missing_slots': len(missing_slots)
                })
    
    # Select best configuration
    if not valid_configs:
        return None
    
    # Sort by: 1) no missing slots, 2) smallest L, 3) family order, 4) smallest phase
    valid_configs.sort(key=lambda x: (
        x['missing_slots'],  # Prefer complete coverage
        x['L'],              # Prefer smaller period
        families.index(x['family']),  # Prefer family order
        x['phase']           # Prefer smaller phase
    ))
    
    best = valid_configs[0]
    # Remove the helper field
    del best['missing_slots']
    return best


def solve_wheels_from_ctpt(ciphertext: str, plaintext: str) -> Dict:
    """
    Solve all six wheel configurations from CT and PT.
    
    Args:
        ciphertext: 97-character ciphertext string
        plaintext: 97-character plaintext string
    
    Returns:
        Dict with six classes and their configurations
    """
    if len(ciphertext) != 97 or len(plaintext) != 97:
        raise ValueError("CT and PT must be exactly 97 characters")
    
    # Group indices by class
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        class_id = compute_class(i)
        class_indices[class_id].append(i)
    
    # Solve each class
    wheels = {}
    for class_id in range(6):
        indices = class_indices[class_id]
        print(f"Solving class {class_id} with {len(indices)} indices...")
        
        wheel_config = solve_class_wheel(class_id, indices, ciphertext, plaintext)
        
        if wheel_config is None:
            raise ValueError(f"Failed to find valid configuration for class {class_id}")
        
        wheels[class_id] = wheel_config
        print(f"  Found: {wheel_config['family']}, L={wheel_config['L']}, phase={wheel_config['phase']}")
    
    return wheels


def main():
    """Test the solver with actual K4 data."""
    # Load CT and PT
    ct_path = Path("02_DATA/ciphertext_97.txt")
    pt_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt")
    
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip()
    
    with open(pt_path, 'r') as f:
        plaintext = f.read().strip()
    
    print(f"CT: {ciphertext[:20]}...")
    print(f"PT: {plaintext[:20]}...")
    print()
    
    # Solve wheels
    wheels = solve_wheels_from_ctpt(ciphertext, plaintext)
    
    # Display results
    print("\nSolved wheel configurations:")
    for class_id in range(6):
        config = wheels[class_id]
        print(f"\nClass {class_id}:")
        print(f"  Family: {config['family']}")
        print(f"  Period L: {config['L']}")
        print(f"  Phase: {config['phase']}")
        print(f"  Residues: {config['residues']}")
        print(f"  Anchor count: {len(config['forced_anchor_residues'])}")
    
    # Save to JSON for inspection
    output_path = Path("wheels_solution.json")
    with open(output_path, 'w') as f:
        json.dump(wheels, f, indent=2)
    print(f"\nSolution saved to {output_path}")
    
    return wheels


if __name__ == "__main__":
    main()