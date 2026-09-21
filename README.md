# HA Clothing Advisor

A provider-independent Home Assistant custom integration that combines current
conditions and forecasts from any compatible `weather.*` entity into a useful,
layer-aware clothing recommendation.

## Installation with HACS

1. Open HACS in Home Assistant.
2. Select **Integrations**, open the menu, and choose **Custom repositories**.
3. Add `https://github.com/isimagan/HA-Clothing-Advisor` as an **Integration**.
4. Install **HA Clothing Advisor** and restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and search for
   **HA Clothing Advisor**.

The setup wizard guides you through three steps:

1. Select a `weather.*` entity.
2. Review a compatibility report for temperature, forecast, apparent
   temperature, wind, precipitation, gusts, and UV data.
3. Choose a temperature profile. Selecting **Custom** opens a separate page
   where each clothing threshold can be adjusted.

The selected entity must provide a current temperature and at least one
supported forecast type. Hourly forecasts give the best results; twice-daily
and daily forecasts are supported with reduced precision.

## Dashboard card

The integration bundles a compact dashboard card and registers it automatically.
After restarting Home Assistant, add a manual card with:

```yaml
type: custom:clothing-advisor-card
entity: sensor.clothing_recommendation
```

The card is also available in the dashboard card picker. It shows the current
recommendation, feels-like temperature, clothing layers, and forecast range.
Select **See why** to open a mobile-friendly detail view with the explanation
and weather factors used by the recommendation. The card follows the active
Home Assistant theme and supports English and Norwegian.

The integration creates a **Look ahead / Se fremover** select entity with 2,
4, 6, 8, 12, 16, and 24-hour choices. It defaults to 4 hours and can be changed
for the day at any time. The same selector is available directly in the card's
**See why** detail view, and changing it immediately recalculates the advice.

## Recommendation sensor

The integration creates one **Clothing recommendation** sensor. A typical state
is displayed in the user's selected Home Assistant language:

```text
Trousers · T-shirt · Light jacket
```

The sensor exposes structured attributes for dashboards and automations. Their
raw values are stable identifiers such as `trousers` and `light_jacket`; Home
Assistant translates them for display:

- `bottom`, `base_layer`, `mid_layer`, and `outerwear`
- `top`, retained as a combined compatibility value
- `umbrella`, `rain`, and a human-readable `reason`
- current and apparent temperature
- lowest and highest apparent temperature in the selected period
- highest precipitation probability and maximum wind speed
- forecast type and forecast period

The sensor is attached to a **Clothing Advisor** device, so it can be opened
from the integration's device page. Raw attributes are also available under
**Developer tools → States**, or in templates such as:

```jinja2
{{ state_attr('sensor.clothing_recommendation', 'outerwear') }}
{{ state_attr('sensor.clothing_recommendation', 'reason') }}
```

The recommendation engine uses apparent temperature when available and falls
back to regular temperature. A T-shirt is the base layer, while a sweater is an
optional mid-layer. Outerwear is selected independently as no jacket, vest,
light jacket, jacket, winter jacket, or rain jacket. In dry, calm weather, a
vest can replace a light jacket over the sweater; a vest is never recommended
without a sweater or together with a jacket. An umbrella is a separate yes/no
recommendation. Warm rain can therefore result in a T-shirt and umbrella with
no jacket, while cool rain replaces a light jacket or jacket with a rain jacket.
The engine selects removable layers for temperature changes and then adjusts
outerwear for wind and rain.

English and Norwegian translations are included for the complete recommendation,
individual clothing attributes, forecast type, and the human-readable reason.

## Personalization

The default settings are:

| Setting | Default |
|---|---:|
| Temperature profile | Normal |
| Shorts threshold | 18 °C |
| Sweater threshold | 12 °C |
| Light jacket threshold | 15 °C |
| Jacket threshold | 10 °C |
| Winter jacket threshold | 6 °C |
| Look-ahead period | 4 hours |

The **I get cold easily** profile shifts clothing thresholds 2 °C warmer. The
**I get warm easily** profile shifts them 2 °C cooler. **Custom** uses the exact
thresholds entered on the following page. All settings, including the weather
entity, can be changed later from the integration's **Configure** dialog without
removing and re-adding it. The look-ahead period is changed through its select
entity or the card detail view rather than the configuration dialog.

## Manual installation

Copy `custom_components/clothing_advisor` into the `custom_components`
directory in your Home Assistant configuration, restart Home Assistant, and
add the integration from **Settings → Devices & services**.

## Development

The repository is checked by both HACS validation and Hassfest on every push,
pull request, and on a daily schedule.

## License

MIT
