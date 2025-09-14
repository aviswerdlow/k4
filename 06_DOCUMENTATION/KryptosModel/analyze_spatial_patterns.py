#!/usr/bin/env python3
"""
Analyze spatial patterns in Kryptos 3D model data
Looks for geometric relationships, alignments, and hidden patterns
"""

import json
import csv
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

class KryptosSpatialAnalyzer:
    """Analyze 3D spatial patterns in Kryptos sculpture letters"""
    
    def __init__(self, csv_file: str = None, json_file: str = None):
        """Load letter data from CSV or JSON export"""
        self.letters = []
        self.k4_letters = []
        
        if json_file:
            self.load_json(json_file)
        elif csv_file:
            self.load_csv(csv_file)
    
    def load_json(self, filepath: str):
        """Load from JSON export"""
        with open(filepath, 'r') as f:
            self.letters = json.load(f)
        print(f"Loaded {len(self.letters)} letters from JSON")
    
    def load_csv(self, filepath: str):
        """Load from CSV export"""
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                letter_data = {
                    'idx': int(row['idx']) if 'idx' in row else 0,
                    'char': row['char'],
                    'x': float(row['x']),
                    'y': float(row['y']),
                    'z': float(row['z'])
                }
                # Add optional fields if present
                for field in ['nx', 'ny', 'nz', 'sx', 'sy', 'sz']:
                    if field in row:
                        letter_data[field] = float(row[field])
                
                self.letters.append(letter_data)
        
        print(f"Loaded {len(self.letters)} letters from CSV")
        
        # Extract K4 (last 97 letters)
        if len(self.letters) >= 97:
            self.k4_letters = self.letters[-97:]
            print(f"K4 section identified: {len(self.k4_letters)} letters")
    
    def analyze_distances(self) -> Dict:
        """Analyze distance patterns between letters"""
        if not self.letters:
            return {}
        
        distances = []
        for i in range(len(self.letters) - 1):
            l1 = self.letters[i]
            l2 = self.letters[i + 1]
            dist = math.sqrt(
                (l2['x'] - l1['x'])**2 + 
                (l2['y'] - l1['y'])**2 + 
                (l2['z'] - l1['z'])**2
            )
            distances.append(dist)
        
        return {
            'mean_spacing': np.mean(distances),
            'std_spacing': np.std(distances),
            'min_spacing': np.min(distances),
            'max_spacing': np.max(distances),
            'uniform': np.std(distances) < 0.01  # Check if uniform spacing
        }
    
    def find_alignments(self, tolerance: float = 0.01) -> List[Dict]:
        """Find letters that align on x, y, or z axes"""
        alignments = {
            'x_lines': defaultdict(list),
            'y_lines': defaultdict(list),
            'z_lines': defaultdict(list)
        }
        
        # Group letters by similar coordinates
        for i, letter in enumerate(self.letters):
            # Round to tolerance
            x_key = round(letter['x'] / tolerance) * tolerance
            y_key = round(letter['y'] / tolerance) * tolerance
            z_key = round(letter['z'] / tolerance) * tolerance
            
            alignments['x_lines'][x_key].append(i)
            alignments['y_lines'][y_key].append(i)
            alignments['z_lines'][z_key].append(i)
        
        # Find significant alignments (3+ letters)
        significant = []
        for axis, lines in alignments.items():
            for coord, indices in lines.items():
                if len(indices) >= 3:
                    chars = ''.join([self.letters[i]['char'] for i in indices])
                    significant.append({
                        'axis': axis,
                        'coordinate': coord,
                        'count': len(indices),
                        'indices': indices,
                        'text': chars
                    })
        
        return significant
    
    def analyze_angles(self) -> List[Dict]:
        """Find interesting angles between consecutive letter triplets"""
        angles = []
        
        for i in range(len(self.letters) - 2):
            l1 = self.letters[i]
            l2 = self.letters[i + 1]
            l3 = self.letters[i + 2]
            
            # Vectors
            v1 = np.array([l2['x'] - l1['x'], l2['y'] - l1['y'], l2['z'] - l1['z']])
            v2 = np.array([l3['x'] - l2['x'], l3['y'] - l2['y'], l3['z'] - l2['z']])
            
            # Angle between vectors
            v1_norm = np.linalg.norm(v1)
            v2_norm = np.linalg.norm(v2)
            
            if v1_norm > 0 and v2_norm > 0:
                cos_angle = np.dot(v1, v2) / (v1_norm * v2_norm)
                cos_angle = np.clip(cos_angle, -1, 1)  # Handle numerical errors
                angle_rad = np.arccos(cos_angle)
                angle_deg = np.degrees(angle_rad)
                
                angles.append({
                    'index': i + 1,
                    'chars': f"{l1['char']}{l2['char']}{l3['char']}",
                    'angle_deg': angle_deg
                })
        
        # Find special angles (90°, 45°, 60°, etc.)
        special_angles = []
        for a in angles:
            for special in [0, 30, 45, 60, 90, 120, 135, 150, 180]:
                if abs(a['angle_deg'] - special) < 2:  # 2° tolerance
                    special_angles.append({
                        **a,
                        'special_angle': special
                    })
        
        return special_angles
    
    def find_geometric_shapes(self) -> Dict:
        """Look for geometric patterns (triangles, rectangles, etc.)"""
        patterns = {
            'equilateral_triangles': [],
            'right_triangles': [],
            'rectangles': [],
            'regular_patterns': []
        }
        
        # Check every set of 3 points for triangles
        for i in range(len(self.letters) - 2):
            for j in range(i + 1, len(self.letters) - 1):
                for k in range(j + 1, len(self.letters)):
                    p1 = self.letters[i]
                    p2 = self.letters[j]
                    p3 = self.letters[k]
                    
                    # Calculate distances
                    d12 = self.distance_3d(p1, p2)
                    d23 = self.distance_3d(p2, p3)
                    d31 = self.distance_3d(p3, p1)
                    
                    # Check for equilateral
                    if abs(d12 - d23) < 0.01 and abs(d23 - d31) < 0.01:
                        patterns['equilateral_triangles'].append({
                            'indices': [i, j, k],
                            'chars': f"{p1['char']}{p2['char']}{p3['char']}",
                            'side_length': d12
                        })
                    
                    # Check for right triangle (Pythagorean)
                    sides = sorted([d12, d23, d31])
                    if abs(sides[2]**2 - (sides[0]**2 + sides[1]**2)) < 0.01:
                        patterns['right_triangles'].append({
                            'indices': [i, j, k],
                            'chars': f"{p1['char']}{p2['char']}{p3['char']}"
                        })
        
        return patterns
    
    def analyze_anchor_positions(self) -> Dict:
        """Analyze the spatial positions of K4 anchors"""
        if not self.k4_letters:
            return {}
        
        # K4 anchor positions (0-based)
        anchors = {
            "EAST": (21, 24),
            "NORTHEAST": (25, 33),
            "BERLIN": (63, 68),
            "CLOCK": (69, 73)
        }
        
        anchor_analysis = {}
        
        for name, (start, end) in anchors.items():
            if end < len(self.k4_letters):
                anchor_letters = self.k4_letters[start:end+1]
                
                # Calculate center of mass
                center_x = np.mean([l['x'] for l in anchor_letters])
                center_y = np.mean([l['y'] for l in anchor_letters])
                center_z = np.mean([l['z'] for l in anchor_letters])
                
                # Calculate span
                x_span = max(l['x'] for l in anchor_letters) - min(l['x'] for l in anchor_letters)
                y_span = max(l['y'] for l in anchor_letters) - min(l['y'] for l in anchor_letters)
                z_span = max(l['z'] for l in anchor_letters) - min(l['z'] for l in anchor_letters)
                
                anchor_analysis[name] = {
                    'center': (center_x, center_y, center_z),
                    'span': (x_span, y_span, z_span),
                    'letters': ''.join([l['char'] for l in anchor_letters])
                }
        
        # Calculate distances between anchor centers
        if len(anchor_analysis) >= 2:
            anchor_distances = {}
            anchor_names = list(anchor_analysis.keys())
            for i in range(len(anchor_names)):
                for j in range(i + 1, len(anchor_names)):
                    name1, name2 = anchor_names[i], anchor_names[j]
                    c1 = anchor_analysis[name1]['center']
                    c2 = anchor_analysis[name2]['center']
                    dist = math.sqrt(sum((c2[k] - c1[k])**2 for k in range(3)))
                    anchor_distances[f"{name1}-{name2}"] = dist
            
            anchor_analysis['distances'] = anchor_distances
        
        return anchor_analysis
    
    def find_curves_and_arcs(self) -> Dict:
        """Detect if letters follow curves or arcs"""
        curves = {
            'curvature': [],
            'arc_segments': []
        }
        
        # Calculate curvature at each point
        for i in range(1, len(self.letters) - 1):
            p_prev = self.letters[i - 1]
            p_curr = self.letters[i]
            p_next = self.letters[i + 1]
            
            # Use Menger curvature formula
            curvature = self.menger_curvature(p_prev, p_curr, p_next)
            
            curves['curvature'].append({
                'index': i,
                'char': p_curr['char'],
                'curvature': curvature
            })
            
            # High curvature indicates curve/corner
            if curvature > 0.1:  # Threshold for significant curvature
                curves['arc_segments'].append({
                    'index': i,
                    'char': p_curr['char'],
                    'curvature': curvature
                })
        
        return curves
    
    def distance_3d(self, p1: Dict, p2: Dict) -> float:
        """Calculate 3D distance between two points"""
        return math.sqrt(
            (p2['x'] - p1['x'])**2 + 
            (p2['y'] - p1['y'])**2 + 
            (p2['z'] - p1['z'])**2
        )
    
    def menger_curvature(self, p1: Dict, p2: Dict, p3: Dict) -> float:
        """Calculate Menger curvature for three points"""
        # Get distances
        d12 = self.distance_3d(p1, p2)
        d23 = self.distance_3d(p2, p3)
        d31 = self.distance_3d(p3, p1)
        
        # Calculate area using Heron's formula
        s = (d12 + d23 + d31) / 2  # Semi-perimeter
        
        # Avoid division by zero
        if s * (s - d12) * (s - d23) * (s - d31) <= 0:
            return 0
        
        area = math.sqrt(s * (s - d12) * (s - d23) * (s - d31))
        
        # Menger curvature
        if d12 * d23 * d31 == 0:
            return 0
        
        return 4 * area / (d12 * d23 * d31)
    
    def generate_report(self) -> str:
        """Generate comprehensive spatial analysis report"""
        if not self.letters:
            return "No letter data loaded. Please provide CSV or JSON export from Blender."
        
        report = []
        report.append("=" * 80)
        report.append("KRYPTOS 3D SPATIAL ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nTotal letters analyzed: {len(self.letters)}")
        
        if self.k4_letters:
            report.append(f"K4 section: {len(self.k4_letters)} letters")
        
        # Distance analysis
        report.append("\n" + "-" * 40)
        report.append("LETTER SPACING ANALYSIS")
        report.append("-" * 40)
        distances = self.analyze_distances()
        for key, value in distances.items():
            if isinstance(value, bool):
                report.append(f"{key}: {'Yes' if value else 'No'}")
            else:
                report.append(f"{key}: {value:.4f}")
        
        # Alignments
        report.append("\n" + "-" * 40)
        report.append("SIGNIFICANT ALIGNMENTS")
        report.append("-" * 40)
        alignments = self.find_alignments()
        if alignments:
            for align in alignments[:10]:  # Top 10
                report.append(f"{align['axis']}: {align['count']} letters at {align['coordinate']:.3f}")
                report.append(f"  Text: {align['text']}")
        else:
            report.append("No significant alignments found")
        
        # Special angles
        report.append("\n" + "-" * 40)
        report.append("SPECIAL ANGLES")
        report.append("-" * 40)
        angles = self.analyze_angles()
        if angles:
            for angle in angles[:10]:  # Top 10
                report.append(f"Index {angle['index']}: {angle['chars']} = {angle['special_angle']}°")
        else:
            report.append("No special angles found")
        
        # Anchor analysis
        if self.k4_letters:
            report.append("\n" + "-" * 40)
            report.append("K4 ANCHOR SPATIAL ANALYSIS")
            report.append("-" * 40)
            anchors = self.analyze_anchor_positions()
            for name, data in anchors.items():
                if name != 'distances':
                    report.append(f"\n{name}:")
                    report.append(f"  Center: ({data['center'][0]:.3f}, {data['center'][1]:.3f}, {data['center'][2]:.3f})")
                    report.append(f"  Span: ({data['span'][0]:.3f}, {data['span'][1]:.3f}, {data['span'][2]:.3f})")
            
            if 'distances' in anchors:
                report.append("\nDistances between anchors:")
                for pair, dist in anchors['distances'].items():
                    report.append(f"  {pair}: {dist:.3f}")
        
        # Curves
        report.append("\n" + "-" * 40)
        report.append("CURVATURE ANALYSIS")
        report.append("-" * 40)
        curves = self.find_curves_and_arcs()
        if curves['arc_segments']:
            report.append(f"Found {len(curves['arc_segments'])} high-curvature points")
            for arc in curves['arc_segments'][:5]:  # Top 5
                report.append(f"  Index {arc['index']}: '{arc['char']}' (curvature: {arc['curvature']:.3f})")
        else:
            report.append("No significant curves detected")
        
        return '\n'.join(report)

