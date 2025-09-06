#!/usr/bin/env python3
"""
Production A/B Pilot for Explore v4.1.1 Language Weights Hotfix
Interfaces with actual verb_robust_mcmc generation pipeline
"""

import json
import hashlib
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
from datetime import datetime
import subprocess
import sys

# Constants
MASTER_SEED = 1337
PILOT_SIZE = 50  # per arm

# Weight file paths
WEIGHTS_V4_1_PATH = "experiments/pipeline_v4/policies/weights.explore_v4_1.json"
WEIGHTS_V4_1_1_PATH = "experiments/pipeline_v4/policies/weights.explore_v4_1_1.json"

# Output paths
OUTPUT_DIR = Path("experiments/pipeline_v4/runs/track_a_l/pilot")
MATRIX_PATH = OUTPUT_DIR / "HEAD_GATE_MATRIX.csv"
REPORT_PATH = OUTPUT_DIR / "PILOT_REPORT.md"

# Thresholds (from pre-registration)
HEAD_GATE_THRESHOLDS = {
    "fw_min": 0.35,
    "verb_min": 3,
    "cov_min": 0.70,
    "pattern_min": 0.60
}
DELTA_THRESHOLD = 0.15
SHUFFLED_THRESHOLD = 0.12
ACCEPTANCE_THRESHOLDS = {
    "head_gate_rate": 0.80,
    "delta_rate": 0.25,
    "max_leakage": 0.000
}

def derive_seed(master_seed: int, head_id: int) -> int:
    """Derive deterministic seed for each head."""
    seed_str = f"{master_seed}:{head_id}"
    hash_val = hashlib.sha256(seed_str.encode()).hexdigest()
    return int(hash_val[:16], 16) % (2**32)

