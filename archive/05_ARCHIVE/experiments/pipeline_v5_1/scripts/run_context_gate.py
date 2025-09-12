#!/usr/bin/env python3
"""
Run LLM-based Context Gate evaluation on plaintext candidates.
Deterministic, cached, and fully auditable.
"""

import json
import csv
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import argparse

# For LLM calls, we'll use OpenAI API as an example
# In production, replace with your preferred provider
try:
    import openai
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)

# Model configuration (fixed for v5.1)
MODEL_ID = "gpt-4o-mini"
TEMPERATURE = 0
TOP_P = 0
MAX_TOKENS = 256

# Prompt templates (fixed for v5.1)
SYSTEM_PROMPT = """You are a strict evaluator of one-sentence English instructions. Output JSON only; never prose. Penalize function-word salads and incoherent sequences."""

USER_PROMPT_TEMPLATE = """Evaluate the head window (0..74) of a proposed K4 clause.

TEXT (head only):
{HEAD_TEXT_0_74}

CONTEXT:
- The clause should read like a compact instruction (surveying/navigation cadence).
- Anchors like EAST/NORTHEAST and nouns like BERLIN/CLOCK may appear, but do not assume they make the sentence meaningful.
- Avoid crediting repeated function words or meaningless connectives.

Return JSON with these fields:
- label: string
- overall: 1-5 (general quality)
- coherence: 1-5 (logical flow; avoids non-sequiturs)
- fluency: 1-5 (grammar & naturalness)
- instructional_fit: 0-5 (imperative/surveying vibe)
- semantic_specificity: 0-5 (concrete, content-bearing tokens)
- repetition_penalty: 0-1 (1 if repeated words like "the the")
- notes: one short sentence why"""

# Acceptance thresholds
THRESHOLDS = {
    "overall": 4,
    "coherence": 4,
    "fluency": 4,
    "instructional_fit": 3,
    "semantic_specificity": 3,
    "repetition_penalty": 0  # Must be 0 (no repetition)
}

def compute_prompt_sha256():
    """Compute SHA-256 of the concatenated prompts."""
    full_prompt = SYSTEM_PROMPT + "\n\n" + USER_PROMPT_TEMPLATE
    return hashlib.sha256(full_prompt.encode()).hexdigest()

def compute_context_seed(label: str, pt_sha: str) -> int:
    """Generate deterministic seed for a given head."""
    seed_string = f"CONTEXT|{label}|{pt_sha}|{MODEL_ID}|v5.1"
    hash_bytes = hashlib.sha256(seed_string.encode()).digest()
    # Take low 64 bits as integer
    return int.from_bytes(hash_bytes[:8], byteorder='little') & 0xFFFFFFFFFFFFFFFF

def get_cache_key(label: str, head_text: str) -> str:
    """Generate cache key for LLM response."""
    cache_data = {
        "model_id": MODEL_ID,
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": USER_PROMPT_TEMPLATE.format(HEAD_TEXT_0_74=head_text),
        "label": label
    }
    cache_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.sha256(cache_string.encode()).hexdigest()

