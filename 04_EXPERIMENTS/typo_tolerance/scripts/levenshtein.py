#!/usr/bin/env python3
"""
Levenshtein distance implementation with optional orthographic equivalence mapping.
Supports U↔V equivalence for historical spelling variations.
"""

def levenshtein_distance(s1, s2, orth_map=None):
    """
    Calculate Levenshtein distance between two strings.
    
    Args:
        s1, s2: Input strings to compare
        orth_map: Optional dict for orthographic equivalence (e.g., {"U":"V","V":"U"})
                  Zero cost for mapped character substitutions
    
    Returns:
        int: Minimum edit distance (insertions, deletions, substitutions)
    """
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    
    # Convert to uppercase for consistency
    s1 = s1.upper()
    s2 = s2.upper()
    
    m, n = len(s1), len(s2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i  # Cost of deleting i characters
    for j in range(n + 1):
        dp[0][j] = j  # Cost of inserting j characters
    
    # Fill DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            char1, char2 = s1[i-1], s2[j-1]
            
            # Check for exact match
            if char1 == char2:
                substitute_cost = 0
            # Check for orthographic equivalence (zero cost)
            elif orth_map and char1 in orth_map and orth_map[char1] == char2:
                substitute_cost = 0
            elif orth_map and char2 in orth_map and orth_map[char2] == char1:
                substitute_cost = 0
            else:
                substitute_cost = 1
            
            dp[i][j] = min(
                dp[i-1][j] + 1,      # Deletion
                dp[i][j-1] + 1,      # Insertion  
                dp[i-1][j-1] + substitute_cost  # Substitution
            )
    
    return dp[m][n]


def is_fuzzy_match(token, vocab_list, max_distance=1, orth_map=None):
    """
    Check if token fuzzy-matches any vocabulary item within max_distance.
    
    Args:
        token: Input token to check
        vocab_list: List of vocabulary items to match against
        max_distance: Maximum allowed edit distance (default 1)
        orth_map: Optional orthographic equivalence mapping
    
    Returns:
        tuple: (matched_vocab_item, distance) or (None, float('inf')) if no match
    """
    if not token:
        return (None, float('inf'))
    
    # Short tokens require exact match to avoid false positives
    if len(token) <= 2:
        token_upper = token.upper()
        for vocab_item in vocab_list:
            if token_upper == vocab_item.upper():
                return (vocab_item, 0)
        return (None, float('inf'))
    
    best_match = None
    best_distance = float('inf')
    
    for vocab_item in vocab_list:
        distance = levenshtein_distance(token, vocab_item, orth_map)
        if distance <= max_distance and distance < best_distance:
            best_distance = distance
            best_match = vocab_item
    
    return (best_match, best_distance)


def test_levenshtein():
    """Test the Levenshtein implementation"""
    # Basic tests
    assert levenshtein_distance("", "") == 0
    assert levenshtein_distance("cat", "cat") == 0
    assert levenshtein_distance("cat", "bat") == 1
    assert levenshtein_distance("cat", "cats") == 1
    assert levenshtein_distance("cat", "at") == 1
    assert levenshtein_distance("kitten", "sitting") == 3
    
    # Orthographic equivalence tests
    orth_map = {"U": "V", "V": "U"}
    assert levenshtein_distance("COURSE", "COVRSE", orth_map) == 0
    assert levenshtein_distance("TRUE", "TRVE", orth_map) == 0
    assert levenshtein_distance("OBSERVE", "OBSERUE", orth_map) == 0
    
    # Fuzzy matching tests
    vocab = ["READ", "SEE", "COURSE", "TRUE", "BERLIN", "CLOCK"]
    
    # Exact matches
    assert is_fuzzy_match("READ", vocab, 1)[0] == "READ"
    assert is_fuzzy_match("READ", vocab, 1)[1] == 0
    
    # Distance 1 matches
    result = is_fuzzy_match("REED", vocab, 1, orth_map)  # READ -> REED (substitute A->E)
    assert result[0] == "READ"
    assert result[1] == 1
    
    result = is_fuzzy_match("READS", vocab, 1, orth_map)  # READ -> READS (insert S)
    assert result[0] == "READ"
    assert result[1] == 1
    
    # With orthographic equivalence
    assert is_fuzzy_match("TRVE", vocab, 1, orth_map)[0] == "TRUE"
    assert is_fuzzy_match("TRVE", vocab, 1, orth_map)[1] == 0
    
    # No match beyond threshold
    assert is_fuzzy_match("XXXXXX", vocab, 1)[0] is None
    
    # Short tokens require exact match
    assert is_fuzzy_match("SE", vocab, 1)[0] is None  # Too short for fuzzy
    
    print("All Levenshtein tests passed!")


if __name__ == "__main__":
    test_levenshtein()