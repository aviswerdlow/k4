#!/usr/bin/env python3
"""
Generate SHA-256 manifest for reproducibility and integrity verification.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    
    return sha256.hexdigest()

def generate_manifest(root_dir: Path, exclude_patterns: List[str] = None) -> Dict[str, str]:
    """
    Generate manifest of all files in directory.
    
    Args:
        root_dir: Root directory to manifest
        exclude_patterns: Patterns to exclude (e.g., ["*.pyc", "__pycache__"])
        
    Returns:
        Dictionary mapping relative paths to SHA-256 hashes
    """
    if exclude_patterns is None:
        exclude_patterns = [
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            "*.swp",
            "*.swo",
            ".git",
            "archive"
        ]
    
    manifest = {}
    
    for file_path in sorted(root_dir.rglob("*")):
        if file_path.is_dir():
            continue
            
        # Check exclusions
        skip = False
        for pattern in exclude_patterns:
            if pattern in str(file_path):
                skip = True
                break
        
        if skip:
            continue
        
        # Compute relative path
        rel_path = file_path.relative_to(root_dir)
        
        # Compute hash
        file_hash = compute_file_hash(file_path)
        
        manifest[str(rel_path)] = file_hash
    
    return manifest

def write_manifest(manifest: Dict[str, str], output_path: Path):
    """Write manifest to file."""
    with open(output_path, 'w') as f:
        # Write header
        f.write(f"# SHA-256 Manifest\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Files: {len(manifest)}\n")
        f.write("#\n")
        f.write("# Format: SHA256  PATH\n")
        f.write("#" + "=" * 70 + "\n\n")
        
        # Write entries
        for path, hash_val in sorted(manifest.items()):
            f.write(f"{hash_val}  {path}\n")

def verify_manifest(manifest_path: Path, verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Verify files against a manifest.
    
    Returns:
        Tuple of (all_valid, list_of_issues)
    """
    if not manifest_path.exists():
        return False, ["Manifest file not found"]
    
    root_dir = manifest_path.parent
    issues = []
    checked = 0
    
    with open(manifest_path) as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse line
            parts = line.split(None, 1)
            if len(parts) != 2:
                issues.append(f"Invalid line format: {line}")
                continue
            
            expected_hash, rel_path = parts
            file_path = root_dir / rel_path
            
            checked += 1
            
            # Check if file exists
            if not file_path.exists():
                issues.append(f"Missing file: {rel_path}")
                continue
            
            # Verify hash
            actual_hash = compute_file_hash(file_path)
            if actual_hash != expected_hash:
                issues.append(f"Hash mismatch: {rel_path}")
                if verbose:
                    print(f"  Expected: {expected_hash}")
                    print(f"  Actual:   {actual_hash}")
    
    if verbose:
        print(f"Checked {checked} files")
    
    return len(issues) == 0, issues

def create_repro_steps(run_dir: Path, config: Dict) -> Path:
    """
    Create REPRO_STEPS.md for a run.
    
    Args:
        run_dir: Run directory
        config: Configuration used for the run
        
    Returns:
        Path to created file
    """
    repro_path = run_dir / "REPRO_STEPS.md"
    
    with open(repro_path, 'w') as f:
        f.write("# Reproduction Steps\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        
        f.write("## Configuration\n")
        f.write(f"- Global seed: {config.get('seed', 1337)}\n")
        f.write(f"- Campaign: {config.get('campaign', 'unknown')}\n")
        f.write(f"- Mode: {config.get('mode', 'unknown')}\n\n")
        
        f.write("## Commands\n\n")
        
        if "explore" in str(run_dir):
            f.write("### Explore Lane\n")
            f.write("```bash\n")
            f.write("python experiments/pipeline_v2/scripts/explore/run_anchor_modes.py \\\n")
            f.write(f"  --seed {config.get('seed', 1337)}\n")
            f.write("```\n\n")
        
        if "confirm" in str(run_dir):
            f.write("### Confirm Lane\n")
            f.write("```bash\n")
            f.write("python experiments/pipeline_v2/scripts/confirm/run_confirm.py \\\n")
            f.write(f"  --seed {config.get('seed', 1337)}\n")
            f.write("```\n\n")
        
        f.write("## Seed Derivation\n")
        f.write("```\n")
        f.write('seed_worker = lo64(SHA256(seed_recipe + "|" + label + "|worker:" + worker_id))\n')
        f.write("```\n\n")
        
        f.write("## Output Files\n")
        
        # List key output files
        key_files = [
            "ANCHOR_MODE_MATRIX.csv",
            "CONFIRM_SUMMARY.csv",
            "promotion_queue.json",
            "ORBIT_SUMMARY.csv",
            "NEG_CONTROL_SUMMARY.csv"
        ]
        
        for file_name in key_files:
            file_path = run_dir / file_name
            if file_path.exists():
                f.write(f"- `{file_name}`\n")
        
        f.write("\n## Verification\n")
        f.write("```bash\n")
        f.write("python experiments/pipeline_v2/scripts/common/make_manifest.py --verify MANIFEST.sha256\n")
        f.write("```\n")
    
    return repro_path

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate or verify SHA-256 manifest")
    parser.add_argument("directory", nargs="?", default=".", 
                       help="Directory to manifest (default: current)")
    parser.add_argument("--output", default="MANIFEST.sha256",
                       help="Output manifest file name")
    parser.add_argument("--verify", metavar="MANIFEST",
                       help="Verify files against manifest")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("--repro", action="store_true",
                       help="Also create REPRO_STEPS.md")
    
    args = parser.parse_args()
    
    if args.verify:
        # Verify mode
        manifest_path = Path(args.verify)
        print(f"Verifying manifest: {manifest_path}")
        
        valid, issues = verify_manifest(manifest_path, args.verbose)
        
        if valid:
            print("✅ All files match manifest")
            return 0
        else:
            print(f"❌ Verification failed: {len(issues)} issues")
            for issue in issues[:10]:  # Show first 10
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more")
            return 1
    else:
        # Generate mode
        root_dir = Path(args.directory)
        output_path = root_dir / args.output
        
        print(f"Generating manifest for: {root_dir}")
        
        manifest = generate_manifest(root_dir)
        write_manifest(manifest, output_path)
        
        print(f"✅ Manifest written: {output_path}")
        print(f"   Files: {len(manifest)}")
        
        # Create repro steps if requested
        if args.repro:
            config = {
                "seed": 1337,
                "campaign": "PV2-001",
                "mode": "explore" if "explore" in str(root_dir) else "confirm"
            }
            repro_path = create_repro_steps(root_dir, config)
            print(f"✅ Repro steps written: {repro_path}")
        
        return 0

if __name__ == "__main__":
    exit(main())