#!/usr/bin/env python3
"""
Sanborn Twist Detector - Test small modifications to baseline solutions
"""

import json
import copy
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List


class TwistDetector:
    """Test small twists to baseline manifests"""
    
    def __init__(self, baseline_path: str):
        """Load baseline manifest"""
        with open(baseline_path, 'r') as f:
            self.baseline = json.load(f)
        
        # Import zone runner
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / '03_SOLVERS'))
        from zone_mask_v1.scripts.zone_runner import ZoneRunner
        self.ZoneRunner = ZoneRunner
    
    def apply_twist(self, manifest: Dict[str, Any], twist_type: str) -> Dict[str, Any]:
        """Apply a specific twist to the manifest"""
        twisted = copy.deepcopy(manifest)
        
        if twist_type == 'family_toggle_mid':
            # Toggle cipher family for MID zone
            if twisted['cipher']['family'] == 'vigenere':
                # Need to handle per-zone cipher families
                twisted['cipher']['family_overrides'] = {'mid': 'beaufort'}
            else:
                twisted['cipher']['family_overrides'] = {'mid': 'vigenere'}
        
        elif twist_type == 'reverse_tableau_10':
            # Add parameter to reverse tableau every 10 positions
            twisted['cipher']['tableau_reverse'] = {
                'enabled': True,
                'period': 10
            }
        
        elif twist_type == 'rotate_key_64_69':
            # Rotate key at positions 64 and 69
            twisted['cipher']['schedule'] = 'rotate_on_control'
            twisted['cipher']['schedule_params'] = {
                'indices': [64, 69]
            }
        
        elif twist_type == 'add_tumble_flip':
            # Add a tumble flip between passes
            if 'route' not in twisted:
                twisted['route'] = {
                    'type': 'columnar',
                    'params': {'rows': 7, 'cols': 14}
                }
            
            twisted['route']['params']['passes'] = 2
            twisted['route']['params']['row_flip_between_passes'] = True
        
        elif twist_type == 'swap_head_tail_keys':
            # Swap HEAD and TAIL keys
            head_key = twisted['cipher']['keys'].get('head')
            tail_key = twisted['cipher']['keys'].get('tail')
            if head_key and tail_key:
                twisted['cipher']['keys']['head'] = tail_key
                twisted['cipher']['keys']['tail'] = head_key
        
        elif twist_type == 'add_period2_mask':
            # Add period-2 mask if not present
            if 'mask' not in twisted:
                twisted['mask'] = {'type': 'period2', 'params': {}}
        
        elif twist_type == 'control_mode_toggle':
            # Toggle control mode
            if twisted['control']['mode'] == 'content':
                twisted['control']['mode'] = 'control'
            else:
                twisted['control']['mode'] = 'content'
        
        return twisted
    
    def test_twist(self, twisted_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Test a twisted manifest"""
        # Load ciphertext
        ct_path = Path(__file__).parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        
        # Create temporary runner
        runner = self.ZoneRunner()
        runner.manifest = twisted_manifest
        runner.load_ciphertext(str(ct_path))
        
        try:
            # Decrypt
            plaintext = runner.decrypt()
            
            # Check round-trip
            roundtrip_valid = runner.verify_roundtrip()
            
            # Check BERLINCLOCK
            control_indices = runner.control_indices
            berlin_found = False
            if control_indices and plaintext:
                control_text = ''.join([plaintext[i] for i in control_indices if i < len(plaintext)])
                berlin_found = (control_text == 'BERLINCLOCK')
            
            # Simple English frequency check
            english_score = self.score_english(plaintext)
            
            return {
                'success': True,
                'roundtrip_valid': roundtrip_valid,
                'berlin_found': berlin_found,
                'english_score': english_score,
                'plaintext_preview': plaintext[:50] if plaintext else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def score_english(self, text: str) -> float:
        """Simple English frequency scoring"""
        # Common English letter frequencies
        english_freq = {
            'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,
            'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'L': 4.0
        }
        
        text = text.upper()
        score = 0
        for char, expected_freq in english_freq.items():
            actual_freq = (text.count(char) / len(text)) * 100 if text else 0
            score -= abs(actual_freq - expected_freq)
        
        return score
    
    def run_all_twists(self) -> List[Dict[str, Any]]:
        """Run all twist types"""
        twist_types = [
            'family_toggle_mid',
            'reverse_tableau_10',
            'rotate_key_64_69',
            'add_tumble_flip',
            'swap_head_tail_keys',
            'add_period2_mask',
            'control_mode_toggle'
        ]
        
        results = []
        
        # Test baseline first
        print("Testing baseline...")
        baseline_result = self.test_twist(self.baseline)
        baseline_score = baseline_result.get('english_score', -1000)
        
        results.append({
            'twist': 'baseline',
            'manifest': self.baseline,
            'result': baseline_result,
            'improvement': 0
        })
        
        # Test each twist
        for twist_type in twist_types:
            print(f"Testing twist: {twist_type}...")
            
            twisted = self.apply_twist(self.baseline, twist_type)
            result = self.test_twist(twisted)
            
            improvement = 0
            if result['success']:
                twist_score = result.get('english_score', -1000)
                improvement = twist_score - baseline_score
            
            results.append({
                'twist': twist_type,
                'manifest': twisted,
                'result': result,
                'improvement': improvement
            })
        
        # Sort by improvement
        results.sort(key=lambda x: x['improvement'], reverse=True)
        
        return results


def main():
    parser = argparse.ArgumentParser(description='Sanborn Twist Detector')
    parser.add_argument('--baseline', required=True, help='Path to baseline manifest')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Run twist detection
    detector = TwistDetector(args.baseline)
    results = detector.run_all_twists()
    
    print("\nTwist Detection Results")
    print("=" * 60)
    
    # Display results
    for i, item in enumerate(results):
        twist = item['twist']
        result = item['result']
        improvement = item['improvement']
        
        status = "✓" if result.get('success') else "✗"
        
        print(f"\n{i+1}. {twist}: {status}")
        
        if result.get('success'):
            print(f"   Round-trip: {result['roundtrip_valid']}")
            print(f"   BERLINCLOCK: {result['berlin_found']}")
            print(f"   English score: {result['english_score']:.2f}")
            print(f"   Improvement: {improvement:+.2f}")
            
            if args.verbose and result.get('plaintext_preview'):
                print(f"   Preview: {result['plaintext_preview']}")
        else:
            print(f"   Error: {result.get('error')}")
    
    # Find best twist
    best_twist = None
    for item in results:
        if item['twist'] != 'baseline' and item['result'].get('success'):
            if item['result'].get('roundtrip_valid') and item['improvement'] > 0:
                best_twist = item
                break
    
    if best_twist:
        print("\n" + "=" * 60)
        print(f"BEST TWIST: {best_twist['twist']}")
        print(f"Improvement: {best_twist['improvement']:+.2f}")
        
        # Save best twist manifest
        output_dir = Path('04_EXPERIMENTS/twist_detector')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        best_manifest_path = output_dir / 'best_twist.json'
        with open(best_manifest_path, 'w') as f:
            json.dump(best_twist['manifest'], f, indent=2)
        
        print(f"Best twist manifest saved to: {best_manifest_path}")
    else:
        print("\n" + "=" * 60)
        print("No improving twist found. Baseline remains best.")
    
    # Save full results if requested
    if args.output:
        # Convert results to JSON-serializable format
        output_data = []
        for item in results:
            output_data.append({
                'twist': item['twist'],
                'improvement': item['improvement'],
                'result': item['result']
            })
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nFull results saved to: {args.output}")


if __name__ == '__main__':
    main()