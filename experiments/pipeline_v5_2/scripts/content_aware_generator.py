#!/usr/bin/env python3
"""
Content-Aware Generator for v5.2
Enforces semantic content during generation, not just post-hoc.
"""

import json
import random
import re
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
import hashlib

class ContentAwareGenerator:
    """
    Generate heads with actual semantic content using surveying vocabulary.
    Enforces content constraints during generation.
    """
    
    def __init__(self, lexicon_path: Path, weights_path: Path):
        """Initialize with lexicon and weights."""
        
        # Load lexicon
        with open(lexicon_path, 'r') as f:
            self.lexicon = json.load(f)
        
        # Load weights
        with open(weights_path, 'r') as f:
            self.weights = json.load(f)
        
        # Build vocabulary sets
        self.content_words = set()
        self.content_words.update(self.lexicon["SURVEY_NOUNS"])
        self.content_words.update(self.lexicon["ACTION_VERBS"])
        self.content_words.update(self.lexicon["RELATORS"])
        self.content_words.update(self.lexicon["MEASURE_TERMS"])
        
        self.function_words = {
            'THE', 'A', 'AN', 'AND', 'THEN', 'THAT', 'THIS', 'THESE', 'THOSE',
            'IS', 'ARE', 'WAS', 'WERE', 'BE', 'BEEN', 'BEING',
            'HAVE', 'HAS', 'HAD', 'DO', 'DOES', 'DID',
            'WILL', 'WOULD', 'COULD', 'SHOULD', 'MAY', 'MIGHT',
            'TO', 'OF', 'IN', 'ON', 'AT', 'BY', 'FOR', 'WITH', 'FROM',
            'BUT', 'OR', 'IF', 'BECAUSE', 'AS', 'UNTIL', 'WHILE'
        }
        
        # Templates with content placeholders
        self.templates = [
            "SET THE {NOUN1} TO {MEASURE} {NOUN2} THEN READ THE {NOUN3}",
            "SIGHT THE {NOUN1} THEN NOTE THE {NOUN2}",
            "APPLY {MEASURE} THEN READ {NOUN1}",
            "TRACE THE {NOUN1} THEN SET THE {NOUN2}",
            "FOLLOW THE {NOUN1} {RELATOR} THE {NOUN2} THEN READ THE {NOUN3}",
            "MARK THE {NOUN1} THEN ADJUST THE {NOUN2}",
            "OBSERVE THE {NOUN1} THEN REDUCE THE {NOUN2} TO {MEASURE}",
            "{VERB1} THE {NOUN1} {RELATOR} {MEASURE} {NOUN2}",
            "NOTE THE {NOUN1} AT THE {NOUN2} THEN {VERB1}",
            "BRING THE {NOUN1} TO {NOUN2} THEN {VERB1} THE {NOUN3}"
        ]
        
    def generate_from_template(self, template: str, seed: int) -> str:
        """Generate a head by filling a template with content words."""
        
        rng = random.Random(seed)
        
        # Extract placeholders
        placeholders = re.findall(r'\{(\w+)\}', template)
        
        # Create substitutions
        subs = {}
        noun_count = 0
        verb_count = 0
        
        for placeholder in placeholders:
            if placeholder.startswith("NOUN"):
                # Pick a survey noun
                noun = rng.choice(self.lexicon["SURVEY_NOUNS"])
                subs[placeholder] = noun
                noun_count += 1
            elif placeholder.startswith("VERB"):
                # Pick an action verb
                verb = rng.choice(self.lexicon["ACTION_VERBS"])
                subs[placeholder] = verb
                verb_count += 1
            elif placeholder == "MEASURE":
                # Pick a measure term
                measure = rng.choice(self.lexicon["MEASURE_TERMS"])
                subs[placeholder] = measure
            elif placeholder == "RELATOR":
                # Pick a relator
                relator = rng.choice(self.lexicon["RELATORS"])
                subs[placeholder] = relator
        
        # Apply substitutions
        result = template
        for placeholder, value in subs.items():
            result = result.replace(f"{{{placeholder}}}", value)
        
        return result
    
    def check_content_ratio(self, text: str) -> float:
        """Calculate content word ratio."""
        
        words = text.split()
        if not words:
            return 0.0
        
        content_count = sum(1 for w in words if w.upper() in self.content_words)
        return content_count / len(words)
    
    def check_consecutive_functions(self, text: str) -> bool:
        """Check if text has 3+ consecutive function words."""
        
        words = text.split()
        consec_count = 0
        
        for word in words:
            if word.upper() in self.function_words:
                consec_count += 1
                if consec_count >= 3:
                    return False  # Fails constraint
            else:
                consec_count = 0
        
        return True  # Passes constraint
    
    def check_repetition(self, text: str) -> bool:
        """Check for repeated bigrams like 'the the'."""
        
        words = text.lower().split()
        
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and words[i] in ['the', 'and', 'then', 'a', 'an']:
                return False  # Has repetition
        
        return True  # No repetition
    
    def count_noun_phrases(self, text: str) -> int:
        """Simple heuristic for counting noun phrases."""
        
        # Pattern: (DET)? (ADJ)* NOUN
        # Simplified: count content nouns preceded by THE/A/AN
        
        words = text.split()
        np_count = 0
        
        for i in range(len(words) - 1):
            if words[i].upper() in ['THE', 'A', 'AN']:
                if words[i + 1].upper() in self.lexicon["SURVEY_NOUNS"]:
                    np_count += 1
        
        return np_count
    
    def count_unique_content_types(self, text: str) -> int:
        """Count unique content word types."""
        
        words = text.split()
        content_types = set()
        
        for word in words:
            word_upper = word.upper()
            if word_upper in self.content_words:
                content_types.add(word_upper)
        
        return len(content_types)
    
    def validate_constraints(self, text: str) -> Dict[str, bool]:
        """Check all content constraints."""
        
        return {
            "content_ratio": self.check_content_ratio(text) >= 0.35,
            "np_count": self.count_noun_phrases(text) >= 2,
            "unique_content_types": self.count_unique_content_types(text) >= 3,
            "no_function_run": self.check_consecutive_functions(text),
            "repetition_penalty": self.check_repetition(text)
        }
    
    def generate_head(self, seed: int, max_attempts: int = 100) -> Optional[str]:
        """
        Generate a head that meets all content constraints.
        Returns None if constraints cannot be met.
        """
        
        rng = random.Random(seed)
        
        for attempt in range(max_attempts):
            # Pick a template
            template = rng.choice(self.templates)
            
            # Generate from template
            attempt_seed = seed + attempt
            head = self.generate_from_template(template, attempt_seed)
            
            # Validate constraints
            constraints = self.validate_constraints(head)
            
            if all(constraints.values()):
                # Truncate to 74 chars if needed
                if len(head) > 74:
                    head = head[:74].rstrip()
                    # Re-validate after truncation
                    constraints = self.validate_constraints(head)
                    if all(constraints.values()):
                        return head
                else:
                    # Pad if too short
                    while len(head) < 60:
                        # Add a simple instruction
                        additions = [
                            " THEN NOTE",
                            " AND READ",
                            " THEN MARK",
                            " AT STATION"
                        ]
                        add = rng.choice(additions)
                        if len(head) + len(add) <= 74:
                            head += add
                    
                    return head
        
        return None  # Could not generate valid head
    
    def generate_batch(self, count: int, base_seed: int) -> List[Dict[str, any]]:
        """Generate a batch of heads with metadata."""
        
        results = []
        
        for i in range(count):
            seed = base_seed + i * 1000
            head = self.generate_head(seed)
            
            if head:
                # Calculate metrics
                metrics = {
                    "label": f"HEAD_{i:03d}_v52",
                    "head": head,
                    "seed": seed,
                    "content_ratio": self.check_content_ratio(head),
                    "np_count": self.count_noun_phrases(head),
                    "unique_content_types": self.count_unique_content_types(head),
                    "passes_constraints": True,
                    "head_sha256": hashlib.sha256(head.encode()).hexdigest()
                }
                results.append(metrics)
            else:
                # Failed to generate valid head
                results.append({
                    "label": f"HEAD_{i:03d}_v52",
                    "head": None,
                    "seed": seed,
                    "passes_constraints": False,
                    "error": "Could not generate valid head"
                })
        
        return results


