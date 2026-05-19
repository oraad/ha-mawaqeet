# Mawaqeet

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![Community Forum][forum-shield]][forum]

Home Assistant integration for Islamic prayer times (Mawaqeet), calculated locally for your location using [adhanpy](https://pypi.org/project/adhanpy/).

**Platforms**

| Platform | Description |
| -- | -- |
| `sensor` | Prayer timestamps (Fajr, Shuruq, Dhuhr, Asr, Maghrib, Ishaa, Midnight, Last Third) and diagnostic sensors |
| `event` | Latest prayer time and latest prayer reminder events |

## Installation

### HACS (recommended)

1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS (category: Integration).
2. Install **Mawaqeet** from the HACS Integrations tab.
3. Restart Home Assistant.

### Manual

1. Open your Home Assistant configuration directory (where `configuration.yaml` lives).
2. Create `custom_components/mawaqeet/` if it does not exist.
3. Copy the contents of [`custom_components/mawaqeet/`](custom_components/mawaqeet/) into that folder.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and search for **Mawaqeet**.

## Removal

1. Go to **Settings → Devices & services**, open **Mawaqeet**, and delete each configured location.
2. If you installed manually, remove the `custom_components/mawaqeet` folder (or disable the HACS integration and restart).
3. Restart Home Assistant.

## Configuration

Configuration is done in the UI. Supported languages: **English**, **Arabic** (match your Home Assistant profile language).

1. **Initial setup**: name, map location, and calculation method (MWL, ISNA, Umm Al-Qura, custom, etc.).
2. **Adjustments** (options): madhab (Shafi/Hanafi), per-prayer **calculation** offsets (minutes), optional custom angles for the custom method, and per-prayer **reminder** lead times.
3. **Reconfigure** (from the integration menu): change name, location, or calculation method without removing the entry.

Saving **options** or completing **reconfigure** reloads the integration automatically so prayer times and reminders pick up changes immediately.

### Configuration parameters

| Parameter | Config entry data | Options |
| --- | --- | --- |
| Name | Yes | No |
| Location (lat/lon) | Yes (reconfigure) | No |
| Calculation method | Yes (reconfigure) | No |
| Madhab | No | Yes |
| Per-prayer calculation offsets | No | Yes |
| Custom angles / high-latitude rule | No (custom method) | Yes |
| Prayer reminders on/off | No | Yes |
| Per-prayer reminder minutes | No | Yes |

Each location is one config entry (unique by coordinates). You cannot add the same map position twice.

### Prayer reminders

When enabled (default), the integration fires reminder events before each upcoming prayer (Fajr through Ishaa). Set a separate “minutes before” value for each prayer in the options flow. Use these events with automations or the included blueprint.

### Automations

The [adhan blueprint](blueprints/adhan.yaml) plays adhan when a Mawaqeet prayer time fires. Import it from **Settings → Automations → Blueprints** (or place `blueprints/adhan.yaml` in your config `blueprints/` folder).

#### Blueprint options

| Input | Description |
| --- | --- |
| Location | Mawaqeet device (prayer time trigger) |
| Playback mode | **Media playback** (normal play) or **Announcement** (duck/pause other audio where supported) |
| Player backend | **Home Assistant** (`media_player.play_media`) or **Music Assistant** (`music_assistant.*` actions) |
| Enable per prayer | Toggle Fajr, Dhuhr, Asr, Maghrib, Ishaa |
| Fajr adhan (playback) | Player + file for Fajr in media playback mode |
| Other prayers adhan (playback) | Player + file for Dhuhr–Ishaa in media playback mode |
| Fajr adhan (announcement) | Player + file for Fajr in announcement mode (can differ from playback) |
| Other prayers adhan (announcement) | Player + file for Dhuhr–Ishaa in announcement mode |
| Announcement volume (Fajr / other) | Optional 0–100 for Music Assistant announcements only |

**Fajr vs other prayers:** Use the four media selectors to use a different clip or speaker for Fajr than for the rest of the day, and to use different assets for announcement vs full playback (e.g. short Fajr announce on kitchen speaker, full adhan on living room for playback).

**Home Assistant + announcement:** Uses `announce: true` on `media_player.play_media` (works best on Sonos and similar players).

**Music Assistant:** Requires the [Music Assistant](https://www.home-assistant.io/integrations/music_assistant/) integration. Target MA media players (e.g. `media_player.ma_kitchen`). For announcements, local files under `/config/www/` (`http://<your-ha>/local/...`) or `http(s)` URLs work reliably; other media paths are resolved via `media_source.resolve_media` before playback.

**Defaults for existing setups:** Player backend **Home Assistant**, playback mode **Media playback** — same behavior as earlier blueprint versions if you re-create the automation and fill the four media fields (duplicate playback settings into announcement fields if you want the same audio in both modes).

Example (Music Assistant, Fajr announcement):

```yaml
action: music_assistant.play_announcement
target:
  entity_id: media_player.ma_kitchen
data:
  url: http://homeassistant.local:8123/local/adhan/fajr.mp3
  announce_volume: 40
```

### Services

| Service | Description |
| --- | --- |
| `mawaqeet.trigger_event` | Fire a prayer time or reminder event immediately (for testing automations) |

**Fields:** `config_entry` (your Mawaqeet location), `trigger_type` (`prayer_time` or `prayer_reminder`), `prayer` (any prayer: `fajr`, `shuruq`, `dhuhr`, `asr`, `maghrib`, `ishaa`, `midnight`, `last_third`).

Example in **Developer Tools → Actions**:

```yaml
action: mawaqeet.trigger_event
data:
  config_entry: YOUR_CONFIG_ENTRY_ID
  trigger_type: prayer_time
  prayer: fajr
```

### Use cases

- **Adhan / media**: Trigger speakers or notifications on `latest_prayer_time` events (see blueprint).
- **Reminders**: Automate lights, TTS, or mobile notifications on `latest_prayer_reminder` before each prayer.
- **Dashboards**: Use the [Mawaqeet prayer Lovelace card](#dashboard-cards) (next prayer, horizontal/vertical timetable).
- **Testing automations**: Call `mawaqeet.trigger_event` to simulate a prayer time or reminder without waiting for the schedule.

### Data updates

Prayer times are calculated locally (no cloud API). The coordinator refreshes at each prayer boundary and schedules the next update, so entities stay in sync without constant polling. Changing options or reconfiguring reloads the entry and rebuilds timers.

### Troubleshooting

| Symptom | Things to check |
| --- | --- |
| Times differ from local mosque | Calculation method, madhab (Asr), and per-prayer offsets in options |
| High-latitude odd times | Enable custom method and set high-latitude rule if needed |
| Reminders not firing | Options → prayer reminders enabled; per-prayer minutes set; automations listen to reminder events |
| Duplicate location rejected | One entry per map position; remove or reconfigure the existing entry |

## Dashboard cards

The integration ships a custom Lovelace card that binds to a **Mawaqeet location device** and auto-discovers that device’s prayer timestamp sensors (no manual entity list).

### Setup

1. Add the card resource (served by the integration after restart):

```yaml
lovelace:
  mode: storage
  resources:
    - url: /mawaqeet/mawaqeet-prayer-card.js
      type: module
```

2. Add a card in the dashboard UI (**Mawaqeet Prayer**) or YAML:

```yaml
type: custom:mawaqeet-prayer-card
device: DEVICE_ID_FROM_SETTINGS
layout: next
show_shuruq: false
```

Pick the device under **Settings → Devices & services → Mawaqeet →** your location. Each config entry is one device.

### Layouts

| `layout` | Description |
| --- | --- |
| `next` | Next prayer name, countdown, and following prayer |
| `horizontal` | Compact row of all prayers (highlights next) |
| `vertical` | Full list with optional relative times |
| `combined` | Next prayer hero + horizontal strip |
| `timeline` | Day timeline from Fajr to Ishaa |
| `agenda` | “Earlier today” and “Upcoming” sections |

By default the card shows the five daily prayers (Fajr, Dhuhr, Asr, Maghrib, Ishaa). Enable **Show Shuruq** in the card editor to include sunrise.

### Troubleshooting

| Symptom | Fix |
| --- | --- |
| Card type unknown | Add the Lovelace resource and restart Home Assistant |
| No prayer times found | Select the correct Mawaqeet device; confirm the integration is loaded |
| Wrong location | One card per device; add another card for a second config entry |

### Rebuild the card (developers)

Requires **Node.js 24 LTS** (see `.nvmrc`). CI runs the same steps in the [Frontend workflow](.github/workflows/frontend.yml).

```bash
cd custom_components/mawaqeet/frontend && npm ci && npm run test && npm run build
# or: python scripts/build_frontend.py  (requires npm on PATH)
```

Output: `custom_components/mawaqeet/www/mawaqeet-prayer-card.js`

## Brand assets

Icons and logos are bundled under `custom_components/mawaqeet/brand/` (light and dark variants) for Home Assistant 2026.3+. To regenerate them after design changes:

```bash
python scripts/generate_brand.py
```

## Requirements

- Home Assistant **2026.3.2** or newer

## Development

```bash
scripts/setup
scripts/develop
```

Run linting:

```bash
scripts/lint
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT — see [LICENSE](LICENSE).

[mawaqeet]: https://github.com/oraad/ha-mawaqeet
[commits-shield]: https://img.shields.io/github/commit-activity/y/oraad/ha-mawaqeet.svg?style=for-the-badge
[commits]: https://github.com/oraad/ha-mawaqeet/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/oraad/ha-mawaqeet.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/oraad/ha-mawaqeet.svg?style=for-the-badge
[releases]: https://github.com/oraad/ha-mawaqeet/releases
