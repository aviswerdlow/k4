#!/usr/bin/env python3
"""
score_ct.py - Track A: Ciphertext-only structure tests
Tests IC, n-grams, and Kasiski patterns against null distributions
"""

import json, numpy as np, pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib

rng = np.random.default_rng(20250913)

ROOT = Path(".")
CTMAP = ROOT/"04_full_sculpture/letters_map_full_ct.csv"
SCAN  = ROOT/"03_projection_scan/light_sweep_results.json"
XPATH = ROOT/"04_full_sculpture/full_sculpture_cross_section.json"

OUT_SCAN = ROOT/"runs/projection_scan_ct"
OUT_XP   = ROOT/"runs/cross_section_ct"
OUT_SCAN.mkdir(parents=True, exist_ok=True)
OUT_XP.mkdir(parents=True, exist_ok=True)

N_NULL = 1000
# K4 anchor windows (0-based local indices): mask from null universe if you wish consistency with PT runs
K4_ANCHORS = [(21,25),(25,34),(63,69),(69,74)]

def compute_hash(filepath):
    """Compute SHA256 hash of file"""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

# ---- load CT universe ----
ct = pd.read_csv(CTMAP)  # global_tick, index_in_section, section, char
# build dict tick -> char
t2c = dict(zip(ct["global_tick"].astype(int), ct["char"].astype(str)))
# known (K1..K3) tick pool for null sampling
KNOWN = ct[ct["section"].isin(["K1","K2","K3"])]["global_tick"].astype(int).to_numpy()

# Also get K4 anchor ticks to potentially exclude from nulls
k4_anchor_ticks = []
for start, end in K4_ANCHORS:
    k4_rows = ct[(ct["section"] == "K4") &
                 (ct["index_in_section"] >= start) &
                 (ct["index_in_section"] < end)]
    k4_anchor_ticks.extend(k4_rows["global_tick"].tolist())
k4_anchor_set = set(k4_anchor_ticks)

# Remove K4 anchors from known pool
KNOWN_NO_ANCHOR = np.array([t for t in KNOWN if t not in k4_anchor_set])

def sample_null(m):
    """Sample m ticks from known non-anchor pool"""
    if len(KNOWN_NO_ANCHOR) >= m:
        return rng.choice(KNOWN_NO_ANCHOR, size=m, replace=False)
    else:
        # Fallback if not enough non-anchor ticks
        return rng.choice(KNOWN, size=m, replace=False)

def ic_score(s):
    """Index of coincidence"""
    if not s: return 0.0
    cnt=Counter(s)
    n=len(s)
    return sum(c*(c-1) for c in cnt.values())/(n*(n-1)) if n>1 else 0.0

def repeats_score(s, n=2):
    """Count repeated n-grams"""
    if len(s) < n: return 0
    cnt=Counter(s[i:i+n] for i in range(0, len(s)-n+1))
    return sum(c for g,c in cnt.items() if c>1)

def kasiski_score(s, n=3):
    """Sum of distances between repeated n-grams"""
    if len(s) < n: return 0
    pos={}
    for i in range(len(s)-n+1):
        g=s[i:i+n]
        pos.setdefault(g, []).append(i)
    score=0
    for g, P in pos.items():
        if len(P)>1:
            # Count number of distance pairs
            score += len(P) * (len(P) - 1) // 2
    return score

def null_p(obs, m, stat_fn):
    """Compute p-value from null distribution"""
    draws=[]
    for _ in range(N_NULL):
        sample = sample_null(m)
        s = "".join(t2c.get(int(t), "") for t in sample if int(t) in t2c)
        draws.append(stat_fn(s))
    draws=np.array(draws)
    return float((np.count_nonzero(draws >= obs) + 1) / (N_NULL + 1))

def score_selection(ticks_ordered, label):
    """Score a single selection against null distribution"""
    # Map tick → char and compute stats & nulls
    S = [int(t) for t in ticks_ordered if int(t) in t2c]
    s = "".join(t2c[int(t)] for t in S)

    if len(s) < 5:
        return dict(label=label, n=len(s), skip=True)

    results=[]
    stats_obs = {}

    for name, stat_fn in [
        ("ic", lambda s: ic_score(s)),
        ("rep2", lambda s: repeats_score(s,2)),
        ("rep3", lambda s: repeats_score(s,3)),
        ("kas3", lambda s: kasiski_score(s,3)),
    ]:
        obs = stat_fn(s)
        p   = null_p(obs, len(S), stat_fn)
        results.append((name, obs, p))
        stats_obs[name] = obs

    best = min(results, key=lambda x: x[2])  # smallest p_raw

    return dict(
        label=label,
        n=len(s),
        ic_obs=stats_obs["ic"],
        rep2_obs=stats_obs["rep2"],
        rep3_obs=stats_obs["rep3"],
        kas3_obs=stats_obs["kas3"],
        best_stat=best[0],
        best_obs=best[1],
        p_raw=best[2]
    )

print("="*60)
print("Track A: Ciphertext Structure Analysis")
print("="*60)
print(f"CT map: {CTMAP}")
print(f"Null samples: {N_NULL}")
print(f"Random seed: 20250913")
print()

