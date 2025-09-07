#!/usr/bin/env python3
"""
Enhanced compute_normalized_score with anchor alignment scoring.
Scores anchors BEFORE blinding, then combines with language scores.
"""

import sys
from pathlib import Path
from typing import Dict, Tuple

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v2.scripts.explore.anchor_score import (
    score_anchors, combine_scores
)
from experiments.pipeline_v2.scripts.explore.blind_text import blind_text
from experiments.pipeline_v2.scripts.explore.run_anchor_modes import (
    compute_ngram_score, compute_coverage_score, compute_compress_score
)


def compute_normalized_score_v2(text: str, policy: Dict, baseline_stats: Dict) -> Dict:
    """
    Compute normalized explore score with anchor alignment.
    
    Process:
    1. Score anchor alignment BEFORE blinding
    2. Blind text (mask anchors/narrative)  
    3. Compute z-normalized language scores
    4. Combine with weights
    
    Args:
        text: Head text to score
        policy: Policy with anchor_scoring config
        baseline_stats: Baseline statistics for z-normalization
        
    Returns:
        Dict with score components and final score
    """
    # Step 1: Score anchors BEFORE blinding
    anchor_result = None
    if "anchor_scoring" in policy:
        anchor_result = score_anchors(text, policy)
    else:
        # Fallback for policies without anchor scoring
        anchor_result = {"anchor_score": 0.0, "per_anchor": []}
    
    # Step 2: Blind text
    if policy.get("scorer", {}).get("blind_anchors", True):
        blinded_text, mask_report = blind_text(
            text,
            blind_anchors=True,
            blind_narrative=policy.get("scorer", {}).get("blind_narrative", True)
        )
    else:
        blinded_text = text
        mask_report = None
    
    # Step 3: Compute raw language scores
    ngram_raw = compute_ngram_score(blinded_text)
    coverage_raw = compute_coverage_score(blinded_text)
    compress_raw = compute_compress_score(blinded_text)
    
    # Step 4: Compute penalties
    penalties = 0.0
    words = []  # Simple word extraction
    for length in [3, 4, 5, 6, 7]:
        for i in range(len(blinded_text) - length + 1):
            word = blinded_text[i:i+length]
            if word not in ["THE", "AND", "OF", "TO", "A"]:  # Non-function words
                words.append(word)
    
    # Repetition penalty
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    for count in word_counts.values():
        if count > 2:
            penalties += 0.1 * (count - 2)
    
    # Step 5: Z-normalize language scores
    if baseline_stats:
        z_ngram = (ngram_raw - baseline_stats["ngram_mean"]) / max(0.001, baseline_stats["ngram_std"])
        z_coverage = (coverage_raw - baseline_stats["coverage_mean"]) / max(0.001, baseline_stats["coverage_std"])
        z_compress = (compress_raw - baseline_stats["compress_mean"]) / max(0.001, baseline_stats["compress_std"])
    else:
        # No normalization if no baseline
        z_ngram = ngram_raw
        z_coverage = coverage_raw
        z_compress = compress_raw
    
    # Step 6: Combine scores
    weights = policy.get("anchor_scoring", {}).get("weights", {})
    if not weights:
        # Fallback weights if not in anchor_scoring
        weights = {
            "w_anchor": 0.0,  # No anchor contribution if not configured
            "w_zngram": 0.45,
            "w_coverage": 0.25,
            "w_compress": 0.30
        }
    
    combined_score = combine_scores(
        anchor_result,
        z_ngram,
        z_coverage,
        z_compress,
        weights,
        penalties
    )
    
    return {
        "score_norm": combined_score,
        "anchor_result": anchor_result,
        "z_ngram": z_ngram,
        "z_coverage": z_coverage,
        "z_compress": z_compress,
        "penalties": penalties,
        "raw_ngram": ngram_raw,
        "raw_coverage": coverage_raw,
        "raw_compress": compress_raw,
        "mask_report": mask_report
    }