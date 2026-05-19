import { html, nothing, type TemplateResult } from "lit";
import {
  findNextPrayer,
  formatRelative,
  formatTime,
  getDeviceDisplayName,
} from "../entity-resolver";
import type {
  HomeAssistant,
  MawaqeetCardConfig,
  ResolvedPrayer,
  TimeFormat,
} from "../types";

function timeFmt(hass: HomeAssistant, config: MawaqeetCardConfig): TimeFormat {
  return config.time_format ?? "system";
}

export function renderHeader(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
): TemplateResult | typeof nothing {
  if (!config.show_device_name || !config.device) {
    return nothing;
  }
  const name = getDeviceDisplayName(hass, config.device);
  if (!name) {
    return nothing;
  }
  return html`<div class="header">${name}</div>`;
}

export function renderError(message: string): TemplateResult {
  return html`<div class="error">${message}</div>`;
}

function iconNode(icon: string): TemplateResult {
  return html`<ha-icon .icon=${icon}></ha-icon>`;
}

function rowClick(
  entityId: string,
  onTap: (entityId: string) => void,
): (ev: Event) => void {
  return (ev) => {
    ev.stopPropagation();
    onTap(entityId);
  };
}

export function renderNext(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
  prayers: ResolvedPrayer[],
  now: Date,
  onTap: (entityId: string) => void,
): TemplateResult {
  const nextInfo = findNextPrayer(prayers, now);
  if (!nextInfo) {
    return renderError("No prayer times available.");
  }
  const { prayer, following, isTomorrow } = nextInfo;
  const tf = timeFmt(hass, config);
  const countdown = formatRelative(prayer.at, now, isTomorrow);
  const atLabel = formatTime(prayer.at, hass, tf);
  const followingLabel =
    following &&
    html`Following: ${following.label} at ${formatTime(following.at, hass, tf)}`;

  return html`
    ${renderHeader(hass, config)}
    <div
      class="next-hero"
      @click=${rowClick(prayer.entity_id, onTap)}
      role="button"
      tabindex="0"
    >
      ${iconNode(prayer.icon)}
      <div class="prayer-name">${prayer.label}</div>
      <div class="countdown">${countdown} · ${atLabel}</div>
      ${isTomorrow
        ? html`<div class="following">Tomorrow</div>`
        : nothing}
      ${followingLabel
        ? html`<div class="following">${followingLabel}</div>`
        : nothing}
    </div>
  `;
}

export function renderVertical(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
  prayers: ResolvedPrayer[],
  now: Date,
  onTap: (entityId: string) => void,
): TemplateResult {
  const nextInfo = findNextPrayer(prayers, now);
  const nextId = nextInfo?.prayer.entity_id;
  const tf = timeFmt(hass, config);
  const showRelative = config.show_relative !== false;

  return html`
    ${renderHeader(hass, config)}
    ${prayers.map((p) => {
      const isNext = p.entity_id === nextId;
      const isPassed =
        config.show_passed_style !== false && p.at.getTime() < now.getTime();
      const classes = ["row", isNext ? "next" : "", isPassed ? "passed strike" : ""]
        .filter(Boolean)
        .join(" ");
      return html`
        <div
          class=${classes}
          @click=${rowClick(p.entity_id, onTap)}
          role="button"
          tabindex="0"
        >
          ${iconNode(p.icon)}
          <span class="name">${p.label}</span>
          <span class="times">
            <div>${formatTime(p.at, hass, tf)}</div>
            ${showRelative
              ? html`<div class="relative">
                  ${formatRelative(p.at, now)}
                </div>`
              : nothing}
          </span>
        </div>
      `;
    })}
  `;
}

export function renderHorizontal(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
  prayers: ResolvedPrayer[],
  now: Date,
  onTap: (entityId: string) => void,
): TemplateResult {
  const nextInfo = findNextPrayer(prayers, now);
  const nextId = nextInfo?.prayer.entity_id;
  const tf = timeFmt(hass, config);
  const showRelative = config.show_relative === true;

  return html`
    ${renderHeader(hass, config)}
    <div class="horizontal">
      ${prayers.map((p) => {
        const isNext = p.entity_id === nextId;
        const isPassed =
          config.show_passed_style !== false && p.at.getTime() < now.getTime();
        const classes = ["chip", isNext ? "next" : "", isPassed ? "passed" : ""]
          .filter(Boolean)
          .join(" ");
        return html`
          <div
            class=${classes}
            @click=${rowClick(p.entity_id, onTap)}
            role="button"
            tabindex="0"
          >
            ${iconNode(p.icon)}
            <div>${p.label}</div>
            <div class="chip-time">${formatTime(p.at, hass, tf)}</div>
            ${showRelative
              ? html`<div class="chip-relative">
                  ${formatRelative(p.at, now)}
                </div>`
              : nothing}
          </div>
        `;
      })}
    </div>
  `;
}

