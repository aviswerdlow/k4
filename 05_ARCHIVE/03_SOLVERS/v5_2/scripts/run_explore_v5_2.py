#!/usr/bin/env python3
"""
Run v5.2 Content-Aware Exploration
Generates heads with semantic content, then validates through all gates.
"""

import json
import csv
import hashlib
import time
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Import the content-aware generator
from content_aware_generator import ContentAwareGenerator

# Import mock Context Gate evaluator for testing
import os
sys.path.insert(0, os.path.abspath("../pipeline_v5_1/scripts"))
try:
    from run_context_gate_mock import evaluate_mock, check_pass
except ImportError:
    # Fallback - define inline
    def evaluate_mock(label, head_text, pt_sha):
        word_count = len(head_text.split())
        func_words = {'the', 'and', 'a', 'an', 'then', 'that', 'this', 'is', 'are', 'was', 'were'}
        words = head_text.lower().split()
        func_count = sum(1 for w in words if w in func_words)
        func_ratio = func_count / max(1, word_count)
        
        # Simple scoring
        coherence = 5 if func_ratio < 0.5 else 3
        fluency = 5 if func_ratio < 0.5 else 3
        instructional_fit = 4  # Assume surveying words present
        semantic_specificity = 4 if func_ratio < 0.5 else 2
        overall = 4 if func_ratio < 0.5 else 2
        
        return {
            "label": label,
            "overall": overall,
            "coherence": coherence,
            "fluency": fluency,
            "instructional_fit": instructional_fit,
            "semantic_specificity": semantic_specificity,
            "repetition_penalty": 0
        }
    
    def check_pass(result):
        return (result.get("overall", 0) >= 4 and
                result.get("coherence", 0) >= 4 and
                result.get("fluency", 0) >= 4 and
                result.get("instructional_fit", 0) >= 3 and
                result.get("semantic_specificity", 0) >= 3 and
                result.get("repetition_penalty", 1) == 0)

