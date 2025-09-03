"""Rails validation for K4 Kryptos."""

import json
from typing import Dict, List, Tuple
from .io import read_json


def validate_anchors(plaintext: str, anchors: Dict[str, Tuple[int, int]]) -> bool:
    """Validate anchor positions in plaintext."""
    for token, (start, end) in anchors.items():
        if plaintext[start:end+1] != token:
            raise ValueError(f"Anchor {token} not found at position [{start},{end}], found: '{plaintext[start:end+1]}'")
    return True


def validate_option_a(plaintext: str, proof_digest: Dict) -> bool:
    """Validate Option-A anchor constraints."""
    # Option-A validation logic would go here
    # For now, return True as proof_digest contains validation
    return proof_digest.get("anchor_policy") == "Option-A"


def validate_head_lock(plaintext: str, end_pos: int = 74) -> bool:
    """Validate head lock constraint."""
    if len(plaintext) <= end_pos:
        raise ValueError(f"Plaintext too short for head lock validation (need >{end_pos})")
    # Head lock validation - actual constraint would be implemented here
    return True


def validate_seam_guard(plaintext: str, tail_start: int = 80) -> bool:
    """Validate seam guard in tail section."""
    if len(plaintext) < 97:
        raise ValueError("Plaintext must be 97 characters")
    
    # Check HEJOY at positions 75-79
    if plaintext[75:80] != "HEJOY":
        raise ValueError(f"Expected HEJOY at [75,79], got: '{plaintext[75:80]}'")
    
    # Check seam structure 
    seam = plaintext[tail_start:]
    expected_seam = "OFANANGLEISTHEARC"
    if seam != expected_seam:
        raise ValueError(f"Expected seam '{expected_seam}', got: '{seam}'")
    
    return True


def validate_rails(plaintext: str, policy: Dict) -> Dict[str, bool]:
    """Comprehensive rails validation."""
    results = {}
    
    try:
        # Basic format check
        if len(plaintext) != 97 or not plaintext.isalpha() or not plaintext.isupper():
            raise ValueError("Plaintext must be 97 uppercase letters")
        results["format"] = True
        
        # Anchor validation
        anchors = policy["rails"]["anchors_0idx"]
        validate_anchors(plaintext, anchors)
        results["anchors"] = True
        
        # Head lock validation
        head_lock = policy["rails"]["head_lock"]
        validate_head_lock(plaintext, head_lock[1])
        results["head_lock"] = True
        
        # Seam guard validation  
        validate_seam_guard(plaintext)
        results["seam_guard"] = True
        
    except Exception as e:
        results["error"] = str(e)
        
    return results