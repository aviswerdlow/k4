#!/usr/bin/env python3
"""Generate or verify MANIFEST.sha256 for results and data directories."""

import sys
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

from validate_bundle import validate_bundle


MANIFEST_VERSION = "1.0.0"


def sha256_file(path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_manifest(base_dir, manifest_path):
    """Generate MANIFEST.sha256 for all files in base_dir."""
    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"Error: Directory {base_dir} does not exist")
        return False

    # Validate JSON files before hashing
    if not validate_bundle(base_path, Path("scripts/schema"), mode="strict"):
        print("Schema validation failed; aborting manifest generation")
        return False

    commit_cmd = ["git", "rev-parse", "HEAD"]
    commit = subprocess.check_output(commit_cmd, text=True).strip()

    pins = []
    registry_dir = Path("data/registry")
    if registry_dir.exists():
        for reg in sorted(registry_dir.glob("*.sha256")):
            with open(reg, "r", encoding="utf-8") as f:
                line = f.readline().strip()
            if not line:
                continue
            expected, rel_path = line.split()
            policy_path = Path(rel_path)
            actual = sha256_file(policy_path)
            if actual != expected:
                print(f"Policy hash mismatch for {rel_path}")
                return False
            pins.append((policy_path.name, actual))

    print(f"Generating manifest for: {base_dir}")

    manifest_lines = [
        f"# manifest_version: {MANIFEST_VERSION}",
        f"# generated_at: {datetime.utcnow().isoformat()}Z",
        f"# git_commit: {commit}",
    ]
    for name, digest in pins:
        manifest_lines.append(f"# {name}: {digest}")
    file_count = 0

    for file_path in sorted(base_path.rglob("*")):
        if file_path.is_file() and not file_path.name.startswith("."):
            if file_path.name == "MANIFEST.sha256":
                continue
            rel_path = file_path.relative_to(base_path)
            file_hash = sha256_file(str(file_path))
            manifest_lines.append(f"{file_hash}  {rel_path}")
            file_count += 1
            if file_count % 10 == 0:
                print(f"  Processed {file_count} files...")

    with open(manifest_path, "w") as f:
        f.write("\n".join(manifest_lines) + "\n")

    print(f"Manifest written: {manifest_path}")
    print(f"Total files: {file_count}")
    return True


def verify_manifest(base_dir, manifest_path):
    """Verify MANIFEST.sha256 against actual files."""
    base_path = Path(base_dir)
    manifest_file = Path(manifest_path)

    if not base_path.exists():
        print(f"Error: Directory {base_dir} does not exist")
        return False

    if not manifest_file.exists():
        print(f"Error: Manifest {manifest_path} does not exist")
        return False

    print(f"Verifying manifest: {manifest_path}")

    with open(manifest_path, "r") as f:
        manifest_lines = []
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                manifest_lines.append(line)

    errors = []
    verified = 0

    for line in manifest_lines:
        if "  " not in line:
            continue
        expected_hash, rel_path = line.split("  ", 1)
        file_path = base_path / rel_path
        if not file_path.exists():
            errors.append(f"Missing file: {rel_path}")
            continue
        actual_hash = sha256_file(str(file_path))
        if actual_hash != expected_hash:
            errors.append(f"Hash mismatch: {rel_path}")
            errors.append(f"  Expected: {expected_hash}")
            errors.append(f"  Actual:   {actual_hash}")
        else:
            verified += 1

    print(f"Verified: {verified} files")

    if errors:
        print(f"\nErrors found ({len(errors)} issues):")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ All files verified successfully")
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python make_manifest.py <base_dir> [manifest_path]")
        print("  python make_manifest.py --check <base_dir> <manifest_path>")
        sys.exit(1)

    if sys.argv[1] == "--check":
        if len(sys.argv) != 4:
            print("Error: --check requires base_dir and manifest_path")
            sys.exit(1)
        base_dir = sys.argv[2]
        manifest_path = sys.argv[3]
        success = verify_manifest(base_dir, manifest_path)
        sys.exit(0 if success else 1)
    else:
        base_dir = sys.argv[1]
        manifest_path = (
            sys.argv[2]
            if len(sys.argv) > 2
            else str(Path(base_dir) / "MANIFEST.sha256")
        )
        success = generate_manifest(base_dir, manifest_path)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
