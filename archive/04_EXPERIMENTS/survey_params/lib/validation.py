#!/usr/bin/env python3
"""
validation.py

Validation framework for surveying cipher tests.
Enforces hard anchor constraints and measures text quality.
"""

import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Survey-related terms to search for
SURVEY_TERMS = [
    'MERIDIAN', 'LINE', 'BEARING', 'ANGLE', 'NORTH', 'EAST', 'SOUTH', 'WEST',
    'TRUE', 'MAGNETIC', 'STATION', 'POINT', 'DEGREE', 'MINUTE', 'SECOND',
    'CHAIN', 'ROD', 'FOOT', 'METER', 'LATITUDE', 'DEPARTURE', 'TRAVERSE',
    'SURVEY', 'COMPASS', 'DECLINATION', 'AZIMUTH', 'FIELD', 'OFFSET'
]

# Common English words for basic readability check
COMMON_WORDS = [
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'USE', 'MAN', 'HAS', 'HIM', 'HOW',
    'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'OIL',
    'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'LET', 'MAY', 'NOT', 'NOW',
    'WITH', 'FROM', 'HAVE', 'THIS', 'THAT', 'THEY', 'BEEN', 'MORE', 'WHEN',
    'TIME', 'VERY', 'YOUR', 'OVER', 'KNOW', 'THAN', 'CALL', 'FIND', 'LONG'
]

class AnchorValidator:
    """Validates anchor constraints in decrypted text."""
    
    def __init__(self, anchors_path: Path = None):
        """Load anchor constraints from JSON."""
        if anchors_path is None:
            anchors_path = Path("02_DATA/anchors/four_anchors.json")
        
        with open(anchors_path, 'r') as f:
            anchors_data = json.load(f)
        
        # Convert to expected format
        self.anchors = {}
        for name, data in anchors_data.items():
            self.anchors[name] = {
                'start': data['start'],
                'end': data['end'],
                'text': data['plaintext']
            }
    
    def validate(self, plaintext: str) -> Tuple[bool, List[str]]:
        """
        Check if plaintext preserves all anchors at correct positions.
        
        Returns:
            (success, list_of_failures)
        """
        failures = []
        
        for name, anchor in self.anchors.items():
            start = anchor['start']
            end = anchor['end'] + 1  # Convert to Python slice notation
            expected = anchor['text']
            
            if start >= len(plaintext):
                failures.append(f"{name}: Text too short (need position {start})")
                continue
            
            actual = plaintext[start:end]
            
            if actual != expected:
                failures.append(f"{name}: Expected '{expected}' at {start}-{anchor['end']}, got '{actual}'")
        
        return len(failures) == 0, failures

class TextAnalyzer:
    """Analyzes text quality and readability metrics."""
    
    @staticmethod
    def analyze_head(text: str, head_length: int = 20) -> Dict:
        """
        Analyze the head portion of text for quality metrics.
        """
        head = text[:head_length].upper()
        
        # Vowel ratio
        vowels = sum(1 for c in head if c in 'AEIOU')
        vowel_ratio = vowels / len(head) if head else 0
        
        # Maximum consonant run
        max_consonant_run = TextAnalyzer._max_consonant_run(head)
        
        # Find dictionary words (3+ letters)
        words_found = TextAnalyzer._find_words(head, min_length=3)
        
        # Find survey terms
        survey_terms = TextAnalyzer._find_survey_terms(head)
        
        # Bigram frequency score (rough)
        bigram_score = TextAnalyzer._bigram_score(head)
        
        return {
            'vowel_ratio': round(vowel_ratio, 3),
            'max_consonant_run': max_consonant_run,
            'dict_words_3plus': words_found,
            'survey_terms': survey_terms,
            'bigram_score': bigram_score,
            'head_text': head
        }
    
    @staticmethod
    def analyze_full(text: str) -> Dict:
        """
        Analyze full text for patterns and terms.
        """
        text_upper = text.upper()
        
        # Find all survey terms
        all_survey_terms = TextAnalyzer._find_survey_terms(text_upper)
        
        # Find all common words
        all_common_words = TextAnalyzer._find_words(text_upper, min_length=3)
        
        # Letter frequency distribution
        letter_freq = {}
        total_letters = 0
        for c in text_upper:
            if c.isalpha():
                letter_freq[c] = letter_freq.get(c, 0) + 1
                total_letters += 1
        
        # Normalize frequencies
        for letter in letter_freq:
            letter_freq[letter] = round(letter_freq[letter] / total_letters, 4)
        
        # Calculate chi-squared statistic vs English
        english_freq = {
            'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070,
            'N': 0.067, 'S': 0.063, 'H': 0.061, 'R': 0.060, 'D': 0.043,
            'L': 0.040, 'U': 0.028, 'C': 0.028, 'M': 0.024, 'W': 0.024,
            'F': 0.022, 'G': 0.020, 'Y': 0.020, 'P': 0.019, 'B': 0.015,
            'V': 0.010, 'K': 0.008, 'J': 0.002, 'X': 0.002, 'Q': 0.001, 'Z': 0.001
        }
        
        chi_squared = 0
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            observed = letter_freq.get(letter, 0)
            expected = english_freq.get(letter, 0.001)
            chi_squared += ((observed - expected) ** 2) / expected
        
        return {
            'survey_terms_found': all_survey_terms,
            'common_words_found': all_common_words[:20],  # Limit output
            'letter_freq_chi_squared': round(chi_squared, 3),
            'total_survey_terms': len(all_survey_terms),
            'total_common_words': len(all_common_words)
        }
    
    @staticmethod
    def _max_consonant_run(text: str) -> int:
        """Find the maximum run of consecutive consonants."""
        vowels = set('AEIOU')
        max_run = 0
        current_run = 0
        
        for c in text.upper():
            if c.isalpha():
                if c not in vowels:
                    current_run += 1
                    max_run = max(max_run, current_run)
                else:
                    current_run = 0
        
        return max_run
    
    @staticmethod
    def _find_words(text: str, min_length: int = 3) -> List[str]:
        """Find dictionary words in text."""
        found = []
        text_upper = text.upper()
        
        # Check survey terms first
        for term in SURVEY_TERMS:
            if len(term) >= min_length and term in text_upper:
                if term not in found:
                    found.append(term)
        
        # Check common words
        for word in COMMON_WORDS:
            if len(word) >= min_length and word in text_upper:
                if word not in found:
                    found.append(word)
        
        return found
    
    @staticmethod
    def _find_survey_terms(text: str) -> List[str]:
        """Find surveying-related terms in text."""
        found = []
        text_upper = text.upper()
        
        for term in SURVEY_TERMS:
            if term in text_upper:
                found.append(term)
        
        return found
    
    @staticmethod
    def _bigram_score(text: str) -> float:
        """
        Calculate a rough bigram frequency score.
        Higher scores indicate more English-like bigram patterns.
        """
        # Common English bigrams
        common_bigrams = [
            'TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES',
            'ST', 'RE', 'NT', 'ON', 'AT', 'OU', 'IT', 'TE', 'ET', 'NG',
            'AR', 'AL', 'OR', 'AS', 'IS', 'HA', 'SE', 'EA', 'VE', 'LE'
        ]
        
        if len(text) < 2:
            return 0.0
        
        score = 0
        text_upper = text.upper()
        
        for i in range(len(text_upper) - 1):
            bigram = text_upper[i:i+2]
            if bigram in common_bigrams:
                score += 1
        
        # Normalize by text length
        return round(score / (len(text) - 1), 3)

