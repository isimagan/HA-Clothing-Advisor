"""Sensor platform for HA Clothing Advisor."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ClothingAdvisorConfigEntry
from .const import DOMAIN
from .coordinator import ClothingAdvisorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ClothingAdvisorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the clothing recommendation sensor."""
    async_add_entities([ClothingRecommendationSensor(entry.runtime_data)])


class ClothingRecommendationSensor(
    CoordinatorEntity[ClothingAdvisorCoordinator], SensorEntity
):
    """Expose the coordinator's structured recommendation."""

    _attr_has_entity_name = True
    _attr_translation_key = "recommendation"
    _attr_icon = "mdi:tshirt-crew"

    def __init__(self, coordinator: ClothingAdvisorCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        assert coordinator.config_entry is not None
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Clothing Advisor",
            manufacturer="HA Clothing Advisor",
            model="Forecast-based clothing recommendation",
            configuration_url="https://github.com/isimagan/HA-Clothing-Advisor",
        )

    @property
    def native_value(self) -> str:
        """Return the human-readable clothing combination."""
        return self.coordinator.data.state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return details for dashboards and automations."""
        attributes = asdict(self.coordinator.data)
        attributes.pop("state")
        return attributes
