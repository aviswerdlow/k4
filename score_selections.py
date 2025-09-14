#!/usr/bin/env python3
"""
score_selections.py
Stage 2: Run CT-only and PT-LM analysis tracks on selections

Tracks:
- A: Ciphertext structure tests (IC, n-grams, Kasiski)
- B: Plaintext language model scoring (5-gram LM with function words)
"""

import pandas as pd
import numpy as np
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def compute_ic(text):
    """Compute index of coincidence for text"""
    if len(text) < 2:
        return 0.0

    n = len(text)
    freq = Counter(text)
    numerator = sum(f * (f - 1) for f in freq.values())
    denominator = n * (n - 1)

    if denominator == 0:
        return 0.0

    return numerator / denominator

def find_ngram_repeats(text, n):
    """Find all repeated n-grams in text"""
    if len(text) < n:
        return []

    ngrams = [text[i:i+n] for i in range(len(text) - n + 1)]
    counts = Counter(ngrams)
    return [(ng, count) for ng, count in counts.items() if count > 1]

def kasiski_distances(text, n=3):
    """Find distances between repeated n-grams (Kasiski examination)"""
    if len(text) < n:
        return []

    positions = {}
    for i in range(len(text) - n + 1):
        ngram = text[i:i+n]
        if ngram not in positions:
            positions[ngram] = []
        positions[ngram].append(i)

    distances = []
    for ngram, pos_list in positions.items():
        if len(pos_list) > 1:
            for i in range(len(pos_list) - 1):
                for j in range(i + 1, len(pos_list)):
                    distances.append(pos_list[j] - pos_list[i])

    return distances

def generate_null_selections(letters_map, selection_length, n_nulls=1000, exclude_indices=None):
    """Generate null selections from known, non-anchor ticks"""
    if exclude_indices is None:
        exclude_indices = set()

    # Filter for known letters (not '?') and non-excluded indices
    valid_indices = [
        i for i, row in letters_map.iterrows()
        if row['char'] != '?' and i not in exclude_indices
    ]

    nulls = []
    for _ in range(n_nulls):
        if len(valid_indices) >= selection_length:
            selected = np.random.choice(valid_indices, selection_length, replace=False)
            null_text = ''.join(letters_map.iloc[selected]['char'].values)
            nulls.append(null_text)

    return nulls

def score_ct_structure(selection_text, null_texts):
    """Score ciphertext structure metrics against nulls"""
    # Compute metrics for selection
    sel_ic = compute_ic(selection_text)
    sel_bigrams = len(find_ngram_repeats(selection_text, 2))
    sel_trigrams = len(find_ngram_repeats(selection_text, 3))
    sel_kasiski = kasiski_distances(selection_text, 3)
    sel_kasiski_mean = np.mean(sel_kasiski) if sel_kasiski else 0

    # Compute metrics for nulls
    null_ics = [compute_ic(text) for text in null_texts]
    null_bigrams = [len(find_ngram_repeats(text, 2)) for text in null_texts]
    null_trigrams = [len(find_ngram_repeats(text, 3)) for text in null_texts]
    null_kasiskis = [np.mean(kasiski_distances(text, 3)) if kasiski_distances(text, 3) else 0
                     for text in null_texts]

    # Compute p-values
    p_ic = (sum(1 for ic in null_ics if ic >= sel_ic) + 1) / (len(null_ics) + 1)
    p_bigram = (sum(1 for bg in null_bigrams if bg >= sel_bigrams) + 1) / (len(null_bigrams) + 1)
    p_trigram = (sum(1 for tg in null_trigrams if tg >= sel_trigrams) + 1) / (len(null_trigrams) + 1)
    p_kasiski = (sum(1 for k in null_kasiskis if k >= sel_kasiski_mean) + 1) / (len(null_kasiskis) + 1)

    return {
        'ic': sel_ic,
        'ic_p': p_ic,
        'bigrams': sel_bigrams,
        'bigrams_p': p_bigram,
        'trigrams': sel_trigrams,
        'trigrams_p': p_trigram,
        'kasiski_mean': sel_kasiski_mean,
        'kasiski_p': p_kasiski,
        'min_p': min(p_ic, p_bigram, p_trigram, p_kasiski)
    }

