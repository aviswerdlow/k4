#!/usr/bin/env python3
"""
Validate v5.2 production run outputs.
"""

import json
import csv
import hashlib
from pathlib import Path
import sys

def validate_production_run(run_dir: Path) -> bool:
    """Validate production run outputs."""
    
    print(f"Validating production run: {run_dir}")
    
    errors = []
    
    # Check required files
    required_files = [
        "EXPLORE_MATRIX.csv",
        "DASHBOARD.csv",
        "README.md",
        "MANIFEST.sha256"
    ]
    
    for file in required_files:
        path = run_dir / file
        if not path.exists():
            errors.append(f"Missing required file: {file}")
        else:
            print(f"  ✓ Found {file}")
    
    # Check promotion queue if exists
    queue_path = run_dir / "promotion_queue.json"
    if queue_path.exists():
        print(f"  ✓ Found promotion_queue.json")
        
        # Validate queue structure
        try:
            with open(queue_path, 'r') as f:
                queue = json.load(f)
            
            if "policy_version" not in queue:
                errors.append("promotion_queue missing policy_version")
            if "candidates" not in queue:
                errors.append("promotion_queue missing candidates")
            else:
                print(f"    - {len(queue['candidates'])} candidates in queue")
                
                # Validate first candidate
                if queue['candidates']:
                    cand = queue['candidates'][0]
                    required_fields = ["label", "seed", "head_0_74", "score"]
                    for field in required_fields:
                        if field not in cand:
                            errors.append(f"Candidate missing field: {field}")
        except Exception as e:
            errors.append(f"Error parsing promotion_queue.json: {e}")
    
    # Validate explore matrix
    matrix_path = run_dir / "EXPLORE_MATRIX.csv"
    if matrix_path.exists():
        try:
            with open(matrix_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                print(f"    - {len(rows)} rows in explore matrix")
                
                # Check required columns
                if rows:
                    required_cols = [
                        "label", "seed", "head_0_74", "content_ratio",
                        "near_gate", "context", "promoted"
                    ]
                    for col in required_cols:
                        if col not in rows[0]:
                            errors.append(f"Missing column in explore matrix: {col}")
        except Exception as e:
            errors.append(f"Error parsing EXPLORE_MATRIX.csv: {e}")
    
    # Validate manifest
    manifest_path = run_dir / "MANIFEST.sha256"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) != 2:
                        errors.append(f"Invalid manifest line: {line}")
                    else:
                        sha, filename = parts
                        file_path = run_dir / filename
                        if file_path.exists():
                            # Verify hash
                            with open(file_path, 'rb') as f:
                                actual_sha = hashlib.sha256(f.read()).hexdigest()
                            if actual_sha != sha:
                                errors.append(f"Hash mismatch for {filename}")
                            else:
                                print(f"  ✓ Hash verified for {filename}")
        except Exception as e:
            errors.append(f"Error parsing MANIFEST.sha256: {e}")
    
    # Report results
    if errors:
        print("\n❌ Validation FAILED:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n✅ Validation PASSED!")
        return True

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <run_directory>")
        return 1
    
    run_dir = Path(sys.argv[1])
    if not run_dir.exists():
        print(f"Error: Directory not found: {run_dir}")
        return 1
    
    if validate_production_run(run_dir):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())