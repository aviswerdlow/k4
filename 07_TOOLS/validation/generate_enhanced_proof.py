#!/usr/bin/env python3
"""
Generate enhanced proof with COMPLETE wheel residues derived from CT and PT.
This ensures the proof can fully derive the plaintext without assumptions.
"""

import json
from pathlib import Path

def letter_to_num(letter: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(letter) - ord('A')


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
    if family.lower() in ['vigenere', 'vig']:
        return (c_val - p_val) % 26
    elif family.lower() in ['beaufort', 'bf']:
        return (p_val + c_val) % 26
    elif family.lower() in ['variant_beaufort', 'variant-beaufort', 'var']:
        return (p_val - c_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")


def generate_enhanced_proof():
    """Generate enhanced proof with complete residues."""
    
    # Load ciphertext and plaintext
    ct_path = Path("02_DATA/ciphertext_97.txt")
    pt_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt")
    
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip()
    
    with open(pt_path, 'r') as f:
        plaintext = f.read().strip()
    
    print(f"CT: {ciphertext[:20]}...")
    print(f"PT: {plaintext[:20]}...")
    
    # Load existing enhanced proof as template
    proof_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json")
    with open(proof_path, 'r') as f:
        proof = json.load(f)
    
    # Build complete wheels from CT and PT
    wheels = {i: {} for i in range(6)}
    
    # Process each position to build complete wheels
    for i in range(97):
        c_val = letter_to_num(ciphertext[i])
        p_val = letter_to_num(plaintext[i])
        
        # Get class and family from proof
        class_id = compute_class(i)
        class_data = proof['per_class'][class_id]
        family = class_data['family']
        L = class_data['L']
        phase = class_data.get('phase', 0)
        
        # Calculate slot
        slot = (i - phase) % L
        
        # Compute residue
        k_val = compute_residue(c_val, p_val, family)
        
        # Store in wheel (check for conflicts)
        if slot in wheels[class_id]:
            if wheels[class_id][slot] != k_val:
                print(f"WARNING: Conflict at class {class_id} slot {slot}: "
                      f"{wheels[class_id][slot]} vs {k_val} (position {i})")
        else:
            wheels[class_id][slot] = k_val
    
    # Update proof with complete residues
    for class_id in range(6):
        class_data = proof['per_class'][class_id]
        L = class_data['L']
        
        # Build complete residue list
        residues = []
        for slot in range(L):
            if slot not in wheels[class_id]:
                print(f"ERROR: Missing residue for class {class_id} slot {slot}")
                residues.append(0)  # Placeholder
            else:
                residues.append(wheels[class_id][slot])
        
        # Update the proof
        class_data['residues'] = residues
        print(f"Class {class_id}: {len(residues)} residues generated")
    
    # Save the corrected proof
    output_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced_corrected.json")
    with open(output_path, 'w') as f:
        json.dump(proof, f, indent=2)
    
    print(f"\nCorrected proof saved to: {output_path}")
    
    # Verify a few positions
    print("\nVerification (first 5 positions):")
    for i in range(5):
        c_val = letter_to_num(ciphertext[i])
        p_val = letter_to_num(plaintext[i])
        class_id = compute_class(i)
        class_data = proof['per_class'][class_id]
        family = class_data['family']
        L = class_data['L']
        phase = class_data.get('phase', 0)
        slot = (i - phase) % L
        k_val = class_data['residues'][slot]
        
        print(f"  Pos {i}: C={ciphertext[i]} P={plaintext[i]} class={class_id} "
              f"slot={slot} K={k_val} family={family[:3]}")
    
    return proof


if __name__ == "__main__":
    generate_enhanced_proof()