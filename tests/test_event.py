"""Test event platform."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DOMAIN,
    MADHAB,
    MAWAQEET_EVENT,
    PRAYER_TIME_TRIGGER,
)
from custom_components.mawaqeet.enum import PrayerTime
from custom_components.mawaqeet.event import LATEST_PRAYER_TIME


async def test_prayer_time_event_entity(hass: HomeAssistant) -> None:
    """Test event entity updates when bus event fires."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
            CALCULATION_METHOD: "mwl",
        },
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state == ConfigEntryState.LOADED

    coordinator = entry.runtime_data.coordinator
    device_id = coordinator.device_id
    assert device_id is not None

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "event", DOMAIN, f"{entry.entry_id}_{LATEST_PRAYER_TIME}"
    )
    assert entity_id is not None

    hass.bus.async_fire(
        MAWAQEET_EVENT,
        {
            "device_id": device_id,
            "type": PRAYER_TIME_TRIGGER,
            "prayer": str(PrayerTime.FAJR),
        },
    )
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes.get("event_type") == str(PrayerTime.FAJR)
