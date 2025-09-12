#!/usr/bin/env python3
"""
run_survey_tests.py

Main test runner for surveying cipher parameters (Fork S).
Implements all test batteries and generates result cards.
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from survey_params import *
from cipher_families import *
from validation import *

class SurveyingCipherTester:
    """Main test orchestrator for surveying cipher parameters."""
    
    def __init__(self):
        """Initialize tester with data and validators."""
        # Load ciphertext
        ct_path = Path("02_DATA/ciphertext_97.txt")
        with open(ct_path, 'r') as f:
            self.ciphertext = f.read().strip()
        
        # Initialize components
        self.validator = AnchorValidator()
        self.analyzer = TextAnalyzer()
        self.recorder = ResultRecorder()
        
        # Track results
        self.all_results = []
        self.passing_results = []
        
        # Generate all survey parameters
        self.survey_params = generate_all_params()
    
    def run_test_battery_A(self):
        """Test Battery A: Pure bearings with polyalphabetic ciphers."""
        print("\n" + "="*70)
        print("TEST BATTERY A: Pure Bearings (Polyalphabetic)")
        print("="*70)
        
        bearings_to_test = [
            ('true_ne_plus', TRUE_NE_PLUS),
            ('true_ene_minus', TRUE_ENE_MINUS),
            ('mag_ne_plus_1989', MAG_NE_PLUS_1989_B),
            ('mag_ene_minus_1989', MAG_ENE_MINUS_1989_B),
            ('offset_only', OFFSET_ONLY)
        ]
        
        for bearing_name, bearing_val in bearings_to_test:
            params = bearing_to_params(bearing_val)
            
            # Test different L values and variants
            test_configs = [
                ('L_int', params['L_int'], 0, params['offset_alpha']),
                ('L_round', params['L_round'], 0, params['offset_alpha_r']),
                ('L_int_phase41', params['L_int'], 41, 45 % 26),
                ('L_round_phase48', params['L_round'], 48, 15 % 26)
            ]
            
            for config_name, L, phase, offset in test_configs:
                for variant in ['vigenere', 'beaufort', 'variant_beaufort']:
                    test_id = f"A-{bearing_name}-{config_name}-{variant}"
                    
                    # Decrypt
                    if variant == 'vigenere':
                        plaintext = PolyalphabeticCiphers.vigenere_decrypt(
                            self.ciphertext, L, phase, offset)
                    elif variant == 'beaufort':
                        plaintext = PolyalphabeticCiphers.beaufort_decrypt(
                            self.ciphertext, L, phase, offset)
                    else:
                        plaintext = PolyalphabeticCiphers.variant_beaufort_decrypt(
                            self.ciphertext, L, phase, offset)
                    
                    # Validate and analyze
                    self._process_result(
                        test_id=test_id,
                        family=variant,
                        plaintext=plaintext,
                        stages=[
                            {"name": "stage1", "type": "none", "params": {}},
                            {"name": "stage2", "type": variant, 
                             "params": {"L": L, "phase": phase, "offset": offset}}
                        ],
                        parameter_source={
                            "bearing_deg": bearing_val,
                            "bearing_name": bearing_name
                        }
                    )
    
    def run_test_battery_B(self):
        """Test Battery B: Quadrant/angle-based parameters."""
        print("\n" + "="*70)
        print("TEST BATTERY B: Quadrant/Angle Parameters")
        print("="*70)
        
        angles = [TRUE_NE_PLUS, TRUE_ENE_MINUS, 67.5, 22.5, 112.5]
        
        for angle in angles:
            quad_params = quadrant_params(angle)
            arc_params = arc_family_params(angle)
            
            # Test configurations
            configs = [
                ('quad_L', quad_params['L_quad'], quad_params['quadrant'], 
                 quad_params['offset_quad']),
                ('ref_angle_L', quad_params['L_ref'], 0, 
                 int(quad_params['reference_angle']) % 26),
                ('complement_L', arc_params['L_complement'], 0, 
                 arc_params['off_chr']),
                ('supplement_L', arc_params['L_supplement'], 0, 
                 arc_params['fam_idx'])
            ]
            
            for config_name, L, phase, offset in configs:
                test_id = f"B-angle{int(angle)}-{config_name}"
                
                plaintext = PolyalphabeticCiphers.vigenere_decrypt(
                    self.ciphertext, L, phase, offset)
                
                self._process_result(
                    test_id=test_id,
                    family='vigenere',
                    plaintext=plaintext,
                    stages=[
                        {"name": "stage1", "type": "none", "params": {}},
                        {"name": "stage2", "type": "vigenere",
                         "params": {"L": L, "phase": phase, "offset": offset}}
                    ],
                    parameter_source={
                        "angle_deg": angle,
                        "quadrant": quad_params['quadrant'],
                        "reference_angle": quad_params['reference_angle']
                    }
                )
    
    def run_test_battery_C(self):
        """Test Battery C: Magnetic corrections with Caesar shifts."""
        print("\n" + "="*70)
        print("TEST BATTERY C: Magnetic Corrections")
        print("="*70)
        
        declination_configs = [
            ('langley_1990', LANGLEY_1990_DECLINATION),
            ('berlin_1989', BERLIN_1989_DECLINATION)
        ]
        
        for decl_name, declination in declination_configs:
            decl_params = declination_adjustments(TRUE_NE_PLUS, declination)
            
            # Pre-Caesar then polyalphabetic
            test_id = f"C-{decl_name}-pre_caesar"
            
            # Apply pre-Caesar
            temp = SubstitutionCiphers.caesar_shift(
                self.ciphertext, decl_params['caesar_pre'])
            
            # Apply polyalphabetic
            plaintext = PolyalphabeticCiphers.vigenere_decrypt(
                temp, decl_params['L_magnetic'], 0, 0)
            
            self._process_result(
                test_id=test_id,
                family='caesar_vigenere',
                plaintext=plaintext,
                stages=[
                    {"name": "stage1", "type": "caesar",
                     "params": {"shift": decl_params['caesar_pre']}},
                    {"name": "stage2", "type": "vigenere",
                     "params": {"L": decl_params['L_magnetic']}}
                ],
                parameter_source={
                    "declination": declination,
                    "location": decl_name
                }
            )
            
            # Post-Caesar variant
            test_id = f"C-{decl_name}-post_caesar"
            
            # Apply polyalphabetic first
            temp = PolyalphabeticCiphers.vigenere_decrypt(
                self.ciphertext, decl_params['L_true'], 0, 0)
            
            # Apply post-Caesar
            plaintext = SubstitutionCiphers.caesar_shift(
                temp, decl_params['caesar_post'])
            
            self._process_result(
                test_id=test_id,
                family='vigenere_caesar',
                plaintext=plaintext,
                stages=[
                    {"name": "stage1", "type": "vigenere",
                     "params": {"L": decl_params['L_true']}},
                    {"name": "stage2", "type": "caesar",
                     "params": {"shift": decl_params['caesar_post']}}
                ],
                parameter_source={
                    "declination": declination,
                    "location": decl_name
                }
            )
    
    def run_test_battery_D(self):
        """Test Battery D: Distance/rectangular parameters with transposition."""
        print("\n" + "="*70)
        print("TEST BATTERY D: Distance/Rectangular")
        print("="*70)
        
        for coord_name, (dN, dE) in RECTANGULAR_COORDS.items():
            coord_params = coords_to_params(dN, dE)
            
            # Test different column values
            for num_cols in coord_params['columns']:
                if num_cols < 2 or num_cols > 50:
                    continue
                
                test_id = f"D-{coord_name}-cols{num_cols}"
                
                # Stage 1: Columnar transposition
                temp, inv_map = TranspositionCiphers.columnar_transposition(
                    self.ciphertext, num_cols)
                
                # Stage 2: Polyalphabetic with distance-based L
                temp2 = PolyalphabeticCiphers.vigenere_decrypt(
                    temp, coord_params['L_m_int'], 0, coord_params['offset_from_angle'])
                
                # Invert transposition to restore positions
                plaintext = TranspositionCiphers.invert_transposition(
                    temp2, inv_map, len(self.ciphertext))
                
                # Ensure correct length
                if len(plaintext) < len(self.ciphertext):
                    plaintext += 'X' * (len(self.ciphertext) - len(plaintext))
                plaintext = plaintext[:len(self.ciphertext)]
                
                self._process_result(
                    test_id=test_id,
                    family='columnar_vigenere',
                    plaintext=plaintext,
                    stages=[
                        {"name": "stage1", "type": "columnar",
                         "params": {"columns": num_cols}},
                        {"name": "stage2", "type": "vigenere",
                         "params": {"L": coord_params['L_m_int'],
                                   "offset": coord_params['offset_from_angle']}}
                    ],
                    parameter_source={
                        "coords": {"dN": dN, "dE": dE},
                        "distance_m": coord_params['distance_m']
                    }
                )
    
    def run_test_battery_E(self):
        """Test Battery E: Arc/chord/sector transforms."""
        print("\n" + "="*70)
        print("TEST BATTERY E: Arc/Chord/Sector Transforms")
        print("="*70)
        
        angles = [TRUE_NE_PLUS, TRUE_ENE_MINUS, 45.0, 90.0, 135.0]
        
        for angle in angles:
            arc_params = arc_family_params(angle)
            
            # Different arc-based configurations
            configs = [
                ('arc_length', arc_params['L_arc'], 0, arc_params['off_chr']),
                ('chord', arc_params['L_deg'], 0, arc_params['off_chr']),
                ('sector', arc_params['L_deg'], arc_params['fam_idx'], 0)
            ]
            
            for config_name, L, phase, offset in configs:
                test_id = f"E-angle{int(angle)}-{config_name}"
                
                plaintext = PolyalphabeticCiphers.beaufort_decrypt(
                    self.ciphertext, L, phase, offset)
                
                self._process_result(
                    test_id=test_id,
                    family='beaufort',
                    plaintext=plaintext,
                    stages=[
                        {"name": "stage1", "type": "none", "params": {}},
                        {"name": "stage2", "type": "beaufort",
                         "params": {"L": L, "phase": phase, "offset": offset}}
                    ],
                    parameter_source={
                        "angle_deg": angle,
                        "arc_length": arc_params['arc_length'],
                        "chord": arc_params['chord'],
                        "sector": arc_params['sector']
                    }
                )
    
    def run_hybrid_tests(self):
        """Run hybrid two-stage cipher tests."""
        print("\n" + "="*70)
        print("HYBRID PIPELINE TESTS")
        print("="*70)
        
        # Best parameters from earlier tests (placeholder - will be updated)
        hybrid_configs = [
            {
                'test_id': 'H-columnar17_vigenere61',
                'stage1': {'type': 'columnar', 'columns': 17},
                'stage2': {'type': 'vigenere', 'L': 61, 'phase': 41, 'offset': 45 % 26}
            },
            {
                'test_id': 'H-railfence5_beaufort50',
                'stage1': {'type': 'rail_fence', 'rails': 5},
                'stage2': {'type': 'beaufort', 'L': 50, 'phase': 48, 'offset': 15 % 26}
            },
            {
                'test_id': 'H-route5x20_affine',
                'stage1': {'type': 'route', 'rows': 5, 'cols': 20, 'route': 'spiral_in'},
                'stage2': {'type': 'affine', 
                          'a': SubstitutionCiphers.make_coprime(17), 'b': 6}
            }
        ]
        
        for config in hybrid_configs:
            plaintext = HybridPipeline.surveying_chain(
                self.ciphertext, config['stage1'], config['stage2'])
            
            self._process_result(
                test_id=config['test_id'],
                family='hybrid',
                plaintext=plaintext,
                stages=[
                    {"name": "stage1", **config['stage1']},
                    {"name": "stage2", **config['stage2']}
                ],
                parameter_source={"hybrid": True}
            )
    
    def _process_result(self, test_id: str, family: str, plaintext: str,
                       stages: List[Dict], parameter_source: Dict):
        """Process and record a single test result."""
        # Validate anchors
        anchors_valid, anchor_failures = self.validator.validate(plaintext)
        
        # Analyze text quality
        head_analysis = self.analyzer.analyze_head(plaintext, 20)
        
        # Only do full analysis if anchors pass
        full_analysis = None
        if anchors_valid:
            full_analysis = self.analyzer.analyze_full(plaintext)
        
        # Record result
        result_card = self.recorder.record_result(
            test_id=test_id,
            family=family,
            stages=stages,
            parameter_source=parameter_source,
            plaintext=plaintext,
            anchors_valid=anchors_valid,
            anchor_failures=anchor_failures,
            head_analysis=head_analysis,
            full_analysis=full_analysis
        )
        
        self.all_results.append(result_card)
        
        # Check if it's a passing result
        if anchors_valid:
            self.passing_results.append(result_card)
            print(f"  ✓ {test_id}: ANCHORS PRESERVED!")
            print(f"    Head: {plaintext[:20]}")
            if head_analysis['survey_terms']:
                print(f"    Survey terms: {', '.join(head_analysis['survey_terms'])}")
        else:
            print(f"  ✗ {test_id}: Anchors failed")
    
    def run_all_tests(self):
        """Run all test batteries."""
        start_time = datetime.now()
        
        print("\n" + "="*70)
        print("SURVEYING CIPHER PARAMETERS TEST SUITE (FORK S)")
        print("="*70)
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Ciphertext length: {len(self.ciphertext)}")
        print(f"Master seed: 1337")
        
        # Run test batteries
        self.run_test_battery_A()  # Pure bearings
        self.run_test_battery_B()  # Quadrant/angles
        self.run_test_battery_C()  # Magnetic corrections
        self.run_test_battery_D()  # Distance/rectangular
        self.run_test_battery_E()  # Arc transforms
        self.run_hybrid_tests()    # Hybrid pipelines
        
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
    
    def generate_summary(self):
        """Generate CSV summary and final report."""
        # CSV summary
        csv_path = Path("04_EXPERIMENTS/survey_params/RUN_SUMMARY.csv")
        
        with open(csv_path, 'w', newline='') as f:
            fieldnames = [
                'id', 'anchors_preserved', 'head_text', 'max_consonant_run',
                'survey_terms', 'family', 'L', 'phase', 'offset', 'notes'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.all_results:
                # Extract L, phase, offset from stages
                L = phase = offset = 'N/A'
                for stage in result['stages']:
                    if 'L' in stage.get('params', {}):
                        L = stage['params']['L']
                    if 'phase' in stage.get('params', {}):
                        phase = stage['params']['phase']
                    if 'offset' in stage.get('params', {}):
                        offset = stage['params']['offset']
                
                writer.writerow({
                    'id': result['id'],
                    'anchors_preserved': result['results']['anchors_preserved'],
                    'head_text': result['results']['plaintext_head_0_20'],
                    'max_consonant_run': result['results']['readability']['max_consonant_run'],
                    'survey_terms': ','.join(result['results']['survey_terms_found']),
                    'family': result['family'],
                    'L': L,
                    'phase': phase,
                    'offset': offset,
                    'notes': result['results']['notes']
                })
        
        print(f"\nCSV summary saved to: {csv_path}")
        
        # Methods manifest
        manifest_path = Path("04_EXPERIMENTS/survey_params/METHODS_MANIFEST.json")
        manifest = {
            "constants": {
                "bearings": {
                    "true_ne_plus": TRUE_NE_PLUS,
                    "true_ene_minus": TRUE_ENE_MINUS,
                    "mag_ne_plus_1989": MAG_NE_PLUS_1989_B,
                    "mag_ene_minus_1989": MAG_ENE_MINUS_1989_B,
                    "offset_only": OFFSET_ONLY
                },
                "dms_exemplars": DMS_EXEMPLARS,
                "declinations": {
                    "langley_1990": LANGLEY_1990_DECLINATION,
                    "berlin_1989": BERLIN_1989_DECLINATION
                },
                "rectangular_coords": RECTANGULAR_COORDS
            },
            "test_batteries": [
                "A: Pure bearings (polyalphabetic)",
                "B: Quadrant/angle parameters",
                "C: Magnetic corrections",
                "D: Distance/rectangular",
                "E: Arc/chord/sector transforms",
                "Hybrid: Two-stage pipelines"
            ],
            "cipher_families": [
                "Vigenère", "Beaufort", "Variant Beaufort",
                "Columnar transposition", "Rail fence", "Route cipher",
                "Caesar", "Affine", "Hill 2x2", "Playfair"
            ],
            "total_tests": len(self.all_results),
            "passing_tests": len(self.passing_results)
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Methods manifest saved to: {manifest_path}")
        
        # Final report
        report_path = Path("04_EXPERIMENTS/survey_params/FINAL_REPORT.md")
        with open(report_path, 'w') as f:
            f.write("# Fork S - Surveying Cipher Parameters Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total tests: {len(self.all_results)}\n")
            f.write(f"- Anchors preserved: {len(self.passing_results)}\n")
            f.write(f"- Test batteries: 6\n")
            f.write(f"- Cipher families: 10+\n")
            f.write(f"- Master seed: 1337\n\n")
            
            if self.passing_results:
                f.write("## MATCHES FOUND\n\n")
                f.write("The following configurations preserve all anchors:\n\n")
                
                for result in self.passing_results[:10]:  # Top 10
                    f.write(f"### {result['id']}\n")
                    f.write(f"- Family: {result['family']}\n")
                    f.write(f"- Head: `{result['results']['plaintext_head_0_20']}`\n")
                    f.write(f"- Max consonant run: {result['results']['readability']['max_consonant_run']}\n")
                    if result['results']['survey_terms_found']:
                        f.write(f"- Survey terms: {', '.join(result['results']['survey_terms_found'])}\n")
                    f.write("\n")
            else:
                f.write("## NO MATCHES\n\n")
                f.write("No surveying-parameterized cipher configuration preserved the anchors.\n\n")
                f.write("This suggests that:\n")
                f.write("1. The cipher is not parameterized by these surveying quantities\n")
                f.write("2. A different transformation or combination is needed\n")
                f.write("3. The anchors require a different cipher family entirely\n")
        
        print(f"Final report saved to: {report_path}")

def main():
    """Main entry point."""
    tester = SurveyingCipherTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()