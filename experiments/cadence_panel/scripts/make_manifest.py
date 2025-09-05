#!/usr/bin/env python3
"""
make_manifest.py - Generate SHA-256 manifest for experiments folder
"""

import hashlib
import argparse
from pathlib import Path
import json
from datetime import datetime


def compute_file_hash(filepath):
    """Compute SHA-256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_manifest(directory, output_file=None):
    """
    Generate SHA-256 manifest for all files in directory.
    
    Args:
        directory: path to directory to scan
        output_file: where to save manifest (default: directory/MANIFEST.sha256)
        
    Returns:
        dict: manifest data
    """
    directory = Path(directory)
    
    if output_file is None:
        output_file = directory / "MANIFEST.sha256"
    
    manifest = {
        'generated': datetime.now().isoformat(),
        'directory': str(directory.absolute()),
        'files': {}
    }
    
    # Walk through all files
    for filepath in sorted(directory.rglob('*')):
        if filepath.is_file():
            # Skip the manifest file itself
            if filepath.samefile(output_file) if output_file.exists() else False:
                continue
            
            # Compute relative path
            rel_path = filepath.relative_to(directory)
            
            # Compute hash
            file_hash = compute_file_hash(filepath)
            
            # Get file size
            file_size = filepath.stat().st_size
            
            manifest['files'][str(rel_path)] = {
                'sha256': file_hash,
                'size': file_size
            }
    
    # Save manifest
    with open(output_file, 'w') as f:
        # Write in sorted, deterministic format
        for rel_path in sorted(manifest['files'].keys()):
            entry = manifest['files'][rel_path]
            f.write(f"{entry['sha256']}  {rel_path}\n")
    
    # Also save JSON version
    json_file = output_file.with_suffix('.json')
    with open(json_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest written to: {output_file}")
    print(f"JSON manifest written to: {json_file}")
    print(f"Total files: {len(manifest['files'])}")
    
    return manifest


def verify_manifest(manifest_file, verbose=False):
    """
    Verify files against a manifest.
    
    Args:
        manifest_file: path to MANIFEST.sha256
        verbose: print each file check
        
    Returns:
        tuple: (is_valid, errors)
    """
    manifest_path = Path(manifest_file)
    directory = manifest_path.parent
    
    errors = []
    checked = 0
    
    with open(manifest_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('  ', 1)
            if len(parts) != 2:
                errors.append(f"Invalid manifest line: {line}")
                continue
            
            expected_hash, rel_path = parts
            filepath = directory / rel_path
            
            if not filepath.exists():
                errors.append(f"Missing file: {rel_path}")
                continue
            
            actual_hash = compute_file_hash(filepath)
            
            if actual_hash != expected_hash:
                errors.append(f"Hash mismatch: {rel_path}")
            elif verbose:
                print(f"✓ {rel_path}")
            
            checked += 1
    
    is_valid = len(errors) == 0
    
    if verbose or not is_valid:
        print(f"\nChecked {checked} files")
        if errors:
            print(f"Found {len(errors)} errors:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
    
    return is_valid, errors


def main():
    parser = argparse.ArgumentParser(description='Generate or verify SHA-256 manifest')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--verify', action='store_true',
                       help='Verify existing manifest instead of generating')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verify:
        # Verify mode
        manifest_file = Path(args.directory) / "MANIFEST.sha256"
        if args.output:
            manifest_file = Path(args.output)
        
        if not manifest_file.exists():
            print(f"Error: Manifest file not found: {manifest_file}")
            return 1
        
        is_valid, errors = verify_manifest(manifest_file, args.verbose)
        
        if is_valid:
            print("✓ All files verified successfully")
            return 0
        else:
            print("✗ Verification failed")
            return 1
    else:
        # Generate mode
        generate_manifest(args.directory, args.output)
        return 0


if __name__ == '__main__':
    exit(main())