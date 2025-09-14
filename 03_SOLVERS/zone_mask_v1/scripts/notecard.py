#!/usr/bin/env python3
"""
Notecard Generator - Creates single-page human-readable explanations
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any


class NotecardGenerator:
    """Generate single-page notecard explanations for K4 solutions"""
    
    def __init__(self, manifest_path: str):
        """Initialize with manifest"""
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
    
    def generate(self) -> str:
        """Generate notecard content"""
        lines = []
        lines.append("# K4 Recipe (One Page)\n")
        
        # Extract configuration
        zones = self.manifest.get('zones', {})
        mask = self.manifest.get('mask', {})
        route = self.manifest.get('route', {})
        cipher = self.manifest.get('cipher', {})
        control = self.manifest.get('control', {})
        
        # Step counter
        step = 1
        
        # Step 1: Grid setup
        if route.get('type') in ['columnar', 'serpentine', 'spiral', 'tumble']:
            rows = route.get('params', {}).get('rows', 7)
            cols = route.get('params', {}).get('cols', 14)
            lines.append(f"{step}. Write the 97 ciphertext letters into a {rows}×{cols} grid row-wise.")
            if rows * cols > 97:
                lines.append(f"   Leave the last {rows * cols - 97} cell(s) blank.")
            step += 1
        
        # Step 2: Apply mask
        if mask.get('type'):
            mask_desc = self._describe_mask(mask)
            lines.append(f"{step}. Apply Mask: {mask_desc}")
            lines.append(f"   Record the order map for reversal.")
            step += 1
        
        # Step 3: Apply route
        if route.get('type'):
            route_desc = self._describe_route(route)
            lines.append(f"{step}. Route: {route_desc}")
            step += 1
        
        # Step 4: Apply cipher
        if cipher.get('family'):
            cipher_desc = self._describe_cipher(cipher)
            lines.append(f"{step}. Cipher: {cipher_desc}")
            
            # Add key rotation info if applicable
            if cipher.get('schedule') == 'rotate_on_control':
                indices = cipher.get('schedule_params', {}).get('indices', [])
                if indices:
                    lines.append(f"   Rotate the key at indices {', '.join(map(str, indices))} only.")
            step += 1
        
        # Step 5: Process zones
        lines.append(f"{step}. Process zones separately:")
        lines.append(f"   HEAD: positions {zones['head']['start']}-{zones['head']['end']}")
        lines.append(f"   MID: positions {zones['mid']['start']}-{zones['mid']['end']}")
        lines.append(f"   TAIL: positions {zones['tail']['start']}-{zones['tail']['end']}")
        step += 1
        
        # Step 6: Verify
        lines.append(f"{step}. Verify: Re-encrypt using steps {step-1} to 1 in reverse")
        lines.append(f"   to reproduce the published ciphertext.")
        step += 1
        
        # Add BERLINCLOCK note if applicable
        if control.get('mode') == 'content':
            indices = control.get('indices', [])
            if indices:
                lines.append(f"\nNote: Positions {indices[0]}-{indices[-1]} should read 'BERLINCLOCK' after decryption.")
        
        return '\n'.join(lines)
    
    def _describe_mask(self, mask: Dict[str, Any]) -> str:
        """Generate human-readable mask description"""
        mask_type = mask.get('type')
        params = mask.get('params', {})
        
        descriptions = {
            'period2': "periodic interleave with period 2 (alternating positions)",
            'period3': "periodic interleave with period 3",
            'cycle3': "3-cycle rotation (rotate every 3 characters)",
            'cycle5': "5-cycle rotation (rotate every 5 characters)",
            'diag_weave': f"diagonal weave with step {params.get('step', [1,1])}",
            'alt_sheet': f"alternating sheet, take every {params.get('n', 3)}th character",
            'fib_skip': "Fibonacci skip pattern",
            'lowfreq_smoother': f"duplicate low-frequency letters at residue {params.get('residue', 3)}"
        }
        
        return descriptions.get(mask_type, f"{mask_type} mask")
    
    def _describe_route(self, route: Dict[str, Any]) -> str:
        """Generate human-readable route description"""
        route_type = route.get('type')
        params = route.get('params', {})
        
        if route_type == 'columnar':
            desc = "columnar read"
            if params.get('key_order'):
                desc += f" with key order {params['key_order']}"
            if params.get('passes', 1) > 1:
                desc += f", {params['passes']} passes"
                if params.get('row_flip_between_passes'):
                    desc += " (flip rows between passes)"
        
        elif route_type == 'serpentine':
            desc = "serpentine S-read (alternating row direction)"
        
        elif route_type == 'spiral':
            direction = params.get('direction', 'in')
            desc = f"spiral {'inward' if direction == 'in' else 'outward'}"
        
        elif route_type == 'tumble':
            rotations = params.get('rotations', 1)
            desc = f"tumble route ({rotations}×90° rotation)"
            if params.get('second_pass_flip'):
                desc += " with horizontal flip"
        
        else:
            desc = f"{route_type} route"
        
        return desc
    
    def _describe_cipher(self, cipher: Dict[str, Any]) -> str:
        """Generate human-readable cipher description"""
        family = cipher.get('family', 'vigenere').capitalize()
        keys = cipher.get('keys', {})
        
        # Get first key for example
        key_example = None
        if keys:
            if 'head' in keys:
                key_example = keys['head']
            elif 'mid' in keys:
                key_example = keys['mid']
            else:
                key_example = list(keys.values())[0]
        
        desc = f"{family} cipher"
        if key_example:
            desc += f" with key {key_example}"
        
        return desc
    
    def save(self, output_path: str):
        """Save notecard to file"""
        content = self.generate()
        
        # Check length (approximate page limit)
        lines = content.split('\n')
        if len(lines) > 40:
            print(f"Warning: Notecard has {len(lines)} lines (target: <40 for one page)")
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"Notecard saved to: {output_path}")
        print(f"Lines: {len(lines)}")
        print(f"Characters: {len(content)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='K4 Notecard Generator')
    parser.add_argument('--manifest', required=True, help='Path to manifest JSON file')
    parser.add_argument('--out', required=True, help='Output path for notecard')
    
    args = parser.parse_args()
    
    # Generate notecard
    generator = NotecardGenerator(args.manifest)
    content = generator.generate()
    
    # Display preview
    print("Notecard Preview:")
    print("-" * 60)
    print(content)
    print("-" * 60)
    
    # Save to file
    generator.save(args.out)


if __name__ == '__main__':
    main()