#!/usr/bin/env python3
"""
Score all community hypothesis campaigns through the Explore pipeline.
Creates aggregate dashboard with results.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add adapters to path
sys.path.append(str(Path(__file__).parent / "adapters"))

from score_community_heads import score_campaign_heads, compute_baseline_stats


def score_all_campaigns():
    """Score all community campaigns and create dashboard."""
    
    base_dir = Path("experiments/community_hypotheses")
    
    # Campaign definitions
    campaigns = [
        ("c1", "quagmire", "QUAGMIRE_III"),
        ("c2", "trifid_cube", "TRIFID_CUBE"),
        ("c3", "morse", "MORSE"),
        ("c4", "bigram_polybius", "BIGRAM_POLYBIUS"),
        ("c5", "time_key", "TIME_KEY"),
        ("c6", "letter_shape", "LETTER_SHAPE")
    ]
    
    # Compute baseline once
    print("Computing baseline statistics...")
    baseline_stats = compute_baseline_stats(num_samples=1000, seed=1337)
    
    # Score each campaign
    all_summaries = []
    total_promotions = 0
    
    for campaign_id, name, label in campaigns:
        print(f"\n{'='*60}")
        print(f"Scoring Campaign {campaign_id.upper()}: {label}")
        print(f"{'='*60}")
        
        # Find heads file
        heads_file = base_dir / f"runs/2025-01-06-campaign-{campaign_id}" / f"heads_{campaign_id}_{name}.json"
        
        if not heads_file.exists():
            print(f"  ⚠️  No heads file found: {heads_file}")
            continue
        
        # Score the campaign
        output_dir = heads_file.parent
        
        try:
            summary = score_campaign_heads(heads_file, output_dir)
            all_summaries.append(summary)
            total_promotions += summary["promotions"]
            
            print(f"\n  ✅ Campaign {campaign_id.upper()} complete:")
            print(f"     - Heads: {summary['heads']}")
            print(f"     - Tests: {summary['tests']}")
            print(f"     - Promotions: {summary['promotions']}")
            
        except Exception as e:
            print(f"  ❌ Error scoring campaign {campaign_id}: {e}")
    
    # Create aggregate dashboard
    print(f"\n{'='*60}")
    print("AGGREGATE DASHBOARD")
    print(f"{'='*60}")
    
    dashboard = {
        "title": "Community Hypothesis Mining - Aggregate Results",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "description": "Testing community K4 decryption hypotheses through Explore pipeline",
        "total_campaigns": len(all_summaries),
        "total_heads": sum(s["heads"] for s in all_summaries),
        "total_tests": sum(s["tests"] for s in all_summaries),
        "total_promotions": total_promotions,
        "promotion_rate": total_promotions / sum(s["tests"] for s in all_summaries) if all_summaries else 0,
        "campaigns": []
    }
    
    # Add campaign summaries
    for summary in all_summaries:
        campaign_summary = {
            "campaign": summary["campaign"],
            "heads": summary["heads"],
            "tests": summary["tests"],
            "promotions": summary["promotions"],
            "promotion_rate": summary["promotion_rate"],
            "status": "✅ Complete" if summary["promotions"] == 0 else f"⚠️ {summary['promotions']} promotions"
        }
        dashboard["campaigns"].append(campaign_summary)
    
    # Save dashboard
    dashboard_file = base_dir / "COMMUNITY_DASHBOARD.json"
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    # Create markdown report
    report = [
        "# Community Hypothesis Mining Results",
        "",
        f"**Date:** {dashboard['date']}",
        f"**Total Campaigns:** {dashboard['total_campaigns']}",
        f"**Total Heads:** {dashboard['total_heads']}",
        f"**Total Tests:** {dashboard['total_tests']}",
        f"**Total Promotions:** {dashboard['total_promotions']} 🎯",
        "",
        "## Campaign Results",
        "",
        "| Campaign | Heads | Tests | Promotions | Status |",
        "|----------|-------|-------|------------|--------|"
    ]
    
    for campaign in dashboard["campaigns"]:
        report.append(
            f"| {campaign['campaign']} | {campaign['heads']} | "
            f"{campaign['tests']} | {campaign['promotions']} | {campaign['status']} |"
        )
    
    report.extend([
        "",
        "## Conclusion",
        "",
        f"All {dashboard['total_campaigns']} community hypothesis campaigns have been tested through the Explore pipeline."
    ])
    
    if dashboard["total_promotions"] == 0:
        report.extend([
            "",
            "**Result:** ✅ 0 promotions across all campaigns",
            "",
            "This is the expected outcome for the Explore pipeline - weak hypotheses are efficiently",
            "falsified through blinded scoring and hard controls. The pipeline is working as designed."
        ])
    else:
        report.extend([
            "",
            f"**Result:** ⚠️ {dashboard['total_promotions']} promotions detected",
            "",
            "Some heads passed the delta thresholds. These should be investigated further",
            "in the Confirm pipeline with stricter validation."
        ])
    
    report.extend([
        "",
        "## Files",
        "",
        f"- Dashboard: `{dashboard_file}`",
        f"- Campaign runs: `{base_dir}/runs/2025-01-06-campaign-*/`",
        f"- Scores: `{base_dir}/runs/*/scores_*.json`",
        "",
        "---",
        "",
        "*Community Hypothesis Mining Complete*"
    ])
    
    report_file = base_dir / "COMMUNITY_REPORT.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"\n📊 Dashboard saved: {dashboard_file}")
    print(f"📄 Report saved: {report_file}")
    print(f"\n✅ Community Hypothesis Mining Complete!")
    print(f"   Total promotions: {dashboard['total_promotions']}")
    
    return dashboard


def main():
    """Main entry point."""
    dashboard = score_all_campaigns()
    
    # Print summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    for campaign in dashboard["campaigns"]:
        print(f"  {campaign['campaign']:20} → {campaign['status']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()