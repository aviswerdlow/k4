#!/usr/bin/env python3
"""
Hardened scorer for Plan O validation
No anchor leakage, fixed objectives, linguistic constraints
"""

import hashlib
import json
from typing import Dict, List, Tuple, Set
from collections import Counter

class HardenedScorer:
    """
    Frozen scorer with anchor masking and linguistic constraints
    """
    
    def __init__(self):
        # FROZEN wordlists - no modifications allowed
        self.content_words = {
            'ABOUT', 'AFTER', 'AGAIN', 'AGAINST', 'ALMOST', 'ALONE', 'ALONG',
            'ALREADY', 'ALTHOUGH', 'ALWAYS', 'AMONG', 'ANOTHER', 'ANYONE',
            'ANYTHING', 'AROUND', 'BECAUSE', 'BEFORE', 'BEHIND', 'BEING',
            'BELOW', 'BETWEEN', 'BEYOND', 'BRING', 'CANNOT', 'COMES', 'COULD',
            'COURSE', 'DIFFERENT', 'DURING', 'EARLY', 'ENOUGH', 'EVERY',
            'EXAMPLE', 'FIRST', 'FOLLOW', 'FOUND', 'GENERAL', 'GIVEN',
            'GOING', 'GOVERNMENT', 'GREAT', 'GROUP', 'HANDS', 'HAVING',
            'HOWEVER', 'HUMAN', 'IMPORTANT', 'INFORMATION', 'INTEREST',
            'KNOWN', 'LARGE', 'LATER', 'LEAST', 'LEAVE', 'LEVEL', 'LITTLE',
            'LOCAL', 'MAKING', 'MEANS', 'MIGHT', 'MONEY', 'NEVER', 'NIGHT',
            'NUMBER', 'OFTEN', 'ORDER', 'OTHER', 'OTHERS', 'PEOPLE', 'PERHAPS',
            'PLACE', 'POINT', 'POSSIBLE', 'POWER', 'PRESENT', 'PROBLEM',
            'PUBLIC', 'QUESTION', 'RATHER', 'REALLY', 'REASON', 'RESULT',
            'RIGHT', 'SECOND', 'SEEMS', 'SEVERAL', 'SHALL', 'SHORT', 'SHOULD',
            'SINCE', 'SMALL', 'SOCIAL', 'SOMETHING', 'SPECIAL', 'STATE',
            'STILL', 'STUDY', 'SYSTEM', 'TAKEN', 'THEIR', 'THERE', 'THESE',
            'THING', 'THINGS', 'THINK', 'THOSE', 'THOUGH', 'THREE', 'THROUGH',
            'TODAY', 'TOGETHER', 'TOWARD', 'UNDER', 'UNDERSTAND', 'UNITED',
            'UNTIL', 'USING', 'VALUE', 'VARIOUS', 'WATER', 'WHERE', 'WHETHER',
            'WHICH', 'WHILE', 'WHOLE', 'WITHIN', 'WITHOUT', 'WORDS', 'WORLD',
            'WOULD', 'WRITE', 'YEARS', 'YOUNG'
        }
        
        self.function_words = {
            'THE', 'OF', 'AND', 'TO', 'IN', 'THAT', 'IT', 'IS', 'YOU', 'FOR',
            'WITH', 'ON', 'AS', 'AT', 'BY', 'ARE', 'BE', 'WAS', 'OR', 'AN',
            'BUT', 'NOT', 'ALL', 'CAN', 'HER', 'ONE', 'OUR', 'OUT', 'HIS',
            'HAS', 'HAD', 'MAY', 'WHO', 'ITS', 'ANY', 'HIM', 'HOW', 'NOW'
        }
        
        # Top 10 English digrams - FROZEN
        self.required_digrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ND', 'AT', 'ON', 'EN']
        
        # FROZEN weights - record hash
        self.weights = {
            'content_word': 10.0,
            'function_word': 5.0,
            'digram': 2.0,
            'trigram': 3.0,
            'frequency_chi': -1.0,  # Negative because lower chi-squared is better
            'complexity_penalty': -2.0
        }
        
        # English letter frequencies for chi-squared
        self.eng_freq = {
            'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070,
            'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060, 'D': 0.043,
            'L': 0.040, 'C': 0.028, 'U': 0.028, 'M': 0.024, 'W': 0.024,
            'F': 0.022, 'G': 0.020, 'Y': 0.020, 'P': 0.019, 'B': 0.013,
            'V': 0.010, 'K': 0.008, 'J': 0.002, 'X': 0.002, 'Q': 0.001,
            'Z': 0.001
        }
        
        # Common trigrams
        self.common_trigrams = {
            'THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE',
            'FOR', 'ENT', 'ION', 'TER', 'WAS', 'YOU', 'ITH', 'VER',
            'ALL', 'WIT', 'THI', 'TIO', 'HAS', 'BUT', 'NOT', 'HAD'
        }
    
    def get_scorer_hash(self) -> str:
        """Get hash of scorer configuration for reproducibility"""
        config = {
            'content_words': sorted(list(self.content_words)),
            'function_words': sorted(list(self.function_words)),
            'required_digrams': self.required_digrams,
            'common_trigrams': sorted(list(self.common_trigrams)),
            'weights': self.weights,
            'eng_freq': self.eng_freq
        }
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def mask_anchors(self, text: str, anchor_positions: Dict[str, Tuple[int, int]]) -> str:
        """Mask anchor positions with 'X' to prevent scoring leakage"""
        masked = list(text)
        for start, end in anchor_positions.values():
            for i in range(start, end + 1):
                if i < len(masked):
                    masked[i] = 'X'
        return ''.join(masked)
    
    def check_linguistic_constraints(self, text: str, 
                                    anchor_positions: Dict[str, Tuple[int, int]]) -> Tuple[bool, Dict]:
        """
        Check hard linguistic constraints
        Returns (pass/fail, details)
        """
        # Mask anchors first
        masked_text = self.mask_anchors(text.upper(), anchor_positions)
        
        # Remove X's for analysis
        non_anchor_text = masked_text.replace('X', '')
        
        constraints = {
            'content_words_5plus': [],
            'function_words': [],
            'vowel_ratio': 0.0,
            'required_digrams_count': 0,
            'longest_phrase': '',
            'passes': False
        }
        
        # 1. Content words ≥5 letters
        for word in self.content_words:
            if len(word) >= 5 and word in non_anchor_text:
                constraints['content_words_5plus'].append(word)
        
        # 2. Function words
        for word in self.function_words:
            if word in non_anchor_text:
                constraints['function_words'].append(word)
        
        # 3. Vowel ratio
        vowels = sum(1 for c in non_anchor_text if c in 'AEIOU')
        letters = sum(1 for c in non_anchor_text if c.isalpha())
        constraints['vowel_ratio'] = vowels / letters if letters > 0 else 0
        
        # 4. Required digrams
        for digram in self.required_digrams:
            constraints['required_digrams_count'] += non_anchor_text.count(digram)
        
        # 5. Find longest phrase (consecutive letters that form words)
        # Simple approach: find longest substring with high word coverage
        max_phrase_len = 0
        for i in range(len(non_anchor_text)):
            for j in range(i + 8, min(i + 30, len(non_anchor_text) + 1)):
                substring = non_anchor_text[i:j]
                word_chars = 0
                for word in self.function_words.union(self.content_words):
                    if word in substring:
                        word_chars += len(word)
                        break
                if word_chars >= 8 and j - i > max_phrase_len:
                    max_phrase_len = j - i
                    constraints['longest_phrase'] = substring
        
        # Check if all constraints pass
        passes = (
            len(constraints['content_words_5plus']) >= 2 and
            len(constraints['function_words']) >= 3 and
            0.35 <= constraints['vowel_ratio'] <= 0.55 and
            constraints['required_digrams_count'] >= 6 and
            len(constraints['longest_phrase']) >= 8
        )
        
        constraints['passes'] = passes
        return passes, constraints
    
    def score_masked(self, text: str, anchor_positions: Dict[str, Tuple[int, int]],
                     mapping: Dict[str, str] = None) -> float:
        """
        Score text with anchors masked out
        Includes complexity penalty if mapping provided
        """
        # Mask anchors
        masked_text = self.mask_anchors(text.upper(), anchor_positions)
        non_anchor_text = masked_text.replace('X', '')
        
        score = 0.0
        
        # Content words
        for word in self.content_words:
            if word in non_anchor_text:
                score += len(word) * self.weights['content_word']
        
        # Function words
        for word in self.function_words:
            if word in non_anchor_text:
                score += len(word) * self.weights['function_word']
        
        # Digrams
        for i in range(len(non_anchor_text) - 1):
            digram = non_anchor_text[i:i+2]
            if digram in self.required_digrams:
                score += self.weights['digram']
        
        # Trigrams
        for i in range(len(non_anchor_text) - 2):
            trigram = non_anchor_text[i:i+3]
            if trigram in self.common_trigrams:
                score += self.weights['trigram']
        
        # Frequency chi-squared
        if len(non_anchor_text) > 0:
            freq_counts = Counter(non_anchor_text)
            total = sum(freq_counts.values())
            chi_squared = 0.0
            for letter in self.eng_freq:
                expected = self.eng_freq[letter] * total
                observed = freq_counts.get(letter, 0)
                if expected > 0:
                    chi_squared += ((observed - expected) ** 2) / expected
            score += chi_squared * self.weights['frequency_chi']
        
        # Complexity penalty if mapping provided
        if mapping:
            complexity = self.calculate_mapping_complexity(mapping)
            score += complexity * self.weights['complexity_penalty']
        
        return score
    
    def calculate_mapping_complexity(self, mapping: Dict[str, str]) -> float:
        """
        Calculate mapping complexity for regularization
        Lower is simpler (better)
        """
        # Count homophones per PT letter
        pt_to_ct = {}
        for ct, pt in mapping.items():
            if pt not in pt_to_ct:
                pt_to_ct[pt] = []
            pt_to_ct[pt].append(ct)
        
        # Complexity metrics
        total_homophones = sum(max(0, len(cts) - 1) for cts in pt_to_ct.values())
        multi_ct_symbols = sum(1 for cts in pt_to_ct.values() if len(cts) > 1)
        
        return total_homophones + multi_ct_symbols * 0.5

