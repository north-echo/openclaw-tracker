"""Tests for Shodan query helpers with mocked API."""

from unittest.mock import MagicMock

from openclaw_tracker.shodan_query import _country_name, run_all_queries, run_query


class TestCountryName:
    def test_known_code(self):
        assert _country_name("US") == "United States"
        assert _country_name("DE") == "Germany"

    def test_unknown_code_returns_code(self):
        assert _country_name("ZZ") == "ZZ"
        assert _country_name("XX") == "XX"


class TestRunQuery:
    def test_parses_facets(self):
        api = MagicMock()
        api.count.return_value = {
            "total": 25,
            "facets": {
                "country": [
                    {"value": "US", "count": 15},
                    {"value": "DE", "count": 10},
                ],
                "city": [
                    {"value": "New York", "count": 8},
                ],
            },
        }

        qr = run_query(api, "test query", top_n=5)

        api.count.assert_called_once_with(
            "test query", facets=[("country", 5), ("city", 5)]
        )
        assert qr.query == "test query"
        assert qr.total == 25
        assert len(qr.countries) == 2
        assert qr.countries[0].country_code == "US"
        assert qr.countries[0].country_name == "United States"
        assert qr.countries[0].count == 15
        assert qr.countries[1].country_code == "DE"
        assert len(qr.cities) == 1
        assert qr.cities[0].city == "New York"
        assert qr.cities[0].count == 8

    def test_empty_facets(self):
        api = MagicMock()
        api.count.return_value = {"total": 0, "facets": {}}

        qr = run_query(api, "empty", top_n=10)

        assert qr.total == 0
        assert qr.countries == []
        assert qr.cities == []


class TestRunAllQueries:
    def test_merges_results(self):
        call_count = 0

        def mock_count(query, facets=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "total": 10,
                    "facets": {
                        "country": [{"value": "US", "count": 10}],
                        "city": [{"value": "NYC", "count": 6}],
                    },
                }
            return {
                "total": 5,
                "facets": {
                    "country": [
                        {"value": "US", "count": 3},
                        {"value": "DE", "count": 2},
                    ],
                    "city": [{"value": "NYC", "count": 2}],
                },
            }

        import shodan as shodan_mod
        original_shodan = shodan_mod.Shodan

        try:
            mock_api = MagicMock()
            mock_api.count.side_effect = mock_count
            shodan_mod.Shodan = MagicMock(return_value=mock_api)

            result = run_all_queries(
                api_key="fake-key",
                queries=["q1", "q2"],
                top_countries=10,
            )

            assert result.total_instances == 15
            assert result.queries_run == ["q1", "q2"]
            assert len(result.query_results) == 2

            # Merged country counts: US=13, DE=2
            us = next(c for c in result.countries if c.country_code == "US")
            de = next(c for c in result.countries if c.country_code == "DE")
            assert us.count == 13
            assert de.count == 2

            # Merged city counts: NYC=8
            nyc = next(c for c in result.cities if c.city == "NYC")
            assert nyc.count == 8

            # Countries sorted descending
            assert result.countries[0].count >= result.countries[-1].count
        finally:
            shodan_mod.Shodan = original_shodan
