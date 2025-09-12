#!/usr/bin/env python3
"""
Gap Composer for v5.2.2
Selects exact-length gap fillers to meet function word quota (≥8).
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Function words set
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

# Scoring weights
WEIGHTS = {
    "lambda_fw": 1.0,      # Function words (target ≥8)
    "lambda_verbs": 0.8,   # Verbs (target ≥2)
    "lambda_ng": 0.7,      # N-gram score
    "lambda_boundary": -0.3, # Penalty for function words near boundaries
    "lambda_true": 0.5     # Bonus for TRUE keyword
}

@dataclass
class GapFiller:
    """A phrase that fills a gap exactly."""
    text: str
    f_words: List[str]
    f_count: int
    verbs: List[str]
    v_count: int
    length: int
    gap: str

class GapComposer:
    """Composes gap fillers to meet function word quotas."""
    
    def __init__(self, phrasebank_path: Path):
        """Load phrasebank."""
        with open(phrasebank_path, 'r') as f:
            self.phrasebank = json.load(f)
        
        # Filter to only allowed entries
        self.g1_options = [
            entry for entry in self.phrasebank.get("G1_21", [])
            if entry.get("allow", True) and entry["len"] == 21
        ]
        
        self.g2_options = [
            entry for entry in self.phrasebank.get("G2_29", [])
            if entry.get("allow", True) and entry["len"] == 29
        ]
        
        print(f"Loaded {len(self.g1_options)} G1 options, {len(self.g2_options)} G2 options")
    
    def check_boundary_risk(self, g1: Dict, g2: Dict) -> float:
        """Check if function words are near gap boundaries (risky for anchors)."""
        risk = 0.0
        
        # Check G1 end (position 20 - adjacent to EAST at 21)
        g1_words = g1["text"].split()
        if g1_words and g1_words[-1] in FUNCTION_WORDS:
            risk += 1.0  # Last word of G1 is function word
        
        # Check G2 start (position 34 - adjacent to NORTHEAST at 33)
        g2_words = g2["text"].split()
        if g2_words and g2_words[0] in FUNCTION_WORDS:
            risk += 1.0  # First word of G2 is function word
        
        # Check G2 end (position 62 - adjacent to BERLINCLOCK at 63)
        if g2_words and g2_words[-1] in FUNCTION_WORDS:
            risk += 1.0  # Last word of G2 is function word
        
        return risk
    
    def score_combination(self, g1: Dict, g2: Dict) -> float:
        """Score a combination of G1 and G2 fillers."""
        
        # Total function words
        total_f = g1["f_count"] + g2["f_count"]
        
        # Total verbs
        total_v = g1["v_count"] + g2["v_count"]
        
        # Mock n-gram score
        ngram_score = 0.7 + random.random() * 0.3
        
        # Boundary risk
        boundary_risk = self.check_boundary_risk(g1, g2)
        
        # Check for TRUE keyword
        has_true = "TRUE" in g1["text"] or "TRUE" in g2["text"]
        
        # Calculate score
        score = (
            WEIGHTS["lambda_fw"] * total_f +
            WEIGHTS["lambda_verbs"] * total_v +
            WEIGHTS["lambda_ng"] * ngram_score +
            WEIGHTS["lambda_boundary"] * boundary_risk +
            WEIGHTS["lambda_true"] * (1.0 if has_true else 0.0)
        )
        
        return score
    
    def select_best_combination(self, seed: int, beam_size: int = 10) -> Tuple[Dict, Dict, Dict]:
        """
        Select best combination of G1 and G2 using beam search.
        
        Returns: (g1, g2, metrics)
        """
        random.seed(seed)
        
        # Sample candidates
        if len(self.g1_options) > beam_size:
            g1_candidates = random.sample(self.g1_options, beam_size)
        else:
            g1_candidates = self.g1_options
        
        if len(self.g2_options) > beam_size:
            g2_candidates = random.sample(self.g2_options, beam_size)
        else:
            g2_candidates = self.g2_options
        
        # Find best combination
        best_score = -float('inf')
        best_g1 = None
        best_g2 = None
        best_metrics = None
        
        for g1 in g1_candidates:
            for g2 in g2_candidates:
                # Check hard constraints
                total_f = g1["f_count"] + g2["f_count"]
                total_v = g1["v_count"] + g2["v_count"]
                
                # Must meet minimum requirements
                if total_f < 8 or total_v < 2:
                    continue
                
                # Score combination
                score = self.score_combination(g1, g2)
                
                if score > best_score:
                    best_score = score
                    best_g1 = g1
                    best_g2 = g2
                    best_metrics = {
                        "total_f_words": total_f,
                        "total_verbs": total_v,
                        "score": score,
                        "has_true": "TRUE" in g1["text"] or "TRUE" in g2["text"]
                    }
        
        # Fallback if no combination meets requirements
        if best_g1 is None:
            # Select highest function word options
            best_g1 = max(g1_candidates, key=lambda x: x["f_count"])
            best_g2 = max(g2_candidates, key=lambda x: x["f_count"])
            
            total_f = best_g1["f_count"] + best_g2["f_count"]
            total_v = best_g1["v_count"] + best_g2["v_count"]
            
            best_metrics = {
                "total_f_words": total_f,
                "total_verbs": total_v,
                "score": 0.0,
                "has_true": "TRUE" in best_g1["text"] or "TRUE" in best_g2["text"],
                "fallback": True
            }
        
        return best_g1, best_g2, best_metrics
    
    def compose_layout(self, label: str, seed: int) -> Dict:
        """
        Compose a complete layout for a head.
        
        Returns layout with G1, G2, metrics, and anchor positions.
        """
        
        # Select best combination
        g1, g2, metrics = self.select_best_combination(seed)
        
        # Create layout
        layout = {
            "label": label,
            "seed": seed,
            "gaps": {
                "G1": {"start": 0, "end": 20, "text": g1["text"], "f_count": g1["f_count"], "v_count": g1["v_count"]},
                "G2": {"start": 34, "end": 62, "text": g2["text"], "f_count": g2["f_count"], "v_count": g2["v_count"]}
            },
            "anchors": {
                "EAST": [21, 24],
                "NORTHEAST": [25, 33],
                "BERLINCLOCK": [63, 73]
            },
            "metrics": metrics,
            "meets_requirements": metrics["total_f_words"] >= 8 and metrics["total_verbs"] >= 2
        }
        
        return layout

def test_composer():
    """Test the gap composer."""
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    phrasebank_path = base_dir / "policies" / "phrasebank.gaps.json"
    
    if not phrasebank_path.exists():
        print(f"Phrasebank not found at {phrasebank_path}")
        return
    
    composer = GapComposer(phrasebank_path)
    
    print("\nGap Composer Test")
    print("=" * 80)
    
    # Test multiple seeds
    for i in range(5):
        label = f"HEAD_{i+1:03d}_v522"
        seed = 1337 + i * 1000
        
        layout = composer.compose_layout(label, seed)
        
        print(f"\n{label}:")
        print(f"G1: {layout['gaps']['G1']['text']} (f={layout['gaps']['G1']['f_count']}, v={layout['gaps']['G1']['v_count']})")
        print(f"G2: {layout['gaps']['G2']['text']} (f={layout['gaps']['G2']['f_count']}, v={layout['gaps']['G2']['v_count']})")
        print(f"Total: f_words={layout['metrics']['total_f_words']}, verbs={layout['metrics']['total_verbs']}")
        print(f"Meets requirements: {layout['meets_requirements']}")
        print(f"Has TRUE: {layout['metrics']['has_true']}")
    
    print("\n" + "=" * 80)
    print("Composer test complete.")

if __name__ == "__main__":
    test_composer()