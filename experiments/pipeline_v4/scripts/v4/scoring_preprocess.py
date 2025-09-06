#!/usr/bin/env python3
"""
Deterministic preprocessing for scoring with proper blinding.
"""

import re
from typing import List, Set


class ScoringPreprocessor:
    """
    Single deterministic preprocessor for all scoring operations.
    Ensures no leakage between normal and ablation runs.
    """
    
    def __init__(self):
        # Define anchor terms to mask
        self.anchor_terms = [
            "EAST",
            "NORTHEAST", 
            "BERLINCLOCK"
        ]
        
        # Define narrative terms (Flint v2 vocabulary)
        self.narrative_terms = [
            "SLOWLY",
            "DIGITAL",
            "LANGLEY",
            "VIRTUALLY",
            "INVISIBLE",
            "SHADOW",
            "FORCES",
            "DEBRIS"
        ]
        
        self.mask_token = "X"
    
    def preprocess_for_scoring(
        self, 
        raw_text: str, 
        mask_anchors: bool = True,
        mask_narrative: bool = True
    ) -> str:
        """
        Single preprocessing function used by ALL policies.
        
        Args:
            raw_text: Input text
            mask_anchors: Whether to mask anchor terms
            mask_narrative: Whether to mask narrative terms
            
        Returns:
            Preprocessed text with consistent masking
        """
        # 1. Normalize to uppercase, remove non-alpha
        text = ''.join(c for c in raw_text.upper() if c.isalpha())
        
        # 2. Build mask terms list based on flags
        mask_terms = []
        if mask_anchors:
            mask_terms.extend(self.anchor_terms)
        if mask_narrative:
            mask_terms.extend(self.narrative_terms)
        
        # 3. Apply masking with exact boundaries
        # Sort by length descending to match longest first
        mask_terms.sort(key=len, reverse=True)
        
        for term in mask_terms:
            # Replace with mask tokens of same length
            mask_replacement = self.mask_token * len(term)
            text = text.replace(term, mask_replacement)
        
        return text
    
    def tokenize_for_ngrams(self, text: str) -> List[str]:
        """
        Tokenize text for n-gram scoring, breaking at mask boundaries.
        
        Args:
            text: Preprocessed text
            
        Returns:
            List of valid n-gram segments (no cross-mask n-grams)
        """
        # Split on mask token runs
        segments = []
        current = []
        
        for char in text:
            if char == self.mask_token:
                if current:
                    segments.append(''.join(current))
                    current = []
            else:
                current.append(char)
        
        if current:
            segments.append(''.join(current))
        
        # Filter out very short segments
        return [seg for seg in segments if len(seg) >= 2]
    
    def compute_ngram_score(self, text: str, n: int = 3) -> float:
        """
        Compute n-gram score with proper window breaking.
        
        Args:
            text: Preprocessed text
            n: N-gram size
            
        Returns:
            N-gram score (avoiding cross-mask boundaries)
        """
        segments = self.tokenize_for_ngrams(text)
        
        if not segments:
            return 0.0
        
        total_score = 0.0
        total_ngrams = 0
        
        for segment in segments:
            # Only compute n-grams within segments
            for i in range(len(segment) - n + 1):
                ngram = segment[i:i+n]
                # Here you would look up ngram probability
                # For now, use simple heuristic
                if 'E' in ngram or 'T' in ngram or 'A' in ngram:
                    total_score += 1.0
                total_ngrams += 1
        
        if total_ngrams == 0:
            return 0.0
        
        return total_score / total_ngrams