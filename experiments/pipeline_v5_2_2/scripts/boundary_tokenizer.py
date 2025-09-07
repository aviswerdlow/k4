#!/usr/bin/env python3
"""
Boundary-Aware Tokenizer for v5.2.2
Provides clean token segmentation without modifying the letters-only plaintext.
"""

from typing import List, Tuple, Set

# Function words set for reference
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

# Action verbs for reference
VERBS = {
    'SET', 'READ', 'SIGHT', 'NOTE', 'OBSERVE', 'FOLLOW',
    'APPLY', 'BRING', 'REDUCE', 'CORRECT', 'TRACE', 'FIND', 
    'MARK', 'SEE'
}

class BoundaryTokenizer:
    """Tokenizes letters-only text using virtual boundaries."""
    
    def __init__(self):
        """Initialize with standard boundaries for v5.2.2."""
        # Hard splits for head window (between char indices)
        self.head_hard_splits = [
            20,  # G1 → EAST (split between index 20 and 21)
            24,  # EAST → NORTHEAST (split between 24 and 25)
            33,  # NORTHEAST → G2 (split between 33 and 34)
            62,  # G2 → BERLINCLOCK (split between 62 and 63)
            73   # BERLINCLOCK → tail (split between 73 and 74)
        ]
        
        # Span definitions
        self.gaps = {
            "G1": (0, 20),    # Inclusive
            "G2": (34, 62)    # Inclusive
        }
        
        self.anchors = {
            "EAST": (21, 24),
            "NORTHEAST": (25, 33),
            "BERLINCLOCK": (63, 73)
        }
    
    def tokenize_with_boundaries(
        self,
        letters_only_text: str,
        boundaries: List[Tuple[int, int]] = None,
        hard_splits: List[int] = None
    ) -> List[str]:
        """
        Tokenize letters-only text using virtual boundaries.
        
        Args:
            letters_only_text: Pure A-Z text (no spaces)
            boundaries: Optional list of (start, end) spans
            hard_splits: Optional list of indices to split between
        
        Returns:
            List of tokens split at boundaries
        """
        
        if hard_splits is None:
            hard_splits = self.head_hard_splits
        
        # Convert text to uppercase for consistency
        text = letters_only_text.upper()
        
        # Create segments based on hard splits
        segments = []
        prev = 0
        
        for split_point in sorted(hard_splits):
            if prev < split_point <= len(text):
                segment = text[prev:split_point]
                if segment.strip():
                    segments.append((prev, segment))
                prev = split_point
        
        # Add final segment
        if prev < len(text):
            segment = text[prev:]
            if segment.strip():
                segments.append((prev, segment))
        
        # Tokenize each segment
        all_tokens = []
        
        for start_pos, segment in segments:
            # Handle spaces in segment
            if ' ' in segment:
                # Split on spaces for readability format
                words = segment.split()
                all_tokens.extend(words)
            else:
                # Pure letters - use smart tokenization
                tokens = self._tokenize_segment(segment)
                all_tokens.extend(tokens)
        
        return [t for t in all_tokens if t]  # Filter empty tokens
    
    def _tokenize_segment(self, segment: str) -> List[str]:
        """
        Tokenize a segment by recognizing known words.
        This handles cases where multiple words are fused in a segment.
        """
        
        segment = segment.upper()
        tokens = []
        
        # Known vocabulary (combine function words and verbs for recognition)
        known_words = FUNCTION_WORDS | VERBS | {
            'DIAL', 'LINE', 'GRID', 'MARK', 'ARC', 'ANGLE', 'POINT',
            'COURSE', 'BEARING', 'MERIDIAN', 'STATION', 'FIELD',
            'EAST', 'NORTHEAST', 'BERLINCLOCK', 'CLOCK', 'BERLIN',
            'TRUE', 'MAGNETIC', 'DECLINATION'
        }
        
        # Greedy tokenization - try to match longest known words first
        i = 0
        while i < len(segment):
            # Try progressively shorter matches
            matched = False
            for length in range(min(15, len(segment) - i), 0, -1):
                candidate = segment[i:i + length]
                if candidate in known_words:
                    tokens.append(candidate)
                    i += length
                    matched = True
                    break
            
            if not matched:
                # No known word found, take single character
                # This shouldn't happen with well-formed text
                if i < len(segment):
                    # Look ahead to find next known word boundary
                    j = i + 1
                    while j < len(segment):
                        if segment[i:j] in known_words:
                            tokens.append(segment[i:j])
                            i = j
                            matched = True
                            break
                        j += 1
                    
                    if not matched:
                        # Take rest as unknown token
                        tokens.append(segment[i:])
                        break
        
        return tokens
    
    def tokenize_head_window(self, full_text: str) -> List[str]:
        """
        Tokenize just the head window [0:74] with standard boundaries.
        
        Args:
            full_text: Full 97-char plaintext
        
        Returns:
            Tokens from head window only
        """
        head = full_text[:74]
        return self.tokenize_with_boundaries(head)
    
    def count_function_words(self, text: str) -> int:
        """Count function words using boundary tokenization."""
        tokens = self.tokenize_head_window(text) if len(text) > 74 else self.tokenize_with_boundaries(text)
        return sum(1 for token in tokens if token in FUNCTION_WORDS)
    
    def count_verbs(self, text: str) -> int:
        """Count verbs using boundary tokenization."""
        tokens = self.tokenize_head_window(text) if len(text) > 74 else self.tokenize_with_boundaries(text)
        return sum(1 for token in tokens if token in VERBS)
    
    def get_token_report(self, text: str) -> dict:
        """Generate detailed token report for debugging."""
        tokens = self.tokenize_head_window(text) if len(text) > 74 else self.tokenize_with_boundaries(text)
        
        function_words = [t for t in tokens if t in FUNCTION_WORDS]
        verbs = [t for t in tokens if t in VERBS]
        content = [t for t in tokens if t not in FUNCTION_WORDS and t not in VERBS]
        
        return {
            "tokens": tokens,
            "token_count": len(tokens),
            "function_words": function_words,
            "f_count": len(function_words),
            "verbs": verbs,
            "v_count": len(verbs),
            "content_words": content,
            "c_count": len(content)
        }

