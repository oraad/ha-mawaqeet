import {
  buildPrayerOrder,
  isPrayerKey,
  prayerSortIndex,
  requiredPrayerCount,
  type PrayerDisplayOptions,
  type PrayerKey,
} from "./prayer-order";
import type {
  EntityRegistryEntry,
  HassEntity,
  HomeAssistant,
  ResolvedPrayer,
} from "./types";

const DOMAIN = "mawaqeet";
const DEFAULT_ICON = "mdi:mosque";

/** Defaults mirror custom_components/mawaqeet/icons.json entity icons. */
export const PRAYER_DEFAULT_ICONS: Record<PrayerKey, string> = {
  fajr: "mdi:weather-sunset-up",
  shuruq: "mdi:weather-sunny",
  dhuhr: "mdi:white-balance-sunny",
  asr: "mdi:weather-partly-cloudy",
  maghrib: "mdi:weather-sunset",
  ishaa: "mdi:weather-night",
  midnight: "mdi:clock-time-twelve",
  last_third: "mdi:clock-outline",
};

export function resolvePrayerIcon(
  key: PrayerKey,
  stateIcon: string | undefined,
  configIcons?: Partial<Record<PrayerKey, string>>,
): string {
  const override = configIcons?.[key];
  if (override) {
    return override;
  }
  if (stateIcon) {
    return stateIcon;
  }
  return PRAYER_DEFAULT_ICONS[key] || DEFAULT_ICON;
}

export function extractPrayerKey(entry: EntityRegistryEntry): string | null {
  if (entry.translation_key) {
    return entry.translation_key;
  }
  const suffix = entry.entity_id.split(".").pop()?.split("_").pop();
  return suffix ?? null;
}

export function resolvePrayerEntities(
  hass: HomeAssistant,
  deviceId: string,
  options: PrayerDisplayOptions = {},
  configIcons?: Partial<Record<PrayerKey, string>>,
): ResolvedPrayer[] {
  if (!deviceId || !hass.entities) {
    return [];
  }

  const order = buildPrayerOrder(options);
  const resolved: ResolvedPrayer[] = [];

  for (const entry of Object.values(hass.entities)) {
    if (entry.platform !== DOMAIN || entry.device_id !== deviceId) {
      continue;
    }
    if (!entry.entity_id.startsWith("sensor.")) {
      continue;
    }

    const key = extractPrayerKey(entry);
    if (!key || !isPrayerKey(key, options)) {
      continue;
    }

    const state = hass.states[entry.entity_id];
    if (!state || state.state === "unavailable" || state.state === "unknown") {
      continue;
    }

    const deviceClass = state.attributes.device_class as string | undefined;
    if (deviceClass && deviceClass !== "timestamp") {
      continue;
    }

    const at = new Date(state.state);
    if (Number.isNaN(at.getTime())) {
      continue;
    }

    resolved.push({
      entity_id: entry.entity_id,
      prayer_key: key,
      label: formatPrayerLabel(hass, entry, state),
      icon: resolvePrayerIcon(
        key,
        state.attributes.icon as string | undefined,
        configIcons,
      ),
      at,
      state,
    });
  }

  resolved.sort(
    (a, b) =>
      prayerSortIndex(a.prayer_key, options) -
      prayerSortIndex(b.prayer_key, options),
  );

  const required = requiredPrayerCount(options);
  const coreAndShuruq = resolved.filter((p) =>
    (order as readonly string[])
      .filter((k) => k !== "midnight" && k !== "last_third")
      .includes(p.prayer_key),
  );
  if (coreAndShuruq.length < required) {
    return [];
  }

  return resolved;
}

export interface NextPrayerInfo {
  prayer: ResolvedPrayer;
  following: ResolvedPrayer | null;
  isTomorrow: boolean;
}

export function findNextPrayer(
  prayers: ResolvedPrayer[],
  now: Date = new Date(),
): NextPrayerInfo | null {
  if (prayers.length === 0) {
    return null;
  }

  const future = prayers.filter((p) => p.at.getTime() > now.getTime());
  if (future.length > 0) {
    const next = future[0];
    return {
      prayer: next,
      following: future[1] ?? null,
      isTomorrow: false,
    };
  }

  const fajr = prayers.find((p) => p.prayer_key === "fajr") ?? prayers[0];
  const following =
    prayers.find((p) => p.prayer_key !== fajr.prayer_key) ?? null;
  return {
    prayer: fajr,
    following,
    isTomorrow: true,
  };
}

export function findCurrentPrayer(
  prayers: ResolvedPrayer[],
  now: Date = new Date(),
): ResolvedPrayer | null {
  let current: ResolvedPrayer | null = null;
  for (const prayer of prayers) {
    if (prayer.at.getTime() <= now.getTime()) {
      current = prayer;
    }
  }
  return current;
}

export function formatPrayerLabel(
  hass: HomeAssistant,
  entry: EntityRegistryEntry,
  state: HassEntity,
): string {
  if (entry.translation_key) {
    const key = `component.mawaqeet.entity.sensor.${entry.translation_key}.name`;
    const localized = hass.localize?.(key);
    if (localized && localized !== key) {
      return localized;
    }
  }
  return (state.attributes.friendly_name as string) || entry.entity_id;
}

export function formatTime(
  date: Date,
  hass: HomeAssistant,
  timeFormat: "system" | "24" | "12",
): string {
  const use12 =
    timeFormat === "12" ||
    (timeFormat === "system" && hass.locale?.time_format === "12");
  return new Intl.DateTimeFormat(hass.locale?.language || undefined, {
    hour: "numeric",
    minute: "2-digit",
    hour12: use12,
  }).format(date);
}

export function formatRelative(
  target: Date,
  now: Date = new Date(),
  isTomorrow = false,
): string {
  const diffMs = target.getTime() - now.getTime();
  if (isTomorrow && diffMs < 0) {
    const tomorrow = new Date(target);
    tomorrow.setDate(tomorrow.getDate() + 1);
    return formatRelativeSpan(tomorrow.getTime() - now.getTime());
  }
  return formatRelativeSpan(diffMs);
}

function formatRelativeSpan(diffMs: number): string {
  const abs = Math.abs(diffMs);
  const minutes = Math.round(abs / 60000);
  if (minutes < 1) {
    return diffMs >= 0 ? "now" : "just now";
  }
  if (minutes < 60) {
    return diffMs >= 0 ? `in ${minutes}m` : `${minutes}m ago`;
  }
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours < 24) {
    const label = mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    return diffMs >= 0 ? `in ${label}` : `${label} ago`;
  }
  const days = Math.floor(hours / 24);
  return diffMs >= 0 ? `in ${days}d` : `${days}d ago`;
}

export function getDeviceDisplayName(
  hass: HomeAssistant,
  deviceId: string,
): string {
  const device = hass.devices?.[deviceId];
  if (!device) {
    return "";
  }
  return device.name_by_user || device.name || deviceId;
}
