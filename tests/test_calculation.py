"""Test prayer time calculation."""

from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.calculation import (
    async_compute_prayer_times,
    compute_prayer_times,
    compute_prayer_times_from_options,
)
from custom_components.mawaqeet.const import CALCULATION_METHOD, DOMAIN, MADHAB
from custom_components.mawaqeet.enum import PrayerTime, PrayerTimeOption


async def test_compute_prayer_times(hass: HomeAssistant) -> None:
    """Test sync and async calculation return prayer times."""
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

    sync_data = compute_prayer_times(entry)
    async_data = await async_compute_prayer_times(hass, entry)

    assert set(sync_data["prayer_times"]) == set(PrayerTime)
    assert (
        sync_data["prayer_times_config"][PrayerTimeOption.CALCULATION_METHOD] == "mwl"
    )
    assert (
        async_data["prayer_times"][PrayerTime.FAJR]
        == sync_data["prayer_times"][PrayerTime.FAJR]
    )


async def test_compute_prayer_times_from_options_matches_entry(
    hass: HomeAssistant,
) -> None:
    """Test param-based compute matches ConfigEntry-based compute."""
    location = {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278}
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Home", CONF_LOCATION: location},
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    from_entry = compute_prayer_times(entry)
    from_options = compute_prayer_times_from_options(
        location,
        {CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )

    assert from_options["prayer_times"] == from_entry["prayer_times"]
    assert (
        from_options["prayer_times_config"][PrayerTimeOption.CALCULATION_METHOD]
        == "mwl"
    )


def test_offset_changes_prayer_times() -> None:
    """Test prayer offsets change computed times."""
    location = {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278}
    base = compute_prayer_times_from_options(
        location, {CALCULATION_METHOD: "mwl", MADHAB: "shafi"}
    )
    shifted = compute_prayer_times_from_options(
        location,
        {CALCULATION_METHOD: "mwl", MADHAB: "shafi", "fajr": 10},
    )
    assert (
        shifted["prayer_times"][PrayerTime.FAJR]
        != base["prayer_times"][PrayerTime.FAJR]
    )


def test_preset_ignores_leftover_custom_interval() -> None:
    """Test non-custom compute ignores stale ishaa_interval in options."""
    location = {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278}
    clean = compute_prayer_times_from_options(
        location, {CALCULATION_METHOD: "mwl", MADHAB: "shafi"}
    )
    polluted = compute_prayer_times_from_options(
        location,
        {
            CALCULATION_METHOD: "mwl",
            MADHAB: "shafi",
            "ishaa_interval": 90,
            "fajr_angle": 12.0,
            "ishaa_angle": 12.0,
        },
    )
    assert (
        polluted["prayer_times"][PrayerTime.ISHAA]
        == clean["prayer_times"][PrayerTime.ISHAA]
    )
    assert polluted["prayer_times_config"][PrayerTimeOption.ISHAA_INTERVAL] == 0
