#!/usr/bin/env python3
"""
Fork B L=15 Analysis: Complete tail emergence and comparison study.
Pure algebra, no semantics, deterministic.
"""

import json
import hashlib
from collections import defaultdict

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_ciphertext():
    """Load the 97-character ciphertext"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        return f.read().strip()

def load_canonical_plaintext():
    """Load the canonical plaintext for comparison"""
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        return f.read().strip()

def get_anchors():
    """Get anchor positions and plaintext"""
    return {
        'EAST': (21, 24),
        'NORTHEAST': (25, 33),
        'BERLIN': (63, 68),
        'CLOCK': (69, 73)
    }

def build_wheels_from_anchors(L, ciphertext, anchors, phase=0):
    """
    Build wheels for given L using anchors only.
    Returns wheels dictionary with residues.
    """
    # Initialize wheels
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'phase': phase,
            'residues': [None] * L
        }
    
    # Process anchors
    conflicts = []
    for crib_text, (start, end) in anchors.items():
        for i, p_char in enumerate(crib_text):
            pos = start + i
            if pos > end:
                break
            
            c = compute_class_baseline(pos)
            s = (pos + phase) % L
            
            c_char = ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            # Compute residue
            if wheels[c]['family'] == 'vigenere':
                k_val = (c_val - p_val) % 26
            else:  # beaufort
                k_val = (p_val + c_val) % 26
            
            # Check Option-A for Beaufort
            if wheels[c]['family'] == 'beaufort' and k_val == 0:
                continue  # Skip, Option-A violation
            
            # Store or check for conflict
            if wheels[c]['residues'][s] is not None:
                if wheels[c]['residues'][s] != k_val:
                    conflicts.append((c, s, wheels[c]['residues'][s], k_val))
            else:
                wheels[c]['residues'][s] = k_val
    
    return wheels, conflicts

def derive_plaintext(ciphertext, wheels):
    """
    Derive plaintext using wheels.
    Returns plaintext string with '?' for unknowns.
    """
    plaintext = []
    derived_count = 0
    
    for i in range(len(ciphertext)):
        c = compute_class_baseline(i)
        L = wheels[c]['L']
        phase = wheels[c]['phase']
        s = (i + phase) % L
        
        if wheels[c]['residues'][s] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:  # beaufort
                p_val = (k_val - c_val) % 26
            
            plaintext.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            plaintext.append('?')
    
    return ''.join(plaintext), derived_count

def extract_tail_grid(plaintext):
    """
    Extract tail (positions 74-96) as a grid.
    Returns formatted string and counts.
    """
    tail = plaintext[74:97]  # Positions 74-96 (0-indexed)
    grid_lines = []
    derived = 0
    unknown = 0
    
    for i, char in enumerate(tail):
        pos = 74 + i
        if char == '?':
            unknown += 1
            grid_lines.append(f"{pos:2d} ?")
        else:
            derived += 1
            grid_lines.append(f"{pos:2d} {char}")
    
    # Format as 11 pairs per line
    grid = ""
    for i in range(0, len(grid_lines), 11):
        grid += "  ".join(grid_lines[i:i+11]) + "\n"
    
    return grid, derived, unknown

def analyze_L_period(L, output_dir):
    """
    Analyze a specific L value with anchors only.
    """
    print(f"\n=== Analyzing L={L} (Anchors Only) ===")
    
    ciphertext = load_ciphertext()
    anchors = get_anchors()
    
    # Build wheels from anchors
    wheels, conflicts = build_wheels_from_anchors(L, ciphertext, anchors)
    
    if conflicts:
        print(f"  Conflicts detected: {len(conflicts)}")
    
    # Derive plaintext
    plaintext, derived_total = derive_plaintext(ciphertext, wheels)
    unknown_total = 97 - derived_total
    
    # Extract tail
    tail_grid, tail_derived, tail_unknown = extract_tail_grid(plaintext)
    
    print(f"  Total: {derived_total} derived, {unknown_total} unknown")
    print(f"  Tail: {tail_derived} derived, {tail_unknown} unknown")
    
    # Save outputs
    with open(f'{output_dir}/PT_PARTIAL.txt', 'w') as f:
        f.write(plaintext)
    
    with open(f'{output_dir}/TAIL_GRID.txt', 'w') as f:
        f.write(f"L={L} TAIL EMERGENCE (Positions 74-96)\n")
        f.write("="*50 + "\n\n")
        f.write(tail_grid)
        f.write(f"\nSummary: {tail_derived} letters, {tail_unknown} unknowns\n")
    
    with open(f'{output_dir}/COUNTS.json', 'w') as f:
        json.dump({
            'L': L,
            'derived_total': derived_total,
            'unknown_total': unknown_total,
            'tail_derived': tail_derived,
            'tail_unknown': tail_unknown
        }, f, indent=2)
    
    return wheels, plaintext, derived_total

def test_canonical_tail_fit(L, wheels, output_dir):
    """
    Test if canonical tail fits under L.
    """
    print(f"\n=== Testing Canonical Tail Fit (L={L}) ===")
    
    ciphertext = load_ciphertext()
    canonical_pt = load_canonical_plaintext()
    canonical_tail = canonical_pt[74:97]
    
    print(f"  Canonical tail: {canonical_tail}")
    
    # Add tail constraints to wheels
    phase = 0
    for i, p_char in enumerate(canonical_tail):
        pos = 74 + i
        c = compute_class_baseline(pos)
        s = (pos + phase) % L
        
        # Skip if already forced
        if wheels[c]['residues'][s] is not None:
            continue
        
        c_char = ciphertext[pos]
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        # Compute residue
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:  # beaufort
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    # Derive full plaintext
    plaintext, derived_total = derive_plaintext(ciphertext, wheels)
    
    print(f"  Derived: {derived_total}/97")
    
    # Save outputs
    with open(f'{output_dir}/PT_FULL.txt', 'w') as f:
        f.write(plaintext)
    
    # Extract tail
    tail_grid, tail_derived, tail_unknown = extract_tail_grid(plaintext)
    
    with open(f'{output_dir}/TAIL_GRID.txt', 'w') as f:
        f.write(f"L={L} WITH CANONICAL TAIL (Positions 74-96)\n")
        f.write("="*50 + "\n\n")
        f.write(tail_grid)
    
    # Check if identical
    derived_tail = plaintext[74:97]
    if derived_tail == canonical_tail:
        diff_result = "IDENTICAL"
        print("  ✓ Canonical tail reproduced exactly")
    else:
        diff_result = []
        for i in range(len(canonical_tail)):
            if i < len(derived_tail):
                if canonical_tail[i] != derived_tail[i]:
                    diff_result.append(f"Pos {74+i}: expected '{canonical_tail[i]}', got '{derived_tail[i]}'")
        diff_result = "\n".join(diff_result) if diff_result else "LENGTHS DIFFER"
        print(f"  ✗ Differences found")
    
    with open(f'{output_dir}/TAIL_DIFF.txt', 'w') as f:
        f.write(diff_result)
    
    return plaintext, derived_total

def test_minimal_tail_subsets(L, ciphertext):
    """
    Test how much tail is needed to close the solution.
    """
    print(f"\n=== Minimal Tail Analysis (L={L}) ===")
    
    canonical_pt = load_canonical_plaintext()
    canonical_tail = canonical_pt[74:97]
    anchors = get_anchors()
    
    results = []
    
    for k in [10, 14, 18, 22]:
        # Build wheels from anchors
        wheels, _ = build_wheels_from_anchors(L, ciphertext, anchors)
        
        # Add first k tail positions
        tail_subset = canonical_tail[:k]
        
        for i, p_char in enumerate(tail_subset):
            pos = 74 + i
            c = compute_class_baseline(pos)
            s = pos % L
            
            if wheels[c]['residues'][s] is None:
                c_char = ciphertext[pos]
                c_val = ord(c_char) - ord('A')
                p_val = ord(p_char) - ord('A')
                
                if wheels[c]['family'] == 'vigenere':
                    k_val = (c_val - p_val) % 26
                else:
                    k_val = (p_val + c_val) % 26
                
                wheels[c]['residues'][s] = k_val
        
        # Check closure
        plaintext, derived = derive_plaintext(ciphertext, wheels)
        closes = (derived == 97)
        
        results.append({
            'k': k,
            'closes': closes,
            'derived_total': derived
        })
        
        print(f"  k={k:2d}: {derived:2d}/97 derived, {'✓ CLOSES' if closes else '✗ incomplete'}")
    
    # Save results
    with open(f'L15/mts/MTS_L15_SUMMARY.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def forward_encode_check(L, wheels):
    """
    Forward encode: PT + wheels -> CT
    """
    print(f"\n=== Forward Encode Check (L={L}) ===")
    
    canonical_pt = load_canonical_plaintext()
    canonical_ct = load_ciphertext()
    
    # Encode
    encoded_ct = []
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        
        p_char = canonical_pt[i]
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['residues'][s] is not None:
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                c_val = (p_val + k_val) % 26
            else:  # beaufort
                c_val = (k_val - p_val) % 26
            
            encoded_ct.append(chr(c_val + ord('A')))
        else:
            encoded_ct.append('?')  # Should not happen if wheels complete
    
    encoded_ct_str = ''.join(encoded_ct)
    
    # Save
    with open(f'L15/forward_encode/CT.txt', 'w') as f:
        f.write(encoded_ct_str)
    
    # SHA check
    encoded_sha = hashlib.sha256(encoded_ct_str.encode()).hexdigest()
    canonical_sha = hashlib.sha256(canonical_ct.encode()).hexdigest()
    
    with open(f'L15/forward_encode/CT_SHA.txt', 'w') as f:
        f.write(f"Encoded SHA256: {encoded_sha}\n")
        f.write(f"Canonical SHA256: {canonical_sha}\n")
        f.write(f"Match: {'YES' if encoded_sha == canonical_sha else 'NO'}\n")
    
    print(f"  SHA match: {'✓' if encoded_sha == canonical_sha else '✗'}")
    
    return encoded_sha == canonical_sha

def reverse_derive_check(L, wheels):
    """
    Reverse derive: CT + wheels -> PT
    """
    print(f"\n=== Reverse Derive Check (L={L}) ===")
    
    ciphertext = load_ciphertext()
    canonical_pt = load_canonical_plaintext()
    
    # Derive
    derived_pt, _ = derive_plaintext(ciphertext, wheels)
    
    # Save
    with open(f'L15/rederive/PT.txt', 'w') as f:
        f.write(derived_pt)
    
    # SHA check
    derived_sha = hashlib.sha256(derived_pt.encode()).hexdigest()
    canonical_sha = hashlib.sha256(canonical_pt.encode()).hexdigest()
    
    with open(f'L15/rederive/PT_SHA.txt', 'w') as f:
        f.write(f"Derived SHA256: {derived_sha}\n")
        f.write(f"Canonical SHA256: {canonical_sha}\n")
        f.write(f"Match: {'YES' if derived_sha == canonical_sha else 'NO'}\n")
    
    print(f"  SHA match: {'✓' if derived_sha == canonical_sha else '✗'}")
    
    return derived_sha == canonical_sha

def main():
    """Run complete Fork B analysis"""
    print("\n" + "="*60)
    print("FORK B - L=15 COMPLETE ANALYSIS")
    print("="*60)
    
    ciphertext = load_ciphertext()
    
    # Step 1: L=15 anchors only
    wheels_15, pt_15_anchors, derived_15 = analyze_L_period(15, 'L15/anchors_only')
    
    # Step 2: L=17 anchors only
    wheels_17, pt_17_anchors, derived_17 = analyze_L_period(17, 'L17/anchors_only')
    
    # Step 3: Canonical tail fit test
    pt_15_full, derived_15_full = test_canonical_tail_fit(15, wheels_15, 'L15/anchors_plus_tail')
    pt_17_full, derived_17_full = test_canonical_tail_fit(17, wheels_17, 'L17/anchors_plus_tail')
    
    # Step 3.5: Minimal tail analysis (L=15 only)
    minimal_results = test_minimal_tail_subsets(15, ciphertext)
    
    # Step 4: Forward/reverse checks for L=15
    # Need complete wheels for this
    anchors = get_anchors()
    wheels_15_complete, _ = build_wheels_from_anchors(15, ciphertext, anchors)
    canonical_pt = load_canonical_plaintext()
    canonical_tail = canonical_pt[74:97]
    
    # Add full tail to make wheels complete
    for i, p_char in enumerate(canonical_tail):
        pos = 74 + i
        c = compute_class_baseline(pos)
        s = pos % 15
        
        if wheels_15_complete[c]['residues'][s] is None:
            c_char = ciphertext[pos]
            c_val = ord(c_char) - ord('A')
            p_val = ord(p_char) - ord('A')
            
            if wheels_15_complete[c]['family'] == 'vigenere':
                k_val = (c_val - p_val) % 26
            else:
                k_val = (p_val + c_val) % 26
            
            wheels_15_complete[c]['residues'][s] = k_val
    
    forward_ok = forward_encode_check(15, wheels_15_complete)
    reverse_ok = reverse_derive_check(15, wheels_15_complete)
    
    # Step 5: Summary JSON
    summary = {
        'L15': {
            'anchors_only': {
                'derived': derived_15,
                'unknown': 97 - derived_15
            },
            'anchors_plus_tail': {
                'derived': derived_15_full,
                'unknown': 97 - derived_15_full
            }
        },
        'L17': {
            'anchors_only': {
                'derived': derived_17,
                'unknown': 97 - derived_17
            },
            'anchors_plus_tail': {
                'derived': derived_17_full,
                'unknown': 97 - derived_17_full
            }
        }
    }
    
    with open('COMPARE/L_SUMMARY.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"\nL=15:")
    print(f"  Anchors only: {derived_15}/97")
    print(f"  With tail: {derived_15_full}/97")
    print(f"  Forward encode: {'✓' if forward_ok else '✗'}")
    print(f"  Reverse derive: {'✓' if reverse_ok else '✗'}")
    
    print(f"\nL=17:")
    print(f"  Anchors only: {derived_17}/97")
    print(f"  With tail: {derived_17_full}/97")
    
    print("\n✅ Analysis complete. Check output directories for details.")

if __name__ == "__main__":
    main()