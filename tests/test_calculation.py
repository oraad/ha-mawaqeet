"""Test prayer time calculation."""

from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.calculation import (
    async_compute_prayer_times,
    compute_prayer_times,
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
    assert async_data["prayer_times"][PrayerTime.FAJR] == sync_data["prayer_times"][
        PrayerTime.FAJR
    ]
