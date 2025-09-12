#!/usr/bin/env python3
"""
Shared utilities for the Core-Hardening Program.
Provides common functions for all three studies.
"""

import hashlib
import json
import csv
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ProcessPoolExecutor
import os

# Master seed for deterministic randomness
MASTER_SEED = 1337

# Canonical paths
CT_PATH = Path("02_DATA/ciphertext_97.txt")
PT_PATH = Path("01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt")

# Canonical CT hash for verification
CANONICAL_CT_HASH = "eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab"

# Baseline anchors (0-index)
BASELINE_ANCHORS = {
    "EAST": (21, 24),       # indices 21-24 inclusive
    "NORTHEAST": (25, 33),  # indices 25-33 inclusive
    "BERLIN": (63, 68),     # indices 63-68 inclusive
    "CLOCK": (69, 73)       # indices 69-73 inclusive
}

# Cipher families
FAMILIES = ['vigenere', 'variant_beaufort', 'beaufort']
ADDITIVE_FAMILIES = ['vigenere', 'variant_beaufort']

# Period constraints
MIN_L = 10
MAX_L = 22


def letter_to_num(letter: str) -> int:
    """Convert A-Z to 0-25."""
    return ord(letter) - ord('A')


def num_to_letter(num: int) -> str:
    """Convert 0-25 to A-Z."""
    return chr(num + ord('A'))


