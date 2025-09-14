#!/usr/bin/env python3
"""
Plan P: Token segmentation using dynamic programming
Segments non-anchor text into survey/bearing tokens
"""

import json
from typing import List, Tuple, Dict, Optional
from token_dictionary import TOKEN_SET, TOKEN_SCORES, MAX_TOKEN_LENGTH

def dp_segment(text: str, token_set: set = TOKEN_SET, 
                token_scores: dict = TOKEN_SCORES) -> Tuple[List[str], float]:
    """
    Dynamic programming segmentation to find optimal token split
    
    Args:
        text: Text to segment (uppercase)
        token_set: Set of valid tokens
        token_scores: Scoring for each token
    
    Returns:
        Tuple of (token_list, total_score)
    """
    n = len(text)
    if n == 0:
        return [], 0.0
    
    # DP arrays
    dp = [float('-inf')] * (n + 1)  # Best score ending at position i
    parent = [-1] * (n + 1)  # Parent pointer for reconstruction
    token_at = [''] * (n + 1)  # Token that got us here
    
    dp[0] = 0  # Base case: empty string has score 0
    
    # Fill DP table
    for i in range(1, n + 1):
        # Try all possible token endings at position i
        for j in range(max(0, i - MAX_TOKEN_LENGTH), i):
            substring = text[j:i]
            
            if substring in token_set:
                # Valid token found
                score = dp[j] + token_scores.get(substring, len(substring))
                
                if score > dp[i]:
                    dp[i] = score
                    parent[i] = j
                    token_at[i] = substring
            elif len(substring) == 1:
                # Single character fallback (penalty)
                score = dp[j] - 2  # Penalty for non-token char
                
                if score > dp[i]:
                    dp[i] = score
                    parent[i] = j
                    token_at[i] = substring
    
    # Reconstruct path
    tokens = []
    pos = n
    while pos > 0:
        if parent[pos] == -1:
            # No valid segmentation found
            break
        tokens.append(token_at[pos])
        pos = parent[pos]
    
    tokens.reverse()
    
    return tokens, dp[n]

def segment_with_anchors(full_text: str, anchor_positions: Dict[str, Tuple[int, int]]) -> Dict:
    """
    Segment text while preserving anchor positions
    
    Args:
        full_text: Complete text including anchors
        anchor_positions: Dict of anchor_name -> (start, end) positions
    
    Returns:
        Dictionary with segmentation results
    """
    # Extract non-anchor positions
    locked_positions = set()
    for start, end in anchor_positions.values():
        for i in range(start, end + 1):
            locked_positions.add(i)
    
    # Build non-anchor text
    non_anchor_chars = []
    non_anchor_positions = []
    for i, char in enumerate(full_text):
        if i not in locked_positions:
            non_anchor_chars.append(char)
            non_anchor_positions.append(i)
    
    non_anchor_text = ''.join(non_anchor_chars)
    
    # Segment non-anchor text
    tokens, score = dp_segment(non_anchor_text.upper())
    
    # Analyze token categories
    from token_dictionary import get_token_category
    
    categories = {}
    for token in tokens:
        if len(token) > 1:  # Skip single chars
            cat = get_token_category(token)
            if cat:
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(token)
    
    return {
        'full_text': full_text,
        'non_anchor_text': non_anchor_text,
        'tokens': tokens,
        'score': score,
        'num_tokens': len(tokens),
        'categories': categories,
        'token_coverage': sum(len(t) for t in tokens if len(t) > 1) / len(non_anchor_text)
    }

