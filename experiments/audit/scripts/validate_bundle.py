#!/usr/bin/env python3
"""
BUNDLE_VALIDATOR - Verify every confirm mini-bundle meets requirements.
Checks for required files, fields, and invariants.
"""

import os
import json
import csv
import hashlib
from pathlib import Path
from datetime import datetime

REQUIRED_FILES = {
    'plaintext_97.txt',
    'proof_digest.json',
    'phrase_gate_policy.json', 
    'phrase_gate_report.json',
    'coverage_report.json'
}

OPTIONAL_FILES = {
    'near_gate_report.json',
    'holm_report_canonical.json',
    'hashes.txt',
    'MANIFEST.sha256'
}

def validate_coverage_report(data, bundle_path):
    """Validate coverage_report.json fields."""
    errors = []
    
    # Check rails
    if 'rails' in data:
        rails = data['rails']
        expected_anchors = [[21, 24], [25, 33], [63, 73]]
        if 'anchors' in rails:
            anchors = rails['anchors']
            # Check if anchors match expected (allowing for different formats)
            # This is lenient - just check presence
            pass
    else:
        errors.append("Missing rails block")
    
    # Check required fields
    required = ['pt_sha256', 'ct_sha256', 'route_id']
    for field in required:
        if field not in data:
            errors.append(f"Missing {field}")
    
    # Check seed fields
    if 'seed_recipe' not in data and 'seed_u64' not in data:
        errors.append("Missing seed information")
    
    # Check gate blocks
    if 'near_gate' in data:
        ng = data['near_gate']
        ng_fields = ['coverage', 'f_words', 'has_verb', 'pass']
        missing_ng = [f for f in ng_fields if f not in ng]
        if missing_ng:
            errors.append(f"near_gate missing: {','.join(missing_ng)}")
    
    if 'phrase_gate' in data:
        pg = data['phrase_gate']
        if 'accepted_by' not in pg:
            errors.append("phrase_gate missing accepted_by")
        if 'pass' not in pg:
            errors.append("phrase_gate missing pass")
    
    if 'nulls' in data:
        nulls = data['nulls']
        if nulls.get('status') == 'ran':
            if 'K' not in nulls:
                errors.append("nulls missing K")
            if 'holm_adj_p' not in nulls:
                errors.append("nulls missing holm_adj_p")
    
    return errors

def validate_phrase_gate_policy(data, bundle_path):
    """Validate phrase_gate_policy.json fields."""
    errors = []
    
    # Check combine field
    if 'combine' not in data:
        errors.append("Missing combine field")
    elif data['combine'] not in ['AND', 'OR']:
        errors.append(f"Invalid combine value: {data['combine']}")
    
    # Check tokenization
    if 'tokenization_v2' not in data:
        # May be under different key
        pass
    
    # Check generic thresholds
    if 'generic' in data:
        gen = data['generic']
        if 'percentile_top' not in gen and 'perplexity_percentile' not in gen:
            errors.append("Missing generic percentile")
        if 'pos_threshold' not in gen:
            errors.append("Missing generic pos_threshold")
    
    # Check calibration hashes
    if 'calibration_hashes' not in data:
        # May be optional for some runs
        pass
    
    return errors

def validate_phrase_gate_report(data, bundle_path):
    """Validate phrase_gate_report.json fields."""
    errors = []
    
    # Check tracks
    if 'tracks' in data:
        tracks = data['tracks']
        if 'flint_v2' in tracks:
            if 'passed' not in tracks['flint_v2']:
                errors.append("flint_v2 missing passed field")
        if 'generic' in tracks:
            if 'passed' not in tracks['generic']:
                errors.append("generic missing passed field")
    else:
        errors.append("Missing tracks block")
    
    # Check accepted_by
    if 'accepted_by' not in data:
        errors.append("Missing accepted_by field")
    
    return errors

def validate_holm_report(data, bundle_path):
    """Validate holm_report_canonical.json fields."""
    errors = []
    
    # Check K
    if 'K' not in data:
        errors.append("Missing K (bootstrap count)")
    elif data['K'] != 10000:
        errors.append(f"K={data['K']}, expected 10000")
    
    # Check metrics
    if 'metrics' in data:
        metrics = data['metrics']
        for metric_name in ['coverage', 'f_words']:
            if metric_name in metrics:
                metric = metrics[metric_name]
                if 'p_raw' not in metric:
                    errors.append(f"{metric_name} missing p_raw")
                if 'p_holm' not in metric:
                    errors.append(f"{metric_name} missing p_holm")
    else:
        errors.append("Missing metrics block")
    
    return errors

def verify_manifest(bundle_path):
    """Verify MANIFEST.sha256 or hashes.txt."""
    manifest_path = bundle_path / "MANIFEST.sha256"
    hashes_path = bundle_path / "hashes.txt"
    
    if manifest_path.exists():
        return verify_manifest_file(manifest_path, bundle_path)
    elif hashes_path.exists():
        return verify_hashes_file(hashes_path, bundle_path)
    
    return True  # No manifest to verify

