#!/usr/bin/env python3
"""
Mock Context Gate evaluator for testing without LLM API.
Uses heuristics to simulate LLM judgments based on text patterns.
"""

import json
import csv
import hashlib
import re
import time
from pathlib import Path
from typing import Dict, Any
import argparse

# Model configuration (mock)
MODEL_ID = "mock-evaluator-v1"

# Thresholds (same as real)
THRESHOLDS = {
    "overall": 4,
    "coherence": 4,
    "fluency": 4,
    "instructional_fit": 3,
    "semantic_specificity": 3,
    "repetition_penalty": 0
}

def compute_prompt_sha256():
    """Compute SHA-256 of the prompts (mock)."""
    return "mock_" + "0" * 60

def compute_context_seed(label: str, pt_sha: str) -> int:
    """Generate deterministic seed."""
    seed_string = f"CONTEXT|{label}|{pt_sha}|{MODEL_ID}|v5.1"
    hash_bytes = hashlib.sha256(seed_string.encode()).digest()
    return int.from_bytes(hash_bytes[:8], byteorder='little') & 0xFFFFFFFFFFFFFFFF

def detect_repetition(text: str) -> int:
    """Detect repeated words like 'the the', 'and and'."""
    words = text.lower().split()
    for i in range(len(words) - 1):
        if words[i] == words[i + 1] and words[i] in ['the', 'and', 'then', 'that', 'this', 'a', 'an']:
            return 1
    return 0

def count_function_words(text: str) -> int:
    """Count function words in text."""
    function_words = {
        'the', 'and', 'a', 'an', 'then', 'that', 'this', 'these', 'those',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'shall', 'can', 'need', 'ought', 'used', 'to', 'of', 'in', 'on',
        'at', 'by', 'for', 'with', 'from', 'up', 'about', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'between', 'under',
        'but', 'or', 'if', 'because', 'as', 'until', 'while', 'since'
    }
    
    words = text.lower().split()
    return sum(1 for w in words if w in function_words)

def count_content_words(text: str) -> int:
    """Count content words (nouns, verbs, adjectives)."""
    # Simple heuristic: words not in function word list
    function_words = {
        'the', 'and', 'a', 'an', 'then', 'that', 'this', 'these', 'those',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'shall', 'can', 'need', 'ought', 'used', 'to', 'of', 'in', 'on'
    }
    
    words = text.lower().split()
    return sum(1 for w in words if w not in function_words and len(w) > 2)

def has_surveying_keywords(text: str) -> bool:
    """Check for surveying/navigation keywords."""
    keywords = [
        'EAST', 'WEST', 'NORTH', 'SOUTH', 'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
        'DEGREE', 'DISTANCE', 'SET', 'READ', 'MEASURE', 'POINT', 'LINE', 'ANGLE',
        'BERLIN', 'CLOCK', 'SHADOW', 'MEMORY'
    ]
    text_upper = text.upper()
    return any(kw in text_upper for kw in keywords)

