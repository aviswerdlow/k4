"""I/O utilities for K4 analysis."""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional


def read_text(path: str) -> str:
    """Read text file."""
    return Path(path).read_text(encoding='utf-8').strip()


def write_text(path: str, content: str) -> None:
    """Write text file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding='utf-8')


def read_json(path: str) -> Dict[str, Any]:
    """Read JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data: Dict[str, Any], indent: int = 2) -> None:
    """Write JSON file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)


def sha256_file(path: str) -> str:
    """Calculate SHA-256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def sha256_string(text: str) -> str:
    """Calculate SHA-256 hash of string."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def generate_hashes_file(directory: str, output_path: str) -> None:
    """Generate SHA-256 hashes for all files in directory."""
    dir_path = Path(directory)
    hashes = []
    
    for file_path in sorted(dir_path.rglob('*')):
        if file_path.is_file() and not file_path.name.startswith('.'):
            rel_path = file_path.relative_to(dir_path)
            file_hash = sha256_file(str(file_path))
            hashes.append(f"{file_hash}  {rel_path}")
    
    write_text(output_path, '\n'.join(hashes) + '\n')