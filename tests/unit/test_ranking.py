from datetime import date

import pytest

from projeto_clima.services.ranking import daily_max_snapshot, rank_locations
from projeto_clima.storage.locations import Location


def test_rank_orders_and_breaks_ties_by_name():
    locations = [Location(name, 0, index) for index, name in enumerate(["Z", "B", "A"])]
    records = [
        {
            "current": {"temperature_2m": value, "time": "2026-01-01T12:00"},
            "current_units": {"temperature_2m": "°C"},
            "timezone": "UTC",
            "utc_offset_seconds": 0,
        }
        for value in [20, 25, 25]
    ]
    top, all_results, _ = rank_locations(locations, records)
    assert [item.name for item in top] == ["A", "B", "Z"]
    assert all_results[0].requested_longitude == 0


def test_invalid_values_are_excluded_and_timestamp_spread_warned():
    locations = [Location("A", 0, 0), Location("B", 0, 1)]
    records = [
        {
            "current": {"temperature_2m": None, "time": "2026-01-01T12:00"},
            "timezone": "UTC",
            "utc_offset_seconds": 0,
        },
        {
            "current": {"temperature_2m": 1, "time": "2026-01-01T14:00"},
            "timezone": "UTC",
            "utc_offset_seconds": 0,
        },
    ]
    top, results, warnings = rank_locations(locations, records)
    assert len(top) == 1 and results[0].temperature is None
    assert any("divergem" in warning for warning in warnings)
    assert any("ignorada" in warning for warning in warnings)


def test_rejects_response_count_mismatch():
    with pytest.raises(ValueError, match="Quantidade"):
        rank_locations([Location("A", 0, 0)], [])


def test_daily_max_snapshot_selects_requested_local_date():
    records = [
        {
            "daily": {"time": ["2025-04-03"], "temperature_2m_max": [23.0]},
            "daily_units": {"temperature_2m_max": "°C"},
            "utc_offset_seconds": -10800,
            "timezone": "America/Sao_Paulo",
        }
    ]
    snapshot = daily_max_snapshot(records, date(2025, 4, 3))[0]
    assert snapshot["current"] == {
        "time": "2025-04-03",
        "temperature_2m": 23.0,
    }
    assert snapshot["current_units"]["temperature_2m"] == "°C"
    assert "utc_offset_seconds" not in snapshot


def test_daily_max_snapshot_marks_missing_date_as_missing():
    records = [{"daily": {"time": [], "temperature_2m_max": []}}]
    snapshot = daily_max_snapshot(records, date(2025, 4, 3))[0]
    assert snapshot["current"]["time"] is None
    assert snapshot["current"]["temperature_2m"] is None
