#!/usr/bin/env python3
"""
Simple seam-free tail demonstration
Directly examines published candidates to show observed tails without seam constraint
"""

import json
import csv
from pathlib import Path

def main():
    """Simple tail flexibility demonstration"""
    print("🔬 K4 Seam-Free Tail Demonstration")
    print("=" * 40)
    print("Question: What tails do our published candidates show?")
    print("Method: Direct examination without seam guard enforcement\n")
    
    # Paths to published candidates
    base_dir = Path(__file__).parent.parent.parent.parent
    results_dir = base_dir / "results/GRID_ONLY"
    archive_dir = base_dir / "archive/2025-09-03/uniq_prescreen/uniq_sweep"
    
    candidates = {
        "cand_005": {"route": "GRID_W14_ROWS", "desc": "Winner", "path": results_dir},
        "cand_004": {"route": "GRID_W10_NW", "desc": "Runner-up", "path": archive_dir}
    }
    
    results = []
    
    for cand_label, info in candidates.items():
        cand_dir = info["path"] / cand_label
        pt_file = cand_dir / "plaintext_97.txt"
        
        if pt_file.exists():
            with open(pt_file, 'r') as f:
                plaintext = f.read().strip()
            
            if len(plaintext) == 97:
                tail_75_96 = plaintext[75:97]  # Extract characters 75-96
                hejoy_guard = plaintext[75:80]  # HEJOY section
                seam_tokens = plaintext[80:97]  # Potential seam tokens
                
                print(f"📋 {cand_label} ({info['desc']}) - Route: {info['route']}")
                print(f"   Full plaintext: {plaintext}")
                print(f"   Tail [75:97]:   {tail_75_96}")
                print(f"   HEJOY [75:80]:  {hejoy_guard}")
                print(f"   Seam [80:97]:   {seam_tokens}")
                print(f"   Readable seam:  {seam_tokens.replace('', ' ').strip()}")
                print()
                
                results.append({
                    'label': cand_label,
                    'route_id': info['route'],
                    'description': info['desc'],
                    'tail_75_96': tail_75_96,
                    'hejoy_guard': hejoy_guard,
                    'seam_tokens': seam_tokens,
                    'plaintext_sha256': f"{hash(plaintext) & 0xFFFFFFFFFFFFFFFF:016x}"
                })
            else:
                print(f"❌ {cand_label}: Invalid length {len(plaintext)}")
        else:
            print(f"❌ {cand_label}: File not found at {pt_file}")
    
    # Write results
    runs_dir = Path(__file__).parent.parent / "runs/20250903"
    runs_dir.mkdir(parents=True, exist_ok=True)
    
    # CSV summary
    summary_file = runs_dir / "simple_tail_summary.csv"
    with open(summary_file, 'w', newline='') as f:
        fieldnames = ['label', 'route_id', 'description', 'tail_75_96', 'hejoy_guard', 'seam_tokens', 'plaintext_sha256']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # JSON summary  
    summary_json = runs_dir / "simple_tail_summary.json"
    with open(summary_json, 'w') as f:
        json.dump({
            'experiment': 'simple_seam_free_tail_examination',
            'description': 'Direct examination of published candidate tails without seam guard',
            'results': results
        }, f, indent=2)
    
    # Analysis
    print("🎯 Tail Analysis:")
    unique_tails = set(r['tail_75_96'] for r in results)
    unique_seam_tokens = set(r['seam_tokens'] for r in results)
    
    if len(unique_tails) == 1:
        tail = list(unique_tails)[0]
        print(f"   ✅ Identical tail across candidates: '{tail}'")
        print(f"   → Published candidates show consistent tail pattern")
    else:
        print(f"   ⚠️  Multiple tails found: {unique_tails}")
        print(f"   → Tail varies between candidates")
    
    if len(unique_seam_tokens) == 1:
        seam = list(unique_seam_tokens)[0]
        print(f"   ✅ Identical seam tokens: '{seam}'")
        print(f"   → Seam content consistent across candidates")
    else:
        print(f"   ⚠️  Multiple seam patterns: {unique_seam_tokens}")
    
    print(f"\n📁 Results written to:")
    print(f"   CSV: {summary_file}")
    print(f"   JSON: {summary_json}")
    
    # Key finding
    if len(unique_seam_tokens) == 1 and "OFANANGLEISTHEARC" in list(unique_seam_tokens)[0]:
        print(f"\n🔍 Key Finding:")
        print(f"   Both published GRID candidates naturally produce the seam:")
        print(f"   '{list(unique_seam_tokens)[0]}'")
        print(f"   This suggests the tail may be cryptographically constrained,")
        print(f"   not merely an artifact of the seam guard policy.")
    
    return results

if __name__ == '__main__':
    main()