"""Tests for the pure clothing recommendation engine."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest


ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components" / "clothing_advisor"
PACKAGE_NAME = "custom_components.clothing_advisor"

package = ModuleType(PACKAGE_NAME)
package.__path__ = [str(PACKAGE_PATH)]
sys.modules.setdefault(PACKAGE_NAME, package)


def _load(name: str):
    """Load a module without importing the Home Assistant package initializer."""
    full_name = f"{PACKAGE_NAME}.{name}"
    spec = importlib.util.spec_from_file_location(
        full_name, PACKAGE_PATH / f"{name}.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


const = _load("const")
recommendation = _load("recommendation")
localization = _load("localization")

NOW = datetime(2026, 9, 13, 8, tzinfo=timezone.utc)
DEFAULT_SETTINGS = dict(const.DEFAULTS)


def snapshot(
    temperature: float,
    forecasts: list[dict],
    *,
    condition: str = "sunny",
    wind_speed: float | None = None,
):
    """Create a weather snapshot for a test."""
    return recommendation.WeatherSnapshot(
        temperature=temperature,
        apparent_temperature=None,
        condition=condition,
        wind_speed=wind_speed,
        wind_gust_speed=None,
        forecast_type="hourly",
        forecast=forecasts,
    )


class RecommendationTests(unittest.TestCase):
    """Verify the layer-aware decision rules."""

    def test_warming_day_uses_removable_layer(self) -> None:
        """A cold morning that warms up uses a light removable jacket."""
        result = recommendation.build_recommendation(
            snapshot(
                12,
                [
                    {"datetime": "2026-09-13T10:00:00+00:00", "temperature": 17},
                    {"datetime": "2026-09-13T12:00:00+00:00", "temperature": 21},
                ],
            ),
            DEFAULT_SETTINGS,
            NOW,
        )
        self.assertEqual(result.state, "trousers_t_shirt_light_jacket")
        self.assertIn("warming", result.reason)

    def test_falling_temperature_keeps_current_base_layer(self) -> None:
        """A warm start with a cooler forecast adds outerwear."""
        result = recommendation.build_recommendation(
            snapshot(
                20,
                [
                    {"datetime": "2026-09-13T12:00:00+00:00", "temperature": 14}
                ],
            ),
            DEFAULT_SETTINGS,
            NOW,
        )
        self.assertEqual(result.state, "shorts_t_shirt_light_jacket")
        self.assertIn("cooling", result.reason)

    def test_rain_changes_outerwear(self) -> None:
        """Likely rain promotes rainproof outerwear."""
        result = recommendation.build_recommendation(
            snapshot(
                21,
                [
                    {
                        "datetime": "2026-09-13T10:00:00+00:00",
                        "temperature": 20,
                        "precipitation_probability": 70,
                    }
                ],
            ),
            DEFAULT_SETTINGS,
            NOW,
        )
        self.assertEqual(result.outerwear, "rain_jacket")
        self.assertTrue(result.rain)

    def test_sweater_is_an_optional_mid_layer(self) -> None:
        """Cold steady weather adds a sweater between T-shirt and jacket."""
        result = recommendation.build_recommendation(
            snapshot(
                12,
                [
                    {"datetime": "2026-09-13T10:00:00+00:00", "temperature": 12}
                ],
            ),
            DEFAULT_SETTINGS,
            NOW,
        )
        self.assertEqual(result.base_layer, "t_shirt")
        self.assertEqual(result.mid_layer, "sweater")
        self.assertEqual(result.top, "t_shirt_sweater")
        self.assertEqual(
            result.state, "trousers_t_shirt_sweater_light_jacket"
        )

    def test_jacket_does_not_require_sweater(self) -> None:
        """Mild weather can recommend a T-shirt and jacket without a sweater."""
        result = recommendation.build_recommendation(
            snapshot(
                14,
                [
                    {"datetime": "2026-09-13T10:00:00+00:00", "temperature": 14}
                ],
            ),
            DEFAULT_SETTINGS,
            NOW,
        )
        self.assertIsNone(result.mid_layer)
        self.assertEqual(result.state, "trousers_t_shirt_light_jacket")

    def test_profiles_shift_thresholds(self) -> None:
        """Cold and warm profiles shift the shorts threshold by two degrees."""
        weather = snapshot(
            17,
            [{"datetime": "2026-09-13T10:00:00+00:00", "temperature": 17}],
        )
        cold = DEFAULT_SETTINGS | {const.CONF_PROFILE: const.PROFILE_COLD}
        warm = DEFAULT_SETTINGS | {const.CONF_PROFILE: const.PROFILE_WARM}
        self.assertEqual(
            recommendation.build_recommendation(weather, cold, NOW).bottom,
            "trousers",
        )
        self.assertEqual(
            recommendation.build_recommendation(weather, warm, NOW).bottom,
            "shorts",
        )

    def test_custom_profile_uses_exact_thresholds(self) -> None:
        """The custom profile does not add a profile temperature adjustment."""
        weather = snapshot(
            17,
            [{"datetime": "2026-09-13T10:00:00+00:00", "temperature": 17}],
        )
        custom = DEFAULT_SETTINGS | {
            const.CONF_PROFILE: const.PROFILE_CUSTOM,
            const.CONF_SHORTS_THRESHOLD: 17,
        }
        self.assertEqual(
            recommendation.build_recommendation(weather, custom, NOW).bottom,
            "shorts",
        )

    def test_reason_uses_norwegian_translation_templates(self) -> None:
        """The human-readable reason is built from translated templates."""
        result = recommendation.build_recommendation(
            snapshot(
                12,
                [
                    {"datetime": "2026-09-13T10:00:00+00:00", "temperature": 17}
                ],
                wind_speed=9,
            ),
            DEFAULT_SETTINGS,
            NOW,
        )
        prefix = "component.clothing_advisor.common.reason_"
        translations = {
            f"{prefix}current": "Føles som {temperature} °C nå",
            f"{prefix}warming": "Blir varmere til {temperature} °C",
            f"{prefix}wind": "Vinden gjør et ekstra lag nyttig",
        }
        self.assertEqual(
            localization.localized_reason(result, translations),
            "Føles som 12.0 °C nå. Blir varmere til 17.0 °C. "
            "Vinden gjør et ekstra lag nyttig.",
        )


if __name__ == "__main__":
    unittest.main()
