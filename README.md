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

[![Open in HACS][hacs-badge]][hacs]

Requires [HACS](https://hacs.xyz/). If this repository is not listed yet, add `https://github.com/oraad/ha-mawaqeet` as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) (category: **Integration**), then use the button above.

1. Install **Mawaqeet** from the HACS Integrations tab.
2. Restart Home Assistant.

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

Five automation blueprints ship with this repository. Use the **Import** badges to open the blueprint import dialog on your Home Assistant instance ([My Home Assistant](https://my.home-assistant.io) link). You can also import manually from **Settings → Automations → Blueprints**, or copy YAML into your config `blueprints/` folder.

| Blueprint | Use when | Import |
| --- | --- | --- |
| [Adhan (Home Assistant)](blueprints/adhan_home_assistant.yaml) | Play adhan on prayer time via Sonos, Cast, and other `media_player` entities (not Music Assistant) | [![Import blueprint][import-adhan-ha-badge]][import-adhan-ha] |
| [Adhan (Music Assistant)](blueprints/adhan_music_assistant.yaml) | Play adhan via `media_player` entities from the [Music Assistant](https://www.home-assistant.io/integrations/music_assistant/) integration | [![Import blueprint][import-adhan-ma-badge]][import-adhan-ma] |
| [Fajr wake-up](blueprints/fajr_wakeup.yaml) | Gradually turn on lights (and optional tone) at Fajr or the Mawaqeet Fajr reminder; use adhan blueprints for full adhan | [![Import blueprint][import-fajr-wakeup-badge]][import-fajr-wakeup] |
| [Prayer reminder notification](blueprints/prayer_reminder_notify.yaml) | Send a notification or TTS when a Mawaqeet prayer reminder fires | [![Import blueprint][import-prayer-reminder-badge]][import-prayer-reminder] |
| [Prayer time lighting](blueprints/prayer_time_lights.yaml) | Control lights or scenes when a Mawaqeet prayer time occurs | [![Import blueprint][import-prayer-lights-badge]][import-prayer-lights] |

#### Blueprint options (both adhan blueprints)

| Input | Description |
| --- | --- |
| Location | Mawaqeet device (prayer time trigger) |
| Playback mode | **Media playback** (normal play) or **Announcement** (duck/pause other audio where supported) |
| Enable per prayer | Toggle Fajr, Dhuhr, Asr, Maghrib, Ishaa |
| Fajr media player(s) | One or more `media_player` entities for Fajr (HA: not MA; MA: MA players only) |
| Other prayers media player(s) | One or more `media_player` entities for Dhuhr–Ishaa |
| Fajr adhan audio (playback) | Audio file for Fajr in media playback mode |
| Other prayers adhan audio (playback) | Audio for Dhuhr–Ishaa in media playback mode |
| Fajr adhan audio (announcement) | Audio for Fajr in announcement mode (can differ from playback) |
| Other prayers adhan audio (announcement) | Audio for Dhuhr–Ishaa in announcement mode |
| Announcement volume (Fajr / other) | Music Assistant blueprint only: optional 0–100 |

**Fajr vs other prayers:** Pick separate players and audio files for Fajr and for the rest of the day. Select **multiple** `media_player` entities per window to play adhan on all speakers at once. Use different announcement vs playback clips if you want a short announce at Fajr and full adhan elsewhere.

**Home Assistant blueprint:** Uses `media_player.play_media`. Announcement mode sets `announce: true` (works best on Sonos and similar players). Do not select `media_player.ma_*` entities — use the Music Assistant blueprint for those.

**Music Assistant blueprint:** Uses `music_assistant.play_media` and `music_assistant.play_announcement`. Player selectors list only Music Assistant players. For announcements, local files under `/config/www/` (`http://<your-ha>/local/...`) or `http(s)` URLs work reliably; other paths are resolved via `media_source.resolve_media`.

**Migration from older adhan blueprints:** Re-import the Home Assistant or Music Assistant blueprint (badges above), then edit or recreate your automation. Map each former single player to the new multi-select **media player(s)** fields (one entry per speaker). Audio inputs are unchanged.

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

### Known limitations

- Prayer times are **calculated locally** from coordinates and method settings; there is no link to a specific mosque timetable or cloud API.
- **Shuruq**, **Midnight**, and **Last Third** are optional sensors; automations for the five daily prayers use Fajr through Ishaa.
- **Reminder** events cover Fajr through Ishaa only (not Shuruq, Midnight, or Last Third).
- Only **one config entry** per map position is allowed.
- The custom Lovelace card requires adding a [Lovelace resource](#dashboard-cards) (served by the integration).

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

When the integration loads, it **registers the Lovelace resource automatically** (storage-mode dashboards). After a refresh, **Mawaqeet Prayer** appears in the card picker. The module is served at `/mawaqeet/mawaqeet-prayer-card.js` (version query string is added for cache busting).

1. Add a card in the dashboard UI (**Mawaqeet Prayer**) or YAML:

```yaml
type: custom:mawaqeet-prayer-card
device: DEVICE_ID_FROM_SETTINGS
layout: next
show_shuruq: false
```

Pick the device under **Settings → Devices & services → Mawaqeet →** your location. Each config entry is one device.

**YAML-only Lovelace** cannot be updated from the UI; add the resource manually under `lovelace.resources`:

```yaml
lovelace:
  resources:
    - url: /mawaqeet/mawaqeet-prayer-card.js
      type: module
```

**Troubleshooting (storage mode):** if the card is missing from the picker, reload the integration and check **Settings → Dashboards → Resources** for `/mawaqeet/mawaqeet-prayer-card.js`, then refresh the dashboard.

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
| **Mawaqeet Prayer** not in Add card list | Reload the integration; check **Settings → Dashboards → Resources** for `/mawaqeet/mawaqeet-prayer-card.js`. On YAML Lovelace, add the resource manually (see Setup). Refresh the dashboard |
| Card type unknown | Ensure the Lovelace resource exists (auto-registered on load); restart Home Assistant |
| `/mawaqeet/mawaqeet-prayer-card.js` returns 404 | Reinstall the integration (ensure `www/` is present); restart Home Assistant |
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

This integration targets the Home Assistant [integration quality scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) at **Gold** (Silver test coverage in CI; Platinum deferred).

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
[hacs-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[hacs]: https://my.home-assistant.io/redirect/hacs_repository/?owner=oraad&repository=ha-mawaqeet&category=integration
[import-adhan-ha-badge]: https://my.home-assistant.io/badges/blueprint_import.svg
[import-adhan-ha]: https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Foraad%2Fha-mawaqeet%2Fblob%2Fmain%2Fblueprints%2Fadhan_home_assistant.yaml
[import-adhan-ma-badge]: https://my.home-assistant.io/badges/blueprint_import.svg
[import-adhan-ma]: https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Foraad%2Fha-mawaqeet%2Fblob%2Fmain%2Fblueprints%2Fadhan_music_assistant.yaml
[import-fajr-wakeup-badge]: https://my.home-assistant.io/badges/blueprint_import.svg
[import-fajr-wakeup]: https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Foraad%2Fha-mawaqeet%2Fblob%2Fmain%2Fblueprints%2Ffajr_wakeup.yaml
[import-prayer-reminder-badge]: https://my.home-assistant.io/badges/blueprint_import.svg
[import-prayer-reminder]: https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Foraad%2Fha-mawaqeet%2Fblob%2Fmain%2Fblueprints%2Fprayer_reminder_notify.yaml
[import-prayer-lights-badge]: https://my.home-assistant.io/badges/blueprint_import.svg
[import-prayer-lights]: https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Foraad%2Fha-mawaqeet%2Fblob%2Fmain%2Fblueprints%2Fprayer_time_lights.yaml
