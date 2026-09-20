"""Tests for the forecast horizon select entity."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


ROOT = Path(__file__).parents[1]
PACKAGE_PATH = ROOT / "custom_components" / "clothing_advisor"
PACKAGE_NAME = "custom_components.clothing_advisor"


class _SelectEntity:
    """Minimal SelectEntity test double."""

    @property
    def options(self):
        return self._attr_options


class _CoordinatorEntity:
    """Minimal CoordinatorEntity test double."""

    def __class_getitem__(cls, _item):
        return cls

    def __init__(self, coordinator) -> None:
        self.coordinator = coordinator


class _DeviceInfo(dict):
    """Minimal DeviceInfo test double."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


def _module(name: str, **attributes) -> ModuleType:
    """Create and register a module test double."""
    module = ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


package = sys.modules.get(PACKAGE_NAME) or ModuleType(PACKAGE_NAME)
package.__path__ = [str(PACKAGE_PATH)]
package.ClothingAdvisorConfigEntry = object
sys.modules[PACKAGE_NAME] = package

_module("homeassistant")
_module("homeassistant.components")
_module("homeassistant.components.select", SelectEntity=_SelectEntity)
_module("homeassistant.core", HomeAssistant=object)
_module("homeassistant.helpers")
_module("homeassistant.helpers.device_registry", DeviceInfo=_DeviceInfo)
_module(
    "homeassistant.helpers.entity_platform",
    AddConfigEntryEntitiesCallback=object,
)
_module(
    "homeassistant.helpers.update_coordinator",
    CoordinatorEntity=_CoordinatorEntity,
)
_module(
    f"{PACKAGE_NAME}.coordinator",
    ClothingAdvisorCoordinator=object,
)


def _load(name: str):
    """Load an integration module with the Home Assistant test doubles."""
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
select_platform = _load("select")


class _ConfigEntries:
    def __init__(self) -> None:
        self.updated_options = None

    def async_update_entry(self, entry, *, options) -> None:
        self.updated_options = options
        entry.options = options


class ForecastHoursSelectTests(unittest.IsolatedAsyncioTestCase):
    """Verify persistence and validation of the look-ahead period."""

    def _entity(self, *, data=None, options=None):
        entry = SimpleNamespace(
            entry_id="entry-1",
            data=data or {},
            options=options or {},
        )
        coordinator = SimpleNamespace(config_entry=entry)
        entity = select_platform.ClothingAdvisorForecastHoursSelect(coordinator)
        entity.hass = SimpleNamespace(config_entries=_ConfigEntries())
        return entity, entry

    def test_default_and_legacy_options_are_available(self) -> None:
        """New installs default to four hours and legacy six-hour values survive."""
        entity, _entry = self._entity()
        self.assertEqual(entity.current_option, "4")
        self.assertEqual(entity.options, ["2", "4", "6", "8", "12", "16", "24"])

        entity, _entry = self._entity(data={const.CONF_FORECAST_HOURS: 6})
        self.assertEqual(entity.current_option, "6")

    def test_options_have_english_and_norwegian_translations(self) -> None:
        """Every select option has an entity-state translation."""
        for filename in (
            "strings.json",
            "translations/en.json",
            "translations/nb.json",
        ):
            with self.subTest(filename=filename):
                translations = json.loads((PACKAGE_PATH / filename).read_text())
                states = translations["entity"]["select"]["forecast_hours"][
                    "state"
                ]
                self.assertEqual(set(states), set(self._entity()[0].options))

    async def test_selecting_horizon_updates_config_entry_options(self) -> None:
        """A selection persists as an integer config-entry option."""
        entity, entry = self._entity(options={"another_option": True})
        await entity.async_select_option("16")
        self.assertEqual(
            entry.options,
            {"another_option": True, const.CONF_FORECAST_HOURS: 16},
        )

    async def test_invalid_horizon_is_rejected(self) -> None:
        """Only published select options can be persisted."""
        entity, _entry = self._entity()
        with self.assertRaises(ValueError):
            await entity.async_select_option("10")
