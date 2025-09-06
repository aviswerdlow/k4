#!/usr/bin/env python3
"""
Campaign L: Alternative cheap signals (report-only).
Tests LZ compression, mutual information, and token entropy.
"""

import json
import csv
import lzma
import math
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import Dict, List
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))


def compute_lz_ratio(text: str) -> float:
    """Compute LZ compression ratio."""
    original_bytes = text.encode('utf-8')
    compressed = lzma.compress(original_bytes, preset=6)
    return len(compressed) / len(original_bytes)


def compute_shannon_entropy(text: str) -> float:
    """Compute Shannon entropy of character distribution."""
    if not text:
        return 0.0
    
    counts = Counter(text)
    total = len(text)
    entropy = 0.0
    
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


def compute_mutual_information(text1: str, text2: str) -> float:
    """
    Compute approximate mutual information between two texts.
    Uses character-level joint distribution.
    """
    if len(text1) != len(text2):
        # Pad shorter text
        max_len = max(len(text1), len(text2))
        text1 = text1.ljust(max_len, 'X')
        text2 = text2.ljust(max_len, 'X')
    
    # Compute joint distribution
    joint_counts = Counter(zip(text1, text2))
    marginal1 = Counter(text1)
    marginal2 = Counter(text2)
    total = len(text1)
    
    mi = 0.0
    for (c1, c2), joint_count in joint_counts.items():
        p_joint = joint_count / total
        p1 = marginal1[c1] / total
        p2 = marginal2[c2] / total
        
        if p_joint > 0 and p1 > 0 and p2 > 0:
            mi += p_joint * math.log2(p_joint / (p1 * p2))
    
    return mi


def compute_token_entropy(text: str, token_len: int = 4) -> float:
    """Compute entropy of token distribution."""
    tokens = []
    for i in range(len(text) - token_len + 1):
        tokens.append(text[i:i+token_len])
    
    if not tokens:
        return 0.0
    
    counts = Counter(tokens)
    total = len(tokens)
    entropy = 0.0
    
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


