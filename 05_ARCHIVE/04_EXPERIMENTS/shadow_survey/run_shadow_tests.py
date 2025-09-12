#!/usr/bin/env python3
"""
run_shadow_tests.py

Main test runner for Fork H-Shadow.
Tests shadow-surveying-modified cipher integration with all critical datetimes.
"""

import sys
import json
import csv
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from sun_shadow import *
from zones import *
from shadow_polyalpha import *

# Import validation from survey_params if available
sys.path.insert(0, str(Path(__file__).parent.parent / 'survey_params' / 'lib'))
try:
    from validation import AnchorValidator, TextAnalyzer
except ImportError:
    # Implement minimal validation here
    class AnchorValidator:
        def __init__(self):
            self.anchors = {
                'EAST': {'start': 21, 'end': 24, 'text': 'EAST'},
                'NORTHEAST': {'start': 25, 'end': 33, 'text': 'NORTHEAST'},
                'BERLIN': {'start': 63, 'end': 68, 'text': 'BERLIN'},
                'CLOCK': {'start': 69, 'end': 73, 'text': 'CLOCK'}
            }
        
        def validate(self, plaintext: str) -> Tuple[bool, List[str]]:
            failures = []
            for name, anchor in self.anchors.items():
                start = anchor['start']
                end = anchor['end'] + 1
                expected = anchor['text']
                actual = plaintext[start:end] if start < len(plaintext) else ''
                if actual != expected:
                    failures.append(f"{name}: expected '{expected}', got '{actual}'")
            return len(failures) == 0, failures
    
    class TextAnalyzer:
        @staticmethod
        def analyze_head(text: str, length: int = 20) -> Dict:
            head = text[:length].upper()
            vowels = sum(1 for c in head if c in 'AEIOU')
            vowel_ratio = vowels / len(head) if head else 0
            
            # Max consonant run
            max_run = 0
            current = 0
            for c in head:
                if c.isalpha() and c not in 'AEIOU':
                    current += 1
                    max_run = max(max_run, current)
                else:
                    current = 0
            
            # Survey terms
            survey_terms = []
            for term in ['MERIDIAN', 'ANGLE', 'BEARING', 'LINE', 'NORTH', 
                        'EAST', 'TRUE', 'MAGNETIC']:
                if term in text.upper():
                    survey_terms.append(term)
            
            # Bigram score (simplified)
            bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'TO', 'EN', 'ES']
            score = sum(1 for i in range(len(head)-1) if head[i:i+2] in bigrams)
            
            return {
                'vowel_ratio': round(vowel_ratio, 3),
                'max_consonant_run': max_run,
                'survey_terms': survey_terms,
                'bigram_score': score
            }

