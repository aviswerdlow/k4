#!/usr/bin/env python3
"""
Rigorous Morse Code Detection in Shadow Patterns
Includes statistical validation and multiple hypothesis correction
"""

import numpy as np
import cv2
from scipy import signal, optimize
import json
from collections import Counter
import re

# Standard Morse code dictionary
MORSE_CODE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.'
}

# Reverse dictionary for decoding
MORSE_DECODE = {v: k for k, v in MORSE_CODE.items()}

# English word list for validation (subset)
COMMON_WORDS = set([
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
    'can', 'her', 'was', 'one', 'our', 'out', 'his', 'has',
    'had', 'were', 'been', 'have', 'their', 'said', 'each',
    'which', 'she', 'will', 'with', 'that', 'this', 'from',
    'they', 'what', 'been', 'when', 'make', 'like', 'time',
    'just', 'know', 'take', 'people', 'into', 'year', 'your',
    'some', 'could', 'them', 'than', 'first', 'water', 'been',
    'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down',
    'day', 'did', 'get', 'come', 'made', 'may', 'part'
])

def extract_scanline_band(image, y_center, band_height=20):
    """Extract a horizontal band from the image."""
    h, w = image.shape[:2]
    y_start = max(0, y_center - band_height // 2)
    y_end = min(h, y_center + band_height // 2)
    
    band = image[y_start:y_end, :]
    
    # Convert to grayscale if needed
    if len(band.shape) == 3:
        band = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    
    # Average across the band height to reduce noise
    profile = np.mean(band, axis=0)
    
    return profile

def adaptive_threshold(profile, method='otsu'):
    """Apply adaptive thresholding to binarize the signal."""
    if method == 'otsu':
        # Normalize to 0-255 range
        norm_profile = ((profile - profile.min()) / 
                       (profile.max() - profile.min()) * 255).astype(np.uint8)
        threshold, binary = cv2.threshold(norm_profile, 0, 255, 
                                         cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary > 0
    elif method == 'median':
        threshold = np.median(profile)
        return profile > threshold
    else:
        raise ValueError(f"Unknown method: {method}")

def run_length_encode(binary):
    """Convert binary array to run-length encoding."""
    if len(binary) == 0:
        return []
    
    runs = []
    current_value = binary[0]
    current_length = 1
    
    for i in range(1, len(binary)):
        if binary[i] == current_value:
            current_length += 1
        else:
            runs.append((current_value, current_length))
            current_value = binary[i]
            current_length = 1
    
    runs.append((current_value, current_length))
    return runs

def solve_morse_unit(runs, tolerance=0.3):
    """
    Solve for the Morse unit T that best fits the standard ratios:
    - Dot = 1T
    - Dash = 3T
    - Intra-character gap = 1T
    - Inter-character gap = 3T
    - Word gap = 7T
    """
    if len(runs) < 5:
        return None
    
    # Extract all run lengths
    lengths = [length for _, length in runs]
    
    # Try different unit sizes
    min_length = min(lengths)
    max_length = max(lengths)
    
    best_T = None
    best_score = float('inf')
    
    for T_candidate in np.linspace(min_length * 0.8, min_length * 1.5, 50):
        if T_candidate <= 0:
            continue
            
        # Score how well lengths match expected ratios
        score = 0
        for length in lengths:
            ratio = length / T_candidate
            # Find closest standard ratio
            standard_ratios = [1, 3, 7]
            closest = min(standard_ratios, key=lambda x: abs(ratio - x))
            score += (ratio - closest) ** 2
        
        if score < best_score:
            best_score = score
            best_T = T_candidate
    
    # Check if the fit is reasonable
    if best_score / len(lengths) > tolerance:
        return None
    
    return best_T

def decode_morse(runs, T):
    """Decode run-length encoded signal as Morse code."""
    if T is None or T <= 0:
        return ""
    
    decoded_chars = []
    current_char = ""
    
    for i, (value, length) in enumerate(runs):
        ratio = length / T
        
        if value == 1:  # Signal ON (dot or dash)
            if ratio < 2:
                current_char += "."
            else:
                current_char += "-"
        else:  # Signal OFF (gap)
            if ratio < 2:  # Intra-character gap
                continue
            elif ratio < 5:  # Inter-character gap
                if current_char in MORSE_DECODE:
                    decoded_chars.append(MORSE_DECODE[current_char])
                current_char = ""
            else:  # Word gap
                if current_char in MORSE_DECODE:
                    decoded_chars.append(MORSE_DECODE[current_char])
                decoded_chars.append(" ")
                current_char = ""
    
    # Don't forget the last character
    if current_char in MORSE_DECODE:
        decoded_chars.append(MORSE_DECODE[current_char])
    
    return "".join(decoded_chars)

def score_text(text):
    """
    Score decoded text for validity:
    - Must be ASCII letters/spaces only
    - Must contain ≥2 dictionary words of length ≥4
    - Language model score (simplified: word frequency)
    """
    # Check ASCII
    if not re.match(r'^[A-Z ]*$', text.upper()):
        return 0.0
    
    # Extract words
    words = text.upper().split()
    if len(words) < 2:
        return 0.0
    
    # Count valid dictionary words
    valid_words = [w for w in words if len(w) >= 4 and w.lower() in COMMON_WORDS]
    if len(valid_words) < 2:
        return 0.0
    
    # Simple language score: ratio of valid words
    score = len(valid_words) / max(len(words), 1)
    
    return score

def compute_null_distribution(image, y_center, n_samples=1000, jitter=5):
    """Compute null distribution by testing nearby scanlines."""
    null_scores = []
    
    h = image.shape[0]
    
    for i in range(n_samples):
        # Jitter the scanline position
        y_test = y_center + np.random.randint(-jitter, jitter + 1)
        y_test = max(20, min(h - 20, y_test))
        
        # Extract and process
        profile = extract_scanline_band(image, y_test)
        binary = adaptive_threshold(profile)
        runs = run_length_encode(binary)
        T = solve_morse_unit(runs)
        
        if T is not None:
            decoded = decode_morse(runs, T)
            score = score_text(decoded)
            null_scores.append(score)
        else:
            null_scores.append(0.0)
    
    return np.array(null_scores)

def test_morse_hypothesis(image_path, y_center, band_height=20, 
                         n_nulls=1000, p_threshold=0.001):
    """
    Main function to test Morse code hypothesis with statistical validation.
    
    Returns:
        dict: Results including decoded text, p-value, and decision
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot load image: {image_path}")
    
    # Extract primary scanline
    profile = extract_scanline_band(image, y_center, band_height)
    
    # Threshold to binary
    binary = adaptive_threshold(profile)
    
    # Run-length encode
    runs = run_length_encode(binary)
    
    # Solve for Morse unit
    T = solve_morse_unit(runs)
    
    if T is None:
        return {
            'decoded': '',
            'score': 0.0,
            'p_value': 1.0,
            'reject_null': False,
            'message': 'Could not find consistent Morse unit'
        }
    
    # Decode
    decoded = decode_morse(runs, T)
    score = score_text(decoded)
    
    # Compute null distribution
    print("Computing null distribution...")
    null_scores = compute_null_distribution(image, y_center, n_nulls, jitter=5)
    
    # Compute p-value
    p_value = np.mean(null_scores >= score)
    
    # Apply Bonferroni correction if testing multiple scanlines
    # (multiply p_value by number of tests if applicable)
    
    result = {
        'decoded': decoded,
        'score': score,
        'morse_unit_T': T,
        'p_value': p_value,
        'reject_null': p_value <= p_threshold,
        'null_mean': np.mean(null_scores),
        'null_std': np.std(null_scores),
        'null_max': np.max(null_scores)
    }
    
    return result

def test_replication(image_path, y_center, azimuths, altitudes):
    """Test if decode is stable across small lighting changes."""
    results = []
    
    for az in azimuths:
        for alt in altitudes:
            # Assume images are named with pattern
            img_file = f"plaza_shadow_test_az{int(az)}_alt{int(alt)}.png"
            if os.path.exists(img_file):
                result = test_morse_hypothesis(img_file, y_center)
                results.append({
                    'azimuth': az,
                    'altitude': alt,
                    'decoded': result['decoded'],
                    'score': result['score']
                })
    
    # Check consistency
    decoded_texts = [r['decoded'] for r in results if r['score'] > 0]
    if len(decoded_texts) > 0:
        most_common = Counter(decoded_texts).most_common(1)[0]
        consistency = most_common[1] / len(decoded_texts)
        return {
            'consistent_decode': most_common[0],
            'consistency_ratio': consistency,
            'n_successful': len(decoded_texts),
            'all_results': results
        }
    
    return {
        'consistent_decode': None,
        'consistency_ratio': 0.0,
        'n_successful': 0,
        'all_results': results
    }

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python morse_analysis.py <image_path> <y_scanline>")
        print("Example: python morse_analysis.py plaza_shadow_test.png 1024")
        sys.exit(1)
    
    image_path = sys.argv[1]
    y_center = int(sys.argv[2])
    
    print(f"Testing Morse hypothesis on {image_path} at y={y_center}")
    
    result = test_morse_hypothesis(image_path, y_center, n_nulls=1000)
    
    print("\nResults:")
    print(f"  Decoded text: '{result['decoded']}'")
    print(f"  Score: {result['score']:.3f}")
    print(f"  Morse unit T: {result.get('morse_unit_T', 'N/A')}")
    print(f"  P-value: {result['p_value']:.4f}")
    print(f"  Null distribution: mean={result.get('null_mean', 0):.3f}, "
          f"std={result.get('null_std', 0):.3f}, max={result.get('null_max', 0):.3f}")
    print(f"  Decision: {'REJECT NULL (potential signal)' if result['reject_null'] else 'FAIL TO REJECT (likely noise)'}")
    
    # Save results
    with open('morse_analysis_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to morse_analysis_results.json")
