"""Carregamento e validação do catálogo CSV de localidades."""

import csv
from dataclasses import dataclass
from pathlib import Path


class CatalogError(ValueError):
    """Erro de formato ou conteúdo no catálogo de localidades."""


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    country: str | None = None
    state: str | None = None


def load_locations(path: str | Path) -> list[Location]:
    """Lê um CSV UTF-8 e valida nomes e coordenadas WGS84."""
    catalog_path = Path(path).expanduser()
    try:
        with catalog_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {"name", "latitude", "longitude"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise CatalogError("O CSV precisa das colunas name, latitude e longitude.")
            locations: list[Location] = []
            names: set[tuple[str, str, str]] = set()
            for row_number, row in enumerate(reader, start=2):
                name = (row.get("name") or "").strip()
                if not name:
                    raise CatalogError(f"Linha {row_number}: nome da localidade vazio.")
                country = (row.get("country") or "").strip() or None
                state = (row.get("state") or "").strip() or None
                identity = (
                    name.casefold(),
                    (country or "").casefold(),
                    (state or "").casefold(),
                )
                if identity in names:
                    raise CatalogError(f"Linha {row_number}: localidade duplicada '{name}'.")
                try:
                    latitude = float(row.get("latitude", ""))
                    longitude = float(row.get("longitude", ""))
                except (TypeError, ValueError) as exc:
                    message = f"Linha {row_number}: latitude/longitude inválidas."
                    raise CatalogError(message) from exc
                if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                    raise CatalogError(f"Linha {row_number}: coordenadas fora dos limites WGS84.")
                locations.append(Location(name, latitude, longitude, country, state))
                names.add(identity)
    except OSError as exc:
        raise CatalogError(f"Não foi possível ler '{catalog_path}': {exc}") from exc
    if not locations:
        raise CatalogError("O catálogo não contém localidades.")
    return locations


def filter_locations(
    locations: list[Location], country: str | None = None, state: str | None = None
) -> list[Location]:
    """Filtra pelo país e pela região administrativa presentes no catálogo."""
    return [
        item
        for item in locations
        if (country is None or item.country == country) and (state is None or item.state == state)
    ]
