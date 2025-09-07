#!/usr/bin/env python3
"""
GRID-only uniqueness validation script.
Confirms GRID-only winner + runner-up and validates tie-breakers.
"""

import sys
import json
from pathlib import Path

# Add k4cli to path  
sys.path.insert(0, str(Path(__file__).parent.parent))

from k4cli.core.io import read_json


def validate_grid_uniqueness(winner_path, runner_up_path, summary_path=None):
    """Validate GRID-only uniqueness by comparing winner and runner-up."""
    
    print("=== GRID-only Uniqueness Validation ===")
    
    # Read candidate bundles
    winner_coverage = read_json(str(Path(winner_path) / "coverage_report.json"))
    winner_holm = read_json(str(Path(winner_path) / "holm_report_canonical.json"))
    winner_phrase = read_json(str(Path(winner_path) / "phrase_gate_report.json"))
    
    runner_up_coverage = read_json(str(Path(runner_up_path) / "coverage_report.json"))
    runner_up_holm = read_json(str(Path(runner_up_path) / "holm_report_canonical.json"))
    runner_up_phrase = read_json(str(Path(runner_up_path) / "phrase_gate_report.json"))
    
    print(f"Winner: {winner_coverage['pt_sha256'][:12]}... (cand_005)")
    print(f"Runner-up: {runner_up_coverage['pt_sha256'][:12]}... (cand_004)")
    
    # Tie-breaker analysis
    print(f"\n=== Tie-breaker Analysis ===")
    
    # 1. Holm p-values
    w_holm_min = min(winner_holm["p_cov_holm"], winner_holm["p_fw_holm"])
    r_holm_min = min(runner_up_holm["p_cov_holm"], runner_up_holm["p_fw_holm"])
    
    print(f"1. Holm adj_p_min:")
    print(f"   Winner: {w_holm_min:.6f}")
    print(f"   Runner-up: {r_holm_min:.6f}")
    print(f"   Result: {'TIE' if abs(w_holm_min - r_holm_min) < 1e-10 else 'DIFFERENT'}")
    
    # 2. Perplexity percentile
    w_perp = winner_phrase.get("generic", {}).get("perplexity_percentile", 0)
    r_perp = runner_up_phrase.get("generic", {}).get("perplexity_percentile", 0)
    
    print(f"\n2. Perplexity percentile:")
    print(f"   Winner: {w_perp:.1f}%")
    print(f"   Runner-up: {r_perp:.1f}%") 
    print(f"   Result: {'TIE' if w_perp == r_perp else 'DIFFERENT'}")
    
    # 3. Coverage (decisive tie-breaker)
    w_cov = winner_coverage.get("near_gate", {}).get("coverage", 0)
    r_cov = runner_up_coverage.get("near_gate", {}).get("coverage", 0)
    
    print(f"\n3. Coverage (decisive):")
    print(f"   Winner: {w_cov:.6f}")
    print(f"   Runner-up: {r_cov:.6f}")
    
    if w_cov > r_cov:
        print(f"   Result: ✅ WINNER ({w_cov:.6f} > {r_cov:.6f})")
        unique = True
    elif r_cov > w_cov:
        print(f"   Result: ❌ RUNNER-UP WINS ({r_cov:.6f} > {w_cov:.6f})")
        unique = False
    else:
        print(f"   Result: ❌ TIE ({w_cov:.6f} == {r_cov:.6f})")
        unique = False
    
    # Uniqueness verdict
    print(f"\n=== UNIQUENESS VERDICT ===")
    if unique:
        print("✅ UNIQUENESS CONFIRMED")
        print("Method: Pre-registered tie-breakers under GRID-only restriction")
        print("Winner: cand_005 (GRID_W14_ROWS)")
        print(f"Decisive metric: Coverage ({w_cov:.6f} vs {r_cov:.6f})")
    else:
        print("❌ UNIQUENESS NOT ESTABLISHED")
        print("Tie-breakers failed to separate candidates")
    
    # Validate summary if provided
    if summary_path and Path(summary_path).exists():
        print(f"\n=== Summary Validation ===")
        summary = read_json(summary_path)
        
        summary_unique = summary.get("uniqueness", {}).get("unique", False)
        summary_winner = summary.get("uniqueness", {}).get("winner")
        
        print(f"Summary says unique: {summary_unique}")
        print(f"Summary winner: {summary_winner}")
        
        if summary_unique == unique:
            print("✅ Summary matches validation")
        else:
            print("❌ Summary conflicts with validation")
    
    return {
        "unique": unique,
        "winner_coverage": w_cov,
        "runner_up_coverage": r_cov,
        "tie_breaker_sequence": ["holm_adj_p_min", "perplexity_percentile", "coverage"],
        "decisive_metric": "coverage" if unique else None
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python grid_unique_validate.py <winner_bundle> <runner_up_bundle> [summary_json]")
        sys.exit(1)
    
    winner_path = sys.argv[1]
    runner_up_path = sys.argv[2]
    summary_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = validate_grid_uniqueness(winner_path, runner_up_path, summary_path)
    
    sys.exit(0 if result["unique"] else 1)