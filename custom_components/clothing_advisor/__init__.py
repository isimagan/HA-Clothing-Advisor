"""HA Clothing Advisor integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_WEATHER_ENTITY, DEFAULTS
from .coordinator import ClothingAdvisorCoordinator

PLATFORMS = [Platform.SENSOR]

ClothingAdvisorConfigEntry = ConfigEntry[ClothingAdvisorCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: ClothingAdvisorConfigEntry
) -> bool:
    """Set up HA Clothing Advisor from a config entry."""
    coordinator = ClothingAdvisorCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    weather_entity = (DEFAULTS | entry.data | entry.options)[CONF_WEATHER_ENTITY]
    entry.async_on_unload(
        async_track_state_change_event(
            hass,
            [weather_entity],
            lambda _event: coordinator.async_request_refresh(),
        )
    )
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ClothingAdvisorConfigEntry
) -> bool:
    """Unload a HA Clothing Advisor config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(
    hass: HomeAssistant, entry: ClothingAdvisorConfigEntry
) -> None:
    """Reload the integration after its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
