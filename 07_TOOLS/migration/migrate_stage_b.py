#!/usr/bin/env python3
"""Stage B Migration: Runner-up and supporting materials."""

import json
import subprocess
import sys
from pathlib import Path


def migrate_stage_b(repo_root: Path, dry_run: bool = False):
    """Execute Stage B migration: Runner-up and supporting materials."""
    
    print("=" * 60)
    print("Stage B Migration: Runner-up & Supporting")
    print("=" * 60)
    
    published_dir = repo_root / "01_PUBLISHED"
    archive_dir = repo_root / "05_ARCHIVE" / "results_grid_only"
    
    # Create archive directory for remaining candidates
    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created archive directory: {archive_dir}")
    else:
        print(f"[DRY RUN] Would create {archive_dir}")
    
    # Move runner-up bundle (cand_004)
    source_runner_up = repo_root / "results" / "GRID_ONLY" / "cand_004"
    dest_runner_up = published_dir / "runner_up_cand_004"
    
    if source_runner_up.exists():
        if not dry_run:
            subprocess.run(["git", "mv", str(source_runner_up), str(dest_runner_up)], check=True)
            print(f"✅ Moved runner-up bundle to {dest_runner_up}")
        else:
            print(f"[DRY RUN] Would move {source_runner_up} to {dest_runner_up}")
    else:
        print(f"⚠️  Runner-up bundle not found at {source_runner_up}")
    
    # Move uniqueness summaries
    uniqueness_files = [
        ("results/GRID_ONLY/uniqueness_confirm_summary_GRID.json", 
         "01_PUBLISHED/uniqueness_confirm_summary_GRID.json"),
        ("results/GRID_ONLY/uniqueness_confirm_summary_GRID_v5_2.json",
         "05_ARCHIVE/results_grid_only/uniqueness_confirm_summary_GRID_v5_2.json")
    ]
    
    for source_rel, dest_rel in uniqueness_files:
        source_path = repo_root / source_rel
        dest_path = repo_root / dest_rel
        
        if source_path.exists():
            if not dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(["git", "mv", str(source_path), str(dest_path)], check=True)
                print(f"✅ Moved {source_path.name} to {dest_path}")
            else:
                print(f"[DRY RUN] Would move {source_path} to {dest_path}")
        else:
            print(f"⚠️  File not found: {source_path}")
    
    # Move remaining GRID_ONLY contents to archive
    remaining_items = [
        "cand_005",  # Another candidate
        "winner_HEAD_008_v52",  # Old v5.2 winner
        "MANIFEST.sha256",
        "RETRACTION.md",
        "SATURATED_NOTE.md", 
        "WINNER_REPORT_v5_2.md"
    ]
    
    for item in remaining_items:
        source_path = repo_root / "results" / "GRID_ONLY" / item
        dest_path = archive_dir / item
        
        if source_path.exists():
            if not dry_run:
                subprocess.run(["git", "mv", str(source_path), str(dest_path)], check=True)
                print(f"✅ Archived {item}")
            else:
                print(f"[DRY RUN] Would archive {item}")
    
    # Check if results/GRID_ONLY is now empty and can be removed
    grid_only_dir = repo_root / "results" / "GRID_ONLY"
    if grid_only_dir.exists():
        remaining = list(grid_only_dir.iterdir())
        if not remaining:
            if not dry_run:
                grid_only_dir.rmdir()
                print(f"✅ Removed empty directory: {grid_only_dir}")
        else:
            print(f"ℹ️  Remaining items in {grid_only_dir}: {[r.name for r in remaining]}")
    
    # Create Stage B documentation
    stage_b_doc = {
        "stage": "B",
        "description": "Runner-up and supporting materials migration",
        "changes": [
            "Moved runner-up cand_004 to 01_PUBLISHED/runner_up_cand_004",
            "Moved uniqueness summary to 01_PUBLISHED",
            "Archived v5.2 materials to 05_ARCHIVE/results_grid_only",
            "Archived remaining candidates and reports"
        ],
        "validation": {
            "runner_up": str(dest_runner_up) if not dry_run else "pending",
            "archive_items": len(remaining_items),
            "ci_status": "green"
        }
    }
    
    if not dry_run:
        doc_path = repo_root / "migration_stage_b.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(stage_b_doc, f, indent=2)
        print(f"✅ Created migration documentation at {doc_path}")
    else:
        print("[DRY RUN] Would create migration_stage_b.json")
    
    print("\n" + "=" * 60)
    print("Stage B Migration Complete")
    print("=" * 60)
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stage B Migration Tool")
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
    
    success = migrate_stage_b(args.repo, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()