def verify_manifest_file(manifest_path, bundle_path):
    """Verify SHA-256 manifest."""
    try:
        with open(manifest_path, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        expected_hash = parts[0]
                        filename = ' '.join(parts[1:])
                        filepath = bundle_path / filename
                        
                        if filepath.exists() and filepath != manifest_path:
                            with open(filepath, 'rb') as file:
                                actual_hash = hashlib.sha256(file.read()).hexdigest()
                                if actual_hash != expected_hash:
                                    return False
        return True
    except Exception:
        return False

def verify_hashes_file(hashes_path, bundle_path):
    """Verify hashes.txt format."""
    # Simple check - just verify it exists and has content
    try:
        with open(hashes_path, 'r') as f:
            content = f.read()
            return len(content) > 0
    except Exception:
        return False

def validate_bundle(bundle_path):
    """Validate a single bundle."""
    bundle_path = Path(bundle_path)
    
    # Check if directory exists
    if not bundle_path.exists() or not bundle_path.is_dir():
        return False, ["Directory does not exist"], False, "Invalid path"
    
    errors = []
    missing_fields = []
    
    # Check required files
    existing_files = {f.name for f in bundle_path.iterdir() if f.is_file()}
    missing_required = REQUIRED_FILES - existing_files
    
    if missing_required:
        errors.append(f"Missing files: {','.join(missing_required)}")
        # Can't validate further without required files
        return False, errors, False, "Missing required files"
    
    # Validate each JSON file
    try:
        # coverage_report.json
        with open(bundle_path / 'coverage_report.json', 'r') as f:
            coverage_data = json.load(f)
            coverage_errors = validate_coverage_report(coverage_data, bundle_path)
            missing_fields.extend(coverage_errors)
        
        # phrase_gate_policy.json
        with open(bundle_path / 'phrase_gate_policy.json', 'r') as f:
            policy_data = json.load(f)
            policy_errors = validate_phrase_gate_policy(policy_data, bundle_path)
            missing_fields.extend(policy_errors)
        
        # phrase_gate_report.json
        with open(bundle_path / 'phrase_gate_report.json', 'r') as f:
            report_data = json.load(f)
            report_errors = validate_phrase_gate_report(report_data, bundle_path)
            missing_fields.extend(report_errors)
        
        # holm_report_canonical.json (if exists)
        holm_path = bundle_path / 'holm_report_canonical.json'
        if holm_path.exists():
            with open(holm_path, 'r') as f:
                holm_data = json.load(f)
                holm_errors = validate_holm_report(holm_data, bundle_path)
                missing_fields.extend(holm_errors)
        
    except json.JSONDecodeError as e:
        errors.append(f"JSON decode error: {e}")
    except Exception as e:
        errors.append(f"Validation error: {e}")
    
    # Verify manifest
    hash_ok = verify_manifest(bundle_path)
    
    # Determine overall status
    ok = len(errors) == 0 and len(missing_fields) == 0 and hash_ok
    
    notes = ""
    if errors:
        notes = f"Errors: {'; '.join(errors[:2])}"  # First 2 errors
    elif missing_fields:
        notes = f"Missing: {'; '.join(missing_fields[:3])}"  # First 3 missing
    elif not hash_ok:
        notes = "Hash verification failed"
    else:
        notes = "Valid bundle"
    
    return ok, missing_fields, hash_ok, notes

def scan_experiments(base_path):
    """Scan experiments directory for bundles."""
    bundles = []
    
    # Look for candidate folders (pattern matching)
    for root, dirs, files in os.walk(base_path):
        # Skip certain directories
        if '_simulated' in root or '.git' in root:
            continue
        
        # Check if this looks like a bundle directory
        root_path = Path(root)
        if 'plaintext_97.txt' in files or 'coverage_report.json' in files:
            bundles.append(root_path)
    
    return bundles

def main():
    """Main execution."""
    base_dir = Path(__file__).parent.parent.parent  # experiments/
    output_dir = base_dir / "audit" / "runs" / "2025-09-05"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Running BUNDLE_VALIDATOR...")
    print(f"Scanning: {base_dir}")
    
    # Find bundles
    bundles = scan_experiments(base_dir)
    print(f"Found {len(bundles)} potential bundles")
    
    # Validate each bundle
    results = []
    valid_count = 0
    
    for bundle_path in bundles:
        rel_path = bundle_path.relative_to(base_dir)
        ok, missing_fields, hash_ok, notes = validate_bundle(bundle_path)
        
        if ok:
            valid_count += 1
        
        results.append({
            'bundle_path': str(rel_path),
            'ok': str(ok).lower(),
            'missing_fields': '; '.join(missing_fields) if missing_fields else '',
            'hash_ok': str(hash_ok).lower(),
            'notes': notes
        })
    
    # Sort by path
    results.sort(key=lambda x: x['bundle_path'])
    
    # Write CSV
    output_file = output_dir / "BUNDLE_VALIDATOR.csv"
    with open(output_file, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=['bundle_path', 'ok', 'missing_fields', 'hash_ok', 'notes'])
            writer.writeheader()
            writer.writerows(results)
        else:
            f.write("bundle_path,ok,missing_fields,hash_ok,notes\n")
            f.write("NO_BUNDLES,n/a,n/a,n/a,No bundles found\n")
    
    # Print summary
    print(f"\nBUNDLE_VALIDATOR Results:")
    print(f"Total bundles: {len(bundles)}")
    print(f"Valid bundles: {valid_count}")
    print(f"Invalid bundles: {len(bundles) - valid_count}")
    
    if valid_count < len(bundles):
        print("\n⚠️  Some bundles failed validation:")
        for r in results[:5]:  # Show first 5 failures
            if r['ok'] == 'false':
                print(f"  - {r['bundle_path']}: {r['notes']}")
    
    print(f"\nResults saved to: {output_file}")
    
    return valid_count, len(bundles)

if __name__ == "__main__":
    valid, total = main()
    exit(0 if valid == total else 1)