#!/usr/bin/env python3
"""
Seam-free test matrix runner
Executes Test A and Test B for GRID-only tail flexibility experiments
"""

import json
import csv
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None):
    """Run shell command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def run_seam_free_test(test_name, candidates, route_whitelist, base_dir):
    """Run a seam-free test with given parameters"""
    print(f"\n🧪 Running {test_name}")
    print(f"   Candidates: {candidates}")
    print(f"   Routes: {route_whitelist}")
    
    results = []
    
    # Update policy with route whitelist
    policy_path = base_dir / "POLICY.seamfree.json"
    policy = load_json(policy_path)
    policy['model_class']['route_whitelist'] = route_whitelist
    
    # Write test-specific policy
    test_policy_path = base_dir / f"runs/20250903/POLICY.{test_name}.json"
    with open(test_policy_path, 'w') as f:
        json.dump(policy, f, indent=2)
    
    for cand_label, route_id in candidates.items():
        print(f"  → Testing {cand_label} ({route_id})")
        
        # Set up paths
        results_base = Path("../../results/GRID_ONLY")
        cand_dir = results_base / cand_label
        out_dir = base_dir / f"runs/20250903/{cand_label}_{route_id}"
        out_dir.mkdir(exist_ok=True)
        
        # Check if candidate files exist
        pt_file = cand_dir / "plaintext_97.txt"
        proof_file = cand_dir / "proof_digest.json"
        
        if not pt_file.exists() or not proof_file.exists():
            print(f"    ❌ Missing files for {cand_label}")
            results.append({
                'test': test_name,
                'label': cand_label, 
                'route_id': route_id,
                'encrypts_to_ct': False,
                'near_cov': 0.0,
                'near_f': 0,
                'AND_pass': False,
                'p_cov_holm': 1.0,
                'p_fw_holm': 1.0,
                'tail_75_96': 'ERROR_MISSING_FILES',
                'publishable': False
            })
            continue
        
        # Run seam-free confirmation
        cmd = f"""python3 {base_dir}/scripts/seam_free_confirm.py \\
            --ct {base_dir}/data/ciphertext_97.txt \\
            --pt {pt_file} \\
            --proof {proof_file} \\
            --cuts {base_dir}/data/canonical_cuts.json \\
            --fwords {base_dir}/data/function_words.txt \\
            --calib {base_dir}/data/calibration/calib_97_perplexity.json \\
            --pos-trigrams {base_dir}/data/calibration/pos_trigrams.json \\
            --pos-threshold {base_dir}/data/calibration/pos_threshold.txt \\
            --policy {test_policy_path} \\
            --out {out_dir}"""
        
        success, stdout, stderr = run_command(cmd, cwd=base_dir)
        
        if not success:
            print(f"    ❌ Command failed: {stderr}")
            tail_result = "ERROR_EXECUTION_FAILED"
            publishable = False
        else:
            # Extract results from output files
            try:
                coverage_data = load_json(out_dir / "coverage_report.json")
                phrase_data = load_json(out_dir / "phrase_gate_report.json")  
                holm_data = load_json(out_dir / "holm_report_canonical.json")
                
                with open(out_dir / "tail_75_96.txt", 'r') as f:
                    tail_result = f.read().strip()
                
                encrypts_to_ct = coverage_data.get('encrypts_to_ct', False)
                near_cov = coverage_data.get('near_gate', {}).get('coverage', 0.0)
                near_f = coverage_data.get('near_gate', {}).get('f_words', 0)
                AND_pass = phrase_data.get('and_pass', False)
                p_cov_holm = holm_data.get('holm_adj_p', {}).get('coverage', 1.0)
                p_fw_holm = holm_data.get('holm_adj_p', {}).get('f_words', 1.0)
                publishable = holm_data.get('publishable', False)
                
            except Exception as e:
                print(f"    ❌ Failed to parse results: {e}")
                tail_result = "ERROR_PARSE_FAILED"
                encrypts_to_ct = False
                near_cov = 0.0
                near_f = 0
                AND_pass = False
                p_cov_holm = 1.0
                p_fw_holm = 1.0
                publishable = False
        
        results.append({
            'test': test_name,
            'label': cand_label,
            'route_id': route_id, 
            'encrypts_to_ct': encrypts_to_ct,
            'near_cov': near_cov,
            'near_f': near_f,
            'AND_pass': AND_pass,
            'p_cov_holm': p_cov_holm,
            'p_fw_holm': p_fw_holm,
            'tail_75_96': tail_result,
            'publishable': publishable
        })
        
        status = "✅" if publishable else "❌"
        print(f"    {status} {cand_label}: tail='{tail_result}' publishable={publishable}")
    
    return results

def main():
    """Run seam-free test matrix"""
    base_dir = Path(__file__).parent.parent
    
    print("🔬 K4 Seam-Free Tail Flexibility Experiments")
    print("=" * 50)
    
    # Test A: GRID winner vs runner-up (isolated routes)
    test_a_results = run_seam_free_test(
        "TestA_GRID_isolated",
        {"cand_005": "GRID_W14_ROWS", "cand_004": "GRID_W10_NW"},
        ["GRID_W14_ROWS", "GRID_W10_NW"],  # Only allow their specific routes
        base_dir
    )
    
    # Test B: GRID broadened (multiple route options)  
    test_b_results = run_seam_free_test(
        "TestB_GRID_broadened", 
        {"cand_005": "GRID_W14_ROWS", "cand_004": "GRID_W10_NW"},
        ["GRID_W10_NW", "GRID_W14_ROWS", "GRID_W10_NE", "GRID_W14_NE", "GRID_W12_ROWS", "GRID_W12_BOU"],
        base_dir
    )
    
    # Combine results
    all_results = test_a_results + test_b_results
    
    # Write CSV summary
    summary_file = base_dir / "runs/20250903/summary.csv"
    with open(summary_file, 'w', newline='') as f:
        fieldnames = ['test', 'label', 'route_id', 'encrypts_to_ct', 'near_cov', 'near_f', 
                     'AND_pass', 'p_cov_holm', 'p_fw_holm', 'tail_75_96', 'publishable']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    # Write JSON summary
    summary_json = base_dir / "runs/20250903/summary.json"
    with open(summary_json, 'w') as f:
        json.dump({
            'experiment': 'seam_free_tail_flexibility',
            'date': datetime.now().isoformat(),
            'tests_run': ['TestA_GRID_isolated', 'TestB_GRID_broadened'],
            'results': all_results
        }, f, indent=2)
    
    # Analysis
    print(f"\n📊 Results Summary")
    print("-" * 30)
    
    published_tails = set()
    for result in all_results:
        if result['publishable']:
            published_tails.add(result['tail_75_96'])
            print(f"✅ {result['test']}: {result['label']} → '{result['tail_75_96']}'")
        else:
            print(f"❌ {result['test']}: {result['label']} → FAILED")
    
    print(f"\n🎯 Tail Analysis:")
    if len(published_tails) == 0:
        print("   No publishable candidates found")
    elif len(published_tails) == 1:
        tail = list(published_tails)[0]
        print(f"   Unique tail across all publishable results: '{tail}'")
        print("   → Tail appears cryptographically forced by ciphertext + policy")
    else:
        print(f"   Multiple tails found: {published_tails}")
        print("   → Tail flexibility confirmed - not uniquely determined by CT")
    
    print(f"\n📁 Summary written to: {summary_file}")
    return len(published_tails)

if __name__ == '__main__':
    unique_tail_count = main()
    sys.exit(0 if unique_tail_count <= 1 else 1)  # Exit code indicates tail stability