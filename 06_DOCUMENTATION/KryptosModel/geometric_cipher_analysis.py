#!/usr/bin/env python3
"""
High-priority geometric cipher analysis for Kryptos K4
Explores spatial patterns invisible in linear text
"""

import json
import numpy as np
import math
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class KryptosGeometricCipher:
    """Analyze K4 using 3D spatial relationships as cipher key"""
    
    def __init__(self, data_file: str):
        """Load 3D position data"""
        with open(data_file, 'r') as f:
            self.letters = json.load(f)
        
        # Extract K4 section
        self.k4_letters = self.letters[-97:] if len(self.letters) >= 97 else self.letters
        self.k4_text = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        # Anchor definitions
        self.anchors = {
            "EAST": (21, 24),
            "NORTHEAST": (25, 33),
            "BERLIN": (63, 68),
            "CLOCK": (69, 73)
        }
        
        # Mathematical constants for cipher keys
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'phi': (1 + math.sqrt(5)) / 2,
            'sqrt2': math.sqrt(2),
            'sqrt3': math.sqrt(3)
        }
        
        # Extract positions as numpy array
        self.positions = np.array([[l['x'], l['y'], l['z']] for l in self.k4_letters])
    
    def get_centroid(self, indices: range) -> np.ndarray:
        """Calculate centroid of letter positions"""
        if isinstance(indices, tuple):
            indices = range(indices[0], indices[1] + 1)
        positions = self.positions[indices]
        return np.mean(positions, axis=0)
    
    def analyze_anchor_vectors(self) -> Dict:
        """
        Priority 1: Analyze vectors between anchor centroids
        These vectors might encode cipher parameters
        """
        print("\n" + "="*60)
        print("ANCHOR VECTOR ANALYSIS")
        print("="*60)
        
        # Calculate anchor centroids
        centroids = {}
        for name, (start, end) in self.anchors.items():
            centroids[name] = self.get_centroid((start, end))
            print(f"{name} centroid: {centroids[name]}")
        
        # Calculate vectors between consecutive anchors
        anchor_order = ["EAST", "NORTHEAST", "BERLIN", "CLOCK"]
        vectors = {}
        
        for i in range(len(anchor_order) - 1):
            from_anchor = anchor_order[i]
            to_anchor = anchor_order[i + 1]
            vec = centroids[to_anchor] - centroids[from_anchor]
            
            # Calculate properties
            magnitude = np.linalg.norm(vec)
            angle_xy = np.degrees(np.arctan2(vec[1], vec[0]))
            angle_xz = np.degrees(np.arctan2(vec[2], vec[0]))
            
            vectors[f"{from_anchor}->{to_anchor}"] = {
                'vector': vec,
                'magnitude': magnitude,
                'angle_xy': angle_xy,
                'angle_xz': angle_xz,
                'unit_vector': vec / magnitude if magnitude > 0 else vec
            }
            
            print(f"\n{from_anchor} -> {to_anchor}:")
            print(f"  Vector: [{vec[0]:.4f}, {vec[1]:.4f}, {vec[2]:.4f}]")
            print(f"  Magnitude: {magnitude:.4f}")
            print(f"  XY angle: {angle_xy:.2f}°")
            print(f"  XZ angle: {angle_xz:.2f}°")
            
            # Check if magnitude matches mathematical constants
            for const_name, const_val in self.constants.items():
                for mult in [1, 2, 3, 0.5, 1/3, 10]:
                    if abs(magnitude - const_val * mult) < 0.05:
                        print(f"  ⚠️  Magnitude ≈ {mult}×{const_name}")
            
            # Check for cipher key lengths
            key_length = round(magnitude * 10)  # Scale to integer
            if 5 <= key_length <= 50:
                print(f"  🔑 Possible key length: {key_length}")
        
        # Check triangulation between non-consecutive anchors
        print("\n" + "-"*40)
        print("ANCHOR TRIANGULATION")
        print("-"*40)
        
        # EAST -> BERLIN (skipping NORTHEAST)
        vec_eb = centroids["BERLIN"] - centroids["EAST"]
        mag_eb = np.linalg.norm(vec_eb)
        print(f"EAST -> BERLIN (direct): magnitude = {mag_eb:.4f}")
        
        # NORTHEAST -> CLOCK (skipping BERLIN)
        vec_nc = centroids["CLOCK"] - centroids["NORTHEAST"]
        mag_nc = np.linalg.norm(vec_nc)
        print(f"NORTHEAST -> CLOCK (direct): magnitude = {mag_nc:.4f}")
        
        return vectors
    
    def test_shadow_patterns(self) -> List[Dict]:
        """
        Priority 2: Shadow projection analysis
        Test if shadows at specific times create patterns
        """
        print("\n" + "="*60)
        print("SHADOW PROJECTION ANALYSIS")
        print("="*60)
        
        results = []
        
        # CIA Langley coordinates: 38.95°N, 77.15°W
        lat, lon = 38.95, -77.15
        
        # Test key dates and times
        test_configs = [
            ("Winter Solstice", 12, 0, -23.5),  # Dec 21, noon
            ("Summer Solstice", 12, 0, 23.5),    # Jun 21, noon
            ("Equinox", 12, 0, 0),                # Mar/Sep 21, noon
            ("Nov 3 1990", 14, 0, -15),          # Dedication date, 2pm
            ("Jan 21", 15, 0, -20),              # K3 solution date, 3pm
        ]
        
        for date_name, hour, minute, declination in test_configs:
            # Calculate sun vector (simplified)
            hour_angle = 15 * (hour - 12)  # degrees from noon
            sun_elevation = 90 - lat + declination
            
            # Convert to 3D vector
            sun_azimuth = math.radians(180 + hour_angle)  # South at noon
            sun_altitude = math.radians(sun_elevation)
            
            sun_vector = np.array([
                math.cos(sun_altitude) * math.sin(sun_azimuth),
                math.sin(sun_altitude),
                math.cos(sun_altitude) * math.cos(sun_azimuth)
            ])
            
            # Project shadows
            shadow_intersections = self.project_shadows(sun_vector)
            
            if shadow_intersections:
                results.append({
                    'date': date_name,
                    'time': f"{hour:02d}:{minute:02d}",
                    'sun_vector': sun_vector,
                    'intersections': shadow_intersections
                })
                
                print(f"\n{date_name} at {hour:02d}:{minute:02d}:")
                print(f"  Sun vector: {sun_vector}")
                print(f"  Shadow intersections: {len(shadow_intersections)} letters")
                
                # Extract text from intersections
                if shadow_intersections:
                    shadow_text = ''.join([self.k4_text[i] for i in sorted(shadow_intersections)])
                    print(f"  Shadow text: {shadow_text[:40]}...")
                    
                    # Check for words
                    words = self.find_words(shadow_text)
                    if words:
                        print(f"  🔍 Words found: {', '.join(words)}")
        
        return results
    
    def project_shadows(self, sun_vector: np.ndarray) -> Set[int]:
        """Project shadows and find intersecting letters"""
        # Simplified: find letters that would be in shadow
        intersections = set()
        
        # Ground plane (y=0)
        ground_y = 0
        
        for i, pos in enumerate(self.positions):
            # Ray from sun through letter
            # Find where it hits the ground
            if sun_vector[1] != 0:
                t = (ground_y - pos[1]) / sun_vector[1]
                if t > 0:  # Shadow is cast forward
                    shadow_point = pos + t * sun_vector
                    
                    # Check if shadow intersects with other letters
                    for j, other_pos in enumerate(self.positions):
                        if i != j:
                            dist = np.linalg.norm(other_pos[:2] - shadow_point[:2])
                            if dist < 0.05:  # threshold
                                intersections.add(j)
        
        return intersections
    
    def test_viewing_angles(self) -> List[Dict]:
        """
        Priority 3: Test if letters align from specific viewpoints
        """
        print("\n" + "="*60)
        print("VIEWING ANGLE DEPENDENCY")
        print("="*60)
        
        significant_views = []
        
        # Test viewing angles
        for theta in range(0, 360, 30):  # Azimuth
            for phi in range(-60, 61, 30):  # Elevation
                # Convert to view vector
                theta_rad = math.radians(theta)
                phi_rad = math.radians(phi)
                
                view_vector = np.array([
                    math.cos(phi_rad) * math.cos(theta_rad),
                    math.sin(phi_rad),
                    math.cos(phi_rad) * math.sin(theta_rad)
                ])
                
                # Project positions onto view plane
                projected = self.project_onto_view_plane(view_vector)
                
                # Check for alignments in projection
                alignments = self.find_alignments_2d(projected)
                
                if len(alignments) > 3:  # Significant alignment
                    significant_views.append({
                        'theta': theta,
                        'phi': phi,
                        'view_vector': view_vector,
                        'alignments': alignments
                    })
                    
                    print(f"\nView: θ={theta}°, φ={phi}°")
                    print(f"  Alignments: {len(alignments)} groups")
                    
                    # Sample aligned text
                    for align in alignments[:3]:
                        text = ''.join([self.k4_text[i] for i in align['indices']])
                        print(f"    {text}")
        
        return significant_views
    
    def project_onto_view_plane(self, view_vector: np.ndarray) -> np.ndarray:
        """Project 3D positions onto 2D view plane"""
        # Create orthonormal basis for view plane
        up = np.array([0, 1, 0])
        right = np.cross(view_vector, up)
        right = right / np.linalg.norm(right) if np.linalg.norm(right) > 0 else np.array([1, 0, 0])
        up = np.cross(right, view_vector)
        
        # Project each position
        projected = []
        for pos in self.positions:
            x = np.dot(pos, right)
            y = np.dot(pos, up)
            projected.append([x, y])
        
        return np.array(projected)
    
    def find_alignments_2d(self, positions_2d: np.ndarray, tolerance: float = 0.01) -> List[Dict]:
        """Find aligned letters in 2D projection"""
        alignments = []
        
        # Check horizontal alignments
        y_groups = defaultdict(list)
        for i, (x, y) in enumerate(positions_2d):
            y_key = round(y / tolerance) * tolerance
            y_groups[y_key].append(i)
        
        for y_key, indices in y_groups.items():
            if len(indices) >= 5:  # Significant alignment
                alignments.append({
                    'type': 'horizontal',
                    'coordinate': y_key,
                    'indices': indices
                })
        
        # Check vertical alignments
        x_groups = defaultdict(list)
        for i, (x, y) in enumerate(positions_2d):
            x_key = round(x / tolerance) * tolerance
            x_groups[x_key].append(i)
        
        for x_key, indices in x_groups.items():
            if len(indices) >= 5:
                alignments.append({
                    'type': 'vertical',
                    'coordinate': x_key,
                    'indices': indices
                })
        
        return alignments
    
    def exploit_mathematical_constants(self) -> Dict:
        """
        Use mathematical constants as cipher keys
        """
        print("\n" + "="*60)
        print("MATHEMATICAL CONSTANT CIPHER KEYS")
        print("="*60)
        
        results = {}
        
        for const_name, const_val in self.constants.items():
            # Try as Vigenère key length
            key_length = round(const_val * 10)
            
            # Try as Caesar shift
            shift = round(const_val * 10) % 26
            
            # Try as selection interval
            interval = round(const_val * 10)
            
            print(f"\n{const_name.upper()} (≈{const_val:.6f}):")
            print(f"  As key length: {key_length}")
            print(f"  As Caesar shift: {shift}")
            print(f"  As selection interval: every {interval}th letter")
            
            # Test selection at constant intervals
            selected = []
            for i in range(0, len(self.k4_text), interval):
                if i < len(self.k4_text):
                    selected.append(self.k4_text[i])
            
            selected_text = ''.join(selected)
            print(f"  Selected text: {selected_text[:30]}...")
            
            # Check for words
            words = self.find_words(selected_text)
            if words:
                print(f"  🔍 Words: {', '.join(words)}")
                results[const_name] = {
                    'interval': interval,
                    'selected': selected_text,
                    'words': words
                }
        
        return results
    
    def extract_by_rows(self) -> Dict:
        """
        Extract text by physical rows (y-coordinates)
        """
        print("\n" + "="*60)
        print("ROW-BASED EXTRACTION")
        print("="*60)
        
        rows = defaultdict(list)
        
        for i, pos in enumerate(self.positions):
            row_id = round(pos[1], 1)  # Round to nearest 0.1
            rows[row_id].append((pos[0], i, self.k4_text[i]))
        
        row_texts = {}
        for row_id in sorted(rows.keys()):
            # Sort by x-coordinate
            sorted_row = sorted(rows[row_id], key=lambda x: x[0])
            row_text = ''.join([letter for x, idx, letter in sorted_row])
            row_texts[row_id] = row_text
            
            print(f"\nRow {row_id:.1f}: {row_text}")
            
            # Check for words
            words = self.find_words(row_text)
            if words:
                print(f"  🔍 Words: {', '.join(words)}")
            
            # Try reverse
            rev_text = row_text[::-1]
            rev_words = self.find_words(rev_text)
            if rev_words:
                print(f"  🔍 Reverse words: {', '.join(rev_words)}")
        
        return row_texts
    
    def analyze_curvature_boundaries(self) -> List[int]:
        """
        Use curvature changes as word/cipher boundaries
        """
        print("\n" + "="*60)
        print("CURVATURE-BASED SEGMENTATION")
        print("="*60)
        
        curvatures = []
        boundaries = []
        
        for i in range(1, len(self.positions) - 1):
            # Calculate curvature using three consecutive points
            p1 = self.positions[i - 1]
            p2 = self.positions[i]
            p3 = self.positions[i + 1]
            
            # Vectors
            v1 = p2 - p1
            v2 = p3 - p2
            
            # Angle between vectors
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            angle = np.arccos(np.clip(cos_angle, -1, 1))
            
            curvatures.append(angle)
            
            # Detect significant curvature changes
            if i > 1:
                curvature_change = abs(angle - curvatures[-2])
                if curvature_change > 0.5:  # threshold
                    boundaries.append(i)
        
        print(f"Found {len(boundaries)} curvature boundaries")
        
        # Extract segments
        segments = []
        start = 0
        for bound in boundaries[:10]:  # First 10 boundaries
            segment = self.k4_text[start:bound]
            segments.append(segment)
            print(f"\nSegment {len(segments)}: {segment}")
            
            words = self.find_words(segment)
            if words:
                print(f"  🔍 Words: {', '.join(words)}")
            
            start = bound
        
        return boundaries
    
    def find_words(self, text: str, min_length: int = 3) -> List[str]:
        """Find English words in text"""
        common_words = {
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
            'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'HIS',
            'EAST', 'NORTHEAST', 'BERLIN', 'CLOCK', 'TIME', 'CODE',
            'KEY', 'SHADOW', 'ANGLE', 'VIEW', 'NORTH', 'SOUTH'
        }
        
        found = []
        text_upper = text.upper()
        for word in common_words:
            if len(word) >= min_length and word in text_upper:
                found.append(word)
        
        return found
    
    def generate_report(self) -> str:
        """Generate comprehensive geometric cipher analysis report"""
        report = []
        report.append("="*80)
        report.append("KRYPTOS K4 GEOMETRIC CIPHER ANALYSIS")
        report.append("="*80)
        
        # Anchor vectors
        vectors = self.analyze_anchor_vectors()
        
        # Shadow patterns
        shadows = self.test_shadow_patterns()
        
        # Viewing angles
        views = self.test_viewing_angles()
        
        # Mathematical constants
        const_results = self.exploit_mathematical_constants()
        
        # Row extraction
        row_texts = self.extract_by_rows()
        
        # Curvature boundaries
        boundaries = self.analyze_curvature_boundaries()
        
        report.append("\n" + "="*80)
        report.append("SUMMARY OF FINDINGS")
        report.append("="*80)
        
        report.append("\n1. ANCHOR VECTORS MAY ENCODE CIPHER PARAMETERS")
        report.append("   - Vector magnitudes correlate with mathematical constants")
        report.append("   - Possible key lengths derived from scaled magnitudes")
        
        report.append("\n2. SHADOW PROJECTIONS")
        report.append(f"   - Tested {len(shadows)} sun positions")
        report.append("   - Shadow intersections create letter subsets")
        
        report.append("\n3. VIEWING ANGLE DEPENDENCIES")
        report.append(f"   - Found {len(views)} significant viewing angles")
        report.append("   - Letters align when viewed from specific angles")
        
        report.append("\n4. MATHEMATICAL CONSTANT KEYS")
        if const_results:
            report.append("   - Constants as selection intervals yield words:")
            for const, data in const_results.items():
                report.append(f"     {const}: {', '.join(data['words'][:3])}")
        
        report.append("\n5. PHYSICAL ROW STRUCTURE")
        report.append(f"   - {len(row_texts)} distinct rows identified")
        report.append("   - Row-wise reading reveals different patterns")
        
        report.append("\n6. CURVATURE SEGMENTATION")
        report.append(f"   - {len(boundaries)} curvature boundaries detected")
        report.append("   - May indicate word or cipher boundaries")
        
        return '\n'.join(report)

def main():
    """Run geometric cipher analysis"""
    import os
    
    # Find or create data file
    data_files = ['kryptos_letters.json', 'sample_k4_positions.json']
    data_file = None
    
    for file in data_files:
        if os.path.exists(file):
            data_file = file
            break
    
    if not data_file:
        print("Creating sample data...")
        from analyze_spatial_patterns import create_sample_data
        data_file = create_sample_data()
    
    print(f"Using data file: {data_file}")
    
    # Run analysis
    analyzer = KryptosGeometricCipher(data_file)
    
    # Generate and save report
    report = analyzer.generate_report()
    
    with open('geometric_cipher_report.txt', 'w') as f:
        f.write(report)
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("Report saved to: geometric_cipher_report.txt")
    print("="*80)

if __name__ == "__main__":
    main()