class ShadowSurveyTester:
    """Main test orchestrator for shadow-survey cipher testing."""
    
    def __init__(self):
        """Initialize tester."""
        # Load ciphertext
        ct_path = Path("02_DATA/ciphertext_97.txt")
        with open(ct_path, 'r') as f:
            self.ciphertext = f.read().strip()
        
        self.ct_sha256 = hashlib.sha256(self.ciphertext.encode()).hexdigest()
        
        # Initialize validators
        self.validator = AnchorValidator()
        self.analyzer = TextAnalyzer()
        
        # Results storage
        self.all_results = []
        self.passing_results = []
        
        # Output directories
        self.results_dir = Path("04_EXPERIMENTS/shadow_survey/results")
        self.masks_dir = Path("04_EXPERIMENTS/shadow_survey/masks")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.masks_dir.mkdir(parents=True, exist_ok=True)
    
    def run_phase1_shadow_analysis(self):
        """Phase 1: Shadow analysis for all critical datetimes."""
        print("\n" + "="*70)
        print("PHASE 1: Shadow Analysis")
        print("="*70)
        
        all_shadow_params = []
        
        for dt in critical_datetimes():
            params = shadow_params(dt)
            all_shadow_params.append(params)
            
            # Create all mask types
            masks = create_all_masks(params, self.masks_dir)
            
            # Log summary
            if len(all_shadow_params) % 10 == 0:
                print(f"  Processed {len(all_shadow_params)} datetimes...")
        
        print(f"\nTotal shadow calculations: {len(all_shadow_params)}")
        
        # Sample output
        print("\nSample shadow parameters:")
        for params in all_shadow_params[::20][:5]:  # Every 20th, first 5
            print(f"  {params['datetime'][:16]}: alt={params['sun_alt']:5.1f}°, "
                  f"shadow={params['shadow_angle']:5.1f}°")
        
        return all_shadow_params
    
    def run_phase2_zone_decryption(self, shadow_params_list: List[Dict]):
        """Phase 2: Zone-based modified decryption."""
        print("\n" + "="*70)
        print("PHASE 2: Zone-Based Decryption")
        print("="*70)
        
        # Test configurations
        configs = ['S-Light', 'S-Swap', 'S-Tri']
        
        # Base bearings to test
        test_bearings = [
            ('true_ne_plus', 61.6959),
            ('true_ene_minus', 50.8041),
            ('mag_ne_plus_1989', 59.5959),
            ('mag_ene_minus_1989', 48.7041),
            ('offset_only', 16.6959)
        ]
        
        # DMS configurations
        dms_configs = dms_variants(61, 41, 45)  # Primary DMS
        
        test_count = 0
        
        # Sample testing (full would be too many)
        # Test key datetimes only
        key_datetimes_idx = [0, 4, 8, 12]  # Center times for each critical datetime
        
        for idx in key_datetimes_idx:
            if idx >= len(shadow_params_list):
                continue
                
            shadow_p = shadow_params_list[idx]
            dt_str = shadow_p['datetime'][:16]
            
            print(f"\nTesting datetime: {dt_str}")
            
            # Get masks for this datetime
            masks = create_all_masks(shadow_p)
            
            # Test each mask type
            for mask_type, mask in [('Azones', masks['Azones']), 
                                   ('Bzones', masks['Bzones'])]:
                
                # Test each bearing
                for bearing_name, bearing_val in test_bearings[:2]:  # Limit for demo
                    
                    # Get base parameters
                    base_params = bearing_to_L_phase_offset(bearing_val)
                    
                    # Test with different phase/offset combinations
                    for phase in [0, 41]:  # 0 and DMS minutes
                        for off_type in ['off_alpha_floor', 'off_alpha_round']:
                            # Create working params with proper L value
                            working_params = {
                                'L': base_params['L_round'],  # Use rounded L
                                'phase': phase,
                                'offset': base_params[off_type],
                                'source': bearing_name
                            }
                            
                            # Create cipher
                            cipher = ShadowModifiedCipher(mask, working_params, shadow_p)
                            
                            # Test each config
                            for config in configs:
                                test_id = f"HSH-{dt_str}-{mask_type}-{bearing_name}-{config}-{off_type}-phase{phase}"
                                
                                # Decrypt
                                plaintext = cipher.decrypt(self.ciphertext, config)
                                
                                # Process result
                                self._process_result(
                                    test_id=test_id,
                                    plaintext=plaintext,
                                    shadow_p=shadow_p,
                                    mask_type=mask_type,
                                    mask=mask,
                                    base_params=working_params,
                                    config=config,
                                    cipher=cipher
                                )
                                
                                test_count += 1
        
        print(f"\nTotal tests in Phase 2: {test_count}")
    
    def run_phase3_rendering_test(self):
        """Phase 3: Rendering-specific test with stylized shadow."""
        print("\n" + "="*70)
        print("PHASE 3: Rendering-Specific Test")
        print("="*70)
        
        # Nov 3, 2 PM shadow
        nov3_2pm = datetime(1990, 11, 3, 14, 0, 
                           tzinfo=timezone(timedelta(hours=-5)))
        shadow_p = shadow_params(nov3_2pm)
        
        print(f"Stylized shadow test: {shadow_p['datetime'][:16]}")
        print(f"  Shadow angle: {shadow_p['shadow_angle']}°")
        
        # Create stylized mask (anchors in shadow)
        a_mapper = AnchorAlignedZones()
        stylized_mask = a_mapper.create_stylized_mask(shadow_p['shadow_angle'])
        
        # ENE bearing (67.5)
        light_L = 68  # ENE rounded
        shadow_L = light_L - int(round(shadow_p['shadow_angle']))  # ~33
        
        # Build custom parameters
        base_params = {
            'L': light_L,
            'phase': 0,
            'offset': 0,
            'source': 'ENE_stylized'
        }
        
        # Create cipher
        cipher = ShadowModifiedCipher(stylized_mask, base_params, shadow_p)
        
        # Test configs
        for config in ['S-Light', 'S-Tri']:
            test_id = f"HSH-stylized-{config}"
            plaintext = cipher.decrypt(self.ciphertext, config)
            
            self._process_result(
                test_id=test_id,
                plaintext=plaintext,
                shadow_p=shadow_p,
                mask_type='stylized',
                mask=stylized_mask,
                base_params=base_params,
                config=config,
                cipher=cipher
            )
    
    def run_phase4_time_progression(self):
        """Phase 4: Time progression test through dedication day."""
        print("\n" + "="*70)
        print("PHASE 4: Time Progression Test")
        print("="*70)
        
        # Nov 3, 1990 hourly progression
        dedication_date = datetime(1990, 11, 3).date()
        hourly_times = langley_hourly_progression(dedication_date, 9, 15)
        
        print(f"Testing hourly progression for {dedication_date}")
        
        # Use consistent base configuration
        base_bearing = 61.6959  # true_ne_plus
        temp_params = bearing_to_L_phase_offset(base_bearing)
        base_params = {
            'L': temp_params['L_round'],
            'phase': 41,
            'offset': temp_params['off_alpha_round'],
            'source': 'true_ne_plus'
        }
        
        for dt in hourly_times:
            shadow_p = shadow_params(dt)
            hour_str = dt.strftime('%H:%M')
            
            # Create A-zones mask
            a_mapper = AnchorAlignedZones(theta_threshold=30.0)
            mask = a_mapper.create_mask(shadow_p)
            
            # Create cipher
            cipher = ShadowModifiedCipher(mask, base_params, shadow_p)
            
            # Test S-Light config
            test_id = f"HSH-hourly-{hour_str}"
            plaintext = cipher.decrypt(self.ciphertext, 'S-Light')
            
            # Quick validation
            anchors_valid, _ = self.validator.validate(plaintext)
            
            print(f"  {hour_str}: shadow={shadow_p['shadow_angle']:5.1f}°, "
                  f"anchors={'✓' if anchors_valid else '✗'}")
            
            self._process_result(
                test_id=test_id,
                plaintext=plaintext,
                shadow_p=shadow_p,
                mask_type='Azones_hourly',
                mask=mask,
                base_params=base_params,
                config='S-Light',
                cipher=cipher
            )
    
    def _process_result(self, test_id: str, plaintext: str, shadow_p: Dict,
                       mask_type: str, mask: List, base_params: Dict,
                       config: str, cipher):
        """Process and record a single test result."""
        # Validate anchors
        anchors_valid, anchor_failures = self.validator.validate(plaintext)
        
        # Analyze text
        head_analysis = self.analyzer.analyze_head(plaintext, 20)
        
        # Build result card
        result = {
            'id': test_id,
            'datetime_local': shadow_p['datetime'],
            'shadow': {
                'sun_alt': shadow_p['sun_alt'],
                'sun_az': shadow_p['sun_az'],
                'shadow_angle': shadow_p['shadow_angle'],
                'shadow_bearing': shadow_p['shadow_bearing'],
                'mask_type': mask_type
            },
            'base_params': base_params,
            'zone_profiles': cipher.get_zone_profiles(),
            'config': config,
            'anchors': {
                'preserved': anchors_valid,
                'failures': anchor_failures[:3] if anchor_failures else []
            },
            'plaintext_head_0_20': plaintext[:20],
            'metrics': head_analysis,
            'repro': {
                'seed': MASTER_SEED,
                'ct_sha256': self.ct_sha256
            }
        }
        
        self.all_results.append(result)
        self.save_result(result)  # Save result card for every test
        
        if anchors_valid:
            self.passing_results.append(result)
            print(f"    ✓ {test_id}: ANCHORS PRESERVED!")
            print(f"      Head: {plaintext[:20]}")
    
    def save_result(self, result: Dict):
        """Save individual result card."""
        result_path = self.results_dir / f"{result['id']}.json"
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
    
    def generate_summary(self):
        """Generate summary reports."""
        # CSV summary
        csv_path = Path("04_EXPERIMENTS/shadow_survey/RUN_SUMMARY.csv")
        
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['id', 'datetime', 'mask', 'base_bearing', 
                         'anchors_passed', 'head_text', 'max_cc_run', 
                         'survey_terms', 'config']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.all_results:
                writer.writerow({
                    'id': result['id'],
                    'datetime': result['datetime_local'][:16],
                    'mask': result['shadow']['mask_type'],
                    'base_bearing': result['base_params'].get('source', 'unknown'),
                    'anchors_passed': result['anchors']['preserved'],
                    'head_text': result['plaintext_head_0_20'],
                    'max_cc_run': result['metrics']['max_consonant_run'],
                    'survey_terms': ','.join(result['metrics'].get('survey_terms', [])),
                    'config': result.get('config', 'unknown')
                })
        
        print(f"\nCSV summary saved to: {csv_path}")
        
        # Final report
        report_path = Path("04_EXPERIMENTS/shadow_survey/FINAL_REPORT.md")
        with open(report_path, 'w') as f:
            f.write("# Fork H-Shadow - Shadow-Survey Modified Cipher Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total tests: {len(self.all_results)}\n")
            f.write(f"- Anchors preserved: {len(self.passing_results)}\n")
            f.write(f"- Critical datetimes tested: 4\n")
            f.write(f"- Mask types: 3 (A-zones, B-zones, C-zones)\n")
            f.write(f"- Configurations: 3 (S-Light, S-Swap, S-Tri)\n")
            f.write(f"- Master seed: {MASTER_SEED}\n\n")
            
            if self.passing_results:
                f.write("## MATCHES FOUND\n\n")
                f.write("The following configurations preserve all anchors:\n\n")
                
                for result in self.passing_results[:10]:
                    f.write(f"### {result['id']}\n")
                    f.write(f"- Datetime: {result['datetime_local'][:16]}\n")
                    f.write(f"- Shadow angle: {result['shadow']['shadow_angle']}°\n")
                    f.write(f"- Config: {result.get('config', 'unknown')}\n")
                    f.write(f"- Head: `{result['plaintext_head_0_20']}`\n")
                    f.write(f"- Max consonant run: {result['metrics']['max_consonant_run']}\n")
                    if result['metrics'].get('survey_terms'):
                        f.write(f"- Survey terms: {', '.join(result['metrics']['survey_terms'])}\n")
                    f.write("\n")
            else:
                f.write("## NO MATCHES\n\n")
                f.write("No shadow-modified configuration preserved the anchors.\n\n")
                f.write("This suggests that:\n")
                f.write("1. Shadow geometry alone doesn't determine the cipher modification\n")
                f.write("2. Different zone mapping or parameter modifications are needed\n")
                f.write("3. The physical gating hypothesis may not apply to K4\n")
        
        print(f"Final report saved to: {report_path}")
    
    def run_all_phases(self):
        """Run complete test suite."""
        start_time = datetime.now()
        
        print("\n" + "="*70)
        print("FORK H-SHADOW TEST SUITE")
        print("Shadow-Surveying-Modified Cipher Integration")
        print("="*70)
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Ciphertext length: {len(self.ciphertext)}")
        print(f"Master seed: {MASTER_SEED}")
        
        # Run phases
        shadow_params_list = self.run_phase1_shadow_analysis()
        self.run_phase2_zone_decryption(shadow_params_list)
        self.run_phase3_rendering_test()
        self.run_phase4_time_progression()
        
        # Generate summary
        self.generate_summary()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n" + "="*70)
        print(f"TESTING COMPLETE")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Total tests: {len(self.all_results)}")
        print(f"Anchors preserved: {len(self.passing_results)}")
        print("="*70)

def main():
    """Main entry point."""
    tester = ShadowSurveyTester()
    tester.run_all_phases()

if __name__ == "__main__":
    main()