def compute_sha256(text: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(text.encode()).hexdigest()


def generate_seed(study: str, label: str) -> int:
    """Generate deterministic seed for a specific context."""
    seed_str = f"CORE_HARDEN|{study}|{label}|{MASTER_SEED}"
    hash_bytes = hashlib.sha256(seed_str.encode()).digest()
    # Extract low 64 bits
    seed_u64 = int.from_bytes(hash_bytes[:8], 'little')
    return seed_u64


def load_ciphertext() -> str:
    """Load and verify canonical ciphertext."""
    with open(CT_PATH, 'r') as f:
        ct = f.read().strip()
    
    # Verify hash
    ct_hash = compute_sha256(ct)
    if ct_hash != CANONICAL_CT_HASH:
        raise ValueError(f"CT hash mismatch: got {ct_hash}, expected {CANONICAL_CT_HASH}")
    
    return ct


def load_plaintext() -> str:
    """Load baseline plaintext."""
    with open(PT_PATH, 'r') as f:
        pt = f.read().strip()
    return pt


def compute_baseline_class(i: int) -> int:
    """Compute baseline class using the 1989 formula."""
    return ((i % 2) * 3) + (i % 3)


def compute_residue(c_val: int, p_val: int, family: str) -> int:
    """
    Compute the residue K from ciphertext and plaintext values.
    
    For finding K (given C and P):
    - Vigenere: K = C - P (mod 26)
    - Beaufort: K = P + C (mod 26)
    - Variant-Beaufort: K = P - C (mod 26)
    """
    if family == 'vigenere':
        return (c_val - p_val) % 26
    elif family == 'beaufort':
        return (p_val + c_val) % 26
    elif family == 'variant_beaufort':
        return (p_val - c_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")


def decrypt_cell(c_val: int, k_val: int, family: str) -> int:
    """Apply family-specific decrypt rule."""
    if family == 'vigenere':
        return (c_val - k_val) % 26
    elif family == 'beaufort':
        return (k_val - c_val) % 26
    elif family == 'variant_beaufort':
        return (c_val + k_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")


def is_anchor_index(i: int, anchors: Dict[str, Tuple[int, int]] = None) -> bool:
    """Check if index i is in an anchor span."""
    if anchors is None:
        anchors = BASELINE_ANCHORS
    
    for name, (start, end) in anchors.items():
        if start <= i <= end:
            return True
    return False


def get_anchor_plaintext(anchors: Dict[str, Tuple[int, int]] = None) -> Dict[int, str]:
    """Get plaintext characters at anchor positions."""
    if anchors is None:
        anchors = BASELINE_ANCHORS
    
    anchor_pt = {}
    
    # Known anchor strings
    anchor_strings = {
        "EAST": "EAST",
        "NORTHEAST": "NORTHEAST",
        "BERLIN": "BERLIN",
        "CLOCK": "CLOCK"
    }
    
    for name, (start, end) in anchors.items():
        anchor_str = anchor_strings[name]
        for offset, char in enumerate(anchor_str):
            idx = start + offset
            if idx <= end:  # Safety check
                anchor_pt[idx] = char
    
    return anchor_pt


def solve_class_wheel(
    class_id: int,
    class_indices: List[int],
    ciphertext: str,
    plaintext_constraints: Dict[int, str],
    families_to_try: List[str] = None,
    enforce_option_a: bool = True
) -> Optional[Dict]:
    """
    Solve for the wheel configuration of a single class.
    
    Args:
        class_id: The class ID (0-5 for baseline)
        class_indices: List of indices belonging to this class
        ciphertext: Full ciphertext string
        plaintext_constraints: Dict mapping index -> plaintext character
        families_to_try: List of families to try (default: all)
        enforce_option_a: Whether to enforce Option-A (no K=0 at anchors for additive)
    
    Returns:
        Dict with family, L, phase, residues, etc. or None if no valid config
    """
    if families_to_try is None:
        families_to_try = FAMILIES
    
    valid_configs = []
    
    for family in families_to_try:
        for L in range(MIN_L, MAX_L + 1):
            for phase in range(L):
                wheel = {}
                forced_anchors = []
                valid = True
                
                for i in class_indices:
                    if i not in plaintext_constraints:
                        continue  # Skip unconstrained positions
                    
                    c_val = letter_to_num(ciphertext[i])
                    p_val = letter_to_num(plaintext_constraints[i])
                    
                    # Compute residue K
                    k_val = compute_residue(c_val, p_val, family)
                    
                    # Option-A check
                    if enforce_option_a and is_anchor_index(i):
                        if k_val == 0 and family in ADDITIVE_FAMILIES:
                            valid = False
                            break
                    
                    # Compute slot
                    slot = (i - phase) % L
                    
                    # Check consistency
                    if slot in wheel:
                        if wheel[slot] != k_val:
                            valid = False
                            break
                    else:
                        wheel[slot] = k_val
                    
                    # Record anchor residue
                    if is_anchor_index(i):
                        forced_anchors.append({
                            'index': i,
                            'slot': slot,
                            'residue': k_val,
                            'C': ciphertext[i],
                            'P': plaintext_constraints[i],
                            'family': family
                        })
                
                if not valid:
                    continue
                
                # Build complete residue array
                residues = []
                present_slots_mask = []
                
                for slot in range(L):
                    if slot in wheel:
                        residues.append(wheel[slot])
                        present_slots_mask.append('1')
                    else:
                        residues.append(None)
                        present_slots_mask.append('0')
                
                present_slots_mask_str = ''.join(present_slots_mask)
                missing_slots = present_slots_mask.count('0')
                
                # Check Option-A violations
                optionA_violations = []
                if enforce_option_a:
                    for anchor in forced_anchors:
                        if anchor['residue'] == 0 and family in ADDITIVE_FAMILIES:
                            optionA_violations.append({
                                'index': anchor['index'],
                                'violation': 'K=0 at anchor for additive family'
                            })
                
                valid_configs.append({
                    'class_id': class_id,
                    'family': family,
                    'L': L,
                    'phase': phase,
                    'residues': residues,
                    'present_slots_mask': present_slots_mask_str,
                    'forced_anchor_residues': forced_anchors,
                    'optionA_checks': optionA_violations,
                    'missing_slots': missing_slots
                })
    
    if not valid_configs:
        return None
    
    # Sort by: 1) no Option-A violations, 2) fewer missing slots, 3) smaller L
    valid_configs.sort(key=lambda x: (
        len(x['optionA_checks']),
        x['missing_slots'],
        x['L'],
        FAMILIES.index(x['family']),
        x['phase']
    ))
    
    best = valid_configs[0]
    del best['missing_slots']
    return best


def derive_plaintext_from_wheels(
    ciphertext: str,
    wheels: Dict[int, Dict],
    class_function
) -> str:
    """
    Derive plaintext from ciphertext using wheel configurations.
    
    Args:
        ciphertext: The ciphertext to decrypt
        wheels: Dict mapping class_id -> wheel configuration
        class_function: Function that takes index i and returns class_id
    
    Returns:
        Derived plaintext string
    """
    plaintext = []
    
    for i in range(len(ciphertext)):
        c_val = letter_to_num(ciphertext[i])
        class_id = class_function(i)
        
        if class_id not in wheels:
            # No wheel for this class
            plaintext.append('?')
            continue
        
        config = wheels[class_id]
        family = config['family']
        L = config['L']
        phase = config['phase']
        residues = config['residues']
        
        # Get K from wheel
        slot = (i - phase) % L
        k_val = residues[slot]
        
        if k_val is None:
            # Slot not filled
            plaintext.append('?')
            continue
        
        # Decrypt
        p_val = decrypt_cell(c_val, k_val, family)
        plaintext.append(num_to_letter(p_val))
    
    return ''.join(plaintext)


def write_proof_json(
    filepath: Path,
    skeleton_spec: str,
    anchors: Dict[str, Tuple[int, int]],
    wheels: Dict[int, Dict],
    pt_sha256: str,
    ct_sha256: str,
    seed_u64: int,
    notes: str = ""
) -> None:
    """Write a proof JSON file compatible with proof_digest_enhanced.json format."""
    
    # Format anchors
    anchor_data = {}
    for name, (start, end) in anchors.items():
        anchor_data[name] = [start, end]
    
    # Check if BERLIN/CLOCK are combined
    if "BERLINCLOCK" in anchors:
        anchor_data["mode"] = "COMBINED"
    else:
        anchor_data["mode"] = "SPLIT"
    
    # Format wheels
    wheel_data = []
    for class_id in sorted(wheels.keys()):
        config = wheels[class_id]
        wheel_data.append({
            "class_id": class_id,
            "family": config['family'],
            "L": config['L'],
            "phase": config['phase'],
            "residues": config['residues'],
            "present_slots_mask": config.get('present_slots_mask', '1' * config['L'])
        })
    
    proof = {
        "schema_version": "1.0.0",
        "class_formula": skeleton_spec,
        "class_formula_note": notes if notes else "Core hardening study",
        "anchors": anchor_data,
        "wheels": wheel_data,
        "forced_anchor_residues": [],
        "optionA_checks": [],
        "pt_sha256_derived": pt_sha256,
        "ct_sha256": ct_sha256,
        "notes": notes,
        "seed_u64": seed_u64
    }
    
    # Collect forced anchor residues from all wheels
    for class_id, config in wheels.items():
        if 'forced_anchor_residues' in config:
            proof["forced_anchor_residues"].extend(config['forced_anchor_residues'])
        if 'optionA_checks' in config:
            proof["optionA_checks"].extend(config['optionA_checks'])
    
    with open(filepath, 'w') as f:
        json.dump(proof, f, indent=2)


def write_csv_row(
    csv_writer,
    row_data: Dict[str, Any]
) -> None:
    """Write a row to CSV with proper formatting."""
    csv_writer.writerow(row_data)


def generate_manifest(directory: Path) -> None:
    """Generate MANIFEST.sha256 for a directory."""
    manifest_lines = []
    
    for filepath in sorted(directory.rglob('*')):
        if filepath.is_file() and filepath.name != 'MANIFEST.sha256':
            # Compute file hash
            with open(filepath, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Relative path from directory
            rel_path = filepath.relative_to(directory)
            manifest_lines.append(f"{file_hash}  {rel_path}")
    
    manifest_path = directory / 'MANIFEST.sha256'
    with open(manifest_path, 'w') as f:
        f.write('\n'.join(manifest_lines))
        if manifest_lines:
            f.write('\n')


def create_run_log(
    study_dir: Path,
    study_name: str,
    start_time: float,
    end_time: float,
    attempted: int,
    feasible: int,
    notes: str = ""
) -> None:
    """Create RUN_LOG.md for a study."""
    import platform
    import sys
    
    runtime = end_time - start_time
    
    content = f"""# Run Log - {study_name}

## Environment
- Python: {sys.version}
- Platform: {platform.platform()}
- Machine: {platform.machine()}
- Processor: {platform.processor()}

## Execution
- Start: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(start_time))}
- End: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(end_time))}
- Runtime: {runtime:.2f} seconds
- Master Seed: {MASTER_SEED}

## Results
- Scenarios Attempted: {attempted}
- Feasible Solutions: {feasible}
- Success Rate: {(feasible/attempted*100) if attempted > 0 else 0:.2f}%

## Notes
{notes if notes else 'No additional notes.'}
"""
    
    log_path = study_dir / 'RUN_LOG.md'
    with open(log_path, 'w') as f:
        f.write(content)


def create_summary_json(
    study_dir: Path,
    attempted: int,
    feasible: int,
    matching_pt_sha: int,
    distinct_tails: int,
    notes: str = ""
) -> None:
    """Create SUMMARY.json for a study."""
    summary = {
        "attempted": attempted,
        "feasible": feasible,
        "matching_pt_sha": matching_pt_sha,
        "distinct_tails": distinct_tails,
        "notes": notes
    }
    
    summary_path = study_dir / 'SUMMARY.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)


# Parallelization helper
def get_executor(max_workers: int = None) -> ProcessPoolExecutor:
    """Get a process pool executor with appropriate worker count."""
    if max_workers is None:
        max_workers = min(8, os.cpu_count() or 1)
    return ProcessPoolExecutor(max_workers=max_workers)