class ResultRecorder:
    """Records test results in standardized format."""
    
    def __init__(self, output_dir: Path = None):
        """Initialize result recorder."""
        if output_dir is None:
            output_dir = Path("04_EXPERIMENTS/survey_params/results")
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load ciphertext for checksumming
        ct_path = Path("02_DATA/ciphertext_97.txt")
        with open(ct_path, 'r') as f:
            self.ciphertext = f.read().strip()
        self.ct_sha256 = hashlib.sha256(self.ciphertext.encode()).hexdigest()
    
    def record_result(self, test_id: str, family: str, stages: List[Dict],
                     parameter_source: Dict, plaintext: str,
                     anchors_valid: bool, anchor_failures: List[str],
                     head_analysis: Dict, full_analysis: Dict = None,
                     notes: str = "") -> Dict:
        """
        Record a single test result.
        
        Returns the result card dictionary.
        """
        result_card = {
            "id": test_id,
            "family": family,
            "stages": stages,
            "parameter_source": parameter_source,
            "results": {
                "anchors_preserved": anchors_valid,
                "anchor_failures": anchor_failures,
                "plaintext_head_0_20": plaintext[:20],
                "readability": {
                    "vowel_ratio": head_analysis.get('vowel_ratio', 0),
                    "max_consonant_run": head_analysis.get('max_consonant_run', 99),
                    "dict_words_3plus": head_analysis.get('dict_words_3plus', []),
                    "bigram_score": head_analysis.get('bigram_score', 0)
                },
                "survey_terms_found": head_analysis.get('survey_terms', []),
                "notes": notes
            },
            "repro": {
                "seed": 1337,
                "ct_sha256": self.ct_sha256,
                "code_version": self._get_git_sha()
            }
        }
        
        # Add full analysis if provided
        if full_analysis:
            result_card["results"]["full_analysis"] = full_analysis
        
        # Save to JSON file
        output_path = self.output_dir / f"{test_id}.json"
        with open(output_path, 'w') as f:
            json.dump(result_card, f, indent=2)
        
        return result_card
    
    def _get_git_sha(self) -> str:
        """Get current git commit SHA."""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()[:8]
        except:
            pass
        return "unknown"

class NegativeControls:
    """Negative control tests to validate our testing framework."""
    
    @staticmethod
    def scrambled_anchors_test(cipher_func, params: Dict, ciphertext: str) -> bool:
        """
        Test with scrambled anchor positions.
        Should NOT preserve anchors if our test is valid.
        """
        # Scramble the ciphertext at anchor positions
        import random
        random.seed(1337)
        
        ct_list = list(ciphertext)
        
        # Scramble positions 21-73 (anchor region)
        anchor_chars = ct_list[21:74]
        random.shuffle(anchor_chars)
        ct_list[21:74] = anchor_chars
        
        scrambled_ct = ''.join(ct_list)
        
        # Run cipher
        plaintext = cipher_func(scrambled_ct, params)
        
        # Check anchors
        validator = AnchorValidator()
        anchors_valid, _ = validator.validate(plaintext)
        
        # If anchors are still valid with scrambled input, that's suspicious
        return not anchors_valid  # Return True if test passes (anchors NOT preserved)
    
    @staticmethod
    def random_params_test(cipher_func, ciphertext: str, num_tests: int = 10) -> float:
        """
        Test with random parameters.
        Returns fraction of random tests that preserve anchors.
        Should be very low (~0) for a good cipher test.
        """
        import random
        random.seed(1337)
        
        validator = AnchorValidator()
        successes = 0
        
        for _ in range(num_tests):
            # Generate random parameters
            params = {
                'L': random.randint(2, 97),
                'phase': random.randint(0, 25),
                'offset': random.randint(0, 25)
            }
            
            # Run cipher
            plaintext = cipher_func(ciphertext, params)
            
            # Check anchors
            anchors_valid, _ = validator.validate(plaintext)
            if anchors_valid:
                successes += 1
        
        return successes / num_tests