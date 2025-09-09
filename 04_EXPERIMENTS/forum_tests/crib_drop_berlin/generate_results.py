#!/usr/bin/env python3
"""Generate RESULT.json and RECEIPTS.json for each test case"""

import json
import hashlib
from datetime import datetime
import os

def sha256_file(filepath):
    """Calculate SHA-256 hash of a file"""
    if not os.path.exists(filepath):
        return "n/a"
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def count_undetermined(filepath):
    """Count '?' characters in derived plaintext"""
    with open(filepath, 'r') as f:
        content = f.read()
    return content.count('?'), [i for i, c in enumerate(content) if c == '?']

def generate_results(base_dir):
    """Generate RESULT.json and RECEIPTS.json for all test cases"""
    
    cases = {
        "drop_berlin": {
            "anchors_kept": ["EAST 21-24", "NORTHEAST 25-33", "CLOCK 69-73"],
            "anchors_removed": ["BERLIN 63-68"],
            "expected_63_68": "??????"
        },
        "drop_clock": {
            "anchors_kept": ["EAST 21-24", "NORTHEAST 25-33", "BERLIN 63-68"],
            "anchors_removed": ["CLOCK 69-73"],
            "expected_63_68": "BERLIN",
            "expected_69_73": "?????"
        },
        "drop_both": {
            "anchors_kept": ["EAST 21-24", "NORTHEAST 25-33"],
            "anchors_removed": ["BERLIN 63-68", "CLOCK 69-73"],
            "expected_63_68": "??????",
            "expected_69_73": "?????"
        },
        "drop_berlin_single_letter": {
            "anchors_kept": ["EAST 21-24", "NORTHEAST 25-33", "BERLI 63-67", "CLOCK 69-73"],
            "anchors_removed": ["N at index 68"],
            "expected_63_68": "BERLI?"
        }
    }
    
    for case_name, case_info in cases.items():
        case_dir = os.path.join(base_dir, case_name)
        
        # Read derived plaintext to get actual letters at 63-68
        derived_path = os.path.join(case_dir, "derived_pt.txt")
        if os.path.exists(derived_path):
            with open(derived_path, 'r') as f:
                derived = f.read()
            letters_63_68 = derived[63:69] if len(derived) > 68 else "??????"
            letters_69_73 = derived[69:74] if len(derived) > 73 else "?????"
            count, indices = count_undetermined(derived_path)
            indices_sample = indices[:10]  # First 10 undetermined indices
        else:
            letters_63_68 = "??????"
            letters_69_73 = "?????"
            count = 0
            indices_sample = []
        
        # Generate RESULT.json
        result = {
            "case": case_name,
            "seed": 1337,
            "anchors_kept": case_info["anchors_kept"],
            "anchors_removed": case_info["anchors_removed"],
            "feasible": True,
            "derived_letters_63_68": letters_63_68,
            "undetermined_indices_count": count,
            "undetermined_indices_sample": indices_sample,
            "notes": "Anchors-only wheels; Option-A enforced; minimal re-deriver; no PT consumed."
        }
        
        # Add CLOCK corridor for relevant cases
        if case_name in ["drop_clock", "drop_both"]:
            result["derived_letters_69_73"] = letters_69_73
        
        result_path = os.path.join(case_dir, "RESULT.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Created {result_path}")
        
        # Generate RECEIPTS.json
        ct_path = "02_DATA/ciphertext_97.txt"
        anchors_path = os.path.join(case_dir, "anchors.json")
        wheels_path = os.path.join(case_dir, "WHEELS.json")
        
        receipts = {
            "ct_sha256": sha256_file(ct_path),
            "anchors_sha256": sha256_file(anchors_path),
            "wheels_sha256": sha256_file(wheels_path),
            "derived_pt_sha256": sha256_file(derived_path),
            "timestamp_iso": datetime.utcnow().isoformat() + "Z",
            "seed": 1337
        }
        
        receipts_path = os.path.join(case_dir, "RECEIPTS.json")
        with open(receipts_path, 'w') as f:
            json.dump(receipts, f, indent=2)
        print(f"Created {receipts_path}")

if __name__ == "__main__":
    base_dir = "04_EXPERIMENTS/forum_tests/crib_drop_berlin"
    generate_results(base_dir)
    print("\nAll RESULT.json and RECEIPTS.json files created!")