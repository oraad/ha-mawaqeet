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
  return html`<span class="icon-slot" aria-hidden="true"
    ><ha-icon .icon=${icon}></ha-icon
  ></span>`;
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

function rowKeydown(
  entityId: string,
  onTap: (entityId: string) => void,
): (ev: KeyboardEvent) => void {
  return (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      ev.stopPropagation();
      onTap(entityId);
    }
  };
}

function interactiveRow(
  entityId: string,
  onTap: (entityId: string) => void,
  classes: string,
  content: TemplateResult,
  ariaLabel?: string,
): TemplateResult {
  return html`
    <div
      class=${classes}
      @click=${rowClick(entityId, onTap)}
      @keydown=${rowKeydown(entityId, onTap)}
      role="button"
      tabindex="0"
      aria-label=${ariaLabel ?? nothing}
    >
      ${content}
    </div>
  `;
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
  const ariaLabel = `Next prayer: ${prayer.label} ${countdown} at ${atLabel}`;

  return html`
    ${renderHeader(hass, config)}
    ${interactiveRow(
      prayer.entity_id,
      onTap,
      "next-hero",
      html`
        ${iconNode(prayer.icon)}
        <div class="prayer-name">${prayer.label}</div>
        <div class="countdown">${countdown}</div>
        <div class="at-time">${atLabel}</div>
        ${isTomorrow
          ? html`<div class="tomorrow-badge">Tomorrow</div>`
          : nothing}
        ${followingLabel
          ? html`<div class="following">${followingLabel}</div>`
          : nothing}
      `,
      ariaLabel,
    )}
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
      const classes = ["row", isNext ? "next" : "", isPassed ? "passed" : ""]
        .filter(Boolean)
        .join(" ");
      const timeLabel = formatTime(p.at, hass, tf);
      return interactiveRow(
        p.entity_id,
        onTap,
        classes,
        html`
          ${iconNode(p.icon)}
          <span class="name">${p.label}</span>
          <span class="times">
            <div>${timeLabel}</div>
            ${showRelative
              ? html`<div class="relative">
                  ${formatRelative(p.at, now)}
                </div>`
              : nothing}
          </span>
        `,
        `${p.label} ${timeLabel}`,
      );
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
        const timeLabel = formatTime(p.at, hass, tf);
        return interactiveRow(
          p.entity_id,
          onTap,
          classes,
          html`
            ${iconNode(p.icon)}
            <div>${p.label}</div>
            <div class="chip-time">${timeLabel}</div>
            ${showRelative
              ? html`<div class="chip-relative">
                  ${formatRelative(p.at, now)}
                </div>`
              : nothing}
          `,
          `${p.label} ${timeLabel}`,
        );
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
      const timeLabel = formatTime(p.at, hass, tf);
      return interactiveRow(
        p.entity_id,
        onTap,
        classes,
        html`
          <span class="agenda-status" aria-hidden="true">
            ${isPassed
              ? html`<ha-icon .icon=${"mdi:check"}></ha-icon>`
              : nothing}
          </span>
          ${iconNode(p.icon)}
          <span class="name">${p.label}</span>
          <span class="times">${timeLabel}</span>
        `,
        `${p.label} ${timeLabel}`,
      );
    })}
  `;

  return html`
    ${renderHeader(hass, config)}
    ${earlier.length ? renderSection("Earlier today", earlier) : nothing}
    ${upcoming.length
      ? renderSection("Upcoming", upcoming)
      : html`<div class="section-title">Upcoming</div>
          <div class="agenda-empty">All prayers complete for today</div>`}
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
  const nowPct = Math.min(
    100,
    Math.max(0, ((now.getTime() - start) / span) * 100),
  );
  const tf = timeFmt(hass, config);
  const nextInfo = findNextPrayer(prayers, now);
  const nextId = nextInfo?.prayer.entity_id;

  return html`
    ${renderHeader(hass, config)}
    <div class="timeline">
      <div class="timeline-track"></div>
      <div class="timeline-now" style="left: ${nowPct}%"></div>
      ${prayers.map((p) => {
        const left = ((p.at.getTime() - start) / span) * 100;
        const isNext = p.entity_id === nextId;
        const isPassed =
          config.show_passed_style !== false && p.at.getTime() < now.getTime();
        const classes = [
          "timeline-marker",
          isNext ? "next" : "",
          isPassed ? "passed" : "",
        ]
          .filter(Boolean)
          .join(" ");
        const timeLabel = formatTime(p.at, hass, tf);
        const label = `${p.label} ${timeLabel}`;
        return html`
          <div
            class=${classes}
            style="left: ${left}%"
            @click=${rowClick(p.entity_id, onTap)}
            @keydown=${rowKeydown(p.entity_id, onTap)}
            role="button"
            tabindex="0"
            aria-label=${label}
            title=${label}
          >
            ${iconNode(p.icon)}
            <div>${p.label}</div>
            <div>${timeLabel}</div>
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
