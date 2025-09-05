#!/usr/bin/env python3
"""
Blinding system for Explore lane scorer.
Masks anchor words and narrative lexemes to avoid expectancy effects.
"""

import re
import hashlib
from typing import List, Dict, Set, Tuple

# Anchor words to mask
ANCHOR_WORDS = {"EAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK"}

# Narrative lexemes to mask
NARRATIVE_LEXEMES = {
    "DIAL", "SET", "COURSE", "TRUE", "READ", "SEE", "NOTE", 
    "SIGHT", "OBSERVE", "MERIDIAN", "DECLINATION", "BEARING", "LINE"
}

def compute_mask_hash(words: Set[str]) -> str:
    """Compute SHA-256 hash of mask word list for reproducibility."""
    sorted_words = sorted(words)
    combined = "|".join(sorted_words)
    return hashlib.sha256(combined.encode()).hexdigest()

def blind_text(text: str, blind_anchors: bool = True, blind_narrative: bool = True) -> Tuple[str, Dict]:
    """
    Blind text by replacing anchor/narrative words with <MASK>.
    
    Args:
        text: Input text to blind
        blind_anchors: Whether to mask anchor words
        blind_narrative: Whether to mask narrative lexemes
        
    Returns:
        Tuple of (blinded_text, mask_report)
    """
    mask_report = {
        "original_length": len(text),
        "masked_tokens": [],
        "mask_positions": [],
        "anchor_hash": compute_mask_hash(ANCHOR_WORDS) if blind_anchors else None,
        "narrative_hash": compute_mask_hash(NARRATIVE_LEXEMES) if blind_narrative else None
    }
    
    # Build mask set
    mask_words = set()
    if blind_anchors:
        mask_words.update(ANCHOR_WORDS)
    if blind_narrative:
        mask_words.update(NARRATIVE_LEXEMES)
    
    if not mask_words:
        return text, mask_report
    
    # Create regex pattern for whole word matching
    pattern = r'\b(' + '|'.join(re.escape(word) for word in mask_words) + r')\b'
    
    # Track what we mask
    def replacer(match):
        word = match.group(0)
        start = match.start()
        mask_report["masked_tokens"].append(word)
        mask_report["mask_positions"].append((start, start + len(word)))
        return "<MASK>"
    
    blinded = re.sub(pattern, replacer, text, flags=re.IGNORECASE)
    mask_report["blinded_length"] = len(blinded)
    mask_report["num_masks"] = len(mask_report["masked_tokens"])
    
    return blinded, mask_report

def unblind_text(blinded_text: str, mask_report: Dict) -> str:
    """
    Restore original text from blinded version using mask report.
    
    Args:
        blinded_text: Text with <MASK> placeholders
        mask_report: Report from blind_text()
        
    Returns:
        Original unblinded text
    """
    if not mask_report.get("masked_tokens"):
        return blinded_text
    
    result = blinded_text
    # Replace masks in reverse order to preserve positions
    for i, token in enumerate(reversed(mask_report["masked_tokens"])):
        result = result.replace("<MASK>", token, 1)
    
    return result

def is_narrative_heavy(text: str, threshold: float = 0.15) -> bool:
    """
    Check if text contains too many narrative terms (possible self-confirmation).
    
    Args:
        text: Text to check
        threshold: Max fraction of text that can be narrative
        
    Returns:
        True if narrative-heavy
    """
    words = text.upper().split()
    if not words:
        return False
    
    all_mask_words = ANCHOR_WORDS | NARRATIVE_LEXEMES
    narrative_count = sum(1 for word in words if word in all_mask_words)
    
    return narrative_count / len(words) > threshold

if __name__ == "__main__":
    # Test blinding
    test_text = "WECANSEETHEEASTANDNORTHEASTFROMBERLINCLOCKWHENWESETTHECOURSETRUE"
    
    print("Original text:")
    print(test_text)
    print()
    
    blinded, report = blind_text(test_text)
    print("Blinded text:")
    print(blinded)
    print()
    
    print("Mask report:")
    for key, value in report.items():
        if key != "mask_positions":  # Skip verbose position list
            print(f"  {key}: {value}")
    
    print()
    print("Narrative heavy?", is_narrative_heavy(test_text))
    
    # Test unblinding
    restored = unblind_text(blinded, report)
    print()
    print("Restored text:", restored)
    print("Restoration correct?", restored == test_text)