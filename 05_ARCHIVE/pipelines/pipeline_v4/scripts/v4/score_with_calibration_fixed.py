#!/usr/bin/env python3
"""
Fixed scoring pipeline with proper blinding and no leakage.
"""

import json
import csv
import sys
import random
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v4.scripts.v4.gen_blinded_mcmc import BlindedMCMCGenerator
from experiments.pipeline_v4.scripts.v4.scoring_preprocess import ScoringPreprocessor


class CalibratedScorerFixed:
    """
    Fixed scorer with proper blinding to prevent leakage.
    """
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Initialize components
        self.blinded_scorer = BlindedMCMCGenerator(seed)
        self.preprocessor = ScoringPreprocessor()
        
        # Load calibration from lockbox
        self.calibration = self.load_calibration()
    
    def load_calibration(self) -> Dict:
        """Load calibration stats from lockbox."""
        calibration_path = Path(__file__).parent.parent.parent / "lockbox" / "baseline_v4.json"
        
        if not calibration_path.exists():
            raise FileNotFoundError(f"Calibration not found at {calibration_path}")
        
        with open(calibration_path, 'r') as f:
            return json.load(f)
    
    def apply_anchors_deterministic(self, text: str, policy: str, window_radius: int = 0) -> str:
        """
        Apply anchors to text according to policy.
        IMPORTANT: This happens BEFORE blinding for scoring.
        """
        if len(text) != 75:
            text = (text + "X" * 75)[:75]
        
        text_list = list(text)
        
        if policy == "fixed" or window_radius == 0:
            # Fixed placement - deterministic positions
            text_list[21:25] = "EAST"
            text_list[25:34] = "NORTHEAST"
            text_list[63:74] = "BERLINCLOCK"
        elif policy == "shuffled" or window_radius >= 100:
            # Shuffled - use seed for deterministic random placement
            rng = random.Random(self.seed + window_radius)
            positions = sorted(rng.sample(range(60), 3))
            text_list[positions[0]:positions[0]+4] = "EAST"
            text_list[positions[1]:positions[1]+9] = "NORTHEAST"  
            text_list[positions[2]:positions[2]+11] = "BERLINCLOCK"
        else:
            # Windowed placement - deterministic offsets based on seed
            rng = random.Random(self.seed + window_radius)
            offset1 = rng.randint(-window_radius, window_radius)
            offset2 = rng.randint(-window_radius, window_radius)
            offset3 = rng.randint(-window_radius, window_radius)
            
            pos1 = max(0, min(71, 21 + offset1))
            pos2 = max(pos1 + 4, min(66, 25 + offset2))
            pos3 = max(pos2 + 9, min(64, 63 + offset3))
            
            text_list[pos1:pos1+4] = "EAST"
            text_list[pos2:pos2+9] = "NORTHEAST"
            text_list[pos3:pos3+11] = "BERLINCLOCK"
        
        return ''.join(text_list[:75])
    
    def score_with_blinding(self, text: str) -> float:
        """
        Score text with proper blinding using preprocessor.
        This ensures consistent blinding across all scoring.
        """
        # Apply blinding using the preprocessor
        blinded = self.preprocessor.preprocess_for_scoring(
            text, 
            mask_anchors=True,  # Always mask anchors for language scoring
            mask_narrative=True  # Always mask narrative for language scoring
        )
        
        # Score the blinded text
        score, _ = self.blinded_scorer.compute_blinded_score(blinded)
        return score
    
    def score_head(self, text: str, label: str = "unknown", ablation_mode: str = "normal") -> Dict:
        """
        Score a single head with all policies and compute deltas.
        
        Args:
            text: Head text (without anchors)
            label: Head label
            ablation_mode: "normal" or "masked" for ablation testing
        """
        policies = [
            ("fixed", 0),
            ("windowed_r2", 2),
            ("windowed_r3", 3),
            ("windowed_r4", 4),
            ("shuffled", 100)
        ]
        
        results = {}
        z_scores = {}
        
        # Score original (no anchors) with blinding
        original_score = self.score_with_blinding(text)
        
        # Score with each policy
        for policy_name, radius in policies:
            # Apply anchors BEFORE blinding
            anchored_text = self.apply_anchors_deterministic(text, policy_name, radius)
            
            # Score with blinding (same function for all)
            score = self.score_with_blinding(anchored_text)
            
            # Get calibration stats
            mu = self.calibration[policy_name]["mu"]
            sigma = self.calibration[policy_name]["sigma"]
            
            # Compute z-score
            z = (score - mu) / max(0.001, sigma)
            
            results[policy_name] = {
                "S_blind": score,
                "z": z,
                "mu": mu,
                "sigma": sigma
            }
            z_scores[policy_name] = z
        
        # Compute deltas (NO CLAMPING!)
        z_fixed = z_scores["fixed"]
        delta_windowed_best = max(
            z_fixed - z_scores["windowed_r2"],
            z_fixed - z_scores["windowed_r3"],
            z_fixed - z_scores["windowed_r4"]
        )
        delta_shuffled = z_fixed - z_scores["shuffled"]
        
        # Check thresholds
        pass_windowed = delta_windowed_best >= 0.05
        pass_shuffled = delta_shuffled >= 0.10
        candidate = pass_windowed and pass_shuffled
        
        return {
            "label": label,
            "original_score": original_score,
            "policies": results,
            "z_scores": z_scores,
            "delta_windowed_best": delta_windowed_best,
            "delta_shuffled": delta_shuffled,
            "pass_windowed": pass_windowed,
            "pass_shuffled": pass_shuffled,
            "candidate": candidate
        }