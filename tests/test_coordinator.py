"""Test coordinator."""

from datetime import UTC, datetime
from unittest.mock import PropertyMock, patch

from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import Event, HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.calculation import async_compute_prayer_times
from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DEFAULT_REMINDER_MINUTES,
    DOMAIN,
    MADHAB,
    MAWAQEET_EVENT,
    PRAYER_TIME_TRIGGER,
    REMINDER_ENABLED,
    REMINDER_MINUTES,
)
from custom_components.mawaqeet.coordinator import MawaqeetDataUpdateCoordinator
from custom_components.mawaqeet.data import MawaqeetRuntimeData
from custom_components.mawaqeet.enum import PrayerTime, prayer_reminder_minutes_key


async def test_prayer_times_computed(hass: HomeAssistant) -> None:
    """Test prayer times are computed for a fixed location."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
            CALCULATION_METHOD: "mwl",
        },
        options={
            MADHAB: "shafi",
            REMINDER_ENABLED: True,
            prayer_reminder_minutes_key(PrayerTime.FAJR): 15,
        },
    )
    entry.add_to_hass(hass)

    data = await async_compute_prayer_times(hass, entry)

    assert set(data["prayer_times"].keys()) == set(PrayerTime)
    for prayer_time in data["prayer_times"].values():
        assert prayer_time is not None


async def test_coordinator_refresh(hass: HomeAssistant) -> None:
    """Test coordinator refresh loads data via async calculation."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
            CALCULATION_METHOD: "mwl",
        },
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    coordinator = MawaqeetDataUpdateCoordinator(hass, entry)
    entry.runtime_data = MawaqeetRuntimeData(coordinator=coordinator)
    await coordinator.async_refresh()

    assert coordinator.data is not None
    assert set(coordinator.data["prayer_times"].keys()) == set(PrayerTime)

    coordinator.clear_event_sub()


async def test_refresh_schedules_callbacks(hass: HomeAssistant) -> None:
    """Test refresh clears and schedules event callbacks."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
            CALCULATION_METHOD: "mwl",
        },
        options={MADHAB: "shafi", REMINDER_ENABLED: False},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    coordinator = entry.runtime_data.coordinator

    assert coordinator.data is not None

    coordinator.clear_event_sub()
    coordinator.async_schedule_future_update(coordinator.data["prayer_times"])
    coordinator.clear_event_sub()


async def test_per_prayer_reminder_minutes(hass: HomeAssistant) -> None:
    """Test per-prayer reminder minute resolution."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
            CALCULATION_METHOD: "mwl",
        },
        options={
            MADHAB: "shafi",
            prayer_reminder_minutes_key(PrayerTime.FAJR): 10,
            prayer_reminder_minutes_key(PrayerTime.DHUHR): 25,
        },
    )
    entry.add_to_hass(hass)

    coordinator = MawaqeetDataUpdateCoordinator(hass, entry)
    assert coordinator._get_reminder_minutes(PrayerTime.FAJR) == 10
    assert coordinator._get_reminder_minutes(PrayerTime.DHUHR) == 25
    assert coordinator._get_reminder_minutes(PrayerTime.ASR) == DEFAULT_REMINDER_MINUTES


async def test_legacy_reminder_minutes_fallback(hass: HomeAssistant) -> None:
    """Test legacy global reminder_minutes is used as fallback."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
            CALCULATION_METHOD: "mwl",
        },
        options={MADHAB: "shafi", REMINDER_MINUTES: 20},
    )
    entry.add_to_hass(hass)

    coordinator = MawaqeetDataUpdateCoordinator(hass, entry)
    assert coordinator._get_reminder_minutes(PrayerTime.FAJR) == 20


async def test_scheduled_fire_resolves_device_id_at_fire_time(
    hass: HomeAssistant,
) -> None:
    """Test scheduled callbacks read device_id when firing, not when scheduling."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
        },
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    coordinator = MawaqeetDataUpdateCoordinator(hass, entry)
    entry.runtime_data = MawaqeetRuntimeData(coordinator=coordinator)

    fired: list[dict] = []

    def capture(event: Event) -> None:
        fired.append(event.data)

    hass.bus.async_listen(MAWAQEET_EVENT, capture)

    with patch.object(
        type(coordinator),
        "device_id",
        new_callable=PropertyMock,
        return_value="device-abc",
    ) as mock_device_id:
        fire_cb = coordinator._async_fire_prayer_event(
            PRAYER_TIME_TRIGGER, str(PrayerTime.FAJR)
        )
        mock_device_id.assert_not_called()
        fire_cb(datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC))
        await hass.async_block_till_done()
        mock_device_id.assert_called()

    assert fired
    assert fired[0]["device_id"] == "device-abc"
    assert fired[0]["prayer"] == str(PrayerTime.FAJR)
