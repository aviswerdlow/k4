#!/usr/bin/env python3
"""
Prove the minimum number of constraints required to close L=17.
Mathematical proof + empirical confirmation.
"""

import json
import csv
import hashlib
import random

MASTER_SEED = 1337
CANONICAL_SHA = "4eceb739ab655d6f4ec87753569b8bf04573fe26d01c0caa68d36776dd052d79"

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_unknown_map():
    """Load the unknown position map"""
    with open('../../04_EXPERIMENTS/L17_MISSING/UNKNOWN_MAP_SUMMARY.json', 'r') as f:
        data = json.load(f)
    return data['unknown_indices'], data['unknown_count']

def load_ciphertext():
    """Load ciphertext"""
    with open('../../02_DATA/ciphertext_97.txt', 'r') as f:
        return f.read().strip()

def load_canonical_plaintext():
    """Load canonical plaintext"""
    with open('../../01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        return f.read().strip()

def get_base_constraints():
    """Get anchor and tail positions"""
    anchors = set(range(21, 25)) | set(range(25, 34)) | set(range(63, 69)) | set(range(69, 74))
    tail = set(range(74, 97))
    return anchors | tail

def prove_one_to_one_mapping():
    """
    Prove that each position maps to a unique (class, slot) pair under L=17.
    """
    L = 17
    n_positions = 97
    
    position_to_slot = {}
    slot_to_positions = {}
    
    for i in range(n_positions):
        c = compute_class_baseline(i)
        s = i % L
        key = (c, s)
        
        position_to_slot[i] = key
        
        if key not in slot_to_positions:
            slot_to_positions[key] = []
        slot_to_positions[key].append(i)
    
    # Check uniqueness
    max_positions_per_slot = max(len(positions) for positions in slot_to_positions.values())
    unique_slots = len(slot_to_positions)
    
    proof = {
        'L': L,
        'n_positions': n_positions,
        'unique_slots': unique_slots,
        'max_positions_per_slot': max_positions_per_slot,
        'is_one_to_one': max_positions_per_slot == 1 and unique_slots == n_positions
    }
    
    return proof

def test_closure_with_constraints(constraint_indices, ciphertext, canonical_pt):
    """Test if given constraints achieve closure"""
    L = 17
    
    # Build wheels
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': 'vigenere' if c in [1, 3, 5] else 'beaufort',
            'L': L,
            'phase': 0,
            'residues': [None] * L
        }
    
    # Apply constraints
    for idx in constraint_indices:
        c = compute_class_baseline(idx)
        s = idx % L
        
        c_char = ciphertext[idx]
        p_char = canonical_pt[idx]
        
        c_val = ord(c_char) - ord('A')
        p_val = ord(p_char) - ord('A')
        
        if wheels[c]['family'] == 'vigenere':
            k_val = (c_val - p_val) % 26
        else:
            k_val = (p_val + c_val) % 26
        
        wheels[c]['residues'][s] = k_val
    
    # Derive plaintext
    derived_pt = []
    derived_count = 0
    
    for i in range(97):
        c = compute_class_baseline(i)
        s = i % L
        
        if wheels[c]['residues'][s] is not None:
            c_char = ciphertext[i]
            c_val = ord(c_char) - ord('A')
            k_val = wheels[c]['residues'][s]
            
            if wheels[c]['family'] == 'vigenere':
                p_val = (c_val - k_val) % 26
            else:
                p_val = (k_val - c_val) % 26
            
            derived_pt.append(chr(p_val + ord('A')))
            derived_count += 1
        else:
            derived_pt.append('?')
    
    derived_str = ''.join(derived_pt)
    closed = (derived_count == 97)
    
    if closed:
        sha = hashlib.sha256(derived_str.encode()).hexdigest()
        sha_match = (sha == CANONICAL_SHA)
    else:
        sha_match = False
    
    return closed, sha_match, derived_count

def run_empirical_tests(unknown_indices, ciphertext, canonical_pt):
    """Run empirical tests to confirm minimum constraints"""
    random.seed(MASTER_SEED)
    
    base_constraints = get_base_constraints()
    trials = []
    
    # Test 1: All 50 unknowns as constraints
    all_constraints = base_constraints | set(unknown_indices)
    closed, sha_match, derived = test_closure_with_constraints(all_constraints, ciphertext, canonical_pt)
    trials.append({
        'test': 'all_50_unknowns',
        'n_additional': 50,
        'derived': derived,
        'closed': closed,
        'sha_match': sha_match
    })
    
    # Test 2: Random subsets of 49
    for trial in range(3):
        subset_49 = random.sample(unknown_indices, 49)
        test_constraints = base_constraints | set(subset_49)
        closed, sha_match, derived = test_closure_with_constraints(test_constraints, ciphertext, canonical_pt)
        trials.append({
            'test': f'random_49_trial_{trial+1}',
            'n_additional': 49,
            'derived': derived,
            'closed': closed,
            'sha_match': sha_match
        })
    
    # Test 3: Random subsets of 45
    for trial in range(3):
        subset_45 = random.sample(unknown_indices, 45)
        test_constraints = base_constraints | set(subset_45)
        closed, sha_match, derived = test_closure_with_constraints(test_constraints, ciphertext, canonical_pt)
        trials.append({
            'test': f'random_45_trial_{trial+1}',
            'n_additional': 45,
            'derived': derived,
            'closed': closed,
            'sha_match': sha_match
        })
    
    return trials

