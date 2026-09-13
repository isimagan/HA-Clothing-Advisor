"""Sensor platform for HA Clothing Advisor."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import Event, EventStateChangedData, HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.components.sensor import SensorEntity

from .const import CONF_WEATHER_ENTITY

RAINY_CONDITIONS = {"pouring", "rainy", "lightning-rainy"}
SNOWY_CONDITIONS = {"snowy", "snowy-rainy"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the clothing recommendation sensor."""
    async_add_entities([ClothingRecommendationSensor(entry)])


class ClothingRecommendationSensor(SensorEntity):
    """Recommend clothing based on a weather entity."""

    _attr_has_entity_name = True
    _attr_name = "Clothing recommendation"
    _attr_icon = "mdi:tshirt-crew"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._weather_entity = entry.data[CONF_WEATHER_ENTITY]
        self._attr_unique_id = entry.entry_id
        self._attr_native_value = "Waiting for weather data"
        self._attr_extra_state_attributes = {
            "weather_entity": self._weather_entity
        }

    async def async_added_to_hass(self) -> None:
        """Start listening for weather changes."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._weather_entity], self._async_weather_changed
            )
        )
        self._update_recommendation()

    async def _async_weather_changed(
        self, event: Event[EventStateChangedData]
    ) -> None:
        """Update when the source weather entity changes."""
        self._update_recommendation()
        self.async_write_ha_state()

    def _update_recommendation(self) -> None:
        """Calculate a recommendation from the current conditions."""
        weather = self.hass.states.get(self._weather_entity)
        if weather is None:
            self._attr_available = False
            return

        temperature = weather.attributes.get(ATTR_TEMPERATURE)
        condition = weather.state
        self._attr_available = True

        if not isinstance(temperature, (int, float)):
            recommendation = "Check the forecast before getting dressed"
        elif temperature <= 0:
            recommendation = "Winter coat, warm layers, hat and gloves"
        elif temperature <= 8:
            recommendation = "Warm jacket and layered clothing"
        elif temperature <= 15:
            recommendation = "Light jacket or sweater"
        elif temperature <= 20:
            recommendation = "Light layers"
        else:
            recommendation = "T-shirt and light clothing"

        if condition in RAINY_CONDITIONS:
            recommendation += "; bring a rain jacket or umbrella"
        elif condition in SNOWY_CONDITIONS:
            recommendation += "; choose waterproof footwear"

        self._attr_native_value = recommendation
        self._attr_extra_state_attributes = {
            "weather_entity": self._weather_entity,
            "temperature": temperature,
            "condition": condition,
        }

