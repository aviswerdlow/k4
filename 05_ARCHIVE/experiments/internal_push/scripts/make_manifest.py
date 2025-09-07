#!/usr/bin/env python3
"""
Generate SHA-256 manifest for internal push experiment directory.
"""

import hashlib
import sys
from pathlib import Path

def generate_manifest(base_dir):
    """Generate SHA-256 manifest for directory."""
    base_path = Path(base_dir)
    
    entries = []
    
    # Walk directory tree
    for file_path in sorted(base_path.rglob('*')):
        if file_path.is_file():
            # Skip manifest files
            if file_path.name == 'MANIFEST.sha256':
                continue
                
            # Calculate SHA-256
            with open(file_path, 'rb') as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            
            # Get relative path
            rel_path = file_path.relative_to(base_path)
            entries.append(f"{sha256}  {rel_path}")
    
    # Write manifest
    manifest_content = '\n'.join(entries)
    if entries:
        manifest_content += '\n'
    
    manifest_file = base_path / 'MANIFEST.sha256'
    with open(manifest_file, 'w') as f:
        f.write(manifest_content)
    
    print(f"Generated manifest with {len(entries)} entries")
    print(f"Written to: {manifest_file}")
    
    return manifest_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)
    
    generate_manifest(sys.argv[1])