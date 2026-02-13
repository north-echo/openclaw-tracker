# OpenClaw Tracker

Shodan-based tool for querying the geographic distribution of public OpenClaw instances. Provides both a CLI with Rich tables and an interactive Streamlit dashboard with maps and charts.

## Installation

```bash
pip install -e .
```

Requires Python 3.11+.

## Usage

### CLI

```bash
# Run a scan (prints Rich tables to terminal)
openclaw-tracker scan --shodan-key YOUR_KEY

# Limit to top 10 countries per query
openclaw-tracker scan --shodan-key YOUR_KEY --top 10

# Export results to JSON
openclaw-tracker scan --shodan-key YOUR_KEY -o results.json

# Use custom Shodan queries instead of defaults
openclaw-tracker scan --shodan-key YOUR_KEY -q 'title:"OpenClaw Control"' -q 'port:18789 openclaw'
```

You can also set the `SHODAN_API_KEY` environment variable instead of passing `--shodan-key` each time:

```bash
export SHODAN_API_KEY=YOUR_KEY
openclaw-tracker scan
```

### Dashboard

Launch the interactive Streamlit dashboard:

```bash
openclaw-tracker dashboard
```

By default the dashboard runs on port 8501. Use `--port` to change it:

```bash
openclaw-tracker dashboard --port 8080
```

The dashboard includes:

- **Metric cards** — total instances, country count, city count, top country
- **Choropleth world map** — countries colored by instance count
- **Bar charts** — top N countries and cities by instance count
- **Per-query breakdown** — expandable sections with individual charts
- **Sortable data tables** — country and city level
- **JSON export** — download button for full results

## Default Shodan Queries

The tool searches for OpenClaw and its predecessor products:

| Query | Target |
|-------|--------|
| `title:"OpenClaw Control"` | Current product |
| `title:"Moltbot Control"` | Previous name |
| `title:"Clawdbot Control"` | Previous name |
| `port:18789 openclaw` | Default port |

Override these with the `-q` flag on the CLI, or rely on the defaults.

## Dependencies

| Package | Purpose |
|---------|---------|
| `shodan` | Shodan API client |
| `rich` | CLI table formatting |
| `click` | CLI framework |
| `streamlit` | Dashboard web app |
| `plotly` | Choropleth map and bar charts |
| `pycountry` | ISO country code conversion |
