#!/usr/bin/env python3
"""Rank candidates by cadence (style) metrics.

Reads plaintext catalog and computes cadence scores for v5 gate.
"""

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


# K2 declarative bootstrap thresholds (P5/P95 bounds)
CADENCE_THRESHOLDS = {
    "cosine_bigram": {"min": 0.65, "type": "min"},
    "cosine_trigram": {"min": 0.60, "type": "min"},
    "fw_gap_mean": {"min": 2.8, "max": 5.2, "type": "range"},
    "fw_gap_cv": {"min": 0.4, "max": 1.2, "type": "range"},
    "wordlen_chi2": {"max": 95.0, "type": "max"},
    "vc_ratio": {"min": 0.95, "max": 1.15, "type": "range"}
}

# Function words for rhythm analysis
FUNCTION_WORDS = {
    "THE", "AND", "AS", "THAT", "BE", "WITH", "ON", "THEN", 
    "THERE", "OUR", "YOUR", "WHERE", "THEM", "THIS", "A", 
    "AN", "IN", "OF", "TO", "FOR", "BUT", "BY", "IS", "IT"
}


def tokenize_v2(text: str) -> List[str]:
    """Tokenize head window using v2 method."""
    # Simplified tokenizer - would use proper dictionary in production
    words = []
    text = text.upper()
    
    # Common words to extract (expanded vocabulary)
    vocab = [
        "THE", "AND", "THAT", "THIS", "THESE", "THOSE", "THERE", "THEN",
        "WHEN", "WHERE", "WHICH", "WHAT", "WHO", "WHOM", "WITH", "WITHIN",
        "READ", "FOLLOW", "BERLIN", "CLOCK", "EAST", "NORTHEAST", "SOUTHEAST",
        "NORTHWEST", "SOUTHWEST", "WEST", "NORTH", "SOUTH", "DIRECTION",
        "COURSE", "TRUE", "SET", "COORDINATES", "NAVIGATE", "COMPASS",
        "ON", "OFF", "IN", "OUT", "UP", "DOWN", "OVER", "UNDER", "THROUGH",
        "BE", "IS", "ARE", "WAS", "WERE", "BEEN", "BEING", "HAVE", "HAS",
        "HAD", "DO", "DOES", "DID", "WILL", "WOULD", "COULD", "SHOULD",
        "CAN", "MAY", "MIGHT", "MUST", "SHALL", "OUR", "YOUR", "THEIR",
        "HE", "SHE", "HIM", "HER", "HIS", "HERS", "THEM", "THEY", "WE",
        "AS", "BUT", "OR", "IF", "BECAUSE", "WHILE", "ALTHOUGH", "SINCE"
    ]
    
    # Sort by length descending for greedy matching
    vocab_sorted = sorted(set(vocab), key=len, reverse=True)
    
    i = 0
    while i < len(text):
        matched = False
        for word in vocab_sorted:
            if text[i:i+len(word)] == word:
                words.append(word)
                i += len(word)
                matched = True
                break
        if not matched:
            # Single char as unknown token
            if text[i].isalpha():
                words.append(text[i])
            i += 1
    
    return words


def compute_cosine_similarity(text_bigrams: Counter, ref_bigrams: Counter) -> float:
    """Compute cosine similarity between bigram distributions."""
    # Simplified - would use actual K2 reference in production
    common = set(text_bigrams.keys()) & set(ref_bigrams.keys())
    if not common:
        return 0.0
    
    numerator = sum(text_bigrams[k] * ref_bigrams.get(k, 0) for k in common)
    sum1 = sum(v**2 for v in text_bigrams.values())
    sum2 = sum(v**2 for v in ref_bigrams.values())
    
    if sum1 == 0 or sum2 == 0:
        return 0.0
    
    return numerator / (math.sqrt(sum1) * math.sqrt(sum2))


