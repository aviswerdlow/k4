#!/usr/bin/env python3
"""
Zone Edge Jitter - Test small zone boundary adjustments
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / '03_SOLVERS'))


class ZoneJitterTest:
    """Test zone boundary variations"""
    
    def __init__(self, manifest_path: str):
        with open(manifest_path, 'r') as f:
            self.base_manifest = json.load(f)
        
        from zone_mask_v1.scripts.zone_runner import ZoneRunner
        self.ZoneRunner = ZoneRunner
        
        # Load ciphertext
        ct_path = Path(__file__).parent.parent / '02_DATA' / 'ciphertext_97.txt'
        with open(ct_path, 'r') as f:
            self.ciphertext = f.read().strip().upper()
    
    def score_zone(self, text: str) -> Tuple[float, List[str]]:
        """Score text and find patterns"""
        if not text:
            return 0, []
        
        text = text.upper()
        score = 0
        found_patterns = []
        
        # Check for specific K4-related words
        important_words = [
            'BERLIN', 'CLOCK', 'LATITUDE', 'LONGITUDE', 'DEGREE', 'MINUTE', 'SECOND',
            'SHADOW', 'LIGHT', 'BETWEEN', 'SUBTLE', 'ABSENCE', 'ILLUSION', 'NUANCE',
            'SECRET', 'HIDDEN', 'TRUTH', 'KNOWLEDGE', 'POWER', 'LANGLEY', 'STATION',
            'EAST', 'WEST', 'NORTH', 'SOUTH', 'COMPASS', 'BEARING', 'AZIMUTH'
        ]
        
        for word in important_words:
            if word in text:
                score += 50
                found_patterns.append(word)
        
        # Common English patterns
        trigrams = ['THE', 'AND', 'ING', 'ION', 'TIO', 'ENT', 'ATI', 'FOR', 'HER', 'TER']
        for tri in trigrams:
            count = text.count(tri)
            if count > 0:
                score += count * 3
        
        # Letter frequency check (rough)
        common_letters = 'ETAOINSHRDLU'
        freq_score = sum(1 for c in text if c in common_letters) / len(text) if text else 0
        score += freq_score * 10
        
        return score, found_patterns
    
    def test_zones(self, zone_config: Dict[str, Tuple[int, int]]) -> Dict[str, Any]:
        """Test a specific zone configuration"""
        # Create modified manifest
        test_manifest = json.loads(json.dumps(self.base_manifest))
        
        # Update zones
        for zone_name, (start, end) in zone_config.items():
            test_manifest['zones'][zone_name] = {'start': start, 'end': end}
        
        # Run decryption
        runner = self.ZoneRunner()
        runner.manifest = test_manifest
        runner.ciphertext = self.ciphertext
        
        try:
            plaintext = runner.decrypt()
            
            # Score each zone
            results = {}
            total_score = 0
            all_patterns = []
            
            for zone_name, (start, end) in zone_config.items():
                zone_text = plaintext[start:end+1] if plaintext else ''
                score, patterns = self.score_zone(zone_text)
                
                results[zone_name] = {
                    'text': zone_text,
                    'score': score,
                    'patterns': patterns,
                    'preview': zone_text[:20] if zone_text else ''
                }
                
                total_score += score
                all_patterns.extend(patterns)
            
            # Check BERLINCLOCK
            control_indices = test_manifest['control']['indices']
            control_text = ''.join([plaintext[i] for i in control_indices if i < len(plaintext)])
            berlin_found = (control_text == 'BERLINCLOCK')
            
            return {
                'zones': zone_config,
                'results': results,
                'total_score': total_score,
                'patterns_found': all_patterns,
                'berlin_clock': berlin_found,
                'control_text': control_text
            }
            
        except Exception as e:
            return {
                'zones': zone_config,
                'error': str(e),
                'total_score': 0
            }
    
    def generate_jitter_configs(self) -> List[Dict[str, Tuple[int, int]]]:
        """Generate zone configurations with small jitter"""
        base_zones = self.base_manifest['zones']
        
        configs = []
        
        # Original
        original = {
            'head': (base_zones['head']['start'], base_zones['head']['end']),
            'mid': (base_zones['mid']['start'], base_zones['mid']['end']),
            'tail': (base_zones['tail']['start'], base_zones['tail']['end'])
        }
        configs.append(original)
        
        # MID zone variations (keeping anchors fixed)
        # Shrink MID by 1 on each side
        configs.append({
            'head': (0, 20),
            'mid': (35, 61),  # Was 34-62
            'tail': (74, 96)
        })
        
        # Grow MID by 1 on left
        configs.append({
            'head': (0, 19),  # Shrink head
            'mid': (33, 62),  # Was 34-62
            'tail': (74, 96)
        })
        
        # Grow MID by 1 on right
        configs.append({
            'head': (0, 20),
            'mid': (34, 63),  # Was 34-62
            'tail': (74, 96)
        })
        
        # Shift MID left by 1
        configs.append({
            'head': (0, 19),
            'mid': (33, 61),  # Was 34-62
            'tail': (74, 96)
        })
        
        # Shift MID right by 1
        configs.append({
            'head': (0, 21),
            'mid': (35, 63),  # Was 34-62
            'tail': (74, 96)
        })
        
        return configs
    
    def run_jitter_scan(self) -> List[Dict[str, Any]]:
        """Run all jitter configurations"""
        configs = self.generate_jitter_configs()
        results = []
        
        print("Testing zone edge jitter...")
        print("-" * 60)
        
        for i, config in enumerate(configs):
            print(f"\nConfiguration {i+1}:")
            print(f"  HEAD: {config['head']}")
            print(f"  MID:  {config['mid']}")
            print(f"  TAIL: {config['tail']}")
            
            result = self.test_zones(config)
            results.append(result)
            
            if result.get('total_score', 0) > 0:
                print(f"  Score: {result['total_score']:.1f}")
                
                if result.get('patterns_found'):
                    print(f"  Found: {', '.join(result['patterns_found'])}")
                
                if result.get('berlin_clock'):
                    print("  ✅ BERLINCLOCK FOUND!")
                
                # Show MID preview
                mid_result = result.get('results', {}).get('mid', {})
                if mid_result:
                    print(f"  MID: {mid_result['preview']}...")
        
        # Sort by score
        results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Zone Edge Jitter Test')
    parser.add_argument('--manifest', required=True, help='Base manifest to test')
    parser.add_argument('--output', help='Output best configuration')
    
    args = parser.parse_args()
    
    print("ZONE EDGE JITTER TEST")
    print("=" * 60)
    
    tester = ZoneJitterTest(args.manifest)
    results = tester.run_jitter_scan()
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    if results:
        best = results[0]
        print(f"\nBest configuration (score={best.get('total_score', 0):.1f}):")
        print(f"  Zones: {best['zones']}")
        
        if best.get('patterns_found'):
            print(f"  Patterns: {', '.join(best['patterns_found'])}")
        
        if best.get('berlin_clock'):
            print("  ✅ BERLINCLOCK verified!")
        
        # Show zone previews
        for zone_name in ['head', 'mid', 'tail']:
            zone_result = best.get('results', {}).get(zone_name, {})
            if zone_result and zone_result.get('score', 0) > 10:
                print(f"  {zone_name.upper()}: {zone_result['preview']}... (score={zone_result['score']:.1f})")
        
        # Save best configuration
        if args.output and best.get('total_score', 0) > 50:
            # Create optimized manifest
            optimized = json.loads(json.dumps(tester.base_manifest))
            
            for zone_name, (start, end) in best['zones'].items():
                optimized['zones'][zone_name] = {'start': start, 'end': end}
            
            with open(args.output, 'w') as f:
                json.dump(optimized, f, indent=2)
            
            print(f"\nOptimized manifest saved to: {args.output}")


if __name__ == '__main__':
    main()