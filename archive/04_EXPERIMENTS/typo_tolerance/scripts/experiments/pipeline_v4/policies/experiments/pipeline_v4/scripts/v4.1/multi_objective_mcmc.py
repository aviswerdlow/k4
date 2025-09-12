#!/usr/bin/env python3
"""
Multi-Objective MCMC with Verb-Robust Generation
Loads weights from external JSON for reproducibility
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Optional

class MultiObjectiveMCMC:
    """MCMC generator with externalized weight configuration."""
    
    def __init__(self, weights_path: Optional[str] = None):
        """
        Initialize with weights from JSON file.
        
        Args:
            weights_path: Path to weights JSON file. If None, uses default v4.1.1 weights.
        """
        if weights_path:
            self.weights = self._load_weights(weights_path)
        else:
            # Default to v4.1.1 weights
            default_path = Path(__file__).parent.parent.parent / "policies" / "weights.explore_v4_1_1.json"
            if default_path.exists():
                self.weights = self._load_weights(str(default_path))
            else:
                # Fallback to hardcoded v4.1.1 weights
                self.weights = {
                    "lambda_ng": 1.0,
                    "lambda_fw": 0.8,
                    "lambda_cov": 0.2,
                    "lambda_pattern": 0.8,
                    "lambda_verb": 1.2,
                    "lambda_fw_cap": 0.2,
                    "lambda_fratio": 0.3
                }
        
        # Validate weights
        required_keys = ["lambda_ng", "lambda_fw", "lambda_cov", "lambda_pattern", 
                        "lambda_verb", "lambda_fw_cap", "lambda_fratio"]
        for key in required_keys:
            if key not in self.weights:
                raise ValueError(f"Missing required weight: {key}")
    
    def _load_weights(self, path: str) -> Dict:
        """Load weights from JSON file."""
        with open(path, 'r') as f:
            weights = json.load(f)
        
        # Log the loaded weights for transparency
        print(f"Loaded weights from {path}:")
        for key, value in weights.items():
            print(f"  {key}: {value}")
        
        # Calculate and save SHA-256 for verification
        import hashlib
        with open(path, 'rb') as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
        print(f"Weights SHA-256: {sha256}")
        
        return weights
    
    def compute_objective(self, candidate: str, context: Dict) -> float:
        """
        Compute multi-objective score using loaded weights.
        
        Args:
            candidate: Proposed text
            context: Dictionary with scoring components
        
        Returns:
            Weighted objective score
        """
        # Extract components
        ng_score = context.get("ng_score", 0.0)
        fw_score = context.get("fw_score", 0.0)
        cov_score = context.get("coverage", 0.0)
        pattern_score = context.get("pattern_score", 0.0)
        verb_score = context.get("verb_score", 0.0)
        
        # Apply weights
        objective = (
            self.weights["lambda_ng"] * ng_score +
            self.weights["lambda_fw"] * fw_score +
            self.weights["lambda_cov"] * cov_score +
            self.weights["lambda_pattern"] * pattern_score +
            self.weights["lambda_verb"] * verb_score
        )
        
        # Apply caps if needed
        if fw_score > self.weights["lambda_fw_cap"]:
            objective *= (1.0 - self.weights["lambda_fratio"])
        
        return objective
    
    def get_weights_summary(self) -> str:
        """Return a formatted summary of current weights."""
        lines = ["Current Weight Configuration:"]
        for key, value in sorted(self.weights.items()):
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)


def main():
    """Test weight loading."""
    import sys
    
    if len(sys.argv) > 1:
        weights_path = sys.argv[1]
    else:
        weights_path = None
    
    mcmc = MultiObjectiveMCMC(weights_path)
    print("\n" + mcmc.get_weights_summary())
    
    # Test objective computation
    test_context = {
        "ng_score": 0.7,
        "fw_score": 0.5,
        "coverage": 0.8,
        "pattern_score": 0.6,
        "verb_score": 0.9
    }
    
    score = mcmc.compute_objective("test candidate", test_context)
    print(f"\nTest objective score: {score:.3f}")


if __name__ == "__main__":
    main()