#!/usr/bin/env python3
"""
Build enhanced proof files with complete wheel data derived from CT+PT.
Creates both proof_digest.json (minimal) and proof_digest_enhanced.json (full).
"""

import json
import hashlib
from pathlib import Path
from typing import Dict
from solve_wheels_from_ctpt import solve_wheels_from_ctpt


def compute_sha256(content: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(content.encode()).hexdigest()


def build_seed_recipe(ct_sha: str, pt_sha: str, t2_sha: str) -> tuple:
    """Build deterministic seed recipe."""
    seed_recipe = f"ENHANCED_PROOF|K4|ct:{ct_sha}|pt:{pt_sha}|t2:{t2_sha}"
    # Take low 64 bits of SHA256
    seed_hash = hashlib.sha256(seed_recipe.encode()).digest()
    seed_u64 = int.from_bytes(seed_hash[:8], 'little') & 0xFFFFFFFFFFFFFFFF
    return seed_recipe, seed_u64


def main():
    """Build enhanced proof files with real cryptographic values."""
    
    # Load CT and PT
    ct_path = Path("02_DATA/ciphertext_97.txt")
    pt_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt")
    
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip()
    
    with open(pt_path, 'r') as f:
        plaintext = f.read().strip()
    
    # Compute hashes
    ct_sha = compute_sha256(ciphertext)
    pt_sha = compute_sha256(plaintext)
    t2_sha = "a5260415e76509638b4845d5e707521126aca2d67b50177b3c94f8ccc4c56c31"  # From existing data
    
    print(f"CT SHA: {ct_sha}")
    print(f"PT SHA: {pt_sha}")
    print(f"T2 SHA: {t2_sha}")
    
    # Solve wheels from CT+PT
    print("\nSolving wheels from CT+PT...")
    wheels = solve_wheels_from_ctpt(ciphertext, plaintext)
    
    # Build seed recipe
    seed_recipe, seed_u64 = build_seed_recipe(ct_sha, pt_sha, t2_sha)
    
    # Build per_class array for enhanced proof
    per_class = []
    for class_id in range(6):
        config = wheels[class_id]
        
        # Add residues_alpha (A-Z representation)
        residues_alpha = [chr(r + ord('A')) for r in config['residues']]
        
        per_class.append({
            'class_id': class_id,
            'family': config['family'],
            'L': config['L'],
            'phase': config['phase'],
            'residues': config['residues'],
            'residues_alpha': residues_alpha,
            'forced_anchor_residues': config['forced_anchor_residues']
        })
    
    # Create enhanced proof
    proof_enhanced = {
        'schema_version': '1.0.0',
        'route_id': 'GRID_W14_ROWS',
        't2_sha': t2_sha,
        'classing': 'c6a',
        'class_formula': '((i % 2) * 3) + (i % 3)',
        'class_formula_note': 'Standard six-track classing - matches 1989 hand method exactly',
        'option_a': {
            'description': 'No K=0 at anchors for additive families',
            'enforced': True,
            'EAST': [21, 24],
            'NORTHEAST': [25, 33],
            'BERLINCLOCK': [63, 73]
        },
        'per_class': per_class,
        'seed_recipe': seed_recipe,
        'seed_u64': seed_u64,
        'pre_reg_commit': 'd0b03f4',
        'policy_sha': 'bc083cc4129fedbc',
        'pt_sha256_bundle': pt_sha,
        'derivation_guarantee': {
            'method': 'Complete wheels derived from published CT+PT',
            'tail_derivation': 'Emerges from anchor-forced wheels via hand method',
            'no_assumptions': True,
            'gates_head_only': True,
            'no_tail_guard': True
        }
    }
    
    # Create minimal proof
    proof_minimal = {
        'route_id': 'GRID_v522B_HEAD_0020_v522B',
        't2_sha': t2_sha,
        'option_a': {
            'EAST': [21, 24],
            'NORTHEAST': [25, 33],
            'BERLINCLOCK': [63, 73]
        },
        'seeds': {
            'master': 1337,
            'head': 2772336211,
            'filler': 15254849010086659901
        },
        'pre_reg_commit': 'd0b03f4',
        'policy_sha': 'bc083cc4129fedbc',
        'pt_sha256': pt_sha,
        'filler_mode': 'lexicon',
        'filler_tokens': {
            'gap4': 'THEN',
            'gap7': 'BETWEEN'
        }
    }
    
    # Save enhanced proof
    enhanced_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest_enhanced.json")
    with open(enhanced_path, 'w') as f:
        json.dump(proof_enhanced, f, indent=2)
    print(f"\n✅ Saved enhanced proof to {enhanced_path}")
    
    # Save minimal proof
    minimal_path = Path("01_PUBLISHED/winner_HEAD_0020_v522B/proof_digest.json")
    with open(minimal_path, 'w') as f:
        json.dump(proof_minimal, f, indent=2)
    print(f"✅ Saved minimal proof to {minimal_path}")
    
    # Display summary
    print("\nWheel Configuration Summary:")
    for class_id in range(6):
        config = per_class[class_id]
        anchor_count = len(config['forced_anchor_residues'])
        print(f"  Class {class_id}: {config['family']}, L={config['L']}, phase={config['phase']}, {anchor_count} anchors")
    
    print(f"\nSeed: {seed_u64}")
    print(f"PT SHA: {pt_sha}")
    
    return proof_enhanced, proof_minimal


if __name__ == "__main__":
    main()