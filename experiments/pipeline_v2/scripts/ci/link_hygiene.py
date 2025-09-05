#!/usr/bin/env python3
"""
Link hygiene checker for CI.
Ensures documentation only links to empirical folders and proper bundles.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Patterns to find links in markdown
LINK_PATTERNS = [
    r'\[.*?\]\((.*?)\)',  # [text](link)
    r'`([^`]*experiments/[^`]*)`',  # `path/to/experiments/...`
    r'"([^"]*experiments/[^"]*)"',  # "path/to/experiments/..."
]

# Allowed empirical folders
ALLOWED_PATTERNS = [
    r'experiments/pipeline_v2/.*',
    r'experiments/p74_editorial/.*',
    r'results/.*',
]

# Explicitly forbidden patterns
FORBIDDEN_PATTERNS = [
    r'.*_simulated/.*',
    r'.*_conceptual/.*',
    r'.*_draft/.*',
    r'.*_test/.*',
]

def extract_links(file_path: Path) -> List[str]:
    """Extract all experiment links from a file."""
    if not file_path.exists():
        return []
    
    with open(file_path) as f:
        content = f.read()
    
    links = []
    for pattern in LINK_PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE)
        links.extend(matches)
    
    # Filter to only experiment links
    experiment_links = [
        link for link in links 
        if 'experiments/' in link or 'results/' in link
    ]
    
    return experiment_links

def check_link_validity(link: str, allowlist: Set[str] = None) -> Tuple[bool, str]:
    """
    Check if a link is valid according to hygiene rules.
    
    Returns:
        Tuple of (is_valid, reason)
    """
    # Check allowlist first
    if allowlist and link in allowlist:
        return True, "allowlisted"
    
    # Check forbidden patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.match(pattern, link):
            return False, f"forbidden pattern: {pattern}"
    
    # Check allowed patterns
    for pattern in ALLOWED_PATTERNS:
        if re.match(pattern, link):
            return True, "allowed pattern"
    
    # Default: not allowed
    return False, "not in allowed patterns"

def check_bundle_completeness(bundle_dir: Path) -> Tuple[bool, List[str]]:
    """
    Check if a Confirm bundle has all required files.
    
    Returns:
        Tuple of (is_complete, missing_files)
    """
    required_files = [
        "proof_digest.json",
        "phrase_gate_report.json",
        "holm_report_canonical.json",
        "near_gate_report.json",
        "hashes.txt"
    ]
    
    missing = []
    for file_name in required_files:
        if not (bundle_dir / file_name).exists():
            missing.append(file_name)
    
    return len(missing) == 0, missing

def check_pre_registration(runs_dir: Path) -> Tuple[bool, str]:
    """
    Check if latest Confirm run has a pre-registration.
    
    Returns:
        Tuple of (has_prereg, message)
    """
    # Find latest confirm directory
    confirm_dirs = list(runs_dir.glob("*/confirm"))
    if not confirm_dirs:
        return True, "No Confirm runs found"
    
    latest_confirm = max(confirm_dirs, key=lambda p: p.stat().st_mtime)
    run_date = latest_confirm.parent.name
    
    # Check for pre-reg
    prereg_path = Path(f"experiments/pipeline_v2/docs/pre_reg/ANALYSIS_PLAN_{run_date}.md")
    
    if prereg_path.exists():
        return True, f"Pre-registration found: {prereg_path}"
    else:
        return False, f"Missing pre-registration for {run_date}"

def load_allowlist(allowlist_path: Path) -> Set[str]:
    """Load allowlist of permitted links."""
    if not allowlist_path.exists():
        return set()
    
    allowlist = set()
    with open(allowlist_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse format: "path # reason"
                if '#' in line:
                    path = line.split('#')[0].strip()
                else:
                    path = line
                allowlist.add(path)
    
    return allowlist

def run_hygiene_check(root_dir: Path, verbose: bool = False) -> Dict:
    """
    Run complete hygiene check.
    
    Returns:
        Dictionary with check results
    """
    results = {
        "passed": True,
        "link_issues": [],
        "bundle_issues": [],
        "prereg_issues": [],
        "stats": {
            "files_checked": 0,
            "links_found": 0,
            "bundles_checked": 0
        }
    }
    
    # Load allowlist
    allowlist_path = root_dir / "experiments/pipeline_v2/ci/ALLOWLIST.txt"
    allowlist = load_allowlist(allowlist_path)
    
    # Check all markdown files
    for md_file in root_dir.glob("**/*.md"):
        # Skip archive directories
        if "archive" in str(md_file):
            continue
            
        results["stats"]["files_checked"] += 1
        
        links = extract_links(md_file)
        results["stats"]["links_found"] += len(links)
        
        for link in links:
            valid, reason = check_link_validity(link, allowlist)
            
            if not valid:
                results["link_issues"].append({
                    "file": str(md_file.relative_to(root_dir)),
                    "link": link,
                    "reason": reason
                })
                results["passed"] = False
                
                if verbose:
                    print(f"❌ Invalid link in {md_file.name}: {link}")
                    print(f"   Reason: {reason}")
    
    # Check Confirm bundles
    confirm_dirs = list(Path(root_dir).glob("experiments/pipeline_v2/runs/*/confirm/bundle_*"))
    
    for bundle_dir in confirm_dirs:
        results["stats"]["bundles_checked"] += 1
        
        complete, missing = check_bundle_completeness(bundle_dir)
        
        if not complete:
            results["bundle_issues"].append({
                "bundle": str(bundle_dir.relative_to(root_dir)),
                "missing": missing
            })
            results["passed"] = False
            
            if verbose:
                print(f"❌ Incomplete bundle: {bundle_dir.name}")
                print(f"   Missing: {', '.join(missing)}")
    
    # Check pre-registration
    runs_dir = root_dir / "experiments/pipeline_v2/runs"
    has_prereg, message = check_pre_registration(runs_dir)
    
    if not has_prereg:
        results["prereg_issues"].append(message)
        results["passed"] = False
        
        if verbose:
            print(f"❌ {message}")
    
    return results

def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Link hygiene checker")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--create-allowlist", action="store_true", 
                       help="Create example allowlist file")
    
    args = parser.parse_args()
    
    root = Path(args.root)
    
    if args.create_allowlist:
        allowlist_path = root / "experiments/pipeline_v2/ci/ALLOWLIST.txt"
        allowlist_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(allowlist_path, 'w') as f:
            f.write("# Link Hygiene Allowlist\n")
            f.write("# Format: path/to/link # reason for allowing\n")
            f.write("# Lines starting with # are comments\n\n")
            f.write("# Example entries:\n")
            f.write("# experiments/legacy/important_result.csv # Historical reference\n")
            f.write("# experiments/draft/work_in_progress.md # Temporary during migration\n")
        
        print(f"Created allowlist template: {allowlist_path}")
        return
    
    print("Running link hygiene check...")
    results = run_hygiene_check(root, args.verbose)
    
    print(f"\nResults:")
    print(f"  Files checked: {results['stats']['files_checked']}")
    print(f"  Links found: {results['stats']['links_found']}")
    print(f"  Bundles checked: {results['stats']['bundles_checked']}")
    
    if results["link_issues"]:
        print(f"\n❌ Link issues: {len(results['link_issues'])}")
        for issue in results["link_issues"][:5]:  # Show first 5
            print(f"    - {issue['file']}: {issue['link']}")
    
    if results["bundle_issues"]:
        print(f"\n❌ Bundle issues: {len(results['bundle_issues'])}")
        for issue in results["bundle_issues"][:5]:
            print(f"    - {issue['bundle']}: missing {', '.join(issue['missing'])}")
    
    if results["prereg_issues"]:
        print(f"\n❌ Pre-registration issues:")
        for issue in results["prereg_issues"]:
            print(f"    - {issue}")
    
    if results["passed"]:
        print("\n✅ All hygiene checks passed!")
        return 0
    else:
        print("\n❌ Hygiene checks failed. Fix issues before merging.")
        return 1

if __name__ == "__main__":
    exit(main())