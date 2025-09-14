#!/usr/bin/env python3
"""
Generate a mock letters_map.csv for testing the scoring pipeline
This will be replaced with the real mapping when available
"""

import pandas as pd
import random

# K4 ciphertext (97 characters)
K4_TEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def generate_mock_mapping():
    """Generate mock letter mapping for testing"""
    
    # Create index to character mapping
    data = []
    for i in range(len(K4_TEXT)):
        data.append({
            'index': i,
            'char': K4_TEXT[i]
        })
    
    # Save as CSV
    df = pd.DataFrame(data)
    df.to_csv('letters_map.csv', index=False)
    print(f"Generated mock letters_map.csv with {len(data)} entries")
    print("Sample:")
    print(df.head(10))
    print("\nThis is a MOCK file for testing only.")
    print("Replace with real character mapping when available.")

if __name__ == "__main__":
    generate_mock_mapping()