const CARD_TAG = "clothing-advisor-card";

const TEXT = {
  en: {
    title: "Clothing advice",
    period: "Next {hours} hours",
    feelsLike: "feels like",
    seeWhy: "See why",
    recommendation: "Clothing recommendation",
    updated: "Updated now",
    outfit: "Your outfit",
    recommended: "Recommended",
    normalProfile: "Clothing layers",
    why: "Why this?",
    lookAhead: "Look ahead",
    hourOption: "{hours} hours",
    forecast: "Weather ahead",
    hours: "{hours} hours",
    lowest: "Lowest",
    highest: "Highest",
    wind: "Wind",
    rain: "Rain",
    source: "Calculated from {type} forecast",
    close: "Close",
    missing: "Entity not found",
    configure: "Select a Clothing Advisor sensor in the card settings.",
    and: "and",
    bottom: "Bottom",
    top: "Top layers",
    outerwear: "Outerwear",
    noData: "Not available",
  },
  nb: {
    title: "Klesråd",
    period: "De neste {hours} timene",
    feelsLike: "føles som",
    seeWhy: "Se hvorfor",
    recommendation: "Klesanbefaling",
    updated: "Oppdatert nå",
    outfit: "Antrekket ditt",
    recommended: "Anbefalt",
    normalProfile: "Kleslag",
    why: "Hvorfor dette?",
    lookAhead: "Se fremover",
    hourOption: "{hours} timer",
    forecast: "Været fremover",
    hours: "{hours} timer",
    lowest: "Laveste",
    highest: "Høyeste",
    wind: "Vind",
    rain: "Regn",
    source: "Beregnet fra {type} prognose",
    close: "Lukk",
    missing: "Fant ikke entiteten",
    configure: "Velg en Clothing Advisor-sensor i kortinnstillingene.",
    and: "og",
    bottom: "Underlag",
    top: "Overdeler",
    outerwear: "Ytterlag",
    noData: "Ikke tilgjengelig",
  },
};

const VALUE_FALLBACKS = {
  en: {
    shorts: "Shorts",
    trousers: "Trousers",
    t_shirt: "T-shirt",
    sweater: "Sweater",
    t_shirt_sweater: "T-shirt + sweater",
    no_jacket: "No jacket",
    vest: "Vest",
    light_jacket: "Light jacket",
    thick_jacket: "Thick jacket",
    rain_jacket: "Rain jacket",
    thick_waterproof_jacket: "Thick waterproof jacket",
    hourly: "hourly",
    twice_daily: "twice-daily",
    daily: "daily",
  },
  nb: {
    shorts: "Shorts",
    trousers: "Bukse",
    t_shirt: "T-skjorte",
    sweater: "Genser",
    t_shirt_sweater: "T-skjorte + genser",
    no_jacket: "Ingen jakke",
    vest: "Vest",
    light_jacket: "Tynn jakke",
    thick_jacket: "Tykk jakke",
    rain_jacket: "Regnjakke",
    thick_waterproof_jacket: "Tykk vanntett jakke",
    hourly: "timebasert",
    twice_daily: "halvdøgns",
    daily: "daglig",
  },
};

const ICONS = {
  weather: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 4.5V2.8M20.7 6.3l1.2-1.2M18 11h2.2M11.3 6.3 10 5.1"/><path d="M14.4 7.1A4.7 4.7 0 0 1 20 12"/><path d="M6.7 18.7h10.1a3.7 3.7 0 0 0 .4-7.4A5.7 5.7 0 0 0 6.4 9.9a4.4 4.4 0 0 0 .3 8.8Z"/></svg>`,
  shirt: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 4-5 3 2 4 3-1v10h8V10l3 1 2-4-5-3c-.6 1.4-2 2-4 2S8.6 5.4 8 4Z"/></svg>`,
  jacket: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 4-4 2-2 8 3 1 1-4v9h10v-9l1 4 3-1-2-8-4-2c-.4 1.2-1.4 2-3 2s-2.6-.8-3-2Z"/><path d="M12 6v14M9.5 10 12 7.5l2.5 2.5M9 15h2M13 15h2"/></svg>`,
  vest: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 3-3 2-2 8 3 1 1-4v10h10V10l1 4 3-1-2-8-3-2-2 3h-4L8 3Z"/><path d="M12 6v14M8 3l4 7 4-7M9 15h2M13 15h2"/></svg>`,
  trousers: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h10l1 17h-5l-1-10-1 10H6L7 3Z"/><path d="M7 7h10M12 3v7"/></svg>`,
  clock: `<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.2 2"/></svg>`,
  close: `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>`,
};

