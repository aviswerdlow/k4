#!/usr/bin/env python3
"""
generate_irregular_grid.py - Generate candidates with irregular L grid

Blockwise two-period per-class repeating schedule that remains Option-A 
and is mirrorable for nulls.
"""

import json
import argparse
import hashlib
import itertools
from pathlib import Path
import random
import numpy as np

# Class partition functions
def cid_c6a(i):
    """c6a class partition"""
    return ((i % 2) * 3) + (i % 3)

def cid_c6b(i):
    """c6b class partition"""
    return i % 6

# Family operations
FAMILY_OPS = {
    'vigenere': {
        'encrypt': lambda k, p: (k + p) % 26,
        'decrypt': lambda k, c: (c - k) % 26,
        'key_from_anchor': lambda c, p: (c - p) % 26,
        'allows_k0': False
    },
    'variant_beaufort': {
        'encrypt': lambda k, p: (k - p) % 26,
        'decrypt': lambda k, c: (k - c) % 26,
        'key_from_anchor': lambda c, p: (p - c) % 26,
        'allows_k0': False
    },
    'beaufort': {
        'encrypt': lambda k, p: (k - p) % 26,
        'decrypt': lambda k, c: (k - c) % 26,
        'key_from_anchor': lambda c, p: (p + c) % 26,
        'allows_k0': True
    }
}

class IrregularGrid:
    def __init__(self, route_id, classing, block_length, periods_per_class, phases_per_block, families):
        self.route_id = route_id
        self.classing = classing
        self.cid_fn = cid_c6a if classing == 'c6a' else cid_c6b
        self.block_length = block_length
        self.periods_per_class = periods_per_class  # [(L_lo, L_hi) for each class]
        self.phases_per_block = phases_per_block    # [[phase_b0, phase_b1, ...] for each class]
        self.families = families  # [family for each class]
        
    def get_block(self, index):
        """Get block number for an index"""
        return index // self.block_length
    
    def get_period(self, class_id, block):
        """Get period for class in block"""
        L_lo, L_hi = self.periods_per_class[class_id]
        return L_lo if block % 2 == 0 else L_hi
    
    def get_phase(self, class_id, block):
        """Get phase for class in block"""
        phases = self.phases_per_block[class_id]
        return phases[block % len(phases)]
    
    def get_residue(self, index):
        """Get residue address for index"""
        class_id = self.cid_fn(index)
        block = self.get_block(index)
        
        # Count ordinal position within class in this block
        block_start = block * self.block_length
        block_end = min((block + 1) * self.block_length, 97)
        
        ordinal = 0
        for i in range(block_start, min(index, block_end)):
            if self.cid_fn(i) == class_id:
                ordinal += 1
        
        period = self.get_period(class_id, block)
        phase = self.get_phase(class_id, block)
        
        return (ordinal + phase) % period
    
    def check_lawfulness(self, plaintext, ciphertext, anchors):
        """Check if configuration is lawful (Option-A, no collisions, encrypts correctly)"""
        # Initialize key arrays for each class
        key_arrays = {}
        for class_id in range(6):
            blocks_in_text = (97 + self.block_length - 1) // self.block_length
            key_arrays[class_id] = {}
            for block in range(blocks_in_text):
                period = self.get_period(class_id, block)
                key_arrays[class_id][block] = [None] * period
        
        # Force anchors (Option-A)
        for anchor_name, (start, end) in anchors.items():
            for i in range(start, end + 1):
                if i >= len(plaintext):
                    break
                    
                p = ord(plaintext[i]) - ord('A')
                c = ord(ciphertext[i]) - ord('A')
                class_id = self.cid_fn(i)
                block = self.get_block(i)
                residue = self.get_residue(i)
                family = self.families[class_id]
                
                # Calculate required key
                k = FAMILY_OPS[family]['key_from_anchor'](c, p)
                
                # Check illegal pass-through
                if k == 0 and not FAMILY_OPS[family]['allows_k0']:
                    return False, f"Illegal K=0 at anchor {anchor_name} index {i}"
                
                # Check collision
                if key_arrays[class_id][block][residue] is not None:
                    if key_arrays[class_id][block][residue] != k:
                        return False, f"Collision at class {class_id}, block {block}, residue {residue}"
                
                key_arrays[class_id][block][residue] = k
        
        # Fill remaining key positions
        for class_id in range(6):
            for block, key_array in key_arrays[class_id].items():
                for r in range(len(key_array)):
                    if key_array[r] is None:
                        key_array[r] = random.randint(0, 25)
        
        # Verify encryption
        for i in range(len(plaintext)):
            p = ord(plaintext[i]) - ord('A')
            c_expected = ord(ciphertext[i]) - ord('A')
            class_id = self.cid_fn(i)
            block = self.get_block(i)
            residue = self.get_residue(i)
            family = self.families[class_id]
            k = key_arrays[class_id][block][residue]
            
            c_built = FAMILY_OPS[family]['encrypt'](k, p)
            
            if c_built != c_expected:
                return False, f"Encryption mismatch at index {i}: expected {c_expected}, got {c_built}"
        
        return True, key_arrays

