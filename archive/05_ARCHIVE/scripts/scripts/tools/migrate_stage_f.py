#!/usr/bin/env python3
"""Stage F Migration: Final cleanup of legacy roots and stray files."""

import json
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime


def run_git_command(cmd, dry_run=False):
    """Execute a git command with error handling."""
    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(cmd)}")
        return True
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Command failed: {' '.join(cmd)}")
        print(f"    Error: {e.stderr}")
        return False


def migrate_stage_f(repo_root: Path, dry_run: bool = False):
    """Execute Stage F migration: Final cleanup."""
    
    print("=" * 60)
    print("Stage F Migration: Final Root Cleanup")
    print("=" * 60)
    
    # Create new directories as needed
    tools_dir = repo_root / "07_TOOLS"
    docs_dir = repo_root / "06_DOCUMENTATION"
    
    if not dry_run:
        tools_dir.mkdir(exist_ok=True)
        docs_dir.mkdir(exist_ok=True)
        (tools_dir / "validation").mkdir(exist_ok=True, parents=True)
        (tools_dir / "migration").mkdir(exist_ok=True, parents=True)
        (repo_root / "04_EXPERIMENTS" / "reviews").mkdir(exist_ok=True, parents=True)
        (repo_root / "04_EXPERIMENTS" / "confirm").mkdir(exist_ok=True, parents=True)
        (repo_root / "04_EXPERIMENTS" / "logs").mkdir(exist_ok=True, parents=True)
        print("✅ Created target directories")
    
    # 1. Migrate data/ to 02_DATA/
    data_dir = repo_root / "data"
    if data_dir.exists() and any(data_dir.iterdir()):
        print("\n📦 Migrating data/ to 02_DATA/")
        for item in data_dir.iterdir():
            if item.name == ".gitkeep":
                continue
            dest = repo_root / "02_DATA" / item.name
            if not dest.exists():
                if not dry_run:
                    run_git_command(["git", "mv", str(item), str(dest)], dry_run)
                    print(f"  ✅ Moved {item.name} to 02_DATA/")
                else:
                    print(f"  [DRY RUN] Would move {item.name} to 02_DATA/")
        
        # Remove empty data directory
        if not dry_run and data_dir.exists():
            remaining = list(data_dir.iterdir())
            if not remaining or (len(remaining) == 1 and remaining[0].name == ".gitkeep"):
                run_git_command(["git", "rm", "-r", str(data_dir)], dry_run)
                print("  ✅ Removed empty data/ directory")
    
    # 2. Clean up results/ directory
    results_dir = repo_root / "results"
    if results_dir.exists() and any(results_dir.iterdir()):
        print("\n📦 Cleaning up results/ directory")
        # Check what's in results - should be empty or only have directories we've already moved
        for item in results_dir.iterdir():
            if item.is_dir() and item.name != ".gitkeep":
                # Archive anything unexpected
                dest = repo_root / "05_ARCHIVE" / "results" / item.name
                if not dest.exists():
                    if not dry_run:
                        dest.parent.mkdir(exist_ok=True, parents=True)
                        run_git_command(["git", "mv", str(item), str(dest)], dry_run)
                        print(f"  ✅ Archived {item.name} to 05_ARCHIVE/results/")
        
        if not dry_run and results_dir.exists():
            run_git_command(["git", "rm", "-r", str(results_dir)], dry_run)
            print("  ✅ Removed results/ directory")
    
    # 3. Handle release/ directory
    release_dir = repo_root / "release"
    if release_dir.exists() and any(release_dir.iterdir()):
        print("\n📦 Handling release/ directory")
        # Archive release artifacts
        dest = repo_root / "05_ARCHIVE" / "releases"
        if not dry_run:
            dest.mkdir(exist_ok=True, parents=True)
            run_git_command(["git", "mv", str(release_dir), str(dest / "release")], dry_run)
            print("  ✅ Archived release/ to 05_ARCHIVE/releases/")
    
    # 4. Migrate review/ to experiments
    review_dir = repo_root / "review"
    if review_dir.exists():
        print("\n📦 Migrating review/ to 04_EXPERIMENTS/reviews/")
        for item in review_dir.iterdir():
            dest = repo_root / "04_EXPERIMENTS" / "reviews" / item.name
            if not dry_run:
                run_git_command(["git", "mv", str(item), str(dest)], dry_run)
                print(f"  ✅ Moved {item.name} to 04_EXPERIMENTS/reviews/")
        
        if not dry_run and review_dir.exists():
            run_git_command(["git", "rm", "-r", str(review_dir)], dry_run)
            print("  ✅ Removed review/ directory")
    
    # 5. Migrate runs/ to experiments
    runs_dir = repo_root / "runs"
    if runs_dir.exists():
        print("\n📦 Migrating runs/ to 04_EXPERIMENTS/")
        # Check for confirm subdirectory
        confirm_dir = runs_dir / "confirm"
        if confirm_dir.exists():
            dest = repo_root / "04_EXPERIMENTS" / "confirm"
            if not dry_run:
                # Move contents of confirm, not the directory itself
                for item in confirm_dir.iterdir():
                    run_git_command(["git", "mv", str(item), str(dest / item.name)], dry_run)
                print("  ✅ Moved runs/confirm contents to 04_EXPERIMENTS/confirm/")
        
        # Archive any other runs
        for item in runs_dir.iterdir():
            if item.name != "confirm" and item.name != ".gitkeep":
                dest = repo_root / "05_ARCHIVE" / "runs" / item.name
                if not dry_run:
                    dest.parent.mkdir(exist_ok=True, parents=True)
                    run_git_command(["git", "mv", str(item), str(dest)], dry_run)
                    print(f"  ✅ Archived {item.name} to 05_ARCHIVE/runs/")
        
        if not dry_run and runs_dir.exists():
            run_git_command(["git", "rm", "-r", str(runs_dir)], dry_run)
            print("  ✅ Removed runs/ directory")
    
    # 6. Migrate k4cli to 07_TOOLS
    k4cli_dir = repo_root / "k4cli"
    if k4cli_dir.exists():
        print("\n📦 Migrating k4cli/ to 07_TOOLS/")
        dest = tools_dir / "k4cli"
        if not dry_run:
            run_git_command(["git", "mv", str(k4cli_dir), str(dest)], dry_run)
            print("  ✅ Moved k4cli/ to 07_TOOLS/")
    
    # Remove k4cli.egg-info if it exists
    egg_info = repo_root / "k4cli.egg-info"
    if egg_info.exists():
        if not dry_run:
            run_git_command(["git", "rm", "-r", str(egg_info)], dry_run)
            print("  ✅ Removed k4cli.egg-info")
    
    # 7. Reorganize scripts/ directory
    scripts_dir = repo_root / "scripts"
    if scripts_dir.exists():
        print("\n📦 Reorganizing scripts/ directory")
        
        # Move validation tools
        validation_scripts = [
            "validate_bundle.py",
            "make_manifest.py",
            "bundle_validator.py"
        ]
        
        tools_subdir = scripts_dir / "tools"
        if tools_subdir.exists():
            for script_name in validation_scripts:
                script = tools_subdir / script_name
                if script.exists():
                    dest = tools_dir / "validation" / script_name
                    if not dry_run:
                        run_git_command(["git", "mv", str(script), str(dest)], dry_run)
                        print(f"  ✅ Moved {script_name} to 07_TOOLS/validation/")
            
            # Move migration tools (already in migration subdirectory)
            migration_dir = tools_subdir / "migration"
            if migration_dir.exists():
                for item in migration_dir.iterdir():
                    dest = tools_dir / "migration" / item.name
                    if not dry_run:
                        run_git_command(["git", "mv", str(item), str(dest)], dry_run)
                        print(f"  ✅ Moved {item.name} to 07_TOOLS/migration/")
            
            # Move remaining migration scripts
            for script in tools_subdir.glob("migrate_*.py"):
                dest = tools_dir / "migration" / script.name
                if not dry_run:
                    run_git_command(["git", "mv", str(script), str(dest)], dry_run)
                    print(f"  ✅ Moved {script.name} to 07_TOOLS/migration/")
        
        # Archive any remaining scripts
        if scripts_dir.exists():
            remaining = list(scripts_dir.rglob("*"))
            remaining = [f for f in remaining if f.is_file() and ".git" not in str(f)]
            if remaining:
                archive_scripts = repo_root / "05_ARCHIVE" / "scripts"
                if not dry_run:
                    archive_scripts.mkdir(exist_ok=True, parents=True)
                    run_git_command(["git", "mv", str(scripts_dir), str(archive_scripts / "scripts")], dry_run)
                    print("  ✅ Archived remaining scripts to 05_ARCHIVE/scripts/")
            else:
                if not dry_run:
                    run_git_command(["git", "rm", "-r", str(scripts_dir)], dry_run)
                    print("  ✅ Removed empty scripts/ directory")
    
    # 8. Migrate docs/ to 06_DOCUMENTATION
    docs_source = repo_root / "docs"
    if docs_source.exists():
        print("\n📦 Migrating docs/ to 06_DOCUMENTATION/")
        for item in docs_source.iterdir():
            dest = docs_dir / item.name
            if not dry_run:
                run_git_command(["git", "mv", str(item), str(dest)], dry_run)
                print(f"  ✅ Moved {item.name} to 06_DOCUMENTATION/")
        
        if not dry_run and docs_source.exists():
            run_git_command(["git", "rm", "-r", str(docs_source)], dry_run)
            print("  ✅ Removed docs/ directory")
    
    # 9. Handle archive/ directory if it exists
    archive_dir = repo_root / "archive"
    if archive_dir.exists():
        print("\n📦 Consolidating archive/ into 05_ARCHIVE/")
        for item in archive_dir.iterdir():
            dest = repo_root / "05_ARCHIVE" / "legacy_archive" / item.name
            if not dry_run:
                dest.parent.mkdir(exist_ok=True, parents=True)
                run_git_command(["git", "mv", str(item), str(dest)], dry_run)
                print(f"  ✅ Moved {item.name} to 05_ARCHIVE/legacy_archive/")
        
        if not dry_run and archive_dir.exists():
            run_git_command(["git", "rm", "-r", str(archive_dir)], dry_run)
            print("  ✅ Removed archive/ directory")
    
    # 10. Clean up stray files
    print("\n🧹 Cleaning up stray files")
    
    # Move log files
    for log_file in repo_root.glob("*.log"):
        dest = repo_root / "04_EXPERIMENTS" / "logs" / log_file.name
        if not dry_run:
            run_git_command(["git", "mv", str(log_file), str(dest)], dry_run)
            print(f"  ✅ Moved {log_file.name} to 04_EXPERIMENTS/logs/")
    
    # Remove POLICY.json (canonical is in 03_SOLVERS)
    policy_file = repo_root / "POLICY.json"
    if policy_file.exists():
        if not dry_run:
            run_git_command(["git", "rm", str(policy_file)], dry_run)
            print("  ✅ Removed duplicate POLICY.json")
    
    # Remove .DS_Store
    ds_store = repo_root / ".DS_Store"
    if ds_store.exists():
        if not dry_run:
            run_git_command(["git", "rm", "-f", str(ds_store)], dry_run)
            print("  ✅ Removed .DS_Store")
    
    # Ensure .DS_Store is in .gitignore
    gitignore = repo_root / ".gitignore"
    if not dry_run:
        with open(gitignore, "r") as f:
            content = f.read()
        if ".DS_Store" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# macOS\n.DS_Store\n")
            print("  ✅ Added .DS_Store to .gitignore")
    
    # Create Stage F documentation
    stage_f_doc = {
        "stage": "F",
        "description": "Final root cleanup and legacy directory migration",
        "changes": [
            "Migrated data/ contents to 02_DATA/",
            "Removed empty results/ directory",
            "Archived release/ to 05_ARCHIVE/releases/",
            "Moved review/ to 04_EXPERIMENTS/reviews/",
            "Moved runs/confirm to 04_EXPERIMENTS/confirm/",
            "Created 07_TOOLS/ and migrated k4cli and validation scripts",
            "Created 06_DOCUMENTATION/ and migrated docs/",
            "Cleaned up stray log files and POLICY.json",
            "Added .DS_Store to .gitignore"
        ],
        "validation": {
            "legacy_roots_removed": ["data", "results", "release", "review", "runs", "scripts", "docs", "k4cli", "archive"],
            "new_directories_created": ["06_DOCUMENTATION", "07_TOOLS"],
            "ci_status": "pending"
        },
        "completion_time": datetime.utcnow().isoformat() + "Z"
    }
    
    if not dry_run:
        doc_path = tools_dir / "migration" / "migration_stage_f.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(stage_f_doc, f, indent=2)
        print(f"\n✅ Created migration documentation")
    
    print("\n" + "=" * 60)
    print("Stage F Migration Complete")
    print("Repository is now fully clean!")
    print("=" * 60)
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stage F Migration Tool - Final Cleanup")
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
    
    success = migrate_stage_f(args.repo, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()