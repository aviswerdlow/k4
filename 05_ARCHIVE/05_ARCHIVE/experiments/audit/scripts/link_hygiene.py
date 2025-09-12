#!/usr/bin/env python3
"""
LINK_HYGIENE - Check README and docs for links to simulated content.
Ensures all links point to empirical or clearly marked conceptual content.
"""

import os
import re
import csv
from pathlib import Path
from datetime import datetime

def extract_links(content):
    """Extract all experiment links from markdown content."""
    links = []
    
    # Pattern for markdown links and backtick paths
    patterns = [
        r'\[([^\]]+)\]\(([^)]+experiments/[^)]+)\)',  # [text](path)
        r'`(experiments/[^`]+)`',  # `path`
        r'experiments/[\w/_\-\.]+',  # Direct paths
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            if len(match.groups()) == 2:
                # Markdown link
                text = match.group(1)
                path = match.group(2)
            elif len(match.groups()) == 1:
                # Backtick path
                path = match.group(1)
                text = path
            else:
                # Direct path
                path = match.group(0)
                text = path
            
            # Clean up path
            path = path.strip()
            if path.startswith('experiments/'):
                links.append((text, path))
    
    return links

def classify_path(path, base_dir):
    """Classify a path as Empirical, Conceptual, Simulated, or Unknown."""
    full_path = base_dir.parent / path  # Go up to repo root
    
    # Check if path exists
    if not full_path.exists():
        return 'Unknown', False, 'Path does not exist'
    
    # Check for simulated content
    if '_simulated' in str(path):
        return 'Simulated', False, 'In quarantine folder'
    
    # Check for conceptual marker
    if 'conceptual' in str(path).lower():
        return 'Conceptual', True, 'Marked as conceptual'
    
    # Check if directory has README indicating conceptual
    if full_path.is_dir():
        readme_path = full_path / 'README.md'
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read().lower()
                if 'conceptual' in content or 'no execution' in content or 'not executed' in content:
                    return 'Conceptual', True, 'Has conceptual README'
    
    # Check for empirical markers (bundle files)
    if full_path.is_dir():
        required_files = {'coverage_report.json', 'phrase_gate_report.json'}
        existing = {f.name for f in full_path.iterdir() if f.is_file()}
        if required_files.issubset(existing):
            return 'Empirical', True, 'Has bundle files'
    
    # Check parent directories for classification
    parent = full_path.parent
    if parent.name in ['runs', 'results', 'data']:
        # Likely empirical
        return 'Empirical', True, 'In empirical directory'
    
    if parent.name in ['docs', 'policies']:
        # Documentation/configuration
        return 'Empirical', True, 'Documentation/config'
    
    # Default to unknown
    return 'Unknown', False, 'Cannot classify'

def check_file(filepath, base_dir):
    """Check all links in a file."""
    results = []
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        links = extract_links(content)
        
        for text, path in links:
            classification, ok, note = classify_path(path, base_dir)
            
            results.append({
                'link_text': text[:50],  # Truncate long text
                'target_path': path,
                'exists': 'true' if (base_dir.parent / path).exists() else 'false',
                'classification': classification,
                'ok': str(ok).lower(),
                'note': note
            })
    
    except Exception as e:
        results.append({
            'link_text': 'ERROR',
            'target_path': str(filepath),
            'exists': 'false',
            'classification': 'Error',
            'ok': 'false',
            'note': str(e)
        })
    
    return results

def main():
    """Main execution."""
    base_dir = Path(__file__).parent.parent.parent  # experiments/
    repo_root = base_dir.parent
    output_dir = base_dir / "audit" / "runs" / "2025-09-05"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Running LINK_HYGIENE check...")
    print(f"Checking: {repo_root}")
    
    # Files to check
    files_to_check = [
        repo_root / 'README.md',
        repo_root / 'VALIDATION.md',
    ]
    
    # Add any other markdown files in root
    for f in repo_root.glob('*.md'):
        if f not in files_to_check:
            files_to_check.append(f)
    
    # Check all files
    all_results = []
    problematic_count = 0
    
    for filepath in files_to_check:
        if filepath.exists():
            print(f"Checking: {filepath.name}")
            results = check_file(filepath, base_dir)
            all_results.extend(results)
            
            # Count problematic links
            for r in results:
                if r['ok'] == 'false':
                    problematic_count += 1
    
    # Sort by classification and path
    all_results.sort(key=lambda x: (x['classification'], x['target_path']))
    
    # Write CSV
    output_file = output_dir / "LINKS.csv"
    with open(output_file, 'w', newline='') as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=['link_text', 'target_path', 'exists', 'classification', 'ok', 'note'])
            writer.writeheader()
            writer.writerows(all_results)
        else:
            f.write("link_text,target_path,exists,classification,ok,note\n")
            f.write("NO_LINKS,none,n/a,n/a,n/a,No experiment links found\n")
    
    # Print summary
    print(f"\nLINK_HYGIENE Results:")
    print(f"Total links checked: {len(all_results)}")
    print(f"Problematic links: {problematic_count}")
    
    # Count by classification
    classifications = {}
    for r in all_results:
        cls = r['classification']
        classifications[cls] = classifications.get(cls, 0) + 1
    
    print("\nLinks by classification:")
    for cls, count in sorted(classifications.items()):
        print(f"  {cls}: {count}")
    
    if problematic_count > 0:
        print("\n⚠️  Problematic links found:")
        for r in all_results[:10]:  # Show first 10
            if r['ok'] == 'false':
                print(f"  - {r['target_path']}: {r['note']}")
    
    print(f"\nResults saved to: {output_file}")
    
    return problematic_count

if __name__ == "__main__":
    exit(0 if main() == 0 else 1)