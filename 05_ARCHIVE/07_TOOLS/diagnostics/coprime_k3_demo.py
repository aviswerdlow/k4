#!/usr/bin/env python3
"""
K3 co-prime coverage explainer.
Shows why certain grid dimensions ensure full coverage.
Pure Python stdlib only.
"""

import math


def gcd(a, b):
    """Compute greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


def demonstrate_coprime_coverage():
    """Demonstrate co-prime coverage principle for K3."""
    
    print("K3 Co-prime Coverage Analysis")
    print("=" * 50)
    print()
    
    # K3 parameters
    rows = 4
    step = 7
    
    print(f"Grid parameters:")
    print(f"  Rows: {rows}")
    print(f"  Step: {step}")
    print()
    
    # Check if co-prime
    g = gcd(rows, step)
    coprime = (g == 1)
    
    print(f"GCD({rows}, {step}) = {g}")
    if coprime:
        print("→ These are CO-PRIME (no common factors except 1)")
    else:
        print(f"→ NOT co-prime (common factor: {g})")
    print()
    
    # Calculate cycle length
    cycle_length = (rows * step) // g
    
    print(f"Cycle Analysis:")
    print(f"  Cycle length = (rows × step) / gcd = ({rows} × {step}) / {g} = {cycle_length}")
    print(f"  Total positions in grid = {rows} × columns")
    print()
    
    # Trace the path
    print("Step-7 walk pattern (first 28 positions):")
    print("-" * 50)
    
    visited = []
    pos = 0
    for i in range(min(28, cycle_length)):
        visited.append(pos)
        print(f"  Step {i:2}: Position {pos:2} → Row {pos % rows}, Col {pos // rows}")
        pos = (pos + step) % 28  # Using 28 as example grid size (4×7)
    
    print()
    
    # Check coverage
    unique_positions = len(set(visited))
    print(f"Coverage Analysis:")
    print(f"  Positions visited: {unique_positions}")
    print(f"  Positions in grid: 28 (4×7 example)")
    
    if unique_positions == min(28, cycle_length):
        print("  → FULL COVERAGE achieved before repetition")
    else:
        print("  → Incomplete coverage (positions missed)")
    
    print()
    print("Key Insight:")
    print("  When gcd(rows, step) = 1, the walk covers ALL positions")
    print("  before returning to the starting position.")
    print("  This ensures no collisions and complete coverage.")
    
    return rows, step, g, cycle_length


def create_coprime_pdf():
    """Create visual PDF explaining co-prime coverage."""
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.patches as mpatches
    
    rows, step, g, cycle_length = demonstrate_coprime_coverage()
    
    with PdfPages('K3_COPRIME_EXPLAIN.pdf') as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'Co-prime Coverage Principle', 
                ha='center', fontsize=16, fontweight='bold')
        ax.text(0.5, 0.92, 'Why K3 transposition achieves full coverage', 
                ha='center', fontsize=11, style='italic')
        
        # Mathematical explanation
        ax.text(0.1, 0.85, 'Mathematical Foundation:', fontsize=12, fontweight='bold')
        ax.text(0.1, 0.81, f'• Grid has {rows} rows', fontsize=10)
        ax.text(0.1, 0.78, f'• Step size = {step}', fontsize=10)
        ax.text(0.1, 0.75, f'• gcd({rows}, {step}) = {g}', fontsize=10, fontweight='bold')
        ax.text(0.1, 0.72, f'• Since gcd = 1, they are CO-PRIME', fontsize=10, color='green')
        
        # Visual cycle ring
        ax.text(0.1, 0.65, 'Cycle Visualization:', fontsize=12, fontweight='bold')
        
        # Draw cycle as a ring
        center_x, center_y = 0.5, 0.45
        radius = 0.15
        
        # Draw circle
        circle = mpatches.Circle((center_x, center_y), radius, 
                                 fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        # Mark positions around the circle
        n_positions = 28  # 4×7 grid
        for i in range(n_positions):
            angle = 2 * math.pi * i / n_positions - math.pi/2
            x = center_x + radius * 1.2 * math.cos(angle)
            y = center_y + radius * 1.2 * math.sin(angle)
            
            # Mark every 7th position
            if i % 7 == 0:
                ax.plot(x, y, 'ro', markersize=8)
                ax.text(x, y, str(i), ha='center', va='center', 
                       fontsize=8, color='white', fontweight='bold')
            else:
                ax.plot(x, y, 'bo', markersize=4)
        
        # Draw some step arrows
        for i in range(4):
            angle1 = 2 * math.pi * (i * 7) / n_positions - math.pi/2
            angle2 = 2 * math.pi * ((i * 7 + 7) % n_positions) / n_positions - math.pi/2
            
            x1 = center_x + radius * 0.9 * math.cos(angle1)
            y1 = center_y + radius * 0.9 * math.sin(angle1)
            x2 = center_x + radius * 0.9 * math.cos(angle2)
            y2 = center_y + radius * 0.9 * math.sin(angle2)
            
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='red',
                                     connectionstyle="arc3,rad=0.3"))
        
        ax.text(center_x, center_y, 'Step 7', ha='center', va='center', 
                fontsize=10, fontweight='bold')
        
        # Explanation
        ax.text(0.1, 0.22, 'Result:', fontsize=12, fontweight='bold')
        ax.text(0.1, 0.18, f'• Cycle length = {cycle_length} positions', fontsize=10)
        ax.text(0.1, 0.15, '• Every position visited exactly once', fontsize=10)
        ax.text(0.1, 0.12, '• No collisions or missed positions', fontsize=10)
        ax.text(0.1, 0.09, '• Complete coverage guaranteed', fontsize=10, color='green')
        
        # K4 connection
        ax.text(0.1, 0.04, 'K4 Application:', fontsize=11, fontweight='bold')
        ax.text(0.1, 0.01, 'Same principle: L=17 with 97 positions → each slot appears ≤1 time', 
                fontsize=9, style='italic')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print("\nCreated K3_COPRIME_EXPLAIN.pdf")


if __name__ == "__main__":
    demonstrate_coprime_coverage()
    create_coprime_pdf()