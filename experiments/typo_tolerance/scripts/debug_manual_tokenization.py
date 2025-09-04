#!/usr/bin/env python3
"""Manual tokenization debug to understand the expected tokens"""

# Expected tokens from the winner plaintext head
plaintext = "WECANSEETHETEXTISCODEEASTNORTHEASTWESETTHECOURSETRUEREADTHENSEEBERLINCLOCKTHEJOYOFANANGLEISTHEARC"
head = plaintext[:75]
print(f"Head (75 chars): {head}")

# Based on our knowledge of K4 winner content, the tokens should be:
expected_tokens = [
    "WE", "CAN", "SEE", "THE", "TEXT", "IS", "CODE", "EAST", "NORTHEAST", 
    "WE", "SET", "THE", "COURSE", "TRUE", "READ", "THEN", "SEE", "BERLIN", "CLOCK"
]

print(f"Expected tokens: {expected_tokens}")
print(f"Expected token count: {len(expected_tokens)}")

# Let's manually verify these contain Flint vocabulary:
directions = ["EAST", "NORTHEAST"]
instrument_verbs = ["READ", "SEE", "NOTE", "SIGHT", "OBSERVE"] 
instrument_nouns = ["BERLIN", "CLOCK", "BERLINCLOCK", "DIAL"]
declination_scaffolds = ["SET", "COURSE", "TRUE", "MERIDIAN", "BEARING", "LINE"]

flint_vocab = set(directions + instrument_verbs + instrument_nouns + declination_scaffolds)

matches = []
for token in expected_tokens:
    if token in flint_vocab:
        matches.append(token)

print(f"Flint matches in expected tokens: {matches}")
print(f"Domain score would be: {len(matches)}")

# Now let's see where the cuts should be placed to get these tokens
cuts_needed = []
current_pos = 0
for token in expected_tokens:
    if current_pos < 75:  # Only within head
        cuts_needed.append(current_pos + len(token) - 1)  # End of token
        current_pos += len(token)

print(f"Cuts needed for expected tokens: {cuts_needed[:len([c for c in cuts_needed if c < 75])]}")

# Compare with actual cuts
actual_cuts = [1,4,7,10,14,16,20,24,33,35,38,41,47,51,55,59,62,68,73]
print(f"Actual cuts (head only): {actual_cuts}")

# Test the working approach from our P74 analysis
def simple_word_split(text):
    """Simple word splitting that should work"""
    words = []
    current_word = ""
    
    for char in text:
        if char.isalpha():
            current_word += char
        else:
            if current_word:
                words.append(current_word.upper())
                current_word = ""
    
    if current_word:
        words.append(current_word.upper())
    
    return words

simple_tokens = simple_word_split(head)
print(f"Simple word split: {simple_tokens}")

# Check Flint matches with simple splitting
simple_matches = [token for token in simple_tokens if token in flint_vocab]
print(f"Flint matches with simple split: {simple_matches}")
print(f"Simple split domain score: {len(simple_matches)}")