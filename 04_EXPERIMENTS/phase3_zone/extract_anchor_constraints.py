#!/usr/bin/env python3
"""
Extract anchor keystream constraints for all anchor positions
"""

import sys
import json
from pathlib import Path

# Add cipher_families to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families import VigenereCipher, BeaufortCipher


def extract_all_constraints():
    """Extract keystream constraints for all anchor positions"""
    
    # Load ciphertext
    ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    # Define anchors
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    results = {}
    
    for family in ['vigenere', 'beaufort']:
        for tableau in ['kryptos']:  # Focus on KRYPTOS tableau
            # Create cipher
            if family == 'vigenere':
                cipher = VigenereCipher(tableau=tableau)
            else:
                cipher = BeaufortCipher(tableau=tableau)
            
            constraints = []
            
            # Process each anchor
            for anchor_name, start, end in anchors:
                anchor_text = anchor_name
                
                # Extract constraints for each position
                for i, char in enumerate(anchor_text):
                    idx = start + i
                    ct_char = ciphertext[idx]
                    pt_char = char
                    
                    # Find required key letter
                    for key_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        if cipher.decrypt(ct_char, key_char) == pt_char:
                            constraints.append({
                                'idx': idx,
                                'ct': ct_char,
                                'pt': pt_char,
                                'k': key_char,
                                'anchor': anchor_name
                            })
                            break
            
            results[f"{family}_{tableau}"] = {
                'family': family,
                'tableau': tableau,
                'constraints': constraints
            }
    
    return results


def main():
    """Extract and save anchor constraints"""
    
    print("=" * 70)
    print("EXTRACTING ANCHOR KEYSTREAM CONSTRAINTS")
    print("=" * 70)
    
    results = extract_all_constraints()
    
    # Save results
    output_dir = Path(__file__).parent / 'notes'
    output_dir.mkdir(exist_ok=True)
    
    for key, data in results.items():
        family = data['family']
        tableau = data['tableau']
        
        print(f"\n{family.upper()} with {tableau.upper()} tableau:")
        print("-" * 40)
        
        # Group by anchor for display
        current_anchor = None
        for constraint in data['constraints']:
            if constraint['anchor'] != current_anchor:
                current_anchor = constraint['anchor']
                print(f"\n  {current_anchor}:")
            
            print(f"    Position {constraint['idx']:2}: {constraint['ct']} → {constraint['pt']} needs key '{constraint['k']}'")
        
        # Save to file
        filename = f"anchor_keystream_{family}_{tableau}.json"
        output_path = output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nSaved to: {output_path}")
    
    # Also create a summary showing the key patterns
    print("\n" + "=" * 70)
    print("KEY PATTERNS SUMMARY")
    print("=" * 70)
    
    for key, data in results.items():
        family = data['family']
        print(f"\n{family.upper()}:")
        
        # Extract just the key letters in order
        key_letters = [c['k'] for c in data['constraints']]
        
        # Show by position ranges
        print(f"  Positions 21-24 (EAST):      {' '.join(key_letters[0:4])}")
        print(f"  Positions 25-33 (NORTHEAST): {' '.join(key_letters[4:13])}")
        print(f"  Positions 63-68 (BERLIN):    {' '.join(key_letters[13:19])}")
        print(f"  Positions 69-73 (CLOCK):     {' '.join(key_letters[19:24])}")
        
        # Show as continuous string
        print(f"  Full pattern: {''.join(key_letters)}")


if __name__ == '__main__':
    main()