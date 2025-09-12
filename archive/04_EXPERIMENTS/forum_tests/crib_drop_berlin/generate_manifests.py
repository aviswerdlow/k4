#!/usr/bin/env python3
"""Generate MANIFEST.sha256 for each test case directory"""

import os
import hashlib
import json

def sha256_file(filepath):
    """Calculate SHA-256 hash of a file"""
    if not os.path.exists(filepath):
        return None
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_manifest(case_dir):
    """Generate MANIFEST.sha256 for a test case directory"""
    
    # Files to include in manifest (in order)
    files = [
        "anchors.json",
        "WHEELS.json",
        "derived_pt.txt",
        "EXPLAIN_63_73.txt",
        "RESULT.json",
        "RECEIPTS.json"
    ]
    
    manifest_lines = []
    manifest_lines.append("# SHA-256 checksums for crib drop test artifacts")
    manifest_lines.append(f"# Test case: {os.path.basename(case_dir)}")
    manifest_lines.append("# Generated for auditor verification")
    manifest_lines.append("")
    
    for filename in files:
        filepath = os.path.join(case_dir, filename)
        if os.path.exists(filepath):
            hash_val = sha256_file(filepath)
            if hash_val:
                manifest_lines.append(f"{hash_val}  {filename}")
        else:
            print(f"Warning: {filename} not found in {case_dir}")
    
    # Write manifest
    manifest_path = os.path.join(case_dir, "MANIFEST.sha256")
    with open(manifest_path, 'w') as f:
        f.write('\n'.join(manifest_lines) + '\n')
    
    print(f"Created {manifest_path}")
    return manifest_path

def main():
    base_dir = "04_EXPERIMENTS/forum_tests/crib_drop_berlin"
    
    cases = [
        "drop_berlin",
        "drop_clock", 
        "drop_both",
        "drop_berlin_single_letter"
    ]
    
    for case in cases:
        case_dir = os.path.join(base_dir, case)
        if os.path.exists(case_dir):
            generate_manifest(case_dir)
        else:
            print(f"Error: {case_dir} not found")
    
    print("\nAll MANIFEST.sha256 files created!")

if __name__ == "__main__":
    main()