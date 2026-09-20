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
        clothing_advisor_id: "entry-1",
      },
    },
    "select.clothing_advisor_look_ahead": {
      entity_id: "select.clothing_advisor_look_ahead",
      state: "4",
      attributes: {
        clothing_advisor_id: "entry-1",
        options: ["2", "4", "6", "8", "12", "16", "24"],
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

const detailListeners = new Map();
let serviceCall;
card.shadowRoot.querySelector = (selector) => ({
  addEventListener: (type, handler) =>
    detailListeners.set(`${selector}:${type}`, handler),
});
card._detailsOpen = true;
card.hass = {
  ...card._hass,
  callService: (domain, service, data) => {
    serviceCall = { domain, service, data };
    return Promise.resolve();
  },
};
if (!card.shadowRoot.innerHTML.includes("Se fremover") ||
    !card.shadowRoot.innerHTML.includes('<option value="24">24 timer</option>')) {
  throw new Error("Look-ahead selector did not render in the detail view");
}
detailListeners.get(".horizon-select:change")({
  currentTarget: {
    disabled: false,
    dataset: { entityId: "select.clothing_advisor_look_ahead" },
    value: "12",
  },
});
if (serviceCall?.domain !== "select" ||
    serviceCall?.service !== "select_option" ||
    serviceCall?.data.option !== "12") {
  throw new Error("Look-ahead selector did not call the select entity");
}
card._detailsOpen = false;

const vestState = {
  ...card._hass.states["sensor.clothing_recommendation"],
  state: "trousers_t_shirt_sweater_vest",
  attributes: {
    ...card._hass.states["sensor.clothing_recommendation"].attributes,
    mid_layer: "sweater",
    top: "t_shirt_sweater",
    outerwear: "vest",
  },
};
card.hass = {
  ...card._hass,
  states: { "sensor.clothing_recommendation": vestState },
  formatEntityAttributeValue: (_state, attribute) => ({
    bottom: "Bukse",
    top: "T-skjorte + genser",
    outerwear: "Vest",
    forecast_type: "Hver time",
  })[attribute],
};
if (!card.shadowRoot.innerHTML.includes("T-skjorte + genser og vest")) {
  throw new Error("Vest recommendation did not render");
}
if (!/\.garment \{[^}]*background: #fff; color: #17212b;/s.test(card.shadowRoot.innerHTML) ||
    !/\.layer \{[^}]*background: #fff; color: #17212b;/s.test(card.shadowRoot.innerHTML) ||
    !/\.metric \{[^}]*background: #fff; color: #17212b;/s.test(card.shadowRoot.innerHTML)) {
  throw new Error("White boxes need dark text in dark themes");
}

console.log("Frontend card registration, localization, and detail view passed");
