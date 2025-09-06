#!/usr/bin/env python3
"""
ASMKL v2: Anchor-Solved Multi-Class Key Lift with guided sampling.
Couples head generation to provably lawful schedules with quality feedback.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import sys

# Add pipeline modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.explore.run_family import ExplorePipeline

# K4 ciphertext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Anchor positions
ANCHORS = {
    "EAST": (21, 25),
    "NORTHEAST": (25, 34),
    "BERLINCLOCK": (63, 74)
}

ANCHOR_INDICES = list(range(21, 25)) + list(range(25, 34)) + list(range(63, 74))


class ASMKLv2Generator:
    """Enhanced ASMKL with guided sampling."""
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.pipeline = ExplorePipeline(seed)
    
    def solve_forced_residues(self, family: str, period: int, phase: int) -> List[int]:
        """
        Solve for key residues at anchor positions.
        
        Returns:
            Key with forced residues solved, None for free positions
        """
        key = [None] * period
        
        # Expected plaintext at anchors
        expected = "X" * 21 + "EASTNORTHEAST" + "X" * 29 + "BERLINCLOCK" + "X"
        
        for idx in ANCHOR_INDICES:
            if idx >= len(K4_CIPHERTEXT):
                continue
            
            ct_char = K4_CIPHERTEXT[idx]
            pt_char = expected[idx]
            
            if pt_char == 'X':
                continue
            
            ct_val = ord(ct_char) - ord('A')
            pt_val = ord(pt_char) - ord('A')
            key_pos = (idx + phase) % period
            
            if family == "VIG":
                required = (ct_val - pt_val) % 26
                if required == 0:  # Forbid K=0
                    return None
            elif family == "BF":
                required = (pt_val + ct_val) % 26
            else:  # VB
                required = (pt_val - ct_val) % 26
                if required == 0:
                    return None
            
            # Check for conflicts
            if key[key_pos] is not None and key[key_pos] != required:
                return None
            
            key[key_pos] = required
        
        return key
    
    def guided_sample_free_residues(
        self, 
        key_template: List[int], 
        family: str,
        num_samples: int = 64
    ) -> List[Tuple[List[int], float]]:
        """
        Sample free residues with quality-guided selection.
        
        Returns:
            List of (complete_key, blinded_score) tuples
        """
        candidates = []
        
        for _ in range(num_samples):
            # Copy template
            key = key_template.copy()
            
            # Fill free positions
            for i in range(len(key)):
                if key[i] is None:
                    if family in ["VIG", "VB"]:
                        key[i] = random.randint(1, 25)  # Avoid 0
                    else:
                        key[i] = random.randint(0, 25)
            
            # Decrypt with this key
            plaintext = self.decrypt(K4_CIPHERTEXT, key, family)
            head_text = plaintext[:75]
            
            # Score under blinding
            policy = {"name": "fixed", "window_radius": 0, "typo_budget": 0}
            result = self.pipeline.compute_score_v2(head_text, policy)
            blinded_score = result["score_norm"]
            
            candidates.append((key, blinded_score, head_text))
        
        # Sort by score and return top-k
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        return candidates[:3]  # Keep top 3 per schedule
    
    def decrypt(self, ciphertext: str, key: List[int], family: str) -> str:
        """Decrypt ciphertext with given key."""
        plaintext = []
        
        for i, char in enumerate(ciphertext):
            if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                plaintext.append(char)
                continue
            
            ct_val = ord(char) - ord('A')
            key_val = key[i % len(key)]
            
            if family == "VIG":
                pt_val = (ct_val - key_val) % 26
            elif family == "BF":
                pt_val = (key_val - ct_val) % 26
            else:  # VB
                pt_val = (ct_val + key_val) % 26
            
            plaintext.append(chr(pt_val + ord('A')))
        
        return ''.join(plaintext)
    
    def generate_heads(
        self,
        num_schedules: int = 200,
        families: List[str] = ["VIG", "BF", "VB"],
        periods: List[int] = None
    ) -> List[Dict]:
        """
        Generate ASMKL v2 heads with guided sampling.
        
        Returns:
            List of generated heads
        """
        if periods is None:
            periods = list(range(10, 23))
        
        heads = []
        schedules_explored = 0
        
        while schedules_explored < num_schedules and len(heads) < 100:
            schedules_explored += 1
            
            # Sample schedule parameters
            family = random.choice(families)
            period = random.choice(periods)
            phase = random.randint(0, period - 1)
            
            # Solve forced residues
            key_template = self.solve_forced_residues(family, period, phase)
            
            if key_template is None:
                continue  # Skip if conflicts
            
            # Guided sampling of free residues
            best_candidates = self.guided_sample_free_residues(
                key_template, family, num_samples=64
            )
            
            # Add best candidates as heads
            for key, score, text in best_candidates:
                heads.append({
                    "label": f"ASMKLv2_{len(heads):03d}",
                    "text": text,
                    "metadata": {
                        "family": family,
                        "period": period,
                        "phase": phase,
                        "key": key,
                        "blinded_score": score,
                        "schedule_id": schedules_explored
                    }
                })
                
                if len(heads) >= 100:
                    break
        
        return heads


def main():
    """Run ASMKL v2 generation."""
    print("="*60)
    print("ASMKL v2 - GUIDED SAMPLING")
    print("="*60)
    
    generator = ASMKLv2Generator(seed=1337)
    
    print("Generating heads with guided sampling...")
    heads = generator.generate_heads(num_schedules=200)
    
    print(f"Generated {len(heads)} heads from 200 schedules")
    
    # Analyze scores
    scores = [h["metadata"]["blinded_score"] for h in heads]
    print(f"Blinded scores: min={min(scores):.4f}, max={max(scores):.4f}, mean={np.mean(scores):.4f}")
    
    # Save output
    output_dir = Path("experiments/pipeline_v2/runs/2025-01-06-explore-diagnostics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "heads_asmkl_v2.json"
    with open(output_file, 'w') as f:
        json.dump({
            "campaign": "ASMKLv2",
            "date": "2025-01-06",
            "description": "ASMKL with guided sampling",
            "seed": 1337,
            "total_heads": len(heads),
            "heads": heads
        }, f, indent=2)
    
    print(f"Saved to {output_file}")
    
    # Score through full pipeline
    print("\nScoring through Explore pipeline...")
    pipeline = ExplorePipeline(seed=1337)
    
    delta_passers = 0
    for head in heads[:20]:  # Test first 20
        policies = [
            {"name": "fixed", "window_radius": 0, "typo_budget": 0},
            {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
            {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
        ]
        
        results = pipeline.run_anchor_modes(head["text"], policies)
        
        if results["pass_deltas"]:
            delta_passers += 1
            print(f"  ✅ {head['label']} passed deltas!")
    
    print(f"\nDelta passers: {delta_passers}/20")
    
    # Create report
    report_file = output_dir / "ASMKL_V2_REPORT.md"
    with open(report_file, 'w') as f:
        f.write("# ASMKL v2 Report\n\n")
        f.write(f"**Schedules explored:** 200\n")
        f.write(f"**Heads generated:** {len(heads)}\n")
        f.write(f"**Guided samples per schedule:** 64\n")
        f.write(f"**Top-k kept:** 3\n\n")
        
        f.write("## Results\n\n")
        f.write(f"- Blinded score range: {min(scores):.4f} to {max(scores):.4f}\n")
        f.write(f"- Mean blinded score: {np.mean(scores):.4f}\n")
        f.write(f"- Delta passers (sample): {delta_passers}/20\n\n")
        
        if delta_passers > 0:
            f.write("## ✅ Some heads passed delta thresholds!\n\n")
            f.write("The guided sampling approach shows promise.\n")
        else:
            f.write("## Result: No delta passers\n\n")
            f.write("Even with guided sampling, the ASMKL approach doesn't beat deltas.\n")
    
    print(f"Report saved to {report_file}")
    
    return heads


if __name__ == "__main__":
    heads = main()