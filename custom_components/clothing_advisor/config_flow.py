"""Config and options flows for HA Clothing Advisor."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .compatibility import CompatibilityReport, inspect_weather_entity
from .const import (
    CONF_FORECAST_HOURS,
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
    PROFILE_NORMAL,
    PROFILE_WARM,
)


def _weather_schema(default: str | None = None) -> vol.Schema:
    """Return the weather source schema."""
    key = (
        vol.Required(CONF_WEATHER_ENTITY, default=default)
        if default
        else vol.Required(CONF_WEATHER_ENTITY)
    )
    return vol.Schema(
        {
            key: selector.EntitySelector(
                selector.EntitySelectorConfig(domain="weather")
            )
        }
    )


def _profile_schema(values: dict[str, Any]) -> vol.Schema:
    """Return the profile and forecast schema with current values as defaults."""
    return vol.Schema(
        {
            vol.Required(
                CONF_PROFILE, default=values.get(CONF_PROFILE, DEFAULTS[CONF_PROFILE])
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        PROFILE_COLD,
                        PROFILE_NORMAL,
                        PROFILE_WARM,
                        PROFILE_CUSTOM,
                    ],
                    translation_key="temperature_profile",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_FORECAST_HOURS,
                default=str(
                    values.get(CONF_FORECAST_HOURS, DEFAULTS[CONF_FORECAST_HOURS])
                ),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=["2", "4", "6", "8"],
                    translation_key="forecast_hours",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


def _threshold_schema(values: dict[str, Any]) -> vol.Schema:
    """Return the custom temperature threshold schema."""
    temperature_selector = selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=-20,
            max=35,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
            unit_of_measurement="°C",
        )
    )
    return vol.Schema(
        {
            vol.Required(
                CONF_SHORTS_THRESHOLD,
                default=values.get(
                    CONF_SHORTS_THRESHOLD, DEFAULTS[CONF_SHORTS_THRESHOLD]
                ),
            ): temperature_selector,
            vol.Required(
                CONF_SWEATER_THRESHOLD,
                default=values.get(
                    CONF_SWEATER_THRESHOLD, DEFAULTS[CONF_SWEATER_THRESHOLD]
                ),
            ): temperature_selector,
            vol.Required(
                CONF_LIGHT_JACKET_THRESHOLD,
                default=values.get(
                    CONF_LIGHT_JACKET_THRESHOLD,
                    DEFAULTS[CONF_LIGHT_JACKET_THRESHOLD],
                ),
            ): temperature_selector,
            vol.Required(
                CONF_HEAVY_JACKET_THRESHOLD,
                default=values.get(
                    CONF_HEAVY_JACKET_THRESHOLD,
                    DEFAULTS[CONF_HEAVY_JACKET_THRESHOLD],
                ),
            ): temperature_selector,
        }
    )


def _valid_thresholds(values: dict[str, Any]) -> bool:
    """Return whether thresholds move consistently from heavy to light clothing."""
    return (
        float(values[CONF_HEAVY_JACKET_THRESHOLD])
        <= float(values[CONF_SWEATER_THRESHOLD])
        <= float(values[CONF_LIGHT_JACKET_THRESHOLD])
        <= float(values[CONF_SHORTS_THRESHOLD])
    )


def _format_report(report: CompatibilityReport, norwegian: bool) -> str:
    """Format a compatibility report as Markdown for the flow."""
    labels = {
        "temperature": "Temperatur" if norwegian else "Temperature",
        "forecast": "Timeprognose" if norwegian else "Hourly forecast",
        "apparent_temperature": "Føles som" if norwegian else "Feels like",
        "wind_speed": "Vindstyrke" if norwegian else "Wind speed",
        "precipitation": "Nedbør" if norwegian else "Precipitation",
        "precipitation_probability": (
            "Nedbørssannsynlighet" if norwegian else "Precipitation probability"
        ),
        "condition": "Værtilstand" if norwegian else "Weather condition",
        "wind_gust_speed": "Vindkast" if norwegian else "Wind gusts",
        "uv_index": "UV-indeks" if norwegian else "UV index",
    }
    rows = []
    for key, available in report.capabilities.items():
        if key == "forecast":
            status = (
                "✅"
                if report.forecast_type == "hourly"
                else "⚠️"
                if available
                else "❌"
            )
        elif key == "temperature":
            status = "✅" if available else "❌"
        else:
            status = "✅" if available else "⚠️"
        rows.append(f"| {labels[key]} | {status} |")

    heading = "| Egenskap | Status |" if norwegian else "| Capability | Status |"
    report_text = "\n".join([heading, "|---|---|", *rows])
    if report.forecast_type and report.forecast_type != "hourly":
        report_text += (
            "\n\n⚠️ Bruker "
            f"{report.forecast_type}-prognose; presisjonen blir redusert."
            if norwegian
            else f"\n\n⚠️ Using {report.forecast_type} forecast; "
            "precision is reduced."
        )
    return report_text


class ClothingAdvisorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the HA Clothing Advisor config flow."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the flow."""
        self._data: dict[str, Any] = {}
        self._report: CompatibilityReport | None = None

    async def async_migrate_entry(
        self, hass: HomeAssistant, config_entry: config_entries.ConfigEntry
    ) -> bool:
        """Migrate legacy fine-tuned profiles to exact custom thresholds."""
        if config_entry.version != 1:
            return True

        data = dict(config_entry.data)
        options = dict(config_entry.options)
        effective = DEFAULTS | data | options
        threshold_keys = tuple(_default_thresholds())
        if any(
            effective[key] != DEFAULTS[key]
            for key in threshold_keys
        ):
            adjustment = {
                PROFILE_COLD: 2,
                PROFILE_WARM: -2,
            }.get(effective[CONF_PROFILE], 0)
            for key in threshold_keys:
                options[key] = float(effective[key]) + adjustment
            options[CONF_PROFILE] = PROFILE_CUSTOM

        hass.config_entries.async_update_entry(
            config_entry, data=data, options=options, version=2
        )
        return True

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
    ) -> ClothingAdvisorOptionsFlow:
        """Return the options flow."""
        return ClothingAdvisorOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select and validate a weather entity."""
        errors: dict[str, str] = {}
        if user_input is not None:
            weather_entity = user_input[CONF_WEATHER_ENTITY]
            self._report = await inspect_weather_entity(self.hass, weather_entity)
            if not self._report.usable:
                errors["base"] = "incompatible_weather_entity"
            else:
                await self.async_set_unique_id(weather_entity)
                self._abort_if_unique_id_configured()
                self._data.update(user_input)
                return await self.async_step_compatibility()

        return self.async_show_form(
            step_id="user",
            data_schema=_weather_schema(),
            errors=errors,
        )

    async def async_step_compatibility(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show the weather entity compatibility report."""
        if user_input is not None:
            return await self.async_step_personalize()
        assert self._report is not None
        return self.async_show_form(
            step_id="compatibility",
            data_schema=vol.Schema({}),
            description_placeholders={
                "report": _format_report(
                    self._report, self.hass.config.language.startswith("nb")
                )
            },
        )

    async def async_step_personalize(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Collect the user's temperature profile and forecast period."""
        if user_input is not None:
            user_input[CONF_FORECAST_HOURS] = int(user_input[CONF_FORECAST_HOURS])
            self._data.update(user_input)
            if user_input[CONF_PROFILE] == PROFILE_CUSTOM:
                return await self.async_step_custom()
            self._data.update(_default_thresholds())
            return self._create_entry()

        return self.async_show_form(
            step_id="personalize",
            data_schema=_profile_schema(user_input or DEFAULTS),
        )

    async def async_step_custom(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Collect custom clothing temperature thresholds."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not _valid_thresholds(user_input):
                errors["base"] = "invalid_threshold_order"
            else:
                self._data.update(user_input)
                return self._create_entry()

        return self.async_show_form(
            step_id="custom",
            data_schema=_threshold_schema(user_input or DEFAULTS),
            errors=errors,
        )

    def _create_entry(self) -> FlowResult:
        """Create a config entry from the collected settings."""
        weather = self.hass.states.get(self._data[CONF_WEATHER_ENTITY])
        return self.async_create_entry(
            title=weather.name if weather else self._data[CONF_WEATHER_ENTITY],
            data=self._data,
        )


class ClothingAdvisorOptionsFlow(config_entries.OptionsFlow):
    """Allow all Clothing Advisor settings to be changed."""

    def __init__(self) -> None:
        """Initialize the options flow."""
        self._data: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit the source entity, profile, and forecast period."""
        current = DEFAULTS | self.config_entry.data | self.config_entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            report = await inspect_weather_entity(
                self.hass, user_input[CONF_WEATHER_ENTITY]
            )
            if not report.usable:
                errors["base"] = "incompatible_weather_entity"
            else:
                user_input[CONF_FORECAST_HOURS] = int(
                    user_input[CONF_FORECAST_HOURS]
                )
                self._data.update(user_input)
                if user_input[CONF_PROFILE] == PROFILE_CUSTOM:
                    return await self.async_step_custom()
                self._data.update(_default_thresholds())
                return self.async_create_entry(data=self._data)

        schema_values = current | (user_input or {})
        schema = vol.Schema(
            {
                **_weather_schema(schema_values[CONF_WEATHER_ENTITY]).schema,
                **_profile_schema(schema_values).schema,
            }
        )
        return self.async_show_form(
            step_id="init", data_schema=schema, errors=errors
        )

    async def async_step_custom(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit custom clothing temperature thresholds."""
        current = DEFAULTS | self.config_entry.data | self.config_entry.options
        errors: dict[str, str] = {}
        if user_input is not None:
            if not _valid_thresholds(user_input):
                errors["base"] = "invalid_threshold_order"
            else:
                self._data.update(user_input)
                return self.async_create_entry(data=self._data)

        return self.async_show_form(
            step_id="custom",
            data_schema=_threshold_schema(current | self._data | (user_input or {})),
            errors=errors,
        )


def _default_thresholds() -> dict[str, Any]:
    """Return a fresh copy of the normal profile's base thresholds."""
    return {
        key: DEFAULTS[key]
        for key in (
            CONF_SHORTS_THRESHOLD,
            CONF_SWEATER_THRESHOLD,
            CONF_LIGHT_JACKET_THRESHOLD,
            CONF_HEAVY_JACKET_THRESHOLD,
        )
    }
