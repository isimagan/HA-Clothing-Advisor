"""Sensor platform for HA Clothing Advisor."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ClothingAdvisorConfigEntry
from .const import DOMAIN
from .coordinator import ClothingAdvisorCoordinator
from .localization import localized_reason
from .recommendation import RECOMMENDATION_STATES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ClothingAdvisorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the clothing recommendation sensor."""
    translations = await async_get_translations(
        hass, hass.config.language, "common", {DOMAIN}
    )
    async_add_entities(
        [ClothingRecommendationSensor(entry.runtime_data, translations)]
    )


class ClothingRecommendationSensor(
    CoordinatorEntity[ClothingAdvisorCoordinator], SensorEntity
):
    """Expose the coordinator's structured recommendation."""

    _attr_has_entity_name = True
    _attr_translation_key = "recommendation"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(RECOMMENDATION_STATES)
    _attr_icon = "mdi:tshirt-crew"

    def __init__(
        self,
        coordinator: ClothingAdvisorCoordinator,
        translations: dict[str, str],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._translations = translations
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
        attributes["reason"] = localized_reason(
            self.coordinator.data, self._translations
        )
        return attributes
