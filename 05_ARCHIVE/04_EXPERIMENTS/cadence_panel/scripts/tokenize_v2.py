#!/usr/bin/env python3
"""
tokenize_v2.py - Tokenization v2 for candidate heads
Uses canonical_cuts.json for 0..74 boundaries
No inferred splits: tokens spanning 74 counted once
"""

import json
import argparse


def tokenize_head_v2(head_text, cuts_path):
    """
    Tokenize head (0..74) using canonical cuts.
    
    Args:
        head_text: 75-character uppercase head text
        cuts_path: path to canonical_cuts.json
        
    Returns:
        list: tokens from head (0..74)
    """
    # Load canonical cuts
    with open(cuts_path, 'r') as f:
        cuts_data = json.load(f)
    
    # Get inclusive end positions (0-indexed)
    if 'canonical_cuts' in cuts_data:
        cuts = cuts_data['canonical_cuts']
    elif 'cuts_inclusive_0idx' in cuts_data:
        cuts = cuts_data['cuts_inclusive_0idx']
    else:
        raise ValueError(f"Could not find cuts in {cuts_path}")
    
    # Ensure head is exactly 75 characters
    if len(head_text) != 75:
        raise ValueError(f"Head must be exactly 75 characters, got {len(head_text)}")
    
    tokens = []
    start = 0
    
    for end_inclusive in cuts:
        # Convert inclusive to exclusive for Python slicing
        end_exclusive = end_inclusive + 1
        
        # Only include tokens that end at or before position 74
        if end_inclusive <= 74:
            token = head_text[start:end_exclusive]
            tokens.append(token)
            start = end_exclusive
        else:
            # Token spans beyond 74 - include it once if it starts before 75
            if start < 75:
                # Take only the part up to position 74
                token = head_text[start:75]  # Up to but not including 75
                tokens.append(token)
            break
    
    return tokens


def tokenize_k_text(text):
    """
    Simple whitespace tokenization for K1-K3 texts.
    
    Args:
        text: normalized text (already uppercase, alpha-only)
        
    Returns:
        list: tokens
    """
    return text.split()


def main():
    parser = argparse.ArgumentParser(description='Tokenize text using v2 rules')
    parser.add_argument('input', help='Input text or file')
    parser.add_argument('--cuts', required=True, help='Path to canonical_cuts.json')
    parser.add_argument('--type', choices=['head', 'k-text'], default='head',
                       help='Type of tokenization')
    parser.add_argument('--file', action='store_true',
                       help='Input is a file path')
    
    args = parser.parse_args()
    
    # Read input
    if args.file:
        with open(args.input, 'r') as f:
            text = f.read().strip()
    else:
        text = args.input
    
    # Tokenize based on type
    if args.type == 'head':
        tokens = tokenize_head_v2(text, args.cuts)
    else:
        tokens = tokenize_k_text(text)
    
    # Output
    print(f"Tokens ({len(tokens)}):")
    for i, token in enumerate(tokens):
        print(f"  {i:3d}: '{token}'")
    
    print(f"\nTotal tokens: {len(tokens)}")


if __name__ == '__main__':
    main()