def analyze_homophonic_output(json_file: str = 'stabilized_homophonic.json'):
    """
    Apply token segmentation to homophonic output
    """
    # Load homophonic result
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    plaintext = data['plaintext']
    
    # Define anchor positions
    anchors = {
        "EAST": (21, 24),
        "NORTHEAST": (25, 33),
        "BERLIN": (63, 68),
        "CLOCK": (69, 73)
    }
    
    print("=" * 80)
    print("PLAN P: TOKEN SEGMENTATION ANALYSIS")
    print("=" * 80)
    
    # Segment the text
    result = segment_with_anchors(plaintext, anchors)
    
    print(f"\nNon-anchor text: {result['non_anchor_text']}")
    print(f"\nSegmentation score: {result['score']:.2f}")
    print(f"Number of tokens: {result['num_tokens']}")
    print(f"Token coverage: {result['token_coverage']:.2%}")
    
    print("\nTokens found:")
    # Group tokens by length for better display
    tokens_by_length = {}
    for token in result['tokens']:
        length = len(token)
        if length not in tokens_by_length:
            tokens_by_length[length] = []
        tokens_by_length[length].append(token)
    
    for length in sorted(tokens_by_length.keys(), reverse=True):
        if length > 1:  # Skip single chars
            print(f"  Length {length}: {', '.join(tokens_by_length[length])}")
    
    print("\nToken categories:")
    for category, tokens in result['categories'].items():
        print(f"  {category}: {', '.join(set(tokens))}")
    
    # Try to build coherent message
    print("\nPossible interpretations:")
    
    # Look for patterns like "GO [direction] [number]"
    tokens = result['tokens']
    for i in range(len(tokens) - 2):
        if tokens[i] in ['GO', 'SET', 'TURN', 'WALK']:
            if tokens[i+1] in TOKEN_SET:
                print(f"  Command: {tokens[i]} {tokens[i+1]} {tokens[i+2] if i+2 < len(tokens) else ''}")
    
    # Look for bearing patterns
    for i in range(len(tokens) - 1):
        if tokens[i] in ['AZ', 'BEARING', 'AZIMUTH', 'TRUE', 'MAG']:
            print(f"  Bearing: {tokens[i]} {tokens[i+1] if i+1 < len(tokens) else ''}")
    
    return result

def compare_segmentations():
    """
    Compare different segmentation strategies
    """
    # Load homophonic result
    with open('stabilized_homophonic.json', 'r') as f:
        data = json.load(f)
    
    plaintext = data['plaintext']
    
    # Extract non-anchor text
    anchors = {
        "EAST": (21, 24),
        "NORTHEAST": (25, 33),
        "BERLIN": (63, 68),
        "CLOCK": (69, 73)
    }
    
    locked = set()
    for start, end in anchors.values():
        for i in range(start, end + 1):
            locked.add(i)
    
    non_anchor = ''.join([plaintext[i] for i in range(len(plaintext)) if i not in locked])
    
    print("\n" + "=" * 80)
    print("SEGMENTATION COMPARISON")
    print("=" * 80)
    
    # Strategy 1: Greedy longest match
    print("\n1. Greedy Longest Match:")
    text = non_anchor.upper()
    pos = 0
    greedy_tokens = []
    while pos < len(text):
        found = False
        for length in range(min(MAX_TOKEN_LENGTH, len(text) - pos), 0, -1):
            candidate = text[pos:pos+length]
            if candidate in TOKEN_SET:
                greedy_tokens.append(candidate)
                pos += length
                found = True
                break
        if not found:
            greedy_tokens.append(text[pos])
            pos += 1
    
    print(f"  Tokens: {' '.join(greedy_tokens[:20])}...")
    
    # Strategy 2: DP optimal
    print("\n2. Dynamic Programming Optimal:")
    dp_tokens, dp_score = dp_segment(non_anchor.upper())
    print(f"  Tokens: {' '.join(dp_tokens[:20])}...")
    print(f"  Score: {dp_score:.2f}")
    
    # Strategy 3: DP with modified scoring (prefer survey terms)
    print("\n3. DP with Survey-Weighted Scoring:")
    modified_scores = TOKEN_SCORES.copy()
    for token in TOKEN_SET:
        from token_dictionary import get_token_category
        cat = get_token_category(token)
        if cat in ['SURVEY_ACTIONS', 'SURVEY_UNITS', 'BEARING_TERMS']:
            modified_scores[token] *= 2  # Double weight for survey terms
    
    survey_tokens, survey_score = dp_segment(non_anchor.upper(), TOKEN_SET, modified_scores)
    print(f"  Tokens: {' '.join(survey_tokens[:20])}...")
    print(f"  Score: {survey_score:.2f}")

def main():
    """Run token segmentation analysis"""
    print("Loading token dictionary...")
    print(f"Total tokens: {len(TOKEN_SET)}")
    
    # Analyze homophonic output
    result = analyze_homophonic_output()
    
    # Compare strategies
    compare_segmentations()
    
    # Save results
    output = {
        'segmentation': result,
        'interpretation': 'Survey/bearing instructions possibly encoded'
    }
    
    with open('token_segmentation.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Results saved to token_segmentation.json")

if __name__ == "__main__":
    main()