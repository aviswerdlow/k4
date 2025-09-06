#!/usr/bin/env python3
"""
Production K=200 Runner for Explore v4.1.1
Only runs if pilot passes pre-registered thresholds
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import sys

# Constants
MASTER_SEED = 1337
BATCH_SIZE = 200

# Paths
WEIGHTS_PATH = "experiments/pipeline_v4/policies/weights.explore_v4_1_1.json"
OUTPUT_DIR = Path("experiments/pipeline_v4/runs/track_a_l/batch_200_v4_1_1")
PILOT_REPORT = Path("experiments/pipeline_v4/runs/track_a_l/pilot/PILOT_REPORT.md")

# Thresholds (from pre-registration)
HEAD_GATE_THRESHOLDS = {
    "fw_min": 0.35,
    "verb_min": 3,
    "cov_min": 0.70,
    "pattern_min": 0.60
}
DELTA_THRESHOLD = 0.15
SHUFFLED_THRESHOLD = 0.12
ORBIT_EPSILON = 0.15
NULL_K = 1000
NULL_ALPHA = 0.01

def check_pilot_passed() -> bool:
    """Check if pilot passed thresholds before proceeding."""
    if not PILOT_REPORT.exists():
        print("❌ ERROR: No pilot report found. Run pilot first.")
        return False
    
    with open(PILOT_REPORT, 'r') as f:
        report = f.read()
    
    # Check for the decision markers
    if "✅ PROCEED TO K=200" in report:
        print("✅ Pilot passed all thresholds - proceeding to K=200")
        return True
    elif "⚠️ MARGINAL - PROCEED WITH CAUTION" in report:
        print("⚠️ Pilot in marginal range - proceeding with ≥10 survivor requirement")
        return True
    else:
        print("❌ Pilot failed thresholds - cannot proceed to K=200")
        print("Mark v4.1.1 as SATURATED per pre-registration")
        return False

def derive_seed(master_seed: int, head_id: int) -> int:
    """Derive deterministic seed for each head."""
    seed_str = f"{master_seed}:{head_id}"
    hash_val = hashlib.sha256(seed_str.encode()).hexdigest()
    return int(hash_val[:16], 16) % (2**32)

def run_generation_pipeline(
    seed: int,
    head_id: str
) -> Dict:
    """
    Run actual generation pipeline with v4.1.1 weights.
    
    TODO: Connect to your actual verb_robust_mcmc.py pipeline
    """
    raise NotImplementedError(
        "Connect to actual generation pipeline here.\n"
        f"Use weights from: {WEIGHTS_PATH}\n"
        f"Seed: {seed}\n"
        f"Output ID: {head_id}"
    )

def run_orbit_isolation(heads: List[Dict]) -> List[Dict]:
    """
    Run orbit isolation on surviving heads.
    
    Args:
        heads: List of heads that passed head-gate and deltas
    
    Returns:
        List of orbit-isolated heads (ε_tie ≤ 0.15)
    """
    # TODO: Implement actual orbit isolation
    raise NotImplementedError("Implement orbit isolation logic")

def run_fast_nulls(heads: List[Dict]) -> List[Dict]:
    """
    Run fast null hypothesis testing.
    
    Args:
        heads: Orbit-isolated heads
    
    Returns:
        List of heads passing null tests (Holm m=2, both adj-p < 0.01)
    """
    # TODO: Implement fast null testing
    raise NotImplementedError("Implement fast null hypothesis testing")

def generate_explore_matrix(results: List[Dict]) -> pd.DataFrame:
    """Generate the EXPLORE_MATRIX.csv with all metrics."""
    df = pd.DataFrame(results)
    
    # Add derived columns
    df['passed_head_gate'] = df.apply(
        lambda x: (
            x['fw_post'] >= HEAD_GATE_THRESHOLDS['fw_min'] and
            x['verb_post'] >= HEAD_GATE_THRESHOLDS['verb_min'] and
            x['cov_post'] >= HEAD_GATE_THRESHOLDS['cov_min'] and
            x['pattern_post'] >= HEAD_GATE_THRESHOLDS['pattern_min']
        ), axis=1
    )
    
    df['passed_deltas'] = df.apply(
        lambda x: (
            x.get('delta_windowed_min', 0) >= DELTA_THRESHOLD and
            x.get('delta_shuffled', 0) >= SHUFFLED_THRESHOLD
        ), axis=1
    )
    
    return df

def generate_dashboard(df: pd.DataFrame) -> pd.DataFrame:
    """Generate dashboard summary statistics."""
    dashboard = {
        'metric': [],
        'value': []
    }
    
    # Stage counts
    dashboard['metric'].append('total_heads')
    dashboard['value'].append(len(df))
    
    dashboard['metric'].append('passed_head_gate')
    dashboard['value'].append(df['passed_head_gate'].sum())
    
    dashboard['metric'].append('passed_deltas')
    dashboard['value'].append((df['passed_head_gate'] & df['passed_deltas']).sum())
    
    # Pass rates
    dashboard['metric'].append('head_gate_rate')
    dashboard['value'].append(f"{df['passed_head_gate'].mean():.1%}")
    
    dashboard['metric'].append('delta_rate')
    dashboard['value'].append(f"{df[df['passed_head_gate']]['passed_deltas'].mean():.1%}")
    
    # Metric distributions
    for metric in ['fw_post', 'verb_post', 'cov_post', 'pattern_post']:
        dashboard['metric'].append(f'{metric}_mean')
        dashboard['value'].append(f"{df[metric].mean():.3f}")
        
        dashboard['metric'].append(f'{metric}_std')
        dashboard['value'].append(f"{df[metric].std():.3f}")
    
    return pd.DataFrame(dashboard)

def generate_report(df: pd.DataFrame, survivors: List[Dict]) -> str:
    """Generate the final EXPLORE_REPORT.md."""
    
    # Calculate funnel statistics
    total = len(df)
    hg_pass = df['passed_head_gate'].sum()
    delta_pass = (df['passed_head_gate'] & df['passed_deltas']).sum()
    orbit_pass = len([s for s in survivors if s.get('orbit_isolated', False)])
    null_pass = len([s for s in survivors if s.get('null_passed', False)])
    
    report = f"""# Explore v4.1.1 Production Report (K=200)

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Branch**: pipeline-v4.1.1-explore-language-first
**Weights**: v4.1.1 (λ_fw=0.8)
**Weights SHA-256**: 457181035efbc666a0babc1c067d48f8c263862447280f21ef0cafd8988f83b6

