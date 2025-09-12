#!/usr/bin/env python3
"""
Bootstrap cadence thresholds from K1-K3 reference windows.
Generates 2000 windows per text (6000 total) and computes percentiles.
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple
import random

# K1-K3 plaintexts (canonical)
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K2_PLAINTEXT = "ITWASTOTALLYINVISIBLESHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATION"
K3_PLAINTEXT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRTHATESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"

def get_k_plaintexts() -> Dict[str, str]:
    """Return K1-K3 plaintexts."""
    return {
        'K1': K1_PLAINTEXT,
        'K2': K2_PLAINTEXT,
        'K3': K3_PLAINTEXT
    }

def tokenize_v2(text: str, cuts: List[int]) -> List[str]:
    """Apply tokenization v2 rules to get words."""
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

def generate_random_cuts(text_len: int, seed: int) -> List[int]:
    """Generate random cut positions for creating windows."""
    rng = random.Random(seed)
    # Average word length ~5-6 chars
    num_cuts = text_len // 6
    cuts = sorted(rng.sample(range(text_len - 1), min(num_cuts, text_len - 1)))
    if text_len - 1 not in cuts:
        cuts.append(text_len - 1)
    return cuts

def extract_windows(text: str, num_windows: int, seed: int) -> List[Tuple[str, List[str]]]:
    """Extract head-sized windows from text."""
    windows = []
    rng = random.Random(seed)
    
    for i in range(num_windows):
        # Random starting position
        if len(text) <= 75:
            start = 0
        else:
            start = rng.randint(0, len(text) - 75)
        
        window_text = text[start:start + 75]
        if len(window_text) < 75:
            # Pad with text wrap-around if needed
            window_text += text[:75 - len(window_text)]
        
        # Generate cuts for this window
        window_seed = seed + i * 1000
        cuts = generate_random_cuts(75, window_seed)
        words = tokenize_v2(window_text, cuts)
        
        windows.append((window_text, words))
    
    return windows

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
    # Get all keys
    all_keys = set(vec1.keys()) | set(vec2.keys())
    
    if not all_keys:
        return 0.0
    
    # Build vectors
    v1 = np.array([vec1.get(k, 0) for k in all_keys])
    v2 = np.array([vec2.get(k, 0) for k in all_keys])
    
    # Compute cosine
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
    
    # Find positions of function words
    fw_positions = []
    for i, word in enumerate(words):
        if word in function_words:
            fw_positions.append(i)
    
    if len(fw_positions) < 2:
        return 0.0, 0.0
    
    # Compute gaps
    gaps = []
    for i in range(1, len(fw_positions)):
        gaps.append(fw_positions[i] - fw_positions[i-1])
    
    if not gaps:
        return 0.0, 0.0
    
    mean_gap = np.mean(gaps)
    std_gap = np.std(gaps)
    cv_gap = std_gap / mean_gap if mean_gap > 0 else 0.0
    
    return mean_gap, cv_gap

def compute_wordlen_chi2(words: List[str], ref_dist: Dict[int, float]) -> float:
    """Compute chi-squared distance of word length distribution."""
    # Count word lengths
    length_counts = Counter(len(word) for word in words)
    total_words = sum(length_counts.values())
    
    if total_words == 0:
        return float('inf')
    
    # Compute chi-squared
    chi2 = 0.0
    for length in range(1, 15):  # Consider lengths 1-14
        observed = length_counts.get(length, 0) / total_words
        expected = ref_dist.get(length, 0.001)  # Small value to avoid division by zero
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

def bootstrap_cadence():
    """Main bootstrap function."""
    print("=" * 60)
    print("CADENCE BOOTSTRAP")
    print("=" * 60)
    
    # Setup paths
    output_dir = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/experiments/0457_fullbars/runs/2025-01-06/cadence")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get K1-K3 texts
    k_texts = get_k_plaintexts()
    
    # Reference word length distribution (English typical)
    ref_wordlen_dist = {
        1: 0.05, 2: 0.15, 3: 0.20, 4: 0.18, 5: 0.15,
        6: 0.10, 7: 0.08, 8: 0.05, 9: 0.02, 10: 0.01,
        11: 0.005, 12: 0.003, 13: 0.001, 14: 0.001
    }
    
    # Extract windows
    seed = 1337
    all_windows = []
    
    for k_name, k_text in k_texts.items():
        print(f"\nExtracting 2000 windows from {k_name}...")
        windows = extract_windows(k_text, 2000, seed + hash(k_name) % 10000)
        all_windows.extend(windows)
        print(f"  Extracted {len(windows)} windows")
    
    print(f"\nTotal windows: {len(all_windows)}")
    
    # Compute metrics for all windows
    print("\nComputing metrics...")
    metrics = {
        'cosine_bigram': [],
        'cosine_trigram': [],
        'fw_gap_mean': [],
        'fw_gap_cv': [],
        'wordlen_chi2': [],
        'vc_ratio': []
    }
    
    # Compute reference bigrams/trigrams from full K1-K3
    full_text = ''.join(k_texts.values())
    ref_bigrams = compute_letter_bigrams(full_text)
    ref_trigrams = compute_letter_trigrams(full_text)
    
    for window_text, words in all_windows:
        # Bigram/trigram cosine similarity
        window_bigrams = compute_letter_bigrams(window_text)
        window_trigrams = compute_letter_trigrams(window_text)
        
        metrics['cosine_bigram'].append(cosine_similarity(window_bigrams, ref_bigrams))
        metrics['cosine_trigram'].append(cosine_similarity(window_trigrams, ref_trigrams))
        
        # Function word gaps
        mean_gap, cv_gap = compute_function_word_gaps(words)
        metrics['fw_gap_mean'].append(mean_gap)
        metrics['fw_gap_cv'].append(cv_gap)
        
        # Word length chi-squared
        chi2 = compute_wordlen_chi2(words, ref_wordlen_dist)
        metrics['wordlen_chi2'].append(chi2)
        
        # Vowel-consonant ratio
        vc = compute_vc_ratio(window_text)
        metrics['vc_ratio'].append(vc)
    
    # Compute percentiles
    print("\nComputing percentiles...")
    thresholds = {
        'cosine_bigram_p5': float(np.percentile(metrics['cosine_bigram'], 5)),
        'cosine_trigram_p5': float(np.percentile(metrics['cosine_trigram'], 5)),
        'fw_gap_mean_p2.5': float(np.percentile(metrics['fw_gap_mean'], 2.5)),
        'fw_gap_mean_p97.5': float(np.percentile(metrics['fw_gap_mean'], 97.5)),
        'fw_gap_cv_p2.5': float(np.percentile(metrics['fw_gap_cv'], 2.5)),
        'fw_gap_cv_p97.5': float(np.percentile(metrics['fw_gap_cv'], 97.5)),
        'wordlen_chi2_p95': float(np.percentile(metrics['wordlen_chi2'], 95)),
        'vc_ratio_p2.5': float(np.percentile(metrics['vc_ratio'], 2.5)),
        'vc_ratio_p97.5': float(np.percentile(metrics['vc_ratio'], 97.5))
    }
    
    # Save thresholds
    thresholds_file = output_dir / "THRESHOLDS.json"
    with open(thresholds_file, 'w') as f:
        json.dump(thresholds, f, indent=2)
    
    print(f"\nSaved thresholds to {thresholds_file}")
    
    # Compute SHA-256 of thresholds
    with open(thresholds_file, 'rb') as f:
        thresholds_sha = hashlib.sha256(f.read()).hexdigest()
    
    print(f"Thresholds SHA-256: {thresholds_sha}")
    
    # Create bootstrap report
    report = {
        'source': 'K1K2K3',
        'windows_per_text': 2000,
        'total_windows': 6000,
        'seed': seed,
        'thresholds_sha256': thresholds_sha,
        'metrics_summary': {
            'cosine_bigram': {
                'min': float(np.min(metrics['cosine_bigram'])),
                'max': float(np.max(metrics['cosine_bigram'])),
                'mean': float(np.mean(metrics['cosine_bigram'])),
                'p5': thresholds['cosine_bigram_p5']
            },
            'cosine_trigram': {
                'min': float(np.min(metrics['cosine_trigram'])),
                'max': float(np.max(metrics['cosine_trigram'])),
                'mean': float(np.mean(metrics['cosine_trigram'])),
                'p5': thresholds['cosine_trigram_p5']
            },
            'fw_gap_mean': {
                'min': float(np.min(metrics['fw_gap_mean'])),
                'max': float(np.max(metrics['fw_gap_mean'])),
                'mean': float(np.mean(metrics['fw_gap_mean'])),
                'p2.5': thresholds['fw_gap_mean_p2.5'],
                'p97.5': thresholds['fw_gap_mean_p97.5']
            },
            'fw_gap_cv': {
                'min': float(np.min(metrics['fw_gap_cv'])),
                'max': float(np.max(metrics['fw_gap_cv'])),
                'mean': float(np.mean(metrics['fw_gap_cv'])),
                'p2.5': thresholds['fw_gap_cv_p2.5'],
                'p97.5': thresholds['fw_gap_cv_p97.5']
            },
            'wordlen_chi2': {
                'min': float(np.min(metrics['wordlen_chi2'])),
                'max': float(np.max(metrics['wordlen_chi2'])),
                'mean': float(np.mean(metrics['wordlen_chi2'])),
                'p95': thresholds['wordlen_chi2_p95']
            },
            'vc_ratio': {
                'min': float(np.min(metrics['vc_ratio'])),
                'max': float(np.max(metrics['vc_ratio'])),
                'mean': float(np.mean(metrics['vc_ratio'])),
                'p2.5': thresholds['vc_ratio_p2.5'],
                'p97.5': thresholds['vc_ratio_p97.5']
            }
        }
    }
    
    # Save bootstrap report
    report_file = output_dir / "REF_BOOTSTRAP.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create markdown report
    md_content = f"""# Cadence Bootstrap Report

