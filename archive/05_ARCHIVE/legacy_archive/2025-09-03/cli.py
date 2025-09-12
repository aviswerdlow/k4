import json
import csv
import hashlib
import zipfile
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table

from k4audit.validators import (
    assert_upper_97, assert_anchors, assert_head_lock, assert_seam_guard
)
from k4audit.io_utils import read_text, write_text, read_json, sha256_path, list_files_recursive

console = Console()

@click.group(help="K4 Audit CLI — rails verification, readable renders, and audit bundling.")
def cli():
    pass

@cli.command(help="Verify rails: anchors, head lock, seam guard, and plaintext formatting.")
@click.option("--pt", type=click.Path(exists=True), required=True, help="Plaintext 97 letters file.")
@click.option("--ct", type=click.Path(exists=True), required=True, help="Ciphertext 97 letters file.")
@click.option("--anchors", type=click.Path(exists=True), required=True, help="anchors_ledger.csv")
@click.option("--seam", type=click.Path(exists=True), required=True, help="seam_guard_proof.json")
@click.option("--expect-p74", default=None, help="Optional expected char at index 74 (e.g., T).")
def verify(pt, ct, anchors, seam, expect_p74):
    pt_s = read_text(pt).strip()
    ct_s = read_text(ct).strip()
    table = Table(title="Rails Verification")
    table.add_column("Check")
    table.add_column("Result")

    try:
        assert_upper_97(pt_s)
        table.add_row("PT format (97 A..Z)", "[green]OK[/green]")
    except AssertionError as e:
        table.add_row("PT format (97 A..Z)", f"[red]{e}[/red]")

    if expect_p74:
        got = pt_s[74]
        if got == expect_p74:
            table.add_row(f"P[74] == '{expect_p74}'", "[green]OK[/green]")
        else:
            table.add_row(f"P[74] == '{expect_p74}'", f"[red]Got '{got}'[/red]")

    try:
        assert_anchors(pt_s, anchors)
        table.add_row("Anchors at exact indices", "[green]OK[/green]")
    except AssertionError as e:
        table.add_row("Anchors", f"[red]{e}[/red]")

    try:
        assert_head_lock(pt_s)
        table.add_row("Head lock [0,74] sanity", "[green]OK[/green]")
    except AssertionError as e:
        table.add_row("Head lock", f"[red]{e}[/red]")

    try:
        assert_seam_guard(pt_s, seam)
        table.add_row("Tail guard & dotted seam", "[green]OK[/green]")
    except AssertionError as e:
        table.add_row("Tail guard", f"[red]{e}[/red]")

    table.add_row("PT sha256", sha256_path(Path(pt)))
    table.add_row("CT sha256", sha256_path(Path(ct)))
    console.print(table)

@cli.command(help="Render a spaced line from a ledger of inclusive 0-idx end-cuts.")
@click.option("--pt", type=click.Path(exists=True), required=True)
@click.option("--ledger", type=click.Path(exists=True), required=True)
@click.option("--out", type=click.Path(), default="-", help="Output file or '-' for stdout.")
def render(pt, ledger, out):
    pt_s = read_text(pt).strip()
    cuts = read_json(ledger)["cuts"]
    last = -1
    tokens = []
    for end in cuts:
        tokens.append(pt_s[last+1:end+1])
        last = end
    if last < len(pt_s) - 1:
        tokens.append(pt_s[last+1:])
    spaced = " ".join(tokens)
    if out == "-":
        console.print(spaced)
    else:
        write_text(out, spaced)
        console.print(f"[green]Wrote[/green] {out}")

@cli.command(help="Bundle files (with hashes) into an audit zip.")
@click.option("--pt", type=click.Path(exists=True), required=True)
@click.option("--ct", type=click.Path(exists=True), required=True)
@click.option("--proof", type=click.Path(exists=True), required=True)
@click.option("--anchors", type=click.Path(exists=True), required=True)
@click.option("--seam", type=click.Path(exists=True), required=True)
@click.option("--near", type=click.Path(exists=False), required=False)
@click.option("--phrase", type=click.Path(exists=False), required=False)
@click.option("--holm", type=click.Path(exists=False), required=False)
@click.option("--out", type=click.Path(), required=True, help="Output directory for the bundle.")
def bundle(pt, ct, proof, anchors, seam, near, phrase, holm, out):
    outdir = Path(out)
    outdir.mkdir(parents=True, exist_ok=True)
    artifacts = [Path(pt), Path(ct), Path(proof), Path(anchors), Path(seam)]
    if near: artifacts.append(Path(near))
    if phrase: artifacts.append(Path(phrase))
    if holm: artifacts.append(Path(holm))

    hashes_lines = []
    for p in artifacts:
        dst = outdir / p.name
        dst.write_bytes(Path(p).read_bytes())
        hashes_lines.append(f"{sha256_path(dst)}  {dst.name}")
    (outdir / "hashes.txt").write_text("\n".join(hashes_lines) + "\n")

    coverage = {
        "pt_sha256": sha256_path(Path(pt)),
        "ct_sha256": sha256_path(Path(ct)),
        "proof_sha256": sha256_path(Path(proof)),
        "anchors_file": Path(anchors).name,
        "seam_file": Path(seam).name,
        "near_gate_file": Path(near).name if near else None,
        "phrase_gate_file": Path(phrase).name if phrase else None,
        "holm_file": Path(holm).name if holm else None
    }
    (outdir / "coverage_report.json").write_text(json.dumps(coverage, indent=2) + "\n")

    zip_path = outdir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in list_files_recursive(outdir):
            z.write(f, arcname=f.relative_to(outdir))
    console.print(f"[green]Bundled[/green] → {zip_path}")

@cli.group(help="Calibration utilities (perplexity cutoff & POS threshold).")
def calib():
    pass

@calib.command("show", help="Print top-5% perplexity cutoff and POS threshold T.")
@click.option("--perp", type=click.Path(exists=True), required=True, help="calib_97_perplexity.json")
@click.option("--pos", type=click.Path(exists=True), required=True, help="pos_trigrams.json (unused here; for parity)")
@click.option("--th", type=click.Path(exists=True), required=True, help="pos_threshold.txt")
def calib_show(perp, pos, th):
    perp_json = read_json(perp)
    # Expect a field holding the top-5% cutoff; fall back to a conventional key name.
    top5 = perp_json.get("top_5_percentile_cutoff") or perp_json.get("top5_cutoff") or perp_json.get("percentile_top_5")
    T = read_text(th).strip()
    table = Table(title="Phrase-gate Calibration Pins")
    table.add_column("Parameter")
    table.add_column("Value")
    table.add_row("Perplexity top-5% cutoff", str(top5) if top5 is not None else "[red]missing in JSON[/red]")
    table.add_row("POS trigram threshold T", T)
    table.add_row("Perplexity file sha256", sha256_path(Path(perp)))
    table.add_row("POS trigrams file sha256", sha256_path(Path(pos)))
    table.add_row("POS threshold file sha256", sha256_path(Path(th)))
    console.print(table)

if __name__ == "__main__":
    cli()