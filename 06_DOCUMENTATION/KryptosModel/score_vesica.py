#!/usr/bin/env python3
"""
score_vesica.py - Score vesica piscis geometric selections
Tests perimeter, lens regions, and paired-alternation patterns
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib

# Configuration
rng = np.random.default_rng(20250913)
ROOT = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus/06_DOCUMENTATION/KryptosModel")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Input paths
PT_MAP = ROOT / "04_full_sculpture/letters_map_full.csv"
CT_MAP = ROOT / "04_full_sculpture/letters_map_full_ct.csv"
FULL_TICKS = ROOT / "04_full_sculpture/kryptos_full_sculpture_ticks.csv"

# Vesica paths
VESICA_DIR = ROOT / "07_vesica"
PERIMETER = VESICA_DIR / "02_ticks/vesica_perimeter_ticks.csv"
LENS_20 = VESICA_DIR / "02_ticks/vesica_lens_ticks_eps20.csv"
LENS_30 = VESICA_DIR / "02_ticks/vesica_lens_ticks_eps30.csv"
PAIRS = VESICA_DIR / "03_pairs/vesica_nearest_pairs.csv"
SETUP = VESICA_DIR / "01_setup/vesica_setup.json"
RECEIPTS = VESICA_DIR / "05_receipts/vesica_receipts.json"

# Output directories
OUT_PT = ROOT / f"runs/vesica_pt/{TIMESTAMP}"
OUT_CT = ROOT / f"runs/vesica_ct/{TIMESTAMP}"
OUT_PT.mkdir(parents=True, exist_ok=True)
OUT_CT.mkdir(parents=True, exist_ok=True)

# Constants
N_NULL = 1000
K4_ANCHORS = [(21,25), (25,34), (63,69), (69,74)]  # K4 local indices to mask

def compute_hash(filepath):
    """Compute SHA256 hash of file"""
    if not filepath.exists():
        return None
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

def load_character_maps():
    """Load PT and CT character maps"""
    pt_df = pd.read_csv(PT_MAP)
    ct_df = pd.read_csv(CT_MAP)

    # Create tick->char dictionaries
    pt_map = dict(zip(pt_df["global_tick"].astype(int), pt_df["char"]))
    ct_map = dict(zip(ct_df["global_tick"].astype(int), ct_df["char"]))

    # Get K4 anchor ticks
    k4_anchors = []
    for start, end in K4_ANCHORS:
        k4_rows = pt_df[(pt_df["section"] == "K4") &
                        (pt_df["index_in_section"] >= start) &
                        (pt_df["index_in_section"] < end)]
        k4_anchors.extend(k4_rows["global_tick"].tolist())

    # Known non-anchor ticks (K1-K3 only, excluding K4 anchors)
    known_ticks = pt_df[pt_df["section"].isin(["K1", "K2", "K3"])]["global_tick"].astype(int).tolist()
    known_no_anchor = [t for t in known_ticks if t not in k4_anchors]

    return pt_map, ct_map, known_no_anchor, set(k4_anchors)

def load_vesica_selections():
    """Load vesica geometric selections"""
    selections = {}

    # Load perimeter
    if PERIMETER.exists():
        perimeter_df = pd.read_csv(PERIMETER)
        selections["perimeter"] = perimeter_df["global_tick"].astype(int).tolist()
        print(f"  Perimeter: {len(selections['perimeter'])} ticks")

    # Load lens regions
    if LENS_20.exists():
        lens20_df = pd.read_csv(LENS_20)
        selections["lens_eps20"] = lens20_df["global_tick"].astype(int).tolist()
        print(f"  Lens ε=20mm: {len(selections['lens_eps20'])} ticks")

    if LENS_30.exists():
        lens30_df = pd.read_csv(LENS_30)
        selections["lens_eps30"] = lens30_df["global_tick"].astype(int).tolist()
        print(f"  Lens ε=30mm: {len(selections['lens_eps30'])} ticks")

    # Load paired-alternation
    if PAIRS.exists():
        pairs_df = pd.read_csv(PAIRS)
        # Sort by distance and interleave pool/away ticks
        pairs_df = pairs_df.sort_values("dist_m")
        paired_ticks = []
        seen = set()
        for _, row in pairs_df.iterrows():
            pool_tick = int(row["pool_tick"])
            away_tick = int(row["away_tick"])
            if pool_tick not in seen:
                paired_ticks.append(pool_tick)
                seen.add(pool_tick)
            if away_tick not in seen:
                paired_ticks.append(away_tick)
                seen.add(away_tick)
        selections["paired_alternation"] = paired_ticks
        print(f"  Paired-alternation: {len(selections['paired_alternation'])} ticks")

    return selections

def ic_score(text):
    """Index of coincidence"""
    if len(text) < 2:
        return 0.0
    n = len(text)
    freq = Counter(text)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

def ngram_repeats(text, n):
    """Count repeated n-grams"""
    if len(text) < n:
        return 0
    ngrams = Counter(text[i:i+n] for i in range(len(text) - n + 1))
    return sum(1 for count in ngrams.values() if count > 1)

def kasiski_score(text, n=3):
    """Kasiski spacing score"""
    if len(text) < n:
        return 0
    positions = {}
    for i in range(len(text) - n + 1):
        gram = text[i:i+n]
        positions.setdefault(gram, []).append(i)

    score = 0
    for gram, pos_list in positions.items():
        if len(pos_list) > 1:
            score += len(pos_list) * (len(pos_list) - 1) // 2
    return score

def simple_lm_score(text):
    """Simple 5-gram LM with function word bonus"""
    if not text:
        return 0.0

    score = 0.0

    # Function words bonus
    function_words = {'THE', 'AND', 'OF', 'TO', 'IN', 'A', 'IS', 'IT', 'FOR', 'WITH'}
    for word in function_words:
        if word in text:
            score += len(word) * 0.5

    # Basic English frequency
    english_freq = {
        'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
        'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
        'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
        'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
        'Q': 0.10, 'Z': 0.07
    }

    for char in text:
        if char in english_freq:
            score += english_freq[char] / 100

    return score / len(text)

def score_ct_selection(ticks, ct_map, known_pool, label):
    """Score CT structure of a selection"""
    # Map ticks to characters
    text = ''.join(ct_map.get(t, '') for t in ticks if t in ct_map)

    if len(text) < 5:
        return None

    # Compute observed statistics
    obs_ic = ic_score(text)
    obs_bi = ngram_repeats(text, 2)
    obs_tri = ngram_repeats(text, 3)
    obs_kas = kasiski_score(text, 3)

    # Generate null distribution
    null_ics = []
    null_bis = []
    null_tris = []
    null_kass = []

    for _ in range(N_NULL):
        # Use replacement if selection is larger than pool
        replace = len(ticks) > len(known_pool)
        null_ticks = rng.choice(known_pool, size=min(len(ticks), len(known_pool)), replace=replace)
        null_text = ''.join(ct_map.get(t, '') for t in null_ticks if t in ct_map)
        null_ics.append(ic_score(null_text))
        null_bis.append(ngram_repeats(null_text, 2))
        null_tris.append(ngram_repeats(null_text, 3))
        null_kass.append(kasiski_score(null_text, 3))

    # Compute p-values
    p_ic = (sum(1 for x in null_ics if x >= obs_ic) + 1) / (N_NULL + 1)
    p_bi = (sum(1 for x in null_bis if x >= obs_bi) + 1) / (N_NULL + 1)
    p_tri = (sum(1 for x in null_tris if x >= obs_tri) + 1) / (N_NULL + 1)
    p_kas = (sum(1 for x in null_kass if x >= obs_kas) + 1) / (N_NULL + 1)

    min_p = min(p_ic, p_bi, p_tri, p_kas)
    best_stat = ['ic', 'bigram', 'trigram', 'kasiski'][[p_ic, p_bi, p_tri, p_kas].index(min_p)]

    return {
        'label': label,
        'n': len(text),
        'ic': obs_ic,
        'bigrams': obs_bi,
        'trigrams': obs_tri,
        'kasiski': obs_kas,
        'p_ic': p_ic,
        'p_bi': p_bi,
        'p_tri': p_tri,
        'p_kas': p_kas,
        'p_raw': min_p,
        'best_stat': best_stat
    }

def score_pt_selection(ticks, pt_map, known_pool, k4_anchors, label):
    """Score PT language model of a selection"""
    # Filter out K4 anchors and unknown characters
    valid_ticks = [t for t in ticks if t not in k4_anchors and pt_map.get(t, '?') != '?']
    text = ''.join(pt_map.get(t, '') for t in valid_ticks if t in pt_map)

    if len(text) < 5:
        return None

    # Compute observed LM score
    obs_score = simple_lm_score(text)

    # Generate null distribution
    null_scores = []
    for _ in range(N_NULL):
        # Use replacement if selection is larger than pool
        replace = len(valid_ticks) > len(known_pool)
        null_ticks = rng.choice(known_pool, size=min(len(valid_ticks), len(known_pool)), replace=replace)
        null_text = ''.join(pt_map.get(t, '') for t in null_ticks if t in pt_map)
        null_scores.append(simple_lm_score(null_text))

    # Compute p-value
    p_value = (sum(1 for x in null_scores if x >= obs_score) + 1) / (N_NULL + 1)

    return {
        'label': label,
        'n': len(text),
        'lm_score': obs_score,
        'p_raw': p_value
    }

def main():
    print("="*60)
    print("Vesica Piscis Geometric Selection Scoring")
    print("="*60)
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Random seed: 20250913")
    print(f"Null samples: {N_NULL}")
    print()

    # Load character maps
    print("Loading character maps...")
    pt_map, ct_map, known_pool, k4_anchors = load_character_maps()
    print(f"  Known non-anchor ticks: {len(known_pool)}")
    print(f"  K4 anchor ticks masked: {len(k4_anchors)}")

    # Load vesica selections
    print("\nLoading vesica selections...")
    selections = load_vesica_selections()
    n_tests = len(selections)

    if n_tests == 0:
        print("ERROR: No vesica selections found!")
        return

    print(f"\nTotal tests: {n_tests}")
    print(f"Bonferroni divisor: {n_tests}")
    print(f"Adjusted threshold: p_adj ≤ 0.001")

    # Track A: CT Structure
    print("\n" + "="*40)
    print("Track A: Ciphertext Structure")
    print("="*40)

    ct_results = []
    for label, ticks in selections.items():
        result = score_ct_selection(ticks, ct_map, known_pool, label)
        if result:
            ct_results.append(result)
            print(f"  {label}: n={result['n']}, p_raw={result['p_raw']:.4f}")

    if ct_results:
        ct_df = pd.DataFrame(ct_results)
        ct_df['p_adj'] = (ct_df['p_raw'] * n_tests).clip(upper=1.0)
        ct_df = ct_df.sort_values('p_adj')

        # Save results
        ct_df.to_csv(OUT_CT / "ct_top.csv", index=False)
        ct_df.to_json(OUT_CT / "ct_scores.json", orient='records', indent=2)

        # Generate receipts
        ct_receipts = {
            'timestamp': TIMESTAMP,
            'track': 'CT_structure_vesica',
            'random_seed': 20250913,
            'n_nulls': N_NULL,
            'n_tests': n_tests,
            'bonferroni_divisor': n_tests,
            'p_threshold': 0.001,
            'input_hashes': {
                'ct_map': compute_hash(CT_MAP),
                'perimeter': compute_hash(PERIMETER),
                'lens_20': compute_hash(LENS_20),
                'lens_30': compute_hash(LENS_30),
                'pairs': compute_hash(PAIRS)
            },
            'best_result': {
                'label': ct_df.iloc[0]['label'],
                'p_raw': float(ct_df.iloc[0]['p_raw']),
                'p_adj': float(ct_df.iloc[0]['p_adj']),
                'passes': bool(ct_df.iloc[0]['p_adj'] <= 0.001)
            }
        }

        with open(OUT_CT / "ct_receipts.json", 'w') as f:
            json.dump(ct_receipts, f, indent=2)

        print(f"\nBest CT result: {ct_df.iloc[0]['label']}")
        print(f"  p_adj = {ct_df.iloc[0]['p_adj']:.4f}")
        print(f"  {'✓ PASSES' if ct_df.iloc[0]['p_adj'] <= 0.001 else '✗ FAILS'}")

    # Track B: PT Language Model
    print("\n" + "="*40)
    print("Track B: Plaintext Language Model")
    print("="*40)

    pt_results = []
    for label, ticks in selections.items():
        result = score_pt_selection(ticks, pt_map, known_pool, k4_anchors, label)
        if result:
            pt_results.append(result)
            print(f"  {label}: n={result['n']}, p_raw={result['p_raw']:.4f}")

    if pt_results:
        pt_df = pd.DataFrame(pt_results)
        pt_df['p_adj'] = (pt_df['p_raw'] * n_tests).clip(upper=1.0)
        pt_df = pt_df.sort_values('p_adj')

        # Save results
        pt_df.to_csv(OUT_PT / "lm_top.csv", index=False)
        pt_df.to_json(OUT_PT / "lm_scores.json", orient='records', indent=2)

        # Generate receipts
        pt_receipts = {
            'timestamp': TIMESTAMP,
            'track': 'PT_LM_vesica',
            'random_seed': 20250913,
            'n_nulls': N_NULL,
            'n_tests': n_tests,
            'bonferroni_divisor': n_tests,
            'p_threshold': 0.001,
            'k4_anchors_masked': K4_ANCHORS,
            'input_hashes': {
                'pt_map': compute_hash(PT_MAP),
                'perimeter': compute_hash(PERIMETER),
                'lens_20': compute_hash(LENS_20),
                'lens_30': compute_hash(LENS_30),
                'pairs': compute_hash(PAIRS)
            },
            'best_result': {
                'label': pt_df.iloc[0]['label'],
                'p_raw': float(pt_df.iloc[0]['p_raw']),
                'p_adj': float(pt_df.iloc[0]['p_adj']),
                'passes': bool(pt_df.iloc[0]['p_adj'] <= 0.001)
            }
        }

        with open(OUT_PT / "lm_receipts.json", 'w') as f:
            json.dump(pt_receipts, f, indent=2)

        print(f"\nBest PT result: {pt_df.iloc[0]['label']}")
        print(f"  p_adj = {pt_df.iloc[0]['p_adj']:.4f}")
        print(f"  {'✓ PASSES' if pt_df.iloc[0]['p_adj'] <= 0.001 else '✗ FAILS'}")

    # Final summary
    print("\n" + "="*60)
    print("VESICA ANALYSIS COMPLETE")
    print("="*60)

    ct_pass = False
    if ct_results and ct_df is not None and len(ct_df) > 0:
        ct_pass = ct_df.iloc[0]['p_adj'] <= 0.001

    pt_pass = False
    if pt_results and pt_df is not None and len(pt_df) > 0:
        pt_pass = pt_df.iloc[0]['p_adj'] <= 0.001

    if ct_pass or pt_pass:
        print("🎯 SIGNIFICANT RESULT FOUND!")
        if ct_pass:
            print("  CT structure shows non-random pattern")
        if pt_pass:
            print("  PT language model shows significant pattern")
        print("\n⚠️  Requires replication testing (±2° rotation or ±2cm translation)")
    else:
        print("No vesica selection passes the frozen criteria.")
        print("The two-arc interaction hypothesis can be retired.")

    print(f"\nResults saved to:")
    print(f"  {OUT_CT}")
    print(f"  {OUT_PT}")

if __name__ == "__main__":
    main()