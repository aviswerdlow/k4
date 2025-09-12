#!/usr/bin/env python3
"""
Content+Function Harmonized Generator for v5.2.1
Generates heads with both semantic content AND sufficient function words.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Function words set - matches production
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

class ContentFunctionGenerator:
    """Generates heads with harmonized content and function words."""
    
    def __init__(self, 
                 templates_path: Path,
                 weights_path: Path,
                 lexicon_path: Optional[Path] = None):
        """Initialize generator with policies."""
        
        # Load templates
        with open(templates_path, 'r') as f:
            self.templates_data = json.load(f)
            self.templates = self.templates_data['templates']
        
        # Load weights
        with open(weights_path, 'r') as f:
            self.weights_data = json.load(f)
            self.weights = self.weights_data['weights']
            self.hard_constraints = self.weights_data['hard_constraints']
            self.soft_constraints = self.weights_data['soft_constraints']
        
        # Load lexicon if provided (for vocabulary substitution)
        if lexicon_path and lexicon_path.exists():
            with open(lexicon_path, 'r') as f:
                self.lexicon = json.load(f)
        else:
            # Default surveying vocabulary
            self.lexicon = {
                "SURVEY_NOUNS": ["MERIDIAN", "DIAL", "BEARING", "COURSE", "LINE", 
                                 "ANGLE", "STATION", "FIELD", "MARK", "GRID",
                                 "ARC", "POINT", "DECLINATION"],
                "ACTION_VERBS": ["SET", "READ", "SIGHT", "NOTE", "OBSERVE", 
                                "FOLLOW", "APPLY", "BRING", "REDUCE", "CORRECT",
                                "TRACE", "FIND", "MARK"],
                "MODIFIERS": ["TRUE", "MAGNETIC", "EXACT", "PRECISE"]
            }
    
    def count_function_words(self, text: str) -> int:
        """Count function words in text."""
        words = text.upper().split()
        return sum(1 for w in words if w in FUNCTION_WORDS)
    
    def count_content_words(self, text: str) -> int:
        """Count content words (non-function words)."""
        words = text.upper().split()
        return sum(1 for w in words if w not in FUNCTION_WORDS)
    
    def calculate_content_ratio(self, text: str) -> float:
        """Calculate ratio of content words to total words."""
        words = text.upper().split()
        if not words:
            return 0.0
        content = sum(1 for w in words if w not in FUNCTION_WORDS)
        return content / len(words)
    
    def has_verb(self, text: str) -> bool:
        """Check if text contains at least one verb."""
        words = text.upper().split()
        all_verbs = set(self.lexicon.get("ACTION_VERBS", []))
        return any(w in all_verbs for w in words)
    
    def check_hard_constraints(self, text: str) -> Tuple[bool, List[str]]:
        """Check if text meets all hard constraints."""
        violations = []
        
        # Length constraint
        if len(text) > self.hard_constraints['length_max']:
            violations.append(f"length {len(text)} > {self.hard_constraints['length_max']}")
        
        # Function words constraint
        f_words = self.count_function_words(text)
        if f_words < self.hard_constraints['f_words_min']:
            violations.append(f"f_words {f_words} < {self.hard_constraints['f_words_min']}")
        
        # Verb constraint
        if self.hard_constraints['has_verb'] and not self.has_verb(text):
            violations.append("no verb found")
        
        # Coverage constraint (mock - would need cipher in production)
        coverage = 0.85 + random.random() * 0.10  # Mock 0.85-0.95
        if coverage < self.hard_constraints['coverage_min']:
            violations.append(f"coverage {coverage:.3f} < {self.hard_constraints['coverage_min']}")
        
        return len(violations) == 0, violations
    
    def score_candidate(self, text: str) -> float:
        """Score candidate using MCMC objective function."""
        
        # Hard constraints must pass
        passes, _ = self.check_hard_constraints(text)
        if not passes:
            return -1000.0  # Reject
        
        score = 0.0
        
        # Function words score (capped)
        f_words = self.count_function_words(text)
        f_words_capped = min(f_words, self.soft_constraints['f_words_cap'])
        score += self.weights['lambda_fw'] * f_words_capped
        
        # N-gram score (mock - would use real model in production)
        ngram_score = 0.7 + random.random() * 0.3  # Mock 0.7-1.0
        score += self.weights['lambda_ng'] * ngram_score
        
        # Pattern score (has AND THEN or similar connective)
        has_pattern = "AND THEN" in text or "TO THE" in text
        score += self.weights['lambda_pat'] * (1.0 if has_pattern else 0.0)
        
        # Content ratio score
        content_ratio = self.calculate_content_ratio(text)
        if content_ratio >= self.soft_constraints['content_ratio_min']:
            score += self.weights['lambda_ctx'] * content_ratio
        
        # Repetition penalty
        words = text.upper().split()
        if words:
            max_repeat = max(words.count(w) for w in set(words))
            if max_repeat > self.soft_constraints['repetition_max']:
                score += self.weights['lambda_run'] * (max_repeat - self.soft_constraints['repetition_max'])
        
        return score
    
    def generate_from_template(self, template: Dict) -> str:
        """Generate a head from a template with vocabulary substitution."""
        
        pattern = template['pattern']
        
        # Substitute vocabulary while preserving structure
        # This is simplified - production would have more sophisticated substitution
        text = pattern
        
        # Randomly substitute some nouns
        if random.random() > 0.5:
            nouns = self.lexicon.get("SURVEY_NOUNS", [])
            for noun in ["MERIDIAN", "DIAL", "BEARING", "COURSE", "LINE", "ANGLE"]:
                if noun in text and random.random() > 0.6:
                    replacement = random.choice([n for n in nouns if n != noun])
                    text = text.replace(noun, replacement, 1)
        
        # Ensure TRUE appears if it's a declination template
        if "true" in template.get("category", "").lower() and "TRUE" not in text:
            text = text.replace("MERIDIAN", "TRUE MERIDIAN", 1)
        
        return text[:74]  # Ensure within head window
    
    def generate_candidates(self, n_candidates: int, seed: int) -> List[Dict]:
        """Generate n candidates with harmonized content and function words."""
        
        random.seed(seed)
        candidates = []
        
        # Filter templates to those with sufficient function words
        valid_templates = [t for t in self.templates if t.get('f_words', 0) >= 8]
        
        attempts = 0
        max_attempts = n_candidates * 10
        
        while len(candidates) < n_candidates and attempts < max_attempts:
            attempts += 1
            
            # Select template
            template = random.choice(valid_templates)
            
            # Generate from template
            text = self.generate_from_template(template)
            
            # Check constraints
            passes, violations = self.check_hard_constraints(text)
            if not passes:
                continue
            
            # Score candidate
            score = self.score_candidate(text)
            if score < 0:
                continue
            
            # Create candidate record
            candidate = {
                "text": text,
                "template_id": template['id'],
                "f_words": self.count_function_words(text),
                "content_ratio": self.calculate_content_ratio(text),
                "has_verb": self.has_verb(text),
                "length": len(text),
                "score": score,
                "has_true": "TRUE" in text.upper()
            }
            
            candidates.append(candidate)
        
        return candidates

def main():
    """Test the generator."""
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    templates_path = base_dir / "policies" / "templates.json"
    weights_path = base_dir / "policies" / "weights.v5_2_1.json"
    
    # Initialize generator
    generator = ContentFunctionGenerator(templates_path, weights_path)
    
    # Generate test candidates
    print("Generating test candidates with content+function harmonization...")
    print("=" * 70)
    
    candidates = generator.generate_candidates(n_candidates=10, seed=1337)
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\nCandidate {i}:")
        print(f"Text: {candidate['text']}")
        print(f"Length: {candidate['length']}")
        print(f"F-words: {candidate['f_words']}")
        print(f"Content ratio: {candidate['content_ratio']:.2%}")
        print(f"Has TRUE: {candidate['has_true']}")
        print(f"Score: {candidate['score']:.3f}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"Generated: {len(candidates)}/10 candidates")
    print(f"Avg f-words: {sum(c['f_words'] for c in candidates) / len(candidates):.1f}")
    print(f"With TRUE: {sum(1 for c in candidates if c['has_true'])}")
    print(f"All pass f_words >= 8: {all(c['f_words'] >= 8 for c in candidates)}")

if __name__ == "__main__":
    main()