def call_llm(label: str, head_text: str, pt_sha: str, cache_dir: Path) -> Dict[str, Any]:
    """Call LLM with deterministic settings and caching."""
    
    # Check cache first
    cache_key = get_cache_key(label, head_text)
    cache_file = cache_dir / f"{label}.json"
    
    if cache_file.exists():
        print(f"  Using cached result for {label}")
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    # Prepare the prompt
    user_prompt = USER_PROMPT_TEMPLATE.format(HEAD_TEXT_0_74=head_text)
    
    # Compute seed
    seed = compute_context_seed(label, pt_sha)
    
    print(f"  Calling LLM for {label} (seed: {seed})")
    
    start_time = time.time()
    
    try:
        # Make the API call
        # Note: seed parameter may not be supported by all providers
        # For true determinism, use a local model or provider that supports seeds
        response = openai.ChatCompletion.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=MAX_TOKENS,
            seed=seed  # May not be supported by all providers
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Extract JSON from response
        response_text = response.choices[0].message.content
        
        # Parse JSON
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Invalid JSON from LLM for {label}: {e}")
            # Fail closed - invalid JSON means context_pass=false
            result = {
                "label": label,
                "overall": 1,
                "coherence": 1,
                "fluency": 1,
                "instructional_fit": 0,
                "semantic_specificity": 0,
                "repetition_penalty": 1,
                "notes": "Parse error - invalid JSON response",
                "parse_error": True
            }
        
        # Add metadata
        result["model_id"] = MODEL_ID
        result["prompt_sha256"] = compute_prompt_sha256()
        result["seed"] = seed
        result["elapsed_ms"] = elapsed_ms
        result["cache_key"] = cache_key
        
        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
        
    except Exception as e:
        print(f"  ERROR: LLM call failed for {label}: {e}")
        # Fail closed
        result = {
            "label": label,
            "overall": 1,
            "coherence": 1,
            "fluency": 1,
            "instructional_fit": 0,
            "semantic_specificity": 0,
            "repetition_penalty": 1,
            "notes": f"API error: {str(e)}",
            "api_error": True,
            "model_id": MODEL_ID,
            "prompt_sha256": compute_prompt_sha256(),
            "seed": seed,
            "elapsed_ms": 0,
            "cache_key": cache_key
        }
        
        # Save error to cache
        with open(cache_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result

def check_pass(result: Dict[str, Any]) -> bool:
    """Check if result passes all thresholds."""
    if result.get("parse_error") or result.get("api_error"):
        return False
    
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
    """Process plaintext catalog through Context Gate."""
    
    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = output_dir / "context"
    cache_dir.mkdir(exist_ok=True)
    
    # Read catalog
    with open(catalog_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Processing {len(rows)} candidates...")
    
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
        
        print(f"[{i}/{len(rows)}] Processing {label}")
        
        # Call LLM
        result = call_llm(label, head_text, pt_sha, cache_dir)
        
        # Check pass/fail
        result["context_pass"] = check_pass(result)
        
        if result["context_pass"]:
            pass_count += 1
            print(f"  ✅ PASS")
        else:
            print(f"  ❌ FAIL")
        
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
        if not r.get("parse_error") and not r.get("api_error"):
            for metric in scores:
                if metric in r:
                    scores[metric].append(r[metric])
    
    with open(summary_path, 'w') as f:
        f.write("# Context Gate Summary (v5.1)\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d')}\n")
        f.write(f"**Model**: {MODEL_ID}\n")
        f.write(f"**Prompt SHA-256**: {compute_prompt_sha256()}\n\n")
        
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
                f.write(f"- Max: {max(values)}\n")
                
                # Histogram
                if metric != "repetition_penalty":
                    hist = {i: values.count(i) for i in range(6)}
                else:
                    hist = {i: values.count(i) for i in range(2)}
                
                f.write("- Distribution:\n")
                for score, count in hist.items():
                    if count > 0:
                        bar = "█" * (count // max(1, total // 50))
                        f.write(f"  - {score}: {count:3d} {bar}\n")
                f.write("\n")
        
        f.write("## Thresholds\n\n")
        f.write("Required for pass:\n")
        for metric, threshold in THRESHOLDS.items():
            if metric == "repetition_penalty":
                f.write(f"- {metric}: == {threshold}\n")
            else:
                f.write(f"- {metric}: ≥ {threshold}\n")
    
    print(f"Summary written to {summary_path}")

def generate_manifest(output_dir: Path):
    """Generate SHA-256 manifest of all outputs."""
    
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
    
    print(f"Manifest written to {manifest_path}")

def main():
    parser = argparse.ArgumentParser(description="Run Context Gate evaluation")
    parser.add_argument("--catalog", required=True, help="Path to plaintext catalog CSV")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--head-col", help="Column name for head text (default: auto-detect)")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        openai.api_key = args.api_key
    elif "OPENAI_API_KEY" not in os.environ:
        print("ERROR: Please provide --api-key or set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    catalog_path = Path(args.catalog)
    output_dir = Path(args.out)
    
    if not catalog_path.exists():
        print(f"ERROR: Catalog not found: {catalog_path}")
        sys.exit(1)
    
    # Process catalog
    results = process_catalog(catalog_path, output_dir, args.head_col)
    
    print("\n✅ Context Gate evaluation complete!")

if __name__ == "__main__":
    main()