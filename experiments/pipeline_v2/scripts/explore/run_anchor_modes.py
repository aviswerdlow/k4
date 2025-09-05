#!/usr/bin/env python3
"""
Run Explore lane with three anchor modes: fixed, windowed, shuffled.
Implements soft scoring, blinding, and promotion logic.
"""

import json
import hashlib
import random
import gzip
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import sys
import os

# Add parent dirs to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.blind_text import blind_text, is_narrative_heavy

def compute_ngram_score(text: str, ngram_tables: Optional[Dict] = None) -> float:
    """
    Compute n-gram plausibility score.
    Higher score = more plausible text.
    """
    if not text:
        return 0.0
        
    # Simplified n-gram scoring
    score = 0.0
    
    # Bigrams
    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        # Common English bigrams get positive score
        if bigram in ["TH", "HE", "IN", "ER", "AN", "ED", "ND", "TO", "EN", "ES"]:
            score += 0.1
        # Rare bigrams get negative score
        elif bigram in ["QX", "ZX", "XQ", "QZ", "JQ", "QJ"]:
            score -= 0.2
    
    # Trigrams
    for i in range(len(text) - 2):
        trigram = text[i:i+3]
        if trigram in ["THE", "AND", "ING", "HER", "HAT", "HIS", "THA", "ERE", "FOR", "ENT"]:
            score += 0.15
        elif "Q" in trigram and "U" not in trigram:
            score -= 0.1
    
    # Normalize by length
    return score / max(1, len(text))

def compute_coverage_score(text: str, function_words: Optional[Set[str]] = None) -> float:
    """
    Compute coverage score based on function words and lexicon hits.
    """
    if not text:
        return 0.0
    
    # Default function words if not provided
    if function_words is None:
        function_words = {"THE", "AND", "OF", "TO", "A", "IN", "THAT", "IS", "WAS", "HE", 
                         "FOR", "IT", "WITH", "AS", "HIS", "ON", "BE", "AT", "BY", "I"}
    
    words = []
    # Simple word segmentation (would use better algorithm in production)
    for length in [2, 3, 4, 5, 6, 7]:
        for i in range(len(text) - length + 1):
            candidate = text[i:i+length]
            if candidate in function_words:
                words.append(candidate)
    
    # Score based on coverage
    if not words:
        return 0.0
    
    unique_words = set(words)
    coverage = len(unique_words) / len(function_words)
    density = len(words) / max(1, len(text) / 4)  # Expect ~1 function word per 4 chars
    
    return min(1.0, coverage * 0.5 + density * 0.5)

def compute_compress_score(text: str) -> float:
    """
    Compute compressibility score using gzip.
    More compressible = more regular/patterned.
    """
    if not text:
        return 0.0
    
    text_bytes = text.encode('utf-8')
    compressed = gzip.compress(text_bytes)
    
    # Compression ratio
    ratio = len(compressed) / len(text_bytes)
    
    # Lower ratio = more compressible = higher score
    # Map ratio [0.3, 1.0] to score [1.0, 0.0]
    score = max(0.0, min(1.0, (1.0 - ratio) / 0.7))
    
    return score

def check_anchor_match(text: str, anchor_config: Dict, mode: str) -> float:
    """
    Check how well text matches anchor constraints.
    Returns score [0, 1] based on match quality.
    """
    total_score = 0.0
    total_weight = 0.0
    
    for anchor_name, config in anchor_config.get("anchors", {}).items():
        span = config.get("span", [])
        if len(span) != 2:
            continue
            
        start, end = span
        weight = config.get("weight", 0.1)
        total_weight += weight
        
        if mode == "fixed":
            # Exact match required
            if start < len(text) and end <= len(text):
                segment = text[start:end+1]
                # Simple exact match check (would be more sophisticated in production)
                if anchor_name.startswith("MASK_"):
                    # Shuffled control - any text scores
                    total_score += weight
                elif anchor_name in segment:
                    total_score += weight
                    
        elif mode == "windowed":
            # Allow ±1 window
            window = config.get("window", 1)
            found = False
            for offset in range(-window, window + 1):
                s = max(0, start + offset)
                e = min(len(text), end + offset + 1)
                if s < len(text) and e <= len(text):
                    segment = text[s:e]
                    if anchor_name in segment:
                        # Partial credit for windowed match
                        distance_penalty = abs(offset) * 0.2
                        total_score += weight * (1.0 - distance_penalty)
                        found = True
                        break
            
            # Check for typo if not found
            if not found and anchor_config.get("allow_typo", False):
                # Simple edit distance check
                for offset in range(-window, window + 1):
                    s = max(0, start + offset)
                    e = min(len(text), end + offset + 1)
                    if s < len(text) and e <= len(text):
                        segment = text[s:e]
                        # Allow one character difference
                        if len(segment) == len(anchor_name):
                            diffs = sum(1 for a, b in zip(segment, anchor_name) if a != b)
                            if diffs <= 1:
                                total_score += weight * 0.5  # Half credit for typo
                                break
                                
        elif mode == "shuffled":
            # Random control - always scores if text present
            if start < len(text) and end <= len(text):
                total_score += weight
    
    return total_score / max(0.001, total_weight)

