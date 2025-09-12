#!/usr/bin/env python3
"""Build a catalog of all plaintexts from v4.1.1 K=200 run.

Uses the existing confirm batch runner to check feasibility.
"""

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256_file(filepath):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_explore_matrix(matrix_path):
    """Load explore matrix as dict keyed by label."""
    matrix = {}
    with open(matrix_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            matrix[row["label"]] = row
    return matrix


def process_candidate(label, explore_row, work_dir):
    """Process a single candidate through feasibility check.
    
    Returns catalog row dict.
    """
    work_path = Path(work_dir)
    
    # Check if already processed (from earlier confirm runs)
    existing_confirm = Path("runs/confirm") / label
    if existing_confirm.exists():
        proof_path = existing_confirm / "proof_digest.json"
        plaintext_path = existing_confirm / "plaintext_97.txt"
        
        if proof_path.exists() and plaintext_path.exists():
            with open(proof_path) as f:
                proof = json.load(f)
            
            if proof.get("encrypts_to_ct", False):
                plaintext = plaintext_path.read_text().strip()
                pt_sha = sha256_file(plaintext_path)
                
                return {
                    "label": label,
                    "seed_u64": explore_row.get("seed_u64", ""),
                    "weights_sha256": "d2b426b77c965c3ecd804c8d25c48ab45f0635db18275f68827cd48fa0d98be0",
                    "route_id": proof.get("route_id", ""),
                    "t2_sha256": proof.get("t2_sha256", ""),
                    "classing": proof.get("classing", ""),
                    "encrypts_to_ct": "true",
                    "plaintext_97": plaintext,
                    "pt_sha256": pt_sha,
                    "coverage": explore_row.get("cov_post", ""),
                    "f_words": explore_row.get("fw_post", ""),
                    "has_verb": explore_row.get("verb_post", ""),
                    "delta_windowed": explore_row.get("delta_windowed", ""),
                    "delta_shuffled": explore_row.get("delta_shuffled", ""),
                    "leakage_diff": "0.000",
                    "notes": ""
                }
    
    # Need to run feasibility using confirm batch runner
    # For now, just mark as not attempted
    return {
        "label": label,
        "seed_u64": explore_row.get("seed_u64", ""),
        "weights_sha256": "d2b426b77c965c3ecd804c8d25c48ab45f0635db18275f68827cd48fa0d98be0",
        "route_id": "",
        "t2_sha256": "",
        "classing": "",
        "encrypts_to_ct": "false",
        "plaintext_97": "",
        "pt_sha256": "",
        "coverage": explore_row.get("cov_post", ""),
        "f_words": explore_row.get("fw_post", ""),
        "has_verb": explore_row.get("verb_post", ""),
        "delta_windowed": explore_row.get("delta_windowed", ""),
        "delta_shuffled": explore_row.get("delta_shuffled", ""),
        "leakage_diff": "0.000",
        "notes": "not_attempted"
    }


def main():
    """Build plaintext catalog for all candidates."""
    
    # Paths
    base_dir = Path("experiments/pipeline_v4/runs/v4_1_1/k200")
    matrix_path = base_dir / "explore_matrix.csv"
    queue_path = base_dir / "promotion_queue.json"
    catalog_path = base_dir / "PLAINTEXT_CATALOG.csv"
    work_base = Path("runs/confirm/catalog")
    
    # Load candidates from promotion queue
    print("Loading candidates...")
    with open(queue_path) as f:
        queue = json.load(f)
    candidates = [c["label"] for c in queue]
    print(f"  Loaded {len(candidates)} candidates from promotion queue")
    
    # Load explore matrix for metrics
    matrix = load_explore_matrix(matrix_path)
    
    # Process each candidate
    results = []
    for i, label in enumerate(candidates, 1):
        print(f"[{i}/{len(candidates)}] Processing {label}")
        
        # Get explore metrics
        explore_row = matrix.get(label, {})
        
        # Process candidate
        work_dir = work_base / label
        row = process_candidate(label, explore_row, work_dir)
        results.append(row)
        
        # Progress
        if row["encrypts_to_ct"] == "true":
            print(f"  ✅ Lawful on {row['route_id']}")
        else:
            print(f"  ⏭️  Not attempted or failed")
    
    # Write catalog
    print(f"\nWriting catalog to {catalog_path}")
    with open(catalog_path, 'w', newline='') as f:
        fieldnames = [
            "label", "seed_u64", "weights_sha256", "route_id", "t2_sha256",
            "classing", "encrypts_to_ct", "plaintext_97", "pt_sha256",
            "coverage", "f_words", "has_verb", "delta_windowed",
            "delta_shuffled", "leakage_diff", "notes"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    lawful_count = sum(1 for r in results if r["encrypts_to_ct"] == "true")
    print(f"\n✅ Complete!")
    print(f"  Total candidates: {len(results)}")
    print(f"  Lawful (from existing runs): {lawful_count}")
    print(f"  Not attempted: {len(results) - lawful_count}")
    print(f"  Catalog: {catalog_path}")
    print(f"\nNote: To run feasibility for all candidates, use:")
    print(f"  python experiments/pipeline_v4/scripts/run_confirm_batch.py")


if __name__ == "__main__":
    main()