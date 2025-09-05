#!/usr/bin/env python3
"""
generate_candidates.py - Generate K4 candidate heads with surveying imperatives

Generates alternative K4 candidate heads with different surveying-equivalent
imperatives while maintaining the GRID-only structure.

Usage:
    python3 generate_candidates.py \
        --policy policies/POLICY.seamfree.and.json \
        --permutations data/permutations.txt \
        --candidates data/candidates_within_frame.txt
"""

import json
import argparse
import hashlib
from pathlib import Path

# Surveying-equivalent imperatives
IMPERATIVES = [
    "SIGHT THE BERLIN",       # Original (published)
    "SET THE BEARING",        # Survey/navigation equivalent
    "NOTE THE BERLIN",        # Observation equivalent  
    "READ THE BERLIN",        # Reading equivalent
    "OBSERVE THE DIAL"        # Instrument observation
]

# Declination scaffolds (from policies)
DECLINATION_SCAFFOLDS = [
    "SET", "TRUE", "CORRECT", "BRING"  # High-confidence surveying terms
]

def normalize_text(text):
    """Normalize text for cryptographic operations."""
    return text.upper().replace(' ', '').replace('\n', '')

def generate_variants(base_text, anchor_start, anchor_end):
    """Generate imperative variants maintaining structure."""
    variants = []
    
    # Extract parts
    prefix = base_text[:anchor_start]
    anchor = base_text[anchor_start:anchor_end]  
    suffix = base_text[anchor_end:]
    
    # Generate each variant
    for imperative in IMPERATIVES:
        # Build variant with exact positioning
        variant = prefix + imperative
        
        # Pad or adjust to maintain positioning
        target_len = anchor_end - anchor_start
        current_len = len(imperative)
        
        if current_len < target_len:
            # Add padding/filler
            variant += 'X' * (target_len - current_len)
        elif current_len > target_len:
            # Truncate if too long
            variant = prefix + imperative[:target_len]
        
        variant += suffix
        
        # Record variant
        variants.append({
            'imperative': imperative,
            'full_head': variant[:74],  # Head region only
            'hash': hashlib.sha256(variant[:74].encode()).hexdigest()[:16]
        })
    
    return variants

def load_permutation(perm_file):
    """Load a representative permutation."""
    with open(perm_file, 'r') as f:
        lines = f.readlines()
        # Use first valid permutation or a specific one
        for line in lines:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    return parts[1]  # Return the permutation text
    return None

def main():
    parser = argparse.ArgumentParser(description='Generate K4 candidate heads')
    parser.add_argument('--policy', required=True, help='Policy JSON file')
    parser.add_argument('--permutations', required=True, help='Permutations file')
    parser.add_argument('--candidates', required=True, help='Output candidates file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Load policy
    with open(args.policy, 'r') as f:
        policy = json.load(f)
    
    # Extract anchor positions
    anchors = policy['rails']['anchors_0idx']
    east_range = anchors.get('EAST', [21, 24])
    northeast_range = anchors.get('NORTHEAST', [25, 33])
    
    # Load a base permutation
    base_text = load_permutation(args.permutations)
    if not base_text:
        print("Error: Could not load base permutation")
        return 1
    
    # Generate candidates for each anchor type
    all_candidates = []
    
    # EAST variants (positions 21-24)
    print(f"Generating EAST variants (positions {east_range[0]}-{east_range[1]})...")
    east_variants = generate_variants(base_text, east_range[0], east_range[1]+1)
    for v in east_variants:
        v['anchor_type'] = 'EAST'
    all_candidates.extend(east_variants)
    
    # NORTHEAST variants (positions 25-33)
    print(f"Generating NORTHEAST variants (positions {northeast_range[0]}-{northeast_range[1]})...")
    ne_variants = generate_variants(base_text, northeast_range[0], northeast_range[1]+1)
    for v in ne_variants:
        v['anchor_type'] = 'NORTHEAST'
    all_candidates.extend(ne_variants)
    
    # Write candidates
    with open(args.candidates, 'w') as f:
        f.write("# K4 Candidate Heads with Surveying Imperatives\n")
        f.write("# Format: anchor_type | imperative | head_text | hash\n")
        f.write("#\n")
        
        for candidate in all_candidates:
            f.write(f"{candidate['anchor_type']}\t")
            f.write(f"{candidate['imperative']}\t")
            f.write(f"{candidate['full_head']}\t")
            f.write(f"{candidate['hash']}\n")
    
    print(f"\nGenerated {len(all_candidates)} candidate heads")
    print(f"Written to: {args.candidates}")
    
    if args.verbose:
        print("\nSample candidates:")
        for c in all_candidates[:3]:
            print(f"  {c['anchor_type']}: {c['imperative']} -> {c['full_head'][:40]}...")
    
    return 0

if __name__ == "__main__":
    exit(main())