# ---- Projection scan ----
if SCAN.exists():
    print("Processing projection scan selections...")
    scan = json.loads(SCAN.read_text())
    rows=[]

    # Process each M value
    for mkey in ["M_15", "M_20", "M_24"]:
        if mkey in scan.get("selections", {}):
            entries = scan["selections"][mkey]
            for e in entries:
                label=f"scan_angle{e['angle']}_M{mkey.split('_')[1]}"
                result = score_selection(e["tick_indices"], label)
                rows.append(result)
                if not result.get("skip"):
                    print(f"  {label}: n={result['n']}, p_raw={result['p_raw']:.4f}")

    if rows:
        df = pd.DataFrame(rows)
        # Remove skipped entries
        if 'skip' in df.columns:
            df = df[df['skip'] != True]

        if len(df) > 0:
            tests = len(df)
            df["p_adj"] = (df["p_raw"]*tests).clip(upper=1.0)
            df = df.sort_values("p_adj")

            # Save outputs
            df.to_csv(OUT_SCAN/"ct_top.csv", index=False)
            df.to_json(OUT_SCAN/"ct_scores.json", orient="records", indent=2)

            # Generate receipts
            receipts = {
                "timestamp": datetime.now().isoformat(),
                "track": "CT_structure",
                "input_hash": compute_hash(CTMAP),
                "scan_hash": compute_hash(SCAN) if SCAN.exists() else None,
                "random_seed": 20250913,
                "n_nulls": N_NULL,
                "n_tests": tests,
                "bonferroni_divisor": tests,
                "p_threshold": 0.001,
                "top_result": {
                    "label": df.iloc[0]["label"],
                    "p_raw": float(df.iloc[0]["p_raw"]),
                    "p_adj": float(df.iloc[0]["p_adj"])
                } if len(df) > 0 else None
            }

            with open(OUT_SCAN/"ct_receipts.json", "w") as f:
                json.dump(receipts, f, indent=2)

            print(f"\n[CT scan] Wrote {len(df)} results to {OUT_SCAN}")
            print(f"  Best p_adj: {df.iloc[0]['p_adj']:.4f} ({df.iloc[0]['label']})")

# ---- Cross-section paths ----
if XPATH.exists():
    print("\nProcessing cross-section paths...")
    xp=json.loads(XPATH.read_text())
    rows=[]

    # Process vertical columns
    if "vertical_columns" in xp:
        for col in xp["vertical_columns"]:
            label=f"col_{col['column_id']}"
            result = score_selection(col["global_ticks"], label)
            rows.append(result)
            if not result.get("skip"):
                print(f"  {label}: n={result['n']}, p_raw={result['p_raw']:.4f}")

    # Process jump paths
    if "section_jump_paths" in xp:
        for p in xp["section_jump_paths"]:
            label = f"jump_{p.get('name', 'unnamed')}"
            result = score_selection(p["global_ticks"], label)
            rows.append(result)
            if not result.get("skip"):
                print(f"  {label}: n={result['n']}, p_raw={result['p_raw']:.4f}")

    # Process spiral
    if "spiral" in xp:
        result = score_selection(xp["spiral"]["global_ticks"], "spiral")
        rows.append(result)
        if not result.get("skip"):
            print(f"  spiral: n={result['n']}, p_raw={result['p_raw']:.4f}")

    if rows:
        dfx = pd.DataFrame(rows)
        # Remove skipped entries
        if 'skip' in dfx.columns:
            dfx = dfx[dfx['skip'] != True]

        if len(dfx) > 0:
            T=len(dfx)
            dfx["p_adj"]=(dfx["p_raw"]*T).clip(upper=1.0)
            dfx = dfx.sort_values("p_adj")

            # Save outputs
            dfx.to_csv(OUT_XP/"ct_top.csv", index=False)
            dfx.to_json(OUT_XP/"ct_scores.json", orient="records", indent=2)

            # Generate receipts
            receipts = {
                "timestamp": datetime.now().isoformat(),
                "track": "CT_structure_paths",
                "input_hash": compute_hash(CTMAP),
                "xpath_hash": compute_hash(XPATH),
                "random_seed": 20250913,
                "n_nulls": N_NULL,
                "n_tests": T,
                "bonferroni_divisor": T,
                "p_threshold": 0.001,
                "top_result": {
                    "label": dfx.iloc[0]["label"],
                    "p_raw": float(dfx.iloc[0]["p_raw"]),
                    "p_adj": float(dfx.iloc[0]["p_adj"])
                } if len(dfx) > 0 else None
            }

            with open(OUT_XP/"ct_receipts.json", "w") as f:
                json.dump(receipts, f, indent=2)

            print(f"\n[CT paths] Wrote {len(dfx)} results to {OUT_XP}")
            print(f"  Best p_adj: {dfx.iloc[0]['p_adj']:.4f} ({dfx.iloc[0]['label']})")

print("\n" + "="*60)
print("CT Structure Analysis Complete")
print("="*60)