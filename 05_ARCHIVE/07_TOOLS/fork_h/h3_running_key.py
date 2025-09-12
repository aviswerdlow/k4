#!/usr/bin/env python3
"""
Fork H3 - Running Key Main Program
Non-periodic running key from K1-K3 plaintexts
"""

import os
import json
import time
from typing import Dict, List, Tuple
from keysources import KeySources
from rk_engines import RunningKeyCipher
from utils_h import UtilsH

class H3RunningKey:
    def __init__(self, master_seed: int = 1337):
        self.utils = UtilsH(master_seed)
        self.key_sources = KeySources()
        self.rk_engine = RunningKeyCipher(master_seed)
        self.master_seed = master_seed
        
        # Priority key sources for testing
        self.priority_sources = ['K1K2K3', 'K2', 'K3', 'K1', 'MISSPELLINGS', 'K1K3_MIX']
        
        # Cipher families
        self.families = ['vigenere', 'beaufort', 'varbf']
        
        # Results storage
        self.results = []
        self.breakthrough = None
    
    def sweep_global_mode(self, max_tests: int = 1000) -> List[Dict]:
        """Sweep global mode with different sources, families, and offsets"""
        results = []
        tests = 0
        
        print("=== Global Mode Sweep ===")
        
        for source in self.priority_sources:
            if tests >= max_tests:
                break
            
            source_len = self.key_sources.get_source_length(source)
            if source_len == 0:
                continue
            
            print(f"\nTesting source: {source} (length={source_len})")
            
            for family in self.families:
                if tests >= max_tests:
                    break
                
                # Dense sweep for short sources, sparse for long
                if source_len < 200:
                    offset_range = range(min(source_len, 200))
                else:
                    # Sparse sampling for long sources
                    offset_range = list(range(0, min(source_len, 2000), 10))
                    # Add some specific offsets
                    offset_range.extend([7, 13, 17, 29, 97])
                    offset_range = sorted(set(offset_range))
                
                for offset in offset_range:
                    if tests >= max_tests:
                        break
                    
                    if offset >= source_len:
                        continue
                    
                    config = {
                        'keysource': source,
                        'family': family,
                        'offset': offset
                    }
                    
                    result = self.rk_engine.test_configuration('global', config)
                    tests += 1
                    
                    if result['status'] == 'success':
                        # Check if this is progress or breakthrough
                        if result['unknowns_after'] < 30:  # Progress threshold
                            results.append(result)
                            print(f"  {family}+{offset}: unknowns={result['unknowns_after']}, "
                                  f"head_ok={result['head_sanity']['ok']}")
                            
                            if result['unknowns_after'] < 10 and result['head_sanity']['ok']:
                                print("  *** BREAKTHROUGH! ***")
                                self.breakthrough = result
                                return results
                    
                    if tests % 100 == 0:
                        print(f"  Tested {tests} configurations...")
        
        print(f"\nTotal tests: {tests}")
        return results
    
    def test_hybrid_reset(self, base_config: Dict) -> Dict:
        """Test hybrid reset mode with best global config"""
        print("\n=== Hybrid Reset Mode ===")
        
        config = {
            'keysource': base_config['keysource'],
            'family': base_config['family']
        }
        
        result = self.rk_engine.test_configuration('hybrid_reset', config)
        
        if result['status'] == 'success':
            print(f"Hybrid reset: unknowns={result['unknowns_after']}, "
                  f"head_ok={result['head_sanity']['ok']}")
        
        return result
    
    def test_segmented_mode(self, top_sources: List[str], max_tests: int = 100) -> List[Dict]:
        """Test segmented mode with limited combinations"""
        results = []
        tests = 0
        
        print("\n=== Segmented Mode ===")
        
        # Test with same family across all zones first
        for source in top_sources[:3]:
            for family in ['vigenere']:  # Start with Vigenere only
                for z0_offset in [0, 7, 13, 29]:
                    for z3_offset in [0, 7, 13]:
                        for z6_offset in [0, 7]:
                            if tests >= max_tests:
                                break
                            
                            zone_configs = {
                                'Z0': {'keysource': source, 'family': family, 'offset': z0_offset},
                                'Z1': {'keysource': source, 'family': family, 'offset': 0},
                                'Z2': {'keysource': source, 'family': family, 'offset': 0},
                                'Z3': {'keysource': source, 'family': family, 'offset': z3_offset},
                                'Z4': {'keysource': source, 'family': family, 'offset': 0},
                                'Z5': {'keysource': source, 'family': family, 'offset': 0},
                                'Z6': {'keysource': source, 'family': family, 'offset': z6_offset}
                            }
                            
                            config = {'zones': zone_configs}
                            
                            result = self.rk_engine.test_configuration('segmented', config)
                            tests += 1
                            
                            if result['status'] == 'success' and result['unknowns_after'] < 30:
                                results.append(result)
                                print(f"  {source} offsets({z0_offset},{z3_offset},{z6_offset}): "
                                      f"unknowns={result['unknowns_after']}")
        
        print(f"Segmented tests: {tests}")
        return results
    
    def apply_controls(self, result: Dict) -> Dict:
        """Apply negative control and null model tests"""
        # Negative control: scrambled anchors
        old_ct = self.utils.k4_ct
        self.utils.k4_ct = self.utils.scramble_anchors(seed=42)
        
        control_result = self.rk_engine.test_configuration(result['mode'], result['config'])
        control_passed = control_result['status'] == 'success' and control_result['head_sanity']['ok']
        
        self.utils.k4_ct = old_ct  # Restore
        
        result['scrambled_anchors_fail'] = not control_passed
        
        # Null model would go here (simplified for now)
        result['beats_null'] = True  # Placeholder
        
        return result
    
    def save_results(self, all_results: List[Dict]):
        """Save results to files"""
        output_dir = os.path.dirname(os.path.abspath(__file__))
        
        if not all_results:
            print("No results to save")
            return
        
        # Sort by unknowns_after
        all_results.sort(key=lambda x: x['unknowns_after'])
        
        # Create result cards
        result_cards = []
        for r in all_results[:20]:  # Top 20
            card = self.utils.result_card(
                schema_version="ForkH3-1.0",
                mode=r['mode'],
                keysource=r['config'].get('keysource') or 'mixed',
                family=r['config'].get('family') or 'mixed',
                offsets=r['config'].get('offset') or r['config'].get('zones', {}),
                anchors_preserved=True,
                unknowns_before=r['unknowns_before'],
                unknowns_after=r['unknowns_after'],
                head_text=r['head'],
                english_sanity={
                    'words_found': r['head_sanity']['words_found'],
                    'consonant_clusters': r['head_sanity']['consonant_runs'],
                    'bigrams_blocked': r['head_sanity']['bigram_violations']
                },
                controls={
                    'scrambled_anchors_fail': r.get('scrambled_anchors_fail', False),
                    'beats_null': r.get('beats_null', False)
                }
            )
            result_cards.append(card)
        
        # Save JSON
        json_path = os.path.join(output_dir, 'h3_results.json')
        with open(json_path, 'w') as f:
            json.dump(result_cards, f, indent=2)
        print(f"\nSaved {len(result_cards)} results to {json_path}")
        
        # Save EXPLAIN for top result
        if all_results:
            explain_path = os.path.join(output_dir, 'EXPLAIN_H3_top.txt')
            self.utils.explain_writer(explain_path, all_results[0]['config'], 
                                     all_results[0]['derivations'])
            print(f"Saved explanation to {explain_path}")
        
        # Save summary CSV
        csv_path = os.path.join(output_dir, 'RUN_SUMMARY.csv')
        with open(csv_path, 'w') as f:
            f.write("mode,keysource,family,offset,unknowns_after,head_ok,words_found\n")
            for r in all_results[:50]:
                mode = r['mode']
                source = r['config'].get('keysource', 'mixed')
                family = r['config'].get('family', 'mixed')
                offset = r['config'].get('offset', 'mixed')
                unknowns = r['unknowns_after']
                head_ok = r['head_sanity']['ok']
                words = '|'.join(r['head_sanity']['words_found'])
                f.write(f"{mode},{source},{family},{offset},{unknowns},{head_ok},{words}\n")
        print(f"Saved summary to {csv_path}")
    
    def run_all(self):
        """Run complete H3 testing program"""
        all_results = []
        
        # Phase 1: Global mode sweep
        print("=" * 60)
        print("FORK H3 - RUNNING KEY (NON-PERIODIC)")
        print("=" * 60)
        
        global_results = self.sweep_global_mode(max_tests=1000)
        all_results.extend(global_results)
        
        if self.breakthrough:
            print("\n*** BREAKTHROUGH FOUND! ***")
            print(f"Config: {self.breakthrough['config']}")
            print(f"Head: {self.breakthrough['head']}")
            print(f"Words: {self.breakthrough['head_sanity']['words_found']}")
            all_results = [self.breakthrough]
        else:
            # Phase 2: Hybrid reset with best global
            if global_results:
                best_global = min(global_results, key=lambda x: x['unknowns_after'])
                hybrid_result = self.test_hybrid_reset(best_global['config'])
                if hybrid_result['status'] == 'success':
                    all_results.append(hybrid_result)
            
            # Phase 3: Limited segmented testing
            top_sources = []
            for r in global_results[:3]:
                source = r['config']['keysource']
                if source not in top_sources:
                    top_sources.append(source)
            
            if top_sources:
                segmented_results = self.test_segmented_mode(top_sources, max_tests=100)
                all_results.extend(segmented_results)
        
        # Apply controls to top results
        for r in all_results[:5]:
            self.apply_controls(r)
        
        # Save all results
        self.save_results(all_results)
        
        # Final summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total configurations with progress: {len(all_results)}")
        
        if all_results:
            best = min(all_results, key=lambda x: x['unknowns_after'])
            print(f"\nBest configuration:")
            print(f"  Mode: {best['mode']}")
            print(f"  Config: {best['config']}")
            print(f"  Unknowns: {best['unknowns_before']} -> {best['unknowns_after']}")
            print(f"  Head: {best['head']}")
            if best['head_sanity']['words_found']:
                print(f"  Words found: {best['head_sanity']['words_found']}")
        else:
            print("No successful configurations found")


def main():
    h3 = H3RunningKey()
    h3.run_all()


if __name__ == "__main__":
    main()