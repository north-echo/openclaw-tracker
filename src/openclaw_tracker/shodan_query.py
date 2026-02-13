"""Query Shodan API for OpenClaw instance statistics."""

from __future__ import annotations

import shodan

from .models import CityCount, CountryCount, QueryResult, ScanResult

# Shodan search queries targeting OpenClaw and its predecessor names.
DEFAULT_QUERIES = [
    'title:"OpenClaw Control"',
    'title:"Moltbot Control"',
    'title:"Clawdbot Control"',
    "port:18789 openclaw",
]

# Map Shodan's two-letter codes to readable names (common ones).
_COUNTRY_NAMES: dict[str, str] = {
    "US": "United States",
    "GB": "United Kingdom",
    "DE": "Germany",
    "FR": "France",
    "ES": "Spain",
    "NL": "Netherlands",
    "CA": "Canada",
    "AU": "Australia",
    "JP": "Japan",
    "KR": "South Korea",
    "IN": "India",
    "BR": "Brazil",
    "CN": "China",
    "RU": "Russia",
    "IT": "Italy",
    "SE": "Sweden",
    "NO": "Norway",
    "FI": "Finland",
    "PL": "Poland",
    "SG": "Singapore",
    "HK": "Hong Kong",
    "TW": "Taiwan",
    "IE": "Ireland",
    "CH": "Switzerland",
    "AT": "Austria",
    "BE": "Belgium",
    "DK": "Denmark",
    "PT": "Portugal",
    "CZ": "Czech Republic",
    "RO": "Romania",
    "ZA": "South Africa",
    "MX": "Mexico",
    "AR": "Argentina",
    "CL": "Chile",
    "CO": "Colombia",
    "ID": "Indonesia",
    "TH": "Thailand",
    "VN": "Vietnam",
    "PH": "Philippines",
    "MY": "Malaysia",
    "NZ": "New Zealand",
    "UA": "Ukraine",
    "IL": "Israel",
    "AE": "United Arab Emirates",
    "SA": "Saudi Arabia",
    "TR": "Turkey",
    "EG": "Egypt",
    "NG": "Nigeria",
    "KE": "Kenya",
}


def _country_name(code: str) -> str:
    return _COUNTRY_NAMES.get(code, code)


def run_query(api: shodan.Shodan, query: str, top_n: int = 20) -> QueryResult:
    """Run a single Shodan count query with country and city facets."""
    result = api.count(query, facets=[("country", top_n), ("city", top_n)])

    countries = []
    for facet in result.get("facets", {}).get("country", []):
        countries.append(
            CountryCount(
                country_code=facet["value"],
                country_name=_country_name(facet["value"]),
                count=facet["count"],
            )
        )

    cities = []
    for facet in result.get("facets", {}).get("city", []):
        cities.append(
            CityCount(
                city=facet["value"],
                count=facet["count"],
            )
        )

    return QueryResult(
        query=query,
        total=result.get("total", 0),
        countries=countries,
        cities=cities,
    )


def run_all_queries(
    api_key: str,
    queries: list[str] | None = None,
    top_countries: int = 20,
) -> ScanResult:
    """Run all Shodan queries and merge results into a ScanResult."""
    api = shodan.Shodan(api_key)
    queries = queries or DEFAULT_QUERIES

    scan = ScanResult(queries_run=list(queries))
    merged_country_counts: dict[str, int] = {}
    merged_city_counts: dict[str, int] = {}

    for query in queries:
        qr = run_query(api, query, top_n=top_countries)
        scan.query_results.append(qr)
        scan.total_instances += qr.total

        for c in qr.countries:
            merged_country_counts[c.country_code] = (
                merged_country_counts.get(c.country_code, 0) + c.count
            )

        for c in qr.cities:
            merged_city_counts[c.city] = (
                merged_city_counts.get(c.city, 0) + c.count
            )

    # Build sorted merged country list.
    scan.countries = sorted(
        [
            CountryCount(
                country_code=code,
                country_name=_country_name(code),
                count=count,
            )
            for code, count in merged_country_counts.items()
        ],
        key=lambda c: c.count,
        reverse=True,
    )

    # Build sorted merged city list.
    scan.cities = sorted(
        [
            CityCount(city=city, count=count)
            for city, count in merged_city_counts.items()
        ],
        key=lambda c: c.count,
        reverse=True,
    )

    return scan
