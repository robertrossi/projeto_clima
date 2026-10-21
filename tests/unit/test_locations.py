import pytest

from projeto_clima.storage.locations import (
    CatalogError,
    Location,
    filter_locations,
    load_locations,
)


def test_loads_catalog_and_coordinates(tmp_path):
    path = tmp_path / "locations.csv"
    path.write_text(
        "name,latitude,longitude,country,state\nA,-23.5,-46.6,Brasil,São Paulo\n",
        encoding="utf-8",
    )
    location = load_locations(path)[0]
    assert location.name == "A"
    assert location.country == "Brasil"
    assert location.state == "São Paulo"


def test_geographic_metadata_is_optional(tmp_path):
    path = tmp_path / "locations.csv"
    path.write_text("name,latitude,longitude\nA,-23.5,-46.6\n", encoding="utf-8")
    location = load_locations(path)[0]
    assert location.country is None
    assert location.state is None


def test_filters_locations_by_country_and_state():
    locations = [
        Location("A", 0, 0, "Brasil", "SP"),
        Location("B", 0, 0, "Brasil", "RJ"),
        Location("C", 0, 0, "Chile", "Santiago"),
    ]
    assert [item.name for item in filter_locations(locations, country="Brasil")] == [
        "A",
        "B",
    ]
    assert [item.name for item in filter_locations(locations, country="Brasil", state="SP")] == [
        "A"
    ]


def test_same_city_name_is_allowed_in_different_regions(tmp_path):
    path = tmp_path / "locations.csv"
    path.write_text(
        "name,latitude,longitude,country,state\n"
        "San José,9.9,-84.1,Costa Rica,San José\n"
        "San José,37.3,-121.9,United States,California\n",
        encoding="utf-8",
    )
    assert len(load_locations(path)) == 2


@pytest.mark.parametrize(
    "csv, message",
    [
        ("name,latitude\nA,1\n", "colunas"),
        ("name,latitude,longitude\nA,91,0\n", "limites"),
        ("name,latitude,longitude\nA,1,2\na,3,4\n", "duplicad"),
        ("name,latitude,longitude\nA,x,2\n", "inválidas"),
        ("name,latitude,longitude\n", "não contém"),
    ],
)
def test_rejects_invalid_catalog(tmp_path, csv, message):
    path = tmp_path / "bad.csv"
    path.write_text(csv, encoding="utf-8")
    with pytest.raises(CatalogError, match=message):
        load_locations(path)
