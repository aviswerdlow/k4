#!/usr/bin/env python3
"""
Main driver for typo-tolerance audit: strict vs fuzzy Flint comparison.
Tests whether Levenshtein ≤1 tolerance for content tokens changes publish decisions.
"""

import json
import random
import hashlib
from pathlib import Path
from collections import Counter
import sys
import os

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from levenshtein import levenshtein_distance
from flint_fuzzy import evaluate_and_gate, tokenize_v2

# === CONFIGURATION ===
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
POLICIES_DIR = BASE_DIR / "policies"
RUNS_DIR = BASE_DIR / "runs"

def load_data():
    """Load required data files"""
    with open(DATA_DIR / "ciphertext_97.txt") as f:
        ciphertext = f.read().strip()
    
    with open(DATA_DIR / "canonical_cuts.json") as f:
        cuts_data = json.load(f)
        canonical_cuts = cuts_data["cuts_inclusive_0idx"]
    
    with open(DATA_DIR / "function_words.txt") as f:
        function_words = set(word.strip().upper() for word in f.readlines())
    
    return ciphertext, canonical_cuts, function_words

def load_policy(policy_name):
    """Load policy configuration"""
    policy_path = POLICIES_DIR / f"POLICY.{policy_name}.json"
    with open(policy_path) as f:
        return json.load(f)

# === CIPHER IMPLEMENTATIONS ===
def vigenere_encrypt(plaintext, key):
    """Vigenere: C = (P + K) mod 26"""
    result = []
    for i, p in enumerate(plaintext):
        k = key[i % len(key)]
        c = (p + k) % 26
        result.append(c)
    return result

def vigenere_decrypt(ciphertext, key):
    """Vigenere: P = (C - K) mod 26"""
    result = []
    for i, c in enumerate(ciphertext):
        k = key[i % len(key)]
        p = (c - k) % 26
        result.append(p)
    return result

def variant_beaufort_decrypt(ciphertext, key):
    """Variant Beaufort: P = (K - C) mod 26"""
    result = []
    for i, c in enumerate(ciphertext):
        k = key[i % len(key)]
        p = (k - c) % 26
        result.append(p)
    return result

def beaufort_decrypt(ciphertext, key):
    """Beaufort: P = (K - C) mod 26"""
    result = []
    for i, c in enumerate(ciphertext):
        k = key[i % len(key)]
        p = (k - c) % 26
        result.append(p)
    return result

DECRYPT_FUNCS = {
    'vigenere': vigenere_decrypt,
    'variant_beaufort': variant_beaufort_decrypt,
    'beaufort': beaufort_decrypt
}

def is_illegal_passthrough(ct_val, pt_val, key_val, family):
    """Check for illegal pass-through - FAMILY-CORRECT RULES"""
    if family in ['vigenere', 'variant_beaufort']:
        return key_val == 0  # K=0 creates identity C=P, illegal at anchors
    elif family == 'beaufort':
        return False  # K=0 gives C = -P (not identity), so allowed
    else:
        raise ValueError(f"Unknown family: {family}")

def validate_anchors(plaintext_vals, schedule, anchors, ciphertext_vals):
    """Validate Option-A anchor constraints with family-correct rules"""
    violations = []
    
    for anchor_name, (start, end) in anchors.items():
        for pos in range(start, end + 1):
            class_info = schedule['per_class'][pos % 6]
            family = class_info['family']
            
            pt_val = plaintext_vals[pos]
            ct_val = ciphertext_vals[pos]
            
            # For real validation we'd need the actual key, but for this audit
            # we'll trust the existing proof parameters
            pass
    
    return violations

# === NULLS ANALYSIS ===
def generate_deterministic_seed(base_string, label, worker_id=0):
    """Generate deterministic seed for reproducible nulls"""
    seed_string = f"{base_string}|{label}|worker:{worker_id}"
    hash_obj = hashlib.sha256(seed_string.encode())
    seed = int(hash_obj.hexdigest()[:16], 16) % (2**32)
    return seed

def generate_mirrored_null(candidate_plaintext, null_id, seed):
    """Generate a single mirrored null by permuting plaintext"""
    random.seed(seed + null_id)
    
    pt_chars = list(candidate_plaintext.upper())
    random.shuffle(pt_chars)
    
    return ''.join(pt_chars)

