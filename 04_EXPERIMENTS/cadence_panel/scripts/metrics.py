#!/usr/bin/env python3
"""
metrics.py - Compute cadence panel metrics for style comparison
All metrics evaluate head 0..74 for candidates vs K1-K3 reference
"""

import json
import numpy as np
from collections import Counter
from scipy.spatial.distance import cosine
from scipy.stats import chi2_contingency, entropy
import sys
import os

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from normalize import normalize_text
from tokenize_v2 import tokenize_head_v2, tokenize_k_text
from levenshtein import levenshtein_distance, find_close_matches, check_k_quirks


def load_function_words(fwords_path):
    """Load function words list"""
    with open(fwords_path, 'r') as f:
        return set(line.strip().upper() for line in f if line.strip())


def compute_lexical_overlap(head_tokens, k_tokens_list, function_words, use_lev1=False):
    """
    Compute Jaccard overlap with K-vocabulary (content tokens only).
    
    Args:
        head_tokens: list of tokens from candidate head
        k_tokens_list: list of token lists from K1, K2, K3
        function_words: set of function words to exclude
        use_lev1: if True, allow Levenshtein-1 matches
        
    Returns:
        float: Jaccard coefficient
    """
    # Get content tokens (exclude function words)
    head_content = set(t for t in head_tokens if t not in function_words)
    
    # Build K vocabulary (union of all K content tokens)
    k_vocab = set()
    for k_tokens in k_tokens_list:
        k_content = set(t for t in k_tokens if t not in function_words)
        k_vocab.update(k_content)
    
    if not use_lev1:
        # Exact matching
        intersection = head_content & k_vocab
        union = head_content | k_vocab
    else:
        # Allow Levenshtein-1 matches
        intersection = set()
        for h_token in head_content:
            if h_token in k_vocab:
                intersection.add(h_token)
            else:
                # Check for close matches
                matches = find_close_matches(h_token, k_vocab, max_distance=1)
                if matches:
                    intersection.add(h_token)
        
        # For Lev1, union is still the same
        union = head_content | k_vocab
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def compute_function_word_rhythm(tokens, function_words):
    """
    Compute function word rhythm metrics.
    
    Args:
        tokens: list of tokens
        function_words: set of function words
        
    Returns:
        dict: mean gap, std gap, coefficient of variation
    """
    # Find positions of function words
    fw_positions = [i for i, t in enumerate(tokens) if t in function_words]
    
    if len(fw_positions) < 2:
        return {'mean_gap': 0, 'std_gap': 0, 'cv': 0}
    
    # Compute gaps between successive function words
    gaps = [fw_positions[i+1] - fw_positions[i] for i in range(len(fw_positions)-1)]
    
    mean_gap = np.mean(gaps)
    std_gap = np.std(gaps)
    cv = std_gap / mean_gap if mean_gap > 0 else 0
    
    return {
        'mean_gap': mean_gap,
        'std_gap': std_gap,
        'cv': cv
    }


def compute_word_length_distribution(tokens, max_len=12):
    """
    Compute word length distribution.
    
    Args:
        tokens: list of tokens
        max_len: maximum word length to track
        
    Returns:
        np.array: normalized distribution (frequencies)
    """
    lengths = [min(len(t), max_len) for t in tokens]
    
    # Create histogram for lengths 1 to max_len
    hist = np.zeros(max_len)
    for length in lengths:
        if length > 0:
            hist[length-1] += 1
    
    # Normalize
    if hist.sum() > 0:
        hist = hist / hist.sum()
    
    return hist


def chi2_distance(dist1, dist2):
    """Compute chi-squared distance between two distributions"""
    # Add small epsilon to avoid division by zero
    eps = 1e-10
    denominator = dist1 + dist2 + eps
    numerator = (dist1 - dist2) ** 2
    return 0.5 * np.sum(numerator / denominator)


def jensen_shannon_distance(dist1, dist2):
    """Compute Jensen-Shannon distance between two distributions"""
    # Average distribution
    m = 0.5 * (dist1 + dist2)
    
    # JS divergence
    divergence = 0.5 * entropy(dist1, m) + 0.5 * entropy(dist2, m)
    
    # JS distance is square root of divergence
    return np.sqrt(divergence)


def compute_ngram_profile(text, n=2):
    """
    Compute letter n-gram frequency profile.
    
    Args:
        text: string (already normalized, uppercase, alpha-only)
        n: n-gram size (2 for bigrams, 3 for trigrams)
        
    Returns:
        dict: n-gram frequencies
    """
    # Remove spaces for letter n-grams
    text_no_space = text.replace(' ', '')
    
    ngrams = Counter()
    for i in range(len(text_no_space) - n + 1):
        ngram = text_no_space[i:i+n]
        ngrams[ngram] += 1
    
    # Normalize
    total = sum(ngrams.values())
    if total > 0:
        for key in ngrams:
            ngrams[key] /= total
    
    return ngrams


