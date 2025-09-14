#!/usr/bin/env python3
"""
Zone Runner - Orchestrates zones, masks, routes, and ciphers for K4 cryptanalysis
"""

import json
import hashlib
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.mask_library import apply_mask, invert_mask
from scripts.route_engine import apply_route, invert_route
from scripts.cipher_families import apply_cipher, KEY_SETS


class ZoneRunner:
    """Main orchestrator for zone-based K4 cryptanalysis"""
    
    def __init__(self, manifest_path: str = None, verbose: bool = False):
        """Initialize with optional manifest file"""
        self.manifest = None
        self.ciphertext = None
        self.plaintext = None
        self.zones = {}
        self.control_mode = None
        self.control_indices = []
        self.verbose = verbose
        
        if manifest_path:
            self.load_manifest(manifest_path)
    
    def load_manifest(self, manifest_path: str):
        """Load manifest from JSON file"""
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)
        
        # Parse zones
        zones_config = self.manifest.get('zones', {})
        self.zones = {
            'head': (zones_config['head']['start'], zones_config['head']['end']),
            'mid': (zones_config['mid']['start'], zones_config['mid']['end']),
            'tail': (zones_config['tail']['start'], zones_config['tail']['end'])
        }
        
        # Parse control settings
        control = self.manifest.get('control', {})
        self.control_mode = control.get('mode', 'content')
        self.control_indices = control.get('indices', [])
    
    def load_ciphertext(self, ct_path: str):
        """Load ciphertext from file"""
        with open(ct_path, 'r') as f:
            self.ciphertext = f.read().strip().upper()
    
    def _get_control_events(self, zone_name: str, zone_start: int, zone_end: int) -> List[int]:
        """Get control event indices for a zone (converted to zone-local offsets)"""
        events = []
        
        # Check for control indices
        if self.control_mode == 'control' and self.control_indices:
            for idx in self.control_indices:
                if zone_start <= idx <= zone_end:
                    local_offset = idx - zone_start
                    if local_offset not in events:
                        events.append(local_offset)
        
        # Check for schedule-specific indices
        if 'cipher' in self.manifest:
            schedule = self.manifest['cipher'].get('schedule', 'static')
            if schedule == 'rotate_on_control':
                params = self.manifest['cipher'].get('schedule_params', {})
                for idx in params.get('indices', []):
                    if zone_start <= idx <= zone_end:
                        local_offset = idx - zone_start
                        if local_offset not in events:
                            events.append(local_offset)
        
        return sorted(events)
    
    def _apply_with_control(self, zone_text: str, zone_name: str, zone_start: int, 
                           zone_end: int, stage: str) -> str:
        """Apply a stage (mask/route/cipher) with control-mode events"""
        events = self._get_control_events(zone_name, zone_start, zone_end)
        
        if not events or self.control_mode != 'control':
            # No control events, apply normally
            if stage == 'mask' and 'mask' in self.manifest:
                return apply_mask(zone_text, self.manifest['mask'])
            elif stage == 'route' and 'route' in self.manifest:
                return apply_route(zone_text, self.manifest['route'])
            elif stage == 'cipher' and 'cipher' in self.manifest:
                cipher_config = self.manifest['cipher'].copy()
                if 'keys' in cipher_config and zone_name in cipher_config['keys']:
                    zone_key = cipher_config['keys'][zone_name]
                    cipher_config['keys'] = {zone_name: zone_key}
                    zone_zones = {zone_name: (0, len(zone_text) - 1)}
                    return apply_cipher(zone_text, cipher_config, zone_zones, 'decrypt')
            return zone_text
        
        # Process with control events
        result = []
        segments = []
        
        # Create segments based on events
        prev = 0
        for event in events:
            if event > prev:
                segments.append((prev, event))
                prev = event
        if prev < len(zone_text):
            segments.append((prev, len(zone_text)))
        
        # Process each segment
        for seg_idx, (seg_start, seg_end) in enumerate(segments):
            segment = zone_text[seg_start:seg_end]
            
            if stage == 'cipher' and 'cipher' in self.manifest:
                cipher_config = self.manifest['cipher'].copy()
                
                # Handle key rotation
                schedule = cipher_config.get('schedule', 'static')
                if schedule == 'rotate_on_control' and seg_idx > 0:
                    # Rotate key by number of control events passed
                    if 'keys' in cipher_config and zone_name in cipher_config['keys']:
                        zone_key = cipher_config['keys'][zone_name]
                        key_offset = seg_idx
                        rotated_key = zone_key[key_offset:] + zone_key[:key_offset]
                        cipher_config['keys'] = {zone_name: rotated_key}
                else:
                    if 'keys' in cipher_config and zone_name in cipher_config['keys']:
                        zone_key = cipher_config['keys'][zone_name]
                        cipher_config['keys'] = {zone_name: zone_key}
                
                # Handle family overrides
                if 'family_overrides' in cipher_config and zone_name == 'mid':
                    overrides = cipher_config['family_overrides']
                    abs_pos = zone_start + seg_start
                    
                    # Check if we should switch family
                    switch_at = overrides.get('mid_switch_at', -1)
                    revert_at = overrides.get('mid_revert_at', -1)
                    
                    if switch_at >= 0 and abs_pos >= switch_at:
                        if revert_at < 0 or abs_pos < revert_at:
                            cipher_config['family'] = overrides.get('mid_after', 'beaufort')
                
                zone_zones = {zone_name: (0, len(segment) - 1)}
                segment = apply_cipher(segment, cipher_config, zone_zones, 'decrypt')
            
            elif stage == 'mask' and 'mask' in self.manifest:
                mask_config = self.manifest['mask'].copy()
                
                # Handle mask overrides
                if 'mask_overrides' in self.manifest and zone_name == 'mid':
                    overrides = self.manifest['mask_overrides']
                    abs_pos = zone_start + seg_start
                    switch_at = overrides.get('mid_switch_at', -1)
                    
                    if switch_at >= 0 and abs_pos >= switch_at:
                        mask_config = overrides.get('after', mask_config)
                
                segment = apply_mask(segment, mask_config)
            
            elif stage == 'route' and 'route' in self.manifest:
                route_config = self.manifest['route'].copy()
                
                # Handle route overrides (e.g., flip serpentine direction)
                if 'route_overrides' in self.manifest:
                    overrides = self.manifest['route_overrides']
                    abs_pos = zone_start + seg_start
                    flip_at = overrides.get('flip_at', -1)
                    
                    if flip_at >= 0 and abs_pos >= flip_at:
                        # For serpentine, flip the direction
                        if route_config.get('type') == 'serpentine':
                            route_config['flipped'] = True
                
                segment = apply_route(segment, route_config)
            
            result.append(segment)
        
        return ''.join(result)
    
    def decrypt(self, ciphertext: str = None) -> str:
        """
        Decrypt ciphertext using manifest configuration
        
        Returns:
            Decrypted plaintext
        """
        if ciphertext:
            self.ciphertext = ciphertext.upper()
        
        if not self.ciphertext:
            raise ValueError("No ciphertext loaded")
        
        if not self.manifest:
            raise ValueError("No manifest loaded")
        
        # Verbose logging: Initial state
        if self.verbose:
            control_start = 64
            control_end = 74
            print(f"\n=== DECRYPT PIPELINE TRACE ===")
            print(f"stage_0_CT[{control_start}:{control_end}]: {self.ciphertext[control_start:control_end]}")
        
        # Process each zone
        result = list(self.ciphertext)
        
        for zone_name, (start, end) in self.zones.items():
            zone_text = self.ciphertext[start:end+1]
            original_zone = zone_text
            
            # Determine processing order
            order = self.manifest.get('order', ['mask', 'route', 'cipher'])
            
            # Process stages in order
            for stage in order:
                if stage == 'mask' and 'mask' in self.manifest:
                    zone_text = self._apply_with_control(zone_text, zone_name, start, end, 'mask')
                    if self.verbose and zone_name == 'mid':
                        temp_result = list(self.ciphertext)
                        for i, char in enumerate(zone_text):
                            if start + i <= end:
                                temp_result[start + i] = char
                        temp_full = ''.join(temp_result)
                        print(f"stage_1_mask_out[{control_start}:{control_end}]: {temp_full[control_start:control_end]}")
                
                elif stage == 'route' and 'route' in self.manifest:
                    zone_text = self._apply_with_control(zone_text, zone_name, start, end, 'route')
                    if self.verbose and zone_name == 'mid':
                        temp_result = list(self.ciphertext)
                        for i, char in enumerate(zone_text):
                            if start + i <= end:
                                temp_result[start + i] = char
                        temp_full = ''.join(temp_result)
                        print(f"stage_2_route_out[{control_start}:{control_end}]: {temp_full[control_start:control_end]}")
                
                elif stage == 'cipher' and 'cipher' in self.manifest:
                    zone_text = self._apply_with_control(zone_text, zone_name, start, end, 'cipher')
                    if self.verbose and zone_name == 'mid':
                        temp_result = list(self.ciphertext)
                        for i, char in enumerate(zone_text):
                            if start + i <= end:
                                temp_result[start + i] = char
                        temp_full = ''.join(temp_result)
                        print(f"stage_3_cipher_out[{control_start}:{control_end}]: {temp_full[control_start:control_end]}")
            
            # Place decrypted text back
            for i, char in enumerate(zone_text):
                if start + i <= end:
                    result[start + i] = char
        
        self.plaintext = ''.join(result)
        
        # Verbose logging: Final state
        if self.verbose:
            print(f"final_PT[{control_start}:{control_end}]: {self.plaintext[control_start:control_end]}")
            print(f"=== END TRACE ===\n")
        
        # Verify BERLINCLOCK if in content mode
        if self.control_mode == 'content':
            control_text = ''.join([self.plaintext[i] for i in self.control_indices if i < len(self.plaintext)])
            if control_text != 'BERLINCLOCK':
                print(f"Warning: BERLINCLOCK not found at control indices. Got: {control_text}")
        
        return self.plaintext
    
    def encrypt(self, plaintext: str = None) -> str:
        """
        Encrypt plaintext using manifest configuration (for round-trip validation)
        
        Returns:
            Encrypted ciphertext
        """
        if plaintext:
            self.plaintext = plaintext.upper()
        
        if not self.plaintext:
            raise ValueError("No plaintext to encrypt")
        
        if not self.manifest:
            raise ValueError("No manifest loaded")
        
        # Process each zone (reverse order of operations)
        result = list(self.plaintext)
        
        for zone_name, (start, end) in self.zones.items():
            zone_text = self.plaintext[start:end+1]
            
            # Apply cipher (encrypt)
            if 'cipher' in self.manifest:
                cipher_config = self.manifest['cipher'].copy()
                
                # Handle zone-specific keys
                if 'keys' in cipher_config and zone_name in cipher_config['keys']:
                    zone_key = cipher_config['keys'][zone_name]
                    cipher_config['keys'] = {zone_name: zone_key}
                    
                    # Encrypt zone text
                    zone_zones = {zone_name: (0, len(zone_text) - 1)}
                    zone_text = apply_cipher(zone_text, cipher_config, zone_zones, 'encrypt')
            
            # Invert route if configured
            if 'route' in self.manifest:
                zone_text = invert_route(zone_text, self.manifest['route'])
            
            # Invert mask if configured
            if 'mask' in self.manifest:
                zone_text = invert_mask(zone_text, self.manifest['mask'])
            
            # Place encrypted text back
            for i, char in enumerate(zone_text):
                if start + i <= end:
                    result[start + i] = char
        
        return ''.join(result)
    
    def verify_roundtrip(self) -> bool:
        """Verify that decrypt -> encrypt produces original ciphertext"""
        if not self.ciphertext:
            return False
        
        # Decrypt
        plaintext = self.decrypt()
        
        # Re-encrypt
        re_encrypted = self.encrypt(plaintext)
        
        # Compare
        return re_encrypted == self.ciphertext
    
    def generate_receipts(self) -> Dict[str, Any]:
        """Generate receipts for this run"""
        receipts = {
            'timestamp': datetime.now().isoformat(),
            'manifest_hash': hashlib.sha256(json.dumps(self.manifest, sort_keys=True).encode()).hexdigest(),
            'ciphertext_hash': hashlib.sha256(self.ciphertext.encode()).hexdigest() if self.ciphertext else None,
            'plaintext_hash': hashlib.sha256(self.plaintext.encode()).hexdigest() if self.plaintext else None,
            'roundtrip_valid': self.verify_roundtrip() if self.ciphertext else None,
            'zones': self.zones,
            'control_mode': self.control_mode,
            'berlinclock_verified': False
        }
        
        # Check BERLINCLOCK
        if self.plaintext and self.control_indices:
            control_text = ''.join([self.plaintext[i] for i in self.control_indices if i < len(self.plaintext)])
            receipts['berlinclock_verified'] = (control_text == 'BERLINCLOCK')
            receipts['control_text'] = control_text
        
        return receipts
    
    def run_batch(self, batch_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run a batch of experiments based on configuration"""
        results = []
        
        # Extract parameter ranges
        masks = batch_config.get('masks', [])
        routes = batch_config.get('routes', [])
        ciphers = batch_config.get('ciphers', [])
        keys = batch_config.get('keys', {})
        schedules = batch_config.get('schedules', ['static'])
        modes = batch_config.get('modes', ['content'])
        
        # Generate all combinations
        for mask in masks:
            for route in routes:
                for cipher_family in ciphers:
                    for schedule in schedules:
                        for mode in modes:
                            # Build manifest
                            manifest = {
                                'zones': self.manifest.get('zones') if self.manifest else {
                                    'head': {'start': 0, 'end': 20},
                                    'mid': {'start': 34, 'end': 62},
                                    'tail': {'start': 74, 'end': 96}
                                },
                                'control': {
                                    'mode': mode,
                                    'indices': [64, 65, 66, 67, 68, 69, 70, 71, 72, 73]
                                },
                                'mask': mask,
                                'route': route,
                                'cipher': {
                                    'family': cipher_family,
                                    'keys': keys,
                                    'schedule': schedule
                                }
                            }
                            
                            # Run experiment
                            self.manifest = manifest
                            try:
                                plaintext = self.decrypt()
                                receipts = self.generate_receipts()
                                
                                results.append({
                                    'manifest': manifest,
                                    'receipts': receipts,
                                    'plaintext_preview': plaintext[:50] if plaintext else None
                                })
                                
                                # Log successful candidates
                                if receipts.get('berlinclock_verified'):
                                    print(f"✓ Found candidate with BERLINCLOCK!")
                                    print(f"  Mask: {mask.get('type')}")
                                    print(f"  Route: {route.get('type')}")
                                    print(f"  Cipher: {cipher_family}")
                                    print(f"  Plaintext preview: {plaintext[:30]}...")
                            
                            except Exception as e:
                                print(f"Error in batch run: {e}")
                                continue
        
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Zone Runner for K4 Cryptanalysis')
    parser.add_argument('--manifest', required=True, help='Path to manifest JSON file')
    parser.add_argument('--ct', help='Path to ciphertext file')
    parser.add_argument('--output', help='Output directory for results')
    parser.add_argument('--batch', action='store_true', help='Run in batch mode')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = ZoneRunner(args.manifest)
    
    # Load ciphertext if provided
    if args.ct:
        runner.load_ciphertext(args.ct)
    else:
        # Use default ciphertext path
        ct_path = Path(__file__).parent.parent.parent.parent / '02_DATA' / 'ciphertext_97.txt'
        if ct_path.exists():
            runner.load_ciphertext(str(ct_path))
    
    # Run based on mode
    if args.batch:
        # Load batch configuration from manifest
        with open(args.manifest, 'r') as f:
            batch_config = json.load(f)
        
        results = runner.run_batch(batch_config)
        
        # Save results
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = output_dir / f'batch_results_{timestamp}.json'
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Results saved to: {output_file}")
            print(f"Total experiments: {len(results)}")
            
            # Count successful candidates
            successful = [r for r in results if r['receipts'].get('berlinclock_verified')]
            print(f"Successful candidates: {len(successful)}")
    
    else:
        # Single run mode
        plaintext = runner.decrypt()
        receipts = runner.generate_receipts()
        
        print(f"Plaintext: {plaintext}")
        print(f"Round-trip valid: {receipts['roundtrip_valid']}")
        print(f"BERLINCLOCK verified: {receipts['berlinclock_verified']}")
        
        # Save results if output specified
        if args.output:
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save manifest
            manifest_file = output_dir / f'manifest_{timestamp}.json'
            with open(manifest_file, 'w') as f:
                json.dump(runner.manifest, f, indent=2)
            
            # Save receipts
            receipts_file = output_dir / f'receipts_{timestamp}.json'
            with open(receipts_file, 'w') as f:
                json.dump(receipts, f, indent=2)
            
            # Save plaintext
            if plaintext:
                plaintext_file = output_dir / f'plaintext_{timestamp}.txt'
                with open(plaintext_file, 'w') as f:
                    f.write(plaintext)
            
            print(f"Results saved to: {output_dir}")


if __name__ == '__main__':
    main()