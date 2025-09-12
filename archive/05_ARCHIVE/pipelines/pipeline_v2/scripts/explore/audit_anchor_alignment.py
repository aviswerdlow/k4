#!/usr/bin/env python3
"""
Audit anchor alignment in generated heads.
Verifies anchors are placed at expected positions and measures alignment quality.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Expected anchor positions in corridor
EXPECTED_POSITIONS = {
    "EAST": 21,
    "NORTHEAST": 25,
    "BERLINCLOCK": 63
}


def find_anchor_positions(text: str) -> Dict[str, List[int]]:
    """
    Find all occurrences of anchors in text.
    
    Returns:
        Dict mapping anchor to list of positions where found
    """
    positions = {}
    
    for anchor in EXPECTED_POSITIONS.keys():
        found = []
        # Find exact matches
        for match in re.finditer(anchor, text):
            found.append(match.start())
        positions[anchor] = found
    
    return positions


def find_fuzzy_anchor_positions(text: str, max_typos: int = 2) -> Dict[str, List[Tuple[int, int, str]]]:
    """
    Find fuzzy matches for anchors allowing typos.
    
    Returns:
        Dict mapping anchor to list of (position, edit_distance, matched_text) tuples
    """
    from difflib import SequenceMatcher
    
    fuzzy_positions = {}
    
    for anchor in EXPECTED_POSITIONS.keys():
        found = []
        anchor_len = len(anchor)
        
        # Slide window across text
        for i in range(len(text) - anchor_len + 2):  # +2 for deletions
            for window_len in range(max(3, anchor_len - max_typos), 
                                   min(len(text) - i, anchor_len + max_typos) + 1):
                if i + window_len > len(text):
                    continue
                    
                window = text[i:i + window_len]
                
                # Calculate similarity
                matcher = SequenceMatcher(None, anchor, window)
                ratio = matcher.ratio()
                
                # Estimate edit distance
                edit_distance = int((1 - ratio) * max(len(anchor), len(window)))
                
                # Accept if within typo budget and reasonably similar
                if edit_distance <= max_typos and ratio > 0.6:
                    found.append((i, edit_distance, window))
        
        # Remove overlapping matches, keep best
        found.sort(key=lambda x: (x[1], abs(x[0] - EXPECTED_POSITIONS[anchor])))
        filtered = []
        used_positions = set()
        
        for pos, dist, matched in found:
            if not any(abs(pos - used) < 3 for used in used_positions):
                filtered.append((pos, dist, matched))
                used_positions.add(pos)
        
        fuzzy_positions[anchor] = filtered[:3]  # Keep top 3 matches
    
    return fuzzy_positions


def calculate_alignment_score(positions: Dict[str, List[int]]) -> float:
    """
    Calculate alignment score based on how close anchors are to expected positions.
    
    Score = 1.0 if all anchors at exact positions
    Score decreases with distance from expected positions
    """
    total_score = 0.0
    max_score = len(EXPECTED_POSITIONS)
    
    for anchor, expected_pos in EXPECTED_POSITIONS.items():
        found_positions = positions.get(anchor, [])
        
        if not found_positions:
            # No anchor found
            continue
        
        # Find closest match to expected position
        closest_distance = min(abs(pos - expected_pos) for pos in found_positions)
        
        # Score based on distance (max 1.0 for exact match)
        if closest_distance == 0:
            score = 1.0
        elif closest_distance <= 3:
            score = 1.0 - (closest_distance * 0.2)  # -0.2 per position off
        elif closest_distance <= 10:
            score = 0.4 - (closest_distance - 3) * 0.05  # Gradual decay
        else:
            score = 0.0
        
        total_score += score
    
    return total_score / max_score if max_score > 0 else 0.0


def audit_heads(candidates_file: Path) -> Dict:
    """
    Audit anchor alignment in candidate heads.
    
    Returns:
        Audit report with statistics and alignment scores
    """
    with open(candidates_file) as f:
        data = json.load(f)
    
    heads = data.get("heads", [])
    
    audit_results = []
    alignment_scores = []
    
    for head in heads:
        text = head["text"]
        label = head["label"]
        
        # Find exact anchor positions
        exact_positions = find_anchor_positions(text)
        
        # Find fuzzy matches
        fuzzy_positions = find_fuzzy_anchor_positions(text)
        
        # Calculate alignment score
        score = calculate_alignment_score(exact_positions)
        alignment_scores.append(score)
        
        # Determine issues
        issues = []
        for anchor, expected_pos in EXPECTED_POSITIONS.items():
            found = exact_positions.get(anchor, [])
            fuzzy = fuzzy_positions.get(anchor, [])
            
            if not found:
                if fuzzy:
                    best_fuzzy = fuzzy[0]
                    issues.append(f"{anchor} not found exactly, fuzzy match at {best_fuzzy[0]} ('{best_fuzzy[2]}', dist={best_fuzzy[1]})")
                else:
                    issues.append(f"{anchor} missing entirely")
            else:
                closest = min(found, key=lambda x: abs(x - expected_pos))
                if closest != expected_pos:
                    issues.append(f"{anchor} at {closest} (expected {expected_pos}, off by {closest - expected_pos:+d})")
        
        result = {
            "label": label,
            "alignment_score": score,
            "exact_positions": exact_positions,
            "fuzzy_positions": {k: [(p, d, t) for p, d, t in v] for k, v in fuzzy_positions.items()},
            "issues": issues
        }
        audit_results.append(result)
    
    # Calculate statistics
    perfect_count = sum(1 for s in alignment_scores if s == 1.0)
    good_count = sum(1 for s in alignment_scores if 0.8 <= s < 1.0)
    moderate_count = sum(1 for s in alignment_scores if 0.5 <= s < 0.8)
    poor_count = sum(1 for s in alignment_scores if s < 0.5)
    
    # Group by category
    categories = {}
    for result in audit_results:
        category = result["label"].split("_")[1] if "_" in result["label"] else "OTHER"
        if category not in categories:
            categories[category] = []
        categories[category].append(result["alignment_score"])
    
    category_stats = {}
    for cat, scores in categories.items():
        if scores:
            category_stats[cat] = {
                "count": len(scores),
                "mean_score": sum(scores) / len(scores),
                "perfect": sum(1 for s in scores if s == 1.0),
                "has_anchors": sum(1 for s in scores if s > 0)
            }
    
    report = {
        "total_heads": len(heads),
        "alignment_summary": {
            "perfect": perfect_count,
            "good": good_count,
            "moderate": moderate_count,
            "poor": poor_count,
            "mean_score": sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0
        },
        "category_stats": category_stats,
        "detailed_results": audit_results
    }
    
    return report


def generate_audit_report(candidates_file: Path, output_file: Path) -> None:
    """Generate and save audit report."""
    
    print(f"Auditing {candidates_file}...")
    report = audit_heads(candidates_file)
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save JSON report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("ANCHOR ALIGNMENT AUDIT REPORT")
    print("=" * 60)
    
    summary = report["alignment_summary"]
    print(f"\nTotal heads analyzed: {report['total_heads']}")
    print(f"Mean alignment score: {summary['mean_score']:.3f}")
    print(f"\nAlignment distribution:")
    print(f"  Perfect (1.0):     {summary['perfect']:3d} heads")
    print(f"  Good (0.8-1.0):    {summary['good']:3d} heads")
    print(f"  Moderate (0.5-0.8): {summary['moderate']:3d} heads")
    print(f"  Poor (<0.5):       {summary['poor']:3d} heads")
    
    print(f"\nCategory breakdown:")
    for cat, stats in sorted(report["category_stats"].items()):
        print(f"  {cat:12s}: {stats['count']:3d} heads, "
              f"mean={stats['mean_score']:.3f}, "
              f"perfect={stats['perfect']}, "
              f"has_anchors={stats['has_anchors']}")
    
    # Show examples of issues
    print(f"\nExample alignment issues:")
    shown = 0
    for result in report["detailed_results"]:
        if result["issues"] and shown < 5:
            print(f"  {result['label']}: {result['issues'][0]}")
            shown += 1
    
    print(f"\nFull report saved to: {output_file}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Audit anchor alignment in heads")
    parser.add_argument("--input",
                       default="experiments/pipeline_v2/data/corridor_heads.json",
                       help="Input candidates file")
    parser.add_argument("--output",
                       default="experiments/pipeline_v2/runs/2025-01-06-explore-corridor/ANCHOR_AUDIT.json",
                       help="Output audit report")
    
    args = parser.parse_args()
    
    generate_audit_report(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()