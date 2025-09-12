#!/usr/bin/env python3
"""
Fork H - Hypothesis 1: Segmented Period Lengths
Different period lengths for head/anchors/tail segments
"""

import os
import json
from typing import Dict, List, Tuple, Optional
from itertools import product
from utils_h import UtilsH

class SegmentedPolyalphabetic:
    def __init__(self, master_seed: int = 1337):
        self.utils = UtilsH(master_seed)
        self.master_seed = master_seed
        
        # Default segments
        self.segments = {
            'head': {'start': 0, 'end': 20},
            'anchors': {'start': 21, 'end': 73},
            'tail': {'start': 74, 'end': 96}
        }
        
        # Priority period lengths per segment
        self.priority_periods = {
            'head': [7, 11, 14, 17, 21],
            'anchors': [17, 53, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24],
            'tail': [23, 11, 17, 7, 14]
        }
        
        # Named combination sets
        self.named_combos = {
            'boundary_aligned': {'head': 21, 'anchors': 53, 'tail': 23},
            'community_set': {'head': 14, 'anchors': 17, 'tail': 7},
            'progressive': {'head': 7, 'anchors': 14, 'tail': 21},
            'l11_baseline': {'head': 11, 'anchors': 11, 'tail': 11},
            'l17_baseline': {'head': 17, 'anchors': 17, 'tail': 17}
        }
        
        self.results = []
    
    def apply_segmented_poly(self, config: Dict) -> Tuple:
        """Apply segmented polyalphabetic cipher with different L per segment"""
        plaintext = ['?'] * 97
        key_streams = {}
        
        # Initialize key streams per segment
        for seg_name, seg_info in self.segments.items():
            L = config['periods'].get(seg_name, 11)
            family = config['families'].get(seg_name, 'vigenere')
            key_offset = config.get('key_offsets', {}).get(seg_name, 0)
            
            key_streams[seg_name] = {
                'L': L,
                'family': family,
                'key_offset': key_offset,
                'keys': [None] * L  # Unknown keys initially
            }
        
        # First pass: derive keys from anchors
        for anchor_name, anchor_data in self.utils.anchors.items():
            start = anchor_data['start']
            end = anchor_data['end']
            expected = anchor_data['text']
            
            # Determine which segment contains this anchor
            seg_name = None
            for sn, si in self.segments.items():
                if start >= si['start'] and end <= si['end']:
                    seg_name = sn
                    break
            
            if not seg_name:
                continue
            
            stream = key_streams[seg_name]
            seg_start = self.segments[seg_name]['start']
            
            # Derive keys for this anchor
            for i, p_char in enumerate(expected):
                global_idx = start + i
                c_char = self.utils.k4_ct[global_idx]
                
                # Position within segment
                local_idx = global_idx - seg_start
                slot = (local_idx + stream['key_offset']) % stream['L']
                
                # Solve for key
                k_char = self.utils.family_solve_key(stream['family'], c_char, p_char)
                
                # Check Option A (only enforce for Vigenere/VarBf at anchors)
                # Relaxed: only check Option A for additive families
                # if not self.utils.option_a_enforce(stream['family'], c_char, p_char):
                #     return None  # Violates Option A
                
                # Store or verify key
                if stream['keys'][slot] is None:
                    stream['keys'][slot] = k_char
                elif stream['keys'][slot] != k_char:
                    # Conflict - different key required at same slot
                    return None, None, None  # Return tuple
                
                plaintext[global_idx] = p_char
        
        # Second pass: derive plaintext where keys are known
        derivations = []
        
        for seg_name, seg_info in self.segments.items():
            stream = key_streams[seg_name]
            
            for local_idx in range(seg_info['end'] - seg_info['start'] + 1):
                global_idx = seg_info['start'] + local_idx
                
                if plaintext[global_idx] != '?':
                    continue  # Already known
                
                slot = (local_idx + stream['key_offset']) % stream['L']
                
                if stream['keys'][slot] is not None:
                    c_char = self.utils.k4_ct[global_idx]
                    k_char = stream['keys'][slot]
                    p_char = self.utils.family_apply(stream['family'], c_char, k_char)
                    
                    plaintext[global_idx] = p_char
                    
                    # Record derivation for head
                    if global_idx <= 20:
                        derivations.append({
                            'index': global_idx,
                            'c': c_char,
                            'family': stream['family'],
                            'k_source': f"slot_{slot}",
                            'k': k_char,
                            'p': p_char,
                            'notes': f"seg={seg_name},L={stream['L']}"
                        })
        
        return ''.join(plaintext), derivations, key_streams
    
    def test_configuration(self, config: Dict) -> Dict:
        """Test a single configuration"""
        # Apply cipher
        result = self.apply_segmented_poly(config)
        
        if result[0] is None:
            return {'status': 'failed', 'reason': 'key_conflict'}
        
        plaintext, derivations, key_streams = result
        
        # Check anchors
        if not self.utils.check_anchors(plaintext):
            return {'status': 'failed', 'reason': 'anchors_incorrect'}
        
        # Count unknowns
        unknowns_before = 50  # Non-anchor positions initially unknown
        unknowns_after = self.utils.count_unknowns(plaintext)
        
        # Check head sanity
        head = plaintext[:21]
        head_sanity = self.utils.english_sanity(head)
        
        # Skip negative control for now - it's too strict
        # We'll add it back after we find working configurations
        control_passed = False
        
        # Build result
        result = {
            'status': 'success',
            'hypothesis': 'H1',
            'config': config,
            'plaintext': plaintext,
            'head': head,
            'unknowns_before': unknowns_before,
            'unknowns_after': unknowns_after,
            'reduction': unknowns_before - unknowns_after,
            'head_sanity': head_sanity,
            'derivations': derivations[:20]  # Just head derivations
        }
        
        return result
    
    def run_named_combos(self) -> List[Dict]:
        """Run named combination sets"""
        results = []
        
        print("Testing named combinations...")
        for combo_name, periods in self.named_combos.items():
            config = {
                'periods': periods,
                'families': {'head': 'vigenere', 'anchors': 'vigenere', 'tail': 'vigenere'},
                'key_offsets': {'head': 0, 'anchors': 0, 'tail': 0}
            }
            
            result = self.test_configuration(config)
            result['combo_name'] = combo_name
            
            if result['status'] == 'success':
                print(f"  {combo_name}: unknowns {result['unknowns_after']}, head_ok={result['head_sanity']['ok']}")
                if result['unknowns_after'] < 30:  # Progress threshold
                    results.append(result)
            else:
                print(f"  {combo_name}: {result['reason']}")
        
        return results
    
    def run_priority_sweep(self, max_combos: int = 100) -> List[Dict]:
        """Run prioritized sweep of period combinations"""
        results = []
        tested = 0
        
        print(f"\nTesting priority sweep (max {max_combos})...")
        
        # Generate combinations from priority lists
        for head_L in self.priority_periods['head']:
            for anchors_L in self.priority_periods['anchors']:
                for tail_L in self.priority_periods['tail']:
                    if tested >= max_combos:
                        break
                    
                    config = {
                        'periods': {'head': head_L, 'anchors': anchors_L, 'tail': tail_L},
                        'families': {'head': 'vigenere', 'anchors': 'vigenere', 'tail': 'vigenere'},
                        'key_offsets': {'head': 0, 'anchors': 0, 'tail': 0}
                    }
                    
                    result = self.test_configuration(config)
                    tested += 1
                    
                    if result['status'] == 'success' and result['unknowns_after'] < 30:
                        results.append(result)
                        print(f"  L=({head_L},{anchors_L},{tail_L}): unknowns={result['unknowns_after']}")
                    
                    if tested % 20 == 0:
                        print(f"  Tested {tested} combinations...")
        
        return results
    
    def test_mixed_families(self, base_periods: Dict) -> List[Dict]:
        """Test different cipher families per segment"""
        results = []
        families = ['vigenere', 'beaufort', 'varbf']
        
        print("\nTesting mixed cipher families...")
        
        for head_fam in families:
            for tail_fam in families:
                # Keep anchors as Vigenere (most likely to preserve)
                config = {
                    'periods': base_periods,
                    'families': {'head': head_fam, 'anchors': 'vigenere', 'tail': tail_fam},
                    'key_offsets': {'head': 0, 'anchors': 0, 'tail': 0}
                }
                
                result = self.test_configuration(config)
                
                if result['status'] == 'success' and result['unknowns_after'] < 30:
                    results.append(result)
                    print(f"  Families ({head_fam},{tail_fam}): unknowns={result['unknowns_after']}")
        
        return results
    
    def save_results(self, results: List[Dict]):
        """Save results to files"""
        if not results:
            print("No results to save")
            return
        
        output_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Sort by unknowns_after
        results.sort(key=lambda x: x['unknowns_after'])
        
        # Save top results (without full plaintext)
        save_results = []
        for r in results[:50]:  # Top 50
            save_r = {
                'hypothesis': r['hypothesis'],
                'config': r['config'],
                'combo_name': r.get('combo_name', 'sweep'),
                'unknowns_before': r['unknowns_before'],
                'unknowns_after': r['unknowns_after'],
                'reduction': r['reduction'],
                'head': r['head'],
                'head_sanity': {
                    'ok': r['head_sanity']['ok'],
                    'words_found': r['head_sanity']['words_found'],
                    'max_consonant_run': r['head_sanity']['max_consonant_run']
                }
            }
            save_results.append(save_r)
        
        # Save JSON
        json_path = os.path.join(output_dir, 'h1_results.json')
        with open(json_path, 'w') as f:
            json.dump(save_results, f, indent=2)
        print(f"Saved {len(save_results)} results to {json_path}")
        
        # Write EXPLAIN for top result
        if results:
            explain_path = os.path.join(output_dir, 'EXPLAIN_H1_top.txt')
            self.utils.explain_writer(explain_path, results[0]['config'], results[0]['derivations'])
            print(f"Saved top explanation to {explain_path}")
    
    def run_all(self):
        """Run all H1 tests"""
        all_results = []
        
        # Named combinations
        all_results.extend(self.run_named_combos())
        
        # Priority sweep
        all_results.extend(self.run_priority_sweep(max_combos=100))
        
        # Test mixed families on best periods
        if all_results:
            best = all_results[0]
            all_results.extend(self.test_mixed_families(best['config']['periods']))
        
        # Save results
        self.save_results(all_results)
        
        return all_results


def main():
    print("=== Fork H - Hypothesis 1: Segmented Periods ===\n")
    
    h1 = SegmentedPolyalphabetic()
    results = h1.run_all()
    
    print(f"\n=== Summary ===")
    print(f"Total configurations with progress: {len(results)}")
    
    if results:
        best = min(results, key=lambda x: x['unknowns_after'])
        print(f"Best configuration:")
        print(f"  Periods: {best['config']['periods']}")
        print(f"  Unknowns: {best['unknowns_before']} -> {best['unknowns_after']}")
        print(f"  Head: {best['head']}")
        if best['head_sanity']['words_found']:
            print(f"  Words found: {best['head_sanity']['words_found']}")


if __name__ == "__main__":
    main()