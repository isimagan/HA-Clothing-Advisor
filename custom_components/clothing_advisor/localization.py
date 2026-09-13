"""Localization helpers for clothing recommendations."""

from __future__ import annotations

from .const import DOMAIN
from .recommendation import ClothingRecommendation


def localized_reason(
    recommendation: ClothingRecommendation, translations: dict[str, str]
) -> str:
    """Build a localized human-readable explanation."""
    prefix = f"component.{DOMAIN}.common.reason_"

    def translated(key: str, fallback: str) -> str:
        return translations.get(f"{prefix}{key}", fallback)

    parts = [
        translated("current", "Feels like {temperature} °C now").format(
            temperature=f"{recommendation.apparent_temperature:.1f}"
        )
    ]
    if (
        recommendation.highest_apparent_temperature
        - recommendation.apparent_temperature
        >= 4
    ):
        parts.append(
            translated("warming", "Warming to about {temperature} °C").format(
                temperature=f"{recommendation.highest_apparent_temperature:.1f}"
            )
        )
    elif (
        recommendation.apparent_temperature
        - recommendation.lowest_apparent_temperature
        >= 4
    ):
        parts.append(
            translated("cooling", "Cooling to about {temperature} °C").format(
                temperature=f"{recommendation.lowest_apparent_temperature:.1f}"
            )
        )
    if (
        recommendation.max_wind_speed is not None
        and recommendation.max_wind_speed > 8
    ):
        parts.append(translated("wind", "Wind makes an extra layer useful"))
    if recommendation.rain:
        parts.append(translated("rain", "Rain is possible"))
    return ". ".join(parts) + "."
