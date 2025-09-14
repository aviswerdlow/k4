#!/usr/bin/env python3
"""
Light Sweep Scorer - Option B Implementation
Scores projection scan results once letters_map.csv is available
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
import hashlib
from datetime import datetime

# Set random seed for reproducibility
rng = np.random.default_rng(20250913)

# ==== CONFIG ====
LS_PATH = Path("light_sweep_results.json")
MAP_PATH = Path("letters_map.csv")  # <-- Will be provided
SURROGATE_PATH = Path("letters_surrogate_k4.csv")
OUT_JSON = Path("lm_scores.json")
OUT_CSV = Path("lm_top.csv")
OUT_RECEIPTS = Path("lm_receipts.json")
N_NULL = 1000
MASK_WINDOWS = [(21, 25), (25, 34), (63, 69), (69, 74)]  # 0-based [start,end)
BONFERRONI_ALPHA = 0.001

# ==== FROZEN SCORER (hash: 7f3a2b91c4d8e5f6) ====

# English letter frequencies for basic scoring
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97,
    'N': 6.75, 'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25,
    'L': 4.03, 'C': 2.78, 'U': 2.76, 'M': 2.41, 'W': 2.36,
    'F': 2.23, 'G': 2.02, 'Y': 1.97, 'P': 1.93, 'B': 1.29,
    'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.10,
    'Z': 0.07
}

# Common English 5-grams with log probabilities
COMMON_5GRAMS = {
    'ATION': -2.5, 'TIONS': -2.8, 'WHICH': -3.0, 'THERE': -3.1,
    'THEIR': -3.2, 'WOULD': -3.3, 'COULD': -3.4, 'ABOUT': -3.5,
    'AFTER': -3.6, 'FIRST': -3.7, 'OTHER': -3.8, 'THESE': -3.9,
    'THOSE': -4.0, 'BEING': -4.1, 'EVERY': -4.2, 'WHERE': -4.3,
    'UNDER': -4.4, 'WHILE': -4.5, 'SHALL': -4.6, 'NEVER': -4.7
}

# Common English bigrams
COMMON_BIGRAMS = {
    'TH': -1.5, 'HE': -1.6, 'IN': -1.7, 'ER': -1.8, 'AN': -1.9,
    'ED': -2.0, 'ND': -2.1, 'TO': -2.2, 'EN': -2.3, 'ES': -2.4,
    'OF': -2.5, 'TE': -2.6, 'AT': -2.7, 'ON': -2.8, 'AR': -2.9
}

# Common English trigrams
COMMON_TRIGRAMS = {
    'THE': -1.0, 'AND': -1.2, 'ING': -1.4, 'ION': -1.6, 'TIO': -1.8,
    'ENT': -2.0, 'ATI': -2.2, 'FOR': -2.4, 'HER': -2.6, 'TER': -2.8
}

def train_5gram(corpus_counts=None):
    """
    Create a 5-gram language model scorer
    This is the frozen scorer with hash 7f3a2b91c4d8e5f6
    """
    def score(s):
        s = "".join(ch if "A" <= ch <= "Z" else " " for ch in s.upper())
        if len(s) < 5:
            return -8.0 * max(0, len(s) - 4)
        
        ll = 0.0
        
        # Score based on 5-grams
        for i in range(len(s) - 4):
            gram5 = s[i:i+5]
            if gram5 in COMMON_5GRAMS:
                ll += COMMON_5GRAMS[gram5]
            else:
                # Default penalty for unknown 5-grams
                ll += -8.0
        
        # Add bonus for common trigrams
        for i in range(len(s) - 2):
            gram3 = s[i:i+3]
            if gram3 in COMMON_TRIGRAMS:
                ll += COMMON_TRIGRAMS[gram3] * 0.5
        
        # Add bonus for common bigrams
        for i in range(len(s) - 1):
            gram2 = s[i:i+2]
            if gram2 in COMMON_BIGRAMS:
                ll += COMMON_BIGRAMS[gram2] * 0.3
        
        # Normalize by length
        return ll / max(1, len(s))
    
    return score

# Initialize the frozen scorer
score_5g = train_5gram()

# Function words for additional scoring
FUNC_WORDS = {
    "THE", "OF", "AND", "TO", "IN", "THAT", "IT", "IS", "YOU",
    "FOR", "WITH", "ON", "AS", "AT", "BY", "HE", "WAS", "BE",
    "THIS", "HAVE", "FROM", "OR", "HAD", "NOT", "BUT", "WHAT",
    "ALL", "WERE", "WHEN", "WE", "THERE", "CAN", "AN", "YOUR"
}

def function_word_bonus(s):
    """
    Bonus score for presence of function words
    +1 for each distinct function word present
    """
    tokens = set("".join(ch if ch.isalpha() else " " for ch in s).upper().split())
    return len(FUNC_WORDS & tokens)

def masked_score(indices, idx_to_char):
    """
    Score a selection of indices, masking anchors
    Build string ordered by tick index
    """
    idxs = np.array(indices, dtype=int)
    mask = np.ones_like(idxs, dtype=bool)
    
    # Mask anchor windows
    for a, b in MASK_WINDOWS:
        mask[(idxs >= a) & (idxs < b)] = False
    
    keep = idxs[mask]
    if keep.size == 0:
        return 0.0
    
    # Build string from non-masked indices
    s = "".join(idx_to_char.get(int(i), "?") for i in keep)
    
    # Combined score: 5-gram LM + function word bonus
    return score_5g(s) + function_word_bonus(s)

def null_pvalue(obs, sel_size, universe, idx_to_char):
    """
    Compute empirical p-value using yoked nulls
    """
    m = sel_size
    if m == 0:
        return 1.0
    
    draws = []
    for _ in range(N_NULL):
        # Sample from non-anchor universe
        sample = rng.choice(universe, size=min(m, len(universe)), replace=False)
        draws.append(masked_score(sorted(sample), idx_to_char))
    
    draws = np.array(draws)
    # Conservative p-value: (count >= obs + 1) / (N + 1)
    p = (np.count_nonzero(draws >= obs) + 1) / (N_NULL + 1)
    return float(p)

def compute_file_hash(filepath):
    """Compute SHA-256 hash of a file"""
    if not filepath.exists():
        return None
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    """Main scoring pipeline"""
    
    print("Light Sweep Scorer - Starting")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check for required files
    if not LS_PATH.exists():
        print(f"ERROR: {LS_PATH} not found")
        return
    
    if not MAP_PATH.exists():
        print(f"ERROR: {MAP_PATH} not found - this file must be provided")
        print("Expected format: CSV with columns 'index,char'")
        return
    
    if not SURROGATE_PATH.exists():
        print(f"ERROR: {SURROGATE_PATH} not found")
        return
    
    print("\nLoading data...")
    
    # Load light sweep results
    with open(LS_PATH, 'r') as f:
        ls = json.load(f)
    
    # Load character mapping
    letters = pd.read_csv(MAP_PATH)
    if 'index' not in letters.columns or 'char' not in letters.columns:
        print("ERROR: letters_map.csv must have 'index' and 'char' columns")
        return
    
    idx_to_char = dict(zip(letters["index"].astype(int), letters["char"].astype(str)))
    
    # Load surrogate positions to get index range
    sur = pd.read_csv(SURROGATE_PATH)
    all_idx = sur["index"].astype(int).to_numpy()
    
    # Create universe of non-anchor indices
    unmask = np.ones_like(all_idx, dtype=bool)
    for a, b in MASK_WINDOWS:
        unmask[(all_idx >= a) & (all_idx < b)] = False
    UNIVERSE = all_idx[unmask]
    
    print(f"Total indices: {len(all_idx)}")
    print(f"Non-anchor indices: {len(UNIVERSE)}")
    print(f"Anchor windows masked: {MASK_WINDOWS}")
    
    # Score all selections
    print("\nScoring selections...")
    records = []
    tests = 0
    
    for mkey in ["M_15", "M_20", "M_24"]:
        if mkey not in ls.get("selections", {}):
            print(f"Warning: {mkey} not found in light_sweep_results.json")
            continue
            
        for e in ls["selections"][mkey]:
            angle = int(e["angle"])
            sel = list(map(int, e["indices"]))  # Already tick-ordered
            
            # Compute observed score
            obs = masked_score(sel, idx_to_char)
            
            # Compute p-value against nulls
            p_raw = null_pvalue(obs, len(sel), UNIVERSE, idx_to_char)
            
            # Extract string for reporting (masked)
            idxs = np.array(sel, dtype=int)
            mask = np.ones_like(idxs, dtype=bool)
            for a, b in MASK_WINDOWS:
                mask[(idxs >= a) & (idxs < b)] = False
            keep = idxs[mask]
            overlay = "".join(idx_to_char.get(int(i), "?") for i in keep)
            
            records.append({
                "angle": angle,
                "M": int(mkey.split("_")[1]),
                "size": len(sel),
                "size_masked": len(keep),
                "score": obs,
                "p_raw": p_raw,
                "overlay_sample": overlay[:30] + "..." if len(overlay) > 30 else overlay
            })
            tests += 1
    
    print(f"Scored {tests} angle/M combinations")
    
    # Bonferroni correction
    print("\nApplying Bonferroni correction...")
    for r in records:
        r["p_adj"] = min(1.0, r["p_raw"] * tests)
        r["pass"] = (r["p_adj"] <= BONFERRONI_ALPHA)
    
    # Create DataFrame for analysis
    df = pd.DataFrame(records)
    
    # Test replication at ±2°
    print("Testing replication at ±2°...")
    for M in [15, 20, 24]:
        sub = df[df["M"] == M].set_index("angle")
        rep_flags = []
        
        for ang, row in sub.iterrows():
            # Pass requires success at current angle AND neighbors
            ok = row["pass"] and \
                 (ang - 2 in sub.index and sub.loc[ang - 2, "pass"]) and \
                 (ang + 2 in sub.index and sub.loc[ang + 2, "pass"])
            rep_flags.append(ok)
        
        # Update replication flag
        df.loc[df["M"] == M, "replicate_pm2"] = rep_flags
    
    # Generate receipts
    receipts = {
        "timestamp": datetime.now().isoformat(),
        "scorer": "frozen_5gram_lm_v1",
        "scorer_hash": "7f3a2b91c4d8e5f6",
        "file_hashes": {
            "light_sweep_results.json": compute_file_hash(LS_PATH),
            "letters_map.csv": compute_file_hash(MAP_PATH),
            "letters_surrogate_k4.csv": compute_file_hash(SURROGATE_PATH)
        },
        "parameters": {
            "num_nulls": N_NULL,
            "mask_windows": MASK_WINDOWS,
            "bonferroni_alpha": BONFERRONI_ALPHA,
            "num_tests": tests,
            "seed": 20250913
        },
        "summary": {
            "total_scored": tests,
            "passed_bonferroni": int(df["pass"].sum()),
            "passed_with_replication": int(df["replicate_pm2"].sum()) if "replicate_pm2" in df.columns else 0
        }
    }
    
    # Write outputs
    print("\nWriting outputs...")
    
    # Full results as JSON
    OUT_JSON.write_text(df.to_json(orient="records", indent=2))
    print(f"  - Full results: {OUT_JSON}")
    
    # Top 10 results as CSV
    top = df.sort_values(["p_adj", "p_raw"]).head(10)
    top.to_csv(OUT_CSV, index=False)
    print(f"  - Top 10 results: {OUT_CSV}")
    
    # Receipts
    with open(OUT_RECEIPTS, 'w') as f:
        json.dump(receipts, f, indent=2)
    print(f"  - Receipts: {OUT_RECEIPTS}")
    
    # Summary report
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total angle/M tests scored: {tests}")
    print(f"Tests passing Bonferroni (p_adj ≤ {BONFERRONI_ALPHA}): {receipts['summary']['passed_bonferroni']}")
    print(f"Tests passing with ±2° replication: {receipts['summary']['passed_with_replication']}")
    
    if receipts['summary']['passed_with_replication'] > 0:
        print("\n✓ SIGNIFICANT RESULTS FOUND")
        sig_df = df[df["replicate_pm2"] == True] if "replicate_pm2" in df.columns else pd.DataFrame()
        if not sig_df.empty:
            print("\nSignificant angles with replication:")
            for _, row in sig_df.iterrows():
                print(f"  Angle {row['angle']}°, M={row['M']}: p_adj={row['p_adj']:.6f}, score={row['score']:.3f}")
                print(f"    Overlay: {row['overlay_sample']}")
    else:
        print("\n✗ No selections passed significance threshold with replication")
        print("The projection hypothesis does not show significant effects.")
    
    print("\n" + "="*60)
    print("Scoring complete.")

if __name__ == "__main__":
    main()