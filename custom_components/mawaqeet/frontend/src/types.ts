/** Minimal Home Assistant types for the Lovelace card (no runtime HA dependency). */

export interface HomeAssistant {
  states: Record<string, HassEntity>;
  entities: Record<string, EntityRegistryEntry>;
  devices: Record<string, DeviceRegistryEntry>;
  locale: {
    language: string;
    number_format: string;
    time_format: string;
  };
  formatEntityState: (stateObj: HassEntity) => string;
  localize: (key: string) => string;
}

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
  last_changed: string;
}

export interface EntityRegistryEntry {
  entity_id: string;
  platform: string;
  device_id?: string | null;
  translation_key?: string | null;
  original_device_class?: string | null;
}

export interface DeviceRegistryEntry {
  id: string;
  name_by_user?: string | null;
  name?: string | null;
}

export type CardLayout =
  | "next"
  | "horizontal"
  | "vertical"
  | "combined"
  | "timeline"
  | "agenda";

export type TimeFormat = "system" | "24" | "12";

export interface MawaqeetCardConfig {
  type: string;
  device?: string;
  layout?: CardLayout;
  show_shuruq?: boolean;
  show_passed_style?: boolean;
  time_format?: TimeFormat;
  show_relative?: boolean;
  show_device_name?: boolean;
  tap_action?: { action: string };
}

export interface ResolvedPrayer {
  entity_id: string;
  prayer_key: PrayerKey;
  label: string;
  icon: string;
  at: Date;
  state: HassEntity;
}

export type { PrayerKey } from "./prayer-order";
