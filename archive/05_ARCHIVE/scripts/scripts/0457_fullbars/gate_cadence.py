#!/usr/bin/env python3
"""
Cadence gate evaluation using bootstrapped thresholds.
Evaluates 6 primitives for head-only window with tokenization v2.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple

def tokenize_v2(text: str, cuts: List[int]) -> List[str]:
    """Apply tokenization v2 rules to get words from head window."""
    words = []
    prev = 0
    for cut in cuts:
        if cut < 74:  # Head window
            words.append(text[prev:cut+1])
        elif prev <= 74:
            # Word touches position 74
            words.append(text[prev:min(cut+1, 75)])
            break
        prev = cut + 1
    return words

def compute_letter_bigrams(text: str) -> Counter:
    """Compute letter bigram frequencies."""
    bigrams = Counter()
    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        bigrams[bigram] += 1
    return bigrams

def compute_letter_trigrams(text: str) -> Counter:
    """Compute letter trigram frequencies."""
    trigrams = Counter()
    for i in range(len(text) - 2):
        trigram = text[i:i+3]
        trigrams[trigram] += 1
    return trigrams

def cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    """Compute cosine similarity between two frequency vectors."""
    all_keys = set(vec1.keys()) | set(vec2.keys())
    
    if not all_keys:
        return 0.0
    
    v1 = np.array([vec1.get(k, 0) for k in all_keys])
    v2 = np.array([vec2.get(k, 0) for k in all_keys])
    
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def compute_function_word_gaps(words: List[str]) -> Tuple[float, float]:
    """Compute mean and CV of gaps between function words."""
    function_words = {
        'A', 'AN', 'AND', 'ARE', 'AS', 'AT', 'BE', 'BY', 'FOR', 'FROM',
        'HAS', 'HE', 'IN', 'IS', 'IT', 'ITS', 'OF', 'ON', 'THAT', 'THE',
        'TO', 'WAS', 'WILL', 'WITH', 'OR', 'BUT', 'IF', 'SO', 'YET'
    }
    
    fw_positions = []
    for i, word in enumerate(words):
        if word in function_words:
            fw_positions.append(i)
    
    if len(fw_positions) < 2:
        return 0.0, 0.0
    
    gaps = []
    for i in range(1, len(fw_positions)):
        gaps.append(fw_positions[i] - fw_positions[i-1])
    
    if not gaps:
        return 0.0, 0.0
    
    mean_gap = np.mean(gaps)
    std_gap = np.std(gaps)
    cv_gap = std_gap / mean_gap if mean_gap > 0 else 0.0
    
    return mean_gap, cv_gap

def compute_wordlen_chi2(words: List[str]) -> float:
    """Compute chi-squared distance of word length distribution."""
    # Reference distribution (English typical)
    ref_dist = {
        1: 0.05, 2: 0.15, 3: 0.20, 4: 0.18, 5: 0.15,
        6: 0.10, 7: 0.08, 8: 0.05, 9: 0.02, 10: 0.01,
        11: 0.005, 12: 0.003, 13: 0.001, 14: 0.001
    }
    
    length_counts = Counter(len(word) for word in words)
    total_words = sum(length_counts.values())
    
    if total_words == 0:
        return float('inf')
    
    chi2 = 0.0
    for length in range(1, 15):
        observed = length_counts.get(length, 0) / total_words
        expected = ref_dist.get(length, 0.001)
        chi2 += (observed - expected) ** 2 / expected
    
    return chi2

def compute_vc_ratio(text: str) -> float:
    """Compute vowel to consonant ratio."""
    vowels = set('AEIOU')
    vowel_count = sum(1 for c in text if c in vowels)
    consonant_count = len(text) - vowel_count
    
    if consonant_count == 0:
        return float('inf')
    
    return vowel_count / consonant_count

def evaluate_cadence(head_text: str, words: List[str], thresholds_path: str = None) -> Dict:
    """
    Evaluate cadence gate for a candidate head.
    
    Args:
        head_text: Head window text [0:75]
        words: Tokenized words from head
        thresholds_path: Path to THRESHOLDS.json (optional)
    
    Returns:
        Dictionary with gate results and metrics
    """
    
    # Load thresholds
    if thresholds_path is None:
        thresholds_path = "/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/cadence/THRESHOLDS.json"
    
    with open(thresholds_path, 'r') as f:
        thresholds = json.load(f)
    
    # Get reference bigrams/trigrams from K1-K3
    k1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    k2 = "ITWASTOTALLYINVISIBLESHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATION"
    k3 = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRTHATESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
    
    ref_text = k1 + k2 + k3
    ref_bigrams = compute_letter_bigrams(ref_text)
    ref_trigrams = compute_letter_trigrams(ref_text)
    
    # Compute metrics for candidate
    head_bigrams = compute_letter_bigrams(head_text)
    head_trigrams = compute_letter_trigrams(head_text)
    
    cosine_bi = cosine_similarity(head_bigrams, ref_bigrams)
    cosine_tri = cosine_similarity(head_trigrams, ref_trigrams)
    fw_mean, fw_cv = compute_function_word_gaps(words)
    wordlen_chi2 = compute_wordlen_chi2(words)
    vc_ratio = compute_vc_ratio(head_text)
    
    # Evaluate against thresholds
    tests = {
        'cosine_bigram': {
            'value': float(cosine_bi),
            'threshold': float(thresholds['cosine_bigram_p5']),
            'pass': bool(cosine_bi >= thresholds['cosine_bigram_p5'])
        },
        'cosine_trigram': {
            'value': float(cosine_tri),
            'threshold': float(thresholds['cosine_trigram_p5']),
            'pass': bool(cosine_tri >= thresholds['cosine_trigram_p5'])
        },
        'fw_gap_mean': {
            'value': float(fw_mean),
            'band': [float(thresholds['fw_gap_mean_p2.5']), float(thresholds['fw_gap_mean_p97.5'])],
            'pass': bool(thresholds['fw_gap_mean_p2.5'] <= fw_mean <= thresholds['fw_gap_mean_p97.5'])
        },
        'fw_gap_cv': {
            'value': float(fw_cv),
            'band': [float(thresholds['fw_gap_cv_p2.5']), float(thresholds['fw_gap_cv_p97.5'])],
            'pass': bool(thresholds['fw_gap_cv_p2.5'] <= fw_cv <= thresholds['fw_gap_cv_p97.5'])
        },
        'wordlen_chi2': {
            'value': float(wordlen_chi2),
            'threshold': float(thresholds['wordlen_chi2_p95']),
            'pass': bool(wordlen_chi2 <= thresholds['wordlen_chi2_p95'])
        },
        'vc_ratio': {
            'value': float(vc_ratio),
            'band': [float(thresholds['vc_ratio_p2.5']), float(thresholds['vc_ratio_p97.5'])],
            'pass': bool(thresholds['vc_ratio_p2.5'] <= vc_ratio <= thresholds['vc_ratio_p97.5'])
        }
    }
    
    # Overall pass requires all 6 tests
    overall_pass = all(test['pass'] for test in tests.values())
    
    return {
        'pass': bool(overall_pass),  # Convert to Python bool
        'primitives': tests,
        'summary': {
            'passed': sum(1 for t in tests.values() if t['pass']),
            'total': 6
        }
    }

def run_cadence_gate(plaintext_path: str, space_map_path: str, 
                     thresholds_path: str = None) -> Dict:
    """
    Run cadence gate on a candidate from file paths.
    
    Args:
        plaintext_path: Path to plaintext_97.txt
        space_map_path: Path to space_map.json
        thresholds_path: Path to THRESHOLDS.json (optional)
    
    Returns:
        Complete gate results
    """
    
    # Load plaintext
    with open(plaintext_path, 'r') as f:
        plaintext = f.read().strip()
    
    # Load space map
    with open(space_map_path, 'r') as f:
        space_map = json.load(f)
    
    # Get head window
    head_text = plaintext[:75]
    
    # Tokenize
    words = tokenize_v2(plaintext, space_map['cuts'])
    
    # Evaluate
    results = evaluate_cadence(head_text, words, thresholds_path)
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: gate_cadence.py <plaintext_97.txt> <space_map.json> [thresholds.json]")
        sys.exit(1)
    
    plaintext_path = sys.argv[1]
    space_map_path = sys.argv[2]
    thresholds_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    results = run_cadence_gate(plaintext_path, space_map_path, thresholds_path)
    
    print(json.dumps(results, indent=2))
    
    if results['pass']:
        print("\n✅ Cadence gate PASSED")
    else:
        print("\n❌ Cadence gate FAILED")
        failed = [name for name, test in results['primitives'].items() if not test['pass']]
        print(f"   Failed primitives: {', '.join(failed)}")