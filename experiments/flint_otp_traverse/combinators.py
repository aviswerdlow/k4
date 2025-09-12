#!/usr/bin/env python3
"""
combinators.py

Combine multiple keystreams through various operations for ensemble testing.
If single table keystreams fail, try combinations.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

MASTER_SEED = 1337  # Fixed seed for reproducibility

class KeystreamCombinator:
    """Generate combined keystreams from multiple sources."""
    
    def __init__(self):
        random.seed(MASTER_SEED)
        self.combinations = []
    
    def concatenate(self, ks1: List[int], ks2: List[int], split_point: int = 48) -> List[int]:
        """Concatenate two keystreams at split point."""
        return ks1[:split_point] + ks2[:97-split_point]
    
    def interleave(self, ks1: List[int], ks2: List[int]) -> List[int]:
        """Interleave two keystreams (even from ks1, odd from ks2)."""
        result = []
        for i in range(97):
            if i % 2 == 0:
                result.append(ks1[min(i // 2, len(ks1) - 1)])
            else:
                result.append(ks2[min(i // 2, len(ks2) - 1)])
        return result
    
    def xor_combine(self, ks1: List[int], ks2: List[int]) -> List[int]:
        """XOR combine two keystreams (mod 26)."""
        return [(ks1[i] + ks2[i]) % 26 for i in range(97)]
    
    def difference_combine(self, ks1: List[int], ks2: List[int]) -> List[int]:
        """Difference combine (ks1 - ks2 mod 26)."""
        return [(ks1[i] - ks2[i]) % 26 for i in range(97)]
    
    def weighted_average(self, ks1: List[int], ks2: List[int], w1: float = 0.7) -> List[int]:
        """Weighted average of two keystreams."""
        w2 = 1.0 - w1
        return [int((w1 * ks1[i] + w2 * ks2[i]) % 26) for i in range(97)]
    
    def segment_mix(self, keystreams: List[List[int]], segments: List[int]) -> List[int]:
        """Mix segments from different keystreams."""
        result = []
        ks_idx = 0
        
        for seg_len in segments:
            if ks_idx >= len(keystreams):
                ks_idx = 0
            
            ks = keystreams[ks_idx]
            start = len(result)
            end = min(start + seg_len, 97)
            
            for i in range(start, end):
                result.append(ks[i % len(ks)])
            
            ks_idx += 1
            
            if len(result) >= 97:
                break
        
        return result[:97]
    
    def create_combination(self, ks1_data: Dict, ks2_data: Dict, method: str, params: Dict) -> Dict:
        """Create a combination and document it."""
        ks1 = ks1_data["kstream"]
        ks2 = ks2_data["kstream"]
        
        # Apply combination method
        if method == "concatenate":
            combined = self.concatenate(ks1, ks2, params.get("split", 48))
        elif method == "interleave":
            combined = self.interleave(ks1, ks2)
        elif method == "xor":
            combined = self.xor_combine(ks1, ks2)
        elif method == "difference":
            combined = self.difference_combine(ks1, ks2)
        elif method == "weighted":
            combined = self.weighted_average(ks1, ks2, params.get("weight", 0.7))
        else:
            return None
        
        # Create combination record
        combo_id = f"COMBO_{method}_{ks1_data['recipe_id'][:6]}_{ks2_data['recipe_id'][:6]}"
        
        return {
            "combo_id": combo_id,
            "kstream": combined,
            "method": method,
            "params": params,
            "parent1": {
                "recipe_id": ks1_data["recipe_id"],
                "table": ks1_data["provenance"]["table_id"],
                "family": ks1_data["provenance"]["family"]
            },
            "parent2": {
                "recipe_id": ks2_data["recipe_id"],
                "table": ks2_data["provenance"]["table_id"],
                "family": ks2_data["provenance"]["family"]
            },
            "sample_first_20": {
                "integers": combined[:20],
                "letters": ''.join(chr(65 + k) for k in combined[:20])
            }
        }

def generate_combinations():
    """Generate combined keystreams from existing ones."""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    keystreams_dir = base_path / "experiments/flint_otp_traverse/keystreams"
    combos_dir = base_path / "experiments/flint_otp_traverse/combinations"
    combos_dir.mkdir(parents=True, exist_ok=True)
    
    # Load a sample of keystreams
    all_keystreams = []
    for table_dir in keystreams_dir.glob("TRAVERSE_*"):
        ks_files = list(table_dir.glob("*.json"))[:5]  # Limit per table
        
        for kf in ks_files:
            with open(kf) as f:
                all_keystreams.append(json.load(f))
    
    if len(all_keystreams) < 2:
        print("Not enough keystreams to combine!")
        return
    
    print(f"Loaded {len(all_keystreams)} keystreams for combination")
    
    combinator = KeystreamCombinator()
    combinations = []
    
    # Generate combinations
    methods = [
        ("concatenate", {"split": 48}),
        ("concatenate", {"split": 33}),
        ("concatenate", {"split": 64}),
        ("interleave", {}),
        ("xor", {}),
        ("difference", {}),
        ("weighted", {"weight": 0.7}),
        ("weighted", {"weight": 0.5}),
        ("weighted", {"weight": 0.3})
    ]
    
    # Sample pairs to combine
    random.seed(MASTER_SEED)
    num_combos = min(100, len(all_keystreams) * (len(all_keystreams) - 1) // 2)
    
    print(f"Generating {num_combos} combinations...")
    
    combo_count = 0
    for i in range(len(all_keystreams)):
        for j in range(i + 1, len(all_keystreams)):
            if combo_count >= num_combos:
                break
            
            ks1 = all_keystreams[i]
            ks2 = all_keystreams[j]
            
            # Try different combination methods
            for method, params in methods:
                if combo_count >= num_combos:
                    break
                
                combo = combinator.create_combination(ks1, ks2, method, params)
                
                if combo:
                    combinations.append(combo)
                    
                    # Save combination
                    combo_path = combos_dir / f"{combo['combo_id']}.json"
                    with open(combo_path, 'w') as f:
                        json.dump(combo, f, indent=2)
                    
                    combo_count += 1
    
    print(f"Generated {len(combinations)} combinations")
    
    # Save summary
    summary = {
        "total_combinations": len(combinations),
        "methods_used": list(set(c["method"] for c in combinations)),
        "tables_involved": list(set(
            c["parent1"]["table"] for c in combinations
        ).union(set(
            c["parent2"]["table"] for c in combinations
        ))),
        "master_seed": MASTER_SEED
    }
    
    with open(combos_dir / "COMBO_SUMMARY.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Combinations saved to: {combos_dir}")

def test_combinations():
    """Test combined keystreams against K4."""
    base_path = Path("/Users/aviswerdlow/Downloads/Kryptos Team/k4_cli_plus")
    combos_dir = base_path / "experiments/flint_otp_traverse/combinations"
    results_dir = base_path / "experiments/flint_otp_traverse/results"
    
    # Import test functions
    from test_keystreams import (
        load_ciphertext, load_anchors, vigenere_decode, 
        beaufort_decode, check_anchors, has_consonant_cluster, find_words
    )
    
    ciphertext = load_ciphertext()
    anchors = load_anchors()
    
    combo_files = list(combos_dir.glob("COMBO_*.json"))
    
    if not combo_files:
        print("No combinations found! Run generate_combinations first.")
        return
    
    print(f"Testing {len(combo_files)} combinations...")
    
    passing_combos = []
    tested = 0
    
    for cf in combo_files:
        with open(cf) as f:
            combo = json.load(f)
        
        keystream = combo["kstream"]
        tested += 1
        
        # Test Vigenère
        plaintext_v = vigenere_decode(ciphertext, keystream)
        anchors_pass_v, _ = check_anchors(plaintext_v, anchors)
        
        if anchors_pass_v:
            head_20 = plaintext_v[:20]
            has_cluster = has_consonant_cluster(head_20, 5)
            words_found = find_words(head_20, 4)
            
            result = {
                "combo_id": combo["combo_id"],
                "method": combo["method"],
                "variant": "vigenere",
                "anchors_pass": True,
                "head_no_cc5": not has_cluster,
                "words_found": words_found,
                "plaintext": plaintext_v,
                "parents": [combo["parent1"], combo["parent2"]],
                "acceptance": len(words_found) > 0 and not has_cluster
            }
            
            passing_combos.append(result)
            
            print(f"\n✓ COMBO ANCHORS PASS (Vigenère)!")
            print(f"  ID: {combo['combo_id']}")
            print(f"  Method: {combo['method']}")
            print(f"  Head: {plaintext_v[:40]}")
        
        # Test Beaufort
        plaintext_b = beaufort_decode(ciphertext, keystream)
        anchors_pass_b, _ = check_anchors(plaintext_b, anchors)
        
        if anchors_pass_b:
            head_20 = plaintext_b[:20]
            has_cluster = has_consonant_cluster(head_20, 5)
            words_found = find_words(head_20, 4)
            
            result = {
                "combo_id": combo["combo_id"],
                "method": combo["method"],
                "variant": "beaufort",
                "anchors_pass": True,
                "head_no_cc5": not has_cluster,
                "words_found": words_found,
                "plaintext": plaintext_b,
                "parents": [combo["parent1"], combo["parent2"]],
                "acceptance": len(words_found) > 0 and not has_cluster
            }
            
            passing_combos.append(result)
            
            print(f"\n✓ COMBO ANCHORS PASS (Beaufort)!")
            print(f"  ID: {combo['combo_id']}")
            print(f"  Method: {combo['method']}")
            print(f"  Head: {plaintext_b[:40]}")
        
        if tested % 20 == 0:
            print(f"  Tested {tested}/{len(combo_files)}...")
    
    # Save results
    print(f"\n" + "=" * 70)
    print(f"COMBINATION TESTING COMPLETE")
    print(f"  Combinations tested: {tested}")
    print(f"  Anchors preserved: {len(passing_combos)}")
    print(f"  Full acceptance: {sum(1 for r in passing_combos if r['acceptance'])}")
    
    if passing_combos:
        with open(results_dir / "combo_passing.json", 'w') as f:
            json.dump(passing_combos, f, indent=2)
        
        print(f"\nPassing combinations saved to: combo_passing.json")
    
    # Update topline report
    with open(results_dir / "COMBO_REPORT.md", 'w') as f:
        f.write("# COMBINATION TESTING REPORT\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Combinations tested: {tested}\n")
        f.write(f"- Anchors preserved: {len(passing_combos)}\n")
        f.write(f"- Full acceptance: {sum(1 for r in passing_combos if r['acceptance'])}\n\n")
        
        if passing_combos:
            f.write("## MATCHES FOUND\n\n")
            f.write("Combined keystreams that satisfy anchors:\n\n")
            
            for combo in passing_combos[:10]:
                f.write(f"### {combo['combo_id']}\n")
                f.write(f"- Method: {combo['method']}\n")
                f.write(f"- Variant: {combo['variant']}\n")
                f.write(f"- Parents: {combo['parents'][0]['table']} + {combo['parents'][1]['table']}\n")
                f.write(f"- Acceptance: {combo['acceptance']}\n")
                f.write(f"- Head: `{combo['plaintext'][:40]}...`\n\n")
        else:
            f.write("## NO MATCHES\n\n")
            f.write("No combination of traverse table keystreams satisfies all anchors.\n")

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_combinations()
    else:
        generate_combinations()
        print("\nNow run: python combinators.py test")

if __name__ == "__main__":
    main()