#!/usr/bin/env python3
"""
Generate SHA-256 manifests for all experiments.
"""

import hashlib
from pathlib import Path

def generate_manifest(directory):
    """Generate SHA-256 manifest for a directory."""
    manifest_lines = []
    
    for file in sorted(directory.rglob("*")):
        if file.is_file() and file.name != "MANIFEST.sha256":
            with open(file, 'rb') as f:
                hash_val = hashlib.sha256(f.read()).hexdigest()
            rel_path = file.relative_to(directory)
            manifest_lines.append(f"{hash_val}  {rel_path}")
    
    manifest_path = directory / "MANIFEST.sha256"
    if manifest_lines:
        with open(manifest_path, 'w') as f:
            f.write('\n'.join(manifest_lines))
        print(f"✓ Generated manifest for {directory.name}")
    else:
        print(f"⚠ No files to manifest in {directory.name}")

def main():
    """Generate manifests for all experiment directories."""
    base_dir = Path(__file__).parent
    
    # List of experiment directories
    experiments = [
        "sensitivity_strip",
        "p74_publish", 
        "controls_grid",
        "policy_prereg",
        "blinded_panel"
    ]
    
    print("Generating manifests for all experiments...")
    print("="*50)
    
    for exp in experiments:
        exp_dir = base_dir / exp
        if exp_dir.exists():
            generate_manifest(exp_dir)
        else:
            print(f"✗ Directory not found: {exp}")
    
    print("="*50)
    print("✓ All manifests generated")

if __name__ == "__main__":
    main()