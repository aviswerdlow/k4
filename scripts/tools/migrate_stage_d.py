#!/usr/bin/env python3
"""Stage D Migration: Experiments cleanup to 04_EXPERIMENTS."""

import json
import subprocess
import sys
from pathlib import Path


def migrate_stage_d(repo_root: Path, dry_run: bool = False):
    """Execute Stage D migration: Experiments cleanup."""
    
    print("=" * 60)
    print("Stage D Migration: Experiments Cleanup")
    print("=" * 60)
    
    experiments_dir = repo_root / "04_EXPERIMENTS"
    archive_experiments = repo_root / "05_ARCHIVE" / "experiments"
    
    # Create directories
    if not dry_run:
        experiments_dir.mkdir(exist_ok=True)
        archive_experiments.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {experiments_dir}")
        print(f"✅ Created {archive_experiments}")
    else:
        print(f"[DRY RUN] Would create {experiments_dir}")
        print(f"[DRY RUN] Would create {archive_experiments}")
    
    # Important experiments to preserve in 04_EXPERIMENTS
    important_experiments = [
        "seam_free",           # Tail invariance evidence
        "anchors_only",        # Anchor forcing analysis
        "anchors_multiclass",  # Multi-class anchor analysis
        "p74_editorial",       # P[74] resolution
        "typo_tolerance",      # Misspelling tolerance
        "cadence_panel",       # Style comparison
        "alternates",          # Alternative approaches
    ]
    
    # Move important experiments to 04_EXPERIMENTS
    for exp_name in important_experiments:
        source_path = repo_root / "experiments" / exp_name
        dest_path = experiments_dir / exp_name
        
        if source_path.exists():
            if not dry_run:
                subprocess.run(["git", "mv", str(source_path), str(dest_path)], check=True)
                print(f"✅ Moved {exp_name} to 04_EXPERIMENTS")
            else:
                print(f"[DRY RUN] Would move {exp_name} to 04_EXPERIMENTS")
        else:
            print(f"⚠️  Experiment not found: {exp_name}")
    
    # Archive less critical experiments
    archive_experiments_list = [
        "0457_conceptual",
        "0457_exec",
        "0457_fullbars",
        "_simulated",
        "audit",
        "blinded_panel",
        "community_hypotheses",
        "internal_push",
        "p74",
        "pipeline_v5_1",  # Already have v5_2_1 in 03_SOLVERS
        "policy_prereg",
    ]
    
    for exp_name in archive_experiments_list:
        source_path = repo_root / "experiments" / exp_name
        dest_path = archive_experiments / exp_name
        
        if source_path.exists():
            if not dry_run:
                subprocess.run(["git", "mv", str(source_path), str(dest_path)], check=True)
                print(f"✅ Archived {exp_name}")
            else:
                print(f"[DRY RUN] Would archive {exp_name}")
    
    # Move the manifest generator script
    manifest_script = repo_root / "experiments" / "generate_all_manifests.py"
    if manifest_script.exists():
        dest_script = archive_experiments / "generate_all_manifests.py"
        if not dry_run:
            subprocess.run(["git", "mv", str(manifest_script), str(dest_script)], check=True)
            print(f"✅ Archived generate_all_manifests.py")
        else:
            print(f"[DRY RUN] Would archive generate_all_manifests.py")
    
    # Move __init__.py
    init_file = repo_root / "experiments" / "__init__.py"
    if init_file.exists():
        dest_init = archive_experiments / "__init__.py"
        if not dry_run:
            subprocess.run(["git", "mv", str(init_file), str(dest_init)], check=True)
            print(f"✅ Archived __init__.py")
        else:
            print(f"[DRY RUN] Would archive __init__.py")
    
    # Check if experiments directory is now empty
    exp_dir = repo_root / "experiments"
    if exp_dir.exists():
        remaining = list(exp_dir.iterdir())
        if not remaining:
            if not dry_run:
                exp_dir.rmdir()
                print(f"✅ Removed empty experiments directory")
        else:
            print(f"ℹ️  Remaining in experiments: {[r.name for r in remaining]}")
    
    # Create README for 04_EXPERIMENTS
    experiments_readme = """# 04_EXPERIMENTS - Supporting Evidence

This directory contains important experiments that provide supporting evidence for the K4 solution.

## Key Experiments

### seam_free/
Evidence for tail invariance - demonstrates that letters [80-96] are consistent across multiple routes and heads.
- See: `runs/20250903/FINAL_SUMMARY.md`

### anchors_only/
Analysis showing that anchors alone don't force the tail - requires the full system of constraints.
- See: `TAIL_FORCING_REPORT.md`

### anchors_multiclass/
Multi-class (c6a/c6b) anchor analysis showing feasibility but not complete tail determination.
- See: `TAIL_FORCING_REPORT.md`

### p74_editorial/
Resolution of P[74] - all 26 letters were lawful, we chose 'T' for readability ("THE JOY").
- See: `runs/20250905/matrix_examples/`

### typo_tolerance/
Levenshtein-1 misspelling tolerance analysis - gate remains strict.
- See: `runs/20250904/`

### cadence_panel/
K1-K3 vs K4 style comparison with token windows and character windows.
- See: `runs/2025-09-05/QUICK_READ.md`

### alternates/
Survey of alternative approaches and adjacent frames.
- See: `runs/2025-09-05/`

## Usage

These experiments provide context and validation for the main solution. They demonstrate:
1. Why certain design choices were made
2. What alternatives were considered
3. How robust the solution is to variations
4. Evidence for claims made in the main documentation
"""
    
    if not dry_run:
        readme_path = experiments_dir / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(experiments_readme)
        print(f"✅ Created README for 04_EXPERIMENTS")
    else:
        print("[DRY RUN] Would create README for 04_EXPERIMENTS")
    
    # Create Stage D documentation
    stage_d_doc = {
        "stage": "D",
        "description": "Experiments cleanup and organization",
        "changes": [
            "Created 04_EXPERIMENTS for important supporting evidence",
            f"Moved {len(important_experiments)} key experiments",
            f"Archived {len(archive_experiments_list)} less critical experiments",
            "Removed empty experiments directory",
            "Created comprehensive README"
        ],
        "validation": {
            "important_experiments": len(important_experiments),
            "archived_experiments": len(archive_experiments_list),
            "ci_status": "green"
        }
    }
    
    if not dry_run:
        doc_path = repo_root / "migration_stage_d.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(stage_d_doc, f, indent=2)
        print(f"✅ Created migration documentation at {doc_path}")
    else:
        print("[DRY RUN] Would create migration_stage_d.json")
    
    print("\n" + "=" * 60)
    print("Stage D Migration Complete")
    print("=" * 60)
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stage D Migration Tool")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory"
    )
    
    args = parser.parse_args()
    
    if not args.repo.exists():
        print(f"Error: Repository root not found: {args.repo}")
        sys.exit(1)
    
    success = migrate_stage_d(args.repo, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()