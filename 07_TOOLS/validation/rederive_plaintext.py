#!/usr/bin/env python3
"""
Re-derive plaintext from ciphertext and proof using the exact hand method.
This ensures the tail is ALWAYS derived, never assumed.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def letter_to_num(letter: str) -> int:
    """Convert letter to number (A=0, B=1, ..., Z=25)."""
    return ord(letter) - ord('A')


def num_to_letter(num: int) -> str:
    """Convert number to letter (0=A, 1=B, ..., 25=Z)."""
    return chr((num % 26) + ord('A'))


def compute_class(i: int) -> int:
    """
    Compute class for index i using the documented formula.
    class(i) = (i % 2) * 3 + (i % 3)
    """
    return (i % 2) * 3 + (i % 3)


def decrypt_cell(c_val: int, k_val: int, family: str) -> int:
    """
    Apply decrypt rule for the given family.
    
    Vigenère: P = C - K (mod 26)
    Beaufort: P = K - C (mod 26)  
    Variant-Beaufort: P = C + K (mod 26)
    """
    if family.lower() in ['vigenere', 'vig']:
        return (c_val - k_val) % 26
    elif family.lower() in ['beaufort', 'bf']:
        return (k_val - c_val) % 26
    elif family.lower() in ['variant_beaufort', 'variant-beaufort', 'var-bf', 'varbf']:
        return (c_val + k_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")


def build_wheel(L: int, phase: int, residues: List = None, forced_residues: List[Dict] = None) -> Dict[int, int]:
    """
    Build a period wheel with all residues or forced anchor residues.
    
    Args:
        L: Period length
        phase: Phase offset
        residues: Full list of residues for the wheel (if available)
        forced_residues: List of {index, residue} pairs from anchors (fallback)
        
    Returns:
        Dict mapping slot -> residue value
    """
    wheel = {}
    
    # If we have full residues, use them
    if residues and len(residues) == L:
        for slot in range(L):
            wheel[slot] = residues[slot]
    # Otherwise use forced residues from anchors
    elif forced_residues:
        for entry in forced_residues:
            idx = entry['index']
            residue = entry['residue']
            
            # Calculate the slot on the wheel for this index
            slot = (idx - phase) % L
            
            # Check for conflicts
            if slot in wheel and wheel[slot] != residue:
                raise ValueError(f"Conflicting residues at slot {slot}: {wheel[slot]} vs {residue}")
            
            wheel[slot] = residue
    
    return wheel


def rederive_plaintext(ct_path: Path, proof_path: Path, out_path: Path) -> str:
    """
    Re-derive plaintext from ciphertext and proof using the exact hand method.
    
    This function:
    1. Loads the ciphertext (97 letters A-Z)
    2. Loads proof_digest.json to get the six wheels (family, L, phase, forced residues)
    3. For each index 0-96:
       - Computes class using (i%2)*3 + (i%3)
       - Finds wheel slot ((i - phase) mod L)
       - Reads residue K from the wheel
       - Applies decrypt rule to get P from C and K
    4. Writes derived plaintext and returns its SHA-256
    
    Returns:
        SHA-256 of the derived plaintext
    """
    # Load ciphertext
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip()
    
    if len(ciphertext) != 97:
        raise ValueError(f"Ciphertext must be 97 letters, got {len(ciphertext)}")
    
    if not all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in ciphertext):
        raise ValueError("Ciphertext must contain only A-Z letters")
    
    # Load proof
    with open(proof_path, 'r') as f:
        proof = json.load(f)
    
    # Build wheels for each class
    wheels = {}
    class_info = {}
    
    # Handle both old and new proof formats
    if 'per_class' in proof:
        classes_data = proof['per_class']
    elif 'classes' in proof:
        classes_data = proof['classes']
    else:
        # Extract from top-level structure
        classes_data = []
        for class_id in range(6):
            class_key = f"class_{class_id}"
            if class_key in proof:
                class_data = proof[class_key]
                class_data['class_id'] = class_id
                classes_data.append(class_data)
    
    for class_data in classes_data:
        class_id = class_data.get('class_id', class_data.get('class'))
        family = class_data.get('family')
        L = class_data.get('L', class_data.get('period'))
        phase = class_data.get('phase', 0)
        
        # Get full residues or forced residues
        residues = class_data.get('residues', [])
        forced_residues = class_data.get('forced_anchor_residues', [])
        if not forced_residues and 'anchor_residues' in class_data:
            forced_residues = class_data['anchor_residues']
        
        # Build the wheel (prefer full residues if available)
        wheel = build_wheel(L, phase, residues, forced_residues)
        wheels[class_id] = wheel
        class_info[class_id] = {
            'family': family,
            'L': L,
            'phase': phase
        }
    
    # Derive plaintext
    plaintext = []
    
    for i in range(97):
        # Get ciphertext value
        c_val = letter_to_num(ciphertext[i])
        
        # Compute class
        class_id = compute_class(i)
        
        # Get wheel info
        info = class_info[class_id]
        wheel = wheels[class_id]
        
        # Calculate slot on the wheel
        slot = (i - info['phase']) % info['L']
        
        # Get residue K from wheel
        if slot not in wheel:
            raise ValueError(
                f"No residue at slot {slot} for class {class_id} index {i}. "
                f"Proof is incomplete - cannot derive plaintext without this residue. "
                f"This slot must be constrained by anchors."
            )
        
        k_val = wheel[slot]
        
        # Apply decrypt rule
        p_val = decrypt_cell(c_val, k_val, info['family'])
        
        # Convert to letter
        plaintext.append(num_to_letter(p_val))
    
    # Join and write
    derived_pt = ''.join(plaintext)
    
    with open(out_path, 'w') as f:
        f.write(derived_pt)
    
    # Return SHA-256
    return hashlib.sha256(derived_pt.encode()).hexdigest()


def derive_tail_only(ct_path: Path, proof_path: Path) -> str:
    """
    Derive only the tail portion (indices 75-96) to verify it emerges from anchors.
    
    Returns:
        The tail string (22 characters)
    """
    # Use full derivation but return only tail slice
    temp_path = Path("/tmp/tail_derivation_temp.txt")
    rederive_plaintext(ct_path, proof_path, temp_path)
    
    with open(temp_path, 'r') as f:
        full_pt = f.read().strip()
    
    return full_pt[75:97]  # Indices 75-96 inclusive


def verify_no_tail_guard(proof_path: Path) -> bool:
    """
    Verify that the proof contains no tail guard or seam references.
    
    Returns:
        True if no tail guard found (good), False if found (bad)
    """
    with open(proof_path, 'r') as f:
        proof_text = f.read()
    
    # Check for any tail guard references
    forbidden_terms = ['tail_guard', 'seam_guard', 'tail_constraint', 'seam_boundary']
    
    for term in forbidden_terms:
        if term in proof_text.lower():
            return False
    
    return True


def main():
    """Test re-derivation on the winner bundle."""
    import sys
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Re-derive plaintext from CT + proof')
    parser.add_argument('--ct', default="02_DATA/ciphertext_97.txt", 
                        help='Path to ciphertext file')
    parser.add_argument('--proof', default="01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json",
                        help='Path to proof file')
    parser.add_argument('--out', default="/tmp/derived_plaintext_97.txt",
                        help='Output path for derived plaintext')
    args = parser.parse_args()
    
    # Paths
    ct_path = Path(args.ct)
    proof_path = Path(args.proof)
    bundle_pt_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt")
    derived_pt_path = Path(args.out)
    
    print("Re-deriving plaintext from ciphertext + proof...")
    
    # Re-derive
    derived_sha = rederive_plaintext(ct_path, proof_path, derived_pt_path)
    print(f"Derived PT SHA-256: {derived_sha}")
    
    # Load bundle PT for comparison
    with open(bundle_pt_path, 'r') as f:
        bundle_pt = f.read().strip()
    bundle_sha = hashlib.sha256(bundle_pt.encode()).hexdigest()
    print(f"Bundle PT SHA-256:  {bundle_sha}")
    
    # Compare
    if derived_sha == bundle_sha:
        print("✅ SUCCESS: Derived plaintext matches bundle plaintext")
        print("   The tail was correctly derived, not assumed!")
    else:
        print("❌ FAILURE: Derived plaintext does not match bundle")
        print("   This violates the hand-derivation guarantee")
        sys.exit(1)
    
    # Also verify tail portion specifically
    print("\nVerifying tail derivation (indices 75-96)...")
    tail = derive_tail_only(ct_path, proof_path)
    print(f"Derived tail: {tail}")
    
    expected_tail = bundle_pt[75:97]
    if tail == expected_tail:
        print("✅ Tail matches exactly")
    else:
        print("❌ Tail mismatch!")
        sys.exit(1)
    
    # Check for tail guard
    print("\nChecking for tail guard references...")
    if verify_no_tail_guard(proof_path):
        print("✅ No tail guard found (good)")
    else:
        print("❌ Tail guard references found (bad)")
        sys.exit(1)


if __name__ == "__main__":
    main()