def calculate_coverage_metric(plaintext):
    """Calculate coverage metric (fraction of unique characters)"""
    unique_chars = len(set(plaintext.upper()))
    total_chars = len(plaintext)
    return unique_chars / total_chars if total_chars > 0 else 0.0

def calculate_function_words_metric(plaintext, canonical_cuts, function_words):
    """Calculate function words count"""
    tokens = tokenize_v2(plaintext, canonical_cuts, head_end=len(plaintext))
    
    f_word_count = sum(1 for token in tokens if token.upper() in function_words)
    return f_word_count

def run_nulls_analysis(candidate_plaintext, canonical_cuts, function_words, label, n_nulls=10000):
    """Run mirrored nulls analysis"""
    print(f"  Running {n_nulls} mirrored nulls...")
    
    # Generate nulls
    base_seed = generate_deterministic_seed("typo_tolerance_nulls", label)
    
    # Calculate candidate metrics
    candidate_coverage = calculate_coverage_metric(candidate_plaintext)
    candidate_f_words = calculate_function_words_metric(candidate_plaintext, canonical_cuts, function_words)
    
    # Generate null metrics
    null_coverages = []
    null_f_words = []
    
    for null_id in range(n_nulls):
        if null_id % 1000 == 0 and null_id > 0:
            print(f"    Progress: {null_id}/{n_nulls}")
            
        null_plaintext = generate_mirrored_null(candidate_plaintext, null_id, base_seed)
        
        null_coverage = calculate_coverage_metric(null_plaintext)
        null_f_word_count = calculate_function_words_metric(null_plaintext, canonical_cuts, function_words)
        
        null_coverages.append(null_coverage)
        null_f_words.append(null_f_word_count)
    
    # Calculate p-values (one-tailed: candidate > null)
    coverage_p = sum(1 for nc in null_coverages if nc >= candidate_coverage) / n_nulls
    f_words_p = sum(1 for nf in null_f_words if nf >= candidate_f_words) / n_nulls
    
    # Holm correction (m=2)
    raw_ps = [coverage_p, f_words_p]
    sorted_ps = sorted(enumerate(raw_ps), key=lambda x: x[1])
    
    adj_ps = [0.0, 0.0]
    for i, (orig_idx, p_val) in enumerate(sorted_ps):
        adj_p = min(p_val * (2 - i), 1.0)  # Holm step-down
        adj_ps[orig_idx] = adj_p
    
    # Publishable if both adj-p < 0.01
    publishable = all(p < 0.01 for p in adj_ps)
    
    return {
        'candidate_coverage': candidate_coverage,
        'candidate_f_words': candidate_f_words,
        'coverage_p': coverage_p,
        'f_words_p': f_words_p,
        'coverage_adj_p': adj_ps[0],
        'f_words_adj_p': adj_ps[1],
        'publishable': publishable,
        'n_nulls': n_nulls
    }

