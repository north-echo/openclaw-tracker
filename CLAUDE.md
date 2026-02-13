# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

```bash
pip install -e ".[test]"                 # Install in editable mode with test deps
openclaw-tracker scan --shodan-key KEY   # Run CLI scan
openclaw-tracker dashboard               # Launch Streamlit dashboard (port 8501)
openclaw-tracker dashboard --open        # Launch dashboard and open browser
```

## Testing & Linting

```bash
pytest tests/                # Run all tests (19 tests across 3 files)
pylint src/                  # Lint source code (should score 10/10)
```

Tests cover models (`test_models.py`), Shodan query logic with mocked API (`test_shodan_query.py`), and reporter output (`test_reporter.py`). CI runs both pylint and pytest on Python 3.11, 3.12, and 3.13.

## Architecture

This is a Shodan-based tool that queries for geographic distribution of public OpenClaw instances. It has two interfaces sharing the same data layer:

- **CLI** (`cli.py`) — Click command group with `scan` and `dashboard` subcommands
- **Dashboard** (`dashboard.py`) — Streamlit app with Plotly visualizations (choropleth globe, bar charts, data tables)

Data flow: `shodan_query.run_all_queries()` → `ScanResult` (dataclass) → rendered by either `reporter.py` (CLI/Rich tables) or `dashboard.py` (Streamlit).

### Key constraint

`dashboard.py` is executed by Streamlit as a standalone script, not as a module. It must use **absolute imports** (`from openclaw_tracker.models import ...`), not relative imports. The `dashboard` CLI command injects `PYTHONPATH` to make this work.

## Dependencies

Requires Python 3.11+. Core deps: `shodan`, `rich`, `click`, `streamlit`, `plotly`, `pycountry`. Test dep: `pytest` (installed via `.[test]`).
