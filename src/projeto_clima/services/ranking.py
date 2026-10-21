"""Associação de respostas e cálculo determinístico do ranking."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from math import isfinite

from projeto_clima.storage.locations import Location


@dataclass(frozen=True)
class Result:
    name: str
    country: str | None
    state: str | None
    requested_latitude: float
    requested_longitude: float
    grid_latitude: float | None
    grid_longitude: float | None
    temperature: float | None
    unit: str
    local_time: str | None
    timezone: str | None
    comparable_time: datetime | None
    status: str


def rank_locations(
    locations: list[Location], responses: list[dict], limit: int = 5
) -> tuple[list[Result], list[Result], list[str]]:
    """Valida respostas alinhadas por ordem da API; devolve ranking, detalhes e avisos."""
    if len(locations) != len(responses):
        raise ValueError("Quantidade de respostas diferente da quantidade de localidades.")
    results: list[Result] = []
    warnings: list[str] = []
    for location, record in zip(locations, responses, strict=True):
        current = record.get("current") if isinstance(record, dict) else None
        value = current.get("temperature_2m") if isinstance(current, dict) else None
        status = "ok"
        temperature: float | None
        try:
            if isinstance(value, bool):
                raise ValueError
            temperature = float(value)
            if not isfinite(temperature):
                raise ValueError
        except (TypeError, ValueError):
            temperature = None
            status = "Temperatura ausente ou inválida"
        units = record.get("current_units")
        unit = str(units.get("temperature_2m", "°C")) if isinstance(units, dict) else "°C"
        if unit not in {"°C", "°F"}:
            temperature, status = None, f"Unidade inesperada: {unit}"
        local_time = current.get("time") if isinstance(current, dict) else None
        tz_name = record.get("timezone")
        comparable_time = None
        if isinstance(local_time, str):
            try:
                parsed = datetime.fromisoformat(local_time)
                if parsed.tzinfo:
                    comparable_time = parsed.astimezone(UTC)
                elif isinstance(record.get("utc_offset_seconds"), (int, float)):
                    offset = timedelta(seconds=record["utc_offset_seconds"])
                    comparable_time = (parsed - offset).replace(tzinfo=UTC)
            except ValueError:
                warnings.append(f"Horário inválido recebido para {location.name}.")
        else:
            warnings.append(f"Horário ausente para {location.name}.")
        results.append(
            Result(
                name=location.name,
                country=location.country,
                state=location.state,
                requested_latitude=location.latitude,
                requested_longitude=location.longitude,
                grid_latitude=record.get("latitude"),
                grid_longitude=record.get("longitude"),
                temperature=temperature,
                unit=unit,
                local_time=local_time,
                timezone=tz_name,
                comparable_time=comparable_time,
                status=status,
            )
        )
    units = {item.unit for item in results if item.temperature is not None}
    if len(units) > 1:
        raise ValueError("Não é possível comparar temperaturas em unidades diferentes.")
    valid = sorted(
        (item for item in results if item.temperature is not None),
        key=lambda item: (-item.temperature, item.name.casefold()),
    )
    if len(valid) < min(limit, 5):
        warnings.append(f"Somente {len(valid)} localidades têm temperatura válida.")
    timestamps = [item.comparable_time for item in results if item.comparable_time]
    if timestamps and (max(timestamps) - min(timestamps)).total_seconds() > 3600:
        warnings.append(
            "Os horários das medições divergem em mais de uma hora; compare com cautela."
        )
    ignored = sum(item.temperature is None for item in results)
    if ignored:
        warnings.append(
            f"{ignored} localidade(s) ignorada(s) por temperatura inválida ou unidade inesperada."
        )
    return valid[: min(limit, 5)], results, warnings


def daily_max_snapshot(records: list[dict], selected_date: date) -> list[dict]:
    """Extrai a máxima diária local de cada resposta para usar no ranking."""
    target = selected_date.isoformat()
    snapshots: list[dict] = []
    for record in records:
        daily = record.get("daily") if isinstance(record, dict) else None
        dates = daily.get("time") if isinstance(daily, dict) else None
        temperatures = daily.get("temperature_2m_max") if isinstance(daily, dict) else None
        value = None
        local_date = None
        if isinstance(dates, list) and isinstance(temperatures, list) and target in dates:
            index = dates.index(target)
            local_date = dates[index]
            if index < len(temperatures):
                value = temperatures[index]
        units = record.get("daily_units") if isinstance(record, dict) else None
        snapshot = record.copy() if isinstance(record, dict) else {}
        snapshot["current"] = {"time": local_date, "temperature_2m": value}
        snapshot["current_units"] = {
            "temperature_2m": units.get("temperature_2m_max", "°C")
            if isinstance(units, dict)
            else "°C"
        }
        snapshot.pop("utc_offset_seconds", None)
        snapshots.append(snapshot)
    return snapshots
