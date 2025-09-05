#!/usr/bin/env python3
"""
Generate SHA-256 manifest for alternates experiment directory.
"""

import hashlib
import sys
from pathlib import Path

def generate_manifest(base_dir):
    """Generate SHA-256 manifest for directory."""
    base_path = Path(base_dir)
    manifest_file = base_path / 'MANIFEST.sha256'
    
    entries = []
    
    # Walk directory tree
    for file_path in sorted(base_path.rglob('*')):
        if file_path.is_file() and file_path != manifest_file:
            # Skip existing manifests to avoid recursion
            if file_path.name == 'MANIFEST.sha256':
                continue
                
            # Calculate SHA-256
            with open(file_path, 'rb') as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            
            # Get relative path
            rel_path = file_path.relative_to(base_path)
            entries.append(f"{sha256}  {rel_path}")
    
    # Write manifest
    with open(manifest_file, 'w') as f:
        f.write('\n'.join(entries))
        f.write('\n')
    
    print(f"Generated manifest with {len(entries)} entries")
    print(f"Written to: {manifest_file}")
    
    return manifest_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)
    
    generate_manifest(sys.argv[1])