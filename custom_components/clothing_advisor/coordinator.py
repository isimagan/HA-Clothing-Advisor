"""Data coordinator for HA Clothing Advisor."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.weather import WeatherEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_SUPPORTED_FEATURES,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.unit_conversion import SpeedConverter, TemperatureConverter

from .compatibility import async_get_forecast
from .const import CONF_WEATHER_ENTITY, DEFAULTS, DOMAIN
from .recommendation import (
    ClothingRecommendation,
    WeatherSnapshot,
    build_recommendation,
)

_LOGGER = logging.getLogger(__name__)
UPDATE_INTERVAL = timedelta(minutes=30)


class ClothingAdvisorCoordinator(DataUpdateCoordinator[ClothingRecommendation]):
    """Fetch forecasts and calculate the current recommendation."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry

    async def _async_update_data(self) -> ClothingRecommendation:
        """Read current weather, fetch a forecast, and calculate clothing."""
        settings = DEFAULTS | self.entry.data | self.entry.options
        entity_id = settings[CONF_WEATHER_ENTITY]
        state = self.hass.states.get(entity_id)
        if state is None or state.state in {"unknown", "unavailable"}:
            raise UpdateFailed(f"Weather entity {entity_id} is unavailable")

        temperature = _number(state.attributes.get("temperature"))
        if temperature is None:
            raise UpdateFailed(f"Weather entity {entity_id} has no temperature")

        forecast_type, forecast = await self._async_best_forecast(
            entity_id, int(state.attributes.get(ATTR_SUPPORTED_FEATURES, 0))
        )
        if forecast_type is None or not forecast:
            raise UpdateFailed(f"Weather entity {entity_id} has no usable forecast")

        temperature_unit = state.attributes.get(
            "temperature_unit", UnitOfTemperature.CELSIUS
        )
        wind_unit = state.attributes.get(
            "wind_speed_unit", UnitOfSpeed.METERS_PER_SECOND
        )
        normalized_forecast = [
            _normalize_forecast(item, temperature_unit, wind_unit)
            for item in forecast
        ]
        snapshot = WeatherSnapshot(
            temperature=_to_celsius(temperature, temperature_unit),
            apparent_temperature=_converted(
                state.attributes.get("apparent_temperature"),
                temperature_unit,
                TemperatureConverter,
                UnitOfTemperature.CELSIUS,
            ),
            condition=state.state,
            wind_speed=_converted(
                state.attributes.get("wind_speed"),
                wind_unit,
                SpeedConverter,
                UnitOfSpeed.METERS_PER_SECOND,
            ),
            wind_gust_speed=_converted(
                state.attributes.get("wind_gust_speed"),
                wind_unit,
                SpeedConverter,
                UnitOfSpeed.METERS_PER_SECOND,
            ),
            forecast_type=forecast_type,
            forecast=normalized_forecast,
        )
        return build_recommendation(snapshot, settings)

    async def _async_best_forecast(
        self, entity_id: str, supported: int
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Fetch the most precise supported forecast."""
        candidates = (
            ("hourly", WeatherEntityFeature.FORECAST_HOURLY),
            ("twice_daily", WeatherEntityFeature.FORECAST_TWICE_DAILY),
            ("daily", WeatherEntityFeature.FORECAST_DAILY),
        )
        for forecast_type, feature in candidates:
            if not supported & feature:
                continue
            try:
                forecast = await async_get_forecast(
                    self.hass, entity_id, forecast_type
                )
            except (HomeAssistantError, ValueError) as err:
                _LOGGER.debug("Unable to fetch %s forecast: %s", forecast_type, err)
                continue
            if forecast:
                return forecast_type, forecast
        return None, []


def _normalize_forecast(
    item: dict[str, Any], temperature_unit: str, wind_unit: str
) -> dict[str, Any]:
    """Normalize forecast temperature and wind values to SI units."""
    normalized = dict(item)
    for key in ("temperature", "apparent_temperature", "templow"):
        normalized[key] = _converted(
            item.get(key),
            temperature_unit,
            TemperatureConverter,
            UnitOfTemperature.CELSIUS,
        )
    for key in ("wind_speed", "wind_gust_speed"):
        normalized[key] = _converted(
            item.get(key),
            wind_unit,
            SpeedConverter,
            UnitOfSpeed.METERS_PER_SECOND,
        )
    return normalized


def _to_celsius(value: float, unit: str) -> float:
    """Convert a temperature to Celsius."""
    return float(TemperatureConverter.convert(value, unit, UnitOfTemperature.CELSIUS))


def _converted(
    value: Any, from_unit: str, converter: Any, to_unit: str
) -> float | None:
    """Convert an optional numeric value between units."""
    numeric = _number(value)
    if numeric is None:
        return None
    try:
        return float(converter.convert(numeric, from_unit, to_unit))
    except (TypeError, ValueError):
        return numeric


def _number(value: Any) -> float | None:
    """Convert a value to float when possible."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
