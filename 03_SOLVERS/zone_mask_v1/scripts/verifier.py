#!/usr/bin/env python3
"""
Verifier - Strict round-trip validation for K4 solutions
"""

import json
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.zone_runner import ZoneRunner


class Verifier:
    """Strict verifier for K4 round-trip validation"""
    
    def __init__(self, manifest_path: str, ct_path: str):
        """Initialize verifier with manifest and ciphertext"""
        self.runner = ZoneRunner(manifest_path)
        self.runner.load_ciphertext(ct_path)
        self.original_ct = self.runner.ciphertext
    
    def verify(self) -> Dict[str, Any]:
        """Perform comprehensive verification"""
        results = {
            'valid': False,
            'checks': {},
            'errors': []
        }
        
        # Check 1: Decrypt to plaintext
        try:
            plaintext = self.runner.decrypt()
            results['checks']['decrypt'] = True
            results['plaintext'] = plaintext
        except Exception as e:
            results['checks']['decrypt'] = False
            results['errors'].append(f"Decryption failed: {e}")
            return results
        
        # Check 2: Re-encrypt to ciphertext
        try:
            re_encrypted = self.runner.encrypt(plaintext)
            results['checks']['encrypt'] = True
            results['re_encrypted'] = re_encrypted
        except Exception as e:
            results['checks']['encrypt'] = False
            results['errors'].append(f"Re-encryption failed: {e}")
            return results
        
        # Check 3: Exact match
        if re_encrypted == self.original_ct:
            results['checks']['exact_match'] = True
        else:
            results['checks']['exact_match'] = False
            results['errors'].append("Re-encrypted text does not match original")
            
            # Find differences
            diffs = []
            for i, (orig, new) in enumerate(zip(self.original_ct, re_encrypted)):
                if orig != new:
                    diffs.append(f"Position {i}: {orig} != {new}")
            results['differences'] = diffs[:10]  # First 10 differences
        
        # Check 4: BERLINCLOCK verification
        control_indices = self.runner.control_indices
        if control_indices and plaintext:
            control_text = ''.join([plaintext[i] for i in control_indices if i < len(plaintext)])
            if control_text == 'BERLINCLOCK':
                results['checks']['berlinclock'] = True
            else:
                results['checks']['berlinclock'] = False
                results['errors'].append(f"BERLINCLOCK not found. Got: {control_text}")
        
        # Check 5: Length consistency
        if len(plaintext) == len(self.original_ct) == 97:
            results['checks']['length'] = True
        else:
            results['checks']['length'] = False
            results['errors'].append(f"Length mismatch: PT={len(plaintext)}, CT={len(self.original_ct)}")
        
        # Overall validation
        results['valid'] = all(results['checks'].values())
        
        return results
    
    def verify_batch(self, manifests: List[str]) -> List[Dict[str, Any]]:
        """Verify multiple manifests"""
        batch_results = []
        
        for manifest_path in manifests:
            self.runner.load_manifest(manifest_path)
            result = self.verify()
            result['manifest'] = manifest_path
            batch_results.append(result)
        
        return batch_results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='K4 Solution Verifier')
    parser.add_argument('--manifest', required=True, help='Path to manifest JSON file')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    # Run verification
    verifier = Verifier(args.manifest, args.ct)
    results = verifier.verify()
    
    # Display results
    if results['valid']:
        print("✅ VERIFICATION SUCCESSFUL")
        print(f"   All checks passed!")
        if args.verbose:
            print(f"   Plaintext: {results['plaintext'][:50]}...")
    else:
        print("❌ VERIFICATION FAILED")
        for error in results['errors']:
            print(f"   - {error}")
    
    # Display check details
    if args.verbose:
        print("\nDetailed checks:")
        for check, passed in results['checks'].items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()