def run_alternate_signals(
    candidates_file: Path,
    output_dir: Path,
    seed: int = 1337
) -> None:
    """
    Run Campaign L: Alternative signals analysis.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load candidates
    with open(candidates_file) as f:
        data = json.load(f)
        heads = data["heads"][:50]  # Analyze subset
    
    print(f"Analyzing {len(heads)} heads with alternative signals")
    print(f"Signals: LZ ratio, MI vs shuffle, Shannon entropy, token entropy\n")
    
    results = []
    
    for head_idx, head in enumerate(heads):
        text = head["text"]
        label = head["label"]
        
        if head_idx % 10 == 0:
            print(f"Processing head {head_idx+1}/{len(heads)}: {label}")
        
        # Generate shuffle for MI comparison
        import random
        random.seed(seed + head_idx)
        shuffled = ''.join(random.sample(text, len(text)))
        
        # Compute signals
        lz_ratio = compute_lz_ratio(text)
        lz_ratio_shuffled = compute_lz_ratio(shuffled)
        
        shannon_entropy = compute_shannon_entropy(text)
        shannon_entropy_shuffled = compute_shannon_entropy(shuffled)
        
        token_entropy_4 = compute_token_entropy(text, 4)
        token_entropy_4_shuffled = compute_token_entropy(shuffled, 4)
        
        mi_vs_shuffled = compute_mutual_information(text, shuffled)
        
        result = {
            "label": label,
            "lz_ratio": lz_ratio,
            "lz_ratio_shuffled": lz_ratio_shuffled,
            "lz_delta": lz_ratio - lz_ratio_shuffled,
            "shannon_entropy": shannon_entropy,
            "shannon_entropy_shuffled": shannon_entropy_shuffled,
            "shannon_delta": shannon_entropy - shannon_entropy_shuffled,
            "token_entropy_4": token_entropy_4,
            "token_entropy_4_shuffled": token_entropy_4_shuffled,
            "token_delta": token_entropy_4 - token_entropy_4_shuffled,
            "mi_vs_shuffled": mi_vs_shuffled
        }
        results.append(result)
    
    # Write results
    results_path = output_dir / "ALTERNATE_SIGNALS.csv"
    with open(results_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Calculate correlations (simplified)
    # Group by register/category if available
    categories = {}
    for result in results:
        # Extract category from label
        if "_" in result["label"]:
            cat = result["label"].split("_")[1]
        else:
            cat = "OTHER"
        
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)
    
    # Summary statistics
    summary_path = output_dir / "SIGNALS_SUMMARY.csv"
    summary_data = []
    
    for cat, cat_results in categories.items():
        if cat_results:
            summary = {
                "category": cat,
                "count": len(cat_results),
                "mean_lz_delta": sum(r["lz_delta"] for r in cat_results) / len(cat_results),
                "mean_shannon_delta": sum(r["shannon_delta"] for r in cat_results) / len(cat_results),
                "mean_token_delta": sum(r["token_delta"] for r in cat_results) / len(cat_results),
                "mean_mi": sum(r["mi_vs_shuffled"] for r in cat_results) / len(cat_results)
            }
            summary_data.append(summary)
    
    with open(summary_path, 'w', newline='') as f:
        if summary_data:
            writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
            writer.writeheader()
            writer.writerows(summary_data)
    
    # Generate report
    report_path = output_dir / "ALTERNATE_SIGNALS_REPORT.md"
    with open(report_path, 'w') as f:
        f.write("# Campaign L: Alternative Signals Report\n\n")
        f.write(f"**Date:** {datetime.now().date()}\n")
        f.write(f"**Heads analyzed:** {len(heads)}\n")
        f.write("**Type:** Report-only (no gating changes)\n\n")
        
        f.write("## Signals Tested\n\n")
        f.write("1. **LZ Compression Ratio**: LZMA compression efficiency\n")
        f.write("2. **Shannon Entropy**: Character distribution entropy\n")
        f.write("3. **Token Entropy**: 4-gram token distribution entropy\n")
        f.write("4. **Mutual Information**: MI between text and shuffle\n\n")
        
        f.write("## Summary by Category\n\n")
        f.write("| Category | Count | LZ Δ | Shannon Δ | Token Δ | MI |\n")
        f.write("|----------|-------|------|-----------|---------|----|\n")
        
        for summary in summary_data:
            f.write(f"| {summary['category']} | {summary['count']} | ")
            f.write(f"{summary['mean_lz_delta']:+.3f} | ")
            f.write(f"{summary['mean_shannon_delta']:+.3f} | ")
            f.write(f"{summary['mean_token_delta']:+.3f} | ")
            f.write(f"{summary['mean_mi']:.3f} |\n")
        
        f.write("\n## Key Observations\n\n")
        
        # Find signals with largest deltas
        all_lz_deltas = [r["lz_delta"] for r in results]
        all_shannon_deltas = [r["shannon_delta"] for r in results]
        all_token_deltas = [r["token_delta"] for r in results]
        
        f.write(f"1. **LZ compression**: Mean Δ = {sum(all_lz_deltas)/len(all_lz_deltas):.4f}\n")
        f.write(f"2. **Shannon entropy**: Mean Δ = {sum(all_shannon_deltas)/len(all_shannon_deltas):.4f}\n")
        f.write(f"3. **Token entropy**: Mean Δ = {sum(all_token_deltas)/len(all_token_deltas):.4f}\n")
        
        # Check which signal shows most differentiation
        lz_spread = max(all_lz_deltas) - min(all_lz_deltas)
        shannon_spread = max(all_shannon_deltas) - min(all_shannon_deltas)
        token_spread = max(all_token_deltas) - min(all_token_deltas)
        
        spreads = [
            ("LZ compression", lz_spread),
            ("Shannon entropy", shannon_spread),
            ("Token entropy", token_spread)
        ]
        best_signal = max(spreads, key=lambda x: x[1])
        
        f.write(f"\n**Most discriminative signal**: {best_signal[0]} (spread = {best_signal[1]:.4f})\n")
        
        f.write("\n## Conclusion\n\n")
        f.write("Alternative signals provide additional characterization of head quality.\n")
        f.write("These metrics are **report-only** and do not affect Explore decisions.\n")
        f.write("Further analysis could correlate these signals with promotion outcomes.\n")
    
    print(f"\n{'='*60}")
    print("Alternative Signals Campaign Complete:")
    print(f"  Heads analyzed: {len(heads)}")
    print(f"  Signals computed: 4")
    print(f"  Output: {output_dir}")
    
    if summary_data:
        print("\nMean deltas across categories:")
        all_lz = sum(s["mean_lz_delta"] for s in summary_data) / len(summary_data)
        all_shannon = sum(s["mean_shannon_delta"] for s in summary_data) / len(summary_data)
        print(f"  LZ compression: {all_lz:+.4f}")
        print(f"  Shannon entropy: {all_shannon:+.4f}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run alternative signals analysis")
    parser.add_argument("--candidates",
                       default="experiments/pipeline_v2/data/heads_registers.json")
    parser.add_argument("--out",
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-L/",
                       type=Path)
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    run_alternate_signals(
        Path(args.candidates),
        args.out,
        args.seed
    )


if __name__ == "__main__":
    main()