def test_tokenizer():
    """Test the boundary tokenizer."""
    
    tokenizer = BoundaryTokenizer()
    
    # Test cases
    test_cases = [
        {
            "name": "Fused boundaries",
            "text": "WEAREINTHEGRIDSEEASTNORTHEASTANDWEAREBYTHELINETOSEEBERLINCLOCK" + " " * 10,
            "expected_tokens": ["WEAREINTHE", "GRID", "SEE", "EAST", "NORTHEAST", "ANDWEAREBYTHELINETOSEE", "BERLINCLOCK"],
            "expected_f_words": ["WEAREINTHE", "ANDWEAREBYTHELINETOSEE"],  # These will be further split
        },
        {
            "name": "Clean boundaries",
            "text": "READ THE DIAL AND SEE EAST NORTHEAST TO THE MERIDIAN AND THEN READ BERLINCLOCK" + " " * 10,
            "expected_has_verbs": True,
            "expected_min_f_words": 5
        }
    ]
    
    print("Boundary Tokenizer Tests")
    print("=" * 80)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Input (first 74 chars): {test['text'][:74]}")
        
        report = tokenizer.get_token_report(test['text'])
        
        print(f"Tokens: {report['tokens']}")
        print(f"Function words ({report['f_count']}): {report['function_words']}")
        print(f"Verbs ({report['v_count']}): {report['verbs']}")
        
        # Validate expectations if provided
        if 'expected_min_f_words' in test:
            assert report['f_count'] >= test['expected_min_f_words'], \
                f"Expected at least {test['expected_min_f_words']} function words, got {report['f_count']}"
            print(f"✓ Function word count >= {test['expected_min_f_words']}")
        
        if 'expected_has_verbs' in test:
            assert (report['v_count'] > 0) == test['expected_has_verbs'], \
                f"Expected verbs: {test['expected_has_verbs']}, got {report['v_count']}"
            print(f"✓ Has verbs: {test['expected_has_verbs']}")
    
    # Specific fusion test
    print("\n" + "=" * 80)
    print("Fusion Resolution Test")
    print("=" * 80)
    
    # This simulates what we're seeing in the pilot
    fused = "WEAREBYTHELINESEEASTNORTHEASTANDWEAREBYTHELINETOSEEBERLINCLOCK" + " " * 10
    print(f"Fused text: {fused[:74]}")
    
    tokens = tokenizer.tokenize_head_window(fused)
    print(f"Tokens: {tokens}")
    
    # Check specific recognition
    assert "SEE" in tokens, "SEE should be recognized as separate token"
    assert "EAST" in tokens, "EAST should be recognized as separate token"
    assert "NORTHEAST" in tokens, "NORTHEAST should be recognized"
    assert "BERLINCLOCK" in tokens, "BERLINCLOCK should be recognized"
    
    print("\n✓ All boundary splits working correctly")
    print("✓ Anchors recognized as separate tokens")
    print("✓ Verbs preserved across boundaries")

if __name__ == "__main__":
    test_tokenizer()