def main():
    """Test the generator."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Content-aware head generator")
    parser.add_argument("--lexicon", required=True, help="Path to lexicon JSON")
    parser.add_argument("--weights", required=True, help="Path to weights JSON")
    parser.add_argument("--count", type=int, default=10, help="Number to generate")
    parser.add_argument("--seed", type=int, default=1337, help="Base seed")
    parser.add_argument("--out", help="Output JSON file")
    
    args = parser.parse_args()
    
    # Initialize generator
    gen = ContentAwareGenerator(
        lexicon_path=Path(args.lexicon),
        weights_path=Path(args.weights)
    )
    
    # Generate batch
    print(f"Generating {args.count} content-aware heads...")
    results = gen.generate_batch(args.count, args.seed)
    
    # Print samples
    print("\nSample heads:")
    for i, result in enumerate(results[:5]):
        if result["passes_constraints"]:
            print(f"{i+1}. {result['head']}")
            print(f"   Content ratio: {result['content_ratio']:.2f}")
            print(f"   Noun phrases: {result['np_count']}")
            print(f"   Unique types: {result['unique_content_types']}")
        else:
            print(f"{i+1}. FAILED: {result.get('error', 'Unknown error')}")
    
    # Statistics
    passed = sum(1 for r in results if r["passes_constraints"])
    print(f"\nGeneration success rate: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    
    if passed > 0:
        avg_content = sum(r["content_ratio"] for r in results if r["passes_constraints"]) / passed
        avg_np = sum(r["np_count"] for r in results if r["passes_constraints"]) / passed
        print(f"Average content ratio: {avg_content:.2f}")
        print(f"Average noun phrases: {avg_np:.1f}")
    
    # Save if requested
    if args.out:
        with open(args.out, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.out}")

if __name__ == "__main__":
    main()