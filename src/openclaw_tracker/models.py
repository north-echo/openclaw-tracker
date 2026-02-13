"""Data models for OpenClaw geographic distribution results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class CountryCount:
    """Instance count for a single country."""

    country_code: str
    country_name: str
    count: int


@dataclass
class CityCount:
    """Instance count for a single city."""

    city: str
    count: int


@dataclass
class QueryResult:
    """Result of a single Shodan query (one search term)."""

    query: str
    total: int
    countries: list[CountryCount] = field(default_factory=list)
    cities: list[CityCount] = field(default_factory=list)


@dataclass
class ScanResult:
    """Aggregated results across all Shodan queries."""

    queries_run: list[str] = field(default_factory=list)
    total_instances: int = 0
    countries: list[CountryCount] = field(default_factory=list)
    cities: list[CityCount] = field(default_factory=list)
    query_results: list[QueryResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_instances": self.total_instances,
            "queries_run": self.queries_run,
            "countries": [
                {
                    "country_code": c.country_code,
                    "country_name": c.country_name,
                    "count": c.count,
                }
                for c in self.countries
            ],
            "cities": [
                {"city": c.city, "count": c.count}
                for c in self.cities
            ],
            "per_query": [
                {
                    "query": qr.query,
                    "total": qr.total,
                    "countries": [
                        {
                            "country_code": c.country_code,
                            "country_name": c.country_name,
                            "count": c.count,
                        }
                        for c in qr.countries
                    ],
                    "cities": [
                        {"city": c.city, "count": c.count}
                        for c in qr.cities
                    ],
                }
                for qr in self.query_results
            ],
        }
