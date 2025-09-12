#!/usr/bin/env python3
"""
POS Sweep to Unique Winner - Find exact POS threshold for uniqueness
Incrementally raise POS threshold until exactly one AND+nulls passer remains
"""

import json
import os
from pathlib import Path
from faraday_and_search import phase_1_generic_screening, phase_2_and_confirmation

def pos_sweep_to_unique():
    """
    Sweep POS thresholds from 0.61 to 0.80 until exactly one publishable candidate remains.
    Returns (unique_threshold, unique_candidate, results).
    """
    print("POS Sweep to Unique Winner")
    print("=" * 50)
    
    # POS thresholds to try (start just above current 0.60)
    pos_thresholds = [0.61, 0.62, 0.65, 0.70, 0.75, 0.80]
    
    for pos_threshold in pos_thresholds:
        print(f"\nTesting POS threshold: {pos_threshold}")
        print("-" * 30)
        
        # Phase 1: Generic screening with new POS threshold
        phase1_results, passers = phase_1_generic_screening(
            percentile_top=1,  # Keep tight perplexity ≤1%
            pos_threshold_override=pos_threshold
        )
        
        print(f"  Generic passers: {len(passers)}")
        
        if len(passers) == 0:
            print(f"  No passers at POS ≥ {pos_threshold} - threshold too strict")
            continue
            
        # Phase 2: AND confirmation + nulls
        phase2_results = phase_2_and_confirmation(
            passers,
            percentile_top=1,
            pos_threshold_override=pos_threshold
        )
        
        # Count publishable candidates
        publishable_candidates = []
        for label, result in phase2_results.items():
            if result.get("publishable", False):
                publishable_candidates.append((label, result))
        
        print(f"  Publishable candidates: {len(publishable_candidates)}")
        
        if len(publishable_candidates) == 1:
            unique_label, unique_result = publishable_candidates[0]
            print(f"  🎯 UNIQUE WINNER FOUND: {unique_label}")
            print(f"  POS threshold for uniqueness: {pos_threshold}")
            
            return pos_threshold, unique_label, phase2_results
            
        elif len(publishable_candidates) > 1:
            print(f"  Multiple publishable: {[c[0] for c in publishable_candidates]}")
            # Continue to next threshold
            
        else:
            print(f"  No publishable candidates at POS ≥ {pos_threshold}")
            # Continue to next threshold
    
    print(f"\n❌ No unique winner found in POS range {pos_thresholds}")
    return None, None, {}

def update_summary_for_unique(pos_threshold, unique_label, phase2_results):
    """Update uniqueness_confirm_summary.json for the unique winner."""
    
    # Build updated summary
    summary = {
        "model_class": {
            "routes": "NA-only SPOKE/GRID/RAILFENCE/HALF/IDENTITY",
            "classings": ["c6a", "c6b"],
            "families": ["vigenere", "variant_beaufort", "beaufort"],
            "periods": [10, 22],
            "phases": "0..L-1",
            "option_A": True
        },
        "phrase_gate_policy": {
            "combine": "AND",
            "tokenization_v2": True,
            "generic": {
                "percentile_top": 1,
                "pos_threshold": pos_threshold,  # Updated threshold
                "min_content_words": 6,
                "max_repeat": 2
            }
        },
        "candidates": []
    }
    
    # Add all processed candidates (including non-publishable)
    for label, result in phase2_results.items():
        cand_summary = {
            "label": label,
            "pt_sha256": result["pt_sha256"],
            "route_id": result.get("route_id", "UNKNOWN"),
            "feasible": result["feasible"],
            "near_gate": result["near_gate_passed"],
            "phrase_gate": {
                "tracks": result["phrase_gate_tracks"],
                "pass": result["phrase_gate_passed"]
            }
        }
        
        if result.get("holm_results"):
            cand_summary["holm_adj_p"] = {
                "coverage": result["holm_results"]["p_cov_holm"],
                "f_words": result["holm_results"]["p_fw_holm"]
            }
            cand_summary["publishable"] = result["publishable"]
        else:
            cand_summary["holm_adj_p"] = {"coverage": None, "f_words": None}
            cand_summary["publishable"] = False
        
        summary["candidates"].append(cand_summary)
    
    # Set uniqueness verdict
    publishable_count = sum(1 for c in summary["candidates"] if c["publishable"])
    
    if publishable_count == 1:
        summary["uniqueness"] = {
            "unique": True,
            "reason": f"unique_under_AND_POS_{pos_threshold}",
            "winner": unique_label
        }
    else:
        summary["uniqueness"] = {
            "unique": False,
            "reason": f"unexpected_count_{publishable_count}_at_POS_{pos_threshold}"
        }
    
    # Write updated summary
    summary_path = "uniq_prescreen/uniq_sweep/uniqueness_confirm_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nUpdated summary written to: {summary_path}")
    return summary

def main():
    """Execute POS sweep to find unique winner."""
    
    pos_threshold, unique_label, phase2_results = pos_sweep_to_unique()
    
    if unique_label:
        print(f"\n🎉 SUCCESS: Unique winner found!")
        print(f"   Winner: {unique_label}")
        print(f"   POS threshold: {pos_threshold}")
        
        # Update summary
        summary = update_summary_for_unique(pos_threshold, unique_label, phase2_results)
        
        # Show final result
        winner_result = phase2_results[unique_label]
        print(f"\n📊 Winner Details:")
        print(f"   Route: {winner_result.get('route_id')}")
        print(f"   Phrase gate tracks: {winner_result['phrase_gate_tracks']}")
        print(f"   Holm p-values: coverage={winner_result['holm_results']['p_cov_holm']:.6f}, "
              f"f_words={winner_result['holm_results']['p_fw_holm']:.6f}")
        print(f"   Publishable: {winner_result['publishable']}")
        
        return unique_label, pos_threshold
    else:
        print(f"\n❌ No unique winner found in sweep range")
        print(f"   Consider wider POS range or different approach")
        return None, None

if __name__ == "__main__":
    main()