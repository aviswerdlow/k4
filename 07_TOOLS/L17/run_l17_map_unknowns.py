#!/usr/bin/env python3
"""
Map the 50 undetermined positions under L=17 with anchors + canonical tail.
Pure algebra, deterministic, stdlib only.
"""

import json
import csv
import hashlib
from collections import defaultdict

MASTER_SEED = 1337

def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)

def load_ciphertext(path):
    """Load the 97-character ciphertext"""
    with open(path, 'r') as f:
        return f.read().strip()

def load_proof_digest(path):
    """Load the proof digest to get L=17 wheels"""
    with open(path, 'r') as f:
        data = json.load(f)
    # Extract wheels from proof
    wheels = {}
    for c in range(6):
        wheels[c] = {
            'family': data['solution']['families'][c],
            'L': 17,
            'phase': 0,
            'residues': data['solution']['wheels'][c]['residues']
        }
    return wheels

def load_anchors(path):
    """Load anchor positions"""
    with open(path, 'r') as f:
        anchors_data = json.load(f)
    
    anchors = {}
    for anchor in anchors_data['anchors']:
        anchors[anchor['name']] = (anchor['start'], anchor['end'])
    return anchors

def get_anchor_positions():
    """Get all anchor position indices"""
    positions = set()
    anchors = {
        'EAST': (21, 24),
        'NORTHEAST': (25, 33),
        'BERLIN': (63, 68),
        'CLOCK': (69, 73)
    }
    for name, (start, end) in anchors.items():
        for i in range(start, end + 1):
            positions.add(i)
    return positions

def get_tail_positions():
    """Get tail position indices (74-96)"""
    return set(range(74, 97))

def analyze_unknowns_from_anchors_tail():
    """
    Analyze which positions are unknown with only anchors + tail.
    """
    # Get constraint positions
    anchor_positions = get_anchor_positions()
    tail_positions = get_tail_positions()
    constrained = anchor_positions | tail_positions
    
    # With L=17 and 1-to-1 mapping, constrained positions = derived positions
    all_positions = set(range(97))
    unknown_positions = all_positions - constrained
    
    return unknown_positions, constrained

def map_unknown_metadata(unknown_positions):
    """
    Create detailed metadata for each unknown position.
    """
    anchor_positions = get_anchor_positions()
    tail_positions = get_tail_positions()
    
    unknown_map = []
    
    for idx in sorted(unknown_positions):
        # Compute class and slot
        c = compute_class_baseline(idx)
        s = idx % 17
        
        # Compute distances
        dist_to_anchor = min([abs(idx - a) for a in anchor_positions])
        dist_to_tail = min([abs(idx - t) for t in tail_positions]) if tail_positions else 97
        
        metadata = {
            'index': idx,
            'class': c,
            'slot': s,
            'mod6': idx % 6,
            'mod17': idx % 17,
            'in_head': idx < 74,
            'near_tail': 70 <= idx < 74,
            'dist_to_anchor': dist_to_anchor,
            'dist_to_tail': dist_to_tail
        }
        
        unknown_map.append(metadata)
    
    return unknown_map

def aggregate_by_class(unknown_map):
    """Aggregate unknowns by class"""
    by_class = defaultdict(int)
    for item in unknown_map:
        by_class[item['class']] += 1
    return dict(by_class)

def aggregate_by_slot(unknown_map):
    """Aggregate unknowns by slot per class"""
    by_slot = defaultdict(lambda: defaultdict(int))
    for item in unknown_map:
        by_slot[item['class']][item['slot']] += 1
    
    # Convert to regular dict
    result = {}
    for c in range(6):
        result[c] = dict(by_slot[c])
    return result

def create_text_grid(unknown_positions):
    """Create a simple text grid showing known/unknown positions"""
    lines = []
    for row in range(10):
        if row == 9:
            # Last row has 7 positions
            positions = range(row * 10, 97)
        else:
            positions = range(row * 10, (row + 1) * 10)
        
        row_chars = []
        for idx in positions:
            if idx in unknown_positions:
                row_chars.append('?')
            else:
                row_chars.append('.')
        
        lines.append(f"{row*10:2d}: " + ' '.join(row_chars))
    
    return '\n'.join(lines)