def ngram_cosine_similarity(profile1, profile2):
    """
    Compute cosine similarity between two n-gram profiles.
    
    Args:
        profile1, profile2: dicts of n-gram frequencies
        
    Returns:
        float: cosine similarity (1 - cosine distance)
    """
    # Get union of all n-grams
    all_ngrams = set(profile1.keys()) | set(profile2.keys())
    
    # Create vectors
    vec1 = np.array([profile1.get(ng, 0) for ng in all_ngrams])
    vec2 = np.array([profile2.get(ng, 0) for ng in all_ngrams])
    
    # Compute cosine similarity
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    
    return 1 - cosine(vec1, vec2)


def compute_vowel_consonant_metrics(text):
    """
    Compute vowel/consonant cadence metrics.
    
    Args:
        text: string (normalized, uppercase, alpha-only)
        
    Returns:
        dict: V:C ratio, VCV fraction, CVC fraction, CCV fraction
    """
    vowels = set('AEIOUY')
    
    # Remove spaces for letter analysis
    text_no_space = text.replace(' ', '')
    
    # Count vowels and consonants
    v_count = sum(1 for c in text_no_space if c in vowels)
    c_count = len(text_no_space) - v_count
    
    # V:C ratio
    vc_ratio = v_count / c_count if c_count > 0 else 0
    
    # Map to V/C sequence
    vc_seq = ''.join('V' if c in vowels else 'C' for c in text_no_space)
    
    # Count patterns
    vcv_count = vc_seq.count('VCV')
    cvc_count = vc_seq.count('CVC')
    ccv_count = vc_seq.count('CCV')
    
    # Total trigrams
    total_trigrams = max(len(vc_seq) - 2, 1)
    
    return {
        'vc_ratio': vc_ratio,
        'vcv_frac': vcv_count / total_trigrams,
        'cvc_frac': cvc_count / total_trigrams,
        'ccv_frac': ccv_count / total_trigrams
    }


def check_orthographic_quirks(tokens):
    """
    Check for presence of K-style orthographic quirks.
    
    Args:
        tokens: list of tokens
        
    Returns:
        dict: quirk analysis results
    """
    known_quirks = {
        'IQLUSION': 'ILLUSION',
        'UNDERGRUUND': 'UNDERGROUND',
        'DESPARATLY': 'DESPERATELY'
    }
    
    results = {
        'has_quirks': False,
        'quirks_found': [],
        'quirks_recovered': []
    }
    
    for token in tokens:
        # Check exact match
        if token in known_quirks:
            results['has_quirks'] = True
            results['quirks_found'].append((token, known_quirks[token]))
        else:
            # Check if distance-1 from any quirk
            for quirk, standard in known_quirks.items():
                if levenshtein_distance(token, quirk) <= 1:
                    results['quirks_recovered'].append((token, quirk, standard))
    
    return results