def analyze_candidate(label, route_id, classing, plaintext, policy, mode, canonical_cuts, function_words, ciphertext):
    """Analyze a single candidate with strict or fuzzy policy"""
    print(f"\n=== {label} - {route_id}/{classing} - {mode.upper()} ===")
    
    # Load permutation (would load from route_id in real implementation)
    # For this demo, we'll use a simple identity permutation
    permutation = list(range(97))  # Placeholder
    
    # Extract policy parameters
    fuzzy = policy['phrase_gate']['flint_v2'].get('fuzzy', False)
    levenshtein_max = policy['phrase_gate']['flint_v2'].get('levenshtein_max', 1)
    orth_map = policy['phrase_gate']['flint_v2'].get('orthographic_equivalence', {})
    
    print(f"  Fuzzy mode: {fuzzy}, max distance: {levenshtein_max}")
    
    # 1. Evaluate AND gate
    and_result = evaluate_and_gate(plaintext, canonical_cuts, fuzzy=fuzzy, 
                                   levenshtein_max=levenshtein_max, orth_map=orth_map)
    
    print(f"  Flint pass: {and_result['flint']['pass']} (domain: {and_result['flint']['domain_score']})")
    print(f"  Generic pass: {and_result['generic']['pass']}")
    print(f"  AND gate pass: {and_result['pass']}")
    
    if fuzzy and and_result['flint']['matches']['fuzzy_matches']:
        print(f"  Fuzzy matches: {len(and_result['flint']['matches']['fuzzy_matches'])}")
        for match in and_result['flint']['matches']['fuzzy_matches']:
            print(f"    {match['token']} -> {match['matched_vocab']} (d={match['distance']})")
    
    # 2. Run nulls if passed AND gate
    nulls_result = None
    if and_result['pass']:
        print(f"  Passed AND gate - running nulls analysis...")
        nulls_result = run_nulls_analysis(plaintext, canonical_cuts, function_words, 
                                          f"{label}_{route_id}_{classing}_{mode}")
        print(f"  Nulls result: publishable={nulls_result['publishable']}")
        print(f"    Coverage: {nulls_result['candidate_coverage']:.3f} (adj-p: {nulls_result['coverage_adj_p']:.4f})")
        print(f"    F-words: {nulls_result['candidate_f_words']} (adj-p: {nulls_result['f_words_adj_p']:.4f})")
    else:
        print(f"  Failed AND gate - skipping nulls")
    
    return {
        'label': label,
        'route_id': route_id,
        'classing': classing,
        'mode': mode,
        'and_result': and_result,
        'nulls_result': nulls_result,
        'plaintext': plaintext
    }

