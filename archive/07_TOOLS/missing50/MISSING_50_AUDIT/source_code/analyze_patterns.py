#!/usr/bin/env python3
"""
C.4: Analyze structure in the 50 unknowns.
Look for patterns, clusters, or special properties.
"""

import json
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np

MASTER_SEED = 1337

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def get_unknown_positions():
    """Get the 50 unknown positions"""
    constrained = set()
    
    # Anchors
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        for i in range(start, end + 1):
            constrained.add(i)
    
    # Tail
    for i in range(74, 97):
        constrained.add(i)
    
    all_positions = set(range(97))
    unknown = sorted(all_positions - constrained)
    
    return unknown

def analyze_class_distribution(unknowns):
    """Analyze distribution by class"""
    class_counts = {}
    class_positions = {}
    
    for idx in unknowns:
        c = compute_class_baseline(idx)
        class_counts[c] = class_counts.get(c, 0) + 1
        if c not in class_positions:
            class_positions[c] = []
        class_positions[c].append(idx)
    
    return class_counts, class_positions

def analyze_slot_distribution(unknowns, L=17):
    """Analyze distribution by slot mod L"""
    slot_counts = {}
    slot_positions = {}
    
    for idx in unknowns:
        s = idx % L
        slot_counts[s] = slot_counts.get(s, 0) + 1
        if s not in slot_positions:
            slot_positions[s] = []
        slot_positions[s].append(idx)
    
    return slot_counts, slot_positions

def analyze_gaps(unknowns):
    """Analyze gaps between unknown positions"""
    gaps = []
    for i in range(1, len(unknowns)):
        gap = unknowns[i] - unknowns[i-1]
        gaps.append(gap)
    
    return gaps

def analyze_clusters(unknowns, threshold=3):
    """Find clusters of unknowns"""
    clusters = []
    current_cluster = [unknowns[0]]
    
    for i in range(1, len(unknowns)):
        if unknowns[i] - unknowns[i-1] <= threshold:
            current_cluster.append(unknowns[i])
        else:
            if len(current_cluster) > 1:
                clusters.append(current_cluster)
            current_cluster = [unknowns[i]]
    
    if len(current_cluster) > 1:
        clusters.append(current_cluster)
    
    return clusters

