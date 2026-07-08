/** Canonical prayer keys and display order (matches integration PrayerTime enum). */

export const CORE_PRAYER_KEYS = [
  "fajr",
  "dhuhr",
  "asr",
  "maghrib",
  "ishaa",
] as const;

export const SHURUQ_KEY = "shuruq" as const;
export const MIDNIGHT_KEY = "midnight" as const;
export const LAST_THIRD_KEY = "last_third" as const;

export const DIAGNOSTIC_SENSOR_KEYS = new Set([
  "calculation_method",
  "madhab",
  "high_latitude_rule",
  "night_length",
  "night_duration",
  "fajr_angle",
  "ishaa_angle",
  "ishaa_interval",
  "fajr_offset",
  "shuruq_offset",
  "dhuhr_offset",
  "asr_offset",
  "maghrib_offset",
  "ishaa_offset",
]);

export type PrayerKey =
  | (typeof CORE_PRAYER_KEYS)[number]
  | typeof SHURUQ_KEY
  | typeof MIDNIGHT_KEY
  | typeof LAST_THIRD_KEY;

export interface PrayerDisplayOptions {
  showShuruq?: boolean;
  showMidnight?: boolean;
  showLastThird?: boolean;
}

export function buildPrayerOrder(options: PrayerDisplayOptions = {}): PrayerKey[] {
  const order: PrayerKey[] = ["fajr"];
  if (options.showShuruq) {
    order.push(SHURUQ_KEY);
  }
  order.push("dhuhr", "asr", "maghrib", "ishaa");
  if (options.showMidnight) {
    order.push(MIDNIGHT_KEY);
  }
  if (options.showLastThird) {
    order.push(LAST_THIRD_KEY);
  }
  return order;
}

/** Core five always required; Shuruq is required when enabled. Night extras are optional. */
export function requiredPrayerCount(options: PrayerDisplayOptions = {}): number {
  return 5 + (options.showShuruq ? 1 : 0);
}

export function isPrayerKey(
  key: string,
  options: PrayerDisplayOptions = {},
): key is PrayerKey {
  if (DIAGNOSTIC_SENSOR_KEYS.has(key)) {
    return false;
  }
  const order = buildPrayerOrder(options);
  return (order as readonly string[]).includes(key);
}

export function prayerSortIndex(
  key: PrayerKey,
  options: PrayerDisplayOptions = {},
): number {
  const order = buildPrayerOrder(options);
  const index = order.indexOf(key);
  return index === -1 ? 999 : index;
}