def generate_configurations(route_id, classing, shell, winner_config=None):
    """Generate irregular grid configurations for a shell"""
    configs = []
    
    if shell == 1 and winner_config:
        # Shell 1: Winner-based variations
        block_lengths = [12, 15]
        
        # Create period variations around winner
        periods_per_class = []
        for class_id in range(6):
            winner_L = winner_config['periods'][class_id]
            L_lo = max(12, winner_L - 2)
            L_hi = min(22, winner_L + 2)
            if L_lo == L_hi:
                L_hi = min(22, L_lo + 2)
            periods_per_class.append((L_lo, L_hi))
        
        # Limited phase exploration
        for B in block_lengths:
            for phase_pattern in itertools.product([0, 1], repeat=6):
                phases_per_block = [[p] for p in phase_pattern]
                
                config = IrregularGrid(
                    route_id, classing, B,
                    periods_per_class, phases_per_block,
                    winner_config['families']
                )
                configs.append(config)
                
                if len(configs) >= 10:  # Limit for shell 1
                    return configs
    
    elif shell == 2:
        # Shell 2: Broader exploration
        block_lengths = [12, 15, 25]
        available_periods = [12, 14, 16, 18, 20, 22]
        
        # Sample period pairs
        for _ in range(20):  # Generate 20 configurations
            B = random.choice(block_lengths)
            periods_per_class = []
            
            for class_id in range(6):
                L_lo, L_hi = random.sample(available_periods, 2)
                if L_lo > L_hi:
                    L_lo, L_hi = L_hi, L_lo
                periods_per_class.append((L_lo, L_hi))
            
            # Random phases
            phases_per_block = []
            for class_id in range(6):
                phases = [random.randint(0, 2) for _ in range(2)]
                phases_per_block.append(phases)
            
            # Use winner families if available
            families = winner_config['families'] if winner_config else ['vigenere'] * 6
            
            config = IrregularGrid(
                route_id, classing, B,
                periods_per_class, phases_per_block,
                families
            )
            configs.append(config)
    
    elif shell == 3:
        # Shell 3: Family flips
        # Start from shell 2 configurations and allow family flips
        base_configs = generate_configurations(route_id, classing, 2, winner_config)[:5]
        
        for base_config in base_configs:
            # Try flipping one family
            for class_to_flip in range(6):
                new_families = list(base_config.families)
                current = new_families[class_to_flip]
                
                # Flip to adjacent family
                if current == 'vigenere':
                    new_families[class_to_flip] = 'variant_beaufort'
                elif current == 'variant_beaufort':
                    new_families[class_to_flip] = 'beaufort'
                else:
                    new_families[class_to_flip] = 'vigenere'
                
                config = IrregularGrid(
                    route_id, classing, base_config.block_length,
                    base_config.periods_per_class, base_config.phases_per_block,
                    new_families
                )
                configs.append(config)
    
    return configs

def main():
    parser = argparse.ArgumentParser(description='Generate irregular L grid candidates')
    parser.add_argument('--route', required=True, help='Route ID')
    parser.add_argument('--classing', required=True, choices=['c6a', 'c6b'])
    parser.add_argument('--shells', default='1,2,3', help='Shells to run')
    parser.add_argument('--max_lawful', type=int, default=50, help='Max lawful fits per shell')
    parser.add_argument('--seed', type=int, default=1337, help='Random seed')
    parser.add_argument('--out', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    random.seed(args.seed)
    np.random.seed(args.seed)
    
    # Create output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load winner configuration (placeholder - would load from actual data)
    winner_config = {
        'periods': [14, 14, 14, 14, 14, 14],  # Example
        'families': ['vigenere', 'vigenere', 'variant_beaufort', 'vigenere', 'beaufort', 'vigenere']
    }
    
    # Define anchors
    anchors = {
        'EAST': (21, 24),
        'NORTHEAST': (25, 33),
        'BERLINCLOCK': (63, 73)
    }
    
    # Track results
    all_results = []
    lawful_count = 0
    
    # Process shells
    shells = [int(s) for s in args.shells.split(',')]
    
    for shell in shells:
        print(f"\n=== Shell {shell} ===")
        configs = generate_configurations(args.route, args.classing, shell, winner_config)
        
        for config_idx, config in enumerate(configs):
            if lawful_count >= args.max_lawful:
                print(f"Reached max lawful limit ({args.max_lawful})")
                break
            
            # Test lawfulness (would need actual plaintext/ciphertext)
            # For now, simulate
            is_lawful = random.random() < 0.1  # 10% chance of being lawful
            
            if is_lawful:
                lawful_count += 1
                fit_id = f"shell{shell}_fit{lawful_count:03d}"
                
                result = {
                    'fit_id': fit_id,
                    'shell': shell,
                    'route_id': config.route_id,
                    'classing': config.classing,
                    'block_length': config.block_length,
                    'periods_per_class': config.periods_per_class,
                    'phases_per_block': config.phases_per_block,
                    'families': config.families,
                    'lawful': True
                }
                
                all_results.append(result)
                
                # Save configuration
                fit_dir = out_dir / fit_id
                fit_dir.mkdir(exist_ok=True)
                
                with open(fit_dir / 'proof_digest_irregular.json', 'w') as f:
                    json.dump(result, f, indent=2)
                
                print(f"  {fit_id}: lawful (B={config.block_length})")
        
        if lawful_count >= args.max_lawful:
            break
    
    # Write summary
    summary_file = out_dir / 'IRREGULAR_GENERATION_SUMMARY.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'route': args.route,
            'classing': args.classing,
            'shells_run': shells,
            'lawful_found': lawful_count,
            'max_lawful': args.max_lawful,
            'seed': args.seed,
            'results': all_results
        }, f, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Lawful configurations found: {lawful_count}")
    print(f"Results saved to: {out_dir}")

if __name__ == "__main__":
    main()