def create_pattern_visualization(unknowns):
    """Create visual analysis of patterns"""
    fig = plt.figure(figsize=(14, 10))
    
    # 1. Position grid with class coloring
    ax1 = plt.subplot(2, 3, 1)
    ax1.set_title('Unknown Positions by Class', fontweight='bold')
    
    class_colors = {
        0: '#FF6B6B', 1: '#4ECDC4', 2: '#45B7D1',
        3: '#96CEB4', 4: '#FFEAA7', 5: '#DDA0DD'
    }
    
    for row in range(10):
        for col in range(10):
            idx = row * 10 + col
            if idx >= 97:
                continue
            
            x = col
            y = 9 - row
            
            if idx in unknowns:
                c = compute_class_baseline(idx)
                color = class_colors[c]
                edge = 'black'
                width = 1.5
            else:
                color = 'lightgray'
                edge = 'gray'
                width = 0.5
            
            rect = Rectangle((x-0.4, y-0.4), 0.8, 0.8,
                           facecolor=color, edgecolor=edge, linewidth=width)
            ax1.add_patch(rect)
            ax1.text(x, y, str(idx), ha='center', va='center', fontsize=7)
    
    ax1.set_xlim(-0.5, 9.5)
    ax1.set_ylim(-0.5, 9.5)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.axis('off')
    
    # 2. Class distribution bar chart
    ax2 = plt.subplot(2, 3, 2)
    ax2.set_title('Distribution by Class', fontweight='bold')
    
    class_counts, _ = analyze_class_distribution(unknowns)
    classes = sorted(class_counts.keys())
    counts = [class_counts[c] for c in classes]
    colors = [class_colors[c] for c in classes]
    
    ax2.bar(classes, counts, color=colors, edgecolor='black')
    ax2.set_xlabel('Class')
    ax2.set_ylabel('Count')
    ax2.set_xticks(classes)
    ax2.grid(True, alpha=0.3)
    
    # Add expected line
    expected = len(unknowns) / 6
    ax2.axhline(y=expected, color='red', linestyle='--', label=f'Expected: {expected:.1f}')
    ax2.legend()
    
    # 3. Slot distribution
    ax3 = plt.subplot(2, 3, 3)
    ax3.set_title('Distribution by Slot (mod 17)', fontweight='bold')
    
    slot_counts, _ = analyze_slot_distribution(unknowns)
    slots = list(range(17))
    counts = [slot_counts.get(s, 0) for s in slots]
    
    ax3.bar(slots, counts, color='steelblue', edgecolor='black')
    ax3.set_xlabel('Slot')
    ax3.set_ylabel('Count')
    ax3.set_xticks(range(0, 17, 2))
    ax3.grid(True, alpha=0.3)
    
    # 4. Gap distribution
    ax4 = plt.subplot(2, 3, 4)
    ax4.set_title('Gap Distribution', fontweight='bold')
    
    gaps = analyze_gaps(unknowns)
    if gaps:
        ax4.hist(gaps, bins=range(1, max(gaps)+2), color='coral', edgecolor='black')
        ax4.set_xlabel('Gap Size')
        ax4.set_ylabel('Frequency')
        ax4.grid(True, alpha=0.3)
        
        # Add statistics
        mean_gap = np.mean(gaps)
        median_gap = np.median(gaps)
        ax4.axvline(x=mean_gap, color='red', linestyle='--', label=f'Mean: {mean_gap:.1f}')
        ax4.axvline(x=median_gap, color='blue', linestyle='--', label=f'Median: {median_gap:.0f}')
        ax4.legend()
    
    # 5. Cluster analysis
    ax5 = plt.subplot(2, 3, 5)
    ax5.set_title('Cluster Analysis', fontweight='bold')
    
    clusters = analyze_clusters(unknowns)
    if clusters:
        cluster_sizes = [len(c) for c in clusters]
        ax5.bar(range(len(cluster_sizes)), cluster_sizes, color='purple', edgecolor='black')
        ax5.set_xlabel('Cluster ID')
        ax5.set_ylabel('Size')
        ax5.set_xticks(range(len(cluster_sizes)))
        ax5.grid(True, alpha=0.3)
        
        # Annotate with positions
        for i, cluster in enumerate(clusters):
            label = f"{cluster[0]}-{cluster[-1]}"
            ax5.text(i, cluster_sizes[i] + 0.1, label, ha='center', fontsize=8)
    else:
        ax5.text(0.5, 0.5, 'No clusters found', ha='center', va='center', transform=ax5.transAxes)
    
    # 6. Mod analysis
    ax6 = plt.subplot(2, 3, 6)
    ax6.set_title('Modular Properties', fontweight='bold')
    
    # Analyze different moduli
    mod_results = {}
    for m in [2, 3, 5, 6, 17]:
        mod_counts = {}
        for idx in unknowns:
            r = idx % m
            mod_counts[r] = mod_counts.get(r, 0) + 1
        
        # Calculate uniformity (lower is more uniform)
        expected = len(unknowns) / m
        variance = sum((count - expected)**2 for count in mod_counts.values()) / m
        mod_results[m] = variance
    
    mods = sorted(mod_results.keys())
    variances = [mod_results[m] for m in mods]
    
    ax6.bar(range(len(mods)), variances, color='teal', edgecolor='black')
    ax6.set_xlabel('Modulus')
    ax6.set_ylabel('Variance from Uniform')
    ax6.set_xticks(range(len(mods)))
    ax6.set_xticklabels(mods)
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('C4_patterns/pattern_analysis.pdf', format='pdf', bbox_inches='tight')
    plt.close()
    
    print("Created pattern_analysis.pdf")