## Funnel Analysis

| Stage | Count | Pass Rate | Notes |
|-------|-------|-----------|-------|
| Generated | {total} | 100% | Input heads |
| Head-gate | {hg_pass} | {hg_pass/total:.1%} | fw≥0.35, verb≥3, cov≥0.70, pattern≥0.60 |
| Deltas | {delta_pass} | {delta_pass/total:.1%} | windowed_min≥0.15, shuffled≥0.12 |
| Orbits | {orbit_pass} | {orbit_pass/total:.1%} | ε_tie ≤ 0.15 |
| Fast Nulls | {null_pass} | {null_pass/total:.1%} | K=1000, Holm m=2, adj-p<0.01 |

## Comparison with v4.1 (Failed Run)

| Metric | v4.1 (λ_fw=0.4) | v4.1.1 (λ_fw=0.8) | Improvement |
|--------|-----------------|-------------------|-------------|
| Head-gate | 1/200 (0.5%) | {hg_pass}/200 ({hg_pass/200:.1%}) | {(hg_pass/200 - 0.005)/0.005:.0%} |
| Deltas | 0/200 (0%) | {delta_pass}/200 ({delta_pass/200:.1%}) | N/A |
| Final | 0 | {null_pass} | +{null_pass} |

## Language Metrics (Post-Repair)

| Metric | Mean | Std | Min | Max |
|--------|------|-----|-----|-----|
| Function Words | {df['fw_post'].mean():.3f} | {df['fw_post'].std():.3f} | {df['fw_post'].min():.3f} | {df['fw_post'].max():.3f} |
| Verb Count | {df['verb_post'].mean():.1f} | {df['verb_post'].std():.1f} | {df['verb_post'].min():.0f} | {df['verb_post'].max():.0f} |
| Coverage | {df['cov_post'].mean():.3f} | {df['cov_post'].std():.3f} | {df['cov_post'].min():.3f} | {df['cov_post'].max():.3f} |
| Pattern | {df['pattern_post'].mean():.3f} | {df['pattern_post'].std():.3f} | {df['pattern_post'].min():.3f} | {df['pattern_post'].max():.3f} |

## Survivors for Promotion

Total heads promoted to Confirm phase: **{null_pass}**

See `promotion_queue.json` for full details including:
- Route IDs
- T2 SHA hashes
- Class schedules
- Seed recipes

## Reproducibility