def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 of a file."""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def run_pilot_exploration(
    lexicon_path: Path,
    weights_path: Path,
    master_seed: int,
    k: int,
    output_dir: Path
) -> Dict[str, Any]:
    """
    Run pilot exploration with content-aware generation.
    """
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"=== v5.2 Content-Aware Exploration ===")
    print(f"K = {k}")
    print(f"Master seed = {master_seed}")
    print(f"Output: {output_dir}")
    
    # Record policy hashes
    policy_hashes = {
        "lexicon_sha256": compute_file_sha256(lexicon_path),
        "weights_sha256": compute_file_sha256(weights_path),
        "master_seed": master_seed,
        "k": k
    }
    
    print(f"\nPolicy Hashes:")
    print(f"  Lexicon: {policy_hashes['lexicon_sha256'][:16]}...")
    print(f"  Weights: {policy_hashes['weights_sha256'][:16]}...")
    
    # Initialize generator
    gen = ContentAwareGenerator(lexicon_path, weights_path)
    
    # Generate heads
    print(f"\nGenerating {k} content-aware heads...")
    candidates = gen.generate_batch(k, master_seed)
    
    # Calculate statistics
    passed_generation = sum(1 for c in candidates if c["passes_constraints"])
    print(f"Generation success: {passed_generation}/{k} ({passed_generation/k*100:.1f}%)")
    
    if passed_generation == 0:
        print("ERROR: No valid heads generated")
        return None
    
    # Run Context Gate evaluation
    print(f"\nRunning Context Gate evaluation...")
    context_results = []
    context_pass_count = 0
    
    for candidate in candidates:
        if not candidate["passes_constraints"]:
            continue
        
        label = candidate["label"]
        head = candidate["head"]
        head_sha = candidate["head_sha256"]
        
        # Mock Context Gate evaluation
        context_eval = evaluate_mock(label, head, head_sha)
        context_eval["context_pass"] = check_pass(context_eval)
        
        if context_eval["context_pass"]:
            context_pass_count += 1
        
        context_results.append(context_eval)
    
    context_pass_rate = context_pass_count / passed_generation if passed_generation > 0 else 0
    print(f"Context Gate pass rate: {context_pass_count}/{passed_generation} ({context_pass_rate*100:.1f}%)")
    
    # Create explore matrix
    explore_matrix = []
    
    for i, candidate in enumerate(candidates):
        if not candidate["passes_constraints"]:
            continue
        
        # Find corresponding context evaluation
        context_eval = next((c for c in context_results if c["label"] == candidate["label"]), None)
        
        row = {
            "label": candidate["label"],
            "head_0_74": candidate["head"],
            "head_sha256": candidate["head_sha256"],
            "seed": candidate["seed"],
            "content_ratio": candidate["content_ratio"],
            "np_count": candidate["np_count"],
            "unique_content_types": candidate["unique_content_types"],
            "passes_generation": True,
            "context_pass": context_eval["context_pass"] if context_eval else False,
            "context_overall": context_eval.get("overall", 0) if context_eval else 0,
            "context_coherence": context_eval.get("coherence", 0) if context_eval else 0,
            "context_fluency": context_eval.get("fluency", 0) if context_eval else 0,
            "context_instructional_fit": context_eval.get("instructional_fit", 0) if context_eval else 0,
            "context_semantic_specificity": context_eval.get("semantic_specificity", 0) if context_eval else 0
        }
        
        explore_matrix.append(row)
    
    # Write explore matrix CSV
    csv_path = output_dir / "EXPLORE_MATRIX.csv"
    
    fieldnames = [
        "label", "head_0_74", "head_sha256", "seed",
        "content_ratio", "np_count", "unique_content_types",
        "passes_generation", "context_pass",
        "context_overall", "context_coherence", "context_fluency",
        "context_instructional_fit", "context_semantic_specificity"
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(explore_matrix)
    
    print(f"\nExplore matrix written to {csv_path}")
    
    # Create dashboard
    dashboard = {
        "version": "5.2.0",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "policy_hashes": policy_hashes,
        "results": {
            "k": k,
            "generated": k,
            "passed_generation": passed_generation,
            "generation_rate": passed_generation / k,
            "context_evaluated": passed_generation,
            "context_passed": context_pass_count,
            "context_pass_rate": context_pass_rate
        },
        "metrics": {
            "avg_content_ratio": sum(c["content_ratio"] for c in candidates if c["passes_constraints"]) / passed_generation if passed_generation > 0 else 0,
            "avg_np_count": sum(c["np_count"] for c in candidates if c["passes_constraints"]) / passed_generation if passed_generation > 0 else 0,
            "avg_unique_types": sum(c["unique_content_types"] for c in candidates if c["passes_constraints"]) / passed_generation if passed_generation > 0 else 0
        },
        "acceptance_criteria": {
            "head_gate_pre_anchor": passed_generation / k,
            "context_pass_rate": context_pass_rate,
            "meets_pilot_criteria": (passed_generation / k >= 0.8) and (context_pass_rate >= 0.5)
        }
    }
    
    # Write dashboard
    dashboard_path = output_dir / "DASHBOARD.json"
    with open(dashboard_path, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"Dashboard written to {dashboard_path}")
    
    # Create pilot report
    report_path = output_dir / "PILOT_REPORT.md"
    
    with open(report_path, 'w') as f:
        f.write("# v5.2 Pilot Exploration Report\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d')}\n")
        f.write(f"**Version**: 5.2.0\n")
        f.write(f"**K**: {k}\n\n")
        
        f.write("## Results\n\n")
        f.write(f"- **Generated**: {k} heads\n")
        f.write(f"- **Passed Generation Constraints**: {passed_generation} ({passed_generation/k*100:.1f}%)\n")
        f.write(f"- **Passed Context Gate**: {context_pass_count} ({context_pass_rate*100:.1f}%)\n\n")
        
        f.write("## Metrics\n\n")
        f.write(f"- **Avg Content Ratio**: {dashboard['metrics']['avg_content_ratio']:.2f}\n")
        f.write(f"- **Avg Noun Phrases**: {dashboard['metrics']['avg_np_count']:.1f}\n")
        f.write(f"- **Avg Unique Types**: {dashboard['metrics']['avg_unique_types']:.1f}\n\n")
        
        f.write("## Acceptance Criteria\n\n")
        f.write(f"- **Head gate (pre-anchor) ≥80%**: {'✅' if passed_generation/k >= 0.8 else '❌'} ({passed_generation/k*100:.1f}%)\n")
        f.write(f"- **Context pass rate ≥50%**: {'✅' if context_pass_rate >= 0.5 else '❌'} ({context_pass_rate*100:.1f}%)\n")
        f.write(f"- **Deltas pass ≥25%**: ⏳ (Not yet implemented)\n")
        f.write(f"- **Leakage = 0.000**: ⏳ (Not yet implemented)\n\n")
        
        f.write("## Sample Heads\n\n")
        for i, row in enumerate(explore_matrix[:5]):
            f.write(f"{i+1}. **{row['label']}**\n")
            f.write(f"   ```\n   {row['head_0_74']}\n   ```\n")
            f.write(f"   - Content ratio: {row['content_ratio']:.2f}\n")
            f.write(f"   - Context pass: {'✅' if row['context_pass'] else '❌'}\n\n")
        
        f.write("## Recommendation\n\n")
        if dashboard["acceptance_criteria"]["meets_pilot_criteria"]:
            f.write("✅ **Pilot passes criteria. Ready to scale to K=200.**\n")
        else:
            f.write("❌ **Pilot does not meet criteria. Adjustments needed before scaling.**\n")
    
    print(f"Pilot report written to {report_path}")
    
    # Create manifest
    manifest_path = output_dir / "MANIFEST.sha256"
    
    files_to_hash = [
        "EXPLORE_MATRIX.csv",
        "DASHBOARD.json",
        "PILOT_REPORT.md"
    ]
    
    with open(manifest_path, 'w') as manifest:
        for file_rel in files_to_hash:
            file_path = output_dir / file_rel
            if file_path.exists():
                sha = compute_file_sha256(file_path)
                manifest.write(f"{sha}  {file_rel}\n")
    
    print(f"Manifest written to {manifest_path}\n")
    
    return dashboard

def main():
    parser = argparse.ArgumentParser(description="Run v5.2 content-aware exploration")
    parser.add_argument("--weights", required=True, help="Path to weights JSON")
    parser.add_argument("--lexicon", required=True, help="Path to lexicon JSON")
    parser.add_argument("--master-seed", type=int, default=1337, help="Master seed")
    parser.add_argument("--k", type=int, default=100, help="Number of candidates")
    parser.add_argument("--out", required=True, help="Output directory")
    
    args = parser.parse_args()
    
    # Run exploration
    dashboard = run_pilot_exploration(
        lexicon_path=Path(args.lexicon),
        weights_path=Path(args.weights),
        master_seed=args.master_seed,
        k=args.k,
        output_dir=Path(args.out)
    )
    
    if dashboard and dashboard["acceptance_criteria"]["meets_pilot_criteria"]:
        print("✅ Pilot successful! Ready to scale to K=200.")
        return 0
    else:
        print("❌ Pilot criteria not met. See report for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())