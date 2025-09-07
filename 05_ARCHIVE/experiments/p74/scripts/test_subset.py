#!/usr/bin/env python3
"""Quick test of first few P74 letters to understand gate behavior"""

import subprocess
import sys

# Test first 5 letters
letters = ['T', 'S', 'A', 'I', 'O']

for letter in letters:
    print(f"\n=== Testing P[74]='{letter}' ===")
    cmd = [sys.executable, 'p74_gate_nulls_sweep.py', '--test_letter', letter, '--no_nulls']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract key info
    output_lines = result.stdout.split('\n')
    for line in output_lines:
        if 'AND gate failed' in line or 'AND gate passed' in line:
            print(f"Result: {line.strip()}")
            break
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")