"""CLI entry point for openclaw-tracker."""

from __future__ import annotations

import os
import sys

import click
from rich.console import Console

from .reporter import print_scan_result, write_json
from .shodan_query import DEFAULT_QUERIES, run_all_queries

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """OpenClaw Tracker — geographic distribution of public OpenClaw instances."""


@main.command()
@click.option(
    "--shodan-key",
    envvar="SHODAN_API_KEY",
    default=None,
    help="Shodan API key (or set SHODAN_API_KEY env var).",
)
@click.option(
    "--top",
    default=20,
    show_default=True,
    help="Number of top countries to display per query.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(),
    help="Write results to a JSON file.",
)
@click.option(
    "--query",
    "-q",
    multiple=True,
    help="Custom Shodan query (repeatable). Overrides defaults if provided.",
)
def scan(
    shodan_key: str | None,
    top: int,
    output: str | None,
    query: tuple[str, ...],
) -> None:
    """Query Shodan for geographic distribution of OpenClaw instances."""
    if not shodan_key:
        console.print(
            "[red]Error:[/red] No Shodan API key provided.\n"
            "Set SHODAN_API_KEY or pass --shodan-key."
        )
        sys.exit(1)

    queries = list(query) if query else None

    console.print("[dim]Querying Shodan...[/dim]")
    try:
        result = run_all_queries(
            api_key=shodan_key,
            queries=queries,
            top_countries=top,
        )
    except Exception as exc:
        console.print(f"[red]Shodan query failed:[/red] {exc}")
        sys.exit(1)

    print_scan_result(result)

    if output:
        write_json(result, output)


@main.command()
@click.option("--port", default=8501, show_default=True, help="Port for the Streamlit server.")
def dashboard(port: int) -> None:
    """Launch the interactive Streamlit dashboard."""
    import subprocess
    from pathlib import Path

    dashboard_path = Path(__file__).parent / "dashboard.py"
    src_dir = str(Path(__file__).parent.parent)
    env = {**os.environ, "PYTHONPATH": src_dir + os.pathsep + os.environ.get("PYTHONPATH", "")}
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(dashboard_path),
         "--server.port", str(port)],
        env=env,
    )


if __name__ == "__main__":
    main()
