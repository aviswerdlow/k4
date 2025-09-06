#!/usr/bin/env python3
"""
Run a family of candidates through the Explore pipeline with full scoring.
Implements proper windowed anchor scoring BEFORE blinding, language scoring after.
"""

import json
import csv
import hashlib
import sys
import random
import string
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

# Add pipeline modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ExplorePipeline:
    """Full Explore pipeline implementation with proper scoring."""
    
    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Anchor definitions
        self.anchors = {
            "EAST": {"text": "EAST", "start": 21, "end": 25},
            "NORTHEAST": {"text": "NORTHEAST", "start": 25, "end": 34},
            "BERLINCLOCK": {"text": "BERLINCLOCK", "start": 63, "end": 74}
        }
        
        # Masked terms for blinding
        self.masked_terms = [
            "DIAL", "SET", "COURSE", "TRUE", "READ", "SEE", "NOTE",
            "SIGHT", "OBSERVE", "MERIDIAN", "DECLINATION", "BEARING", "LINE",
            "EAST", "NORTHEAST", "BERLINCLOCK", "NORTH", "BERLIN", "CLOCK"
        ]
        
        # Function words for coverage scoring
        self.function_words = set([
            "THE", "AND", "OF", "TO", "IN", "IS", "IT", "BE", "AS", "AT",
            "BY", "FOR", "ON", "OR", "IF", "AN", "BUT", "CAN", "HAD", "HER",
            "HIS", "HAS", "WAS", "ARE", "NOT", "ALL", "OUT", "UP", "SO", "SHE"
        ])
        
        # Compute baseline stats
        self.baseline_stats = self._compute_baseline_stats()
        
    def _compute_baseline_stats(self, num_samples: int = 1000) -> Dict:
        """Compute baseline statistics from random text."""
        ngram_scores = []
        coverage_scores = []
        compress_scores = []
        
        for _ in range(num_samples):
            # Generate random text
            text = ''.join(random.choices(string.ascii_uppercase, k=75))
            
            # Blind it
            blinded = self._blind_text(text)
            
            # Compute scores
            ngram_scores.append(self._compute_ngram_score(blinded))
            coverage_scores.append(self._compute_coverage_score(blinded))
            compress_scores.append(self._compute_compress_score(blinded))
        
        return {
            "ngram_mean": np.mean(ngram_scores),
            "ngram_std": np.std(ngram_scores),
            "coverage_mean": np.mean(coverage_scores),
            "coverage_std": np.std(coverage_scores),
            "compress_mean": np.mean(compress_scores),
            "compress_std": np.std(compress_scores)
        }
    
    def score_anchors(self, text: str, policy: Dict) -> Dict:
        """
        Score anchor alignment BEFORE blinding.
        
        Args:
            text: Head text to score
            policy: Anchor mode policy with window_radius and typo_budget
        
        Returns:
            Anchor scoring results
        """
        window_radius = policy.get("window_radius", 0)
        typo_budget = policy.get("typo_budget", 0)
        
        total_score = 0
        matches = {}
        
        for anchor_name, anchor_def in self.anchors.items():
            anchor_text = anchor_def["text"]
            expected_start = anchor_def["start"]
            expected_end = anchor_def["end"]
            
            # Define search window
            if policy["name"] == "shuffled":
                # Shuffled mode: search anywhere
                search_start = 0
                search_end = len(text) - len(anchor_text)
            else:
                # Fixed or windowed: search near expected position
                search_start = max(0, expected_start - window_radius)
                search_end = min(len(text) - len(anchor_text), expected_start + window_radius)
            
            # Search for anchor in window
            best_score = 0
            best_pos = -1
            
            for pos in range(search_start, search_end + 1):
                if pos + len(anchor_text) > len(text):
                    continue
                
                # Calculate match score with typo tolerance
                mismatches = 0
                for i, char in enumerate(anchor_text):
                    if text[pos + i] != char:
                        mismatches += 1
                
                if mismatches <= typo_budget:
                    # Score based on position and mismatches
                    position_penalty = abs(pos - expected_start) * 0.1
                    typo_penalty = mismatches * 0.2
                    score = 1.0 - position_penalty - typo_penalty
                    
                    if score > best_score:
                        best_score = score
                        best_pos = pos
            
            matches[anchor_name] = {
                "found": best_pos >= 0,
                "position": best_pos,
                "score": best_score
            }
            total_score += best_score
        
        return {
            "total_score": total_score / len(self.anchors),
            "matches": matches,
            "window_radius": window_radius,
            "typo_budget": typo_budget
        }
    
    def _blind_text(self, text: str) -> str:
        """
        Blind text by masking anchor and narrative terms.
        
        Args:
            text: Text to blind
        
        Returns:
            Blinded text with masked terms replaced by 'X'
        """
        blinded = text.upper()
        
        # Mask each term
        for term in self.masked_terms:
            # Replace all occurrences with X's
            while term in blinded:
                start = blinded.index(term)
                blinded = blinded[:start] + 'X' * len(term) + blinded[start + len(term):]
        
        return blinded
    
    def _compute_ngram_score(self, text: str) -> float:
        """Compute n-gram language score."""
        # Build bigrams and trigrams
        bigrams = defaultdict(int)
        trigrams = defaultdict(int)
        
        for i in range(len(text) - 1):
            bigrams[text[i:i+2]] += 1
        
        for i in range(len(text) - 2):
            trigrams[text[i:i+3]] += 1
        
        # Score based on common English patterns
        common_bigrams = ["TH", "HE", "IN", "ER", "AN", "ED", "ND", "TO", "EN", "ES"]
        common_trigrams = ["THE", "AND", "ING", "HER", "HAT", "HIS", "THA", "ERE", "FOR", "ENT"]
        
        bigram_score = sum(bigrams.get(bg, 0) for bg in common_bigrams) / max(1, sum(bigrams.values()))
        trigram_score = sum(trigrams.get(tg, 0) for tg in common_trigrams) / max(1, sum(trigrams.values()))
        
        return (bigram_score + trigram_score) / 2
    
    def _compute_coverage_score(self, text: str) -> float:
        """Compute function word coverage score."""
        # Simple word extraction (consecutive letters)
        words = []
        current_word = []
        
        for char in text + ' ':
            if char.isalpha():
                current_word.append(char)
            elif current_word:
                word = ''.join(current_word)
                if len(word) >= 2:
                    words.append(word)
                current_word = []
        
        if not words:
            return 0.0
        
        # Count function words
        function_count = sum(1 for w in words if w in self.function_words)
        
        return function_count / len(words)
    
    def _compute_compress_score(self, text: str) -> float:
        """Compute compressibility score using simple entropy estimate."""
        # Character frequency
        char_counts = defaultdict(int)
        for char in text:
            char_counts[char] += 1
        
        # Calculate entropy
        total = len(text)
        entropy = 0
        
        for count in char_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        # Normalize (max entropy for 26 letters is log2(26) ≈ 4.7)
        return entropy / 4.7
    
    def compute_score_v2(self, text: str, policy: Dict) -> Dict:
        """
        Compute full v2 score with anchors BEFORE blinding.
        
        Args:
            text: Head text to score
            policy: Anchor mode policy
        
        Returns:
            Complete scoring results
        """
        # Step 1: Score anchors BEFORE blinding
        anchor_result = self.score_anchors(text, policy)
        
        # Step 2: Blind the text
        blinded = self._blind_text(text)
        
        # Step 3: Compute language scores on blinded text
        ngram_raw = self._compute_ngram_score(blinded)
        coverage_raw = self._compute_coverage_score(blinded)
        compress_raw = self._compute_compress_score(blinded)
        
        # Step 4: Normalize using baseline
        z_ngram = (ngram_raw - self.baseline_stats["ngram_mean"]) / max(0.001, self.baseline_stats["ngram_std"])
        z_coverage = (coverage_raw - self.baseline_stats["coverage_mean"]) / max(0.001, self.baseline_stats["coverage_std"])
        z_compress = (compress_raw - self.baseline_stats["compress_mean"]) / max(0.001, self.baseline_stats["compress_std"])
        
        # Step 5: Combine scores
        weights = {"anchor": 0.3, "ngram": 0.3, "coverage": 0.2, "compress": 0.2}
        
        combined_score = (
            weights["anchor"] * anchor_result["total_score"] +
            weights["ngram"] * max(0, z_ngram) +
            weights["coverage"] * max(0, z_coverage) +
            weights["compress"] * max(0, z_compress)
        )
        
        return {
            "score_norm": combined_score,
            "anchor_result": anchor_result,
            "z_ngram": z_ngram,
            "z_coverage": z_coverage,
            "z_compress": z_compress,
            "raw_ngram": ngram_raw,
            "raw_coverage": coverage_raw,
            "raw_compress": compress_raw,
            "blinded_text": blinded[:20] + "..."  # Sample for inspection
        }
    
    def run_anchor_modes(self, text: str, policies: List[Dict]) -> Dict:
        """
        Run all anchor modes on a head and compute deltas.
        
        Args:
            text: Head text to evaluate
            policies: List of anchor mode policies
        
        Returns:
            Results including deltas
        """
        results = {}
        scores = {}
        
        # Score with each policy
        for policy in policies:
            result = self.compute_score_v2(text, policy)
            results[policy["name"]] = result
            scores[policy["name"]] = result["score_norm"]
        
        # Compute deltas
        fixed_score = scores.get("fixed", 0)
        shuffled_score = scores.get("shuffled", 0)
        
        # Best windowed score
        windowed_scores = [scores[k] for k in scores if "windowed" in k]
        best_windowed = max(windowed_scores) if windowed_scores else fixed_score
        
        delta_vs_windowed = fixed_score - best_windowed
        delta_vs_shuffled = fixed_score - shuffled_score
        
        return {
            "results": results,
            "scores": scores,
            "delta_vs_windowed": delta_vs_windowed,
            "delta_vs_shuffled": delta_vs_shuffled,
            "best_mode": max(scores, key=scores.get),
            "pass_deltas": delta_vs_windowed > 0.05 and delta_vs_shuffled > 0.10
        }
    
    def run_cheap_nulls(self, text: str, num_nulls: int = 1000) -> Dict:
        """
        Run cheap null hypothesis tests.
        
        Args:
            text: Head text that passed deltas
            num_nulls: Number of null tests
        
        Returns:
            Null test results
        """
        # Generate null distributions
        null_scores = []
        
        for _ in range(num_nulls):
            # Shuffle the text
            null_text = list(text)
            random.shuffle(null_text)
            null_text = ''.join(null_text)
            
            # Score the null
            policy = {"name": "fixed", "window_radius": 0, "typo_budget": 0}
            result = self.compute_score_v2(null_text, policy)
            null_scores.append(result["score_norm"])
        
        # Compare original to nulls
        original_policy = {"name": "fixed", "window_radius": 0, "typo_budget": 0}
        original_score = self.compute_score_v2(text, original_policy)["score_norm"]
        
        # Calculate p-value
        p_value = sum(1 for s in null_scores if s >= original_score) / len(null_scores)
        
        return {
            "original_score": original_score,
            "null_mean": np.mean(null_scores),
            "null_std": np.std(null_scores),
            "p_value": p_value,
            "pass_nulls": p_value < 0.05
        }
    
    def run_orbits(self, text: str, num_orbits: int = 100) -> Dict:
        """
        Run orbit analysis to check for ties.
        
        Args:
            text: Head text that passed nulls
            num_orbits: Number of orbit variations
        
        Returns:
            Orbit analysis results
        """
        orbit_scores = []
        
        for _ in range(num_orbits):
            # Create minor variation
            orbit_text = list(text)
            
            # Swap 2-3 random positions
            for _ in range(random.randint(2, 3)):
                i, j = random.sample(range(len(orbit_text)), 2)
                orbit_text[i], orbit_text[j] = orbit_text[j], orbit_text[i]
            
            orbit_text = ''.join(orbit_text)
            
            # Score orbit
            policy = {"name": "fixed", "window_radius": 0, "typo_budget": 0}
            result = self.compute_score_v2(orbit_text, policy)
            orbit_scores.append(result["score_norm"])
        
        # Check for ties
        original_policy = {"name": "fixed", "window_radius": 0, "typo_budget": 0}
        original_score = self.compute_score_v2(text, original_policy)["score_norm"]
        
        ties = sum(1 for s in orbit_scores if abs(s - original_score) < 0.01)
        
        return {
            "original_score": original_score,
            "orbit_mean": np.mean(orbit_scores),
            "orbit_std": np.std(orbit_scores),
            "num_ties": ties,
            "tie_rate": ties / num_orbits,
            "pass_orbits": ties < num_orbits * 0.1  # Less than 10% ties
        }


