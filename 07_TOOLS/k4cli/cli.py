#!/usr/bin/env python3
"""K4 CLI - Command-line interface for K4 Kryptos validation."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .commands import confirm, verify, grid_unique, summarize

console = Console()


@click.group(help="K4 CLI - Kryptos K4 analysis and validation tools")
@click.version_option(version="1.0.0")
def cli():
    """K4 CLI main entry point."""
    pass


# Register commands
cli.add_command(confirm.confirm)
cli.add_command(verify.verify) 
cli.add_command(grid_unique.grid_unique)
cli.add_command(summarize.summarize)


def main():
    """Main entry point for console script."""
    cli()


if __name__ == "__main__":
    main()