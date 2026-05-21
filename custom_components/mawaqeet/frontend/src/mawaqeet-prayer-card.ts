import { LitElement, html, type CSSResultGroup, type PropertyValues } from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { resolvePrayerEntities } from "./entity-resolver";
import { gridOptionsForLayout } from "./grid-options";
import { renderError, renderLayout } from "./layouts/render";
import { cardStyles } from "./styles";
import type {
  HomeAssistant,
  LovelaceGridOptions,
  MawaqeetCardConfig,
} from "./types";

declare global {
  interface HTMLElementTagNameMap {
    "mawaqeet-prayer-card": MawaqeetPrayerCard;
    "mawaqeet-prayer-card-editor": MawaqeetPrayerCardEditor;
  }
  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description: string;
      preview?: boolean;
    }>;
  }
}

@customElement("mawaqeet-prayer-card")
export class MawaqeetPrayerCard extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MawaqeetCardConfig;

  @state() private _now = new Date();

  private _clockInterval?: number;

  public setConfig(config: MawaqeetCardConfig): void {
    if (!config.device) {
      throw new Error("Set a Mawaqeet device for this card.");
    }
    this._config = {
      type: "custom:mawaqeet-prayer-card",
      layout: "next",
      show_shuruq: false,
      show_passed_style: true,
      time_format: "system",
      show_relative: true,
      show_device_name: false,
      ...config,
    };
  }

  public getCardSize(): number {
    const layout = this._config?.layout ?? "next";
    switch (layout) {
      case "horizontal":
      case "combined":
        return 2;
      case "vertical":
      case "agenda":
        return 4;
      case "timeline":
        return 3;
      default:
        return 2;
    }
  }

  public getGridOptions(): LovelaceGridOptions {
    const layout = this._config?.layout ?? "next";
    return gridOptionsForLayout(layout);
  }

  public static async getConfigElement(): Promise<HTMLElement> {
    return document.createElement("mawaqeet-prayer-card-editor");
  }

  public static getStubConfig(): Partial<MawaqeetCardConfig> {
    return {
      type: "custom:mawaqeet-prayer-card",
      layout: "next",
      show_shuruq: false,
    };
  }

  connectedCallback(): void {
    super.connectedCallback();
    this._clockInterval = window.setInterval(() => {
      this._now = new Date();
    }, 60_000);
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    if (this._clockInterval !== undefined) {
      window.clearInterval(this._clockInterval);
    }
  }

  protected willUpdate(changed: PropertyValues): void {
    if (changed.has("hass")) {
      this._now = new Date();
    }
  }

  protected render() {
    if (!this.hass || !this._config) {
      return html`<ha-card><div class="error">Loading…</div></ha-card>`;
    }

    const showShuruq = this._config.show_shuruq === true;
    const prayers = resolvePrayerEntities(
      this.hass,
      this._config.device!,
      showShuruq,
    );

    let body;
    if (!this._config.device) {
      body = renderError("Select a Mawaqeet location device in card settings.");
    } else if (prayers.length === 0) {
      body = renderError(
        "No prayer times found for this device. Check that Mawaqeet is loaded.",
      );
    } else {
      body = renderLayout(
        this.hass,
        this._config,
        prayers,
        this._now,
        (entityId) => this._moreInfo(entityId),
      );
    }

    return html`<ha-card>${body}</ha-card>`;
  }

  protected static styles: CSSResultGroup = cardStyles;

  private _moreInfo(entityId: string): void {
    const event = new CustomEvent("hass-more-info", {
      bubbles: true,
      composed: true,
      detail: { entityId },
    });
    this.dispatchEvent(event);
  }
}

const EDITOR_SCHEMA = [
  {
    name: "device",
    required: true,
    selector: {
      device: { filter: { integration: "mawaqeet" } },
    },
  },
  {
    name: "layout",
    selector: {
      select: {
        options: [
          { value: "next", label: "Next prayer" },
          { value: "horizontal", label: "Horizontal timetable" },
          { value: "vertical", label: "Vertical timetable" },
          { value: "combined", label: "Combined (next + horizontal)" },
          { value: "timeline", label: "Day timeline" },
          { value: "agenda", label: "Agenda" },
        ],
      },
    },
  },
  { name: "show_shuruq", selector: { boolean: {} } },
  { name: "show_passed_style", selector: { boolean: {} } },
  {
    name: "time_format",
    selector: {
      select: {
        options: [
          { value: "system", label: "System" },
          { value: "24", label: "24-hour" },
          { value: "12", label: "12-hour" },
        ],
      },
    },
  },
  { name: "show_relative", selector: { boolean: {} } },
  { name: "show_device_name", selector: { boolean: {} } },
];

@customElement("mawaqeet-prayer-card-editor")
export class MawaqeetPrayerCardEditor extends LitElement {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private _config?: MawaqeetCardConfig;

  public setConfig(config: MawaqeetCardConfig): void {
    this._config = config;
  }

  protected render() {
    if (!this.hass || !this._config) {
      return html``;
    }
    return html`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${EDITOR_SCHEMA}
        .computeLabel=${(schema: { name: string }) =>
          EDITOR_LABELS[schema.name] ?? schema.name}
        @value-changed=${this._changed}
      ></ha-form>
    `;
  }

  private _changed(ev: CustomEvent): void {
    ev.stopPropagation();
    const config = ev.detail.value as MawaqeetCardConfig;
    this._config = config;
    const event = new CustomEvent("config-changed", {
      detail: { config },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

const EDITOR_LABELS: Record<string, string> = {
  device: "Mawaqeet location",
  layout: "Layout",
  show_shuruq: "Show Shuruq (sunrise)",
  show_passed_style: "Dim passed prayers",
  time_format: "Time format",
  show_relative: "Show relative times",
  show_device_name: "Show location name",
};

if (typeof window !== "undefined") {
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "mawaqeet-prayer-card",
    name: "Mawaqeet Prayer",
    description: "Prayer times from a Mawaqeet location device",
    preview: true,
  });
}
