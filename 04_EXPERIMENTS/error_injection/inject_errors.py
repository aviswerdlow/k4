#!/usr/bin/env python3
"""
Error Injection - Test solution fragility by injecting controlled errors
WARNING: For diagnostic use only. Do not accept solutions based on error injection.
"""

import json
import random
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any


class ErrorInjector:
    """Inject controlled errors to test solution fragility"""
    
    def __init__(self, manifest_path: str):
        """Load manifest and setup"""
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        
        # Import zone runner
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
        from zone_mask_v1.scripts.zone_runner import ZoneRunner
        self.ZoneRunner = ZoneRunner
        
        # Load original ciphertext
        ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            self.original_ct = f.read().strip().upper()
    
    def inject_single_error(self, text: str, position: int) -> str:
        """Inject a single character error at position"""
        text_list = list(text)
        
        if position < len(text_list):
            # Replace with a different random letter
            original = text_list[position]
            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            alternatives = [c for c in alphabet if c != original]
            text_list[position] = random.choice(alternatives)
        
        return ''.join(text_list)
    
    def inject_multiple_errors(self, text: str, positions: List[int]) -> str:
        """Inject errors at multiple positions"""
        for pos in positions:
            text = self.inject_single_error(text, pos)
        return text
    
    def test_with_errors(self, error_positions: List[int]) -> Dict[str, Any]:
        """Test manifest with injected errors"""
        # Inject errors into ciphertext
        corrupted_ct = self.inject_multiple_errors(self.original_ct, error_positions)
        
        # Count actual changes
        changes = sum(1 for i, (o, c) in enumerate(zip(self.original_ct, corrupted_ct)) if o != c)
        
        # Try to decrypt corrupted ciphertext
        runner = self.ZoneRunner()
        runner.manifest = self.manifest
        runner.ciphertext = corrupted_ct
        
        try:
            # Attempt decryption
            plaintext = runner.decrypt()
            
            # Check if BERLINCLOCK still appears
            control_indices = runner.control_indices
            berlin_intact = False
            if control_indices and plaintext:
                control_text = ''.join([plaintext[i] for i in control_indices if i < len(plaintext)])
                berlin_intact = (control_text == 'BERLINCLOCK')
            
            # Calculate error propagation
            if runner.plaintext:
                # Create clean version for comparison
                clean_runner = self.ZoneRunner()
                clean_runner.manifest = self.manifest
                clean_runner.ciphertext = self.original_ct
                clean_plaintext = clean_runner.decrypt()
                
                # Count differences in plaintext
                pt_differences = sum(1 for i, (c1, c2) in enumerate(zip(clean_plaintext, plaintext)) if c1 != c2)
                propagation_factor = pt_differences / changes if changes > 0 else 0
            else:
                propagation_factor = -1
            
            return {
                'success': True,
                'error_positions': error_positions,
                'errors_injected': changes,
                'berlin_intact': berlin_intact,
                'propagation_factor': propagation_factor,
                'plaintext_preview': plaintext[:50] if plaintext else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_positions': error_positions,
                'errors_injected': changes,
                'error': str(e)
            }
    
    def test_sensitive_zones(self) -> List[Dict[str, Any]]:
        """Test errors in sensitive zones"""
        zones = self.manifest.get('zones', {})
        control_indices = self.manifest.get('control', {}).get('indices', [])
        
        test_positions = [
            ('zone_boundaries', [
                zones['head']['end'],
                zones['mid']['start'],
                zones['mid']['end'],
                zones['tail']['start']
            ]),
            ('control_region', control_indices[:2]),
            ('mid_zone_center', [
                (zones['mid']['start'] + zones['mid']['end']) // 2
            ]),
            ('random_positions', [
                random.randint(0, 96),
                random.randint(0, 96)
            ])
        ]
        
        results = []
        
        for zone_name, positions in test_positions:
            print(f"Testing errors in: {zone_name}")
            result = self.test_with_errors(positions)
            result['zone'] = zone_name
            results.append(result)
        
        return results
    
    def analyze_fragility(self) -> Dict[str, Any]:
        """Comprehensive fragility analysis"""
        # Test single errors at different positions
        single_error_results = []
        
        # Sample positions across the ciphertext
        test_positions = [0, 20, 34, 50, 64, 74, 96]
        
        for pos in test_positions:
            result = self.test_with_errors([pos])
            single_error_results.append(result)
        
        # Test double errors
        double_error_results = []
        for _ in range(5):
            pos1 = random.randint(0, 96)
            pos2 = random.randint(0, 96)
            if pos1 != pos2:
                result = self.test_with_errors([pos1, pos2])
                double_error_results.append(result)
        
        # Calculate fragility metrics
        single_failures = sum(1 for r in single_error_results if not r['success'])
        double_failures = sum(1 for r in double_error_results if not r['success'])
        
        avg_propagation = sum(r.get('propagation_factor', 0) for r in single_error_results if r['success'])
        avg_propagation = avg_propagation / len(single_error_results) if single_error_results else 0
        
        return {
            'single_error_failure_rate': single_failures / len(single_error_results) if single_error_results else 0,
            'double_error_failure_rate': double_failures / len(double_error_results) if double_error_results else 0,
            'average_propagation_factor': avg_propagation,
            'single_error_results': single_error_results,
            'double_error_results': double_error_results
        }


