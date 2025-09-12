#!/usr/bin/env python3
"""
tokenize_v21.py - Boundary-aware tokenization v2.1 (report-only)

Splits only "THEJOY" at indices 74..79 into "THE"|"JOY" for reporting and tie-break.
The decision pipeline still uses v2 (no inferred splits) for near/phrase/nulls.
"""

import json
import argparse

def load_canonical_cuts(cuts_file):
    """Load canonical cuts for tokenization."""
    with open(cuts_file, 'r') as f:
        data = json.load(f)
        if 'canonical_cuts' in data:
            return data['canonical_cuts']
        elif 'cuts_inclusive_0idx' in data:
            return data['cuts_inclusive_0idx']
        else:
            raise KeyError("No canonical cuts found in JSON")

def tokenize_v2(text, cuts):
    """Standard v2 tokenization - no inferred splits."""
    tokens = []
    prev = 0
    
    for cut in sorted(cuts):
        if cut > len(text):
            break
        if cut > prev:
            token = text[prev:cut].strip()
            if token:
                tokens.append(token)
            prev = cut
    
    # Add final token
    if prev < len(text):
        token = text[prev:].strip()
        if token:
            tokens.append(token)
    
    return tokens

def tokenize_v21(text, cuts):
    """
    Boundary-aware tokenization v2.1
    
    Special rule: If letters[74:80] == 'THEJOY', split the final glued token
    that spans into position 74 into parts, with 'THE' at 74-76 and 'JOY' at 77-79.
    For head window [0..74], count only 'THE' since 'JOY' lies outside.
    """
    # First get standard v2 tokens
    tokens = tokenize_v2(text, cuts)
    
    # Check if we have the THEJOY boundary case
    if len(text) >= 80 and text[74:80] == 'THEJOY':
        # Find which token spans position 74
        pos = 0
        for i, token in enumerate(tokens):
            token_end = pos + len(token)
            
            # Check if this token spans across position 74
            if pos <= 74 < token_end:
                # This token spans the boundary
                # The boundary is at position 74, so we need to check if THEJOY starts there
                # Get the part of the token before position 74
                prefix_len = 74 - pos
                prefix = token[:prefix_len] if prefix_len > 0 else ""
                
                # The part from position 74 onwards should be THEJOY...
                # Since text[74:80] == 'THEJOY', we split there
                new_tokens = tokens[:i]
                
                # Add the prefix part if it exists (e.g., 'K' from 'KTHEJO')
                if prefix:
                    new_tokens.append(prefix)
                
                # Add 'THE' as a separate token
                new_tokens.append('THE')
                
                # Add 'JOY' as a separate token  
                new_tokens.append('JOY')
                
                # Check if there's more after position 80 in the original token
                # The original token ends at token_end
                if token_end > 80:
                    # There's more content after 'THEJOY' in this token
                    remainder_start = 80 - pos
                    remainder = token[remainder_start:]
                    if remainder:
                        new_tokens.append(remainder)
                
                # Add all subsequent tokens
                new_tokens.extend(tokens[i+1:])
                return new_tokens
            
            pos = token_end
    
    # No boundary case applies - return standard v2 tokens
    return tokens

def get_head_tokens(tokens, text_length=97, head_boundary=74):
    """Extract tokens that belong to the head window [0..74]."""
    head_tokens = []
    pos = 0
    
    for token in tokens:
        token_start = pos
        token_end = pos + len(token)
        
        # Include token if it starts within head window
        if token_start <= head_boundary:
            head_tokens.append(token)
            
            # Special case for v2.1: if token is 'JOY' at position 77-79, exclude it
            if token == 'JOY' and token_start == 77:
                head_tokens.pop()  # Remove 'JOY' as it's outside head
        
        pos = token_end
    
    return head_tokens

def count_function_words(tokens, fwords):
    """Count function words in token list."""
    fword_count = 0
    fword_list = []
    
    for token in tokens:
        if token.lower() in fwords:
            fword_count += 1
            fword_list.append(token.lower())
    
    return fword_count, fword_list

def main():
    parser = argparse.ArgumentParser(description='Tokenize with v2.1 boundary awareness')
    parser.add_argument('--text', required=True, help='Input text (or file path)')
    parser.add_argument('--cuts', required=True, help='Canonical cuts JSON')
    parser.add_argument('--fwords', required=True, help='Function words file')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Load text
    if args.text.endswith('.txt'):
        with open(args.text, 'r') as f:
            text = f.read().strip().upper()
    else:
        text = args.text.upper()
    
    # Load cuts
    cuts = load_canonical_cuts(args.cuts)
    
    # Load function words
    with open(args.fwords, 'r') as f:
        fwords = set(line.strip().lower() for line in f if line.strip())
    
    # Tokenize with both methods
    tokens_v2 = tokenize_v2(text, cuts)
    tokens_v21 = tokenize_v21(text, cuts)
    
    # Get head tokens
    head_tokens_v2 = get_head_tokens(tokens_v2, len(text))
    head_tokens_v21 = get_head_tokens(tokens_v21, len(text))
    
    # Count function words
    fcount_v2, flist_v2 = count_function_words(head_tokens_v2, fwords)
    fcount_v21, flist_v21 = count_function_words(head_tokens_v21, fwords)
    
    # Prepare output
    result = {
        'text_length': len(text),
        'letters_74_80': text[74:80] if len(text) >= 80 else None,
        'v2': {
            'tokens': tokens_v2,
            'head_tokens': head_tokens_v2,
            'head_fword_count': fcount_v2,
            'head_fwords': flist_v2
        },
        'v21': {
            'tokens': tokens_v21,
            'head_tokens': head_tokens_v21,
            'head_fword_count': fcount_v21,
            'head_fwords': flist_v21,
            'delta': fcount_v21 - fcount_v2
        },
        'boundary_split_applied': tokens_v2 != tokens_v21
    }
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(result, indent=2))
    
    # Summary
    print(f"\nBoundary v2.1 Analysis:")
    print(f"  Letters 74-80: {result['letters_74_80']}")
    print(f"  Boundary split applied: {result['boundary_split_applied']}")
    print(f"  v2 head function words: {fcount_v2}")
    print(f"  v21 head function words: {fcount_v21}")
    if result['boundary_split_applied']:
        print(f"  Delta: {result['v21']['delta']:+d}")

if __name__ == "__main__":
    main()