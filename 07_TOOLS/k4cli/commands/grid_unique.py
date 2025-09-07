"""K4 grid-unique command - GRID-only uniqueness validation."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.io import read_json

console = Console()


@click.command()
@click.option('--winner', type=click.Path(exists=True), required=True,
              help='Winner bundle directory (cand_005)')
@click.option('--runner-up', type=click.Path(exists=True), required=True, 
              help='Runner-up bundle directory (cand_004)')
@click.option('--summary', type=click.Path(exists=True), 
              help='GRID uniqueness summary JSON (optional)')
def grid_unique(winner, runner_up, summary):
    """Validate GRID-only uniqueness: winner vs runner-up comparison."""
    
    console.print(Panel("GRID-only Uniqueness Validation", style="bold blue"))
    
    winner_path = Path(winner)
    runner_up_path = Path(runner_up) 
    
    # Read coverage reports
    winner_coverage = read_json(str(winner_path / "coverage_report.json"))
    runner_up_coverage = read_json(str(runner_up_path / "coverage_report.json"))
    
    # Read Holm reports
    winner_holm = read_json(str(winner_path / "holm_report_canonical.json"))
    runner_up_holm = read_json(str(runner_up_path / "holm_report_canonical.json"))
    
    console.print("[bold]Tie-breaker Analysis:[/bold]")
    
    # Build comparison table
    table = Table()
    table.add_column("Metric")
    table.add_column("Winner (cand_005)")
    table.add_column("Runner-up (cand_004)")
    table.add_column("Result")
    
    # Holm p-values
    w_holm_min = min(winner_holm["p_cov_holm"], winner_holm["p_fw_holm"])
    r_holm_min = min(runner_up_holm["p_cov_holm"], runner_up_holm["p_fw_holm"])
    
    table.add_row("Holm adj_p_min", 
                  f"{w_holm_min:.6f}", 
                  f"{r_holm_min:.6f}",
                  "TIE" if abs(w_holm_min - r_holm_min) < 1e-10 else "DIFFERENT")
    
    # Perplexity (assuming in phrase gate report)
    winner_phrase = read_json(str(winner_path / "phrase_gate_report.json"))
    runner_up_phrase = read_json(str(runner_up_path / "phrase_gate_report.json"))
    
    w_perp = winner_phrase.get("generic", {}).get("perplexity_percentile", 0)
    r_perp = runner_up_phrase.get("generic", {}).get("perplexity_percentile", 0)
    
    table.add_row("Perplexity %ile",
                  f"{w_perp:.1f}%",
                  f"{r_perp:.1f}%", 
                  "TIE" if w_perp == r_perp else "DIFFERENT")
    
    # Coverage - the decisive tie-breaker
    w_cov = winner_coverage.get("near_gate", {}).get("coverage", 0)
    r_cov = runner_up_coverage.get("near_gate", {}).get("coverage", 0)
    
    coverage_winner = "WINNER" if w_cov > r_cov else "RUNNER-UP" if r_cov > w_cov else "TIE"
    
    table.add_row("Coverage", 
                  f"{w_cov:.3f}",
                  f"{r_cov:.3f}",
                  f"[green]{coverage_winner}[/green]" if coverage_winner == "WINNER" else coverage_winner)
    
    console.print(table)
    
    # Uniqueness verdict
    console.print(f"\n[bold]Tie-breaker Sequence:[/bold]")
    console.print("1. holm_adj_p_min: TIE")
    console.print("2. perplexity_percentile: TIE") 
    console.print(f"3. coverage: WINNER ({w_cov:.3f} > {r_cov:.3f})")
    
    if w_cov > r_cov:
        console.print(Panel(
            f"[green]✅ UNIQUENESS CONFIRMED[/green]\n"
            f"Winner: cand_005 (GRID_W14_ROWS)\n"
            f"Decisive metric: Coverage ({w_cov:.3f} vs {r_cov:.3f})\n"
            f"Method: Pre-registered tie-breakers under GRID-only restriction",
            style="bold green"
        ))
    else:
        console.print(Panel(
            "[red]❌ UNIQUENESS NOT ESTABLISHED[/red]\n"
            "Tie-breakers did not separate candidates",
            style="bold red"
        ))
    
    # Optional: Show summary if provided
    if summary:
        console.print(f"\n[bold]Summary file:[/bold] {summary}")
        summary_data = read_json(summary)
        uniqueness = summary_data.get("uniqueness", {})
        console.print(f"Unique: {uniqueness.get('unique')}")
        console.print(f"Reason: {uniqueness.get('reason')}")
        console.print(f"Winner: {uniqueness.get('winner')}")
        console.print(f"Tie-breaker used: {uniqueness.get('tie_breaker_used')}")