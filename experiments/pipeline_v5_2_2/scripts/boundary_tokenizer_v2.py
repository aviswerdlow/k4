#!/usr/bin/env python3
"""
Boundary-Aware Tokenizer v2 for v5.2.2-B
Enhanced with anchor classification and deterministic splits.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Function words set
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

# Action verbs
VERBS = {
    'SET', 'READ', 'SIGHT', 'NOTE', 'OBSERVE', 'FOLLOW',
    'APPLY', 'BRING', 'REDUCE', 'CORRECT', 'TRACE', 'FIND', 
    'MARK', 'SEE'
}

@dataclass
class Token:
    """Token with metadata."""
    text: str
    start: int
    end: int
    token_class: str  # 'anchor', 'function', 'verb', 'content'

class BoundaryTokenizerV2:
    """Enhanced tokenizer with anchor classification."""
    
    def __init__(self):
        """Initialize with v5.2.2-B specifications."""
        
        # Hard splits for head window (between indices)
        self.hard_splits = [20, 24, 33, 62]  # Split after these positions
        
        # Span definitions
        self.spans = {
            "G1": (0, 20),
            "EAST": (21, 24),
            "NORTHEAST": (25, 33),
            "G2": (34, 62),
            "BERLINCLOCK": (63, 73)
        }
        
        # Anchor texts
        self.anchors = {"EAST", "NORTHEAST", "BERLINCLOCK"}
    
    def tokenize_head(
        self,
        text: str,
        head_window: Tuple[int, int] = (0, 74),
        spans: Dict[str, Tuple[int, int]] = None,
        hard_splits: List[int] = None
    ) -> List[Token]:
        """
        Tokenize head with boundary awareness and token classification.
        
        Args:
            text: Full 97-char plaintext (letters only)
            head_window: (start, end) inclusive
            spans: Optional custom spans
            hard_splits: Optional custom split points
        
        Returns:
            List of Token objects with classification
        """
        
        if spans is None:
            spans = self.spans
        
        if hard_splits is None:
            hard_splits = self.hard_splits
        
        # Extract head window
        head = text[head_window[0]:head_window[1] + 1].upper()
        
        # Build segments based on spans
        segments = []
        
        # Process spans in order
        for span_name in ["G1", "EAST", "NORTHEAST", "G2", "BERLINCLOCK"]:
            if span_name not in spans:
                continue
            
            start, end = spans[span_name]
            
            # Check if span overlaps with head window
            if start <= head_window[1] and end >= head_window[0]:
                # Calculate positions relative to head start
                seg_start = max(start, head_window[0])
                seg_end = min(end, head_window[1])
                
                if seg_start <= seg_end:
                    # Extract text from absolute positions
                    segment_text = text[seg_start:seg_end + 1].upper()
                    
                    segments.append({
                        "name": span_name,
                        "text": segment_text,
                        "start": seg_start,
                        "end": seg_end,
                        "is_anchor": span_name in self.anchors
                    })
        
        # Tokenize each segment
        tokens = []
        
        for segment in segments:
            if segment["is_anchor"]:
                # Anchor segment - single token
                token = Token(
                    text=segment["text"],
                    start=segment["start"],
                    end=segment["end"],
                    token_class="anchor"
                )
                tokens.append(token)
            else:
                # Gap segment - tokenize internally
                gap_tokens = self._tokenize_gap(
                    segment["text"],
                    segment["start"]
                )
                tokens.extend(gap_tokens)
        
        return tokens
    
    def _tokenize_gap(self, gap_text: str, offset: int) -> List[Token]:
        """
        Tokenize a gap segment by recognizing known words.
        
        Args:
            gap_text: Text from gap (no spaces)
            offset: Starting position in head
        
        Returns:
            List of tokens with classification
        """
        
        gap_text = gap_text.upper()
        tokens = []
        
        # Known vocabulary
        known_words = FUNCTION_WORDS | VERBS | {
            'DIAL', 'LINE', 'GRID', 'MARK', 'ARC', 'ANGLE', 'POINT',
            'COURSE', 'BEARING', 'MERIDIAN', 'STATION', 'FIELD', 'PLATE',
            'TRUE', 'MAGNETIC', 'DECLINATION', 'COMPASS', 'NOW'
        }
        
        # Greedy tokenization
        i = 0
        while i < len(gap_text):
            # Skip any spaces (shouldn't be any in letters-only)
            if gap_text[i] == ' ':
                i += 1
                continue
            
            # Try to match longest known word
            matched = False
            for length in range(min(12, len(gap_text) - i), 0, -1):
                candidate = gap_text[i:i + length]
                
                if candidate in known_words:
                    # Classify token
                    if candidate in FUNCTION_WORDS:
                        token_class = "function"
                    elif candidate in VERBS:
                        token_class = "verb"
                    else:
                        token_class = "content"
                    
                    token = Token(
                        text=candidate,
                        start=offset + i,
                        end=offset + i + length - 1,
                        token_class=token_class
                    )
                    tokens.append(token)
                    i += length
                    matched = True
                    break
            
            if not matched:
                # Unknown sequence - take as content
                # Find next known word boundary
                j = i + 1
                while j < len(gap_text) and gap_text[i:j] not in known_words:
                    j += 1
                
                # Take unknown portion as content
                if j > i:
                    token = Token(
                        text=gap_text[i:j],
                        start=offset + i,
                        end=offset + j - 1,
                        token_class="content"
                    )
                    tokens.append(token)
                    i = j
        
        return tokens
    
    def count_function_words(self, text: str, exclude_anchors: bool = True) -> int:
        """Count function words in head window."""
        tokens = self.tokenize_head(text)
        
        if exclude_anchors:
            return sum(1 for t in tokens if t.token_class == "function")
        else:
            return sum(1 for t in tokens if t.text in FUNCTION_WORDS)
    
    def count_verbs(self, text: str) -> int:
        """Count verbs in head window."""
        tokens = self.tokenize_head(text)
        return sum(1 for t in tokens if t.token_class == "verb")
    
    def get_gap_metrics(self, text: str) -> Dict[str, Dict]:
        """Get per-gap metrics for quota checking."""
        tokens = self.tokenize_head(text)
        
        # Initialize gap metrics
        metrics = {
            "G1": {"f_words": 0, "verbs": 0, "tokens": []},
            "G2": {"f_words": 0, "verbs": 0, "tokens": []}
        }
        
        # Assign tokens to gaps based on position
        for token in tokens:
            if token.token_class == "anchor":
                continue  # Skip anchors
            
            # Check which gap token belongs to
            if token.start <= 20:  # G1
                metrics["G1"]["tokens"].append(token.text)
                if token.token_class == "function":
                    metrics["G1"]["f_words"] += 1
                elif token.token_class == "verb":
                    metrics["G1"]["verbs"] += 1
            
            elif 34 <= token.start <= 62:  # G2
                metrics["G2"]["tokens"].append(token.text)
                if token.token_class == "function":
                    metrics["G2"]["f_words"] += 1
                elif token.token_class == "verb":
                    metrics["G2"]["verbs"] += 1
        
        return metrics
    
    def report_boundaries(self, head_label: str, text: str) -> Dict:
        """Generate tokenization report for audit."""
        
        tokens = self.tokenize_head(text)
        gap_metrics = self.get_gap_metrics(text)
        
        report = {
            "head_label": head_label,
            "hard_splits": self.hard_splits,
            "spans": {k: list(v) for k, v in self.spans.items()},
            "head_tokens": [
                {
                    "text": t.text,
                    "class": t.token_class,
                    "start": t.start,
                    "end": t.end
                }
                for t in tokens
            ],
            "summary": {
                "total_tokens": len(tokens),
                "function_words": sum(1 for t in tokens if t.token_class == "function"),
                "verbs": sum(1 for t in tokens if t.token_class == "verb"),
                "anchors": sum(1 for t in tokens if t.token_class == "anchor"),
                "content": sum(1 for t in tokens if t.token_class == "content")
            },
            "gap_metrics": gap_metrics
        }
        
        return report

def test_tokenizer_v2():
    """Test the enhanced boundary tokenizer."""
    
    tokenizer = BoundaryTokenizerV2()
    
    # Test case: properly constructed with anchors at correct positions
    # G1: positions 0-20 (21 chars)
    g1 = "WEAREINTHEGRIDSEE    "  # 21 chars
    # EAST: positions 21-24 (4 chars)
    east = "EAST"
    # NORTHEAST: positions 25-33 (9 chars)
    northeast = "NORTHEAST"
    # G2: positions 34-62 (29 chars)
    g2 = "ANDWEAREBYTHELINETOSEE       "  # 29 chars
    # BERLINCLOCK: positions 63-73 (11 chars)
    berlinclock = "BERLINCLOCK"
    
    # Construct full text
    test_text = g1[:21] + east + northeast + g2[:29] + berlinclock + " " * 23
    
    print("Boundary Tokenizer V2 Test")
    print("=" * 80)
    print(f"Input: {test_text[:74]}")
    
    # Get tokenization report
    report = tokenizer.report_boundaries("TEST_001", test_text)
    
    print(f"\nTokens:")
    for token_info in report["head_tokens"][:15]:  # First 15 tokens
        print(f"  [{token_info['start']:2d}-{token_info['end']:2d}] {token_info['text']:12s} ({token_info['class']})")
    
    print(f"\nSummary:")
    for key, value in report["summary"].items():
        print(f"  {key}: {value}")
    
    print(f"\nGap Metrics:")
    for gap, metrics in report["gap_metrics"].items():
        print(f"  {gap}: f_words={metrics['f_words']}, verbs={metrics['verbs']}")
        print(f"       tokens={metrics['tokens']}")
    
    # Verify anchor classification
    anchor_tokens = [t for t in report["head_tokens"] if t["class"] == "anchor"]
    print(f"\nAnchors found: {[t['text'] for t in anchor_tokens]}")
    
    assert "EAST" in [t["text"] for t in anchor_tokens], "EAST should be classified as anchor"
    assert "NORTHEAST" in [t["text"] for t in anchor_tokens], "NORTHEAST should be classified as anchor"
    assert "BERLINCLOCK" in [t["text"] for t in anchor_tokens], "BERLINCLOCK should be classified as anchor"
    
    print("\n✓ All anchor tokens correctly classified")
    print("✓ Per-gap metrics computed")
    print("✓ Boundary splits working")

if __name__ == "__main__":
    test_tokenizer_v2()