#!/usr/bin/env python3
"""
Scaled MCMC generator for K=200 heads with duplicate prevention.
Fallback after Confirm feasibility failure.
"""

import json
import random
import hashlib
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v4.scripts.v4.gen_blinded_mcmc_fixed import BlindedMCMCGeneratorFixed


class ScaledMCMCGenerator(BlindedMCMCGeneratorFixed):
    """Scale to K=200 heads using frozen parameters."""
    
    def generate_k200_heads(self) -> List[Dict]:
        """Generate K=200 heads using multiple chains."""
        print("=" * 60)
        print("SCALED GENERATION: K=200 HEADS")
        print("=" * 60)
        print("Fallback initiated after Confirm feasibility failure")
        print("Using frozen parameters from v4 fixed pipeline")
        print(f"  α={self.alpha}, β={self.beta}, γ={self.gamma}")
        print("")
        
        all_heads = []
        seen_hashes = set()
        
        # We need 200 unique heads
        # Run 10 chains with different seeds
        n_chains = 10
        target_per_chain = 25  # Aim for 25 per chain (will get best 200)
        
        print(f"Running {n_chains} chains targeting {target_per_chain} heads each...")
        
        for chain_id in range(n_chains):
            print(f"\n--- Chain {chain_id + 1}/{n_chains} ---")
            
            # Run 4-stage MCMC for this chain
            chain_samples = self.run_mcmc_4stage_fixed(chain_id)
            
            # Add unique samples
            for sample in chain_samples:
                h = hashlib.sha256(sample['text'].encode()).hexdigest()
                if h not in seen_hashes:
                    all_heads.append(sample)
                    seen_hashes.add(h)
            
            print(f"  Chain {chain_id + 1}: {len(chain_samples)} samples, "
                  f"{len(all_heads)} total unique")
            
            # Stop if we have enough
            if len(all_heads) >= 200:
                print(f"\nReached target of 200 unique heads")
                break
        
        # Sort by score and take top 200
        all_heads.sort(key=lambda x: x['score'], reverse=True)
        final_heads = all_heads[:200]
        
        print(f"\n" + "=" * 60)
        print(f"GENERATION COMPLETE")
        print(f"=" * 60)
        print(f"Total unique heads: {len(all_heads)}")
        print(f"Selected top: {len(final_heads)}")
        print(f"Score range: {final_heads[0]['score']:.3f} to {final_heads[-1]['score']:.3f}")
        
        return final_heads


def main():
    """Generate K=200 heads as fallback."""
    print("FALLBACK: SCALING TO K=200")
    print("Reason: Confirm feasibility test failed")
    print("")
    
    generator = ScaledMCMCGenerator(seed=1337)
    
    # Generate 200 heads
    heads = generator.generate_k200_heads()
    
    # Save to new file
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a_k200"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "blinded_heads_k200.json"
    
    # Save with metadata
    output_data = {
        'track': 'A1_BLINDED_MCMC_K200',
        'reason': 'Fallback after Confirm feasibility failure',
        'total_generated': len(heads),
        'config': {
            'n_chains': 10,
            'stages': 4,
            'proposals_per_stage': 15000,
            'alpha': 0.7,
            'beta': 0.3,
            'gamma': 0.15,
            'duplicate_prevention': True,
            'seed': 1337
        },
        'heads': heads
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nSaved {len(heads)} heads to {output_file}")
    
    # Create status file
    status = {
        'status': 'K200_GENERATED',
        'n_heads': len(heads),
        'timestamp': '2024-01-15T14:00:00Z',
        'next_steps': [
            'Score all 200 heads',
            'Apply candidate filter',
            'Run orbit analysis',
            'Execute nulls on survivors',
            'Submit survivors to Confirm'
        ]
    }
    
    status_file = output_dir / "generation_status.json"
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"Status saved to {status_file}")
    print("\nNext: Run scoring pipeline on K=200 heads")
    
    return heads


if __name__ == "__main__":
    heads = main()