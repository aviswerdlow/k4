#!/usr/bin/env python3
"""
SIM_DETECTOR - Scan for mock/placeholder patterns in the repository.
Detects simulated outputs masquerading as empirical results.
"""

import os
import re
import csv
import json
from pathlib import Path
from datetime import datetime

# Patterns that indicate simulation/mock content
CODE_PATTERNS = [
    (r'(?i)(simulated|mock|placeholder|demo|fake|pseudo)', 'HIGH', 'Simulation keyword'),
    (r'if\s+.*:\s*p_value\s*=\s*0\.(0+|999)', 'HIGH', 'Hardcoded p-value'),
    (r'print\(.*"(fabricat|simulate|expected behavior)"', 'MED', 'Simulation print'),
    (r'return\s*{\s*"publishable"\s*:\s*(True|False).*#(?!.*compute)', 'HIGH', 'Fixed return without computation'),
    (r'# Mock|# Simulated|# Placeholder', 'HIGH', 'Simulation comment'),
]

def scan_code_file(filepath):
    """Scan a Python/bash file for simulation patterns."""
    hits = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            for pattern, severity, note in CODE_PATTERNS:
                if re.search(pattern, content):
                    hits.append({
                        'path': str(filepath),
                        'type': 'code',
                        'regex_hit': pattern[:30] + '...',
                        'severity': severity,
                        'note': note
                    })
    except Exception as e:
        pass
    return hits

def scan_json_file(filepath):
    """Scan JSON files for missing required fields."""
    hits = []
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        filename = os.path.basename(filepath)
        
        # Check phrase_gate_report.json
        if filename == 'phrase_gate_report.json':
            if 'accepted_by' not in data or not data.get('accepted_by'):
                hits.append({
                    'path': str(filepath),
                    'type': 'json',
                    'regex_hit': 'missing accepted_by',
                    'severity': 'HIGH',
                    'note': 'Missing or empty accepted_by field'
                })
        
        # Check holm_report_canonical.json
        if filename == 'holm_report_canonical.json':
            required = ['K', 'metrics', 'p_raw', 'p_holm']
            missing = []
            if 'K' not in data:
                missing.append('K')
            if 'metrics' not in data:
                missing.append('metrics')
            elif data.get('metrics'):
                for metric in ['coverage', 'f_words']:
                    if metric in data['metrics']:
                        if 'p_raw' not in data['metrics'][metric]:
                            missing.append(f'{metric}.p_raw')
                        if 'p_holm' not in data['metrics'][metric]:
                            missing.append(f'{metric}.p_holm')
            
            if missing:
                hits.append({
                    'path': str(filepath),
                    'type': 'json',
                    'regex_hit': f'missing: {",".join(missing)}',
                    'severity': 'HIGH',
                    'note': 'Missing nulls fields'
                })
        
        # Check coverage_report.json
        if filename == 'coverage_report.json':
            required = ['encrypts_to_ct', 't2_sha256', 'seed_recipe', 'seed_u64']
            missing = [f for f in required if f not in data]
            if missing:
                hits.append({
                    'path': str(filepath),
                    'type': 'json',
                    'regex_hit': f'missing: {",".join(missing)}',
                    'severity': 'HIGH',
                    'note': 'Missing coverage fields'
                })
                
    except Exception as e:
        pass
    return hits

def scan_markdown_file(filepath):
    """Scan markdown files for claims without evidence."""
    hits = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for pass/fail claims
        if re.search(r'(?i)(pass|publishable|success|fail)', content):
            # Check if there are JSON files in the same directory
            parent_dir = Path(filepath).parent
            json_files = list(parent_dir.glob('*.json'))
            
            if len(json_files) == 0:
                hits.append({
                    'path': str(filepath),
                    'type': 'md',
                    'regex_hit': 'claims without JSON',
                    'severity': 'MED',
                    'note': 'Pass/fail claims but no JSON evidence'
                })
    except Exception as e:
        pass
    return hits

def scan_repository(base_path):
    """Scan the entire repository for simulation patterns."""
    all_hits = []
    
    # Directories to exclude
    exclude_dirs = {
        'experiments/_simulated',
        'release',
        'results',
        '.git',
        '__pycache__'
    }
    
    for root, dirs, files in os.walk(base_path):
        # Remove excluded directories from traversal
        dirs[:] = [d for d in dirs if not any(ex in os.path.join(root, d) for ex in exclude_dirs)]
        
        for file in files:
            filepath = Path(root) / file
            
            # Skip if in excluded path
            if any(ex in str(filepath) for ex in exclude_dirs):
                continue
            
            # Scan based on file type
            if file.endswith('.py') or file.endswith('.sh'):
                all_hits.extend(scan_code_file(filepath))
            elif file.endswith('.json'):
                all_hits.extend(scan_json_file(filepath))
            elif file.endswith('.md'):
                all_hits.extend(scan_markdown_file(filepath))
    
    return all_hits

def main():
    """Main execution."""
    base_dir = Path(__file__).parent.parent.parent  # experiments/
    output_dir = base_dir / "audit" / "runs" / "2025-09-05"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Running SIM_DETECTOR scan...")
    print(f"Scanning: {base_dir}")
    
    # Run scan
    hits = scan_repository(base_dir)
    
    # Sort by severity and path
    severity_order = {'HIGH': 0, 'MED': 1, 'LOW': 2}
    hits.sort(key=lambda x: (severity_order.get(x['severity'], 99), x['path']))
    
    # Write CSV
    output_file = output_dir / "SIM_DETECTOR.csv"
    with open(output_file, 'w', newline='') as f:
        if hits:
            writer = csv.DictWriter(f, fieldnames=['path', 'type', 'regex_hit', 'severity', 'note'])
            writer.writeheader()
            writer.writerows(hits)
        else:
            f.write("path,type,regex_hit,severity,note\n")
            f.write("NO_HITS,none,none,none,Clean scan - no simulation patterns detected\n")
    
    # Print summary
    print(f"\nSIM_DETECTOR Results:")
    print(f"Total hits: {len(hits)}")
    
    high_count = sum(1 for h in hits if h['severity'] == 'HIGH')
    med_count = sum(1 for h in hits if h['severity'] == 'MED')
    low_count = sum(1 for h in hits if h['severity'] == 'LOW')
    
    print(f"  HIGH severity: {high_count}")
    print(f"  MED severity: {med_count}")
    print(f"  LOW severity: {low_count}")
    
    if high_count > 0:
        print("\n⚠️  HIGH severity hits detected - review required!")
        for hit in hits[:5]:  # Show first 5
            if hit['severity'] == 'HIGH':
                print(f"  - {hit['path']}: {hit['note']}")
    
    print(f"\nResults saved to: {output_file}")
    
    return len(hits)

if __name__ == "__main__":
    exit(0 if main() == 0 else 1)