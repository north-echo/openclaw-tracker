"""Streamlit dashboard for OpenClaw Tracker."""

from __future__ import annotations

import json
import os

import plotly.express as px
import pycountry
import streamlit as st

from openclaw_tracker.models import ScanResult
from openclaw_tracker.shodan_query import run_all_queries

st.set_page_config(page_title="OpenClaw Tracker", layout="wide")


def _alpha3(code: str) -> str | None:
    """Convert ISO alpha-2 country code to alpha-3 for Plotly choropleth."""
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except (AttributeError, LookupError):
        return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("OpenClaw Tracker")

api_key = st.sidebar.text_input(
    "Shodan API Key",
    value=os.environ.get("SHODAN_API_KEY", ""),
    type="password",
)

top_n = st.sidebar.number_input(
    "Top N countries",
    min_value=1,
    max_value=200,
    value=20,
)

run_clicked = st.sidebar.button("Run Query")

if run_clicked:
    if not api_key:
        st.sidebar.error("Please enter a Shodan API key.")
    else:
        with st.spinner("Querying Shodan..."):
            try:
                result = run_all_queries(
                    api_key=api_key,
                    top_countries=top_n,
                )
                st.session_state["scan_result"] = result
            except Exception as exc:
                st.sidebar.error(f"Query failed: {exc}")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

result: ScanResult | None = st.session_state.get("scan_result")

if result is None:
    st.title("OpenClaw Tracker Dashboard")
    st.info("Enter your Shodan API key in the sidebar and click **Run Query** to begin.")
    st.stop()

# --- Metric cards ---
st.title("OpenClaw Tracker Dashboard")

num_countries = len(result.countries)
num_cities = len(result.cities)
top_country = result.countries[0] if result.countries else None

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Instances", f"{result.total_instances:,}")
col2.metric("Countries", num_countries)
col3.metric("Cities", num_cities)
if top_country:
    col4.metric(
        "Top Country",
        top_country.country_name,
        f"{top_country.count:,} instances",
    )

# --- Build dataframe rows ---
rows = []
for c in result.countries:
    a3 = _alpha3(c.country_code)
    if a3:
        rows.append(
            {
                "country_code": c.country_code,
                "alpha_3": a3,
                "country_name": c.country_name,
                "count": c.count,
            }
        )

# --- Choropleth globe ---
if rows:
    st.subheader("World Map")
    fig_map = px.choropleth(
        rows,
        locations="alpha_3",
        color="count",
        hover_name="country_name",
        color_continuous_scale="Plasma",
        labels={"count": "Instances", "alpha_3": "ISO Code"},
    )
    fig_map.update_geos(
        projection_type="orthographic",
        showcoastlines=True,
        coastlinecolor="#555555",
        showland=True,
        landcolor="#1a1a2e",
        showocean=True,
        oceancolor="#0f0f1a",
        showlakes=False,
        showcountries=True,
        countrycolor="#333333",
        bgcolor="rgba(0,0,0,0)",
    )
    fig_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=dict(text="Instances", font=dict(color="#cccccc")),
            tickfont=dict(color="#cccccc"),
        ),
        dragmode="pan",
    )
    fig_map.update_traces(
        marker_line_color="#444444",
        marker_line_width=0.5,
    )
    st.plotly_chart(fig_map, use_container_width=True)

# --- Bar chart (top N) ---
if rows:
    st.subheader(f"Top {top_n} Countries")
    bar_rows = rows[:top_n]
    fig_bar = px.bar(
        bar_rows,
        x="count",
        y="country_name",
        orientation="h",
        color="count",
        color_continuous_scale="Blues",
        labels={"count": "Instances", "country_name": "Country"},
    )
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Top cities bar chart ---
if result.cities:
    st.subheader(f"Top {top_n} Cities")
    city_rows = [
        {"city": c.city, "count": c.count}
        for c in result.cities[:top_n]
    ]
    fig_city = px.bar(
        city_rows,
        x="count",
        y="city",
        orientation="h",
        color="count",
        color_continuous_scale="Blues",
        labels={"count": "Instances", "city": "City"},
    )
    fig_city.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_city, use_container_width=True)

# --- Per-query breakdown ---
if result.query_results:
    st.subheader("Per-Query Breakdown")
    for qr in result.query_results:
        with st.expander(f"{qr.query} — {qr.total:,} total"):
            if qr.countries:
                qr_rows = []
                for c in qr.countries:
                    qr_rows.append(
                        {"country_name": c.country_name, "count": c.count}
                    )
                fig_qr = px.bar(
                    qr_rows,
                    x="count",
                    y="country_name",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Blues",
                    labels={"count": "Instances", "country_name": "Country"},
                )
                fig_qr.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_qr, use_container_width=True)
            else:
                st.write("No country results for this query.")

            if qr.cities:
                st.markdown("**Top cities for this query:**")
                qr_city_rows = [
                    {"city": c.city, "count": c.count}
                    for c in qr.cities
                ]
                fig_qr_city = px.bar(
                    qr_city_rows,
                    x="count",
                    y="city",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Blues",
                    labels={"count": "Instances", "city": "City"},
                )
                fig_qr_city.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_qr_city, use_container_width=True)

# --- Data table ---
st.subheader("Country Data")
table_rows = [
    {
        "Country": c.country_name,
        "Code": c.country_code,
        "Instances": c.count,
    }
    for c in result.countries
]
st.dataframe(table_rows, use_container_width=True)

if result.cities:
    st.subheader("City Data")
    city_table_rows = [
        {"City": c.city, "Instances": c.count}
        for c in result.cities
    ]
    st.dataframe(city_table_rows, use_container_width=True)

# --- JSON download ---
st.subheader("Export")
st.download_button(
    label="Download results as JSON",
    data=json.dumps(result.to_dict(), indent=2),
    file_name="openclaw_scan.json",
    mime="application/json",
)
