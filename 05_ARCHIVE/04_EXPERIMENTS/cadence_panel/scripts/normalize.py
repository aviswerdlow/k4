#!/usr/bin/env python3
"""
normalize.py - Text normalization for cadence panel analysis
Uppercase, strip punctuation (track X count), squeeze spaces
"""

import re
import argparse


def normalize_text(text, track_x=True):
    """
    Normalize text for style metrics:
    1. Uppercase only (already)
    2. Alpha only - strip punctuation except track X counts
    3. Whitespace squeeze to single spaces
    
    Returns:
        tuple: (normalized_text, x_count_per_100_tokens)
    """
    # Ensure uppercase
    text = text.upper()
    
    # Count X's before removing them
    x_count = text.count('X') if track_x else 0
    
    # Remove all non-alpha characters except spaces
    # This removes punctuation, numbers, and X
    text = re.sub(r'[^A-Z\s]', ' ', text)
    
    # Squeeze multiple spaces to single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Calculate X per 100 tokens (if text has tokens)
    tokens = text.split()
    x_per_100 = (x_count * 100.0 / len(tokens)) if tokens else 0.0
    
    return text, x_per_100


def normalize_file(filepath, track_x=True):
    """Normalize text from file"""
    with open(filepath, 'r') as f:
        text = f.read()
    return normalize_text(text, track_x)


def main():
    parser = argparse.ArgumentParser(description='Normalize text for cadence analysis')
    parser.add_argument('input', help='Input text file')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--no-track-x', action='store_true', 
                       help='Do not track X count')
    
    args = parser.parse_args()
    
    normalized, x_per_100 = normalize_file(args.input, track_x=not args.no_track_x)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(normalized)
        if not args.no_track_x:
            print(f"X count per 100 tokens: {x_per_100:.2f}")
    else:
        print(normalized)
        if not args.no_track_x:
            print(f"\n# X count per 100 tokens: {x_per_100:.2f}")


if __name__ == '__main__':
    main()