def run_campaign(
    campaign_id: str,
    adapter_path: Path,
    output_dir: Path,
    seed: int = 1337
) -> Dict:
    """
    Run a campaign through the full Explore pipeline.
    
    Args:
        campaign_id: Campaign identifier (C7-C16)
        adapter_path: Path to adapter module
        output_dir: Output directory for results
        seed: Random seed
    
    Returns:
        Campaign results summary
    """
    print(f"\n{'='*60}")
    print(f"Campaign {campaign_id}")
    print(f"{'='*60}")
    
    # Find heads file
    heads_file = output_dir / f"heads_{campaign_id.lower()}_*.json"
    heads_files = list(output_dir.glob(f"heads_{campaign_id.lower()}*.json"))
    
    if not heads_files:
        print(f"❌ No heads file found for {campaign_id}")
        return None
    
    heads_file = heads_files[0]
    
    # Load heads
    with open(heads_file) as f:
        data = json.load(f)
    heads = data["heads"]
    
    print(f"Loaded {len(heads)} heads from {heads_file.name}")
    
    # Initialize pipeline
    pipeline = ExplorePipeline(seed)
    
    # Define anchor policies
    policies = [
        {"name": "fixed", "window_radius": 0, "typo_budget": 0},
        {"name": "windowed_r1", "window_radius": 1, "typo_budget": 0},
        {"name": "windowed_r2", "window_radius": 2, "typo_budget": 0},
        {"name": "windowed_r3", "window_radius": 3, "typo_budget": 1},
        {"name": "windowed_r4", "window_radius": 4, "typo_budget": 1},
        {"name": "shuffled", "window_radius": 100, "typo_budget": 2}
    ]
    
    # Process heads
    all_results = []
    delta_passers = []
    null_passers = []
    orbit_passers = []
    
    for head_idx, head in enumerate(heads):
        if head_idx % 20 == 0:
            print(f"  Processing head {head_idx+1}/{len(heads)}...")
        
        text = head["text"]
        label = head["label"]
        
        # Run anchor modes
        mode_results = pipeline.run_anchor_modes(text, policies)
        
        # Record results
        result = {
            "label": label,
            "delta_vs_windowed": mode_results["delta_vs_windowed"],
            "delta_vs_shuffled": mode_results["delta_vs_shuffled"],
            "pass_deltas": mode_results["pass_deltas"],
            "best_mode": mode_results["best_mode"]
        }
        
        # If passes deltas, run nulls
        if mode_results["pass_deltas"]:
            delta_passers.append(label)
            
            null_result = pipeline.run_cheap_nulls(text, 1000)
            result["p_value"] = null_result["p_value"]
            result["pass_nulls"] = null_result["pass_nulls"]
            
            # If passes nulls, run orbits
            if null_result["pass_nulls"]:
                null_passers.append(label)
                
                orbit_result = pipeline.run_orbits(text, 100)
                result["tie_rate"] = orbit_result["tie_rate"]
                result["pass_orbits"] = orbit_result["pass_orbits"]
                
                if orbit_result["pass_orbits"]:
                    orbit_passers.append(label)
        
        all_results.append(result)
    
    # Create outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # EXPLORE_MATRIX.csv
    matrix_file = output_dir / "EXPLORE_MATRIX.csv"
    with open(matrix_file, 'w', newline='') as f:
        fieldnames = ["label", "delta_vs_windowed", "delta_vs_shuffled", "pass_deltas",
                     "p_value", "pass_nulls", "tie_rate", "pass_orbits"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in all_results:
            row = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(row)
    
    # Campaign report
    report_file = output_dir / f"{campaign_id}_REPORT.md"
    with open(report_file, 'w') as f:
        f.write(f"# Campaign {campaign_id} Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Seed:** {seed}\n")
        f.write(f"**Heads tested:** {len(heads)}\n\n")
        
        f.write("## Pipeline Results\n\n")
        f.write(f"- Delta passers: {len(delta_passers)}/{len(heads)}\n")
        f.write(f"- Null passers: {len(null_passers)}/{len(delta_passers) if delta_passers else 0}\n")
        f.write(f"- Orbit passers: {len(orbit_passers)}/{len(null_passers) if null_passers else 0}\n\n")
        
        if orbit_passers:
            f.write(f"## EXPLORE SURVIVORS: {len(orbit_passers)}\n\n")
            for label in orbit_passers:
                f.write(f"- {label}\n")
            f.write("\nThese heads passed all Explore criteria and could be queued for Confirm.\n")
        else:
            f.write("## Result: NEGATIVE\n\n")
            if not delta_passers:
                f.write("No heads passed delta thresholds.\n")
            elif not null_passers:
                f.write("Delta passers failed null hypothesis tests.\n")
            else:
                f.write("Null passers had too many orbit ties.\n")
    
    # Summary for dashboard
    summary = {
        "campaign": campaign_id,
        "heads_tested": len(heads),
        "delta_passers": len(delta_passers),
        "null_passers": len(null_passers),
        "orbit_passers": len(orbit_passers),
        "explore_survivors": len(orbit_passers)
    }
    
    print(f"\n  Results:")
    print(f"    Delta passers: {len(delta_passers)}")
    print(f"    Null passers: {len(null_passers)}")
    print(f"    Orbit passers: {len(orbit_passers)}")
    
    if orbit_passers:
        print(f"    ✅ {len(orbit_passers)} EXPLORE SURVIVORS")
    else:
        print(f"    ❌ NEGATIVE (stopped at {['deltas', 'nulls', 'orbits'][min(2, [bool(delta_passers), bool(null_passers), True].index(False))]})")
    
    return summary


def main():
    """Run all C7-C16 campaigns with full Explore pipeline."""
    
    base_dir = Path("experiments/pipeline_v2")
    summaries = []
    
    for campaign_id in ["C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16"]:
        output_dir = base_dir / f"runs/2025-01-06-explore-ideas-{campaign_id}"
        
        # Adapter path (not used in this simplified version, but kept for structure)
        adapter_path = base_dir / f"scripts/explore/adapters/gen_{campaign_id.lower()}.py"
        
        summary = run_campaign(campaign_id, adapter_path, output_dir, seed=1337)
        if summary:
            summaries.append(summary)
    
    # Create aggregate dashboard
    print(f"\n{'='*60}")
    print("AGGREGATE DASHBOARD")
    print(f"{'='*60}")
    
    dashboard_dir = base_dir / "runs/2025-01-06-explore-ideas"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    # Dashboard CSV
    dashboard_file = dashboard_dir / "DASHBOARD.csv"
    with open(dashboard_file, 'w', newline='') as f:
        fieldnames = ["campaign", "heads", "delta_passers", "null_passers", 
                     "orbit_passers", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for s in summaries:
            status = f"{s['explore_survivors']} survivors" if s['explore_survivors'] > 0 else "NEGATIVE"
            writer.writerow({
                "campaign": s["campaign"],
                "heads": s["heads_tested"],
                "delta_passers": s["delta_passers"],
                "null_passers": s["null_passers"],
                "orbit_passers": s["orbit_passers"],
                "status": status
            })
    
    # Summary report
    total_survivors = sum(s["explore_survivors"] for s in summaries)
    
    summary_file = dashboard_dir / "AGGREGATE_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write("# Explore C7-C16 Aggregate Summary\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Branch:** pipeline-v2-explore-ideas\n")
        f.write(f"**Seed:** 1337\n\n")
        
        f.write("## Campaign Results\n\n")
        f.write("| Campaign | Heads | Δ Pass | Nulls Pass | Orbits Pass | Status |\n")
        f.write("|----------|-------|--------|------------|-------------|--------|\n")
        
        for s in summaries:
            status = f"{s['explore_survivors']} survivors" if s['explore_survivors'] > 0 else "NEGATIVE"
            f.write(f"| {s['campaign']} | {s['heads_tested']} | {s['delta_passers']} | ")
            f.write(f"{s['null_passers']} | {s['orbit_passers']} | {status} |\n")
        
        f.write(f"\n**Total Explore Survivors:** {total_survivors}\n\n")
        
        if total_survivors == 0:
            f.write("## Conclusion: ALL NEGATIVE ✅\n\n")
            f.write("All 10 high-impact campaigns were successfully falsified by the Explore pipeline.\n")
            f.write("No candidates qualify for the Confirm queue.\n")
        else:
            f.write(f"## Conclusion: {total_survivors} EXPLORE SURVIVORS ⚠️\n\n")
            f.write("These heads passed all Explore criteria:\n")
            f.write("- Beat both delta thresholds (>0.05 vs windowed, >0.10 vs shuffled)\n")
            f.write("- Passed 1k cheap null tests (p < 0.05)\n")
            f.write("- Had minimal orbit ties (<10%)\n\n")
            f.write("Status: `explore_survivor_pending_confirm`\n")
    
    print(f"\n📊 Dashboard: {dashboard_file}")
    print(f"📄 Summary: {summary_file}")
    
    # Final one-liners
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}\n")
    
    for s in summaries:
        if s["explore_survivors"] > 0:
            print(f"{s['campaign']:4} → {s['explore_survivors']} survivors (Explore-only)")
        else:
            reason = "deltas" if s["delta_passers"] == 0 else "nulls" if s["null_passers"] == 0 else "orbits"
            print(f"{s['campaign']:4} → 0 promotions; negative result due to {reason}")
    
    print(f"\n{'='*60}")
    if total_survivors == 0:
        print("✅ ALL CAMPAIGNS NEGATIVE - Pipeline successfully falsified all hypotheses")
    else:
        print(f"⚠️ {total_survivors} EXPLORE SURVIVORS pending Confirm (not run in this wave)")
    
    return summaries


if __name__ == "__main__":
    summaries = main()