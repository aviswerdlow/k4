#!/usr/bin/env python3
"""
Function Glue Augmenter for v5.2.1
Inserts function-rich phrases at low-saliency positions when f_words < 8.
"""

import re
from typing import List, Tuple, Optional

# Function words set
FUNCTION_WORDS = {
    'THE', 'OF', 'AND', 'TO', 'IN', 'IS', 'ARE', 'WAS',
    'THEN', 'THERE', 'HERE', 'WITH', 'AT', 'BY', 'WE'
}

# Glue phrases (all contain 2+ function words)
GLUE_PHRASES = [
    "OF THE",    # 2 function words
    "TO THE",    # 2 function words
    "IN THE",    # 2 function words
    "AND THEN",  # 2 function words
    "AND WE",    # 2 function words
    "BY THE",    # 2 function words
    "AT THE"     # 2 function words
]

class FunctionGlueAugmenter:
    """Augments heads with function-rich glue phrases."""
    
    def __init__(self, max_insertions: int = 2, max_length: int = 74):
        self.max_insertions = max_insertions
        self.max_length = max_length
    
    def count_function_words(self, text: str) -> int:
        """Count function words in text."""
        words = text.upper().split()
        return sum(1 for w in words if w in FUNCTION_WORDS)
    
    def find_low_saliency_positions(self, text: str) -> List[Tuple[int, str]]:
        """Find positions where glue can be inserted without disrupting meaning."""
        
        positions = []
        words = text.split()
        
        # Position 1: After first noun (typically position 2-3)
        if len(words) >= 3:
            # Look for pattern: VERB NOUN ...
            if words[0].upper() not in FUNCTION_WORDS:  # Likely a verb
                if words[1].upper() not in FUNCTION_WORDS:  # Likely a noun
                    positions.append((2, "after_first_noun"))
        
        # Position 2: Before AND (if exists)
        for i, word in enumerate(words):
            if word.upper() == "AND" and i > 0:
                positions.append((i, "before_and"))
                break
        
        # Position 3: After second verb (common in templates)
        verb_count = 0
        for i, word in enumerate(words):
            if word.upper() not in FUNCTION_WORDS and i > 0:
                # Simple heuristic: non-function word after function word might be verb
                if i > 0 and words[i-1].upper() in FUNCTION_WORDS:
                    verb_count += 1
                    if verb_count == 2:
                        positions.append((i+1, "after_second_verb"))
                        break
        
        # Position 4: Before final noun phrase
        if len(words) >= 4:
            # If last 2-3 words contain THE + noun
            if words[-2].upper() == "THE":
                positions.append((len(words)-2, "before_final_noun"))
        
        return positions
    
    def select_glue_phrase(self, position_type: str, existing_text: str) -> Optional[str]:
        """Select appropriate glue phrase for position."""
        
        # Avoid duplication
        existing_upper = existing_text.upper()
        
        # Priority based on position type
        if position_type == "after_first_noun":
            # Prefer prepositional phrases
            for phrase in ["TO THE", "OF THE", "IN THE"]:
                if phrase not in existing_upper:
                    return phrase
        
        elif position_type == "before_and":
            # Only use if doesn't create "AND AND THEN"
            if "AND THEN" not in existing_upper:
                return None  # Don't add before existing AND
        
        elif position_type == "after_second_verb":
            # Prefer directional phrases
            for phrase in ["TO THE", "AT THE", "IN THE"]:
                if phrase not in existing_upper:
                    return phrase
        
        elif position_type == "before_final_noun":
            # Prefer specifying phrases
            for phrase in ["OF THE", "AT THE", "BY THE"]:
                if phrase not in existing_upper:
                    return phrase
        
        # Fallback: any phrase not already in text
        for phrase in GLUE_PHRASES:
            if phrase not in existing_upper:
                return phrase
        
        return None
    
    def insert_glue(self, text: str, position: int, glue: str) -> str:
        """Insert glue phrase at word position."""
        
        words = text.split()
        
        # Insert at position
        if position <= len(words):
            words.insert(position, glue)
        
        result = " ".join(words)
        
        # Ensure doesn't exceed max length
        if len(result) > self.max_length:
            # Try removing trailing words to fit
            while len(result) > self.max_length and len(words) > position + 2:
                words.pop()
                result = " ".join(words)
        
        return result[:self.max_length]
    
    def augment(self, text: str, target_f_words: int = 8) -> Tuple[str, int, List[str]]:
        """
        Augment text with function glue if needed.
        
        Returns:
            Tuple of (augmented_text, insertions_made, insertion_descriptions)
        """
        
        # Check current function word count
        current_f_words = self.count_function_words(text)
        
        if current_f_words >= target_f_words:
            return text, 0, []
        
        # Find insertion positions
        positions = self.find_low_saliency_positions(text)
        
        if not positions:
            return text, 0, []
        
        # Track insertions
        insertions_made = 0
        insertion_log = []
        augmented = text
        
        for word_pos, pos_type in positions:
            if insertions_made >= self.max_insertions:
                break
            
            if self.count_function_words(augmented) >= target_f_words:
                break
            
            # Select glue phrase
            glue = self.select_glue_phrase(pos_type, augmented)
            
            if glue:
                # Insert glue
                new_text = self.insert_glue(augmented, word_pos + insertions_made, glue)
                
                # Verify improvement
                new_f_words = self.count_function_words(new_text)
                if new_f_words > self.count_function_words(augmented):
                    augmented = new_text
                    insertions_made += 1
                    insertion_log.append(f"{glue} at {pos_type}")
        
        return augmented, insertions_made, insertion_log

def test_augmenter():
    """Test the function glue augmenter."""
    
    augmenter = FunctionGlueAugmenter()
    
    test_cases = [
        "FOLLOW DIAL TOWARD MERIDIAN READ COURSE READ",  # 0 function words
        "SET LINE MERIDIAN READ DIAL",  # 0 function words
        "FOLLOW THE DIAL TOWARD MERIDIAN THEN READ COURSE",  # 3 function words
        "READ DIAL AND NOTE ANGLE FIELD",  # 1 function word
        "SIGHT MARK THEN READ LINE MERIDIAN"  # 1 function word
    ]
    
    print("Function Glue Augmenter Tests")
    print("=" * 70)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {text}")
        print(f"F-words: {augmenter.count_function_words(text)}")
        
        augmented, insertions, log = augmenter.augment(text)
        
        print(f"Augmented: {augmented}")
        print(f"F-words: {augmenter.count_function_words(augmented)}")
        print(f"Insertions: {insertions}")
        if log:
            print(f"Details: {', '.join(log)}")
    
    print("\n" + "=" * 70)
    print("Augmenter test complete.")

if __name__ == "__main__":
    test_augmenter()