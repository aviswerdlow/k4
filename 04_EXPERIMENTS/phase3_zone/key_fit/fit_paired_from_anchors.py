#!/usr/bin/env python3
"""
Fit paired alphabet systems (Porta & Quagmire) to anchor constraints
Plan E: Paired-alphabet systems that can produce non-periodic keystreams
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add cipher_families_pair to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / '03_SOLVERS' / 'zone_mask_v1' / 'scripts'))
from cipher_families_pair import create_paired_cipher, decode


def load_ciphertext() -> str:
    """Load K4 ciphertext"""
    ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
    with open(ct_path, 'r') as f:
        return f.read().strip().upper()


def test_anchor_decryption(config: Dict, phase: int = 0) -> bool:
    """
    Test if a cipher configuration correctly decrypts all anchors
    
    Returns:
        True if all anchors decrypt correctly
    """
    ciphertext = load_ciphertext()
    
    # Define anchors
    anchors = [
        ('EAST', 21, 24),
        ('NORTHEAST', 25, 33),
        ('BERLIN', 63, 68),
        ('CLOCK', 69, 73)
    ]
    
    # Update config with phase if needed
    if 'indicator' in config and config['indicator'].get('type') == 'periodic':
        config['indicator']['phase'] = phase
    
    # Test each anchor
    for anchor_text, start, end in anchors:
        # Extract ciphertext segment
        ct_segment = ciphertext[start:end+1]
        
        # Decrypt
        try:
            pt_segment = decode(ct_segment, config)
            
            if pt_segment != anchor_text:
                return False
        except Exception:
            return False
    
    return True


def find_paired_fits() -> List[Dict]:
    """Find paired alphabet configurations that satisfy all anchors"""
    
    results = []
    
    # Define search space
    families = ['porta', 'quag2', 'quag3', 'quag4']
    
    # Alphabet options
    row_alphabets = ['kryptos', {'keyword': 'URANIA'}, {'keyword': 'ABSCISSA'}]
    col_alphabets = ['kryptos', {'keyword': 'ORDINATE'}, {'keyword': 'LATITUDE'}]
    
    # Indicator keys
    indicator_keys = ['ABSCISSA', 'ORDINATE', 'LATITUDE', 'LONGITUDE', 'AZIMUTH', 'GIRASOL']
    
    print("=" * 70)
    print("PAIRED ALPHABET ANCHOR FITTING")
    print("=" * 70)
    
    total_tested = 0
    
    for family in families:
        print(f"\nTesting {family.upper()}...")
        
        for row_alph in row_alphabets:
            row_name = row_alph if isinstance(row_alph, str) else row_alph.get('keyword', 'unknown')
            
            # Porta only uses row alphabet
            if family == 'porta':
                col_options = [None]
            else:
                col_options = col_alphabets
            
            for col_alph in col_options:
                col_name = None if col_alph is None else (col_alph if isinstance(col_alph, str) else col_alph.get('keyword', 'unknown'))
                
                # Test static indicator
                config = {
                    'family': family,
                    'alph_row': row_alph,
                    'indicator': {'type': 'static'}
                }
                
                if col_alph is not None:
                    config['alph_col'] = col_alph
                
                total_tested += 1
                
                if test_anchor_decryption(config):
                    result = {
                        'family': family,
                        'row_alphabet': row_name,
                        'col_alphabet': col_name,
                        'indicator_type': 'static',
                        'config': config,
                        'description': f"{family}, row={row_name}, col={col_name}, static"
                    }
                    results.append(result)
                    print(f"  ✓ Found: {result['description']}")
                
                # Test periodic indicators
                for ind_key in indicator_keys:
                    for L in range(3, 12):
                        # Only test if indicator key is at least L chars
                        if len(ind_key) >= L:
                            test_key = ind_key[:L]
                        else:
                            test_key = (ind_key * ((L // len(ind_key)) + 1))[:L]
                        
                        for phase in range(L):
                            config = {
                                'family': family,
                                'alph_row': row_alph,
                                'indicator': {
                                    'type': 'periodic',
                                    'key': test_key,
                                    'phase': phase
                                }
                            }
                            
                            if col_alph is not None:
                                config['alph_col'] = col_alph
                            
                            total_tested += 1
                            
                            if test_anchor_decryption(config, phase):
                                result = {
                                    'family': family,
                                    'row_alphabet': row_name,
                                    'col_alphabet': col_name,
                                    'indicator_type': 'periodic',
                                    'indicator_key': test_key,
                                    'indicator_length': L,
                                    'indicator_phase': phase,
                                    'config': config,
                                    'description': f"{family}, row={row_name}, col={col_name}, ind={test_key}(L={L},φ={phase})"
                                }
                                results.append(result)
                                print(f"  ✓ Found: {result['description']}")
                                
                                # Don't test all phases if one works
                                break
    
    print(f"\nTotal configurations tested: {total_tested}")
    return results


def main():
    """Find paired alphabet configurations that satisfy anchors"""
    
    results = find_paired_fits()
    
    # Save results
    output_path = Path(__file__).parent / 'paired_fits.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if results:
        print(f"\nFound {len(results)} configurations that satisfy all anchors!")
        
        # Group by family
        by_family = {}
        for r in results:
            family = r['family']
            if family not in by_family:
                by_family[family] = []
            by_family[family].append(r)
        
        for family, fits in by_family.items():
            print(f"\n{family.upper()}: {len(fits)} solutions")
            for fit in fits[:3]:  # Show first 3
                print(f"  - {fit['description']}")
    else:
        print("\nNo paired alphabet configurations found that satisfy all anchors.")
        print("This suggests K4 may not use Porta or Quagmire ciphers,")
        print("or uses them with additional transformations.")
    
    print(f"\nResults saved to: {output_path}")
    
    if results:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\nTop candidates for manifest generation:")
        
        # Prefer shorter indicators and simpler configurations
        results.sort(key=lambda x: (
            0 if x['indicator_type'] == 'static' else x.get('indicator_length', 99),
            x['family']
        ))
        
        for i, r in enumerate(results[:5]):
            print(f"{i+1}. {r['description']}")


if __name__ == '__main__':
    main()