**Date**: 2025-01-06  
**Seed**: {seed}  
**Source**: K1, K2, K3 plaintexts  
**Windows**: 2000 per text, 6000 total  
**Thresholds SHA-256**: {thresholds_sha}

## Methodology

1. Extracted 2000 random head-sized (75-char) windows from each of K1, K2, K3
2. Applied tokenization v2 rules to get words
3. Computed six metrics for each window:
   - Cosine similarity of letter bigrams
   - Cosine similarity of letter trigrams
   - Function word gap mean and CV
   - Word length chi-squared distance
   - Vowel-consonant ratio
4. Computed percentiles for threshold determination

## Thresholds

| Metric | Threshold | Value |
|--------|-----------|-------|
| cosine_bigram | ≥ P5 | {thresholds['cosine_bigram_p5']:.4f} |
| cosine_trigram | ≥ P5 | {thresholds['cosine_trigram_p5']:.4f} |
| fw_gap_mean | P2.5-P97.5 | [{thresholds['fw_gap_mean_p2.5']:.2f}, {thresholds['fw_gap_mean_p97.5']:.2f}] |
| fw_gap_cv | P2.5-P97.5 | [{thresholds['fw_gap_cv_p2.5']:.3f}, {thresholds['fw_gap_cv_p97.5']:.3f}] |
| wordlen_chi2 | ≤ P95 | {thresholds['wordlen_chi2_p95']:.3f} |
| vc_ratio | P2.5-P97.5 | [{thresholds['vc_ratio_p2.5']:.3f}, {thresholds['vc_ratio_p97.5']:.3f}] |

## Files Generated

- `THRESHOLDS.json`: Percentile thresholds for gate evaluation
- `REF_BOOTSTRAP.json`: Full bootstrap report with metrics summary
- `REF_BOOTSTRAP.md`: This report
"""
    
    md_file = output_dir / "REF_BOOTSTRAP.md"
    with open(md_file, 'w') as f:
        f.write(md_content)
    
    # Save SHA-256 of bootstrap report
    with open(report_file, 'rb') as f:
        report_sha = hashlib.sha256(f.read()).hexdigest()
    
    sha_file = output_dir / "REF_BOOTSTRAP.SHA256"
    with open(sha_file, 'w') as f:
        f.write(f"{report_sha}  REF_BOOTSTRAP.json\n")
        f.write(f"{thresholds_sha}  THRESHOLDS.json\n")
    
    print(f"\nBootstrap complete!")
    print(f"  Thresholds: {thresholds_file}")
    print(f"  Report: {report_file}")
    print(f"  Markdown: {md_file}")
    
    return thresholds_sha

if __name__ == "__main__":
    thresholds_sha = bootstrap_cadence()
    print(f"\n✅ Cadence bootstrap complete")
    print(f"   Thresholds SHA-256: {thresholds_sha}")