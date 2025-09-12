#!/usr/bin/env python3
"""
Generate large candidate bank from surveying-equivalent grammars.
Produces several hundred to thousand heads for Explore testing.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Set
import itertools
import random
from datetime import datetime

# Template components
PRED_VALUES = ["REAL", "TRUE", "AMAP", "CODE", "DATA", "FACT", "PLAIN", "CLEAR", "READY", "OPEN"]
COURSE_VALUES = ["COURSE", "LINE", "BEARING", "MERIDIAN"]
INSTR_VERBS = ["READ", "SEE", "NOTE", "SIGHT", "OBSERVE"]

# Declination phrases (with {COURSE} placeholder)
DECLIN_PHRASES = [
    "SETTHE{COURSE}TRUE",
    "CORRECTTHE{COURSE}TOTRUE",
    "REDUCETHE{COURSE}TOTHETRUEMERIDIAN",
    "APPLYDECLINATION",
    "BRINGTHE{COURSE}TOTHETRUELINEE"
]

# Base templates
TEMPLATES = [
    "WECANSEETHETEXTIS{PRED}EASTWESTNORTHEASTWESETTTHE{COURSE}TRUE{VERB1}THENSEEBERLINCCLOCK",
    "WECANSEETHETEXTIS{PRED}WESSETTHE{COURSE}TRUE{VERB1}THEN{VERB2}BERLINCLOCK",
    "{DECLIN}{VERB1}THEN{VERB2}BERLINCLOCK",
    "WESETTTHE{COURSE}TRUEWECANSEEETHE{PRED}EASTWESTNORTHEAST{VERB1}BERLINCLOCK",
    "{VERB1}THEBERLINCLOCKEASTNORTHEAST{DECLIN}WECANSEETHETEXT",
    "THE{PRED}TEXTEASTWESTNORTHEAST{DECLIN}{VERB1}THENSEEEBERLINCLOCK"
]

def remove_spaces(text: str) -> str:
    """Remove spaces and ensure uppercase."""
    return text.upper().replace(" ", "")

def expand_template(template: str) -> List[str]:
    """Expand a single template into all combinations."""
    candidates = []
    
    # Get all possible values for each slot
    pred_options = PRED_VALUES if "{PRED}" in template else [None]
    course_options = COURSE_VALUES if "{COURSE}" in template else [None]
    verb1_options = INSTR_VERBS if "{VERB1}" in template else [None]
    verb2_options = INSTR_VERBS if "{VERB2}" in template else [None]
    
    # Handle declination phrases
    if "{DECLIN}" in template:
        declin_options = []
        for phrase in DECLIN_PHRASES:
            if "{COURSE}" in phrase:
                for course in COURSE_VALUES:
                    declin_options.append(phrase.replace("{COURSE}", course))
            else:
                declin_options.append(phrase)
    else:
        declin_options = [None]
    
    # Generate all combinations
    for pred, course, verb1, verb2, declin in itertools.product(
        pred_options, course_options, verb1_options, verb2_options, declin_options
    ):
        result = template
        
        if pred:
            result = result.replace("{PRED}", pred)
        if course:
            result = result.replace("{COURSE}", course)
        if verb1:
            result = result.replace("{VERB1}", verb1)
        if verb2:
            result = result.replace("{VERB2}", verb2)
        if declin:
            result = result.replace("{DECLIN}", declin)
        
        # Clean up and check length
        result = remove_spaces(result)
        if len(result) <= 75:  # Must fit in head window [0,74]
            candidates.append(result)
    
    return candidates

def add_lexical_perturbations(base_heads: List[str], max_variants: int = 2) -> List[str]:
    """Add synonym expansions and edit-1 variants."""
    variants = []
    
    # Synonyms for variation
    synonyms = {
        "SEE": ["VIEW", "LOOK"],
        "READ": ["SCAN", "CHECK"],
        "TRUE": ["REAL", "EXACT"],
        "COURSE": ["PATH", "ROUTE"],
        "TEXT": ["CODE", "DATA"],
        "CLOCK": ["DIAL", "METER"]
    }
    
    for head in base_heads[:100]:  # Limit to avoid explosion
        # Add synonym variants
        for old, new_options in synonyms.items():
            if old in head:
                for new in new_options[:max_variants]:
                    variant = head.replace(old, new)
                    if len(variant) <= 75:
                        variants.append(variant)
        
        # Add edit-1 misspellings (K-style)
        if random.random() < 0.1:  # 10% get misspellings
            pos = random.randint(0, len(head) - 1)
            chars = list(head)
            # Substitution
            if chars[pos] != 'Q':  # Avoid creating invalid Q patterns
                chars[pos] = chr((ord(chars[pos]) - ord('A') + 1) % 26 + ord('A'))
                variant = ''.join(chars)
                if len(variant) <= 75:
                    variants.append(variant)
    
    return variants

def generate_candidate_bank(seed: int = 1337) -> Dict:
    """Generate full candidate bank."""
    random.seed(seed)
    
    print("Generating base candidates from templates...")
    all_candidates = []
    
    # Expand all templates
    for i, template in enumerate(TEMPLATES):
        print(f"  Template {i+1}/{len(TEMPLATES)}...")
        expanded = expand_template(template)
        all_candidates.extend(expanded)
        print(f"    Generated {len(expanded)} candidates")
    
    # Deduplicate
    unique_candidates = list(set(all_candidates))
    print(f"\nUnique base candidates: {len(unique_candidates)}")
    
    # Add perturbations
    print("Adding lexical perturbations...")
    perturbations = add_lexical_perturbations(unique_candidates)
    all_candidates = unique_candidates + perturbations
    
    # Final deduplication
    final_candidates = list(set(all_candidates))
    print(f"Final unique candidates: {len(final_candidates)}")
    
    # Create labeled entries
    heads = []
    for i, text in enumerate(final_candidates):
        heads.append({
            "label": f"H{i+1:04d}",
            "text": text,
            "length": len(text)
        })
    
    # Sort by length for easier inspection
    heads.sort(key=lambda x: x["length"])
    
    return {
        "seed": seed,
        "generation": "surveying_grammar_v1",
        "timestamp": datetime.now().isoformat(),
        "script_hash": hashlib.sha256(open(__file__, 'rb').read()).hexdigest()[:16],
        "stats": {
            "total_heads": len(heads),
            "min_length": min(h["length"] for h in heads),
            "max_length": max(h["length"] for h in heads),
            "avg_length": sum(h["length"] for h in heads) / len(heads)
        },
        "heads": heads
    }

def main():
    """Generate and save candidate bank."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate candidate bank")
    parser.add_argument("--output", default="experiments/pipeline_v2/data/candidates_explore_hard.json")
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--limit", type=int, help="Limit number of candidates")
    
    args = parser.parse_args()
    
    # Generate candidates
    bank = generate_candidate_bank(args.seed)
    
    # Apply limit if specified
    if args.limit:
        bank["heads"] = bank["heads"][:args.limit]
        bank["stats"]["total_heads"] = len(bank["heads"])
    
    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(bank, f, indent=2)
    
    print(f"\nCandidate bank saved to: {output_path}")
    print(f"Total candidates: {bank['stats']['total_heads']}")
    print(f"Length range: {bank['stats']['min_length']}-{bank['stats']['max_length']}")
    print(f"Script hash: {bank['script_hash']}")

if __name__ == "__main__":
    main()