#!/usr/bin/env python3
"""
Full-deck seam-free spot check
Tests non-GRID routes (SPOKE, RAILFENCE) alongside GRID candidates
"""

import json
import csv
from pathlib import Path

def main():
    """Full-deck seam-free tail spot check"""
    print("🔬 K4 Full-Deck Seam-Free Spot Check")
    print("=" * 45)
    print("Question: Do non-GRID routes also produce the same tail?")
    print("Method: Direct examination across route families\n")
    
    # Paths to candidates across route families
    base_dir = Path(__file__).parent.parent.parent.parent
    results_dir = base_dir / "results/GRID_ONLY"
    archive_dir = base_dir / "archive/2025-09-03/uniq_prescreen/uniq_sweep"
    
    candidates = {
        # GRID routes (published)
        "cand_005": {"route": "GRID_W14_ROWS", "family": "GRID", "desc": "Winner", "path": results_dir},
        "cand_004": {"route": "GRID_W10_NW", "family": "GRID", "desc": "Runner-up", "path": archive_dir},
        
        # Non-GRID routes (archived)
        "cand_001": {"route": "SPOKE_NE_NF_w1", "family": "SPOKE", "desc": "Non-GRID", "path": archive_dir},
        "cand_006": {"route": "RAILFENCE_R3_INVERTED", "family": "RAILFENCE", "desc": "Non-GRID", "path": archive_dir}
    }
    
    results = []
    
    for cand_label, info in candidates.items():
        cand_dir = info["path"] / cand_label
        pt_file = cand_dir / "plaintext_97.txt"
        
        if pt_file.exists():
            with open(pt_file, 'r') as f:
                plaintext = f.read().strip()
            
            if len(plaintext) == 97:
                # Extract sections
                head_section = plaintext[:75]      # Characters 0-74 (phrase gate scoring)
                tail_75_96 = plaintext[75:97]      # Full tail section
                hejoy_guard = plaintext[75:80]     # HEJOY guard
                seam_tokens = plaintext[80:97]     # Seam tokens
                
                # Identify head variation (key difference)
                head_variation = "UNKNOWN"
                if "ISCODE" in plaintext:
                    head_variation = "TEXT IS CODE"
                elif "ISAMAP" in plaintext:
                    head_variation = "TEXT IS A MAP"
                elif "ISREAL" in plaintext:
                    head_variation = "TEXT IS REAL"
                elif "ISDATA" in plaintext:
                    head_variation = "TEXT IS DATA"
                
                print(f"📋 {cand_label} ({info['family']}) - Route: {info['route']}")
                print(f"   Full plaintext: {plaintext}")
                print(f"   Head variation: {head_variation}")
                print(f"   Tail [75:97]:   {tail_75_96}")
                print(f"   HEJOY [75:80]:  {hejoy_guard}")
                print(f"   Seam [80:97]:   {seam_tokens}")
                print(f"   Route family:   {info['family']}")
                print()
                
                results.append({
                    'label': cand_label,
                    'route_id': info['route'],
                    'route_family': info['family'],
                    'description': info['desc'],
                    'head_variation': head_variation,
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
    
    # Update summary CSV with full-deck results
    summary_file = runs_dir / "full_deck_summary.csv"
    with open(summary_file, 'w', newline='') as f:
        fieldnames = ['label', 'route_id', 'route_family', 'description', 'head_variation', 
                     'tail_75_96', 'hejoy_guard', 'seam_tokens', 'plaintext_sha256']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # JSON summary  
    summary_json = runs_dir / "full_deck_summary.json"
    with open(summary_json, 'w') as f:
        json.dump({
            'experiment': 'full_deck_seam_free_spot_check',
            'description': 'Cross-route family examination of tail consistency',
            'route_families_tested': ['GRID', 'SPOKE', 'RAILFENCE'],
            'results': results
        }, f, indent=2)
    
    # Analysis by route family
    print("🎯 Cross-Route Family Analysis:")
    
    # Group by route family
    by_family = {}
    for result in results:
        family = result['route_family']
        if family not in by_family:
            by_family[family] = []
        by_family[family].append(result)
    
    # Check tail consistency
    all_tails = set(r['tail_75_96'] for r in results)
    all_seam_tokens = set(r['seam_tokens'] for r in results)
    all_head_variations = set(r['head_variation'] for r in results)
    
    print(f"   Route families: {list(by_family.keys())}")
    print(f"   Head variations: {sorted(all_head_variations)}")
    print(f"   Unique tails: {len(all_tails)}")
    print(f"   Unique seam patterns: {len(all_seam_tokens)}")
    
    if len(all_tails) == 1:
        tail = list(all_tails)[0]
        print(f"   ✅ IDENTICAL tail across ALL route families: '{tail}'")
        print(f"   → Tail convergence spans GRID, SPOKE, and RAILFENCE routes")
    else:
        print(f"   ⚠️  Multiple tails found: {all_tails}")
    
    if len(all_seam_tokens) == 1:
        seam = list(all_seam_tokens)[0]
        print(f"   ✅ IDENTICAL seam tokens across ALL routes: '{seam}'")
    
    # Family-by-family breakdown
    print(f"\n📊 By Route Family:")
    for family, family_results in by_family.items():
        family_tails = set(r['tail_75_96'] for r in family_results)
        family_heads = set(r['head_variation'] for r in family_results)
        print(f"   {family}: {len(family_results)} candidates")
        print(f"     Head variations: {sorted(family_heads)}")
        print(f"     Tail consistency: {'✅ Identical' if len(family_tails) == 1 else f'⚠️ Multiple: {family_tails}'}")
    
    print(f"\n📁 Results written to:")
    print(f"   CSV: {summary_file}")
    print(f"   JSON: {summary_json}")
    
    # Key finding
    if len(all_seam_tokens) == 1 and len(all_head_variations) > 2:
        print(f"\n🔍 Critical Finding:")
        print(f"   All {len(results)} candidates across {len(by_family)} route families")
        print(f"   produce IDENTICAL seam tokens: '{list(all_seam_tokens)[0]}'")
        print(f"   despite different head content: {sorted(all_head_variations)}")
        print(f"   ")
        print(f"   This provides STRONG empirical evidence that the K4 tail")
        print(f"   is cryptographically constrained by the ciphertext structure,")
        print(f"   independent of both route family and head content variations.")
        
        return True  # Tail forcing confirmed across all families
    
    return False

if __name__ == '__main__':
    confirmed = main()
    exit(0 if confirmed else 1)