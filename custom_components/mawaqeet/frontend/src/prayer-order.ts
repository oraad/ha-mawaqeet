/** Canonical prayer keys and display order (matches integration PrayerTime enum). */

export const CORE_PRAYER_KEYS = [
  "fajr",
  "dhuhr",
  "asr",
  "maghrib",
  "ishaa",
] as const;

export const SHURUQ_KEY = "shuruq" as const;

export const EXCLUDED_PRAYER_KEYS = new Set([
  "midnight",
  "last_third",
]);

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
  | typeof SHURUQ_KEY;

export function buildPrayerOrder(showShuruq: boolean): PrayerKey[] {
  if (!showShuruq) {
    return [...CORE_PRAYER_KEYS];
  }
  return ["fajr", SHURUQ_KEY, "dhuhr", "asr", "maghrib", "ishaa"];
}

export function isPrayerKey(key: string, showShuruq: boolean): key is PrayerKey {
  if (EXCLUDED_PRAYER_KEYS.has(key) || DIAGNOSTIC_SENSOR_KEYS.has(key)) {
    return false;
  }
  const order = buildPrayerOrder(showShuruq);
  return (order as readonly string[]).includes(key);
}

export function prayerSortIndex(key: PrayerKey, showShuruq: boolean): number {
  const order = buildPrayerOrder(showShuruq);
  const index = order.indexOf(key);
  return index === -1 ? 999 : index;
}
