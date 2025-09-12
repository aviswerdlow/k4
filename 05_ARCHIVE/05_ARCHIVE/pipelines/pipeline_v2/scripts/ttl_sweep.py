#!/usr/bin/env python3
"""
TTL sweeper for Pipeline v2 runs.
Archives stale sub-runs and maintains TTL_LOG.md.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict


def check_ttl(run_dir: Path, ttl_days: int = 10) -> bool:
    """Check if a run has exceeded TTL."""
    # Check for date in directory name
    dir_name = run_dir.name
    
    # Extract date from format YYYY-MM-DD-*
    if dir_name.startswith("2025-") or dir_name.startswith("2024-"):
        try:
            date_str = "-".join(dir_name.split("-")[:3])
            run_date = datetime.strptime(date_str, "%Y-%m-%d")
            age_days = (datetime.now() - run_date).days
            return age_days > ttl_days
        except:
            pass
    
    # Check modification time as fallback
    stat = run_dir.stat()
    mod_time = datetime.fromtimestamp(stat.st_mtime)
    age_days = (datetime.now() - mod_time).days
    return age_days > ttl_days


def archive_run(run_dir: Path, archive_dir: Path) -> None:
    """Archive a stale run."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create archive marker
    marker = archive_dir / f"{run_dir.name}.archived"
    with open(marker, 'w') as f:
        f.write(f"Archived: {datetime.now().isoformat()}\n")
        f.write(f"Original: {run_dir}\n")
    
    print(f"  Archived: {run_dir.name}")


def sweep_ttl(
    runs_dir: Path,
    archive_dir: Path,
    ttl_days: int = 10,
    dry_run: bool = False
) -> None:
    """Sweep for stale runs and update TTL log."""
    
    print(f"TTL Sweep: {runs_dir}")
    print(f"TTL threshold: {ttl_days} days")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}\n")
    
    stale_runs = []
    active_runs = []
    
    # Check all run directories
    for run_dir in sorted(runs_dir.glob("*")):
        if not run_dir.is_dir():
            continue
        
        # Skip special directories
        if run_dir.name in ["archive", ".git", "__pycache__"]:
            continue
        
        if check_ttl(run_dir, ttl_days):
            stale_runs.append(run_dir)
        else:
            active_runs.append(run_dir)
    
    print(f"Found {len(stale_runs)} stale runs:")
    for run in stale_runs:
        print(f"  - {run.name}")
    
    print(f"\nActive runs: {len(active_runs)}")
    
    # Archive stale runs
    if stale_runs and not dry_run:
        print("\nArchiving stale runs...")
        for run in stale_runs:
            archive_run(run, archive_dir)
    
    # Update TTL_LOG.md
    log_path = runs_dir / "TTL_LOG.md"
    
    with open(log_path, 'w') as f:
        f.write("# TTL Log\n\n")
        f.write(f"**Last sweep:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**TTL threshold:** {ttl_days} days\n\n")
        
        f.write("## Active Runs\n\n")
        f.write("| Run | Age (days) | Status |\n")
        f.write("|-----|------------|--------|\n")
        
        for run in active_runs:
            # Calculate age
            stat = run.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            age_days = (datetime.now() - mod_time).days
            
            status = "✅ Active" if age_days < ttl_days else "⚠️ Near TTL"
            f.write(f"| {run.name} | {age_days} | {status} |\n")
        
        f.write(f"\n## Archived Runs\n\n")
        f.write(f"Total archived: {len(stale_runs)}\n\n")
        
        if stale_runs:
            f.write("| Run | Archive Date |\n")
            f.write("|-----|-------------|\n")
            for run in stale_runs:
                f.write(f"| {run.name} | {datetime.now().date()} |\n")
        
        f.write("\n## Policy\n\n")
        f.write(f"- Runs older than {ttl_days} days are archived\n")
        f.write("- Archived runs have markers in `archive/` directory\n")
        f.write("- Original data preserved, just marked as stale\n")
    
    print(f"\nTTL log updated: {log_path}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="TTL sweeper for Pipeline v2")
    parser.add_argument("--runs",
                       default="experiments/pipeline_v2/runs",
                       type=Path,
                       help="Runs directory")
    parser.add_argument("--archive",
                       default="experiments/pipeline_v2/runs/archive",
                       type=Path,
                       help="Archive directory")
    parser.add_argument("--ttl", type=int, default=10,
                       help="TTL in days")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run mode (no archiving)")
    
    args = parser.parse_args()
    
    sweep_ttl(
        args.runs,
        args.archive,
        args.ttl,
        args.dry_run
    )


if __name__ == "__main__":
    main()