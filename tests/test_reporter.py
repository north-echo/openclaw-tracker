"""Tests for reporter module."""

import json
from datetime import datetime, timezone
from pathlib import Path

from openclaw_tracker.models import CityCount, CountryCount, ScanResult
from openclaw_tracker.reporter import _bar, write_json


class TestBar:
    def test_full_bar(self):
        result = _bar(100, 100, width=10)
        assert result == "\u2588" * 10

    def test_half_bar(self):
        result = _bar(50, 100, width=10)
        assert result == "\u2588" * 5

    def test_minimum_one_block(self):
        result = _bar(1, 1000, width=10)
        assert result == "\u2588"

    def test_zero_max_returns_empty(self):
        result = _bar(0, 0, width=10)
        assert result == ""

    def test_default_width(self):
        result = _bar(100, 100)
        assert len(result) == 30


class TestWriteJson:
    def test_writes_valid_json(self, tmp_path: Path):
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        sr = ScanResult(
            queries_run=["q1"],
            total_instances=5,
            countries=[CountryCount("US", "United States", 5)],
            cities=[CityCount("NYC", 3)],
            timestamp=ts,
        )

        out = tmp_path / "result.json"
        write_json(sr, out)

        assert out.exists()
        data = json.loads(out.read_text())
        assert data["total_instances"] == 5
        assert data["timestamp"] == "2025-01-15T12:00:00+00:00"
        assert len(data["countries"]) == 1
        assert data["countries"][0]["country_code"] == "US"

    def test_writes_empty_result(self, tmp_path: Path):
        sr = ScanResult()
        out = tmp_path / "empty.json"
        write_json(sr, out)

        data = json.loads(out.read_text())
        assert data["total_instances"] == 0
        assert data["countries"] == []