def main():
    """Run complete unknown position mapping"""
    print("\n=== L=17 Unknown Position Mapping ===")
    print(f"MASTER_SEED: {MASTER_SEED}")
    
    # Analyze unknowns
    unknown_positions, known_positions = analyze_unknowns_from_anchors_tail()
    
    print(f"\nResults:")
    print(f"  Known positions: {len(known_positions)}")
    print(f"  Unknown positions: {len(unknown_positions)}")
    
    # Create detailed map
    unknown_map = map_unknown_metadata(unknown_positions)
    
    # Aggregate statistics
    by_class = aggregate_by_class(unknown_map)
    by_slot = aggregate_by_slot(unknown_map)
    
    # Create outputs
    output_dir = '../../04_EXPERIMENTS/L17_MISSING'
    
    # Save JSON map
    with open(f'{output_dir}/UNKNOWN_MAP.json', 'w') as f:
        json.dump(unknown_map, f, indent=2)
    
    # Save CSV map
    with open(f'{output_dir}/UNKNOWN_MAP.csv', 'w', newline='') as f:
        if unknown_map:
            writer = csv.DictWriter(f, fieldnames=unknown_map[0].keys())
            writer.writeheader()
            writer.writerows(unknown_map)
    
    # Save by-class aggregation
    with open(f'{output_dir}/UNKNOWN_MAP_BY_CLASS.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Class', 'Unknown_Count'])
        for c in range(6):
            writer.writerow([c, by_class.get(c, 0)])
    
    # Save by-slot aggregation
    with open(f'{output_dir}/UNKNOWN_MAP_BY_SLOT.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Class', 'Slot', 'Count'])
        for c in range(6):
            for s in range(17):
                count = by_slot[c].get(s, 0)
                if count > 0:
                    writer.writerow([c, s, count])
    
    # Save summary
    summary = {
        'unknown_count': len(unknown_positions),
        'known_count': len(known_positions),
        'unknown_indices': sorted(list(unknown_positions)),
        'by_class': by_class,
        'in_head': sum(1 for x in unknown_map if x['in_head']),
        'in_tail': sum(1 for x in unknown_map if not x['in_head'])
    }
    
    with open(f'{output_dir}/UNKNOWN_MAP_SUMMARY.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save text grid
    grid = create_text_grid(unknown_positions)
    with open(f'{output_dir}/UNKNOWN_MAP.txt', 'w') as f:
        f.write("L=17 Unknown Position Grid\n")
        f.write("(. = known from anchors+tail, ? = unknown)\n")
        f.write("="*50 + "\n\n")
        f.write(grid)
        f.write(f"\n\nTotal: {len(known_positions)} known, {len(unknown_positions)} unknown\n")
    
    # Save README
    with open(f'{output_dir}/UNKNOWN_MAP_README.md', 'w') as f:
        f.write("# L=17 Unknown Position Map\n\n")
        f.write("## Summary\n")
        f.write(f"- Known positions (anchors+tail): {len(known_positions)}\n")
        f.write(f"- Unknown positions: {len(unknown_positions)}\n\n")
        f.write("## Files\n")
        f.write("- `UNKNOWN_MAP.json`: Detailed metadata for each unknown position\n")
        f.write("- `UNKNOWN_MAP.csv`: Same data in CSV format\n")
        f.write("- `UNKNOWN_MAP_BY_CLASS.csv`: Count of unknowns per class\n")
        f.write("- `UNKNOWN_MAP_BY_SLOT.csv`: Distribution by slot\n")
        f.write("- `UNKNOWN_MAP.txt`: Visual grid of known/unknown\n")
        f.write("- `UNKNOWN_MAP_SUMMARY.json`: Aggregate statistics\n\n")
        f.write("## Key Finding\n")
        f.write("With L=17's 1-to-1 mapping property, each constrained position ")
        f.write("determines exactly one position. Therefore, 47 constraints ")
        f.write("(24 anchors + 23 tail) yield exactly 47 known positions, ")
        f.write("leaving 50 unknown.\n")
    
    print(f"\n✅ Analysis complete. Outputs in {output_dir}/")
    
    # Display summary
    print("\nUnknowns by class:")
    for c in range(6):
        print(f"  Class {c}: {by_class.get(c, 0)} unknown")
    
    print(f"\nUnknowns by region:")
    print(f"  Head (0-73): {summary['in_head']} unknown")
    print(f"  Tail (74-96): {summary['in_tail']} unknown")

if __name__ == "__main__":
    main()