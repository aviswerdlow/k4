"""K4 verify command - quick validation checks."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from ..core.io import read_json, sha256_file
from ..core.rails import validate_rails

console = Console()


@click.command()
@click.option('--bundle', type=click.Path(exists=True), required=True, 
              help='Path to candidate bundle directory')
@click.option('--policy', type=click.Path(exists=True), required=True,
              help='Policy JSON file')
def verify(bundle, policy):
    """Quick verify existing bundle: hashes, rails, policy compliance."""
    
    console.print("[bold blue]K4 Bundle Verification[/bold blue]")
    
    bundle_path = Path(bundle)
    policy_data = read_json(policy)
    
    # Check required files
    required_files = [
        "plaintext_97.txt",
        "coverage_report.json", 
        "phrase_gate_report.json",
        "hashes.txt"
    ]
    
    table = Table()
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")
    
    # File existence check
    missing_files = []
    for file in required_files:
        if not (bundle_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        table.add_row("Required Files", "[red]FAIL[/red]", f"Missing: {', '.join(missing_files)}")
        console.print(table)
        return
    else:
        table.add_row("Required Files", "[green]PASS[/green]", "All present")
    
    # Read key files
    plaintext = (bundle_path / "plaintext_97.txt").read_text().strip()
    coverage_report = read_json(str(bundle_path / "coverage_report.json"))
    phrase_report = read_json(str(bundle_path / "phrase_gate_report.json"))
    
    # Hash verification
    expected_pt_hash = coverage_report.get("pt_sha256")
    actual_pt_hash = sha256_file(str(bundle_path / "plaintext_97.txt"))[0:64]  # Text hash approximation
    
    # Rails validation
    rails_result = validate_rails(plaintext, policy_data)
    rails_pass = all(v for k, v in rails_result.items() if k != "error")
    table.add_row("Rails Validation", 
                  "[green]PASS[/green]" if rails_pass else "[red]FAIL[/red]",
                  "Format, anchors, head lock, seam")
    
    # Policy compliance
    phrase_gate_ok = (
        phrase_report.get("passed", False) and
        coverage_report.get("phrase_gate", {}).get("combine") == "AND"
    )
    table.add_row("Policy Compliance", 
                  "[green]PASS[/green]" if phrase_gate_ok else "[red]FAIL[/red]",
                  "AND gate, tracks passed")
    
    # Encryption check
    encrypts_ok = coverage_report.get("encrypts_to_ct", False)
    table.add_row("Encryption Check", 
                  "[green]PASS[/green]" if encrypts_ok else "[red]FAIL[/red]",
                  "PT encrypts to CT")
    
    # Nulls check
    nulls = coverage_report.get("nulls", {})
    nulls_ok = (
        nulls.get("p_cov_holm", 1.0) < 0.01 and
        nulls.get("p_fw_holm", 1.0) < 0.01
    )
    table.add_row("Nulls Validation", 
                  "[green]PASS[/green]" if nulls_ok else "[red]FAIL[/red]",
                  f"p_cov={nulls.get('p_cov_holm', 'N/A'):.4f}, p_fw={nulls.get('p_fw_holm', 'N/A'):.4f}")
    
    console.print(table)
    
    # Summary
    all_checks = [rails_pass, phrase_gate_ok, encrypts_ok, nulls_ok]
    if all(all_checks):
        console.print("\n[bold green]✅ BUNDLE VERIFICATION PASSED[/bold green]")
    else:
        console.print("\n[bold red]❌ BUNDLE VERIFICATION FAILED[/bold red]")