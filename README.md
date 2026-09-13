# HA Clothing Advisor

A Home Assistant custom integration that turns the current conditions from a
weather entity into a short clothing recommendation.

## Installation with HACS

1. Open HACS in Home Assistant.
2. Select **Integrations**, open the menu, and choose **Custom repositories**.
3. Add `https://github.com/isimagan/HA-Clothing-Advisor` as an **Integration**.
4. Install **HA Clothing Advisor** and restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration**, search for
   **HA Clothing Advisor**, and select the weather entity to use.

The integration creates a sensor named **Clothing recommendation**. Its state
contains a concise recommendation; the source entity, temperature, and weather
condition are exposed as attributes.

## Manual installation

Copy `custom_components/clothing_advisor` into the `custom_components`
directory in your Home Assistant configuration, restart Home Assistant, and
add the integration from **Settings → Devices & services**.

## Development

The repository is checked by both HACS validation and Hassfest on every push,
pull request, and on a daily schedule.

## License

MIT
