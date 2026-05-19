import { describe, expect, it } from "vitest";
import {
  extractPrayerKey,
  findCurrentPrayer,
  findNextPrayer,
  resolvePrayerEntities,
} from "./entity-resolver";
import type { HomeAssistant } from "./types";

const DEVICE = "device-abc";

function mockHass(
  states: Record<string, { state: string; attributes?: Record<string, unknown> }>,
  entities: Record<
    string,
    { translation_key?: string; device_id?: string; platform?: string }
  >,
): HomeAssistant {
  const hassStates: HomeAssistant["states"] = {};
  for (const [entity_id, data] of Object.entries(states)) {
    hassStates[entity_id] = {
      entity_id,
      state: data.state,
      attributes: { device_class: "timestamp", ...data.attributes },
      last_changed: data.state,
    };
  }
  const hassEntities: HomeAssistant["entities"] = {};
  for (const [entity_id, data] of Object.entries(entities)) {
    hassEntities[entity_id] = {
      entity_id,
      platform: data.platform ?? "mawaqeet",
      device_id: data.device_id ?? DEVICE,
      translation_key: data.translation_key ?? null,
    };
  }
  return {
    states: hassStates,
    entities: hassEntities,
    devices: {
      [DEVICE]: { id: DEVICE, name: "Home" },
    },
    locale: { language: "en", number_format: "en", time_format: "24" },
    formatEntityState: (s) => s.state,
    localize: (key) => key,
  };
}

const today = new Date();
const iso = (hours: number, minutes = 0) => {
  const d = new Date(today);
  d.setHours(hours, minutes, 0, 0);
  return d.toISOString();
};

function sixPrayerEntities() {
  return {
    "sensor.x_fajr": { translation_key: "fajr" },
    "sensor.x_dhuhr": { translation_key: "dhuhr" },
    "sensor.x_asr": { translation_key: "asr" },
    "sensor.x_maghrib": { translation_key: "maghrib" },
    "sensor.x_ishaa": { translation_key: "ishaa" },
    "sensor.x_calculation_method": { translation_key: "calculation_method" },
  };
}

function sixPrayerStates() {
  return {
    "sensor.x_fajr": { state: iso(5, 0) },
    "sensor.x_dhuhr": { state: iso(12, 30) },
    "sensor.x_asr": { state: iso(15, 45) },
    "sensor.x_maghrib": { state: iso(18, 10) },
    "sensor.x_ishaa": { state: iso(19, 45) },
    "sensor.x_calculation_method": {
      state: "mwl",
      attributes: { device_class: undefined },
    },
  };
}

describe("extractPrayerKey", () => {
  it("uses translation_key when present", () => {
    expect(
      extractPrayerKey({
        entity_id: "sensor.foo_fajr",
        platform: "mawaqeet",
      }),
    ).toBe("fajr");
  });
});

describe("resolvePrayerEntities", () => {
  it("returns prayers sorted in canonical order", () => {
    const hass = mockHass(sixPrayerStates(), sixPrayerEntities());
    const prayers = resolvePrayerEntities(hass, DEVICE, false);
    expect(prayers.map((p) => p.prayer_key)).toEqual([
      "fajr",
      "dhuhr",
      "asr",
      "maghrib",
      "ishaa",
    ]);
  });

  it("includes shuruq when enabled", () => {
    const entities = {
      ...sixPrayerEntities(),
      "sensor.x_shuruq": { translation_key: "shuruq" },
    };
    const states = {
      ...sixPrayerStates(),
      "sensor.x_shuruq": { state: iso(6, 15) },
    };
    const hass = mockHass(states, entities);
    const prayers = resolvePrayerEntities(hass, DEVICE, true);
    expect(prayers.map((p) => p.prayer_key)).toEqual([
      "fajr",
      "shuruq",
      "dhuhr",
      "asr",
      "maghrib",
      "ishaa",
    ]);
  });

  it("returns empty for wrong device", () => {
    const hass = mockHass(sixPrayerStates(), sixPrayerEntities());
    expect(resolvePrayerEntities(hass, "other", false)).toEqual([]);
  });
});

describe("findNextPrayer", () => {
  it("picks earliest future prayer", () => {
    const hass = mockHass(sixPrayerStates(), sixPrayerEntities());
    const prayers = resolvePrayerEntities(hass, DEVICE, false);
    const now = new Date(iso(13, 0));
    const next = findNextPrayer(prayers, now);
    expect(next?.prayer.prayer_key).toBe("asr");
    expect(next?.isTomorrow).toBe(false);
  });

  it("wraps to fajr tomorrow when all passed", () => {
    const hass = mockHass(sixPrayerStates(), sixPrayerEntities());
    const prayers = resolvePrayerEntities(hass, DEVICE, false);
    const now = new Date(iso(22, 0));
    const next = findNextPrayer(prayers, now);
    expect(next?.prayer.prayer_key).toBe("fajr");
    expect(next?.isTomorrow).toBe(true);
  });
});

describe("findCurrentPrayer", () => {
  it("returns last prayer at or before now", () => {
    const hass = mockHass(sixPrayerStates(), sixPrayerEntities());
    const prayers = resolvePrayerEntities(hass, DEVICE, false);
    const now = new Date(iso(16, 0));
    expect(findCurrentPrayer(prayers, now)?.prayer_key).toBe("asr");
  });
});