def compute_all_metrics(head_text, k_texts, cuts_path, fwords_path):
    """
    Compute all metrics for a candidate head.
    
    Args:
        head_text: 75-char candidate head
        k_texts: list of K1, K2, K3 texts (raw)
        cuts_path: path to canonical_cuts.json
        fwords_path: path to function_words.txt
        
    Returns:
        dict: all computed metrics
    """
    # Load function words
    function_words = load_function_words(fwords_path)
    
    # Normalize head and K texts
    head_norm, head_x_per_100 = normalize_text(head_text[:75])  # Ensure 75 chars
    
    k_normalized = []
    k_x_counts = []
    for k_text in k_texts:
        k_norm, k_x = normalize_text(k_text)
        k_normalized.append(k_norm)
        k_x_counts.append(k_x)
    
    # Tokenize head
    head_tokens = tokenize_head_v2(head_text[:75], cuts_path)
    
    # Tokenize K texts
    k_tokens_list = [tokenize_k_text(k_norm) for k_norm in k_normalized]
    
    # Normalize tokens (they might contain punctuation from original)
    head_tokens_norm = []
    for token in head_tokens:
        norm_token, _ = normalize_text(token, track_x=False)
        if norm_token:  # Skip empty tokens
            head_tokens_norm.extend(norm_token.split())
    
    metrics = {}
    
    # 3.1 Lexical overlap
    metrics['J_content'] = compute_lexical_overlap(
        head_tokens_norm, k_tokens_list, function_words, use_lev1=False)
    metrics['J_content_lev1'] = compute_lexical_overlap(
        head_tokens_norm, k_tokens_list, function_words, use_lev1=True)
    
    # 3.2 Function word rhythm
    fw_rhythm = compute_function_word_rhythm(head_tokens_norm, function_words)
    metrics.update({f'fw_{k}': v for k, v in fw_rhythm.items()})
    
    # 3.3 Word length profile
    head_wordlen = compute_word_length_distribution(head_tokens_norm)
    
    # Compute pooled K word length distribution
    k_all_tokens = []
    for tokens in k_tokens_list:
        k_all_tokens.extend(tokens)
    k_wordlen = compute_word_length_distribution(k_all_tokens)
    
    metrics['chi2_wordlen'] = chi2_distance(head_wordlen, k_wordlen)
    metrics['js_wordlen'] = jensen_shannon_distance(head_wordlen, k_wordlen)
    
    # 3.4 Letter n-gram profiles
    # Build pooled K n-gram profiles
    k_bigrams = Counter()
    k_trigrams = Counter()
    for k_norm in k_normalized:
        bi = compute_ngram_profile(k_norm, n=2)
        tri = compute_ngram_profile(k_norm, n=3)
        k_bigrams.update(bi)
        k_trigrams.update(tri)
    
    # Normalize pooled profiles
    k_bi_total = sum(k_bigrams.values())
    k_tri_total = sum(k_trigrams.values())
    if k_bi_total > 0:
        for key in k_bigrams:
            k_bigrams[key] /= k_bi_total
    if k_tri_total > 0:
        for key in k_trigrams:
            k_trigrams[key] /= k_tri_total
    
    head_bigrams = compute_ngram_profile(head_norm, n=2)
    head_trigrams = compute_ngram_profile(head_norm, n=3)
    
    metrics['cosine_bigram'] = ngram_cosine_similarity(head_bigrams, k_bigrams)
    metrics['cosine_trigram'] = ngram_cosine_similarity(head_trigrams, k_trigrams)
    
    # 3.5 Vowel/consonant cadence
    vc_metrics = compute_vowel_consonant_metrics(head_norm)
    metrics.update({f'vc_{k}': v for k, v in vc_metrics.items()})
    
    # 3.6 Orthographic quirks
    quirks = check_orthographic_quirks(head_tokens_norm)
    metrics['has_quirks'] = quirks['has_quirks']
    metrics['quirks_found'] = len(quirks['quirks_found'])
    metrics['quirks_recovered'] = len(quirks['quirks_recovered'])
    
    # X count tracking
    metrics['x_per_100_head'] = head_x_per_100
    metrics['x_per_100_k_mean'] = np.mean(k_x_counts)
    
    return metrics, quirks


def compute_z_scores(metrics, ref_stats):
    """
    Compute z-scores for metrics relative to reference distribution.
    
    Args:
        metrics: dict of computed metrics
        ref_stats: dict with 'mean' and 'std' for each metric
        
    Returns:
        dict: z-scores for each metric
    """
    z_scores = {}
    
    for metric_name, value in metrics.items():
        if metric_name in ref_stats:
            mean = ref_stats[metric_name]['mean']
            std = ref_stats[metric_name]['std']
            
            if std > 0:
                z = (value - mean) / std
            else:
                z = 0.0
            
            z_scores[f'z_{metric_name}'] = z
    
    return z_scores


def compute_combined_score(metrics, z_scores, weights=None):
    """
    Compute Combined Cadence Score (CCS).
    
    Args:
        metrics: raw metric values
        z_scores: z-scores for metrics
        weights: optional custom weights
        
    Returns:
        float: CCS score
    """
    if weights is None:
        weights = {
            'z_J_content': 0.25,
            'z_J_content_lev1': 0.10,
            'z_cosine_bigram': 0.20,
            'z_cosine_trigram': 0.15,
            'z_chi2_wordlen': -0.10,  # Lower is better, so negative weight
            'z_vc_ratio': -0.10,       # Deviation penalty (abs value)
            'z_fw_mean_gap': -0.05,   # Deviation penalty
            'z_fw_cv': -0.05          # Deviation penalty
        }
    
    ccs = 0.0
    
    for metric, weight in weights.items():
        if metric in z_scores:
            value = z_scores[metric]
            
            # For deviation penalties, use absolute value
            if metric in ['z_vc_ratio', 'z_fw_mean_gap', 'z_fw_cv']:
                value = -abs(value)
            
            ccs += weight * value
    
    return ccs