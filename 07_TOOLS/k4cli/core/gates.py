"""Phrase gate validation for K4 Kryptos."""

import json
import re
from typing import Dict, List, Optional, Tuple
from .io import read_json


def validate_near_gate(plaintext: str, function_words: List[str], 
                      coverage_threshold: float = 0.8, min_f_words: int = 6) -> Dict:
    """Validate near-gate requirements."""
    # Tokenize plaintext 
    words = re.findall(r'[A-Z]+', plaintext)
    total_chars = sum(len(word) for word in words)
    
    # Count function words
    f_word_count = sum(1 for word in words if word in function_words)
    
    # Calculate coverage (simplified)
    coverage = len(plaintext) / 97.0  # Approximate
    
    # Check for verb presence (simplified)
    verbs = ["READ", "SEE", "SET", "NOTE", "SIGHT", "OBSERVE"]
    has_verb = any(verb in plaintext for verb in verbs)
    
    result = {
        "coverage": coverage,
        "function_words": f_word_count,
        "has_verb": has_verb,
        "passed": coverage >= coverage_threshold and f_word_count >= min_f_words and has_verb
    }
    
    return result


def validate_flint_v2(plaintext: str, policy: Dict) -> Dict:
    """Validate Flint v2 track requirements."""
    flint_config = policy["phrase_gate"]["flint_v2"]
    
    # Check for declination patterns
    declination_patterns = [
        "SET COURSE TRUE", "CORRECT BEARING TRUE", 
        "REDUCE COURSE TRUE", "APPLY DECLINATION", "BRING TRUE MERIDIAN"
    ]
    declination_found = any(pattern in plaintext for pattern in declination_patterns)
    declination_type = next((pattern for pattern in declination_patterns if pattern in plaintext), None)
    
    # Check instrument verbs
    instrument_verbs = flint_config["instrument_verbs"]
    verb_found = any(verb in plaintext for verb in instrument_verbs)
    found_verb = next((verb for verb in instrument_verbs if verb in plaintext), None)
    
    # Check direction tokens
    directions = flint_config["directions"]
    found_directions = [direction for direction in directions if direction in plaintext]
    
    # Check instrument nouns
    instrument_nouns = flint_config["instrument_nouns"]  
    noun_found = any(noun in plaintext for noun in instrument_nouns)
    found_noun = next((noun for noun in instrument_nouns if noun in plaintext), None)
    
    # Content word count (simplified)
    words = re.findall(r'[A-Z]+', plaintext)
    content_words = len([w for w in words if len(w) > 2])  # Simplified
    
    # Max repeat check (simplified)
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    max_repeat = max(word_counts.values()) if word_counts else 0
    
    result = {
        "declination_found": declination_found,
        "declination_type": declination_type,
        "instrument_verb_found": verb_found,
        "instrument_verb": found_verb,
        "direction_tokens": found_directions,
        "instrument_noun_found": noun_found,
        "instrument_noun": found_noun,
        "content_words": content_words,
        "max_repeat_non_anchor": max_repeat,
        "passed": all([declination_found, verb_found, len(found_directions) > 0, 
                      noun_found, content_words >= flint_config["min_content"]])
    }
    
    return result


def validate_generic_track(plaintext: str, policy: Dict, 
                          perplexity_percentile: float, pos_score: float) -> Dict:
    """Validate Generic track requirements."""
    generic_config = policy["phrase_gate"]["generic"]
    
    # Content word count
    words = re.findall(r'[A-Z]+', plaintext)
    content_words = len([w for w in words if len(w) > 2])  # Simplified
    
    # Max repeat check
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    max_repeat = max(word_counts.values()) if word_counts else 0
    
    # Validate thresholds
    perp_passed = perplexity_percentile <= generic_config["percentile_top"]
    pos_passed = pos_score >= generic_config["pos_threshold"]
    content_passed = content_words >= generic_config["min_content"]
    repeat_passed = max_repeat <= generic_config["max_repeat"]
    
    result = {
        "perplexity_percentile": perplexity_percentile,
        "pos_score": pos_score,
        "content_words": content_words,
        "max_repeat_non_anchor": max_repeat,
        "passed": all([perp_passed, pos_passed, content_passed, repeat_passed])
    }
    
    return result


def validate_phrase_gate_and(plaintext: str, policy: Dict, function_words: List[str],
                            perplexity_percentile: float, pos_score: float) -> Dict:
    """Validate AND phrase gate (both Flint v2 AND Generic must pass)."""
    
    # Validate both tracks
    flint_result = validate_flint_v2(plaintext, policy)
    generic_result = validate_generic_track(plaintext, policy, perplexity_percentile, pos_score)
    
    # AND logic - both must pass
    accepted_by = []
    if flint_result["passed"]:
        accepted_by.append("flint_v2")
    if generic_result["passed"]:
        accepted_by.append("generic")
    
    and_passed = len(accepted_by) == 2  # Both tracks required
    
    result = {
        "flint_v2": flint_result,
        "generic": generic_result,
        "accepted_by": accepted_by,
        "passed": and_passed
    }
    
    return result