- Master Seed: {MASTER_SEED}
- Weights: `policies/weights.explore_v4_1_1.json`
- Exact CLI: See `REPRO_STEPS.md`
- All artifacts: See `MANIFEST.sha256`

## Conclusion

{"✅ SUCCESS: v4.1.1 weights fixed the function word deficit and produced viable candidates." if null_pass > 0 else "❌ SATURATED: v4.1.1 did not produce sufficient survivors despite improved head-gate performance."}
"""
    return report

def main():
    """Main execution."""
    print("=" * 60)
    print("EXPLORE v4.1.1 PRODUCTION RUN (K=200)")
    print("=" * 60)
    print()
    
    # Check pilot results first
    if not check_pilot_passed():
        sys.exit(1)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load weights and verify SHA
    with open(WEIGHTS_PATH, 'r') as f:
        weights = json.load(f)
    
    with open(WEIGHTS_PATH, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    
    print(f"\nWeights loaded from: {WEIGHTS_PATH}")
    print(f"SHA-256: {sha256}")
    print(f"λ_fw: {weights['lambda_fw']}")
    print()
    
    results = []
    print(f"Generating {BATCH_SIZE} heads...")
    
    for i in range(BATCH_SIZE):
        seed = derive_seed(MASTER_SEED, i)
        head_id = f"explore_v411_{i:04d}"
        
        try:
            # Run generation pipeline
            metrics = run_generation_pipeline(seed, head_id)
            results.append({
                "head_id": head_id,
                "seed": seed,
                **metrics
            })
            
            # Progress update
            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{BATCH_SIZE} heads")
                
        except NotImplementedError as e:
            print(f"\n{e}")
            print("\nProduction runner is ready but needs connection to actual pipeline.")
            print("\nTo complete integration:")
            print("1. Implement run_generation_pipeline()")
            print("2. Implement run_orbit_isolation()")
            print("3. Implement run_fast_nulls()")
            return
    
    # Generate explore matrix
    print("\nGenerating metrics matrix...")
    df = generate_explore_matrix(results)
    df.to_csv(OUTPUT_DIR / "EXPLORE_MATRIX.csv", index=False)
    
    # Generate dashboard
    print("Generating dashboard...")
    dashboard = generate_dashboard(df)
    dashboard.to_csv(OUTPUT_DIR / "DASHBOARD.csv", index=False)
    
    # Filter survivors
    survivors = df[df['passed_head_gate'] & df['passed_deltas']].to_dict('records')
    print(f"\nHeads passing head-gate + deltas: {len(survivors)}")
    
    # Check marginal case requirement
    pilot_marginal = "⚠️ MARGINAL" in open(PILOT_REPORT).read()
    if pilot_marginal and len(survivors) < 10:
        print("❌ FAILURE: Marginal pilot required ≥10 delta survivors, got", len(survivors))
        print("Mark v4.1.1 as SATURATED")
        sys.exit(1)
    
    # Run orbit isolation
    print(f"Running orbit isolation (ε_tie ≤ {ORBIT_EPSILON})...")
    orbit_survivors = run_orbit_isolation(survivors)
    print(f"  Orbit-isolated: {len(orbit_survivors)}")
    
    # Run fast nulls
    print(f"Running fast null tests (K={NULL_K}, Holm m=2)...")
    final_survivors = run_fast_nulls(orbit_survivors)
    print(f"  Null test passed: {len(final_survivors)}")
    
    # Save promotion queue
    with open(OUTPUT_DIR / "promotion_queue.json", 'w') as f:
        json.dump(final_survivors, f, indent=2)
    
    # Generate report
    print("\nGenerating final report...")
    report = generate_report(df, final_survivors)
    with open(OUTPUT_DIR / "EXPLORE_REPORT.md", 'w') as f:
        f.write(report)
    
    # Generate manifest
    print("Generating manifest...")
    manifest = []
    for file in OUTPUT_DIR.glob("*"):
        if file.is_file():
            with open(file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            manifest.append(f"{file_hash}  {file.name}")
    
    with open(OUTPUT_DIR / "MANIFEST.sha256", 'w') as f:
        f.write("\n".join(manifest))
    
    # Final summary
    print("\n" + "=" * 60)
    print("PRODUCTION RUN COMPLETE")
    print(f"  Total heads: {BATCH_SIZE}")
    print(f"  Head-gate passed: {df['passed_head_gate'].sum()}")
    print(f"  Deltas passed: {(df['passed_head_gate'] & df['passed_deltas']).sum()}")
    print(f"  Final survivors: {len(final_survivors)}")
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()