"""Tests for data models."""

from datetime import datetime, timezone

from openclaw_tracker.models import CityCount, CountryCount, QueryResult, ScanResult


class TestCountryCount:
    def test_construction(self):
        cc = CountryCount(country_code="US", country_name="United States", count=42)
        assert cc.country_code == "US"
        assert cc.country_name == "United States"
        assert cc.count == 42


class TestCityCount:
    def test_construction(self):
        cc = CityCount(city="Berlin", count=7)
        assert cc.city == "Berlin"
        assert cc.count == 7


class TestQueryResult:
    def test_construction_defaults(self):
        qr = QueryResult(query="test query", total=10)
        assert qr.query == "test query"
        assert qr.total == 10
        assert qr.countries == []
        assert qr.cities == []

    def test_construction_with_data(self):
        countries = [CountryCount("DE", "Germany", 5)]
        cities = [CityCount("Berlin", 3)]
        qr = QueryResult(query="q", total=5, countries=countries, cities=cities)
        assert len(qr.countries) == 1
        assert len(qr.cities) == 1


class TestScanResult:
    def test_construction_defaults(self):
        sr = ScanResult()
        assert sr.queries_run == []
        assert sr.total_instances == 0
        assert sr.countries == []
        assert sr.cities == []
        assert sr.query_results == []
        assert isinstance(sr.timestamp, datetime)

    def test_to_dict_structure(self):
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        sr = ScanResult(
            queries_run=["q1"],
            total_instances=10,
            countries=[CountryCount("US", "United States", 7)],
            cities=[CityCount("NYC", 5)],
            query_results=[
                QueryResult(
                    query="q1",
                    total=10,
                    countries=[CountryCount("US", "United States", 7)],
                    cities=[CityCount("NYC", 5)],
                ),
            ],
            timestamp=ts,
        )
        d = sr.to_dict()

        assert d["timestamp"] == "2025-01-15T12:00:00+00:00"
        assert d["total_instances"] == 10
        assert d["queries_run"] == ["q1"]
        assert len(d["countries"]) == 1
        assert d["countries"][0] == {
            "country_code": "US",
            "country_name": "United States",
            "count": 7,
        }
        assert len(d["cities"]) == 1
        assert d["cities"][0] == {"city": "NYC", "count": 5}
        assert len(d["per_query"]) == 1
        assert d["per_query"][0]["query"] == "q1"
        assert d["per_query"][0]["total"] == 10

    def test_to_dict_empty(self):
        sr = ScanResult()
        d = sr.to_dict()
        assert d["total_instances"] == 0
        assert d["countries"] == []
        assert d["cities"] == []
        assert d["per_query"] == []
        assert "timestamp" in d
