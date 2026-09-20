"""HA Clothing Advisor integration."""

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_HEAVY_JACKET_THRESHOLD,
    CONF_LIGHT_JACKET_THRESHOLD,
    CONF_PROFILE,
    CONF_SHORTS_THRESHOLD,
    CONF_SWEATER_THRESHOLD,
    CONF_WEATHER_ENTITY,
    DEFAULTS,
    DOMAIN,
    PROFILE_COLD,
    PROFILE_CUSTOM,
    PROFILE_WARM,
)
from .coordinator import ClothingAdvisorCoordinator

PLATFORMS = [Platform.SELECT, Platform.SENSOR]
CARD_URL = "/clothing_advisor/clothing-advisor-card.js"
CARD_VERSION = "0.9.0"
CARD_PATH = Path(__file__).parent / "frontend" / "clothing-advisor-card.js"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

ClothingAdvisorConfigEntry = ConfigEntry[ClothingAdvisorCoordinator]


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Register the bundled dashboard card."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(CARD_PATH), False)]
    )
    add_extra_js_url(hass, f"{CARD_URL}?v={CARD_VERSION}")
    return True


async def async_migrate_entry(
    hass: HomeAssistant, entry: ClothingAdvisorConfigEntry
) -> bool:
    """Migrate legacy fine-tuned profiles to exact custom thresholds."""
    if entry.version != 1:
        return True

    data = dict(entry.data)
    options = dict(entry.options)
    effective = DEFAULTS | data | options
    threshold_keys = (
        CONF_SHORTS_THRESHOLD,
        CONF_SWEATER_THRESHOLD,
        CONF_LIGHT_JACKET_THRESHOLD,
        CONF_HEAVY_JACKET_THRESHOLD,
    )
    if any(effective[key] != DEFAULTS[key] for key in threshold_keys):
        adjustment = {
            PROFILE_COLD: 2,
            PROFILE_WARM: -2,
        }.get(effective[CONF_PROFILE], 0)
        for key in threshold_keys:
            options[key] = float(effective[key]) + adjustment
        options[CONF_PROFILE] = PROFILE_CUSTOM

    hass.config_entries.async_update_entry(
        entry, data=data, options=options, version=2
    )
    return True


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
