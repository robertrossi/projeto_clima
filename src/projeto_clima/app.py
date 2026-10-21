"""Interface Streamlit do dashboard Projeto Clima."""

import logging
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st

from projeto_clima.clients.open_meteo import (
    OpenMeteoError,
    fetch_current,
    fetch_daily_max_for_date,
)
from projeto_clima.services.ranking import daily_max_snapshot, rank_locations
from projeto_clima.storage.locations import (
    CatalogError,
    Location,
    filter_locations,
    load_locations,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
DEFAULT_CATALOG = Path(__file__).resolve().parents[2] / "config" / "locations.example.csv"


@st.cache_data(ttl=300, show_spinner=False)
def _cached_current(locations: tuple[Location, ...]) -> list[dict]:
    return fetch_current(list(locations))


@st.cache_data(ttl=300, show_spinner=False)
def _cached_daily_max(
    locations: tuple[Location, ...], selected_date: date, historical: bool
) -> list[dict]:
    return fetch_daily_max_for_date(list(locations), selected_date, historical)


st.set_page_config(page_title="Projeto Clima", page_icon="🌡️", layout="wide")
st.title("🌡️ Projeto Clima")
st.caption("Compare temperaturas do ar a 2 m em localidades configuráveis.")
catalog_path = st.sidebar.text_input("Arquivo CSV", value=str(DEFAULT_CATALOG))
refresh = st.sidebar.button("Atualizar agora", type="primary")

try:
    catalog_locations = load_locations(catalog_path)
except CatalogError as exc:
    st.error(f"Catálogo inválido: {exc}")
    st.stop()

countries = sorted({item.country for item in catalog_locations if item.country})
country_filter = st.sidebar.selectbox("País", ["Todos", *countries])
country_locations = filter_locations(
    catalog_locations, country=country_filter if country_filter != "Todos" else None
)
states = sorted({item.state for item in country_locations if item.state})
state_filter = st.sidebar.selectbox("Estado / região", ["Todos", *states])
locations = filter_locations(
    country_locations, state=state_filter if state_filter != "Todos" else None
)
st.sidebar.caption(f"{len(locations)} de {len(catalog_locations)} localidades selecionadas")
if not locations:
    st.info("Nenhuma localidade corresponde aos filtros escolhidos.")
    st.stop()

mode = st.sidebar.radio("Período", ["Agora", "Data"])
selected_date = None
historical = False
if mode == "Data":
    today = date.today()
    selected_date = st.sidebar.date_input(
        "Data local",
        value=today,
        min_value=date(1940, 1, 1),
        max_value=today + timedelta(days=15),
    )
    historical = selected_date < today

if "last_query_at" not in st.session_state:
    st.session_state.last_query_at = None
if refresh:
    _cached_current.clear()
    _cached_daily_max.clear()

try:
    with st.spinner(f"Consultando {len(locations)} localidades…"):
        if mode == "Agora":
            responses = _cached_current(tuple(locations))
            data_label = "Condições atuais"
        else:
            responses = daily_max_snapshot(
                _cached_daily_max(tuple(locations), selected_date, historical), selected_date
            )
            data_label = "Reanálise histórica" if historical else "Previsão diária"
    top, all_results, warnings = rank_locations(locations, responses)
    st.session_state.last_query_at = datetime.now().astimezone().isoformat(timespec="seconds")
except OpenMeteoError as exc:
    st.error(str(exc))
    st.info("Confira sua conexão e tente novamente com ‘Atualizar agora’.")
    st.stop()
except (ValueError, KeyError, TypeError) as exc:
    st.error(f"Não foi possível validar os dados recebidos: {exc}")
    st.stop()

st.caption(
    f"{data_label} · consulta em {st.session_state.last_query_at} · Celsius · cache de 5 min"
)
if mode == "Data":
    st.caption(
        "Comparação pelas máximas do dia local de cada cidade; os períodos podem não coincidir "
        "exatamente entre fusos. A reanálise é baseada em modelos e a disponibilidade varia."
    )
for warning in warnings:
    st.warning(warning)
if not top:
    st.info("Nenhuma localidade retornou temperatura válida para este período.")
else:
    st.subheader(f"Até {len(top)} localidades mais quentes")
    cols = st.columns(len(top))
    for column, result in zip(cols, top, strict=False):
        column.metric(result.name, f"{result.temperature:.1f} {result.unit}")
        missing_label = "Data ausente" if mode == "Data" else "Horário ausente"
        local_time = result.local_time or missing_label
        timezone_name = result.timezone or "fuso desconhecido"
        column.caption(f"{local_time} · {timezone_name}")

st.subheader("Localidades consultadas")
table = [
    {
        "Localidade": item.name,
        "País": item.country,
        "Estado / região": item.state,
        "Temperatura": item.temperature,
        "Unidade": item.unit,
        "Data / horário local": item.local_time,
        "Fuso": item.timezone,
        "Latitude solicitada": item.requested_latitude,
        "Longitude solicitada": item.requested_longitude,
        "Latitude da grade": item.grid_latitude,
        "Longitude da grade": item.grid_longitude,
        "Estado do dado": item.status,
    }
    for item in all_results
]
st.dataframe(table, hide_index=True, use_container_width=True)
