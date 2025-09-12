#!/usr/bin/env python3
"""Debug tokenization and gate evaluation"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from flint_fuzzy import tokenize_v2, evaluate_and_gate

# Load data
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "canonical_cuts.json") as f:
    cuts_data = json.load(f)
    canonical_cuts = cuts_data["cuts_inclusive_0idx"]

# Test plaintext
plaintext = "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
head = plaintext[:75]

print(f"Head text: {head}")
print(f"Canonical cuts: {canonical_cuts}")

# Test tokenization
tokens = tokenize_v2(head, canonical_cuts, head_end=75)
print(f"Tokens: {tokens}")
print(f"Token count: {len(tokens)}")

# Test AND gate
result = evaluate_and_gate(plaintext, canonical_cuts, fuzzy=False)
print(f"\nStrict AND gate result:")
print(f"  Flint pass: {result['flint']['pass']}")
print(f"  Flint domain score: {result['flint']['domain_score']}")
print(f"  Flint matches: {result['flint']['matches']}")
print(f"  Generic pass: {result['generic']['pass']}")
print(f"  Generic details: perp={result['generic']['perplexity_percentile']:.1f}%, pos={result['generic']['pos_score']:.3f}")
print(f"  AND pass: {result['pass']}")

# Test fuzzy
result_fuzzy = evaluate_and_gate(plaintext, canonical_cuts, fuzzy=True, levenshtein_max=1, orth_map={"U":"V","V":"U"})
print(f"\nFuzzy AND gate result:")
print(f"  Flint pass: {result_fuzzy['flint']['pass']}")
print(f"  Flint domain score: {result_fuzzy['flint']['domain_score']}")
print(f"  Flint matches: {result_fuzzy['flint']['matches']}")
print(f"  Fuzzy matches: {result_fuzzy['flint']['matches']['fuzzy_matches']}")
print(f"  Generic pass: {result_fuzzy['generic']['pass']}")
print(f"  AND pass: {result_fuzzy['pass']}")