#!/usr/bin/env python3
"""
bootstrap_ref.py - Generate bootstrapped reference distributions from K1-K3
Creates 75-token windows and computes metric distributions
"""

import json
import argparse
import numpy as np
from pathlib import Path
import sys
import os
from datetime import datetime

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from normalize import normalize_text
from tokenize_v2 import tokenize_k_text
from metrics import (
    load_function_words, 
    compute_function_word_rhythm,
    compute_word_length_distribution,
    chi2_distance,
    jensen_shannon_distance,
    compute_ngram_profile,
    ngram_cosine_similarity,
    compute_vowel_consonant_metrics
)


def create_bootstrap_windows(tokens, window_size=75, n_windows=1000, seed=None, mode='tokens'):
    """
    Create bootstrap windows from token list.
    
    Args:
        tokens: list of tokens
        window_size: size of each window (tokens or chars)
        n_windows: number of windows to create
        seed: random seed
        mode: 'tokens' or 'chars' for window type
        
    Returns:
        list: list of token windows
    """
    if seed is not None:
        np.random.seed(seed)
    
    windows = []
    
    if mode == 'tokens':
        n_tokens = len(tokens)
        
        if n_tokens < window_size:
            # If text is shorter than window, pad by resampling
            for _ in range(n_windows):
                # Sample with replacement to get window_size tokens
                window = list(np.random.choice(tokens, size=window_size, replace=True))
                windows.append(window)
        else:
            # Sample windows from the text
            for _ in range(n_windows):
                start = np.random.randint(0, n_tokens - window_size + 1)
                window = tokens[start:start + window_size]
                windows.append(window)
    
    elif mode == 'chars':
        # For character windows, work with the joined text
        text = ' '.join(tokens)
        n_chars = len(text)
        
        if n_chars < window_size:
            # Pad by repeating the text
            padded_text = text * ((window_size // n_chars) + 2)
            for _ in range(n_windows):
                start = np.random.randint(0, len(padded_text) - window_size + 1)
                window_text = padded_text[start:start + window_size]
                # Tokenize the character window
                window = window_text.split()
                windows.append(window)
        else:
            for _ in range(n_windows):
                start = np.random.randint(0, n_chars - window_size + 1)
                window_text = text[start:start + window_size]
                # Tokenize the character window
                window = window_text.split()
                windows.append(window)
    
    return windows


def compute_window_metrics(window_tokens, function_words, pooled_k_profiles=None):
    """
    Compute metrics for a single window.
    
    Args:
        window_tokens: list of tokens in window
        function_words: set of function words
        pooled_k_profiles: pre-computed K reference profiles for n-grams
        
    Returns:
        dict: computed metrics
    """
    metrics = {}
    
    # Content token overlap (will be computed against full K later)
    content_tokens = set(t for t in window_tokens if t not in function_words)
    metrics['n_content_tokens'] = len(content_tokens)
    
    # Function word rhythm
    fw_rhythm = compute_function_word_rhythm(window_tokens, function_words)
    metrics['fw_mean_gap'] = fw_rhythm['mean_gap']
    metrics['fw_std_gap'] = fw_rhythm['std_gap']
    metrics['fw_cv'] = fw_rhythm['cv']
    
    # Word length distribution
    wordlen_dist = compute_word_length_distribution(window_tokens)
    metrics['wordlen_dist'] = wordlen_dist.tolist()  # Store for later aggregation
    
    # Join tokens back to text for letter-level metrics
    window_text = ' '.join(window_tokens)
    
    # Letter n-gram profiles
    bigrams = compute_ngram_profile(window_text, n=2)
    trigrams = compute_ngram_profile(window_text, n=3)
    
    # If we have pooled K profiles, compute similarity
    if pooled_k_profiles:
        metrics['cosine_bigram'] = ngram_cosine_similarity(bigrams, pooled_k_profiles['bigrams'])
        metrics['cosine_trigram'] = ngram_cosine_similarity(trigrams, pooled_k_profiles['trigrams'])
    
    # Store profiles for later pooling
    metrics['bigram_profile'] = dict(bigrams)
    metrics['trigram_profile'] = dict(trigrams)
    
    # Vowel/consonant metrics
    vc_metrics = compute_vowel_consonant_metrics(window_text)
    metrics['vc_ratio'] = vc_metrics['vc_ratio']
    metrics['vcv_frac'] = vc_metrics['vcv_frac']
    metrics['cvc_frac'] = vc_metrics['cvc_frac']
    metrics['ccv_frac'] = vc_metrics['ccv_frac']
    
    return metrics


def compute_pooled_profiles(k_texts_normalized):
    """
    Compute pooled n-gram profiles from all K texts.
    
    Args:
        k_texts_normalized: list of normalized K text strings
        
    Returns:
        dict: pooled bigram and trigram profiles
    """
    from collections import Counter
    
    pooled_bigrams = Counter()
    pooled_trigrams = Counter()
    
    for text in k_texts_normalized:
        bi = compute_ngram_profile(text, n=2)
        tri = compute_ngram_profile(text, n=3)
        pooled_bigrams.update(bi)
        pooled_trigrams.update(tri)
    
    # Normalize
    bi_total = sum(pooled_bigrams.values())
    tri_total = sum(pooled_trigrams.values())
    
    if bi_total > 0:
        for key in pooled_bigrams:
            pooled_bigrams[key] /= bi_total
    if tri_total > 0:
        for key in pooled_trigrams:
            pooled_trigrams[key] /= tri_total
    
    return {
        'bigrams': dict(pooled_bigrams),
        'trigrams': dict(pooled_trigrams)
    }


def main():
    parser = argparse.ArgumentParser(description='Generate bootstrap reference metrics')
    parser.add_argument('--k1', required=True, help='Path to K1.txt')
    parser.add_argument('--k2', help='Path to K2.txt')
    parser.add_argument('--k3', help='Path to K3.txt')
    parser.add_argument('--k2-decl', help='Path to K2_decl.txt (declarative K2)')
    parser.add_argument('--fwords', default='experiments/cadence_panel/data/function_words.txt',
                       help='Path to function words')
    parser.add_argument('--windows', type=int, default=2000,
                       help='Number of bootstrap windows per K text')
    parser.add_argument('--tokens', type=int, help='Size of each window in tokens')
    parser.add_argument('--chars', type=int, help='Size of each window in characters')
    parser.add_argument('--seed', type=int, default=1337,
                       help='Random seed for reproducibility')
    parser.add_argument('--out', required=True, help='Output file for reference metrics')
    
    args = parser.parse_args()
    
    # Determine window mode and size
    if args.tokens and args.chars:
        raise ValueError("Cannot specify both --tokens and --chars")
    elif args.tokens:
        window_mode = 'tokens'
        window_size = args.tokens
    elif args.chars:
        window_mode = 'chars'
        window_size = args.chars
    else:
        # Default to tokens
        window_mode = 'tokens'
        window_size = 75
    
    # Determine which K2 to use
    if args.k2_decl:
        # Using declarative K2
        k_files = [args.k1, args.k2_decl]
        if args.k3:
            k_files.append(args.k3)
        k_labels = ['K1', 'K2_decl', 'K3'] if args.k3 else ['K1', 'K2_decl']
    else:
        # Using regular K2
        if not args.k2:
            raise ValueError("Must provide either --k2 or --k2-decl")
        k_files = [args.k1, args.k2]
        if args.k3:
            k_files.append(args.k3)
        k_labels = ['K1', 'K2', 'K3'] if args.k3 else ['K1', 'K2']
    
    # Load function words
    function_words = load_function_words(args.fwords)
    
    # Load and normalize K texts
    k_texts_raw = []
    k_texts_normalized = []
    k_tokens_all = []
    k_x_counts = []
    
    print("Loading and normalizing K texts...")
    for i, (kfile, label) in enumerate(zip(k_files, k_labels)):
        with open(kfile, 'r') as f:
            raw_text = f.read()
            k_texts_raw.append(raw_text)
        
        # Normalize
        norm_text, x_per_100 = normalize_text(raw_text)
        k_texts_normalized.append(norm_text)
        k_x_counts.append(x_per_100)
        
        # Tokenize
        tokens = tokenize_k_text(norm_text)
        k_tokens_all.append(tokens)
        
        print(f"  {label}: {len(tokens)} tokens, X/100: {x_per_100:.2f}")
    
    # Compute pooled K profiles
    print("Computing pooled K profiles...")
    pooled_profiles = compute_pooled_profiles(k_texts_normalized)
    
    # Get pooled K vocabulary for content overlap baseline
    k_vocab_all = set()
    for tokens in k_tokens_all:
        k_content = set(t for t in tokens if t not in function_words)
        k_vocab_all.update(k_content)
    
    # Generate bootstrap windows and compute metrics
    print(f"Generating {args.windows} {window_mode} windows of size {window_size} per K text...")
    all_metrics = []
    
    for i, (tokens, label) in enumerate(zip(k_tokens_all, k_labels)):
        print(f"  Processing {label}...")
        windows = create_bootstrap_windows(
            tokens, 
            window_size=window_size,
            n_windows=args.windows,
            seed=args.seed + i + 1,  # Different seed for each K
            mode=window_mode
        )
        
        for j, window in enumerate(windows):
            if j % 500 == 0:
                print(f"    Window {j}/{args.windows}")
            
            metrics = compute_window_metrics(window, function_words, pooled_profiles)
            all_metrics.append(metrics)
    
    # Aggregate metrics to compute means and stds
    print("Aggregating metrics...")
    metric_names = [
        'fw_mean_gap', 'fw_std_gap', 'fw_cv',
        'vc_ratio', 'vcv_frac', 'cvc_frac', 'ccv_frac',
        'cosine_bigram', 'cosine_trigram'
    ]
    
    ref_stats = {}
    
    for metric in metric_names:
        values = [m[metric] for m in all_metrics if metric in m]
        if values:
            ref_stats[metric] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'n': len(values)
            }
    
    # Handle word length distributions specially
    wordlen_dists = [np.array(m['wordlen_dist']) for m in all_metrics]
    mean_wordlen_dist = np.mean(wordlen_dists, axis=0)
    
    # Compute chi2 and JS distances for each window against mean
    chi2_values = []
    js_values = []
    for dist in wordlen_dists:
        chi2_values.append(chi2_distance(dist, mean_wordlen_dist))
        js_values.append(jensen_shannon_distance(dist, mean_wordlen_dist))
    
    ref_stats['chi2_wordlen'] = {
        'mean': float(np.mean(chi2_values)),
        'std': float(np.std(chi2_values)),
        'min': float(np.min(chi2_values)),
        'max': float(np.max(chi2_values)),
        'n': len(chi2_values)
    }
    
    ref_stats['js_wordlen'] = {
        'mean': float(np.mean(js_values)),
        'std': float(np.std(js_values)),
        'min': float(np.min(js_values)),
        'max': float(np.max(js_values)),
        'n': len(js_values)
    }
    
    # Add baseline Jaccard values (these will be computed per candidate)
    # For now, store vocabulary size info
    ref_stats['k_vocab_size'] = len(k_vocab_all)
    ref_stats['k_vocab'] = list(k_vocab_all)
    
    # Store X count statistics
    ref_stats['x_per_100'] = {
        'mean': float(np.mean(k_x_counts)),
        'std': float(np.std(k_x_counts)),
        'values': k_x_counts
    }
    
    # Create output structure
    output = {
        'generated': datetime.now().isoformat(),
        'parameters': {
            'n_windows_per_k': args.windows,
            'window_mode': window_mode,
            'window_size': window_size,
            'seed': args.seed,
            'k_files': k_files,
            'k_labels': k_labels,
            'total_windows': len(all_metrics)
        },
        'reference_stats': ref_stats,
        'pooled_profiles': pooled_profiles,
        'mean_wordlen_dist': mean_wordlen_dist.tolist()
    }
    
    # Save to file
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nReference metrics saved to: {output_path}")
    print(f"Total windows generated: {len(all_metrics)}")
    print(f"Metrics computed: {len(ref_stats)}")


if __name__ == '__main__':
    main()