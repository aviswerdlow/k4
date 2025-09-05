#!/usr/bin/env python3
"""
TTL (Time-To-Live) sweeper for hypothesis management.
Archives expired hypotheses and maintains state files.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def load_state_file(state_path: Path) -> Dict:
    """Load hypothesis state file."""
    if not state_path.exists():
        return {}
    
    with open(state_path) as f:
        return json.load(f)

def save_state_file(state_path: Path, state: Dict):
    """Save hypothesis state file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)

def is_expired(state: Dict, ttl_days: int) -> bool:
    """Check if hypothesis has expired."""
    if "created_at" not in state:
        return False
    
    created = datetime.fromisoformat(state["created_at"])
    now = datetime.now()
    age = now - created
    
    return age.days > ttl_days

def archive_hypothesis(run_dir: Path, archive_dir: Path, reason: str) -> bool:
    """Archive a hypothesis directory."""
    try:
        # Create archive directory
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Move directory
        dest = archive_dir / run_dir.name
        if dest.exists():
            # Add timestamp suffix if already exists
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = archive_dir / f"{run_dir.name}_{timestamp}"
        
        shutil.move(str(run_dir), str(dest))
        
        # Create archive note
        note_path = dest / "ARCHIVE_NOTE.txt"
        with open(note_path, 'w') as f:
            f.write(f"Archived: {datetime.now().isoformat()}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Original path: {run_dir}\n")
        
        return True
    except Exception as e:
        print(f"  Error archiving {run_dir}: {e}")
        return False

def update_ttl_log(log_path: Path, archived: List[Dict]):
    """Update TTL log with archived hypotheses."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing log
    if log_path.exists():
        with open(log_path) as f:
            content = f.read()
    else:
        content = "# TTL Archive Log\n\n"
    
    # Add new entries
    content += f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for entry in archived:
        content += f"- **{entry['name']}**: {entry['reason']}\n"
        content += f"  - Created: {entry.get('created', 'unknown')}\n"
        content += f"  - Age: {entry.get('age_days', 'unknown')} days\n"
        content += f"  - Path: `{entry['path']}`\n\n"
    
    # Write updated log
    with open(log_path, 'w') as f:
        f.write(content)

def sweep_ttl(root_dir: Path, ttl_days: int = 10, dry_run: bool = False) -> Dict:
    """
    Sweep for expired hypotheses and archive them.
    
    Args:
        root_dir: Root directory to sweep
        ttl_days: TTL threshold in days
        dry_run: If True, only report what would be archived
        
    Returns:
        Summary of sweep results
    """
    root_dir = Path(root_dir)
    archive_base = root_dir / "archive"
    
    print(f"TTL Sweeper starting...")
    print(f"  Root: {root_dir}")
    print(f"  TTL: {ttl_days} days")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    
    archived = []
    checked = 0
    errors = 0
    
    # Find all run directories
    for run_dir in root_dir.glob("*/"):
        if run_dir.name == "archive":
            continue
            
        # Look for state file
        state_file = run_dir / "hypothesis_state.json"
        
        if not state_file.exists():
            # Create default state for existing directories
            state = {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "ttl_days": ttl_days,
                "label": run_dir.name
            }
            if not dry_run:
                save_state_file(state_file, state)
        else:
            state = load_state_file(state_file)
        
        checked += 1
        
        # Check expiry
        if is_expired(state, ttl_days):
            created = state.get("created_at", "unknown")
            age_days = "unknown"
            
            if created != "unknown":
                created_dt = datetime.fromisoformat(created)
                age_days = (datetime.now() - created_dt).days
            
            entry = {
                "name": run_dir.name,
                "path": str(run_dir),
                "reason": f"TTL expired ({age_days} > {ttl_days} days)",
                "created": created,
                "age_days": age_days
            }
            
            print(f"  Archiving: {run_dir.name} (age: {age_days} days)")
            
            if not dry_run:
                archive_dir = archive_base / datetime.now().strftime("%Y-%m-%d")
                if archive_hypothesis(run_dir, archive_dir, entry["reason"]):
                    archived.append(entry)
                else:
                    errors += 1
            else:
                archived.append(entry)
    
    # Update log
    if archived and not dry_run:
        log_path = root_dir / "TTL_LOG.md"
        update_ttl_log(log_path, archived)
        print(f"\nLog updated: {log_path}")
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "checked": checked,
        "archived": len(archived),
        "errors": errors,
        "dry_run": dry_run,
        "ttl_days": ttl_days
    }
    
    print(f"\nSweep complete:")
    print(f"  Checked: {checked}")
    print(f"  Archived: {len(archived)}")
    print(f"  Errors: {errors}")
    
    return summary

def create_hypothesis_state(run_dir: Path, label: str, ttl_days: int = 10) -> Path:
    """
    Create a new hypothesis state file.
    
    Args:
        run_dir: Directory for the hypothesis
        label: Hypothesis label
        ttl_days: TTL in days
        
    Returns:
        Path to created state file
    """
    state = {
        "label": label,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "ttl_days": ttl_days,
        "status": "active",
        "metadata": {}
    }
    
    state_path = run_dir / "hypothesis_state.json"
    save_state_file(state_path, state)
    
    return state_path

def touch_hypothesis(run_dir: Path) -> bool:
    """
    Update the 'updated_at' timestamp to reset TTL.
    
    Args:
        run_dir: Directory containing hypothesis
        
    Returns:
        True if successful
    """
    state_path = run_dir / "hypothesis_state.json"
    
    if not state_path.exists():
        return False
    
    state = load_state_file(state_path)
    state["updated_at"] = datetime.now().isoformat()
    save_state_file(state_path, state)
    
    return True

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="TTL sweeper for hypothesis management")
    parser.add_argument("--root", default="experiments/pipeline_v2/runs/")
    parser.add_argument("--ttl-days", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true", help="Only report, don't archive")
    
    args = parser.parse_args()
    
    sweep_ttl(Path(args.root), args.ttl_days, args.dry_run)

if __name__ == "__main__":
    main()