export function renderCombined(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
  prayers: ResolvedPrayer[],
  now: Date,
  onTap: (entityId: string) => void,
): TemplateResult {
  return html`
    ${renderNext(hass, { ...config, show_device_name: false }, prayers, now, onTap)}
    <hr class="divider" />
    ${renderHorizontal(
      hass,
      { ...config, show_device_name: false, show_relative: false },
      prayers,
      now,
      onTap,
    )}
  `;
}

export function renderAgenda(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
  prayers: ResolvedPrayer[],
  now: Date,
  onTap: (entityId: string) => void,
): TemplateResult {
  const nextInfo = findNextPrayer(prayers, now);
  const nextId = nextInfo?.prayer.entity_id;
  const upcoming = prayers.filter((p) => p.at.getTime() > now.getTime());
  const earlier = prayers.filter((p) => p.at.getTime() <= now.getTime());
  const tf = timeFmt(hass, config);

  const renderSection = (title: string, items: ResolvedPrayer[]) => html`
    <div class="section-title">${title}</div>
    ${items.map((p) => {
      const isNext = p.entity_id === nextId;
      const isPassed = earlier.includes(p);
      const classes = ["row", isNext ? "next" : "", isPassed ? "passed" : ""]
        .filter(Boolean)
        .join(" ");
      return html`
        <div
          class=${classes}
          @click=${rowClick(p.entity_id, onTap)}
          role="button"
          tabindex="0"
        >
          ${isPassed ? html`<span class="agenda-check">✓</span>` : nothing}
          ${iconNode(p.icon)}
          <span class="name">${p.label}</span>
          <span class="times">${formatTime(p.at, hass, tf)}</span>
        </div>
      `;
    })}
  `;

  return html`
    ${renderHeader(hass, config)}
    ${earlier.length ? renderSection("Earlier today", earlier) : nothing}
    ${upcoming.length ? renderSection("Upcoming", upcoming) : renderSection("Upcoming", prayers)}
  `;
}

export function renderTimeline(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
  prayers: ResolvedPrayer[],
  now: Date,
  onTap: (entityId: string) => void,
): TemplateResult {
  if (prayers.length < 2) {
    return renderError("Not enough prayer times for timeline.");
  }
  const start = prayers[0].at.getTime();
  const end = prayers[prayers.length - 1].at.getTime();
  const span = end - start || 1;
  const nowPct = Math.min(100, Math.max(0, ((now.getTime() - start) / span) * 100));
  const tf = timeFmt(hass, config);

  return html`
    ${renderHeader(hass, config)}
    <div class="timeline">
      <div class="timeline-track"></div>
      <div class="timeline-now" style="left: ${nowPct}%"></div>
      ${prayers.map((p) => {
        const left = ((p.at.getTime() - start) / span) * 100;
        return html`
          <div
            class="timeline-marker"
            style="left: ${left}%"
            @click=${rowClick(p.entity_id, onTap)}
            role="button"
            tabindex="0"
          >
            ${iconNode(p.icon)}
            <div>${p.label}</div>
            <div>${formatTime(p.at, hass, tf)}</div>
          </div>
        `;
      })}
    </div>
  `;
}

export function renderLayout(
  hass: HomeAssistant,
  config: MawaqeetCardConfig,
  prayers: ResolvedPrayer[],
  now: Date,
  onTap: (entityId: string) => void,
): TemplateResult {
  const layout = config.layout ?? "next";
  switch (layout) {
    case "horizontal":
      return renderHorizontal(hass, config, prayers, now, onTap);
    case "vertical":
      return renderVertical(hass, config, prayers, now, onTap);
    case "combined":
      return renderCombined(hass, config, prayers, now, onTap);
    case "timeline":
      return renderTimeline(hass, config, prayers, now, onTap);
    case "agenda":
      return renderAgenda(hass, config, prayers, now, onTap);
  }
  return renderNext(hass, config, prayers, now, onTap);
}
