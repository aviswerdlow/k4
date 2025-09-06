#!/usr/bin/env python3
"""
Generate breadth candidate bank with register mixing, syntactic variations,
and n-gram optimization for Explore-Hard breadth campaign.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Set
import itertools
import random
from datetime import datetime

# Expanded vocabulary for register mixing
PRED_VALUES = ["REAL", "TRUE", "CLEAR", "PLAIN", "EVIDENT", "CONSISTENT", "SHOWN", "KNOWN", "VISIBLE", "DECODED"]
VERB_VALUES = ["READ", "SEE", "NOTE", "SIGHT", "OBSERVE", "VIEW", "SCAN", "CHECK", "MARK", "FIND"]
COURSE_VALUES = ["COURSE", "LINE", "BEARING", "PATH", "ROUTE", "TRACK", "WAY", "DIRECTION"]
CONNECTOR_VALUES = ["THE", "OF", "IN", "TO", "AND", "IS", "ARE", "WAS", "BE", "HAS"]

# Register mixing templates (declarative + imperative hybrids)
HYBRID_TEMPLATES = [
    # Declarative + imperative
    "WEOBSERVETHETEXTTOBE{PRED}EASTNORTHEASTISSHOWN",
    "THETEXTIS{PRED}ANDWEMUSTSETTHECOURSETOTRUE",
    "ITISCLEARTHATTHE{PRED}TEXTEASTNORTHEASTREQUIRESACTION",
    "{PRED}ISTHETEXT{CONNECTOR}SETTHECOURSEANDREADTHECLOCK",
    "THE{COURSE}TOTRUSISSETTHENSEEBERLINCLOCKEASTNORTHEAST",
    
    # With light punctuation (will be removed but affects flow)
    "OBSERVE:THETEXTIS{PRED}.EASTNORTHEASTSHOWN",
    "SETTHETRUECOURSE;THEN{VERB}THEBERLINCLOCK",
    "THE{PRED}TEXT,EASTNORTHEAST,REQUIRES{VERB}ING",
    
    # Clause reshuffles
    "EASTNORTHEASTTHESHOWN{PRED}TEXTREQUIRESTHE{COURSE}SETTRUE",
    "BERLINCLOCKINDICATESTHE{PRED}WHENTHE{COURSE}ISTRUESET",
    "TRUE{COURSE}SETTINGREVEALSTHETEXTASEASTNORTHEAST{PRED}",
    
    # N-gram optimized with glue words
    "THEOFINTHEOF{PRED}TEXTANDTHEEASTNORTHEASTISSHOWN",
    "SETTHETRUECOURSEOFTHEBEARINGTOREADTHEBERLINCLOCKOFNOW",
    "INTHEWAYOFTHETRUETHETEXT{PRED}EASTNORTHEASTAPPEARS"
]

# Length-optimized templates (65-75 chars target)
LONG_TEMPLATES = [
    "WECANOBSERVETHATTHE{PRED}TEXTISEASTNORTHEASTANDTHEBEARINGMUSTSETTRUETOPROCEED",
    "THECOURSETOTRUEISSETANDTHENWEMUSTSEETHEBERLINCLOCKEASTNORTHEASTFORCONFIRMATION",
    "OBSERVECAREFULLYTHETEXTWHICHIS{PRED}EASTNORTHEASTTHENSETTHETRUECOURSEANDREAD",
    "INTHISINSTANCETHE{PRED}TEXTEASTNORTHEASTREQUIRESUSTOSETTHECOURSETOTRUEANDVIEW",
    "WHENTHEBERLINCLOCKISREADANDTHE{COURSE}ISSETTRUETHETEXTEASTNORTHEASTBECOMES{PRED}"
]

def remove_punctuation_and_spaces(text: str) -> str:
    """Remove all punctuation and spaces, ensure uppercase."""
    # Remove common punctuation
    for punct in ".,;:!?-_'\"()[]{}":
        text = text.replace(punct, "")
    # Remove spaces and uppercase
    return text.upper().replace(" ", "")

def add_ngram_glue(text: str, max_additions: int = 3) -> List[str]:
    """Add n-gram improving glue sequences."""
    variants = []
    glue_words = ["THE", "OF", "AND", "IN", "TO", "IS"]
    
    for _ in range(max_additions):
        # Try inserting glue at various positions
        for pos in [10, 20, 30, 40, 50]:
            if pos < len(text):
                for glue in glue_words:
                    variant = text[:pos] + glue + text[pos:]
                    if len(variant) <= 75:
                        variants.append(variant)
    
    return variants

def generate_misspellings(text: str, rate: float = 0.1) -> List[str]:
    """Generate K-style misspellings (Levenshtein-1)."""
    variants = []
    
    if random.random() < rate:
        # Content token misspellings (avoid anchor/direction words)
        avoid_words = ["EAST", "NORTHEAST", "BERLIN", "CLOCK"]
        
        # Find safe positions for misspelling
        safe_positions = []
        for i in range(len(text)):
            safe = True
            for word in avoid_words:
                for j in range(len(word)):
                    if i >= j and i < len(text) - (len(word) - j - 1):
                        if text[i-j:i-j+len(word)] == word:
                            safe = False
                            break
            if safe:
                safe_positions.append(i)
        
        if safe_positions:
            # Substitution
            pos = random.choice(safe_positions)
            chars = list(text)
            old_char = chars[pos]
            # Choose nearby character
            if old_char != 'Q':
                new_char = chr((ord(old_char) - ord('A') + random.choice([-1, 1])) % 26 + ord('A'))
                chars[pos] = new_char
                variants.append(''.join(chars))
            
            # Transposition
            if pos < len(text) - 1:
                chars = list(text)
                chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
                variants.append(''.join(chars))
    
    return variants

def expand_hybrid_template(template: str) -> List[str]:
    """Expand a hybrid template with all slot combinations."""
    candidates = []
    
    # Get slot options
    pred_options = PRED_VALUES if "{PRED}" in template else [None]
    verb_options = VERB_VALUES if "{VERB}" in template else [None]
    course_options = COURSE_VALUES if "{COURSE}" in template else [None]
    connector_options = CONNECTOR_VALUES if "{CONNECTOR}" in template else [None]
    
    # Generate combinations
    for pred, verb, course, connector in itertools.product(
        pred_options, verb_options, course_options, connector_options
    ):
        result = template
        
        if pred:
            result = result.replace("{PRED}", pred)
        if verb:
            result = result.replace("{VERB}", verb)
        if course:
            result = result.replace("{COURSE}", course)
        if connector:
            result = result.replace("{CONNECTOR}", connector)
        
        # Clean and check length
        result = remove_punctuation_and_spaces(result)
        
        # Target 65-75 char range for this campaign
        if 65 <= len(result) <= 75:
            candidates.append(result)
        elif len(result) < 65:
            # Try adding n-gram glue
            glued = add_ngram_glue(result, 2)
            candidates.extend([g for g in glued if 65 <= len(g) <= 75])
    
    return candidates

def generate_breadth_candidates(seed: int = 1337) -> Dict:
    """Generate breadth candidate bank with register mixing."""
    random.seed(seed)
    
    print("Generating breadth candidates...")
    all_candidates = []
    
    # Process hybrid templates
    print("  Processing hybrid templates...")
    for i, template in enumerate(HYBRID_TEMPLATES):
        expanded = expand_hybrid_template(template)
        all_candidates.extend(expanded)
        if i % 5 == 0:
            print(f"    Template {i+1}/{len(HYBRID_TEMPLATES)}: {len(expanded)} candidates")
    
    # Process long templates
    print("  Processing long templates...")
    for i, template in enumerate(LONG_TEMPLATES):
        expanded = expand_hybrid_template(template)
        all_candidates.extend(expanded)
        print(f"    Long template {i+1}/{len(LONG_TEMPLATES)}: {len(expanded)} candidates")
    
    # Deduplicate
    unique_candidates = list(set(all_candidates))
    print(f"\nUnique candidates before variations: {len(unique_candidates)}")
    
    # Add misspellings and variations
    print("Adding misspellings and n-gram variations...")
    variations = []
    
    for candidate in unique_candidates[:200]:  # Limit to avoid explosion
        # Misspellings
        misspelled = generate_misspellings(candidate, rate=0.15)
        variations.extend(misspelled)
        
        # N-gram glue additions
        if len(candidate) < 70:
            glued = add_ngram_glue(candidate, 1)
            variations.extend(glued[:2])  # Limit variants per candidate
    
    all_candidates = unique_candidates + variations
    
    # Final deduplication and filtering
    final_candidates = list(set(all_candidates))
    # Focus on 65-75 char range
    final_candidates = [c for c in final_candidates if 65 <= len(c) <= 75]
    
    print(f"Final candidates in target range: {len(final_candidates)}")
    
    # Create labeled entries
    heads = []
    for i, text in enumerate(final_candidates):
        heads.append({
            "label": f"B{i+1:04d}",  # B for Breadth
            "text": text,
            "length": len(text)
        })
    
    # Sort by score potential (length, n-gram hints)
    def score_potential(head):
        text = head["text"]
        score = 0
        # Favor texts with common bigrams
        for bigram in ["TH", "HE", "IN", "ER", "AN", "ED", "TO", "EN", "ES", "OF"]:
            score += text.count(bigram)
        # Penalty for rare bigrams
        for bigram in ["QX", "ZX", "XQ", "QZ", "JQ"]:
            score -= text.count(bigram) * 2
        return score
    
    heads.sort(key=lambda x: (-score_potential(x), x["length"]))
    
    return {
        "seed": seed,
        "generation": "breadth_grammar_v1",
        "timestamp": datetime.now().isoformat(),
        "script_hash": hashlib.sha256(open(__file__, 'rb').read()).hexdigest()[:16],
        "stats": {
            "total_heads": len(heads),
            "min_length": min(h["length"] for h in heads) if heads else 0,
            "max_length": max(h["length"] for h in heads) if heads else 0,
            "avg_length": sum(h["length"] for h in heads) / len(heads) if heads else 0,
            "length_65_75": sum(1 for h in heads if 65 <= h["length"] <= 75)
        },
        "heads": heads
    }

def main():
    """Generate and save breadth candidate bank."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate breadth candidates")
    parser.add_argument("--output", default="experiments/pipeline_v2/data/candidates_breadth.json")
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--limit", type=int, help="Limit number of candidates")
    
    args = parser.parse_args()
    
    # Generate candidates
    bank = generate_breadth_candidates(args.seed)
    
    # Apply limit if specified
    if args.limit:
        bank["heads"] = bank["heads"][:args.limit]
        bank["stats"]["total_heads"] = len(bank["heads"])
    
    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(bank, f, indent=2)
    
    print(f"\nBreadth candidate bank saved to: {output_path}")
    print(f"Total candidates: {bank['stats']['total_heads']}")
    print(f"Length range: {bank['stats']['min_length']}-{bank['stats']['max_length']}")
    print(f"In target range (65-75): {bank['stats']['length_65_75']}")
    print(f"Script hash: {bank['script_hash']}")

if __name__ == "__main__":
    main()