def create_sample_data():
    """Create sample data for testing without Blender export"""
    print("\nCreating sample K4 data for demonstration...")
    
    # Generate sample 3D positions for K4 letters
    k4_text = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    
    sample_data = []
    for i, char in enumerate(k4_text):
        # Simulate curved panel arrangement
        angle = (i / len(k4_text)) * math.pi  # Half circle
        radius = 2.0
        height = (i // 14) * 0.1  # Row height
        
        sample_data.append({
            'idx': i,
            'char': char,
            'x': radius * math.cos(angle),
            'y': height,
            'z': radius * math.sin(angle),
            'obj_name': f'K4_{char}_{i:03d}'
        })
    
    # Save sample data
    with open('sample_k4_positions.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Created sample data with {len(sample_data)} letters")
    return 'sample_k4_positions.json'

def main():
    """Run spatial analysis"""
    import sys
    import os
    
    # Check for existing exports
    files_to_check = [
        'kryptos_letters.json',
        'kryptos_letters.csv',
        'k4_line.csv',
        'sample_k4_positions.json'
    ]
    
    found_file = None
    for file in files_to_check:
        if os.path.exists(file):
            found_file = file
            print(f"Found export file: {file}")
            break
    
    if not found_file:
        print("No Blender export found. Creating sample data...")
        found_file = create_sample_data()
    
    # Analyze
    analyzer = KryptosSpatialAnalyzer()
    
    if found_file.endswith('.json'):
        analyzer.load_json(found_file)
    else:
        analyzer.load_csv(found_file)
    
    # Generate report
    report = analyzer.generate_report()
    print(report)
    
    # Save report
    report_file = 'spatial_analysis_report.txt'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")

if __name__ == "__main__":
    main()