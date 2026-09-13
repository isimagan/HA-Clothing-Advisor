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
3. Choose a temperature profile and optionally adjust the clothing thresholds
   and forecast period.

The selected entity must provide a current temperature and at least one
supported forecast type. Hourly forecasts give the best results; twice-daily
and daily forecasts are supported with reduced precision.

## Recommendation sensor

The integration creates one **Clothing recommendation** sensor. A typical state
looks like:

```text
Trousers · T-shirt · Light jacket
```

The sensor exposes structured attributes for dashboards and automations:

- `bottom`, `top`, and `outerwear`
- `rain` and a human-readable `reason`
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
back to regular temperature. It selects base layers for the current and warmer
parts of the period, outerwear for the coldest part, and then adjusts for wind
and rain.

## Personalization

The default settings are:

| Setting | Default |
|---|---:|
| Temperature profile | Normal |
| Shorts threshold | 18 °C |
| Sweater threshold | 12 °C |
| Light jacket threshold | 15 °C |
| Thick jacket threshold | 6 °C |
| Forecast period | 4 hours |

The **I get cold easily** profile shifts clothing thresholds 2 °C warmer. The
**I get warm easily** profile shifts them 2 °C cooler. All settings, including
the weather entity, can be changed later from the integration's **Configure**
dialog without removing and re-adding it.

## Manual installation

Copy `custom_components/clothing_advisor` into the `custom_components`
directory in your Home Assistant configuration, restart Home Assistant, and
add the integration from **Settings → Devices & services**.

## Development

The repository is checked by both HACS validation and Hassfest on every push,
pull request, and on a daily schedule.

## License

MIT