def compute_cadence_metrics(plaintext: str) -> Dict:
    """Compute all cadence metrics for head window."""
    # Extract head window (0:74)
    head = plaintext[:74] if len(plaintext) >= 74 else plaintext
    words = tokenize_v2(head)
    
    if not words:
        return {
            "cosine_bigram": 0.0,
            "cosine_trigram": 0.0,
            "fw_gap_mean": 0.0,
            "fw_gap_cv": 0.0,
            "wordlen_chi2": 999.0,
            "vc_ratio": 0.0,
            "passed_metrics": 0,
            "cadence_pass": False
        }
    
    # Bigram/trigram analysis
    bigrams = Counter(zip(words[:-1], words[1:]))
    trigrams = Counter(zip(words[:-2], words[1:-1], words[2:]))
    
    # Mock K2 reference distributions (would load actual in production)
    k2_bigrams = Counter({
        ("THE", "AND"): 5, ("AND", "THE"): 4, ("IN", "THE"): 3,
        ("OF", "THE"): 4, ("TO", "THE"): 3, ("WITH", "THE"): 2
    })
    k2_trigrams = Counter({
        ("IN", "THE", "AND"): 2, ("THE", "AND", "THE"): 1
    })
    
    cosine_bigram = compute_cosine_similarity(bigrams, k2_bigrams)
    cosine_trigram = compute_cosine_similarity(trigrams, k2_trigrams)
    
    # Function word gaps
    fw_positions = [i for i, w in enumerate(words) if w in FUNCTION_WORDS]
    if len(fw_positions) > 1:
        gaps = [fw_positions[i+1] - fw_positions[i] for i in range(len(fw_positions)-1)]
        fw_gap_mean = sum(gaps) / len(gaps)
        fw_gap_std = math.sqrt(sum((g - fw_gap_mean)**2 for g in gaps) / len(gaps))
        fw_gap_cv = fw_gap_std / fw_gap_mean if fw_gap_mean > 0 else 0
    else:
        fw_gap_mean = 0.0
        fw_gap_cv = 0.0
    
    # Word length chi-square
    word_lengths = [len(w) for w in words]
    if word_lengths:
        expected_mean = 4.5  # English average
        observed_mean = sum(word_lengths) / len(word_lengths)
        wordlen_chi2 = sum((wl - expected_mean)**2 / expected_mean for wl in word_lengths)
    else:
        wordlen_chi2 = 999.0
    
    # Vowel-consonant ratio
    vowels = sum(1 for c in head if c in "AEIOU")
    consonants = sum(1 for c in head if c.isalpha() and c not in "AEIOU")
    vc_ratio = vowels / consonants if consonants > 0 else 0.0
    
    # Check thresholds
    passed = 0
    
    if cosine_bigram >= CADENCE_THRESHOLDS["cosine_bigram"]["min"]:
        passed += 1
    
    if cosine_trigram >= CADENCE_THRESHOLDS["cosine_trigram"]["min"]:
        passed += 1
    
    if (CADENCE_THRESHOLDS["fw_gap_mean"]["min"] <= fw_gap_mean <= 
        CADENCE_THRESHOLDS["fw_gap_mean"]["max"]):
        passed += 1
    
    if (CADENCE_THRESHOLDS["fw_gap_cv"]["min"] <= fw_gap_cv <= 
        CADENCE_THRESHOLDS["fw_gap_cv"]["max"]):
        passed += 1
    
    if wordlen_chi2 <= CADENCE_THRESHOLDS["wordlen_chi2"]["max"]:
        passed += 1
    
    if (CADENCE_THRESHOLDS["vc_ratio"]["min"] <= vc_ratio <= 
        CADENCE_THRESHOLDS["vc_ratio"]["max"]):
        passed += 1
    
    return {
        "cosine_bigram": round(cosine_bigram, 3),
        "cosine_trigram": round(cosine_trigram, 3),
        "fw_gap_mean": round(fw_gap_mean, 2),
        "fw_gap_cv": round(fw_gap_cv, 2),
        "wordlen_chi2": round(wordlen_chi2, 1),
        "vc_ratio": round(vc_ratio, 3),
        "passed_metrics": passed,
        "cadence_pass": passed == 6  # All six must pass
    }


def main():
    """Rank candidates by cadence metrics."""
    
    # Paths
    catalog_path = Path("experiments/pipeline_v4/runs/v4_1_1/k200/PLAINTEXT_CATALOG.csv")
    output_path = Path("experiments/pipeline_v5/runs/k200_v5/CADENCE_RANK.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load plaintext catalog
    print("Loading plaintext catalog...")
    candidates = []
    
    with open(catalog_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip if no plaintext (not lawful)
            if not row.get("plaintext_97"):
                continue
            
            # Compute cadence metrics
            metrics = compute_cadence_metrics(row["plaintext_97"])
            
            candidate = {
                "label": row["label"],
                "seed_u64": row["seed_u64"],
                "route_id": row["route_id"],
                "coverage": float(row["coverage"]) if row["coverage"] else 0.0,
                "f_words": int(row["f_words"]) if row["f_words"] else 0,
                **metrics
            }
            candidates.append(candidate)
    
    print(f"  Loaded {len(candidates)} lawful candidates")
    
    # Sort by cadence score (passed metrics), then by cosine_trigram
    candidates.sort(key=lambda x: (-x["passed_metrics"], -x["cosine_trigram"]))
    
    # Write ranked output
    print(f"Writing cadence rankings to {output_path}")
    
    with open(output_path, 'w', newline='') as f:
        fieldnames = [
            "rank", "label", "seed_u64", "route_id", "coverage", "f_words",
            "cosine_bigram", "cosine_trigram", "fw_gap_mean", "fw_gap_cv",
            "wordlen_chi2", "vc_ratio", "passed_metrics", "cadence_pass"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, candidate in enumerate(candidates, 1):
            candidate["rank"] = i
            writer.writerow(candidate)
    
    # Summary
    passers = [c for c in candidates if c["cadence_pass"]]
    print(f"\n✅ Cadence Ranking Complete")
    print(f"  Total lawful candidates: {len(candidates)}")
    print(f"  Cadence passers: {len(passers)}")
    print(f"  Output: {output_path}")
    
    if passers:
        print(f"\nTop cadence passers:")
        for c in passers[:5]:
            print(f"  {c['label']}: {c['passed_metrics']}/6 metrics passed")
    else:
        print("\n⚠️  No candidates pass all cadence requirements!")
        if candidates:
            print(f"\nBest candidate: {candidates[0]['label']} with {candidates[0]['passed_metrics']}/6 metrics")


if __name__ == "__main__":
    main()