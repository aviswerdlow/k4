#!/usr/bin/env python3
"""
Key Phase Scanner - Test all key rotation offsets to find best Englishness
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent / '03_SOLVERS'))


class KeyPhaseScanner:
    """Scan all key phase offsets for best results"""
    
    def __init__(self, manifest_path: str):
        with open(manifest_path, 'r') as f:
            self.base_manifest = json.load(f)
        
        from zone_mask_v1.scripts.zone_runner import ZoneRunner
        self.ZoneRunner = ZoneRunner
        
        # Load ciphertext
        ct_path = Path(__file__).parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            self.ciphertext = f.read().strip().upper()
    
    def score_english(self, text: str) -> float:
        """Score text for English-like properties"""
        if not text:
            return 0
        
        text = text.upper()
        
        # Common trigrams
        trigrams = ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT',
                   'ION', 'TER', 'WAS', 'YOU', 'ITH', 'VER', 'ALL', 'WIT', 'THI', 'TIO']
        
        # Common bigrams
        bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES',
                  'ST', 'RE', 'NT', 'ON', 'AT', 'OU', 'IT', 'TE', 'ET', 'NG']
        
        score = 0
        for tri in trigrams:
            score += text.count(tri) * 3
        for bi in bigrams:
            score += text.count(bi) * 1
        
        # Bonus for words
        words = ['SECRET', 'BERLIN', 'CLOCK', 'LATITUDE', 'LONGITUDE', 'DEGREE',
                'SHADOW', 'LIGHT', 'BETWEEN', 'ABSENCE', 'TRUTH', 'KNOWLEDGE']
        
        for word in words:
            if word in text:
                score += 20
                print(f"    Found word: {word}")
        
        return score
    
    def test_phase(self, zone: str, phase: int) -> Dict[str, Any]:
        """Test a specific key phase offset"""
        # Create modified manifest
        test_manifest = json.loads(json.dumps(self.base_manifest))
        
        # Get key for zone
        zone_key = test_manifest['cipher']['keys'].get(zone, '')
        if not zone_key:
            return {'error': 'No key for zone'}
        
        # Rotate key by phase
        rotated_key = zone_key[phase:] + zone_key[:phase]
        test_manifest['cipher']['keys'][zone] = rotated_key
        
        # Test decryption
        runner = self.ZoneRunner()
        runner.manifest = test_manifest
        runner.ciphertext = self.ciphertext
        
        try:
            plaintext = runner.decrypt()
            
            # Extract zone text
            zones = test_manifest['zones']
            start = zones[zone]['start']
            end = zones[zone]['end']
            zone_text = plaintext[start:end+1] if plaintext else ''
            
            # Score
            score = self.score_english(zone_text)
            
            return {
                'phase': phase,
                'key': rotated_key,
                'zone_text': zone_text,
                'score': score,
                'preview': zone_text[:30] if zone_text else ''
            }
        except:
            return {'phase': phase, 'score': 0, 'error': True}
    
    def scan_all_phases(self) -> Dict[str, Any]:
        """Scan all phases for all zones"""
        results = {}
        
        for zone in ['head', 'mid', 'tail']:
            key = self.base_manifest['cipher']['keys'].get(zone, '')
            if not key:
                continue
            
            print(f"\nScanning {zone.upper()} zone (key: {key}):")
            zone_results = []
            
            for phase in range(len(key)):
                result = self.test_phase(zone, phase)
                zone_results.append(result)
                
                if result.get('score', 0) > 0:
                    print(f"  Phase {phase}: score={result['score']:.1f} | {result.get('preview', '')}")
            
            # Sort by score
            zone_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            results[zone] = zone_results
            
            # Show best
            best = zone_results[0]
            print(f"  BEST: Phase {best['phase']} (score={best.get('score', 0):.1f})")
        
        return results
    
    def create_optimized_manifest(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create manifest with best phases"""
        optimized = json.loads(json.dumps(self.base_manifest))
        
        for zone in ['head', 'mid', 'tail']:
            if zone in results and results[zone]:
                best_phase = results[zone][0]['phase']
                if best_phase > 0:
                    original_key = self.base_manifest['cipher']['keys'][zone]
                    rotated_key = original_key[best_phase:] + original_key[:best_phase]
                    optimized['cipher']['keys'][zone] = rotated_key
                    print(f"  {zone}: rotating key by {best_phase}")
        
        return optimized


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Key Phase Scanner')
    parser.add_argument('--manifest', required=True, help='Base manifest to test')
    parser.add_argument('--output', help='Output optimized manifest')
    parser.add_argument('--zone', help='Test specific zone only')
    
    args = parser.parse_args()
    
    scanner = KeyPhaseScanner(args.manifest)
    
    print("KEY PHASE SCANNING")
    print("=" * 60)
    
    if args.zone:
        # Test single zone
        key = scanner.base_manifest['cipher']['keys'].get(args.zone, '')
        print(f"Testing {args.zone.upper()} zone with key: {key}")
        
        best = None
        best_score = -1
        
        for phase in range(len(key)):
            result = scanner.test_phase(args.zone, phase)
            if result.get('score', 0) > best_score:
                best = result
                best_score = result['score']
        
        print(f"\nBest phase: {best['phase']} (score={best_score:.1f})")
        print(f"Zone text: {best.get('preview', '')}")
    
    else:
        # Test all zones
        results = scanner.scan_all_phases()
        
        # Create optimized manifest
        print("\n" + "=" * 60)
        print("CREATING OPTIMIZED MANIFEST")
        optimized = scanner.create_optimized_manifest(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(optimized, f, indent=2)
            print(f"\nOptimized manifest saved to: {args.output}")
        
        # Test optimized version
        print("\nTesting optimized manifest...")
        runner = scanner.ZoneRunner()
        runner.manifest = optimized
        runner.ciphertext = scanner.ciphertext
        
        try:
            plaintext = runner.decrypt()
            
            # Check MID zone
            mid_start = optimized['zones']['mid']['start']
            mid_end = optimized['zones']['mid']['end']
            mid_text = plaintext[mid_start:mid_end+1]
            
            print(f"MID zone result: {mid_text[:40]}...")
            print(f"English score: {scanner.score_english(mid_text):.1f}")
            
            # Check for BERLINCLOCK
            control_indices = optimized['control']['indices']
            control_text = ''.join([plaintext[i] for i in control_indices if i < len(plaintext)])
            if control_text == 'BERLINCLOCK':
                print("✅ BERLINCLOCK FOUND!")
        except Exception as e:
            print(f"Error testing optimized: {e}")


if __name__ == '__main__':
    main()