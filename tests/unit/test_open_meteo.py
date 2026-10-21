import json
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse

import pytest

from projeto_clima.clients import open_meteo
from projeto_clima.clients.open_meteo import OpenMeteoError
from projeto_clima.storage.locations import Location


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return json.dumps(self.payload).encode()


def test_fetch_builds_expected_query_and_normalizes_object(monkeypatch):
    seen = {}

    def fake_open(url, timeout):
        seen.update(url=url, timeout=timeout)
        return Response({"current": {"temperature_2m": 20}})

    monkeypatch.setattr(open_meteo, "urlopen", fake_open)
    records = open_meteo.fetch_current([Location("A", 1, 2)])
    assert len(records) == 1
    assert "temperature_unit=celsius" in seen["url"]
    assert "timezone=auto" in seen["url"]
    assert seen["timeout"] == 15


@pytest.mark.parametrize(
    "failure",
    [
        HTTPError("url", 503, "down", {}, None),
        URLError("offline"),
        TimeoutError("timeout"),
    ],
)
def test_network_errors_are_actionable(monkeypatch, failure):
    def fail_request(*_args, **_kwargs):
        raise failure

    monkeypatch.setattr(open_meteo, "urlopen", fail_request)
    with pytest.raises(OpenMeteoError):
        open_meteo.fetch_current([Location("A", 1, 2)])


def test_rejects_malformed_json_and_count(monkeypatch):
    monkeypatch.setattr(open_meteo, "urlopen", lambda *_a, **_k: Response([{}]))
    with pytest.raises(OpenMeteoError, match="não corresponde"):
        open_meteo.fetch_current([Location("A", 1, 2), Location("B", 3, 4)])

    class Bad(Response):
        def read(self):
            return b"{"

    monkeypatch.setattr(open_meteo, "urlopen", lambda *_a, **_k: Bad(None))
    with pytest.raises(OpenMeteoError, match="JSON inválido"):
        open_meteo.fetch_current([Location("A", 1, 2)])


@pytest.mark.parametrize(
    ("historical", "expected_url"),
    [
        (False, open_meteo.BASE_URL),
        (True, open_meteo.ARCHIVE_URL),
    ],
)
def test_fetch_daily_max_for_date_selects_endpoint_and_date(monkeypatch, historical, expected_url):
    seen = {}

    def fake_open(url, timeout):
        seen["url"] = url
        return Response({"daily": {"time": [], "temperature_2m_max": []}})

    monkeypatch.setattr(open_meteo, "urlopen", fake_open)
    records = open_meteo.fetch_daily_max_for_date(
        [Location("A", 1, 2)], date(2025, 4, 3), historical
    )

    query = parse_qs(urlparse(seen["url"]).query)
    assert (
        urlparse(seen["url"]).scheme
        + "://"
        + urlparse(seen["url"]).netloc
        + urlparse(seen["url"]).path
        == expected_url
    )
    assert query["daily"] == ["temperature_2m_max"]
    assert query["start_date"] == query["end_date"] == ["2025-04-03"]
    assert query["timezone"] == ["auto"]
    assert records[0]["daily"]["time"] == []