def validate_solution(plaintext: str, mapping: Dict[str, str],
                     ciphertext: str, anchor_positions: Dict[str, Tuple[int, int]]) -> Dict:
    """
    Complete validation of a homophonic solution
    """
    scorer = HardenedScorer()
    
    validation = {
        'scorer_hash': scorer.get_scorer_hash(),
        'plaintext': plaintext,
        'anchors_exact': False,
        'constraints_pass': False,
        'constraint_details': {},
        'masked_score': 0.0,
        'mapping_complexity': 0.0,
        'passes_all': False
    }
    
    # Check anchors
    anchors_exact = (
        plaintext[21:25] == "EAST" and
        plaintext[25:34] == "NORTHEAST" and
        plaintext[63:69] == "BERLIN" and
        plaintext[69:74] == "CLOCK"
    )
    validation['anchors_exact'] = anchors_exact
    
    if not anchors_exact:
        return validation
    
    # Check linguistic constraints
    passes, details = scorer.check_linguistic_constraints(plaintext, anchor_positions)
    validation['constraints_pass'] = passes
    validation['constraint_details'] = details
    
    if not passes:
        return validation
    
    # Calculate masked score
    score = scorer.score_masked(plaintext, anchor_positions, mapping)
    validation['masked_score'] = score
    
    # Calculate complexity
    complexity = scorer.calculate_mapping_complexity(mapping)
    validation['mapping_complexity'] = complexity
    
    # Overall pass
    validation['passes_all'] = (
        anchors_exact and
        passes and
        score > 0 and  # Positive score after penalties
        complexity < 30  # Not too complex
    )
    
    return validation

if __name__ == "__main__":
    # Test the hardened scorer
    scorer = HardenedScorer()
    print(f"Scorer hash: {scorer.get_scorer_hash()}")
    
    # Define anchors
    anchors = {
        "EAST": (21, 24),
        "NORTHEAST": (25, 33),
        "BERLIN": (63, 68),
        "CLOCK": (69, 73)
    }
    
    # Test with a sample text
    test_text = "A" * 21 + "EASTNORTHEAST" + "B" * 29 + "BERLINCLOCK" + "C" * 23
    
    masked = scorer.mask_anchors(test_text, anchors)
    print(f"\nMasked text: {masked[:50]}...")
    
    passes, details = scorer.check_linguistic_constraints(test_text, anchors)
    print(f"\nConstraints pass: {passes}")
    print(f"Details: {json.dumps(details, indent=2)}")