def evaluate_mock(label: str, head_text: str, pt_sha: str) -> Dict[str, Any]:
    """
    Mock evaluation using heuristics.
    Simulates realistic judgments based on text patterns.
    """
    
    # Basic text analysis
    word_count = len(head_text.split())
    func_count = count_function_words(head_text)
    content_count = count_content_words(head_text)
    func_ratio = func_count / max(1, word_count)
    
    # Check for repetition
    repetition = detect_repetition(head_text)
    
    # Check for surveying keywords
    has_keywords = has_surveying_keywords(head_text)
    
    # Heuristic scoring based on patterns
    
    # Coherence: penalize excessive function words
    if func_ratio > 0.7:
        coherence = 2  # Function word salad
    elif func_ratio > 0.6:
        coherence = 3
    elif func_ratio > 0.5:
        coherence = 4
    else:
        coherence = 5
    
    # Fluency: based on word patterns
    if repetition == 1:
        fluency = 2  # Repeated words hurt fluency
    elif func_ratio > 0.7:
        fluency = 3
    else:
        fluency = 4 if func_ratio > 0.5 else 5
    
    # Instructional fit: bonus for surveying keywords
    if has_keywords:
        instructional_fit = 4
    elif content_count > 3:
        instructional_fit = 3
    else:
        instructional_fit = 2 if func_ratio > 0.6 else 3
    
    # Semantic specificity: based on content words
    if content_count >= 5:
        semantic_specificity = 4
    elif content_count >= 3:
        semantic_specificity = 3
    elif content_count >= 2:
        semantic_specificity = 2
    else:
        semantic_specificity = 1  # Pure function words
    
    # Overall: weighted average
    overall = min(5, max(1, round(
        (coherence * 0.3 + fluency * 0.3 + instructional_fit * 0.2 + semantic_specificity * 0.2)
    )))
    
    # Special case: HEAD_147_B pattern (known word salad)
    if "ONTHENREADTHETHISANDA" in head_text.replace(" ", ""):
        coherence = 2
        fluency = 2
        semantic_specificity = 1
        overall = 2
        notes = "Function-word salad pattern detected"
    else:
        notes = f"Mock evaluation: func_ratio={func_ratio:.2f}, content={content_count}"
    
    result = {
        "label": label,
        "overall": overall,
        "coherence": coherence,
        "fluency": fluency,
        "instructional_fit": instructional_fit,
        "semantic_specificity": semantic_specificity,
        "repetition_penalty": repetition,
        "notes": notes,
        "model_id": MODEL_ID,
        "prompt_sha256": compute_prompt_sha256(),
        "seed": compute_context_seed(label, pt_sha),
        "elapsed_ms": 10,  # Mock timing
        "cache_key": hashlib.sha256(f"{label}_{head_text}".encode()).hexdigest()
    }
    
    return result

def check_pass(result: Dict[str, Any]) -> bool:
    """Check if result passes all thresholds."""
    checks = [
        result.get("overall", 0) >= THRESHOLDS["overall"],
        result.get("coherence", 0) >= THRESHOLDS["coherence"],
        result.get("fluency", 0) >= THRESHOLDS["fluency"],
        result.get("instructional_fit", 0) >= THRESHOLDS["instructional_fit"],
        result.get("semantic_specificity", 0) >= THRESHOLDS["semantic_specificity"],
        result.get("repetition_penalty", 1) == THRESHOLDS["repetition_penalty"]
    ]
    
    return all(checks)