def main():
    """Analyze patterns in unknown positions"""
    print("\n=== C.4: Pattern Analysis of 50 Unknowns ===")
    print(f"MASTER_SEED: {MASTER_SEED}")
    
    unknowns = get_unknown_positions()
    
    # Create output directory
    import os
    os.makedirs('C4_patterns', exist_ok=True)
    
    # Basic statistics
    print(f"\nTotal unknowns: {len(unknowns)}")
    print(f"Range: {unknowns[0]}-{unknowns[-1]}")
    
    # Class distribution
    class_counts, class_positions = analyze_class_distribution(unknowns)
    print("\nClass distribution:")
    for c in sorted(class_counts.keys()):
        print(f"  Class {c}: {class_counts[c]} positions")
    
    # Slot distribution
    slot_counts, slot_positions = analyze_slot_distribution(unknowns)
    print(f"\nSlot distribution (mod 17):")
    print(f"  Slots used: {len(slot_counts)}/17")
    print(f"  Max per slot: {max(slot_counts.values())}")
    print(f"  Min per slot: {min(slot_counts.values()) if slot_counts else 0}")
    
    # Gap analysis
    gaps = analyze_gaps(unknowns)
    if gaps:
        print(f"\nGap analysis:")
        print(f"  Mean gap: {np.mean(gaps):.2f}")
        print(f"  Median gap: {np.median(gaps):.0f}")
        print(f"  Max gap: {max(gaps)}")
        print(f"  Min gap: {min(gaps)}")
    
    # Cluster analysis
    clusters = analyze_clusters(unknowns)
    print(f"\nCluster analysis:")
    if clusters:
        print(f"  Clusters found: {len(clusters)}")
        for i, cluster in enumerate(clusters):
            print(f"    Cluster {i+1}: positions {cluster[0]}-{cluster[-1]} (size {len(cluster)})")
    else:
        print("  No significant clusters")
    
    # Special patterns
    print("\nSpecial patterns:")
    
    # Check for arithmetic progressions
    for step in [2, 3, 5, 6, 17]:
        ap_count = 0
        for start in unknowns[:10]:
            seq = []
            pos = start
            while pos in unknowns and pos < 97:
                seq.append(pos)
                pos += step
            if len(seq) >= 3:
                ap_count += 1
        if ap_count > 0:
            print(f"  Arithmetic progressions (step {step}): {ap_count}")
    
    # Create visualization
    create_pattern_visualization(unknowns)
    
    # Save detailed analysis
    analysis = {
        'master_seed': MASTER_SEED,
        'total_unknowns': len(unknowns),
        'positions': unknowns,
        'class_distribution': class_counts,
        'slot_distribution': slot_counts,
        'gap_statistics': {
            'mean': float(np.mean(gaps)) if gaps else 0,
            'median': float(np.median(gaps)) if gaps else 0,
            'max': max(gaps) if gaps else 0,
            'min': min(gaps) if gaps else 0
        },
        'clusters': clusters,
        'observations': [
            f"Unknowns span positions {unknowns[0]}-{unknowns[-1]}",
            f"Class distribution fairly uniform (range {min(class_counts.values())}-{max(class_counts.values())})",
            f"Uses {len(slot_counts)}/17 available slots",
            f"Average gap between unknowns: {np.mean(gaps):.2f}" if gaps else "No gaps",
            f"{len(clusters)} clusters of consecutive unknowns" if clusters else "No clusters"
        ]
    }
    
    with open('C4_patterns/ANALYSIS.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Save CSV for reference
    rows = []
    for idx in unknowns:
        rows.append({
            'index': idx,
            'class': compute_class_baseline(idx),
            'slot_mod17': idx % 17,
            'mod2': idx % 2,
            'mod3': idx % 3,
            'mod6': idx % 6
        })
    
    with open('C4_patterns/unknown_properties.csv', 'w', newline='') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print("\n✅ Pattern analysis complete")

if __name__ == "__main__":
    main()