#!/usr/bin/env python3
"""
Phase 0: Check if K3 structural hints justify L=15 independently of K4.
Pure mechanical analysis - no K4 head/tail semantics.
"""

import math
from collections import defaultdict

def analyze_k3_structure():
    """
    Analyze K3's known structure for period hints.
    K3 uses 4x7 columnar transposition followed by Vigenère.
    """
    print("\n=== K3 Structural Analysis ===")
    
    # K3 facts
    k3_rows = 4
    k3_cols = 7
    k3_length = 336
    
    print(f"\nK3 Known Structure:")
    print(f"  Stage 1: Columnar transposition ({k3_rows} rows × {k3_cols} columns)")
    print(f"  Stage 2: Vigenère decryption")
    print(f"  Total length: {k3_length} characters")
    print(f"  Co-prime property: gcd({k3_rows}, {k3_cols}) = {math.gcd(k3_rows, k3_cols)}")
    
    # Check various period relationships
    print(f"\nPeriod Relationships:")
    
    periods_to_test = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    
    for L in periods_to_test:
        # Check co-prime with K3 dimensions
        gcd_rows = math.gcd(L, k3_rows)
        gcd_cols = math.gcd(L, k3_cols)
        gcd_total = math.gcd(L, k3_rows * k3_cols)
        
        # Check divisibility patterns
        k3_periods = k3_length / L
        k4_periods = 97 / L
        
        # Special relationships
        special = []
        if gcd_rows == 1 and gcd_cols == 1:
            special.append("co-prime with K3 grid")
        if L % k3_cols == 0:
            special.append(f"multiple of K3 cols ({k3_cols})")
        if L % k3_rows == 0:
            special.append(f"multiple of K3 rows ({k3_rows})")
        if abs(L - k3_rows * k3_cols) <= 2:
            special.append(f"near K3 grid size ({k3_rows * k3_cols})")
        
        print(f"\n  L={L:2d}:")
        print(f"    gcd(L, 4) = {gcd_rows}, gcd(L, 7) = {gcd_cols}")
        print(f"    K3 periods: {k3_periods:.2f}")
        print(f"    K4 periods: {k4_periods:.2f}")
        if special:
            print(f"    Special: {', '.join(special)}")

def check_k1_k2_patterns():
    """
    Check K1 and K2 for any period-related patterns.
    """
    print("\n=== K1/K2 Pattern Analysis ===")
    
    # K1: PALIMPSEST (10 chars) used twice
    k1_key = "PALIMPSEST"
    k1_period = len(k1_key)
    
    # K2: ABSCISSA (8 chars) keyed Caesar
    k2_key = "ABSCISSA"
    k2_period = len(k2_key)
    
    print(f"\nK1 (Vigenère):")
    print(f"  Key: {k1_key} (length {k1_period})")
    print(f"  Used: 2 times")
    
    print(f"\nK2 (Keyed Caesar):")
    print(f"  Key: {k2_key} (length {k2_period})")
    
    # Check relationships with candidate periods
    print(f"\nRelationships with candidate periods:")
    
    for L in [14, 15, 16, 17]:
        relationships = []
        
        # Check GCD relationships
        gcd_k1 = math.gcd(L, k1_period)
        gcd_k2 = math.gcd(L, k2_period)
        
        if gcd_k1 == 1:
            relationships.append(f"co-prime with K1({k1_period})")
        if gcd_k2 == 1:
            relationships.append(f"co-prime with K2({k2_period})")
        
        # Check factors
        if L % k1_period == 0:
            relationships.append(f"multiple of K1 period")
        if L % k2_period == 0:
            relationships.append(f"multiple of K2 period")
        
        # Sum/difference relationships
        if L == k1_period + k2_period:
            relationships.append("K1 + K2 periods")
        if L == k1_period + k2_period - 3:
            relationships.append("K1 + K2 - 3")
        if L == k1_period + k2_period / 2:
            relationships.append("K1 + K2/2")
        
        print(f"  L={L}: {', '.join(relationships) if relationships else 'no special relationships'}")