def explore_score(text: str, policy: Dict, blinded: bool = True) -> Dict:
    """
    Compute Explore lane score for text under given policy.
    """
    # Blind if requested
    if blinded and policy.get("scorer", {}).get("blind_anchors", True):
        blinded_text, mask_report = blind_text(
            text, 
            blind_anchors=policy.get("scorer", {}).get("blind_anchors", True),
            blind_narrative=policy.get("scorer", {}).get("blind_narrative", True)
        )
    else:
        blinded_text = text
        mask_report = None
    
    # Compute component scores
    ngram_score = compute_ngram_score(blinded_text)
    coverage_score = compute_coverage_score(blinded_text)
    compress_score = compute_compress_score(blinded_text)
    
    # Check anchors (on original text, not blinded)
    anchor_score = check_anchor_match(
        text, 
        policy.get("anchor_config", {}),
        policy.get("mode", "fixed")
    )
    
    # Weighted combination
    weights = policy.get("scorer", {})
    w_ngram = weights.get("ngram_weight", 0.4)
    w_coverage = weights.get("coverage_weight", 0.3)
    w_compress = weights.get("compress_weight", 0.3)
    
    # Anchor score is a soft penalty/bonus, not part of main score
    base_score = (w_ngram * ngram_score + 
                  w_coverage * coverage_score + 
                  w_compress * compress_score)
    
    # Apply anchor adjustment
    final_score = base_score * (1.0 + anchor_score * 0.2)  # ±20% based on anchors
    
    return {
        "final_score": final_score,
        "base_score": base_score,
        "anchor_score": anchor_score,
        "ngram_score": ngram_score,
        "coverage_score": coverage_score,
        "compress_score": compress_score,
        "blinded": blinded,
        "mask_report": mask_report
    }

def run_anchor_modes(candidates: List[Dict], policies: Dict[str, Dict], 
                    output_dir: Path, seed: int = 1337) -> Path:
    """
    Run all three anchor modes and create comparison matrix.
    """
    random.seed(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for candidate in candidates:
        label = candidate.get("label", "unknown")
        text = candidate.get("plaintext", "")
        
        print(f"Processing {label}...")
        
        # Run each mode
        for mode_name, policy in policies.items():
            print(f"  Mode: {mode_name}")
            
            score_result = explore_score(text, policy, blinded=True)
            
            result = {
                "label": label,
                "mode": mode_name,
                "final_score": score_result["final_score"],
                "base_score": score_result["base_score"],
                "anchor_score": score_result["anchor_score"],
                "ngram_score": score_result["ngram_score"],
                "coverage_score": score_result["coverage_score"],
                "compress_score": score_result["compress_score"],
                "narrative_heavy": is_narrative_heavy(text)
            }
            results.append(result)
    
    # Check promotion criteria
    print("\nChecking promotion criteria...")
    promoted = []
    
    # Group by label
    by_label = {}
    for r in results:
        if r["label"] not in by_label:
            by_label[r["label"]] = {}
        by_label[r["label"]][r["mode"]] = r
    
    for label, modes in by_label.items():
        fixed = modes.get("fixed", {})
        windowed = modes.get("windowed", {})
        shuffled = modes.get("shuffled", {})
        
        # Check deltas
        delta_1 = fixed.get("final_score", 0) - windowed.get("final_score", 0)
        delta_2 = fixed.get("final_score", 0) - shuffled.get("final_score", 0)
        
        # Promotion thresholds from policy
        threshold_1 = policies.get("fixed", {}).get("promotion", {}).get("delta_windowed", 0.05)
        threshold_2 = policies.get("fixed", {}).get("promotion", {}).get("delta_shuffled", 0.10)
        
        if delta_1 >= threshold_1 and delta_2 >= threshold_2:
            promoted.append({
                "label": label,
                "fixed_score": fixed.get("final_score", 0),
                "delta_windowed": delta_1,
                "delta_shuffled": delta_2,
                "promoted": True
            })
            print(f"  {label}: PROMOTED (δ₁={delta_1:.3f}, δ₂={delta_2:.3f})")
        else:
            print(f"  {label}: NOT PROMOTED (δ₁={delta_1:.3f}, δ₂={delta_2:.3f})")
    
    # Write results
    csv_path = output_dir / "ANCHOR_MODE_MATRIX.csv"
    with open(csv_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Write promotion queue
    if promoted:
        queue_path = output_dir / "promotion_queue.json"
        with open(queue_path, 'w') as f:
            json.dump(promoted, f, indent=2)
        print(f"\nPromoted {len(promoted)} candidates to {queue_path}")
    
    print(f"\nResults written to {csv_path}")
    return csv_path

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Explore anchor modes")
    parser.add_argument("--candidates", default="experiments/pipeline_v2/data/candidates.json")
    parser.add_argument("--policy_fixed", default="experiments/pipeline_v2/policies/explore/POLICY.anchor_fixed.json")
    parser.add_argument("--policy_windowed", default="experiments/pipeline_v2/policies/explore/POLICY.anchor_windowed.json")
    parser.add_argument("--policy_shuffled", default="experiments/pipeline_v2/policies/explore/POLICY.anchor_shuffled.json")
    parser.add_argument("--output", default="experiments/pipeline_v2/runs/2025-01-05/explore/")
    parser.add_argument("--seed", type=int, default=1337)
    
    args = parser.parse_args()
    
    # Load candidates
    if Path(args.candidates).exists():
        with open(args.candidates) as f:
            candidates = json.load(f)
    else:
        # Create example candidates for testing
        print(f"Creating example candidates file: {args.candidates}")
        candidates = [
            {
                "label": "winner",
                "plaintext": "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
            },
            {
                "label": "test_variant",
                "plaintext": "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
            }
        ]
        Path(args.candidates).parent.mkdir(parents=True, exist_ok=True)
        with open(args.candidates, 'w') as f:
            json.dump(candidates, f, indent=2)
    
    # Load policies
    policies = {}
    for name, path in [("fixed", args.policy_fixed), 
                       ("windowed", args.policy_windowed),
                       ("shuffled", args.policy_shuffled)]:
        with open(path) as f:
            policies[name] = json.load(f)
    
    # Run
    run_anchor_modes(candidates, policies, Path(args.output), args.seed)

if __name__ == "__main__":
    main()