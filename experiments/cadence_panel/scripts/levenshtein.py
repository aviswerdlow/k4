#!/usr/bin/env python3
"""
levenshtein.py - Levenshtein distance computation with optional U↔V equivalence
Used for misspelling tolerance in content token matching
"""

import argparse


def levenshtein_distance(s1, s2, uv_equiv=False):
    """
    Compute Levenshtein distance between two strings.
    
    Args:
        s1, s2: strings to compare
        uv_equiv: if True, treat U and V as equivalent
        
    Returns:
        int: minimum edit distance
    """
    # Apply U/V equivalence if requested
    if uv_equiv:
        s1 = s1.replace('V', 'U')
        s2 = s2.replace('V', 'U')
    
    # Standard DP algorithm for Levenshtein distance
    m, n = len(s1), len(s2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No change needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],      # Deletion
                    dp[i][j-1],      # Insertion
                    dp[i-1][j-1]     # Substitution
                )
    
    return dp[m][n]


def find_close_matches(word, vocabulary, max_distance=1, uv_equiv=False):
    """
    Find all words in vocabulary within max_distance edits of word.
    
    Args:
        word: target word
        vocabulary: list/set of reference words
        max_distance: maximum allowed edit distance
        uv_equiv: if True, treat U and V as equivalent
        
    Returns:
        list of (matched_word, distance) tuples
    """
    matches = []
    for vocab_word in vocabulary:
        dist = levenshtein_distance(word, vocab_word, uv_equiv)
        if dist <= max_distance:
            matches.append((vocab_word, dist))
    
    # Sort by distance, then alphabetically
    matches.sort(key=lambda x: (x[1], x[0]))
    return matches


def check_k_quirks(word):
    """
    Check if word matches known K-style quirks.
    
    Returns:
        tuple: (is_quirk, standard_form, distance)
    """
    quirks = {
        'IQLUSION': 'ILLUSION',
        'UNDERGRUUND': 'UNDERGROUND',
        'DESPARATLY': 'DESPERATELY'
    }
    
    if word in quirks:
        standard = quirks[word]
        dist = levenshtein_distance(word, standard)
        return True, standard, dist
    
    # Check if word is distance-1 from any quirk
    for quirk, standard in quirks.items():
        if levenshtein_distance(word, quirk) <= 1:
            return True, standard, levenshtein_distance(word, standard)
    
    return False, None, None


def main():
    parser = argparse.ArgumentParser(description='Compute Levenshtein distance')
    parser.add_argument('word1', help='First word')
    parser.add_argument('word2', help='Second word')
    parser.add_argument('--uv-equiv', action='store_true',
                       help='Treat U and V as equivalent')
    parser.add_argument('--check-quirks', action='store_true',
                       help='Check if word1 is a K-style quirk')
    
    args = parser.parse_args()
    
    if args.check_quirks:
        is_quirk, standard, dist = check_k_quirks(args.word1.upper())
        if is_quirk:
            print(f"{args.word1} is a K-quirk for {standard} (distance: {dist})")
        else:
            print(f"{args.word1} is not a known K-quirk")
    
    dist = levenshtein_distance(args.word1.upper(), args.word2.upper(), args.uv_equiv)
    print(f"Distance: {dist}")


if __name__ == '__main__':
    main()