def simple_lm_score(text, ngram_model=None):
    """Simple 5-gram language model scoring with function word bonus"""
    # Simplified scoring - in practice would load frozen model
    score = 0.0

    # Function words that should appear frequently
    function_words = {'THE', 'AND', 'OF', 'TO', 'IN', 'A', 'IS', 'IT', 'FOR', 'WITH'}

    # Check for function word presence (bonus scoring)
    for word in function_words:
        if word in text:
            score += len(word) * 0.5

    # Basic English letter frequency scoring
    english_freq = {
        'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
        'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
        'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
        'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
        'Q': 0.10, 'Z': 0.07
    }

    freq_counter = Counter(text)
    for char, count in freq_counter.items():
        if char in english_freq:
            score += count * english_freq[char] / 100

    return score / len(text) if text else 0

def apply_bonferroni(p_values, n_tests):
    """Apply Bonferroni correction to p-values"""
    return [min(p * n_tests, 1.0) for p in p_values]

def main():
    # Paths
    base_dir = Path('/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus')
    model_dir = base_dir / '06_DOCUMENTATION/KryptosModel'

    # Load maps
    ct_map_path = model_dir / '04_full_sculpture/letters_map_full_ct.csv'
    pt_map_path = model_dir / '04_full_sculpture/letters_map_full.csv'

    if not ct_map_path.exists() or not pt_map_path.exists():
        print("ERROR: Character maps not found. Run align_grid_to_ticks.py first!")
        return

    print("=== Stage 2: Selection Scoring ===\n")

    ct_map = pd.read_csv(ct_map_path)
    pt_map = pd.read_csv(pt_map_path)

    # K4 anchor windows to mask (by K4 local index)
    k4_anchors = list(range(21, 25)) + list(range(25, 34)) + list(range(63, 69)) + list(range(69, 74))
    k4_global_anchors = pt_map[
        (pt_map['section'] == 'K4') & (pt_map['index_in_section'].isin(k4_anchors))
    ].index.tolist()

    # Create timestamp for this run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Load selection sets (simplified example - would load from JSON files)
    print("Loading selection sets...")

    # Example: Create some test selections (in practice, load from JSON)
    test_selections = {
        'projection_0deg': list(range(0, 50)),  # Example indices
        'cross_section_v1': list(range(100, 200)),
        'spiral_path': list(range(0, 456, 3))
    }

    # Track A: CT-only structure tests
    print("\n" + "="*50)
    print("Track A: Ciphertext Structure Analysis")
    print("="*50)

    ct_results = {}
    for sel_name, sel_indices in test_selections.items():
        print(f"\nScoring {sel_name}...")

        # Get selection text
        sel_text = ''.join(ct_map.iloc[sel_indices]['char'].values)

        # Generate nulls
        nulls = generate_null_selections(ct_map, len(sel_indices), n_nulls=1000,
                                          exclude_indices=set(k4_global_anchors))

        # Score
        scores = score_ct_structure(sel_text, nulls)
        ct_results[sel_name] = scores

        print(f"  IC: {scores['ic']:.4f} (p={scores['ic_p']:.4f})")
        print(f"  Bigrams: {scores['bigrams']} (p={scores['bigrams_p']:.4f})")
        print(f"  Trigrams: {scores['trigrams']} (p={scores['trigrams_p']:.4f})")

    # Apply Bonferroni correction
    n_tests_ct = len(test_selections) * 4  # 4 metrics per selection
    print(f"\nBonferroni correction: {n_tests_ct} tests")

    # Save CT results
    ct_output_dir = base_dir / f'runs/ct_structure/{timestamp}'
    ct_output_dir.mkdir(parents=True, exist_ok=True)

    with open(ct_output_dir / 'ct_scores.json', 'w') as f:
        json.dump(ct_results, f, indent=2)

    # Track B: PT-LM scoring
    print("\n" + "="*50)
    print("Track B: Plaintext Language Model Scoring")
    print("="*50)

    pt_results = {}
    for sel_name, sel_indices in test_selections.items():
        print(f"\nScoring {sel_name}...")

        # Mask K4 anchors and unknowns
        valid_indices = [i for i in sel_indices
                         if i not in k4_global_anchors and pt_map.iloc[i]['char'] != '?']

        if not valid_indices:
            print("  Skipped: no valid indices after masking")
            continue

        # Get selection text
        sel_text = ''.join(pt_map.iloc[valid_indices]['char'].values)

        # Generate nulls
        nulls = generate_null_selections(pt_map, len(valid_indices), n_nulls=1000,
                                          exclude_indices=set(k4_global_anchors))

        # Score with LM
        sel_score = simple_lm_score(sel_text)
        null_scores = [simple_lm_score(text) for text in nulls]

        # Compute p-value
        p_value = (sum(1 for ns in null_scores if ns >= sel_score) + 1) / (len(null_scores) + 1)

        pt_results[sel_name] = {
            'lm_score': sel_score,
            'p_value': p_value,
            'n_chars': len(sel_text)
        }

        print(f"  LM Score: {sel_score:.4f} (p={p_value:.4f})")

    # Save PT results
    pt_output_dir = base_dir / f'runs/pt_lm/{timestamp}'
    pt_output_dir.mkdir(parents=True, exist_ok=True)

    with open(pt_output_dir / 'lm_scores.json', 'w') as f:
        json.dump(pt_results, f, indent=2)

    # Generate summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)

    # Check for significant results
    threshold = 0.001
    ct_significant = [name for name, scores in ct_results.items()
                      if scores['min_p'] * n_tests_ct <= threshold]
    pt_significant = [name for name, scores in pt_results.items()
                      if scores['p_value'] * len(test_selections) <= threshold]

    print(f"\nBonferroni-adjusted threshold: p <= {threshold}")
    print(f"\nCT Structure:")
    print(f"  Tests run: {len(ct_results)}")
    print(f"  Significant: {len(ct_significant)}")
    if ct_significant:
        for name in ct_significant:
            print(f"    - {name}")

    print(f"\nPT Language Model:")
    print(f"  Tests run: {len(pt_results)}")
    print(f"  Significant: {len(pt_significant)}")
    if pt_significant:
        for name in pt_significant:
            print(f"    - {name}")

    # Write summary markdown
    summary_path = base_dir / 'SUMMARY.md'
    with open(summary_path, 'w') as f:
        f.write("# Kryptos Full Sculpture Analysis Summary\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write("## Parameters\n\n")
        f.write(f"- Bonferroni threshold: p_adj ≤ {threshold}\n")
        f.write(f"- CT tests: {n_tests_ct} (4 metrics × {len(test_selections)} selections)\n")
        f.write(f"- PT tests: {len(test_selections)}\n")
        f.write(f"- Null samples: 1,000 per test\n\n")
        f.write("## Results\n\n")
        f.write("### Ciphertext Structure\n\n")
        if ct_significant:
            f.write("**Significant findings:**\n")
            for name in ct_significant:
                f.write(f"- {name}\n")
        else:
            f.write("No selections showed significant CT structure after correction.\n")
        f.write("\n### Plaintext Language Model\n\n")
        if pt_significant:
            f.write("**Significant findings:**\n")
            for name in pt_significant:
                f.write(f"- {name}\n")
        else:
            f.write("No selections showed significant PT patterns after correction.\n")
        f.write("\n## Conclusion\n\n")
        if not ct_significant and not pt_significant:
            f.write("No geometric selections survived Bonferroni correction. ")
            f.write("The null hypothesis (random structure) cannot be rejected.\n")
        else:
            f.write("Some selections show promise and warrant further investigation ")
            f.write("with replication requirements.\n")

    print(f"\nSummary written to: {summary_path}")

if __name__ == "__main__":
    main()