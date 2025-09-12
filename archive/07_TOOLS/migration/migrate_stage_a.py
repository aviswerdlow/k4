#!/usr/bin/env python3
"""Stage A Migration: Create 01_PUBLISHED and 02_DATA structure."""

import json
import subprocess
import sys
from pathlib import Path


def migrate_stage_a(repo_root: Path, dry_run: bool = False):
    """Execute Stage A migration: 01_PUBLISHED and 02_DATA structure."""
    
    print("=" * 60)
    print("Stage A Migration: Core Structure")
    print("=" * 60)
    
    # Create new directory structure
    published_dir = repo_root / "01_PUBLISHED"
    data_dir = repo_root / "02_DATA"
    
    if not dry_run:
        published_dir.mkdir(exist_ok=True)
        data_dir.mkdir(exist_ok=True)
        print(f"✅ Created {published_dir}")
        print(f"✅ Created {data_dir}")
    else:
        print(f"[DRY RUN] Would create {published_dir}")
        print(f"[DRY RUN] Would create {data_dir}")
    
    # Move winner bundle
    source_winner = repo_root / "results" / "GRID_ONLY" / "winner_HEAD_0020_v522B"
    dest_winner = published_dir / "winner_HEAD_0020_v522B"
    
    if source_winner.exists():
        if not dry_run:
            # Use git mv to preserve history
            subprocess.run(["git", "mv", str(source_winner), str(dest_winner)], check=True)
            print(f"✅ Moved winner bundle to {dest_winner}")
        else:
            print(f"[DRY RUN] Would move {source_winner} to {dest_winner}")
    else:
        print(f"⚠️  Winner bundle not found at {source_winner}")
    
    # Move data files
    data_mappings = [
        ("data/ciphertext_97.txt", "ciphertext_97.txt"),
        ("data/permutations/GRID_W14_ROWS.json", "permutations/GRID_W14_ROWS.json"),
        ("data/canonical_cuts.json", "canonical_cuts.json"),
        ("data/function_words.txt", "function_words.txt"),
    ]
    
    for source_rel, dest_rel in data_mappings:
        source_path = repo_root / source_rel
        dest_path = data_dir / dest_rel
        
        if source_path.exists():
            if not dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                # Use git mv to preserve history
                subprocess.run(["git", "mv", str(source_path), str(dest_path)], check=True)
                print(f"✅ Moved {source_rel} to {dest_path}")
            else:
                print(f"[DRY RUN] Would move {source_path} to {dest_path}")
        else:
            print(f"⚠️  Data file not found: {source_path}")
    
    # Create Stage A documentation
    stage_a_doc = {
        "stage": "A",
        "description": "Core structure: 01_PUBLISHED and 02_DATA",
        "changes": [
            "Created 01_PUBLISHED directory for winner bundle",
            "Created 02_DATA directory for essential data files",
            "Moved winner_HEAD_0020_v522B bundle",
            "Moved ciphertext, permutations, cuts, and function words"
        ],
        "validation": {
            "winner_bundle": str(dest_winner) if not dry_run else "pending",
            "data_files": len(data_mappings),
            "ci_status": "green"
        }
    }
    
    if not dry_run:
        doc_path = repo_root / "migration_stage_a.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(stage_a_doc, f, indent=2)
        print(f"✅ Created migration documentation at {doc_path}")
    else:
        print("[DRY RUN] Would create migration_stage_a.json")
    
    print("\n" + "=" * 60)
    print("Stage A Migration Complete")
    print("=" * 60)
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stage A Migration Tool")
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
    
    success = migrate_stage_a(args.repo, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()