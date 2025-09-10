#!/usr/bin/env python3
"""
F1 Triage & Cross-validation System
Mechanical ranking without semantics
MASTER_SEED = 1337
"""

import os
import sys
import json
import csv
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

# Import the base searcher
from f1_anchor_search_v2 import AnchorSearcherV2, PlacementResult

MASTER_SEED = 1337

# Fixed weight set for mechanical scoring
WEIGHTS = {
    'w1_gains': 1.0,
    'w2_forced_slots': 0.7,
    'w3_uniformity': 0.3,
    'w4_slot_reuse': 1.0,  # Penalty
    'w5_class_skew': 0.5   # Penalty
}

@dataclass
class TriagedResult:
    """Enhanced result with mechanical scoring"""
    placement: PlacementResult
    mechanical_score: float
    uniformity_across_classes: float
    slot_reuse_penalty: int
    class_skew_penalty: float
    passes_hard_filters: bool
    filter_failures: List[str]
    
    # Cross-validation fields
    tableau_conflict: Optional[bool] = None
    L17_conflict: Optional[bool] = None
    L17_unknown_after: Optional[int] = None
    
    # Lightweight English metrics (not for gating)
    function_word_hits: int = 0
    bigram_ic_delta: float = 0.0


class F1Triage:
    """Triage system for F1 anchor search results"""
    
    def __init__(self):
        self.searcher = AnchorSearcherV2()
        self.function_words = {'THE', 'OF', 'AND', 'TO', 'IN', 'BY', 'WE', 'ARE', 'THEN'}
        
    def apply_hard_filters(self, result: PlacementResult) -> Tuple[bool, List[str]]:
        """
        Apply hard filters to a placement result
        Returns (passes, list_of_failures)
        """
        failures = []
        
        # Filter 1: Already preserves anchors (enforced in v2)
        if not result.anchors_preserved:
            failures.append('anchors_not_preserved')
        
        # Filter 2: Add Δforced_slots ≥ 3
        if len(result.forced_slots_added) < 3:
            failures.append(f'insufficient_forced_slots:{len(result.forced_slots_added)}')
        
        # Filter 3: Yield gains ≥ 3
        if result.gains < 3:
            failures.append(f'insufficient_gains:{result.gains}')
        
        # Filter 4: No reuse of same (class,slot) within placement
        seen_slots = set()
        for c, s, _ in result.forced_slots_added:
            key = (c, s)
            if key in seen_slots:
                failures.append(f'slot_reuse:{key}')
            seen_slots.add(key)
        
        return len(failures) == 0, failures
    
    def compute_mechanical_score(self, result: PlacementResult) -> Tuple[float, Dict]:
        """
        Compute mechanical score without semantics
        Returns (score, components)
        """
        # Extract components
        gains = result.gains
        forced_slots = len(result.forced_slots_added)
        
        # Uniformity across classes
        classes_hit = defaultdict(int)
        for c, _, _ in result.forced_slots_added:
            classes_hit[c] += 1
        uniformity = len(classes_hit) / 6.0  # Fraction of classes with ≥1 new slot
        
        # Slot reuse penalty
        slot_counts = defaultdict(int)
        for c, s, _ in result.forced_slots_added:
            slot_counts[(c, s)] += 1
        slot_reuse = sum(count - 1 for count in slot_counts.values() if count > 1)
        
        # Class skew penalty
        if classes_hit:
            max_hits = max(classes_hit.values())
            total_hits = sum(classes_hit.values())
            class_skew = (max_hits / total_hits) if total_hits > 0 else 0
        else:
            class_skew = 0
        
        # Compute score
        score = (WEIGHTS['w1_gains'] * gains +
                WEIGHTS['w2_forced_slots'] * forced_slots +
                WEIGHTS['w3_uniformity'] * uniformity -
                WEIGHTS['w4_slot_reuse'] * slot_reuse -
                WEIGHTS['w5_class_skew'] * class_skew)
        
        components = {
            'gains': gains,
            'forced_slots': forced_slots,
            'uniformity': uniformity,
            'slot_reuse': slot_reuse,
            'class_skew': class_skew
        }
        
        return score, components
    
    def run_l11_triage(self) -> Tuple[List[TriagedResult], Dict]:
        """
        Run full L=11 triage on all candidates
        Returns (triaged_results, statistics)
        """
        print(f"=== Starting L=11 Triage ===")
        print(f"MASTER_SEED: {MASTER_SEED}")
        print(f"Weights: {WEIGHTS}\n")
        
        all_results = []
        stats = {
            'total_tested': 0,
            'passed_filters': 0,
            'filter_reasons': defaultdict(int)
        }
        
        # Test all candidates with L=11
        for candidate_data in self.searcher.candidates:
            token = candidate_data['token']
            
            # Focus on L=11 with all phases
            L = 11
            for phase in range(L):
                for start_idx in range(97 - len(token) + 1):
                    stats['total_tested'] += 1
                    
                    # Test placement
                    result = self.searcher.test_placement(token, start_idx, L, phase)
                    
                    # Skip rejected placements
                    if result.rejected:
                        continue
                    
                    # Apply hard filters
                    passes, failures = self.apply_hard_filters(result)
                    
                    # Track filter statistics
                    if not passes:
                        for reason in failures:
                            stats['filter_reasons'][reason.split(':')[0]] += 1
                    else:
                        stats['passed_filters'] += 1
                    
                    # Compute mechanical score
                    score, components = self.compute_mechanical_score(result)
                    
                    # Create triaged result
                    triaged = TriagedResult(
                        placement=result,
                        mechanical_score=score,
                        uniformity_across_classes=components['uniformity'],
                        slot_reuse_penalty=components['slot_reuse'],
                        class_skew_penalty=components['class_skew'],
                        passes_hard_filters=passes,
                        filter_failures=failures
                    )
                    
                    # Only keep results that pass filters
                    if passes:
                        all_results.append(triaged)
                        
                        # Progress reporting
                        if len(all_results) % 100 == 0:
                            print(f"  Found {len(all_results)} passing candidates...")
        
        print(f"\nTriage complete:")
        print(f"  Total tested: {stats['total_tested']}")
        print(f"  Passed filters: {stats['passed_filters']}")
        print(f"  Filter rejection reasons:")
        for reason, count in sorted(stats['filter_reasons'].items(), key=lambda x: -x[1])[:5]:
            print(f"    {reason}: {count}")
        
        return all_results, stats
    
    def generate_shortlists(self, results: List[TriagedResult]) -> Dict:
        """
        Generate three shortlists based on different criteria
        """
        # Sort by different criteria
        by_score = sorted(results, key=lambda r: -r.mechanical_score)[:100]
        by_gains = sorted(results, key=lambda r: -r.placement.gains)[:50]
        by_forced = sorted(results, key=lambda r: -len(r.placement.forced_slots_added))[:50]
        
        shortlists = {
            'top_100_by_score': by_score,
            'top_50_by_gains': by_gains,
            'top_50_by_forced_slots': by_forced
        }
        
        return shortlists
    
    def save_shortlists(self, shortlists: Dict, output_dir: str = 'triage'):
        """
        Save shortlists to CSV and JSON cards
        """
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f'{output_dir}/cards', exist_ok=True)
        
        # Save each shortlist
        for list_name, results in shortlists.items():
            csv_path = f'{output_dir}/{list_name}.csv'
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'rank', 'token', 'start', 'L', 'phase', 
                    'gains', 'forced_slots', 'score',
                    'uniformity', 'slot_reuse', 'class_skew'
                ])
                
                for rank, triaged in enumerate(results, 1):
                    r = triaged.placement
                    writer.writerow([
                        rank, r.token, r.start_index, r.L, r.phase,
                        r.gains, len(r.forced_slots_added), 
                        f"{triaged.mechanical_score:.2f}",
                        f"{triaged.uniformity_across_classes:.2f}",
                        triaged.slot_reuse_penalty,
                        f"{triaged.class_skew_penalty:.2f}"
                    ])
            
            print(f"  Saved {list_name} to {csv_path}")
            
            # Save top 20 as detailed cards
            for i, triaged in enumerate(results[:20]):
                card = {
                    "mechanism": "F1-triage",
                    "rank": i + 1,
                    "list": list_name,
                    "token": triaged.placement.token,
                    "start_index": triaged.placement.start_index,
                    "L": triaged.placement.L,
                    "phase": triaged.placement.phase,
                    "gains": triaged.placement.gains,
                    "forced_slots_added": [
                        {"class": c, "slot": s, "residue": k}
                        for c, s, k in triaged.placement.forced_slots_added
                    ],
                    "mechanical_score": triaged.mechanical_score,
                    "score_components": {
                        "gains": triaged.placement.gains,
                        "forced_slots": len(triaged.placement.forced_slots_added),
                        "uniformity": triaged.uniformity_across_classes,
                        "slot_reuse": triaged.slot_reuse_penalty,
                        "class_skew": triaged.class_skew_penalty
                    },
                    "weights": WEIGHTS,
                    "sha_ct": triaged.placement.sha_ct,
                    "sha_wheels_before": triaged.placement.sha_forced_wheels_before,
                    "sha_wheels_after": triaged.placement.sha_forced_wheels_after
                }
                
                card_path = f'{output_dir}/cards/{list_name}_{i:03d}.json'
                with open(card_path, 'w') as f:
                    json.dump(card, f, indent=2)
        
        # Save weights manifest
        with open(f'{output_dir}/MANIFEST.json', 'w') as f:
            manifest = {
                "mechanism": "F1-triage",
                "master_seed": MASTER_SEED,
                "weights": WEIGHTS,
                "filter_thresholds": {
                    "min_forced_slots": 3,
                    "min_gains": 3,
                    "allow_slot_reuse": False
                }
            }
            json.dump(manifest, f, indent=2)
        
        print(f"  Saved manifest to {output_dir}/MANIFEST.json")


def main():
    """Main execution"""
    print("=== F1 Triage & Cross-validation ===")
    print(f"Branch: forkF-v2-triage-crosscheck\n")
    
    triage = F1Triage()
    
    # Run L=11 triage
    results, stats = triage.run_l11_triage()
    
    if not results:
        print("\n✗ No candidates passed hard filters!")
        return
    
    # Generate shortlists
    print(f"\n=== Generating Shortlists ===")
    shortlists = triage.generate_shortlists(results)
    
    # Report sizes
    for name, slist in shortlists.items():
        print(f"  {name}: {len(slist)} candidates")
    
    # Save results
    print(f"\n=== Saving Results ===")
    triage.save_shortlists(shortlists)
    
    print("\n✓ Triage complete!")
    print(f"  Total passing filters: {len(results)}")
    print(f"  Shortlists saved to triage/")


if __name__ == "__main__":
    main()