def create_weights_v4_1():
    """Create v4.1 weights file if it doesn't exist."""
    weights_v4_1 = {
        "lambda_ng": 1.0,
        "lambda_fw": 0.4,
        "lambda_cov": 0.2,
        "lambda_pattern": 0.8,
        "lambda_verb": 1.2,
        "lambda_fw_cap": 0.4,
        "lambda_fratio": 0.5
    }
    
    path = Path(WEIGHTS_V4_1_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(weights_v4_1, f, indent=2)
    
    # Calculate SHA-256
    with open(path, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    
    print(f"Created v4.1 weights: {path}")
    print(f"  SHA-256: {sha256}")
    
    return path

def run_generation_pipeline(
    seed: int, 
    weights_path: str,
    head_id: str
) -> Dict:
    """
    Run actual generation pipeline with given weights.
    
    This function should interface with your actual verb_robust_mcmc.py
    and related pipeline components.
    
    Returns:
        Dictionary with metrics: fw_post, verb_post, cov_post, pattern_post, 
        delta_windowed_min, delta_shuffled, leakage_diff
    """
    # TODO: Replace this with actual pipeline call
    # Example structure:
    # 
    # cmd = [
    #     "python3", 
    #     "verb_robust_mcmc.py",
    #     "--seed", str(seed),
    #     "--weights", weights_path,
    #     "--output", f"pilot_{head_id}.json"
    # ]
    # result = subprocess.run(cmd, capture_output=True, text=True)
    # 
    # Then parse the output and extract metrics
    
    raise NotImplementedError(
        "Connect to actual generation pipeline here.\n"
        "This should call your verb_robust_mcmc.py with the specified weights file."
    )

def check_head_gate(metrics: Dict) -> bool:
    """Check if head passes head-gate criteria."""
    return (
        metrics.get("fw_post", 0) >= HEAD_GATE_THRESHOLDS["fw_min"] and
        metrics.get("verb_post", 0) >= HEAD_GATE_THRESHOLDS["verb_min"] and
        metrics.get("cov_post", 0) >= HEAD_GATE_THRESHOLDS["cov_min"] and
        metrics.get("pattern_post", 0) >= HEAD_GATE_THRESHOLDS["pattern_min"]
    )

def check_deltas(metrics: Dict) -> bool:
    """Check if head passes delta thresholds."""
    return (
        metrics.get("delta_windowed_min", 0) >= DELTA_THRESHOLD and
        metrics.get("delta_shuffled", 0) >= SHUFFLED_THRESHOLD
    )

def run_pilot():
    """Run the production A/B pilot test."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ensure both weight files exist
    if not Path(WEIGHTS_V4_1_PATH).exists():
        create_weights_v4_1()
    
    if not Path(WEIGHTS_V4_1_1_PATH).exists():
        raise FileNotFoundError(f"Missing v4.1.1 weights: {WEIGHTS_V4_1_1_PATH}")
    
    results = []
    
    print(f"Running A/B Pilot with {PILOT_SIZE} heads per arm...")
    print(f"Master seed: {MASTER_SEED}")
    print()
    
    for i in range(PILOT_SIZE):
        seed_u64 = derive_seed(MASTER_SEED, i)
        
        # Arm A: v4.1 weights
        print(f"Generating head {i:03d} Arm A (v4.1 weights)...")
        try:
            metrics_a = run_generation_pipeline(
                seed_u64, 
                WEIGHTS_V4_1_PATH,
                f"head_{i:03d}_A"
            )
            passed_hg_a = check_head_gate(metrics_a)
            passed_delta_a = check_deltas(metrics_a)
            
            results.append({
                "label": f"head_{i:03d}_A",
                "seed_u64": seed_u64,
                "arm": "A",
                **metrics_a,
                "passed_head_gate": passed_hg_a,
                "passed_deltas": passed_delta_a
            })
        except NotImplementedError as e:
            print(f"\n{e}")
            print("\nPilot runner is ready but needs connection to actual pipeline.")
            return None
        
        # Arm B: v4.1.1 weights
        print(f"Generating head {i:03d} Arm B (v4.1.1 weights)...")
        metrics_b = run_generation_pipeline(
            seed_u64,
            WEIGHTS_V4_1_1_PATH,
            f"head_{i:03d}_B"
        )
        passed_hg_b = check_head_gate(metrics_b)
        passed_delta_b = check_deltas(metrics_b)
        
        results.append({
            "label": f"head_{i:03d}_B",
            "seed_u64": seed_u64,
            "arm": "B",
            **metrics_b,
            "passed_head_gate": passed_hg_b,
            "passed_deltas": passed_delta_b
        })
        
        # Progress update
        if (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/{PILOT_SIZE} head pairs")
    
    return pd.DataFrame(results)

def analyze_results(df: pd.DataFrame) -> Dict:
    """Analyze pilot results against pre-registered thresholds."""
    arm_a = df[df["arm"] == "A"]
    arm_b = df[df["arm"] == "B"]
    
    # Calculate pass rates
    hg_rate_a = arm_a["passed_head_gate"].mean()
    hg_rate_b = arm_b["passed_head_gate"].mean()
    delta_rate_a = arm_a["passed_deltas"].mean()
    delta_rate_b = arm_b["passed_deltas"].mean()
    
    # Check leakage
    max_leakage = df["leakage_diff"].max()
    
    # Check acceptance thresholds
    passes_thresholds = (
        hg_rate_b >= ACCEPTANCE_THRESHOLDS["head_gate_rate"] and
        delta_rate_b >= ACCEPTANCE_THRESHOLDS["delta_rate"] and
        max_leakage <= ACCEPTANCE_THRESHOLDS["max_leakage"] and
        hg_rate_b > hg_rate_a  # Clear improvement required
    )
    
    # Check marginal case
    marginal_delta = (0.20 <= delta_rate_b < 0.25)
    
    return {
        "arm_a": {
            "head_gate_rate": hg_rate_a,
            "delta_rate": delta_rate_a,
            "total_survivors": (arm_a["passed_head_gate"] & arm_a["passed_deltas"]).sum()
        },
        "arm_b": {
            "head_gate_rate": hg_rate_b,
            "delta_rate": delta_rate_b,
            "total_survivors": (arm_b["passed_head_gate"] & arm_b["passed_deltas"]).sum()
        },
        "max_leakage": max_leakage,
        "passes_thresholds": passes_thresholds,
        "marginal_delta": marginal_delta
    }

def generate_report(df: pd.DataFrame, analysis: Dict) -> str:
    """Generate pilot report matching pre-registration format."""
    
    # Load weight configurations for report
    with open(WEIGHTS_V4_1_PATH, 'r') as f:
        weights_v4_1 = json.load(f)
    with open(WEIGHTS_V4_1_1_PATH, 'r') as f:
        weights_v4_1_1 = json.load(f)
    
    report = f"""# A/B Pilot Report - Explore v4.1.1 Production

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Master Seed**: {MASTER_SEED}
**Sample Size**: {PILOT_SIZE} heads per arm
**Pre-registration**: `ANALYSIS_PLAN_2025-01-06_explore-v4.1.1.md`

## Weight Configurations

### Arm A (Control - v4.1)
```json
{json.dumps(weights_v4_1, indent=2)}
```

### Arm B (Treatment - v4.1.1)
```json
{json.dumps(weights_v4_1_1, indent=2)}
```

## Results Summary

### Arm A (Control)
- Head-gate Pass Rate: {analysis['arm_a']['head_gate_rate']:.1%}
- Delta Pass Rate: {analysis['arm_a']['delta_rate']:.1%}
- Total Survivors: {analysis['arm_a']['total_survivors']}/{PILOT_SIZE}

### Arm B (Treatment)
- Head-gate Pass Rate: {analysis['arm_b']['head_gate_rate']:.1%}
- Delta Pass Rate: {analysis['arm_b']['delta_rate']:.1%}
- Total Survivors: {analysis['arm_b']['total_survivors']}/{PILOT_SIZE}

## Threshold Assessment (Pre-registered)

- **Head-gate Pass Rate (B)**: ≥80% - {"✅ PASS" if analysis['arm_b']['head_gate_rate'] >= 0.80 else "❌ FAIL"} ({analysis['arm_b']['head_gate_rate']:.1%})
- **Delta Pass Rate (B)**: ≥25% - {"✅ PASS" if analysis['arm_b']['delta_rate'] >= 0.25 else "❌ FAIL"} ({analysis['arm_b']['delta_rate']:.1%})
- **Leakage**: 0.000 - {"✅ PASS" if analysis['max_leakage'] == 0.000 else "❌ FAIL"} ({analysis['max_leakage']:.3f})
- **Improvement over A**: {"✅ YES" if analysis['arm_b']['head_gate_rate'] > analysis['arm_a']['head_gate_rate'] else "❌ NO"}

## Decision

**Overall**: {"✅ PROCEED TO K=200" if analysis['passes_thresholds'] else "⚠️ MARGINAL - PROCEED WITH CAUTION" if analysis['marginal_delta'] else "❌ DO NOT PROCEED - Mark v4.1.1 as SATURATED"}

{"Note: Delta pass rate is in marginal range (20-24%). Proceeding but will require ≥10 survivors at K=200 delta stage before orbits/nulls." if analysis['marginal_delta'] else ""}

## Metrics Distributions

### Function Words (fw_post)
- Arm A: Mean={df[df['arm']=='A']['fw_post'].mean():.3f}, Std={df[df['arm']=='A']['fw_post'].std():.3f}
- Arm B: Mean={df[df['arm']=='B']['fw_post'].mean():.3f}, Std={df[df['arm']=='B']['fw_post'].std():.3f}

### Verb Count
- Arm A: Mean={df[df['arm']=='A']['verb_post'].mean():.1f}, Std={df[df['arm']=='A']['verb_post'].std():.1f}
- Arm B: Mean={df[df['arm']=='B']['verb_post'].mean():.1f}, Std={df[df['arm']=='B']['verb_post'].std():.1f}

### Coverage
- Arm A: Mean={df[df['arm']=='A']['cov_post'].mean():.3f}, Std={df[df['arm']=='A']['cov_post'].std():.3f}
- Arm B: Mean={df[df['arm']=='B']['cov_post'].mean():.3f}, Std={df[df['arm']=='B']['cov_post'].std():.3f}

### Pattern
- Arm A: Mean={df[df['arm']=='A']['pattern_post'].mean():.3f}, Std={df[df['arm']=='A']['pattern_post'].std():.3f}
- Arm B: Mean={df[df['arm']=='B']['pattern_post'].mean():.3f}, Std={df[df['arm']=='B']['pattern_post'].std():.3f}

## Reproducibility

- Master Seed: {MASTER_SEED}
- v4.1 weights SHA-256: [calculated at runtime]
- v4.1.1 weights SHA-256: 457181035efbc666a0babc1c067d48f8c263862447280f21ef0cafd8988f83b6
- All seeds deterministically derived from master seed
"""
    return report

def main():
    """Main execution."""
    print("=" * 60)
    print("PRODUCTION A/B PILOT - Explore v4.1.1")
    print("=" * 60)
    print()
    
    # Run pilot
    df = run_pilot()
    
    if df is None:
        print("\nPilot framework is ready. Connect run_generation_pipeline() to your actual pipeline.")
        return
    
    # Analyze results
    print("\nAnalyzing results...")
    analysis = analyze_results(df)
    
    # Save matrix
    df.to_csv(MATRIX_PATH, index=False)
    print(f"Saved matrix to {MATRIX_PATH}")
    
    # Generate and save report
    report = generate_report(df, analysis)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"Saved report to {REPORT_PATH}")
    
    # Print decision
    print("\n" + "=" * 60)
    if analysis["passes_thresholds"]:
        print("✅ PILOT PASSES ALL THRESHOLDS")
        print("Proceeding to K=200 production run")
    elif analysis["marginal_delta"]:
        print("⚠️ MARGINAL RESULT")
        print("Delta rate in 20-24% range. Proceed with caution.")
        print("K=200 will require ≥10 survivors at delta stage.")
    else:
        print("❌ PILOT FAILS THRESHOLDS")
        print("Do not proceed. Mark v4.1.1 as SATURATED.")
    
    print(f"\nArm B (v4.1.1) Results:")
    print(f"  Head-gate: {analysis['arm_b']['head_gate_rate']:.1%} (threshold: ≥80%)")
    print(f"  Deltas: {analysis['arm_b']['delta_rate']:.1%} (threshold: ≥25%)")
    print(f"  Leakage: {analysis['max_leakage']:.3f} (threshold: 0.000)")
    print(f"  Survivors: {analysis['arm_b']['total_survivors']}/{PILOT_SIZE}")
    print("=" * 60)

if __name__ == "__main__":
    main()