#!/usr/bin/env python3
"""
Antipodes Reorder - Check K4 solutions with Antipodes layout
"""

import json
import argparse
import sys
from pathlib import Path


class AntipodesReorder:
    """Handle Antipodes reordering for K4 validation"""
    
    def __init__(self, layout_path: str):
        """Load Antipodes layout mapping"""
        with open(layout_path, 'r') as f:
            self.layout = json.load(f)
        
        # For now, use identity mapping (can be updated with actual Antipodes ordering)
        # Antipodes typically involves reading from opposite ends or specific reordering
        self.mapping = self.layout.get('mapping', {}).get('indices', list(range(97)))
        
        # If no mapping provided, create a default Antipodes-style mapping
        if not self.mapping:
            # Example: reverse order reading
            self.mapping = list(range(96, -1, -1))
    
    def reorder(self, text: str) -> str:
        """Reorder text according to Antipodes layout"""
        if len(self.mapping) != len(text):
            # Adjust mapping to text length
            self.mapping = self.mapping[:len(text)]
        
        reordered = [''] * len(text)
        for new_pos, old_pos in enumerate(self.mapping):
            if old_pos < len(text):
                reordered[new_pos] = text[old_pos]
        
        return ''.join(reordered)
    
    def inverse_reorder(self, text: str) -> str:
        """Inverse reorder (back to original order)"""
        original = [''] * len(text)
        for new_pos, old_pos in enumerate(self.mapping):
            if new_pos < len(text) and old_pos < len(text):
                original[old_pos] = text[new_pos]
        
        return ''.join(original)
    
    def verify_invertible(self, text: str) -> bool:
        """Verify that reordering is invertible"""
        reordered = self.reorder(text)
        restored = self.inverse_reorder(reordered)
        return restored == text
    
    def test_with_manifest(self, manifest_path: str, ct_path: str) -> dict:
        """Test a manifest with Antipodes reordering"""
        # Import zone runner
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
        from zone_mask_v1.scripts.zone_runner import ZoneRunner
        
        # Load original ciphertext
        with open(ct_path, 'r') as f:
            original_ct = f.read().strip().upper()
        
        # Reorder ciphertext
        reordered_ct = self.reorder(original_ct)
        
        # Try to decrypt with manifest
        runner = ZoneRunner(manifest_path)
        runner.ciphertext = reordered_ct
        
        try:
            # Decrypt reordered ciphertext
            plaintext = runner.decrypt()
            
            # Check for BERLINCLOCK (may be at different positions after reordering)
            has_berlin = 'BERLINCLOCK' in plaintext.replace(' ', '')
            
            # Try round-trip
            re_encrypted = runner.encrypt(plaintext)
            roundtrip_valid = (re_encrypted == reordered_ct)
            
            return {
                'success': True,
                'original_ct': original_ct[:30] + '...',
                'reordered_ct': reordered_ct[:30] + '...',
                'plaintext_preview': plaintext[:30] + '...' if plaintext else None,
                'has_berlinclock': has_berlin,
                'roundtrip_valid': roundtrip_valid,
                'invertible': self.verify_invertible(original_ct)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'invertible': self.verify_invertible(original_ct)
            }


def main():
    parser = argparse.ArgumentParser(description='Antipodes reorder check for K4')
    parser.add_argument('--ct', required=True, help='Path to ciphertext file')
    parser.add_argument('--layout', required=True, help='Path to Antipodes layout JSON')
    parser.add_argument('--manifest', help='Optional manifest to test')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize reorderer
    reorderer = AntipodesReorder(args.layout)
    
    # Load ciphertext
    with open(args.ct, 'r') as f:
        ciphertext = f.read().strip().upper()
    
    print("Antipodes Reorder Check")
    print("-" * 40)
    
    # Test invertibility
    if reorderer.verify_invertible(ciphertext):
        print("✓ Reordering is invertible")
    else:
        print("✗ WARNING: Reordering is not invertible!")
    
    # Show reordered text
    reordered = reorderer.reorder(ciphertext)
    print(f"Original: {ciphertext[:30]}...")
    print(f"Reordered: {reordered[:30]}...")
    
    # Test with manifest if provided
    if args.manifest:
        print("\nTesting with manifest...")
        results = reorderer.test_with_manifest(args.manifest, args.ct)
        
        if results['success']:
            print(f"✓ Manifest processed successfully")
            print(f"  Has BERLINCLOCK: {results['has_berlinclock']}")
            print(f"  Round-trip valid: {results['roundtrip_valid']}")
            if args.verbose and results.get('plaintext_preview'):
                print(f"  Plaintext: {results['plaintext_preview']}")
        else:
            print(f"✗ Manifest failed: {results.get('error')}")
    
    # Save results
    output_file = Path('04_EXPERIMENTS/antipodes_check/antipodes_results.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            'invertible': reorderer.verify_invertible(ciphertext),
            'original_length': len(ciphertext),
            'reordered_sample': reordered[:50],
            'manifest_results': results if args.manifest else None
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()