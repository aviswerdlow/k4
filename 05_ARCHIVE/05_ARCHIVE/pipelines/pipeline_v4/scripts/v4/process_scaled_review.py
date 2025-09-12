#!/usr/bin/env python3
"""
Process the first 25 scaled heads through the full Track A pipeline.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directories
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from experiments.pipeline_v4.scripts.v4.saliency_map import SaliencyMapper
from experiments.pipeline_v4.scripts.v4.place_anchors_pareto import ParetoAnchorPlacer
from experiments.pipeline_v4.scripts.v4.neutral_repair import NeutralMoveRepairer
from experiments.pipeline_v4.scripts.v4.run_explore_v4 import ExploreV4Pipeline
from experiments.pipeline_v4.scripts.v4.json_helper import convert_for_json


def process_review_heads():
    """Process review heads through full pipeline."""
    
    # Load the generated heads
    input_file = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled" / "blinded_heads_scaled_review.json"
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    heads = data['heads']
    print(f"Processing {len(heads)} heads through full pipeline...")
    
    # Initialize components
    saliency_mapper = SaliencyMapper(seed=1337)
    anchor_placer = ParetoAnchorPlacer(seed=1337)
    repairer = NeutralMoveRepairer(seed=1337)
    
    processed_heads = []
    
    for i, head_data in enumerate(heads):
        print(f"\n[{i+1}/{len(heads)}] Processing {head_data['label']}...")
        text = head_data['text']
        
        # 1. Compute saliency map
        print("  Computing saliency map...")
        saliency_result = saliency_mapper.compute_saliency(text, n_samples=5)
        
        # 2. Place anchors using Pareto optimization
        print("  Placing anchors with Pareto optimization...")
        anchor_candidates = anchor_placer.generate_placement_candidates(
            text, 
            saliency_result['saliency'],
            window_radii=[0, 2, 3, 4]
        )
        
        # Find Pareto front
        pareto_front = anchor_placer.find_pareto_front(anchor_candidates, epsilon=0.01)
        
        # Select best placement (prefer fixed if within threshold)
        # Sort by total cost and prefer fixed placement if drop is acceptable
        best_placement = None
        for p in pareto_front:
            if p['window_radius'] == 0:  # Fixed placement
                best_placement = p
                break
        if best_placement is None and pareto_front:
            best_placement = pareto_front[0]  # Take lowest total cost
        
        # Apply the placement to get anchored text
        anchored_text = anchor_placer.apply_placement(text, best_placement['placement'])
        
        # Compute actual score drop
        from experiments.pipeline_v4.scripts.v4.gen_blinded_mcmc import BlindedMCMCGenerator
        scorer = BlindedMCMCGenerator(seed=1337)
        anchored_score, _ = scorer.compute_blinded_score(anchored_text)
        best_placement['text'] = anchored_text
        best_placement['blinded_score'] = anchored_score
        best_placement['score_drop'] = head_data['score'] - anchored_score
        best_placement['anchor_mode'] = 'fixed' if best_placement['window_radius'] == 0 else f'windowed_r{best_placement["window_radius"]}'
        best_placement['anchor_positions'] = list(best_placement['placement'].values())
        
        # 3. Apply neutral repair
        print(f"  Repairing (initial drop: {best_placement['score_drop']:.3f})...")
        repaired_text, repaired_score, repair_stats = repairer.hill_climb_repair(
            best_placement['text'],
            max_iterations=200
        )
        
        # Calculate improvement
        improvement = repaired_score - best_placement['blinded_score']
        print(f"  Repair improvement: {improvement:.3f}")
        
        # Store processed head
        processed_head = {
            'label': head_data['label'],
            'original_text': text,
            'original_score': head_data['score'],
            'saliency': saliency_result,
            'anchor_placement': best_placement,
            'repaired_text': repaired_text,
            'repaired_score': repaired_score,
            'repair_stats': repair_stats,
            'repair_improvement': improvement
        }
        processed_heads.append(processed_head)
    
    # Save processed heads
    output_dir = Path(__file__).parent.parent.parent / "runs" / "track_a_scaled"
    output_file = output_dir / "processed_heads_review.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'track': 'A1_SCALED_REVIEW',
            'n_heads': len(processed_heads),
            'heads': convert_for_json(processed_heads)
        }, f, indent=2)
    
    print(f"\nSaved {len(processed_heads)} processed heads to {output_file}")
    
    # Now run Explore scoring
    print("\n" + "="*60)
    print("Running Explore scoring pipeline...")
    
    pipeline = ExploreV4Pipeline(seed=1337)
    
    # Prepare repair results for scoring (matching expected format)
    repair_results = []
    for ph in processed_heads:
        repair_results.append({
            'label': ph['label'],
            'repaired_text': ph['repaired_text'],
            'anchor_mode': ph['anchor_placement']['anchor_mode'],
            'anchor_positions': ph['anchor_placement']['anchor_positions'],
            'original_score': ph['original_score'],
            'repaired_score': ph['repaired_score'],
            'repair_improvement': ph['repair_improvement'],
            'repair_stats': ph['repair_stats'],
            'saliency_mean': sum(ph['saliency']['saliency']) / len(ph['saliency']['saliency'])
        })
    
    # Run scoring (this will save EXPLORE_MATRIX.csv)
    results = pipeline.score_repaired_heads(repair_results, output_dir)
    
    print(f"\nExplore scoring complete - results saved to {output_dir / 'EXPLORE_MATRIX.csv'}")
    
    # Select one exemplar for detailed saliency output
    exemplar = processed_heads[0]
    saliency_output = output_dir / "SALIENCY_EXEMPLAR.json"
    
    with open(saliency_output, 'w') as f:
        json.dump({
            'label': exemplar['label'],
            'before_anchors': {
                'text': exemplar['original_text'],
                'S_blind': exemplar['original_score']
            },
            'after_anchors': {
                'text': exemplar['anchor_placement']['text'],
                'S_blind': exemplar['anchor_placement']['blinded_score'],
                'C_drop': exemplar['anchor_placement']['score_drop'],
                'anchor_mode': exemplar['anchor_placement']['anchor_mode'],
                'anchor_positions': exemplar['anchor_placement']['anchor_positions']
            },
            'after_repair': {
                'text': exemplar['repaired_text'],
                'S_blind': exemplar['repaired_score'],
                'improvement': exemplar['repair_improvement']
            },
            'saliency': convert_for_json(exemplar['saliency'])
        }, f, indent=2)
    
    print(f"Saved saliency exemplar to {saliency_output}")
    
    # Check for candidates that might pass deltas
    candidates = [r for r in results if r.get('within_eps_0.10', False)]
    print(f"\n{len(candidates)} heads within ε=0.10 of thresholds")
    
    if candidates:
        print("Candidates found! Would run orbit analysis next...")
    
    return processed_heads, results


if __name__ == "__main__":
    processed_heads, results = process_review_heads()