def main():
    parser = argparse.ArgumentParser(description='Error Injection Testing (Diagnostic Only)')
    parser.add_argument('--manifest', required=True, help='Path to manifest')
    parser.add_argument('--positions', help='Comma-separated positions for errors')
    parser.add_argument('--count', type=int, default=1, help='Number of errors to inject')
    parser.add_argument('--analyze', action='store_true', help='Run full fragility analysis')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    print("ERROR INJECTION TEST (DIAGNOSTIC ONLY)")
    print("=" * 60)
    print("WARNING: Do not accept solutions based on error injection.")
    print("=" * 60)
    
    injector = ErrorInjector(args.manifest)
    
    if args.analyze:
        # Run comprehensive analysis
        print("\nRunning fragility analysis...")
        analysis = injector.analyze_fragility()
        
        print("\nFragility Metrics:")
        print(f"Single error failure rate: {analysis['single_error_failure_rate']:.1%}")
        print(f"Double error failure rate: {analysis['double_error_failure_rate']:.1%}")
        print(f"Average error propagation: {analysis['average_propagation_factor']:.2f}x")
        
        # Test sensitive zones
        print("\nTesting sensitive zones...")
        zone_results = injector.test_sensitive_zones()
        
        for result in zone_results:
            zone = result['zone']
            if result['success']:
                print(f"  {zone}: Berlin={'✓' if result['berlin_intact'] else '✗'}, Propagation={result['propagation_factor']:.1f}x")
            else:
                print(f"  {zone}: Failed")
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump({
                    'fragility_analysis': analysis,
                    'zone_results': zone_results
                }, f, indent=2)
            print(f"\nResults saved to: {args.output}")
    
    else:
        # Test specific positions
        if args.positions:
            positions = [int(p) for p in args.positions.split(',')]
        else:
            # Random positions
            positions = random.sample(range(97), min(args.count, 97))
        
        print(f"\nInjecting errors at positions: {positions}")
        result = injector.test_with_errors(positions)
        
        if result['success']:
            print(f"✓ Decryption succeeded despite {result['errors_injected']} error(s)")
            print(f"  BERLINCLOCK intact: {result['berlin_intact']}")
            print(f"  Error propagation: {result['propagation_factor']:.2f}x")
            if result.get('plaintext_preview'):
                print(f"  Plaintext: {result['plaintext_preview']}")
        else:
            print(f"✗ Decryption failed with {result['errors_injected']} error(s)")
            print(f"  Error: {result.get('error')}")
        
        # Save result
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nResult saved to: {args.output}")
    
    print("\n" + "=" * 60)
    print("Remember: This is diagnostic only. Do not accept based on errors.")


if __name__ == '__main__':
    main()