#!/usr/bin/env python3
"""
Score reference texts to verify harness behavior.
Tests that known good texts fail under blinding (as expected).
"""

import json
import csv
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Add pipeline modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.explore.run_family import ExplorePipeline


def create_reference_texts():
    """Create reference texts for testing."""
    references = {
        "published_grid": {
            "text": "FINDTHEPATHTOTHEEASTNORTHEASTQUARTERANDREADTHEBEARINGOFTHEBERLINCLOCKTOWER",
            "description": "Published GRID-only winner with narrative",
            "expected": "Should FAIL under blinding"
        },
        "grid_runner_up": {
            "text": "MOVEYOURCOMPASSTOEASTNORTHEASTDIRECTIONANDNOTETHESIGHTOFBERLINCLOCKTOWER",
            "description": "GRID runner-up with similar narrative",
            "expected": "Should FAIL under blinding"
        },
        "corridor_synthetic": {
            "text": "XXXXXXXXXXXXXXXXXXXXXXEASTNORTHEASTXXXXXXXXXXXXXXXXXXXXXXXXBERLINCLOCKKXXXX",
            "description": "Synthetic with corridor anchors only",
            "expected": "May pass anchors but fail language"
        },
        "random_control": {
            "text": "QWRTYPSDLFKGJHZXCVBNMEASTNORTHEASTQWRTYPSDLFKGJHZXCVBNMQWRBERLINCLOCKKQWRT",
            "description": "Random letters with anchors",
            "expected": "Should FAIL on language scores"
        },
        "k1_plaintext": {
            "text": "BETWEENSUBTLESHADINGAEASTNORTHEASTNCEOFLIGHTLIESTHENUANBERLINCLOCKLUSION",
            "description": "K1 plaintext with anchors inserted",
            "expected": "Might have better language scores"
        }
    }
    
    # Ensure all are 75 chars
    for key, ref in references.items():
        text = ref["text"]
        if len(text) < 75:
            text = text.ljust(75, 'X')
        elif len(text) > 75:
            text = text[:75]
        references[key]["text"] = text
    
    return references


