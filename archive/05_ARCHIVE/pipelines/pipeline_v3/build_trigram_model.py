#!/usr/bin/env python3
"""
Build a letter trigram model from the Brown corpus.
Outputs counts and probabilities for use in generation.
"""

import json
import pickle
import random
from collections import defaultdict, Counter
from pathlib import Path

def build_trigram_model(corpus_path: Path = None):
    """
    Build letter trigram model from corpus.
    
    Returns:
        Dictionary with bigram and trigram counts/probabilities
    """
    # Use Brown corpus text if available, else use sample text
    if corpus_path and corpus_path.exists():
        with open(corpus_path, 'r') as f:
            text = f.read().upper()
    else:
        # Sample English text for demonstration
        sample_text = """
        The quick brown fox jumps over the lazy dog. In the beginning was the Word,
        and the Word was with God, and the Word was God. To be or not to be, that is
        the question. It was the best of times, it was the worst of times. All happy
        families are alike; each unhappy family is unhappy in its own way. Call me
        Ishmael. It is a truth universally acknowledged, that a single man in possession
        of a good fortune must be in want of a wife. The sun also rises. In a hole in
        the ground there lived a hobbit. The past is a foreign country; they do things
        differently there. I am an invisible man. If you really want to hear about it,
        the first thing you'll probably want to know is where I was born. Happy families
        are all alike; every unhappy family is unhappy in its own way. It was a bright
        cold day in April, and the clocks were striking thirteen. Mother died today.
        """
        # Add more variety
        sample_text += """
        East winds blow across the northeast plains. The Berlin clock tower stands tall.
        Mathematics and physics converge at quantum mechanics. Cryptography protects secrets.
        The algorithm efficiently processes large datasets. Neural networks learn patterns.
        Evolution shaped biological diversity. Democracy requires informed citizens.
        Technology transforms society rapidly. Climate change threatens ecosystems globally.
        """ * 10  # Repeat for more data
        
        text = ''.join(c.upper() if c.isalpha() else ' ' for c in sample_text)
        text = ' '.join(text.split())  # Normalize spaces
    
    # Extract only letters and spaces
    clean_text = ''.join(c if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ ' else ' ' for c in text)
    clean_text = ' '.join(clean_text.split())  # Normalize spaces
    
    # Count unigrams, bigrams, and trigrams
    unigram_counts = Counter(clean_text)
    bigram_counts = Counter()
    trigram_counts = Counter()
    
    for i in range(len(clean_text) - 2):
        bigram = clean_text[i:i+2]
        trigram = clean_text[i:i+3]
        bigram_counts[bigram] += 1
        trigram_counts[trigram] += 1
    
    # Build conditional probability tables
    # P(c|ab) = count(abc) / count(ab)
    trigram_probs = defaultdict(dict)
    for trigram, count in trigram_counts.items():
        prefix = trigram[:2]
        char = trigram[2]
        if bigram_counts[prefix] > 0:
            trigram_probs[prefix][char] = count / bigram_counts[prefix]
    
    # P(b|a) = count(ab) / count(a)
    bigram_probs = defaultdict(dict)
    for bigram, count in bigram_counts.items():
        prefix = bigram[0]
        char = bigram[1]
        if unigram_counts[prefix] > 0:
            bigram_probs[prefix][char] = count / unigram_counts[prefix]
    
    # Unigram probabilities
    total_chars = sum(unigram_counts.values())
    unigram_probs = {char: count/total_chars for char, count in unigram_counts.items()}
    
    model = {
        'unigram_counts': dict(unigram_counts),
        'bigram_counts': dict(bigram_counts),
        'trigram_counts': dict(trigram_counts),
        'unigram_probs': unigram_probs,
        'bigram_probs': {k: dict(v) for k, v in bigram_probs.items()},
        'trigram_probs': {k: dict(v) for k, v in trigram_probs.items()},
        'total_chars': total_chars
    }
    
    return model


def score_text_trigram(text: str, model: dict) -> float:
    """
    Score text using trigram model with smoothing.
    
    Returns:
        Log probability of text under model
    """
    text = text.upper()
    text = ''.join(c if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' else '' for c in text)
    
    if len(text) < 3:
        return -100.0
    
    log_prob = 0.0
    smoothing = 1e-6
    
    for i in range(2, len(text)):
        trigram = text[i-2:i+1]
        prefix = trigram[:2]
        char = trigram[2]
        
        # Try trigram probability
        if prefix in model['trigram_probs'] and char in model['trigram_probs'][prefix]:
            prob = model['trigram_probs'][prefix][char]
        # Fall back to bigram
        elif prefix[1] in model['bigram_probs'] and char in model['bigram_probs'][prefix[1]]:
            prob = model['bigram_probs'][prefix[1]][char] * 0.1  # Discount
        # Fall back to unigram
        elif char in model['unigram_probs']:
            prob = model['unigram_probs'][char] * 0.01  # Further discount
        else:
            prob = smoothing
        
        log_prob += max(-20, min(0, -abs(prob)))  # Bounded log to avoid infinities
    
    return log_prob / len(text)  # Normalize by length


def main():
    """Build and save trigram model."""
    print("Building trigram model from corpus...")
    
    # Try to find Brown corpus, else use sample
    corpus_path = Path("data/brown_corpus.txt")
    if not corpus_path.exists():
        print("Using sample English text (Brown corpus not found)")
        corpus_path = None
    
    model = build_trigram_model(corpus_path)
    
    # Save model
    output_dir = Path("experiments/pipeline_v3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_file = output_dir / "trigram_model.json"
    with open(model_file, 'w') as f:
        json.dump(model, f, indent=2)
    
    print(f"Model saved to {model_file}")
    
    # Print statistics
    print(f"\nModel Statistics:")
    print(f"  Total characters: {model['total_chars']:,}")
    print(f"  Unique unigrams: {len(model['unigram_counts'])}")
    print(f"  Unique bigrams: {len(model['bigram_counts'])}")
    print(f"  Unique trigrams: {len(model['trigram_counts'])}")
    
    # Test scoring
    test_texts = [
        "EASTNORTHEASTBERLINCLOCK",
        "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG",
        "XYZQWRTYPLKJHGFDSAZXCVBNM"
    ]
    
    print("\nTest Scoring:")
    for text in test_texts:
        score = score_text_trigram(text, model)
        print(f"  {text[:30]}... : {score:.4f}")
    
    return model


if __name__ == "__main__":
    model = main()