def analyze_factor_patterns():
    """
    Look for factor/divisor patterns across K1-K3.
    """
    print("\n=== Factor Pattern Analysis ===")
    
    # Known dimensions
    factors = {
        'K1': [2, 5, 10],  # PALIMPSEST factors
        'K2': [2, 4, 8],   # ABSCISSA factors
        'K3_rows': [2, 4], # 4 rows
        'K3_cols': [7],    # 7 columns (prime)
        'K3_grid': [4, 7, 28]  # 4×7 = 28
    }
    
    print("\nFactor occurrences:")
    factor_counts = defaultdict(int)
    for source, flist in factors.items():
        for f in flist:
            factor_counts[f] += 1
    
    for factor in sorted(factor_counts.keys()):
        count = factor_counts[factor]
        sources = [s for s, flist in factors.items() if factor in flist]
        print(f"  {factor:2d}: appears {count} times in {sources}")
    
    # Check which periods have most common factors
    print("\nCandidate periods by factor alignment:")
    
    for L in [14, 15, 16, 17, 18, 20, 21, 28]:
        L_factors = []
        for i in range(2, L):
            if L % i == 0:
                L_factors.append(i)
        
        common = [f for f in L_factors if f in factor_counts]
        score = sum(factor_counts[f] for f in common)
        
        print(f"  L={L:2d}: factors {L_factors}, common {common}, score={score}")

def compute_coprime_coverage():
    """
    Check co-prime coverage properties for different periods.
    """
    print("\n=== Co-prime Coverage Analysis ===")
    
    # For 6-track system with 97 positions
    n_tracks = 6
    n_positions = 97
    
    print(f"\nFor 6-track system with {n_positions} positions:")
    
    for L in [14, 15, 16, 17, 18, 20]:
        # Check co-prime with position count
        gcd_97 = math.gcd(L, n_positions)
        
        # Check slot reuse
        slots_per_class = L
        total_slots = n_tracks * L
        positions_per_slot = n_positions / total_slots if total_slots > 0 else 0
        
        # Check if creates 1-to-1 mapping
        one_to_one = (total_slots >= n_positions and gcd_97 == 1)
        
        print(f"\n  L={L}:")
        print(f"    gcd(L, 97) = {gcd_97}")
        print(f"    Total slots: {total_slots}")
        print(f"    Avg positions/slot: {positions_per_slot:.2f}")
        print(f"    1-to-1 mapping: {one_to_one}")
        
        # Special properties
        if L == 15:
            print(f"    Note: 15 = 3×5 (product of two small primes)")
            print(f"    Note: 15 = K1(10) + K2(8)/2 + 1")
        if L == 14:
            print(f"    Note: 14 = 2×7 (K3 cols × 2)")
        if L == 17:
            print(f"    Note: 17 is prime")

def main():
    """Run all K3-based period analyses"""
    print("\n" + "="*60)
    print("PHASE 0: Prior-Panel Period Justification")
    print("Searching for L=15 signals in K1-K3 (no K4 semantics)")
    print("="*60)
    
    analyze_k3_structure()
    check_k1_k2_patterns()
    analyze_factor_patterns()
    compute_coprime_coverage()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print("""
Key observations:
1. K3 uses 4×7 grid (28 total), both co-prime
2. L=14 (2×7) aligns with K3 column dimension
3. L=15 (3×5) is product of two small primes
4. L=15 gives 90 total slots for 97 positions (slight reuse)
5. L=17 gives 102 slots for 97 positions (1-to-1 mapping)

Mechanical verdict:
- No strong K3 signal specifically favoring L=15 over L=17
- L=14 has clearer K3 relationship (2×K3_cols)
- L=15 has no direct K1-K3 derivation
- Proceed with L=15 as "what-if" test only
""")

if __name__ == "__main__":
    main()