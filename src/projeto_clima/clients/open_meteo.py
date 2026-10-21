"""Cliente HTTP simples para as condições atuais da Forecast API."""

import json
import logging
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from projeto_clima.storage.locations import Location

LOGGER = logging.getLogger(__name__)
BASE_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


class OpenMeteoError(RuntimeError):
    """Falha consultando ou interpretando a API Open-Meteo."""


def fetch_current(locations: list[Location], timeout: float = 15) -> list[dict]:
    """Consulta as localidades em lote e normaliza resposta única/lista para lista."""
    if not locations:
        raise ValueError("Informe ao menos uma localidade.")
    params = urlencode(
        {
            "latitude": ",".join(str(item.latitude) for item in locations),
            "longitude": ",".join(str(item.longitude) for item in locations),
            "current": "temperature_2m",
            "temperature_unit": "celsius",
            "timezone": "auto",
        }
    )
    return _request_records(BASE_URL, params, locations, timeout)


def fetch_daily_max_for_date(
    locations: list[Location], selected_date: date, historical: bool, timeout: float = 15
) -> list[dict]:
    """Busca a máxima diária do ar a 2 m no forecast ou arquivo histórico."""
    if not locations:
        raise ValueError("Informe ao menos uma localidade.")
    endpoint = ARCHIVE_URL if historical else BASE_URL
    params = urlencode(
        {
            "latitude": ",".join(str(item.latitude) for item in locations),
            "longitude": ",".join(str(item.longitude) for item in locations),
            "daily": "temperature_2m_max",
            "temperature_unit": "celsius",
            "timezone": "auto",
            "start_date": selected_date.isoformat(),
            "end_date": selected_date.isoformat(),
        }
    )
    return _request_records(endpoint, params, locations, timeout)


def _request_records(
    endpoint: str, params: str, locations: list[Location], timeout: float
) -> list[dict]:
    LOGGER.info("Consultando %s para %d localidades", endpoint, len(locations))
    try:
        with urlopen(f"{endpoint}?{params}", timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise OpenMeteoError(f"A API respondeu HTTP {exc.code}.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise OpenMeteoError(f"Falha de rede ou timeout ao consultar a API: {exc}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OpenMeteoError("A API retornou JSON inválido.") from exc
    records = payload if isinstance(payload, list) else [payload]
    if len(records) != len(locations) or any(not isinstance(item, dict) for item in records):
        raise OpenMeteoError("A estrutura da resposta não corresponde às localidades solicitadas.")
    return records
