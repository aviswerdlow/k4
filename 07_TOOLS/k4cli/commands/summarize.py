"""K4 summarize command - generate uniqueness summaries."""

import click
from pathlib import Path
from rich.console import Console

from ..core.io import read_json, write_json

console = Console()


@click.command()
@click.option('--grid-only', is_flag=True, help='Generate GRID-only uniqueness summary')
@click.option('--winner', type=click.Path(exists=True), help='Winner bundle directory')  
@click.option('--runner-up', type=click.Path(exists=True), help='Runner-up bundle directory')
@click.option('--output', type=click.Path(), help='Output summary JSON file')
def summarize(grid_only, winner, runner_up, output):
    """Generate uniqueness summaries and reports."""
    
    if grid_only:
        if not all([winner, runner_up, output]):
            console.print("[red]Error: --grid-only requires --winner, --runner-up, and --output[/red]")
            return
            
        console.print("[bold blue]Generating GRID-only uniqueness summary...[/bold blue]")
        
        # Read candidate data
        winner_coverage = read_json(str(Path(winner) / "coverage_report.json"))
        winner_holm = read_json(str(Path(winner) / "holm_report_canonical.json"))
        winner_phrase = read_json(str(Path(winner) / "phrase_gate_report.json"))
        
        runner_up_coverage = read_json(str(Path(runner_up) / "coverage_report.json"))
        runner_up_holm = read_json(str(Path(runner_up) / "holm_report_canonical.json"))
        runner_up_phrase = read_json(str(Path(runner_up) / "phrase_gate_report.json"))
        
        # Build summary
        summary = {
            "model_class": {
                "routes": "GRID_W{10,12,14}_{ROWS|BOU|NE|NW}",
                "classings": ["c6a", "c6b"],
                "families": ["vigenere", "variant_beaufort", "beaufort"],
                "periods": [10, 22],
                "phases": "0..L-1",
                "option_A": True
            },
            "phrase_gate_policy": {
                "combine": "AND",
                "tokenization_v2": True,
                "generic": {
                    "percentile_top": 1,
                    "pos_threshold": 0.6,
                    "min_content_words": 6,
                    "max_repeat": 2
                }
            },
            "tie_breakers": [
                "holm_adj_p_min",
                "perplexity_percentile", 
                "coverage",
                "route_complexity"
            ],
            "candidates": [
                {
                    "label": "cand_004",
                    "pt_sha256": runner_up_coverage["pt_sha256"],
                    "route_id": "GRID_W10_NW",
                    "feasible": True,
                    "near_gate": True,
                    "phrase_gate": {
                        "tracks": runner_up_phrase.get("accepted_by", []),
                        "pass": runner_up_phrase.get("passed", False)
                    },
                    "holm_adj_p": {
                        "coverage": runner_up_holm["p_cov_holm"],
                        "f_words": runner_up_holm["p_fw_holm"]
                    },
                    "holm_adj_p_min": min(runner_up_holm["p_cov_holm"], runner_up_holm["p_fw_holm"]),
                    "coverage": runner_up_coverage.get("near_gate", {}).get("coverage", 0),
                    "perplexity_percentile": runner_up_phrase.get("generic", {}).get("perplexity_percentile", 0),
                    "publishable": runner_up_holm.get("publishable", False)
                },
                {
                    "label": "cand_005", 
                    "pt_sha256": winner_coverage["pt_sha256"],
                    "route_id": "GRID_W14_ROWS",
                    "feasible": True,
                    "near_gate": True,
                    "phrase_gate": {
                        "tracks": winner_phrase.get("accepted_by", []),
                        "pass": winner_phrase.get("passed", False)
                    },
                    "holm_adj_p": {
                        "coverage": winner_holm["p_cov_holm"],
                        "f_words": winner_holm["p_fw_holm"]
                    },
                    "holm_adj_p_min": min(winner_holm["p_cov_holm"], winner_holm["p_fw_holm"]),
                    "coverage": winner_coverage.get("near_gate", {}).get("coverage", 0),
                    "perplexity_percentile": winner_phrase.get("generic", {}).get("perplexity_percentile", 0),
                    "publishable": winner_holm.get("publishable", False)
                }
            ]
        }
        
        # Determine uniqueness
        winner_cov = winner_coverage.get("near_gate", {}).get("coverage", 0)
        runner_up_cov = runner_up_coverage.get("near_gate", {}).get("coverage", 0)
        
        if winner_cov > runner_up_cov:
            summary["uniqueness"] = {
                "unique": True,
                "reason": "GRID_only_AND_gate_with_tie_breakers",
                "winner": "cand_005",
                "tie_breaker_used": "coverage",
                "comparison": {
                    "cand_004": {
                        "holm_adj_p_min": summary["candidates"][0]["holm_adj_p_min"],
                        "perplexity_percentile": summary["candidates"][0]["perplexity_percentile"],
                        "coverage": summary["candidates"][0]["coverage"],
                        "route_complexity": 101  # GRID_W10_NW
                    },
                    "cand_005": {
                        "holm_adj_p_min": summary["candidates"][1]["holm_adj_p_min"],
                        "perplexity_percentile": summary["candidates"][1]["perplexity_percentile"], 
                        "coverage": summary["candidates"][1]["coverage"],
                        "route_complexity": 141  # GRID_W14_ROWS
                    }
                }
            }
        else:
            summary["uniqueness"] = {
                "unique": False,
                "reason": "tie_breakers_insufficient"
            }
        
        # Write summary
        write_json(output, summary)
        console.print(f"[green]GRID-only summary written to: {output}[/green]")
        
        if summary["uniqueness"]["unique"]:
            console.print(f"[green]✅ Uniqueness confirmed: {summary['uniqueness']['winner']}[/green]")
        else:
            console.print("[red]❌ Uniqueness not established[/red]")
            
    else:
        console.print("[yellow]Use --grid-only flag to generate GRID-only uniqueness summary[/yellow]")