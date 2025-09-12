#!/usr/bin/env python3
"""
Create a mock complete 97-character plaintext for testing re-derivation.
The head (0-74) is from the actual solution.
The tail (75-96) is the derived tail "HEJOYOFANANGLEISTHEARC".
"""

from pathlib import Path

def create_mock_plaintext():
    """Create a complete 97-char plaintext for testing."""
    
    # Load the actual head
    with open('01_PUBLISHED/winner_HEAD_0020_v522B/plaintext_97.txt', 'r') as f:
        head = f.read().strip()
    
    # The derived tail (from the paper method)
    tail = "HEJOYOFANANGLEISTHEARC"
    
    # Combine
    full_pt = head + tail
    
    if len(full_pt) != 97:
        # Adjust if needed
        if len(full_pt) < 97:
            tail = tail + "X" * (97 - len(head) - len(tail))
        else:
            tail = tail[:97-len(head)]
        full_pt = head + tail
    
    # Save as test file
    test_path = Path("07_TOOLS/validation/test_data/plaintext_97_complete.txt")
    test_path.parent.mkdir(exist_ok=True)
    
    with open(test_path, 'w') as f:
        f.write(full_pt)
    
    print(f"Created mock complete plaintext at {test_path}")
    print(f"Length: {len(full_pt)}")
    print(f"Head (0-74): {full_pt[:75]}")
    print(f"Tail (75-96): {full_pt[75:97]}")
    
    return full_pt

if __name__ == "__main__":
    create_mock_plaintext()