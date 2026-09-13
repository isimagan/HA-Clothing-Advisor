"""Config flow for HA Clothing Advisor."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_WEATHER_ENTITY, DOMAIN


class ClothingAdvisorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the HA Clothing Advisor config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            weather_entity = user_input[CONF_WEATHER_ENTITY]
            await self.async_set_unique_id(weather_entity)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self.hass.states.get(weather_entity).name
                if self.hass.states.get(weather_entity)
                else weather_entity,
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_WEATHER_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="weather")
                    )
                }
            ),
        )