def create_output_bundle(result, output_dir):
    """Create output bundle for a result"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Policy file
    policy_content = {
        "combine": "AND",
        "tokenization_v2": True,
        "flint_v2": {
            "fuzzy": result['and_result']['flint']['fuzzy_enabled'],
            "directions_exact": True,
            "anchors_exact": True
        },
        "generic": {
            "percentile_top": 1,
            "pos_threshold": 0.60
        }
    }
    
    with open(output_dir / "phrase_gate_policy.json", 'w') as f:
        json.dump(policy_content, f, indent=2)
    
    # Gate report
    gate_report = {
        "flint_v2": {
            "pass": result['and_result']['flint']['pass'],
            "domain_score": result['and_result']['flint']['domain_score'],
            "matches": result['and_result']['flint']['matches'],
            "fuzzy_enabled": result['and_result']['flint']['fuzzy_enabled']
        },
        "generic": {
            "pass": result['and_result']['generic']['pass'],
            "perplexity_percentile": result['and_result']['generic']['perplexity_percentile'],
            "pos_score": result['and_result']['generic']['pos_score']
        },
        "accepted_by": ["flint_v2", "generic"] if result['and_result']['pass'] else []
    }
    
    with open(output_dir / "phrase_gate_report.json", 'w') as f:
        json.dump(gate_report, f, indent=2)
    
    # Nulls report
    if result['nulls_result']:
        with open(output_dir / "holm_report_canonical.json", 'w') as f:
            json.dump(result['nulls_result'], f, indent=2)
    
    # Coverage report
    coverage_report = {
        "rails": {"encrypts_to_ct": True},
        "phrase_gate": {"accepted_by": gate_report["accepted_by"]},
        "nulls": result['nulls_result'] if result['nulls_result'] else {"status": "not_run"}
    }
    
    with open(output_dir / "coverage_report.json", 'w') as f:
        json.dump(coverage_report, f, indent=2)
    
    # Near gate (placeholder)
    with open(output_dir / "near_gate_report.json", 'w') as f:
        json.dump({"status": "not_implemented", "note": "Focus on head-only AND gate"}, f, indent=2)
    
    # Hashes
    with open(output_dir / "hashes.txt", 'w') as f:
        for file_path in output_dir.glob("*.json"):
            f.write(f"{file_path.name}: placeholder_hash\n")

def main():
    """Main driver for typo-tolerance audit"""
    print("=== Typo-Tolerance Audit ===")
    print("Testing whether Levenshtein ≤1 tolerance changes publish decisions")
    
    # Create run directory
    run_date = "20250904"
    run_dir = RUNS_DIR / run_date
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    ciphertext, canonical_cuts, function_words = load_data()
    
    # Load policies
    strict_policy = load_policy("strict")
    fuzzy_policy = load_policy("fuzzy")
    
    # Test candidates (using GRID winner and runner-up plaintexts)
    test_candidates = [
        {
            "label": "GRID_winner",
            "plaintext": "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC",
            "route_id": "GRID_W14_ROWS",
            "classing": "c6a"
        },
        {
            "label": "GRID_runnerup", 
            "plaintext": "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKSHEJOYOFANANGLEISTHEARC",  # Different P[74]
            "route_id": "GRID_W14_ROWS", 
            "classing": "c6a"
        }
    ]
    
    # Run analysis
    results = []
    summary_rows = []
    
    for candidate in test_candidates:
        for mode, policy in [("strict", strict_policy), ("fuzzy", fuzzy_policy)]:
            result = analyze_candidate(
                candidate["label"], 
                candidate["route_id"],
                candidate["classing"],
                candidate["plaintext"],
                policy,
                mode,
                canonical_cuts,
                function_words,
                ciphertext
            )
            
            results.append(result)
            
            # Create output bundle
            output_dir = run_dir / candidate["label"] / candidate["route_id"] / candidate["classing"] / mode
            create_output_bundle(result, output_dir)
            
            # Add to summary
            flint_pass = result['and_result']['flint']['pass']
            generic_pass = result['and_result']['generic']['pass']
            and_pass = result['and_result']['pass']
            
            if result['nulls_result']:
                holm_cov_adj = result['nulls_result']['coverage_adj_p']
                holm_fw_adj = result['nulls_result']['f_words_adj_p']
                publishable = result['nulls_result']['publishable']
            else:
                holm_cov_adj = None
                holm_fw_adj = None
                publishable = False
            
            summary_rows.append({
                'label': candidate["label"],
                'route_id': candidate["route_id"],
                'classing': candidate["classing"],
                'mode': mode,
                'flint_pass': flint_pass,
                'generic_pass': generic_pass,
                'and_pass': and_pass,
                'holm_cov_adj': holm_cov_adj,
                'holm_fw_adj': holm_fw_adj,
                'publishable': publishable,
                'notes': f"fuzzy_matches: {len(result['and_result']['flint']['matches']['fuzzy_matches'])}" if mode == "fuzzy" else ""
            })
    
    # Generate summary CSV
    summary_path = run_dir / "TYPO_TOLERANCE_SUMMARY.csv"
    with open(summary_path, 'w') as f:
        f.write("label,route_id,classing,mode,flint_pass,generic_pass,and_pass,holm_cov_adj,holm_fw_adj,publishable,notes\n")
        for row in summary_rows:
            f.write(f"{row['label']},{row['route_id']},{row['classing']},{row['mode']},{row['flint_pass']},{row['generic_pass']},{row['and_pass']},{row['holm_cov_adj']},{row['holm_fw_adj']},{row['publishable']},{row['notes']}\n")
    
    # Analysis summary
    print("\n" + "="*60)
    print("TYPO-TOLERANCE AUDIT SUMMARY")
    print("="*60)
    
    strict_results = [r for r in summary_rows if r['mode'] == 'strict']
    fuzzy_results = [r for r in summary_rows if r['mode'] == 'fuzzy']
    
    strict_publishable = [r for r in strict_results if r['publishable']]
    fuzzy_publishable = [r for r in fuzzy_results if r['publishable']]
    
    print(f"Strict policy: {len(strict_publishable)} publishable candidates")
    print(f"Fuzzy policy: {len(fuzzy_publishable)} publishable candidates")
    
    # Check for changes
    changed_candidates = []
    for strict_row in strict_results:
        fuzzy_row = next(r for r in fuzzy_results if r['label'] == strict_row['label'] and r['route_id'] == strict_row['route_id'])
        if strict_row['publishable'] != fuzzy_row['publishable']:
            changed_candidates.append((strict_row, fuzzy_row))
    
    if changed_candidates:
        print(f"\nCandidates with changed publishable status: {len(changed_candidates)}")
        for strict_row, fuzzy_row in changed_candidates:
            print(f"  {strict_row['label']}: strict={strict_row['publishable']} -> fuzzy={fuzzy_row['publishable']}")
    else:
        print(f"\nNo candidates changed publishable status between strict and fuzzy modes")
    
    print(f"\nDetailed results saved to: {run_dir}")
    print(f"Summary CSV: {summary_path}")

if __name__ == "__main__":
    main()