const STYLE = `
  :host {
    display: block;
    --ca-blue: var(--primary-color, #0788df);
    --ca-soft: color-mix(in srgb, var(--ca-blue) 11%, transparent);
    --ca-text: var(--primary-text-color, #17212b);
    --ca-muted: var(--secondary-text-color, #65727e);
    --ca-line: var(--divider-color, rgba(23, 33, 43, .09));
    color: var(--ca-text);
  }
  * { box-sizing: border-box; }
  button { color: inherit; font: inherit; }
  svg {
    display: block; width: 100%; height: 100%; fill: none; stroke: currentColor;
    stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.8;
  }
  ha-card {
    overflow: hidden; padding: 16px; cursor: default;
    background: var(--ha-card-background, var(--card-background-color, #fff));
  }
  .head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
  .identity { display: flex; align-items: center; min-width: 0; gap: 10px; }
  .weather-icon, .layer-icon {
    display: grid; place-items: center; flex: 0 0 auto; background: var(--ca-soft);
    color: var(--ca-blue);
  }
  .weather-icon { width: 34px; height: 34px; padding: 6px; border-radius: 12px; }
  .title { margin: 0; font-size: 15px; font-weight: 700; }
  .subtitle { margin: 2px 0 0; color: var(--ca-muted); font-size: 11px; }
  .temperature { flex: 0 0 auto; text-align: right; }
  .temperature strong { display: block; font-size: 22px; line-height: 1; letter-spacing: -.04em; }
  .temperature span { color: var(--ca-muted); font-size: 10px; }
  .recommendation { margin: 15px 0 12px; }
  .recommendation h2 { margin: 0; font-size: 21px; line-height: 1.14; letter-spacing: -.035em; }
  .recommendation p {
    display: -webkit-box; margin: 5px 0 0; overflow: hidden; color: var(--ca-muted);
    font-size: 12px; line-height: 1.4; -webkit-box-orient: vertical; -webkit-line-clamp: 2;
  }
  .garments { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }
  .garment {
    display: flex; min-width: 0; min-height: 38px; align-items: center; padding: 8px;
    gap: 6px; border: 1px solid var(--ca-line); border-radius: 12px;
    background: #fff; color: #17212b;
  }
  .garment .icon { width: 17px; height: 17px; flex: 0 0 auto; color: var(--ca-blue); }
  .garment strong { overflow: hidden; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
  .footer {
    display: flex; align-items: center; justify-content: space-between; margin-top: 12px;
    padding-top: 12px; border-top: 1px solid var(--ca-line);
  }
  .range { display: flex; align-items: center; gap: 6px; color: var(--ca-muted); font-size: 11px; }
  .range .icon { width: 14px; height: 14px; }
  .more, .close {
    border: 0; background: var(--ca-soft); color: var(--ca-blue); cursor: pointer;
  }
  .more { padding: 7px 11px; border-radius: 10px; font-size: 11px; font-weight: 700; }
  .overlay {
    position: fixed; z-index: 9999; inset: 0; display: grid; align-items: end;
    justify-items: center; padding: 8px; background: rgba(4, 12, 18, .56);
    backdrop-filter: blur(7px);
  }
  .sheet {
    width: min(430px, 100%); max-height: calc(100dvh - 16px); overflow: auto;
    border-radius: 24px; background: var(--ha-card-background, var(--card-background-color, #fff));
    box-shadow: 0 24px 80px rgba(0, 0, 0, .34); animation: enter 180ms ease-out;
  }
  @keyframes enter { from { opacity: 0; transform: translateY(18px); } }
  .hero {
    position: relative; padding: 18px 20px 20px; overflow: hidden;
    background: linear-gradient(135deg, var(--ca-soft), color-mix(in srgb, #04c6ce 8%, transparent));
  }
  .detail-head, .hero-main, .section-head, .forecast-summary {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
  }
  .kicker { margin: 0 0 3px; color: var(--ca-muted); font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .09em; }
  .status-dot { display: inline-block; width: 6px; height: 6px; margin-right: 6px; border-radius: 50%; background: #25b875; }
  .close { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 50%; }
  .close svg { width: 18px; height: 18px; }
  .hero-main { margin-top: 16px; }
  .hero-main h2 { max-width: 290px; margin: 0; font-size: 27px; line-height: 1.07; letter-spacing: -.045em; }
  .hero-temp { flex: 0 0 auto; text-align: right; }
  .hero-temp strong { display: block; font-size: 31px; line-height: 1; letter-spacing: -.05em; }
  .hero-temp span { color: var(--ca-muted); font-size: 10px; }
  .detail-section { padding: 17px 20px 19px; }
  .section-head { margin-bottom: 12px; }
  .section-head h3 { margin: 0; font-size: 13px; }
  .profile { padding: 4px 8px; border-radius: 999px; background: var(--ca-soft); color: var(--ca-blue); font-size: 9px; font-weight: 700; }
  .layer-list { display: grid; gap: 6px; }
  .layer {
    display: grid; grid-template-columns: 32px 1fr auto; align-items: center; gap: 10px;
    padding: 8px 10px; border: 1px solid var(--ca-line); border-radius: 13px;
    background: #fff; color: #17212b;
  }
  .layer-icon { width: 32px; height: 32px; padding: 7px; border-radius: 11px; }
  .layer strong, .layer span { display: block; }
  .layer strong { font-size: 12px; }
  .layer span { color: #65727e; font-size: 10px; }
  .recommended { color: #1e9b65 !important; font-size: 9px !important; font-weight: 700; }
  .reason { margin-top: 12px; padding: 11px 12px; border-radius: 13px; background: var(--ca-soft); }
  .reason strong { display: block; margin-bottom: 4px; color: var(--ca-blue); font-size: 9px; text-transform: uppercase; letter-spacing: .06em; }
  .reason p { margin: 0; font-size: 11px; line-height: 1.5; }
  .horizon-control {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    margin-top: 8px; padding: 9px 12px; border: 1px solid var(--ca-line);
    border-radius: 13px; background: #fff; color: #17212b;
  }
  .horizon-control label { font-size: 11px; font-weight: 700; }
  .horizon-select {
    min-width: 96px; padding: 6px 28px 6px 9px; border: 1px solid rgba(23, 33, 43, .16);
    border-radius: 9px; background: #fff; color: #17212b; font: inherit; font-size: 11px;
  }
  .horizon-select:disabled { opacity: .6; }
  details { border-top: 1px solid var(--ca-line); }
  summary { padding: 14px 20px; list-style: none; cursor: pointer; }
  summary::-webkit-details-marker { display: none; }
  .forecast-summary strong, .forecast-summary small { display: block; }
  .forecast-summary strong { font-size: 12px; }
  .forecast-summary small { margin-top: 2px; color: var(--ca-muted); font-size: 9px; }
  .chevron { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 50%; background: var(--ca-soft); color: var(--ca-blue); transition: transform 160ms ease; }
  details[open] .chevron { transform: rotate(180deg); }
  .metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 7px; padding: 0 20px 16px; }
  .metric { padding: 10px; border: 1px solid var(--ca-line); border-radius: 12px; background: #fff; color: #17212b; }
  .metric span { display: block; margin-bottom: 3px; color: #65727e; font-size: 9px; }
  .metric strong { font-size: 12px; }
  .source { grid-column: 1 / -1; margin: 5px 0 0; color: var(--ca-muted); font-size: 9px; text-align: center; }
  .error { padding: 20px; }
  .error strong { display: block; margin-bottom: 5px; }
  .error span { color: var(--ca-muted); font-size: 12px; }
  @media (min-width: 600px) { .overlay { align-items: center; padding: 24px; } }
`;

class ClothingAdvisorCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = undefined;
    this._hass = undefined;
    this._detailsOpen = false;
  }

  static getConfigForm() {
    return {
      schema: [
        {
          name: "entity",
          required: true,
          selector: { entity: { filter: { domain: "sensor" } } },
        },
        { name: "name", selector: { text: {} } },
      ],
    };
  }

  static getStubConfig(hass) {
    const entity = Object.values(hass.states).find(
      (state) => state.attributes.base_layer && state.attributes.outerwear,
    );
    return entity ? { entity: entity.entity_id } : {};
  }

  setConfig(config) {
    if (!config.entity) throw new Error("An entity is required");
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 3;
  }

  getGridOptions() {
    return { columns: 6, rows: 3, min_columns: 3, min_rows: 2 };
  }

  _language() {
    const language = this._hass?.locale?.language || "en";
    return /^(nb|nn|no)(-|$)/i.test(language) ? "nb" : "en";
  }

  _text() {
    return TEXT[this._language()];
  }

  _format(template, values) {
    return Object.entries(values).reduce(
      (result, [key, value]) => result.replace(`{${key}}`, value),
      template,
    );
  }

  _attribute(stateObj, attribute) {
    const raw = stateObj.attributes[attribute];
    if (raw === null || raw === undefined) return "";
    try {
      const formatted = this._hass.formatEntityAttributeValue(stateObj, attribute);
      if (typeof formatted === "string" && formatted !== String(raw)) return formatted;
    } catch (_error) {
      // Fall through to the bundled value translations.
    }
    return VALUE_FALLBACKS[this._language()][raw] || String(raw);
  }

  _number(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return this._text().noData;
    }
    return new Intl.NumberFormat(this._language() === "nb" ? "nb-NO" : "en", {
      maximumFractionDigits: 1,
    }).format(Number(value));
  }

  _headline(stateObj) {
    const top = this._attribute(stateObj, "top");
    const outerwear = this._attribute(stateObj, "outerwear");
    return stateObj.attributes.outerwear === "no_jacket"
      ? top
      : `${top} ${this._text().and} ${this._lowerFirst(outerwear)}`;
  }

  _lowerFirst(value) {
    if (!value) return value;
    const locale = this._language() === "nb" ? "nb-NO" : "en";
    return value.charAt(0).toLocaleLowerCase(locale) + value.slice(1);
  }

  _layer(icon, name, category) {
    const text = this._text();
    return `<div class="layer">
      <div class="layer-icon">${ICONS[icon]}</div>
      <div><strong>${escapeHtml(name)}</strong><span>${escapeHtml(category)}</span></div>
      <span class="recommended">${escapeHtml(text.recommended)}</span>
    </div>`;
  }

  _garment(icon, name) {
    return `<div class="garment"><span class="icon">${ICONS[icon]}</span><strong>${escapeHtml(name)}</strong></div>`;
  }

  _horizonSelect(stateObj) {
    const advisorId = stateObj.attributes.clothing_advisor_id;
    if (!advisorId) return "";
    const selectState = Object.values(this._hass.states).find(
      (state) => state.entity_id.startsWith("select.") &&
        state.attributes.clothing_advisor_id === advisorId,
    );
    if (!selectState) return "";

    const text = this._text();
    const options = selectState.attributes.options || [
      "2", "4", "6", "8", "12", "16", "24",
    ];
    return `<div class="horizon-control">
      <label for="clothing-advisor-horizon">${escapeHtml(text.lookAhead)}</label>
      <select class="horizon-select" id="clothing-advisor-horizon" data-entity-id="${escapeHtml(selectState.entity_id)}">
        ${options.map((option) => {
          const selected = String(option) === selectState.state ? " selected" : "";
          const label = this._format(text.hourOption, { hours: option });
          return `<option value="${escapeHtml(option)}"${selected}>${escapeHtml(label)}</option>`;
        }).join("")}
      </select>
    </div>`;
  }

  _detail(stateObj, values) {
    const text = this._text();
    const hours = stateObj.attributes.forecast_hours ?? 4;
    const forecastType = this._attribute(stateObj, "forecast_type") || text.noData;
    const precipitation = stateObj.attributes.highest_precipitation_probability;
    const rain = precipitation === null || precipitation === undefined
      ? (stateObj.attributes.rain ? "100 %" : text.noData)
      : `${this._number(precipitation)} %`;
    const wind = stateObj.attributes.max_wind_speed;

    return `<div class="overlay" role="presentation">
      <section class="sheet" role="dialog" aria-modal="true" aria-label="${escapeHtml(text.recommendation)}">
        <header class="hero">
          <div class="detail-head">
            <div><p class="kicker"><span class="status-dot"></span>${escapeHtml(text.updated)}</p><p class="title">${escapeHtml(text.recommendation)}</p></div>
            <button class="close" type="button" aria-label="${escapeHtml(text.close)}">${ICONS.close}</button>
          </div>
          <div class="hero-main">
            <h2>${escapeHtml(values.headline)}</h2>
            <div class="hero-temp"><strong>${escapeHtml(values.temperature)}°</strong><span>${escapeHtml(text.feelsLike)}</span></div>
          </div>
        </header>
        <section class="detail-section">
          <div class="section-head"><h3>${escapeHtml(text.outfit)}</h3><span class="profile">${escapeHtml(text.normalProfile)}</span></div>
          <div class="layer-list">
            ${this._layer("trousers", values.bottom, text.bottom)}
            ${this._layer("shirt", values.top, text.top)}
            ${this._layer(stateObj.attributes.outerwear === "vest" ? "vest" : "jacket", values.outerwear, text.outerwear)}
          </div>
          <div class="reason"><strong>${escapeHtml(text.why)}</strong><p>${escapeHtml(values.reason)}</p></div>
          ${this._horizonSelect(stateObj)}
        </section>
        <details>
          <summary class="forecast-summary">
            <span><strong>${escapeHtml(text.forecast)}</strong><small>${escapeHtml(values.range)} · ${escapeHtml(this._format(text.hours, { hours }))}</small></span>
            <span class="chevron">⌄</span>
          </summary>
          <div class="metrics">
            <div class="metric"><span>${escapeHtml(text.lowest)}</span><strong>${escapeHtml(values.low)} °C</strong></div>
            <div class="metric"><span>${escapeHtml(text.highest)}</span><strong>${escapeHtml(values.high)} °C</strong></div>
            <div class="metric"><span>${escapeHtml(text.wind)}</span><strong>${wind === null || wind === undefined ? escapeHtml(text.noData) : `${escapeHtml(this._number(wind))} m/s`}</strong></div>
            <div class="metric"><span>${escapeHtml(text.rain)}</span><strong>${escapeHtml(rain)}</strong></div>
            <p class="source">${escapeHtml(this._format(text.source, { type: forecastType }))}</p>
          </div>
        </details>
      </section>
    </div>`;
  }

  _values(stateObj) {
    const values = {
      headline: this._headline(stateObj),
      bottom: this._attribute(stateObj, "bottom"),
      top: this._attribute(stateObj, "top"),
      outerwear: this._attribute(stateObj, "outerwear"),
      reason: stateObj.attributes.reason || this._hass.formatEntityState(stateObj),
      temperature: this._number(stateObj.attributes.apparent_temperature),
      low: this._number(stateObj.attributes.lowest_apparent_temperature),
      high: this._number(stateObj.attributes.highest_apparent_temperature),
    };
    values.range = `${values.low}°–${values.high}°`;
    return values;
  }

  _wireDetailEvents() {
    this.shadowRoot.querySelector(".horizon-select")?.addEventListener(
      "change",
      async (event) => {
        const select = event.currentTarget;
        select.disabled = true;
        try {
          await this._hass.callService("select", "select_option", {
            entity_id: select.dataset.entityId,
            option: select.value,
          });
        } finally {
          select.disabled = false;
        }
      },
    );
    this.shadowRoot.querySelector(".close")?.addEventListener("click", () => {
      this._detailsOpen = false;
      this._render();
    });
    this.shadowRoot.querySelector(".overlay")?.addEventListener("click", (event) => {
      if (event.target.classList.contains("overlay")) {
        this._detailsOpen = false;
        this._render();
      }
    });
  }

  _render() {
    if (!this._config || !this._hass) return;
    const text = this._text();
    const stateObj = this._hass.states[this._config.entity];
    if (!stateObj) {
      this.shadowRoot.innerHTML = `<style>${STYLE}</style><ha-card><div class="error"><strong>${escapeHtml(text.missing)}</strong><span>${escapeHtml(text.configure)}</span></div></ha-card>`;
      return;
    }

    const hours = stateObj.attributes.forecast_hours ?? 4;
    const values = this._values(stateObj);
    const title = this._config.name || text.title;

    this.shadowRoot.innerHTML = `<style>${STYLE}</style>
      <ha-card>
        <div class="head">
          <div class="identity"><span class="weather-icon">${ICONS.weather}</span><div><p class="title">${escapeHtml(title)}</p><p class="subtitle">${escapeHtml(this._format(text.period, { hours }))}</p></div></div>
          <div class="temperature"><strong>${escapeHtml(values.temperature)}°</strong><span>${escapeHtml(text.feelsLike)}</span></div>
        </div>
        <div class="recommendation"><h2>${escapeHtml(values.headline)}</h2><p>${escapeHtml(values.reason)}</p></div>
        <div class="garments">
          ${this._garment("trousers", values.bottom)}
          ${this._garment("shirt", values.top)}
          ${this._garment(stateObj.attributes.outerwear === "vest" ? "vest" : "jacket", values.outerwear)}
        </div>
        <div class="footer"><span class="range"><span class="icon">${ICONS.clock}</span>${escapeHtml(values.range)}</span><button class="more" type="button">${escapeHtml(text.seeWhy)}</button></div>
      </ha-card>
      ${this._detailsOpen ? this._detail(stateObj, values) : ""}`;

    this.shadowRoot.querySelector(".more")?.addEventListener("click", () => {
      this._detailsOpen = true;
      this._render();
    });
    this._wireDetailEvents();
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

if (!customElements.get(CARD_TAG)) {
  customElements.define(CARD_TAG, ClothingAdvisorCard);
}
window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === CARD_TAG)) {
  window.customCards.push({
    type: CARD_TAG,
    name: "Clothing Advisor",
    description: "A compact, localized clothing recommendation card.",
    preview: true,
    getEntitySuggestion: (hass, entityId) => {
      const state = hass.states[entityId];
      return state?.attributes?.base_layer && state?.attributes?.outerwear
        ? { entity: entityId }
        : null;
    },
  });
}
