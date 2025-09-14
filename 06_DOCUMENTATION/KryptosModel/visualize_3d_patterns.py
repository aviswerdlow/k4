#!/usr/bin/env python3
"""
Advanced 3D pattern visualization and analysis for Kryptos
Finds hidden geometric relationships and spatial encodings
"""

import json
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import distance_matrix
from scipy.stats import pearsonr

class KryptosGeometricAnalyzer:
    """Advanced geometric analysis of Kryptos sculpture"""
    
    def __init__(self, data_file: str):
        """Load letter position data"""
        with open(data_file, 'r') as f:
            self.letters = json.load(f)
        
        # Extract K4 section (last 97)
        self.k4_letters = self.letters[-97:] if len(self.letters) >= 97 else self.letters
        
        # K4 text for reference
        self.k4_text = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        
        # Anchor positions
        self.anchors = {
            "EAST": (21, 24),
            "NORTHEAST": (25, 33),
            "BERLIN": (63, 68),
            "CLOCK": (69, 73)
        }
    
    def extract_coordinates(self) -> np.ndarray:
        """Extract xyz coordinates as numpy array"""
        coords = []
        for letter in self.k4_letters:
            coords.append([letter['x'], letter['y'], letter['z']])
        return np.array(coords)
    
    def analyze_golden_ratio(self) -> Dict:
        """Check for golden ratio relationships"""
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618
        coords = self.extract_coordinates()
        
        # Calculate all pairwise distances
        dist_matrix = distance_matrix(coords, coords)
        
        golden_pairs = []
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                for k in range(j + 1, len(coords)):
                    d1 = dist_matrix[i, j]
                    d2 = dist_matrix[j, k]
                    
                    if d2 > 0:
                        ratio = d1 / d2
                        # Check if ratio is close to phi or 1/phi
                        if abs(ratio - phi) < 0.05 or abs(ratio - 1/phi) < 0.05:
                            golden_pairs.append({
                                'indices': (i, j, k),
                                'chars': f"{self.k4_text[i]}{self.k4_text[j]}{self.k4_text[k]}",
                                'ratio': ratio,
                                'distances': (d1, d2)
                            })
        
        return {
            'golden_ratio': phi,
            'found_pairs': len(golden_pairs),
            'examples': golden_pairs[:5]  # Top 5 examples
        }
    
    def find_spirals(self) -> Dict:
        """Detect spiral patterns (Archimedean, logarithmic)"""
        coords = self.extract_coordinates()
        
        # Convert to cylindrical coordinates
        r = np.sqrt(coords[:, 0]**2 + coords[:, 2]**2)
        theta = np.arctan2(coords[:, 2], coords[:, 0])
        z = coords[:, 1]
        
        # Check for Archimedean spiral (r = a + b*theta)
        # Linear regression of r vs theta
        from scipy.stats import linregress
        slope, intercept, r_value, p_value, std_err = linregress(theta, r)
        
        archimedean = {
            'detected': abs(r_value) > 0.8,  # Strong correlation
            'equation': f"r = {intercept:.3f} + {slope:.3f}*θ",
            'correlation': r_value,
            'p_value': p_value
        }
        
        # Check for logarithmic spiral (r = a * e^(b*theta))
        log_r = np.log(r + 0.001)  # Avoid log(0)
        log_slope, log_intercept, log_r_value, log_p_value, _ = linregress(theta, log_r)
        
        logarithmic = {
            'detected': abs(log_r_value) > 0.8,
            'equation': f"r = {np.exp(log_intercept):.3f} * e^({log_slope:.3f}*θ)",
            'correlation': log_r_value,
            'p_value': log_p_value
        }
        
        return {
            'archimedean_spiral': archimedean,
            'logarithmic_spiral': logarithmic,
            'helical': {
                'pitch': np.std(z) if len(set(z)) > 1 else 0,
                'uniform_z': np.std(z) < 0.01
            }
        }
    
    def analyze_anchor_geometry(self) -> Dict:
        """Analyze geometric relationships between anchors"""
        coords = self.extract_coordinates()
        anchor_data = {}
        
        for name, (start, end) in self.anchors.items():
            if end < len(coords):
                anchor_coords = coords[start:end+1]
                center = np.mean(anchor_coords, axis=0)
                anchor_data[name] = {
                    'center': center,
                    'coords': anchor_coords
                }
        
        # Calculate angles between anchor centers
        angles = {}
        names = list(anchor_data.keys())
        
        if len(names) >= 3:
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    for k in range(j + 1, len(names)):
                        p1 = anchor_data[names[i]]['center']
                        p2 = anchor_data[names[j]]['center']
                        p3 = anchor_data[names[k]]['center']
                        
                        # Angle at p2
                        v1 = p1 - p2
                        v2 = p3 - p2
                        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                        angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
                        
                        angles[f"{names[i]}-{names[j]}-{names[k]}"] = angle
        
        # Check if anchors form regular polygon
        if len(anchor_data) >= 3:
            centers = [data['center'] for data in anchor_data.values()]
            distances = []
            for i in range(len(centers)):
                for j in range(i + 1, len(centers)):
                    distances.append(np.linalg.norm(centers[i] - centers[j]))
            
            regular = np.std(distances) < 0.1  # Low variance = regular
        else:
            regular = False
        
        return {
            'anchor_centers': {name: data['center'].tolist() for name, data in anchor_data.items()},
            'angles': angles,
            'forms_regular_polygon': regular
        }
    
    def find_mathematical_constants(self) -> Dict:
        """Look for mathematical constants in spatial relationships"""
        coords = self.extract_coordinates()
        dist_matrix = distance_matrix(coords, coords)
        
        constants = {
            'pi': math.pi,
            'e': math.e,
            'sqrt2': math.sqrt(2),
            'sqrt3': math.sqrt(3),
            'phi': (1 + math.sqrt(5)) / 2
        }
        
        found_constants = {}
        
        for name, value in constants.items():
            matches = []
            for i in range(len(coords)):
                for j in range(i + 1, len(coords)):
                    d = dist_matrix[i, j]
                    # Check if distance is close to constant or its multiples
                    for mult in [1, 2, 3, 0.5, 1/3]:
                        if abs(d - value * mult) < 0.05:
                            matches.append({
                                'indices': (i, j),
                                'chars': f"{self.k4_text[i]}{self.k4_text[j]}",
                                'distance': d,
                                'multiple': mult
                            })
            
            if matches:
                found_constants[name] = matches[:3]  # Top 3
        
        return found_constants
    
    def analyze_projection_patterns(self) -> Dict:
        """Analyze patterns in 2D projections"""
        coords = self.extract_coordinates()
        
        projections = {
            'xy_plane': coords[:, [0, 1]],
            'xz_plane': coords[:, [0, 2]],
            'yz_plane': coords[:, [1, 2]]
        }
        
        patterns = {}
        
        for plane_name, proj in projections.items():
            # Check for grid alignment
            x_unique = len(np.unique(np.round(proj[:, 0], 2)))
            y_unique = len(np.unique(np.round(proj[:, 1], 2)))
            
            # Check for circular arrangement
            center = np.mean(proj, axis=0)
            radii = np.linalg.norm(proj - center, axis=1)
            circular = np.std(radii) < 0.1
            
            patterns[plane_name] = {
                'grid_like': x_unique < 20 and y_unique < 20,
                'circular': circular,
                'unique_x': x_unique,
                'unique_y': y_unique,
                'mean_radius': np.mean(radii) if circular else None
            }
        
        return patterns
    
    def visualize_3d(self, save_file: str = 'kryptos_3d_viz.png'):
        """Create 3D visualization with anchor highlighting"""
        coords = self.extract_coordinates()
        
        fig = plt.figure(figsize=(15, 10))
        
        # 3D plot
        ax1 = fig.add_subplot(2, 3, 1, projection='3d')
        
        # Plot all letters
        ax1.scatter(coords[:, 0], coords[:, 1], coords[:, 2], 
                   c='blue', alpha=0.6, s=30)
        
        # Highlight anchors
        colors = ['red', 'green', 'orange', 'purple']
        for (name, (start, end)), color in zip(self.anchors.items(), colors):
            if end < len(coords):
                anchor_coords = coords[start:end+1]
                ax1.scatter(anchor_coords[:, 0], anchor_coords[:, 1], anchor_coords[:, 2],
                          c=color, s=100, label=name)
        
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.set_title('3D Letter Positions')
        ax1.legend()
        
        # XY projection
        ax2 = fig.add_subplot(2, 3, 2)
        ax2.scatter(coords[:, 0], coords[:, 1], c='blue', alpha=0.6)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_title('XY Projection')
        ax2.grid(True, alpha=0.3)
        
        # XZ projection
        ax3 = fig.add_subplot(2, 3, 3)
        ax3.scatter(coords[:, 0], coords[:, 2], c='blue', alpha=0.6)
        ax3.set_xlabel('X')
        ax3.set_ylabel('Z')
        ax3.set_title('XZ Projection')
        ax3.grid(True, alpha=0.3)
        
        # Distance matrix heatmap
        ax4 = fig.add_subplot(2, 3, 4)
        dist_matrix = distance_matrix(coords, coords)
        im = ax4.imshow(dist_matrix, cmap='viridis')
        ax4.set_title('Distance Matrix')
        ax4.set_xlabel('Letter Index')
        ax4.set_ylabel('Letter Index')
        plt.colorbar(im, ax=ax4)
        
        # Curvature plot
        ax5 = fig.add_subplot(2, 3, 5)
        curvatures = []
        for i in range(1, len(coords) - 1):
            # Simple curvature estimate
            v1 = coords[i] - coords[i-1]
            v2 = coords[i+1] - coords[i]
            angle = np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))
            curvatures.append(angle)
        
        ax5.plot(curvatures)
        ax5.set_xlabel('Position')
        ax5.set_ylabel('Curvature (radians)')
        ax5.set_title('Letter Path Curvature')
        ax5.grid(True, alpha=0.3)
        
        # Radial distribution
        ax6 = fig.add_subplot(2, 3, 6)
        center = np.mean(coords, axis=0)
        radii = np.linalg.norm(coords - center, axis=1)
        ax6.hist(radii, bins=20, alpha=0.7)
        ax6.set_xlabel('Distance from Center')
        ax6.set_ylabel('Count')
        ax6.set_title('Radial Distribution')
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_file, dpi=150)
        print(f"Visualization saved to {save_file}")
        
        return fig
    
    def generate_advanced_report(self) -> str:
        """Generate comprehensive geometric analysis report"""
        report = []
        report.append("=" * 80)
        report.append("KRYPTOS ADVANCED GEOMETRIC ANALYSIS")
        report.append("=" * 80)
        
        # Golden ratio
        report.append("\n" + "-" * 40)
        report.append("GOLDEN RATIO ANALYSIS")
        report.append("-" * 40)
        golden = self.analyze_golden_ratio()
        report.append(f"Golden ratio (φ) = {golden['golden_ratio']:.6f}")
        report.append(f"Found {golden['found_pairs']} potential golden ratio relationships")
        if golden['examples']:
            report.append("\nExamples:")
            for ex in golden['examples']:
                report.append(f"  {ex['chars']}: ratio = {ex['ratio']:.3f}")
        
        # Spirals
        report.append("\n" + "-" * 40)
        report.append("SPIRAL PATTERN ANALYSIS")
        report.append("-" * 40)
        spirals = self.find_spirals()
        
        arch = spirals['archimedean_spiral']
        report.append(f"\nArchimedean Spiral: {'DETECTED' if arch['detected'] else 'Not detected'}")
        if arch['detected']:
            report.append(f"  Equation: {arch['equation']}")
            report.append(f"  Correlation: {arch['correlation']:.3f}")
        
        log = spirals['logarithmic_spiral']
        report.append(f"\nLogarithmic Spiral: {'DETECTED' if log['detected'] else 'Not detected'}")
        if log['detected']:
            report.append(f"  Equation: {log['equation']}")
            report.append(f"  Correlation: {log['correlation']:.3f}")
        
        # Anchor geometry
        report.append("\n" + "-" * 40)
        report.append("ANCHOR GEOMETRIC RELATIONSHIPS")
        report.append("-" * 40)
        anchor_geom = self.analyze_anchor_geometry()
        
        report.append(f"Forms regular polygon: {'YES' if anchor_geom['forms_regular_polygon'] else 'NO'}")
        
        if anchor_geom['angles']:
            report.append("\nAngles between anchor centers:")
            for angle_name, angle_value in anchor_geom['angles'].items():
                report.append(f"  {angle_name}: {angle_value:.1f}°")
        
        # Mathematical constants
        report.append("\n" + "-" * 40)
        report.append("MATHEMATICAL CONSTANTS IN DISTANCES")
        report.append("-" * 40)
        constants = self.find_mathematical_constants()
        
        if constants:
            for const_name, matches in constants.items():
                report.append(f"\n{const_name.upper()}:")
                for match in matches:
                    report.append(f"  {match['chars']}: d={match['distance']:.3f} ({match['multiple']}×{const_name})")
        else:
            report.append("No clear mathematical constants found")
        
        # Projections
        report.append("\n" + "-" * 40)
        report.append("2D PROJECTION PATTERNS")
        report.append("-" * 40)
        projections = self.analyze_projection_patterns()
        
        for plane, data in projections.items():
            report.append(f"\n{plane}:")
            report.append(f"  Grid-like: {'YES' if data['grid_like'] else 'NO'}")
            report.append(f"  Circular: {'YES' if data['circular'] else 'NO'}")
            if data['circular']:
                report.append(f"  Mean radius: {data['mean_radius']:.3f}")
        
        return '\n'.join(report)

def main():
    """Run advanced geometric analysis"""
    import os
    
    # Check for data file
    data_files = ['kryptos_letters.json', 'sample_k4_positions.json']
    data_file = None
    
    for file in data_files:
        if os.path.exists(file):
            data_file = file
            break
    
    if not data_file:
        print("Creating sample data...")
        # Create sample
        from analyze_spatial_patterns import create_sample_data
        data_file = create_sample_data()
    
    print(f"Using data file: {data_file}")
    
    # Analyze
    analyzer = KryptosGeometricAnalyzer(data_file)
    
    # Generate report
    report = analyzer.generate_advanced_report()
    print(report)
    
    # Save report
    with open('geometric_analysis_report.txt', 'w') as f:
        f.write(report)
    
    # Create visualization
    analyzer.visualize_3d()
    
    print("\nAnalysis complete!")
    print("Files created:")
    print("  - geometric_analysis_report.txt")
    print("  - kryptos_3d_viz.png")

if __name__ == "__main__":
    main()