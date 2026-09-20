"""Constants for HA Clothing Advisor."""

DOMAIN = "clothing_advisor"

CONF_WEATHER_ENTITY = "weather_entity"
CONF_PROFILE = "profile"
CONF_SHORTS_THRESHOLD = "shorts_threshold"
CONF_SWEATER_THRESHOLD = "sweater_threshold"
CONF_LIGHT_JACKET_THRESHOLD = "light_jacket_threshold"
CONF_HEAVY_JACKET_THRESHOLD = "heavy_jacket_threshold"
CONF_FORECAST_HOURS = "forecast_hours"
FORECAST_HOUR_OPTIONS = (2, 4, 6, 8, 12, 16, 24)

PROFILE_COLD = "cold"
PROFILE_CUSTOM = "custom"
PROFILE_NORMAL = "normal"
PROFILE_WARM = "warm"

DEFAULTS = {
    CONF_PROFILE: PROFILE_NORMAL,
    CONF_SHORTS_THRESHOLD: 18,
    CONF_SWEATER_THRESHOLD: 12,
    CONF_LIGHT_JACKET_THRESHOLD: 15,
    CONF_HEAVY_JACKET_THRESHOLD: 6,
    CONF_FORECAST_HOURS: 4,
}