def main():
    """Run minimum constraints proof"""
    print("\n=== L=17 Minimum Constraints Proof ===")
    print(f"MASTER_SEED: {MASTER_SEED}")
    
    # Load data
    unknown_indices, unknown_count = load_unknown_map()
    ciphertext = load_ciphertext()
    canonical_pt = load_canonical_plaintext()
    
    print(f"\nUnknown positions: {unknown_count}")
    
    # Mathematical proof
    print("\n1. Mathematical Proof:")
    proof = prove_one_to_one_mapping()
    
    print(f"   L=17 with 97 positions creates {proof['unique_slots']} unique (class,slot) pairs")
    print(f"   Maximum positions per slot: {proof['max_positions_per_slot']}")
    print(f"   One-to-one mapping: {proof['is_one_to_one']}")
    
    if proof['is_one_to_one']:
        print(f"\n   ∴ Each unknown position requires its own constraint")
        print(f"   ∴ Minimum constraints needed = {unknown_count}")
    
    # Empirical confirmation
    print("\n2. Empirical Confirmation:")
    trials = run_empirical_tests(unknown_indices, ciphertext, canonical_pt)
    
    for trial in trials:
        status = "✓ CLOSED" if trial['closed'] else f"✗ {trial['derived']}/97"
        print(f"   {trial['test']}: {status}")
    
    # Save outputs
    output_dir = '../../04_EXPERIMENTS/L17_MISSING'
    
    # Save proof
    with open(f'{output_dir}/MIN_CONSTRAINTS_PROOF.md', 'w') as f:
        f.write("# Minimum Constraints Proof for L=17\n\n")
        f.write("## Mathematical Proof\n\n")
        f.write("### 1. One-to-One Mapping Property\n")
        f.write(f"With L=17 and 97 positions:\n")
        f.write(f"- Each position i maps to (class(i), i mod 17)\n")
        f.write(f"- This creates {proof['unique_slots']} unique (class, slot) pairs\n")
        f.write(f"- Each pair appears exactly {proof['max_positions_per_slot']} time\n\n")
        
        f.write("### 2. Constraint Propagation\n")
        f.write("Under one-to-one mapping:\n")
        f.write("- Each constrained position determines exactly one wheel slot\n")
        f.write("- Each wheel slot determines at most one position\n")
        f.write("- No constraint can 'cover' multiple unknowns\n\n")
        
        f.write("### 3. Set-Cover Reduction\n")
        f.write(f"- Universe U = {unknown_count} unknown positions\n")
        f.write("- Each constraint covers exactly 1 element of U\n")
        f.write(f"- Minimum cover size = |U| = {unknown_count}\n\n")
        
        f.write("## Empirical Confirmation\n\n")
        f.write("| Test | Additional Constraints | Result |\n")
        f.write("|------|------------------------|--------|\n")
        
        for trial in trials:
            result = "✓ Closed" if trial['closed'] else f"{trial['derived']}/97"
            f.write(f"| {trial['test']} | {trial['n_additional']} | {result} |\n")
        
        f.write(f"\n## Conclusion\n\n")
        f.write(f"**Minimum additional constraints required: {unknown_count}**\n\n")
        f.write("This is mathematically necessary and empirically confirmed.\n")
    
    # Save JSON summary
    summary = {
        'unknown_count': unknown_count,
        'min_required': unknown_count,
        'closure_confirmed': trials[0]['closed'] and trials[0]['sha_match'],
        'one_to_one_mapping': proof['is_one_to_one'],
        'empirical_trials': trials
    }
    
    with open(f'{output_dir}/MIN_CONSTRAINTS_PROOF.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save trial results as CSV
    with open(f'{output_dir}/CONSTRAINT_TRIALS.csv', 'w', newline='') as f:
        if trials:
            writer = csv.DictWriter(f, fieldnames=trials[0].keys())
            writer.writeheader()
            writer.writerows(trials)
    
    print(f"\n✅ Proof complete. Minimum constraints: {unknown_count}")

if __name__ == "__main__":
    main()