def process_catalog(catalog_path: Path, output_dir: Path, head_col: str = None):
    """Process plaintext catalog through mock Context Gate."""
    
    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = output_dir / "context"
    cache_dir.mkdir(exist_ok=True)
    
    # Read catalog
    with open(catalog_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} candidates with mock evaluator...")
    
    results = []
    pass_count = 0
    
    for i, row in enumerate(rows, 1):
        label = row.get("label", row.get("candidate", "unknown"))
        
        # Get head text (first 75 chars of plaintext)
        if head_col and head_col in row:
            head_text = row[head_col][:75]
        elif "plaintext_97" in row:
            head_text = row["plaintext_97"][:75]
        elif "plaintext" in row:
            head_text = row["plaintext"][:75]
        else:
            print(f"ERROR: No plaintext column found for {label}")
            continue
        
        # Get PT SHA if available
        pt_sha = row.get("pt_sha256", hashlib.sha256(head_text.encode()).hexdigest())
        
        if i <= 5 or i % 50 == 0:  # Progress indicator
            print(f"[{i}/{len(rows)}] Processing {label}")
        
        # Mock evaluation
        result = evaluate_mock(label, head_text, pt_sha)
        
        # Check pass/fail
        result["context_pass"] = check_pass(result)
        
        if result["context_pass"]:
            pass_count += 1
        
        # Save to cache
        cache_file = cache_dir / f"{label}.json"
        with open(cache_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        results.append(result)
    
    # Write results CSV
    csv_path = output_dir / "CONTEXT_JUDGMENTS.csv"
    
    fieldnames = [
        "label", "context_pass",
        "overall", "coherence", "fluency", 
        "instructional_fit", "semantic_specificity", "repetition_penalty",
        "notes", "model_id", "prompt_sha256", "seed", "elapsed_ms"
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults written to {csv_path}")
    print(f"Passed: {pass_count}/{len(rows)} ({pass_count/len(rows)*100:.1f}%)")
    
    # Generate summary
    generate_summary(results, output_dir, len(rows), pass_count)
    
    # Generate manifest
    generate_manifest(output_dir)
    
    return results

def generate_summary(results: list, output_dir: Path, total: int, passed: int):
    """Generate summary markdown report."""
    
    summary_path = output_dir / "CONTEXT_SUMMARY.md"
    
    # Calculate statistics
    scores = {
        "overall": [],
        "coherence": [],
        "fluency": [],
        "instructional_fit": [],
        "semantic_specificity": [],
        "repetition_penalty": []
    }
    
    for r in results:
        for metric in scores:
            if metric in r:
                scores[metric].append(r[metric])
    
    with open(summary_path, 'w') as f:
        f.write("# Context Gate Summary (v5.1 - Mock Evaluator)\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d')}\n")
        f.write(f"**Model**: {MODEL_ID}\n")
        f.write(f"**Note**: This is a mock evaluation using heuristics, not actual LLM\n\n")
        
        f.write("## Results\n\n")
        f.write(f"- **Total Evaluated**: {total}\n")
        f.write(f"- **Passed Context Gate**: {passed} ({passed/total*100:.1f}%)\n")
        f.write(f"- **Failed Context Gate**: {total-passed} ({(total-passed)/total*100:.1f}%)\n\n")
        
        f.write("## Score Distributions\n\n")
        
        for metric, values in scores.items():
            if values:
                avg = sum(values) / len(values)
                f.write(f"### {metric.replace('_', ' ').title()}\n")
                f.write(f"- Mean: {avg:.2f}\n")
                f.write(f"- Min: {min(values)}\n")
                f.write(f"- Max: {max(values)}\n\n")
        
        f.write("## Thresholds\n\n")
        f.write("Required for pass:\n")
        for metric, threshold in THRESHOLDS.items():
            if metric == "repetition_penalty":
                f.write(f"- {metric}: == {threshold}\n")
            else:
                f.write(f"- {metric}: ≥ {threshold}\n")

def generate_manifest(output_dir: Path):
    """Generate SHA-256 manifest."""
    
    manifest_path = output_dir / "MANIFEST.sha256"
    
    files_to_hash = [
        "CONTEXT_JUDGMENTS.csv",
        "CONTEXT_SUMMARY.md"
    ]
    
    # Add all context JSON files
    context_dir = output_dir / "context"
    if context_dir.exists():
        for json_file in sorted(context_dir.glob("*.json")):
            files_to_hash.append(f"context/{json_file.name}")
    
    with open(manifest_path, 'w') as manifest:
        for file_rel in files_to_hash:
            file_path = output_dir / file_rel
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    sha = hashlib.sha256(f.read()).hexdigest()
                manifest.write(f"{sha}  {file_rel}\n")

def main():
    parser = argparse.ArgumentParser(description="Run mock Context Gate evaluation")
    parser.add_argument("--catalog", required=True, help="Path to plaintext catalog CSV")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--head-col", help="Column name for head text")
    
    args = parser.parse_args()
    
    catalog_path = Path(args.catalog)
    output_dir = Path(args.out)
    
    if not catalog_path.exists():
        print(f"ERROR: Catalog not found: {catalog_path}")
        return 1
    
    # Process catalog
    results = process_catalog(catalog_path, output_dir, args.head_col)
    
    print("\n✅ Mock Context Gate evaluation complete!")
    return 0

if __name__ == "__main__":
    exit(main())