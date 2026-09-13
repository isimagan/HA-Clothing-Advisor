"""Weather entity compatibility checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
    SERVICE_GET_FORECASTS,
    WeatherEntityFeature,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_SUPPORTED_FEATURES
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError


@dataclass(frozen=True)
class CompatibilityReport:
    """Describe data available from a weather entity."""

    usable: bool
    forecast_type: str | None
    capabilities: dict[str, bool]


async def async_get_forecast(
    hass: HomeAssistant, entity_id: str, forecast_type: str
) -> list[dict[str, Any]]:
    """Fetch a forecast through Home Assistant's supported service API."""
    response = await hass.services.async_call(
        WEATHER_DOMAIN,
        SERVICE_GET_FORECASTS,
        {ATTR_ENTITY_ID: entity_id, "type": forecast_type},
        blocking=True,
        return_response=True,
    )
    if not isinstance(response, dict):
        return []
    entity_response = response.get(entity_id, {})
    if not isinstance(entity_response, dict):
        return []
    forecast = entity_response.get("forecast", [])
    return forecast if isinstance(forecast, list) else []


async def inspect_weather_entity(
    hass: HomeAssistant, entity_id: str
) -> CompatibilityReport:
    """Inspect current attributes and the best available forecast."""
    state = hass.states.get(entity_id)
    if state is None or not entity_id.startswith("weather."):
        return CompatibilityReport(False, None, _empty_capabilities())

    supported = int(state.attributes.get(ATTR_SUPPORTED_FEATURES, 0))
    candidates = (
        ("hourly", WeatherEntityFeature.FORECAST_HOURLY),
        ("twice_daily", WeatherEntityFeature.FORECAST_TWICE_DAILY),
        ("daily", WeatherEntityFeature.FORECAST_DAILY),
    )
    forecast_type: str | None = None
    forecast: list[dict[str, Any]] = []
    for candidate, feature in candidates:
        if not supported & feature:
            continue
        try:
            forecast = await async_get_forecast(hass, entity_id, candidate)
        except (HomeAssistantError, ValueError):
            continue
        if forecast:
            forecast_type = candidate
            break

    samples = [state.attributes, *forecast]
    capabilities = {
        "temperature": state.attributes.get("temperature") is not None,
        "forecast": forecast_type is not None and _has_value(
            forecast, "temperature"
        ),
        "apparent_temperature": _has_value(samples, "apparent_temperature"),
        "wind_speed": _has_value(samples, "wind_speed"),
        "precipitation": _has_value(forecast, "precipitation"),
        "precipitation_probability": _has_value(
            forecast, "precipitation_probability"
        ),
        "condition": state.state not in {"unknown", "unavailable"},
        "wind_gust_speed": _has_value(samples, "wind_gust_speed"),
        "uv_index": _has_value(samples, "uv_index"),
    }
    usable = capabilities["temperature"] and capabilities["forecast"]
    return CompatibilityReport(usable, forecast_type, capabilities)


def _has_value(samples: Any, key: str) -> bool:
    """Return whether any mapping has a usable value for a key."""
    return any(
        isinstance(sample, dict) and sample.get(key) is not None
        for sample in samples
    )


def _empty_capabilities() -> dict[str, bool]:
    """Return an empty capability map in display order."""
    return {
        "temperature": False,
        "forecast": False,
        "apparent_temperature": False,
        "wind_speed": False,
        "precipitation": False,
        "precipitation_probability": False,
        "condition": False,
        "wind_gust_speed": False,
        "uv_index": False,
    }
