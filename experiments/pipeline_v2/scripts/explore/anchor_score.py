#!/usr/bin/env python3
"""
Anchor alignment scoring for Explore lane.
Computes position and typo-aware scores BEFORE blinding.
"""

from typing import Dict, List, Tuple, Optional


def hamming_distance(s1: str, s2: str) -> int:
    """Compute Hamming distance between two strings of equal length."""
    if len(s1) != len(s2):
        return len(s1)  # Max penalty if lengths differ
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def score_anchors(head_letters: str, policy: Dict) -> Dict:
    """
    Score anchor alignment for a head based on policy mode.
    
    Args:
        head_letters: Uppercase A-Z string for indices 0..74 (head only)
        policy: Dict with anchor_scoring.{mode, anchors, flexibility, weights}
    
    Returns:
        Dict with:
        {
            "anchor_score": float,    # normalized to [0, 1]
            "per_anchor": [
                {"token": "EAST", "expected": 21, "found": 21, 
                 "offset": 0, "typos": 0, "hit": True, "contrib": ...},
                ...
            ]
        }
    """
    # Extract config
    anchor_config = policy.get("anchor_scoring", {})
    mode = anchor_config.get("mode", "fixed")
    anchors = anchor_config.get("anchors", [])
    flexibility = anchor_config.get("flexibility", {})
    r = flexibility.get("r", 0)
    typo_budget = flexibility.get("typo_budget", 0)
    weights = anchor_config.get("weights", {})
    
    # Weight parameters
    lambda_pos = weights.get("lambda_pos", 1.0)
    lambda_typo = weights.get("lambda_typo", 1.0)
    
    # Process each anchor
    per_anchor = []
    anchor_scores = []
    
    for anchor_def in anchors:
        token = anchor_def["token"]
        expected_start = anchor_def["start"]
        token_len = len(token)
        
        # Initialize result for this anchor
        result = {
            "token": token,
            "expected": expected_start,
            "found": None,
            "offset": None,
            "typos": None,
            "hit": False,
            "contrib": 0.0
        }
        
        if mode == "fixed":
            # Fixed mode: exact position only
            if expected_start + token_len <= len(head_letters):
                observed = head_letters[expected_start:expected_start + token_len]
                if observed == token:
                    result["hit"] = True
                    result["found"] = expected_start
                    result["offset"] = 0
                    result["typos"] = 0
                    result["contrib"] = 1.0
                else:
                    # Check typos even in fixed mode
                    typos = hamming_distance(observed, token)
                    if typos <= typo_budget:
                        result["hit"] = True
                        result["found"] = expected_start
                        result["offset"] = 0
                        result["typos"] = typos
                        result["contrib"] = max(0.0, 1.0 - lambda_typo * (typos / max(1, typo_budget)))
        
        elif mode == "windowed":
            # Windowed mode: search within [s-r, s+r]
            best_k = None
            best_typos = token_len + 1  # Worse than any possible match
            best_score = -1.0
            
            # Search window
            k_min = max(0, expected_start - r)
            k_max = min(len(head_letters) - token_len, expected_start + r)
            
            for k in range(k_min, k_max + 1):
                observed = head_letters[k:k + token_len]
                typos = hamming_distance(observed, token)
                
                if typos <= typo_budget:
                    # Calculate score for this position
                    offset = abs(k - expected_start)
                    score = 1.0
                    if r > 0:
                        score -= lambda_pos * (offset / r)
                    if typo_budget > 0:
                        score -= lambda_typo * (typos / typo_budget)
                    score = max(0.0, min(1.0, score))
                    
                    # Keep best match (minimize offset first, then typos)
                    if score > best_score:
                        best_k = k
                        best_typos = typos
                        best_score = score
            
            if best_k is not None:
                result["hit"] = True
                result["found"] = best_k
                result["offset"] = abs(best_k - expected_start)
                result["typos"] = best_typos
                result["contrib"] = best_score
        
        elif mode == "shuffled":
            # Shuffled mode: always miss (control)
            result["hit"] = False
            result["contrib"] = 0.0
        
        per_anchor.append(result)
        anchor_scores.append(result["contrib"])
    
    # Aggregate anchor score
    if anchor_scores:
        anchor_score = sum(anchor_scores) / len(anchor_scores)
    else:
        anchor_score = 0.0
    
    return {
        "anchor_score": anchor_score,
        "per_anchor": per_anchor
    }


def combine_scores(
    anchor_result: Dict,
    z_ngram: float,
    z_coverage: float,
    z_compress: float,
    weights: Dict,
    penalties: float = 0.0
) -> float:
    """
    Combine anchor score with z-normalized language scores.
    
    Args:
        anchor_result: Output from score_anchors
        z_ngram: Z-normalized n-gram score
        z_coverage: Z-normalized coverage score
        z_compress: Z-normalized compression score
        weights: Weight dict with w_anchor, w_zngram, w_coverage, w_compress
        penalties: Additional penalties to subtract
    
    Returns:
        Combined Explore score
    """
    w_anchor = weights.get("w_anchor", 0.15)
    w_zngram = weights.get("w_zngram", 0.45)
    w_coverage = weights.get("w_coverage", 0.25)
    w_compress = weights.get("w_compress", 0.15)
    
    # Ensure weights sum to 1.0
    total_w = w_anchor + w_zngram + w_coverage + w_compress
    if total_w > 0:
        w_anchor /= total_w
        w_zngram /= total_w
        w_coverage /= total_w
        w_compress /= total_w
    
    combined = (
        w_anchor * anchor_result["anchor_score"] +
        w_zngram * z_ngram +
        w_coverage * z_coverage +
        w_compress * z_compress -
        penalties
    )
    
    return combined