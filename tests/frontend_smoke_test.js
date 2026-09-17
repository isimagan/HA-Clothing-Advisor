const fs = require("fs");
const vm = require("vm");

const registry = new Map();

class HTMLElement {
  attachShadow() {
    this.shadowRoot = { innerHTML: "", querySelector: () => null };
  }
}

const context = {
  console,
  HTMLElement,
  Intl,
  window: {},
  customElements: {
    define: (name, klass) => registry.set(name, klass),
    get: (name) => registry.get(name),
  },
};

vm.createContext(context);
vm.runInContext(
  fs.readFileSync(
    "custom_components/clothing_advisor/frontend/clothing-advisor-card.js",
    "utf8",
  ),
  context,
);

const Card = registry.get("clothing-advisor-card");
if (!Card) throw new Error("Card was not registered");

const card = new Card();
card.setConfig({ entity: "sensor.clothing_recommendation" });
card.hass = {
  locale: { language: "nb" },
  states: {
    "sensor.clothing_recommendation": {
      entity_id: "sensor.clothing_recommendation",
      state: "trousers_t_shirt_light_jacket",
      attributes: {
        bottom: "trousers",
        top: "t_shirt",
        base_layer: "t_shirt",
        outerwear: "light_jacket",
        reason: "Føles som 14 °C nå.",
        apparent_temperature: 14,
        lowest_apparent_temperature: 12,
        highest_apparent_temperature: 16,
        forecast_hours: 4,
        forecast_type: "hourly",
        highest_precipitation_probability: 10,
        max_wind_speed: 3,
      },
    },
  },
  formatEntityAttributeValue: (_state, attribute) =>
    ({
      bottom: "Bukse",
      top: "T-skjorte",
      outerwear: "Tynn jakke",
      forecast_type: "Hver time",
    })[attribute],
  formatEntityState: () => "Bukse · T-skjorte · Tynn jakke",
};

if (!card.shadowRoot.innerHTML.includes("T-skjorte og tynn jakke")) {
  throw new Error("Norwegian recommendation did not render");
}
if (context.window.customCards.length !== 1) {
  throw new Error("Card picker registration failed");
}

const Badge = registry.get("clothing-advisor-badge");
if (!Badge || context.window.customBadges.length !== 1) {
  throw new Error("Badge picker registration failed");
}

const badge = new Badge();
const listeners = new Map();
badge.shadowRoot.querySelector = (selector) => ({
  addEventListener: (type, handler) => listeners.set(`${selector}:${type}`, handler),
});
badge.setConfig({ entity: "sensor.clothing_recommendation" });
badge.hass = card._hass;
if (!badge.shadowRoot.innerHTML.includes('<ha-badge type="button" label="Klesråd"')) {
  throw new Error("Translated badge label or ha-badge wrapper missing");
}
if (!badge.shadowRoot.innerHTML.includes('icon="mdi:tshirt-crew"')) {
  throw new Error("T-shirt icon missing");
}
listeners.get("ha-badge:click")();
if (!badge.shadowRoot.innerHTML.includes('role="dialog"') ||
    !badge.shadowRoot.innerHTML.includes("Føles som 14 °C nå.")) {
  throw new Error("Badge did not open the shared detail view");
}
listeners.get(".close:click")();
if (badge.shadowRoot.innerHTML.includes('role="dialog"')) {
  throw new Error("Badge detail view did not close");
}
let prevented = false;
listeners.get("ha-badge:keydown")({
  key: "Enter",
  preventDefault: () => { prevented = true; },
});
if (!prevented || !badge.shadowRoot.innerHTML.includes('role="dialog"')) {
  throw new Error("Badge keyboard activation failed");
}
listeners.get(".close:click")();
badge.hass = { ...card._hass, locale: { language: "en" } };
if (!badge.shadowRoot.innerHTML.includes('label="Clothing advice"')) {
  throw new Error("English badge label did not render");
}

console.log("Frontend card and badge registration, localization, and detail view passed");
