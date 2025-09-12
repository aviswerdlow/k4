#!/usr/bin/env python3
"""
C.0: Setup - Create unknown positions documentation for L=17.
"""

import json
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle

MASTER_SEED = 1337

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def get_unknown_positions():
    """Get the 50 unknown positions under L=17 with anchors+tail"""
    # Anchors: 21-24, 25-33, 63-68, 69-73
    # Tail: 74-96
    constrained = set()
    
    # Add anchors
    for start, end in [(21, 24), (25, 33), (63, 68), (69, 73)]:
        for i in range(start, end + 1):
            constrained.add(i)
    
    # Add tail
    for i in range(74, 97):
        constrained.add(i)
    
    # All positions
    all_positions = set(range(97))
    
    # Unknown = all - constrained
    unknown = sorted(all_positions - constrained)
    
    return unknown

def create_unknown_map_pdf(unknown_positions):
    """Create PDF showing unknown positions colored by class"""
    fig = plt.figure(figsize=(11, 8.5))
    
    # Title
    fig.text(0.5, 0.95, 'L=17 Unknown Positions Map (50 positions)', 
             fontsize=18, weight='bold', ha='center')
    
    # Create 10x10 grid
    ax = fig.add_subplot(111)
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-0.5, 9.5)
    ax.set_aspect('equal')
    
    # Class colors
    class_colors = {
        0: '#FF6B6B',  # Red
        1: '#4ECDC4',  # Teal
        2: '#45B7D1',  # Blue
        3: '#96CEB4',  # Green
        4: '#FFEAA7',  # Yellow
        5: '#DDA0DD'   # Plum
    }
    
    # Draw grid
    for row in range(10):
        for col in range(10):
            idx = row * 10 + col
            if idx >= 97:
                continue
            
            x = col
            y = 9 - row
            
            if idx in unknown_positions:
                # Unknown - color by class
                c = compute_class_baseline(idx)
                color = class_colors[c]
                edge = 'black'
                width = 1.5
            elif 21 <= idx <= 24:  # EAST
                color = 'lightgreen'
                edge = 'darkgreen'
                width = 1
            elif 25 <= idx <= 33:  # NORTHEAST
                color = 'lightgreen'
                edge = 'darkgreen'
                width = 1
            elif 63 <= idx <= 68:  # BERLIN
                color = 'lightgreen'
                edge = 'darkgreen'
                width = 1
            elif 69 <= idx <= 73:  # CLOCK
                color = 'lightgreen'
                edge = 'darkgreen'
                width = 1
            elif 74 <= idx <= 96:  # Tail
                color = 'lightblue'
                edge = 'blue'
                width = 1
            else:
                # Should not happen
                color = 'white'
                edge = 'gray'
                width = 0.5
            
            rect = Rectangle((x-0.4, y-0.4), 0.8, 0.8,
                           facecolor=color, edgecolor=edge, linewidth=width)
            ax.add_patch(rect)
            
            # Add index number
            ax.text(x, y, str(idx), ha='center', va='center', 
                   fontsize=9, weight='bold' if idx in unknown_positions else 'normal')
    
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-0.5, 9.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    # Legend
    patches = [
        mpatches.Patch(color='lightgreen', label='Anchors (24)'),
        mpatches.Patch(color='lightblue', label='Tail (23)'),
    ]
    for c in range(6):
        patches.append(mpatches.Patch(color=class_colors[c], label=f'Unknown Class {c}'))
    
    ax.legend(handles=patches, loc='center', bbox_to_anchor=(0.5, -0.1), 
             ncol=4, fontsize=9)
    
    # Summary
    summary = f"Total unknowns: 50 | By class: "
    class_counts = {}
    for idx in unknown_positions:
        c = compute_class_baseline(idx)
        class_counts[c] = class_counts.get(c, 0) + 1
    summary += ", ".join([f"C{c}:{n}" for c, n in sorted(class_counts.items())])
    
    fig.text(0.5, 0.02, summary, ha='center', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('../../06_DOCUMENTATION/L17_MISSING_50/unknown_map.pdf', 
               format='pdf', bbox_inches='tight')
    plt.close()
    
    print("Created unknown_map.pdf")

def create_class_slot_table(unknown_positions):
    """Create CSV table with class, slot, family for each unknown"""
    L = 17
    
    rows = []
    for idx in unknown_positions:
        c = compute_class_baseline(idx)
        s = idx % L
        
        # Family based on standard pattern
        if c in [1, 3, 5]:
            family = 'vigenere'
        else:
            family = 'beaufort'
        
        rows.append({
            'index': idx,
            'class': c,
            'slot': s,
            'family': family,
            'mod6': idx % 6,
            'mod17': idx % 17
        })
    
    # Save CSV
    with open('../../06_DOCUMENTATION/L17_MISSING_50/class_slot_table.csv', 'w', newline='') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print("Created class_slot_table.csv")
    
    return rows

def main():
    """Setup unknown positions documentation"""
    print("\n=== C.0: Setup Unknown Positions ===")
    print(f"MASTER_SEED: {MASTER_SEED}")
    
    # Get unknown positions
    unknown_positions = get_unknown_positions()
    
    print(f"\nFound {len(unknown_positions)} unknown positions")
    
    # Save JSON
    with open('../../06_DOCUMENTATION/L17_MISSING_50/unknown_positions.json', 'w') as f:
        json.dump({
            'master_seed': MASTER_SEED,
            'count': len(unknown_positions),
            'positions': unknown_positions
        }, f, indent=2)
    
    print("Created unknown_positions.json")
    
    # Create PDF map
    create_unknown_map_pdf(unknown_positions)
    
    # Create class/slot table
    table_data = create_class_slot_table(unknown_positions)
    
    # Print summary
    print("\nUnknowns by class:")
    class_counts = {}
    for row in table_data:
        c = row['class']
        class_counts[c] = class_counts.get(c, 0) + 1
    
    for c in range(6):
        print(f"  Class {c}: {class_counts.get(c, 0)}")
    
    print("\n✅ Setup complete")

if __name__ == "__main__":
    main()