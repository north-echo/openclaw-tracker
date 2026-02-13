"""Output formatting — Rich CLI tables and JSON export."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .models import QueryResult, ScanResult

console = Console()


def _bar(count: int, max_count: int, width: int = 30) -> str:
    """Render a simple text bar chart segment."""
    if max_count == 0:
        return ""
    filled = max(1, round(count / max_count * width))
    return "\u2588" * filled


def print_query_result(qr: QueryResult) -> None:
    """Print a single query result as a Rich table."""
    table = Table(title=f"Query: {qr.query}", title_style="bold cyan")
    table.add_column("Country", style="white")
    table.add_column("Code", style="dim")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Distribution", style="blue")

    max_count = qr.countries[0].count if qr.countries else 0
    for c in qr.countries:
        table.add_row(
            c.country_name,
            c.country_code,
            f"{c.count:,}",
            _bar(c.count, max_count),
        )

    console.print(table)
    console.print(f"  Total instances for this query: [bold]{qr.total:,}[/bold]\n")


def print_scan_result(result: ScanResult) -> None:
    """Print the full aggregated scan result."""
    console.print()
    console.rule("[bold]OpenClaw Instance Geographic Distribution[/bold]")
    console.print()

    # Per-query breakdown.
    for qr in result.query_results:
        print_query_result(qr)

    # Merged summary.
    if len(result.query_results) > 1:
        table = Table(title="Merged — All Queries", title_style="bold magenta")
        table.add_column("Country", style="white")
        table.add_column("Code", style="dim")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Distribution", style="blue")

        max_count = result.countries[0].count if result.countries else 0
        for c in result.countries:
            table.add_row(
                c.country_name,
                c.country_code,
                f"{c.count:,}",
                _bar(c.count, max_count),
            )

        console.print(table)

    console.print()
    console.print(
        f"[bold]Total instances across all queries:[/bold] {result.total_instances:,}"
    )
    console.print(
        f"[dim]Note: totals may include duplicates across queries.[/dim]"
    )
    console.print(f"[dim]Timestamp: {result.timestamp.isoformat()}[/dim]")
    console.print()


def write_json(result: ScanResult, path: str | Path) -> None:
    """Write scan results to a JSON file."""
    path = Path(path)
    path.write_text(json.dumps(result.to_dict(), indent=2))
    console.print(f"[green]Results written to {path}[/green]")
