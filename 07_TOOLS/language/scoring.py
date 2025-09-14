#!/usr/bin/env python3
"""
Language scoring utilities for cryptanalysis
"""

from typing import Dict, List, Set
import math
import re

class LanguageScorer:
    """
    Score text quality using various metrics
    """
    
    def __init__(self):
        # Common English words for quick checks
        self.common_words = {
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
            'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'HIS',
            'HOW', 'ITS', 'NOW', 'NEW', 'TWO', 'WAY', 'WHO', 'HAS',
            'MAY', 'SAY', 'SHE', 'USE', 'MAKE', 'THAN', 'FIRST',
            'BEEN', 'CALL', 'COME', 'MADE', 'FIND', 'GIVE', 'HAND',
            'HERE', 'HOME', 'KEEP', 'KNOW', 'LAST', 'LONG', 'MAKE',
            'MANY', 'OVER', 'SUCH', 'TAKE', 'THEM', 'TIME', 'VERY',
            'WEEK', 'WELL', 'WORK', 'YEAR', 'BACK', 'GOOD', 'HAVE',
            'INTO', 'JUST', 'LIKE', 'LOOK', 'MOST', 'ONLY', 'SOME',
            'THAT', 'THEY', 'THIS', 'WANT', 'WHAT', 'WHEN', 'WITH',
            'BERLIN', 'CLOCK', 'EAST', 'NORTH', 'NORTHEAST', 'WEST',
            'SOUTH', 'TIME', 'ZONE', 'WATCH', 'HOUR', 'SHADOW'
        }
        
        # English letter frequencies (%)
        self.letter_freq = {
            'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
            'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
            'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
            'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
            'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10,
            'Z': 0.07
        }
        
        # Common bigrams
        self.common_bigrams = {
            'TH', 'HE', 'IN', 'EN', 'NT', 'RE', 'ER', 'AN', 'TI', 'ES',
            'ON', 'AT', 'SE', 'ND', 'OR', 'AR', 'AL', 'TE', 'CO', 'DE',
            'TO', 'RA', 'ET', 'ED', 'IT', 'SA', 'EM', 'RO', 'CH', 'OT',
            'IS', 'HA', 'ST', 'NG', 'HI', 'LE', 'SO', 'AS', 'NO', 'NE'
        }
        
        # Common trigrams
        self.common_trigrams = {
            'THE', 'AND', 'THA', 'ENT', 'ION', 'TIO', 'FOR', 'NDE',
            'HAS', 'NCE', 'EDT', 'TIS', 'OFT', 'STH', 'MEN', 'THI',
            'ING', 'HER', 'HAT', 'HIS', 'TER', 'WAS', 'ARE', 'NOT'
        }
    
    def word_score(self, text: str) -> float:
        """Score based on presence of common words"""
        text_upper = text.upper()
        score = 0.0
        words_found = []
        
        # Check for word presence
        for word in self.common_words:
            if word in text_upper:
                score += len(word) * 2  # Weight by word length
                words_found.append(word)
        
        return score
    
    def frequency_score(self, text: str) -> float:
        """Score based on letter frequency distribution"""
        text_upper = text.upper()
        text_letters = [c for c in text_upper if c.isalpha()]
        
        if not text_letters:
            return 0.0
        
        # Count letter frequencies
        freq_counts = {}
        for letter in text_letters:
            freq_counts[letter] = freq_counts.get(letter, 0) + 1
        
        # Convert to percentages
        total = len(text_letters)
        freq_pct = {k: (v / total) * 100 for k, v in freq_counts.items()}
        
        # Calculate chi-squared statistic
        chi_squared = 0.0
        for letter in self.letter_freq:
            expected = self.letter_freq[letter]
            observed = freq_pct.get(letter, 0)
            if expected > 0:
                chi_squared += ((observed - expected) ** 2) / expected
        
        # Convert to score (lower chi-squared is better)
        # Use negative so higher score is better
        return -chi_squared
    
    def ngram_score(self, text: str, n: int = 2) -> float:
        """Score based on n-gram frequencies"""
        text_upper = text.upper()
        text_letters = ''.join([c for c in text_upper if c.isalpha()])
        
        if len(text_letters) < n:
            return 0.0
        
        score = 0.0
        
        # Extract n-grams
        for i in range(len(text_letters) - n + 1):
            ngram = text_letters[i:i+n]
            
            if n == 2 and ngram in self.common_bigrams:
                score += 1
            elif n == 3 and ngram in self.common_trigrams:
                score += 2
        
        return score
    
    def combined_score(self, text: str) -> float:
        """Combined scoring using multiple metrics"""
        # Weight different scoring methods
        word_weight = 5.0
        freq_weight = 1.0
        bigram_weight = 2.0
        trigram_weight = 3.0
        
        score = (
            self.word_score(text) * word_weight +
            self.frequency_score(text) * freq_weight +
            self.ngram_score(text, 2) * bigram_weight +
            self.ngram_score(text, 3) * trigram_weight
        )
        
        return score
    
    def find_words(self, text: str, min_length: int = 3) -> List[str]:
        """Find all dictionary words in text"""
        text_upper = text.upper()
        words_found = []
        
        for word in self.common_words:
            if len(word) >= min_length and word in text_upper:
                words_found.append(word)
        
        # Sort by length (longest first)
        words_found.sort(key=len, reverse=True)
        
        return words_found
    
    def has_function_words(self, text: str) -> bool:
        """Check if text contains function words"""
        function_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 
                         'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE'}
        
        text_upper = text.upper()
        for word in function_words:
            if word in text_upper:
                return True
        
        return False


def score_text(text: str) -> float:
    """Quick scoring function"""
    scorer = LanguageScorer()
    return scorer.combined_score(text)


def find_words_in_text(text: str) -> List[str]:
    """Find dictionary words in text"""
    scorer = LanguageScorer()
    return scorer.find_words(text)