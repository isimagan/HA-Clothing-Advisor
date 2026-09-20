"""Select platform for HA Clothing Advisor."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ClothingAdvisorConfigEntry
from .const import (
    CONF_FORECAST_HOURS,
    DEFAULTS,
    DOMAIN,
    FORECAST_HOUR_OPTIONS,
)
from .coordinator import ClothingAdvisorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ClothingAdvisorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the forecast horizon select."""
    del hass
    async_add_entities([ClothingAdvisorForecastHoursSelect(entry.runtime_data)])


class ClothingAdvisorForecastHoursSelect(
    CoordinatorEntity[ClothingAdvisorCoordinator], SelectEntity
):
    """Control how many forecast hours the recommendation considers."""

    _attr_has_entity_name = True
    _attr_translation_key = "forecast_hours"
    _attr_icon = "mdi:clock-outline"
    _attr_options = [str(value) for value in FORECAST_HOUR_OPTIONS]

    def __init__(self, coordinator: ClothingAdvisorCoordinator) -> None:
        """Initialize the forecast horizon select."""
        super().__init__(coordinator)
        assert coordinator.config_entry is not None
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_forecast_hours"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Clothing Advisor",
            manufacturer="HA Clothing Advisor",
            model="Forecast-based clothing recommendation",
            configuration_url="https://github.com/isimagan/HA-Clothing-Advisor",
        )

    @property
    def current_option(self) -> str:
        """Return the selected forecast horizon."""
        assert self.coordinator.config_entry is not None
        entry = self.coordinator.config_entry
        settings = DEFAULTS | entry.data | entry.options
        value = int(settings[CONF_FORECAST_HOURS])
        selected = (
            value
            if value in FORECAST_HOUR_OPTIONS
            else DEFAULTS[CONF_FORECAST_HOURS]
        )
        return str(selected)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose the integration instance used to pair the dashboard card."""
        assert self.coordinator.config_entry is not None
        return {"clothing_advisor_id": self.coordinator.config_entry.entry_id}

    async def async_select_option(self, option: str) -> None:
        """Update the forecast horizon and refresh the integration."""
        hours = int(option)
        if hours not in FORECAST_HOUR_OPTIONS:
            raise ValueError(f"Unsupported forecast horizon: {option}")

        assert self.coordinator.config_entry is not None
        entry = self.coordinator.config_entry
        options = dict(entry.options)
        options[CONF_FORECAST_HOURS] = hours
        self.hass.config_entries.async_update_entry(entry, options=options)