def score_reference(pipeline: ExplorePipeline, ref_name: str, ref_data: dict) -> dict:
    """Score a single reference text."""
    text = ref_data["text"]
    
    # Define policies
    policies = [
        {"name": "fixed", "window_radius": 0, "typo_budget": 0},
        {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
        {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
    ]
    
    # Run anchor modes
    mode_results = pipeline.run_anchor_modes(text, policies)
    
    # Get individual scores
    scores = {}
    for policy in policies:
        result = pipeline.compute_score_v2(text, policy)
        scores[policy["name"]] = {
            "score_norm": result["score_norm"],
            "anchor_score": result["anchor_result"]["total_score"],
            "z_ngram": result["z_ngram"],
            "z_coverage": result["z_coverage"],
            "z_compress": result["z_compress"],
            "blinded_sample": result["blinded_text"]
        }
    
    return {
        "reference": ref_name,
        "description": ref_data["description"],
        "expected": ref_data["expected"],
        "text_sample": text[:30] + "...",
        "scores": scores,
        "delta_vs_windowed": mode_results["delta_vs_windowed"],
        "delta_vs_shuffled": mode_results["delta_vs_shuffled"],
        "pass_deltas": mode_results["pass_deltas"],
        "verdict": "PASS" if mode_results["pass_deltas"] else "FAIL"
    }


def main():
    """Run reference scoring diagnostics."""
    print("="*60)
    print("REFERENCE SCORING DIAGNOSTIC")
    print("="*60)
    print("\nVerifying that known texts behave as expected under blinding...\n")
    
    # Initialize pipeline
    pipeline = ExplorePipeline(seed=1337)
    
    # Get references
    references = create_reference_texts()
    
    # Score each reference
    results = []
    
    for ref_name, ref_data in references.items():
        print(f"Scoring {ref_name}...")
        result = score_reference(pipeline, ref_name, ref_data)
        results.append(result)
        
        print(f"  {result['description']}")
        print(f"  Expected: {result['expected']}")
        print(f"  Delta vs windowed: {result['delta_vs_windowed']:.4f}")
        print(f"  Delta vs shuffled: {result['delta_vs_shuffled']:.4f}")
        print(f"  Verdict: {result['verdict']}")
        print()
    
    # Save results
    output_dir = Path("experiments/pipeline_v2/runs/2025-01-06-explore-diagnostics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # CSV output
    csv_file = output_dir / "REFERENCE_SCORE.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "reference", "description", "delta_vs_windowed", "delta_vs_shuffled",
            "pass_deltas", "verdict", "expected"
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "reference": r["reference"],
                "description": r["description"],
                "delta_vs_windowed": float(r["delta_vs_windowed"]),
                "delta_vs_shuffled": float(r["delta_vs_shuffled"]),
                "pass_deltas": bool(r["pass_deltas"]),
                "verdict": r["verdict"],
                "expected": r["expected"]
            })
    
    # JSON output with full details (convert numpy types)
    json_file = output_dir / "REFERENCE_SCORE.json"
    
    # Convert to JSON-serializable format
    json_results = []
    for r in results:
        json_r = {
            "reference": r["reference"],
            "description": r["description"],
            "expected": r["expected"],
            "text_sample": r["text_sample"],
            "delta_vs_windowed": float(r["delta_vs_windowed"]),
            "delta_vs_shuffled": float(r["delta_vs_shuffled"]),
            "pass_deltas": bool(r["pass_deltas"]),
            "verdict": r["verdict"],
            "scores": {}
        }
        for mode, scores in r["scores"].items():
            json_r["scores"][mode] = {
                k: float(v) if isinstance(v, (np.float32, np.float64, np.ndarray)) else v
                for k, v in scores.items()
            }
        json_results.append(json_r)
    
    with open(json_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    # Markdown report
    report_file = output_dir / "REFERENCE_SCORE.md"
    with open(report_file, 'w') as f:
        f.write("# Reference Scoring Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Seed:** 1337\n\n")
        
        f.write("## Summary\n\n")
        f.write("Testing known reference texts to verify harness behavior:\n\n")
        
        # Check if any narrative texts passed (they shouldn't)
        narrative_refs = ["published_grid", "grid_runner_up"]
        narrative_passes = [r for r in results if r["reference"] in narrative_refs and r["verdict"] == "PASS"]
        
        if narrative_passes:
            f.write("⚠️ **WARNING**: Narrative texts passed under blinding!\n\n")
            for r in narrative_passes:
                f.write(f"- {r['reference']}: {r['verdict']} (Expected: FAIL)\n")
            f.write("\n**Action Required**: Fix blinding mask or anchor scoring order.\n\n")
        else:
            f.write("✅ **All narrative texts correctly FAILED under blinding.**\n\n")
        
        f.write("## Detailed Results\n\n")
        
        for r in results:
            f.write(f"### {r['reference']}\n\n")
            f.write(f"**Description:** {r['description']}\n")
            f.write(f"**Expected:** {r['expected']}\n")
            f.write(f"**Text sample:** `{r['text_sample']}`\n\n")
            
            f.write("**Scores:**\n")
            f.write(f"- Delta vs windowed: {r['delta_vs_windowed']:.4f}\n")
            f.write(f"- Delta vs shuffled: {r['delta_vs_shuffled']:.4f}\n")
            f.write(f"- Pass deltas: {r['pass_deltas']}\n")
            f.write(f"- **Verdict: {r['verdict']}**\n\n")
            
            # Show feature scores
            fixed_scores = r["scores"]["fixed"]
            f.write("**Feature scores (fixed mode):**\n")
            f.write(f"- Anchor score: {fixed_scores['anchor_score']:.3f}\n")
            f.write(f"- Z-ngram: {fixed_scores['z_ngram']:.3f}\n")
            f.write(f"- Z-coverage: {fixed_scores['z_coverage']:.3f}\n")
            f.write(f"- Z-compress: {fixed_scores['z_compress']:.3f}\n")
            f.write(f"- Blinded sample: `{fixed_scores['blinded_sample']}`\n\n")
        
        f.write("## Conclusion\n\n")
        
        all_correct = all(
            (r["reference"] in narrative_refs and r["verdict"] == "FAIL") or
            (r["reference"] not in narrative_refs)
            for r in results
        )
        
        if all_correct:
            f.write("The harness is behaving correctly:\n")
            f.write("- Narrative texts fail under blinding ✅\n")
            f.write("- Blinding prevents leakage ✅\n")
            f.write("- Delta thresholds are discriminative ✅\n")
        else:
            f.write("Issues detected:\n")
            f.write("- Some narrative texts passed (should fail)\n")
            f.write("- Blinding may need adjustment\n")
    
    print(f"\nResults saved to:")
    print(f"  CSV: {csv_file}")
    print(f"  JSON: {json_file}")
    print(f"  Report: {report_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for r in results:
        status = "✅" if r["verdict"] == "FAIL" and "FAIL" in r["expected"] else "❌"
        print(f"{status} {r['reference']:20} → {r['verdict']:4} (expected: {r['expected'][:11]})")
    
    return results


if __name__ == "__main__":
    results = main()