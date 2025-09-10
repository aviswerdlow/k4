#!/usr/bin/env python3
"""
Forward encoder for K4: PT + proof → CT
No ciphertext reading allowed - pure forward encoding.
"""

import json
import hashlib
import argparse
from pathlib import Path


def compute_class(i):
    """Compute class for position i."""
    return ((i % 2) * 3) + (i % 3)


def encode_char(p_char, k_val, family):
    """
    Encode a single character using the specified family.
    
    Args:
        p_char: plaintext character (A-Z)
        k_val: key value (0-25)
        family: encoding family (vigenere, beaufort, variant_beaufort)
    
    Returns:
        ciphertext character (A-Z)
    """
    p_val = ord(p_char) - ord('A')
    
    if family == "vigenere":
        c_val = (p_val + k_val) % 26
    elif family == "beaufort":
        c_val = (k_val - p_val) % 26
    elif family == "variant_beaufort":
        c_val = (p_val - k_val) % 26
    else:
        raise ValueError(f"Unknown family: {family}")
    
    return chr(c_val + ord('A'))


def forward_encode(plaintext, proof, explain_indices=None):
    """
    Forward encode plaintext to ciphertext using the proof.
    
    Args:
        plaintext: string of uppercase letters
        proof: dictionary containing per_class array
        explain_indices: list of indices to explain (0-based)
    
    Returns:
        ciphertext string
    """
    ciphertext = []
    explanations = []
    
    # Build lookup for class parameters
    class_params = {}
    for cls_data in proof["per_class"]:
        cls_id = cls_data["class_id"]
        class_params[cls_id] = {
            "family": cls_data["family"],
            "L": cls_data["L"],
            "phase": cls_data["phase"],
            "residues": cls_data["residues"]
        }
    
    for i, p_char in enumerate(plaintext):
        # Compute class
        cls = compute_class(i)
        
        # Get parameters for this class
        params = class_params[cls]
        family = params["family"]
        L_cls = params["L"]
        phase_cls = params["phase"]
        residues_cls = params["residues"]
        
        # Compute slot
        slot = (i - phase_cls) % L_cls
        
        # Get key value
        k_val = residues_cls[slot]
        
        # Encode character
        c_char = encode_char(p_char, k_val, family)
        ciphertext.append(c_char)
        
        # Store explanation if requested
        if explain_indices and i in explain_indices:
            p_val = ord(p_char) - ord('A')
            c_val = ord(c_char) - ord('A')
            
            if family == "vigenere":
                rule = f"C = P + K = {p_val} + {k_val} = {c_val} (mod 26)"
            elif family == "beaufort":
                rule = f"C = K - P = {k_val} - {p_val} = {c_val} (mod 26)"
            else:  # variant_beaufort
                rule = f"C = P - K = {p_val} - {k_val} = {c_val} (mod 26)"
            
            explanations.append({
                "index": i,
                "P(i)": p_char,
                "P_val": p_val,
                "class": cls,
                "slot": slot,
                "K": k_val,
                "family": family,
                "rule": rule,
                "C(i)": c_char,
                "C_val": c_val
            })
    
    return ''.join(ciphertext), explanations


def main():
    parser = argparse.ArgumentParser(description="Forward encode K4: PT + proof → CT")
    parser.add_argument("--pt", required=True, help="Path to plaintext file")
    parser.add_argument("--proof", required=True, help="Path to proof JSON file")
    parser.add_argument("--out", required=True, help="Output path for ciphertext")
    parser.add_argument("--sha", action="store_true", help="Compute SHA-256 of output")
    parser.add_argument("--explain", help="Comma-separated indices to explain (0-based)")
    
    args = parser.parse_args()
    
    # Read plaintext (letters only)
    with open(args.pt, 'r') as f:
        plaintext = f.read().strip().upper()
        # Remove any non-letter characters
        plaintext = ''.join(c for c in plaintext if c.isalpha())
    
    # Read proof
    with open(args.proof, 'r') as f:
        proof = json.load(f)
    
    # Parse explain indices if provided
    explain_indices = None
    if args.explain:
        explain_indices = [int(x) for x in args.explain.split(',')]
    
    # Forward encode
    ciphertext, explanations = forward_encode(plaintext, proof, explain_indices)
    
    # Write output
    with open(args.out, 'w') as f:
        f.write(ciphertext)
    
    print(f"✅ Encoded {len(plaintext)} letters → {args.out}")
    
    # Print explanations if requested
    if explanations:
        print("\n📊 Step-by-step encoding for requested indices:")
        print("-" * 80)
        for exp in explanations:
            print(f"\nIndex {exp['index']}:")
            print(f"  P({exp['index']}) = '{exp['P(i)']}' (value: {exp['P_val']})")
            print(f"  class = {exp['class']}")
            print(f"  slot = {exp['slot']}")
            print(f"  K = {exp['K']}")
            print(f"  family = {exp['family']}")
            print(f"  {exp['rule']}")
            print(f"  C({exp['index']}) = '{exp['C(i)']}' (value: {exp['C_val']})")
    
    # Compute SHA if requested
    if args.sha:
        sha256 = hashlib.sha256(ciphertext.encode()).hexdigest()
        print(f"\n🔐 SHA-256: {sha256}")
        
        # Check against expected
        expected_sha = "eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab"
        if sha256 == expected_sha:
            print(f"✅ SHA matches expected K4 ciphertext SHA!")
        else:
            print(f"❌ SHA mismatch! Expected: {expected_sha}")
    
    return 0


if __name__ == "__main__":
    exit(main())