#!/usr/bin/env python3
"""
K4 co-prime coverage diagnostics.
Analyzes slot usage for different classing/period configurations.
Pure Python stdlib only.
"""

import csv
import json
import argparse


def compute_class_baseline(i):
    """Baseline class function: ((i%2)*3)+(i%3)"""
    return ((i % 2) * 3) + (i % 3)


def compute_class_mod6(i):
    """Simple mod-6 classing."""
    return i % 6


def compute_class_stepN(i, N):
    """Step-N bucket classing."""
    return i % N


def analyze_slot_usage(class_func, periods):
    """Analyze slot usage for given classing and periods."""
    
    # Assign indices to classes
    class_indices = {c: [] for c in range(6)}
    for i in range(97):
        cls = class_func(i)
        if cls < 6:  # Ensure valid class
            class_indices[cls].append(i)
    
    # Analyze slot usage per class
    slot_usage = {}
    for cls in range(6):
        L = periods[cls]
        slot_usage[cls] = {s: [] for s in range(L)}
        
        for idx in class_indices[cls]:
            slot = idx % L
            slot_usage[cls][slot].append(idx)
    
    return class_indices, slot_usage


def generate_reports(class_indices, slot_usage, periods, anchors=None):
    """Generate analysis reports."""
    
    # SLOT_USAGE_TABLE.csv
    with open('SLOT_USAGE_TABLE.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Class', 'Slot', 'Indices', 'Count'])
        
        for cls in range(6):
            for slot in range(periods[cls]):
                indices = slot_usage[cls][slot]
                writer.writerow([cls, slot, ' '.join(map(str, indices)), len(indices)])
    
    print("Created SLOT_USAGE_TABLE.csv")
    
    # Analysis summary
    print("\nSlot Usage Analysis:")
    print("=" * 60)
    
    for cls in range(6):
        L = periods[cls]
        indices_count = len(class_indices[cls])
        slots_used = sum(1 for s in range(L) if slot_usage[cls][s])
        max_reuse = max(len(slot_usage[cls][s]) for s in range(L))
        avg_per_slot = indices_count / L if L > 0 else 0
        
        print(f"\nClass {cls} (L={L}):")
        print(f"  Indices in class: {indices_count}")
        print(f"  Slots used: {slots_used}/{L}")
        print(f"  Max indices per slot: {max_reuse}")
        print(f"  Average indices/slot: {avg_per_slot:.2f}")
        
        if max_reuse > 1:
            print(f"  ⚠️  Some slots appear multiple times (not co-prime)")
        else:
            print(f"  ✓ Each slot appears at most once (co-prime property)")
    
    # Anchor analysis if provided
    if anchors:
        print("\n" + "=" * 60)
        print("Anchor-based Derivation Analysis:")
        print("=" * 60)
        
        total_forced = 0
        for cls in range(6):
            forced_slots = set()
            for anchor_idx in anchors:
                if anchor_idx in class_indices[cls]:
                    slot = anchor_idx % periods[cls]
                    forced_slots.add(slot)
            
            # Count derived positions
            derived = 0
            for slot in forced_slots:
                derived += len(slot_usage[cls][slot])
            
            total_forced += len(forced_slots)
            print(f"Class {cls}: {len(forced_slots)} slots forced → {derived} positions derived")
        
        print(f"\nTotal: {total_forced} unique slots forced")
        
        # Calculate total derived
        total_derived = 0
        for cls in range(6):
            forced_slots = set()
            for anchor_idx in anchors:
                if anchor_idx in class_indices[cls]:
                    slot = anchor_idx % periods[cls]
                    forced_slots.add(slot)
            
            for slot in forced_slots:
                total_derived += len(slot_usage[cls][slot])
        
        print(f"Total positions derived: {total_derived}/97")
        print(f"Positions unknown: {97 - total_derived}/97")
        
        # Save to CSV
        with open('DERIVABLE_FROM_ANCHORS.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Anchor_Positions', len(anchors)])
            writer.writerow(['Forced_Slots', total_forced])
            writer.writerow(['Derived_Positions', total_derived])
            writer.writerow(['Unknown_Positions', 97 - total_derived])
        
        print("\nCreated DERIVABLE_FROM_ANCHORS.csv")
    
    return slot_usage


def create_slot_chart_pdf(slot_usage, periods):
    """Create visual slot usage chart."""
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    with PdfPages('SLOT_USAGE_CHART.pdf') as pdf:
        fig, axes = plt.subplots(2, 3, figsize=(12, 8))
        fig.suptitle('K4 Slot Usage Analysis (L=17 for all classes)', fontsize=14, fontweight='bold')
        
        for cls in range(6):
            ax = axes[cls // 3, cls % 3]
            L = periods[cls]
            
            # Count indices per slot
            slot_counts = [len(slot_usage[cls][s]) for s in range(L)]
            
            # Color based on reuse
            colors = ['green' if c <= 1 else 'red' for c in slot_counts]
            
            # Create bar chart
            ax.bar(range(L), slot_counts, color=colors, alpha=0.7)
            ax.set_xlabel('Slot')
            ax.set_ylabel('Indices Count')
            ax.set_title(f'Class {cls} (L={L})')
            ax.set_ylim(0, max(slot_counts) + 0.5 if slot_counts else 1)
            
            # Add horizontal line at 1
            ax.axhline(y=1, color='blue', linestyle='--', alpha=0.5)
            
            # Add text annotation
            max_count = max(slot_counts) if slot_counts else 0
            if max_count <= 1:
                ax.text(L/2, max_count + 0.2, '✓ Co-prime', 
                       ha='center', color='green', fontweight='bold')
            else:
                ax.text(L/2, max_count + 0.2, '⚠️ Reuse', 
                       ha='center', color='red', fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print("Created SLOT_USAGE_CHART.pdf")


def main():
    parser = argparse.ArgumentParser(description='K4 co-prime coverage analyzer')
    parser.add_argument('--class-func', choices=['baseline', 'mod6', 'step6'], 
                       default='baseline', help='Classing function')
    parser.add_argument('--periods', default='17,17,17,17,17,17', 
                       help='Comma-separated periods per class')
    parser.add_argument('--anchors', default='21,22,23,24,25,26,27,28,29,30,31,32,33,63,64,65,66,67,68,69,70,71,72,73',
                       help='Comma-separated anchor indices')
    
    args = parser.parse_args()
    
    # Parse periods
    periods = list(map(int, args.periods.split(',')))
    if len(periods) == 1:
        periods = periods * 6  # Apply same period to all classes
    elif len(periods) != 6:
        print("Error: Must provide either 1 period (for all) or 6 periods")
        return
    
    # Parse anchors
    anchors = list(map(int, args.anchors.split(','))) if args.anchors else []
    
    # Select class function
    if args.class_func == 'baseline':
        class_func = compute_class_baseline
    elif args.class_func == 'mod6':
        class_func = compute_class_mod6
    elif args.class_func == 'step6':
        class_func = lambda i: compute_class_stepN(i, 6)
    
    print(f"Analyzing with {args.class_func} classing")
    print(f"Periods: {periods}")
    print(f"Anchors: {len(anchors)} positions")
    
    # Analyze
    class_indices, slot_usage = analyze_slot_usage(class_func, periods)
    
    # Generate reports
    generate_reports(class_indices, slot_usage, periods, anchors)
    
    # Create chart
    create_slot_chart_pdf(slot_usage, periods)


if __name__ == "__main__":
    main()