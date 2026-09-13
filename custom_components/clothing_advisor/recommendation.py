"""Pure clothing recommendation engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from .const import (
    CONF_FORECAST_HOURS,
    CONF_HEAVY_JACKET_THRESHOLD,
    CONF_LIGHT_JACKET_THRESHOLD,
    CONF_PROFILE,
    CONF_SHORTS_THRESHOLD,
    CONF_SWEATER_THRESHOLD,
    PROFILE_COLD,
    PROFILE_WARM,
)

RAINY_CONDITIONS = {"pouring", "rainy", "lightning-rainy"}
PROFILE_ADJUSTMENTS = {PROFILE_COLD: 2.0, PROFILE_WARM: -2.0}


@dataclass(frozen=True)
class WeatherSnapshot:
    """Normalized weather data used by the recommendation engine."""

    temperature: float
    apparent_temperature: float | None
    condition: str | None
    wind_speed: float | None
    wind_gust_speed: float | None
    forecast_type: str
    forecast: list[dict[str, Any]]


@dataclass(frozen=True)
class ClothingRecommendation:
    """A structured clothing recommendation."""

    state: str
    bottom: str
    base_layer: str
    mid_layer: str | None
    top: str
    outerwear: str
    rain: bool
    reason: str
    current_temperature: float
    apparent_temperature: float
    lowest_apparent_temperature: float
    highest_apparent_temperature: float
    highest_precipitation_probability: float | None
    max_wind_speed: float | None
    forecast_hours: int
    forecast_type: str


def build_recommendation(
    weather: WeatherSnapshot,
    settings: dict[str, Any],
    now: datetime | None = None,
) -> ClothingRecommendation:
    """Build a layer-aware recommendation from current and forecast weather."""
    now = now or datetime.now(timezone.utc)
    hours = int(settings[CONF_FORECAST_HOURS])
    current_feels = (
        weather.apparent_temperature
        if weather.apparent_temperature is not None
        else weather.temperature
    )
    relevant = _forecast_within_horizon(weather.forecast, now, hours)

    forecast_temperatures: list[float] = []
    for item in relevant:
        value = _number(item.get("apparent_temperature"))
        if value is None:
            value = _number(item.get("temperature"))
        if value is not None:
            forecast_temperatures.append(value)

    temperatures = [current_feels, *forecast_temperatures]
    low = min(temperatures)
    high = max(temperatures)

    adjustment = PROFILE_ADJUSTMENTS.get(settings[CONF_PROFILE], 0.0)
    shorts_threshold = float(settings[CONF_SHORTS_THRESHOLD]) + adjustment
    sweater_threshold = float(settings[CONF_SWEATER_THRESHOLD]) + adjustment
    light_jacket_threshold = (
        float(settings[CONF_LIGHT_JACKET_THRESHOLD]) + adjustment
    )
    heavy_jacket_threshold = (
        float(settings[CONF_HEAVY_JACKET_THRESHOLD]) + adjustment
    )

    bottom = "Shorts" if current_feels >= shorts_threshold else "Trousers"
    top_temperature = high if high - current_feels >= 4 else current_feels
    base_layer = "T-shirt"
    mid_layer = "Sweater" if top_temperature <= sweater_threshold else None
    top = f"{base_layer} + {mid_layer}" if mid_layer else base_layer

    if low < heavy_jacket_threshold:
        outerwear = "Thick jacket"
    elif low < light_jacket_threshold:
        outerwear = "Light jacket"
    else:
        outerwear = "No jacket"

    wind_values = [
        value
        for value in [
            weather.wind_speed,
            weather.wind_gust_speed,
            *(_number(item.get("wind_speed")) for item in relevant),
            *(_number(item.get("wind_gust_speed")) for item in relevant),
        ]
        if value is not None
    ]
    max_wind = max(wind_values, default=None)
    if max_wind is not None and max_wind > 12:
        outerwear = _warmer_outerwear(outerwear)
    elif max_wind is not None and max_wind > 8 and low <= 18 + adjustment:
        if outerwear == "No jacket":
            outerwear = "Light jacket"

    probabilities = [
        value
        for item in relevant
        if (value := _number(item.get("precipitation_probability"))) is not None
    ]
    highest_probability = max(probabilities, default=None)
    precipitation_values = [
        value
        for item in relevant
        if (value := _number(item.get("precipitation"))) is not None
    ]
    precipitation = max(precipitation_values, default=0)
    conditions = {weather.condition} | {item.get("condition") for item in relevant}
    rain = (
        (highest_probability is not None and highest_probability >= 50)
        or precipitation > 0.5
        or bool(conditions & RAINY_CONDITIONS)
    )
    if rain and outerwear in {"No jacket", "Light jacket"}:
        outerwear = "Rain jacket"

    reason_parts = [f"Feels like {current_feels:.1f} °C now"]
    if high - current_feels >= 4:
        reason_parts.append(f"warming to about {high:.1f} °C")
    elif current_feels - low >= 4:
        reason_parts.append(f"cooling to about {low:.1f} °C")
    if max_wind is not None and max_wind > 8:
        reason_parts.append("wind makes an extra layer useful")
    if rain:
        reason_parts.append("rain is possible")
    reason = ". ".join(reason_parts) + "."

    state_layers = [bottom, base_layer]
    if mid_layer:
        state_layers.append(mid_layer)
    state_layers.append(outerwear)

    return ClothingRecommendation(
        state=" · ".join(state_layers),
        bottom=bottom,
        base_layer=base_layer,
        mid_layer=mid_layer,
        top=top,
        outerwear=outerwear,
        rain=rain,
        reason=reason,
        current_temperature=weather.temperature,
        apparent_temperature=current_feels,
        lowest_apparent_temperature=low,
        highest_apparent_temperature=high,
        highest_precipitation_probability=highest_probability,
        max_wind_speed=max_wind,
        forecast_hours=hours,
        forecast_type=weather.forecast_type,
    )


def _forecast_within_horizon(
    forecast: list[dict[str, Any]], now: datetime, hours: int
) -> list[dict[str, Any]]:
    """Return forecast points inside the horizon, with a coarse fallback."""
    horizon = now + timedelta(hours=hours)
    relevant = []
    for item in forecast:
        timestamp = item.get("datetime")
        if not isinstance(timestamp, str):
            continue
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if now <= parsed <= horizon:
            relevant.append(item)
    return relevant or forecast[:1]


def _number(value: Any) -> float | None:
    """Convert a weather value to float when possible."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _warmer_outerwear(current: str) -> str:
    """Move outerwear one warmth level up."""
    return {
        "No jacket": "Light jacket",
        "Light jacket": "Thick jacket",
        "Rain jacket": "Thick waterproof jacket",
    }.get(current, current)
