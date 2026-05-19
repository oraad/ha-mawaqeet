"""Test device triggers."""

import asyncio

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.trigger import TriggerInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DOMAIN,
    MADHAB,
    MAWAQEET_EVENT,
    PRAYER_REMINDER_TRIGGER,
    PRAYER_TIME_TRIGGER,
)
from custom_components.mawaqeet.device_trigger import (
    async_attach_trigger,
    async_get_triggers,
)
from custom_components.mawaqeet.enum import PrayerTime


async def test_get_triggers(hass: HomeAssistant) -> None:
    """Test device exposes prayer time and reminder triggers."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5, CONF_LONGITUDE: -0.12},
            CALCULATION_METHOD: "mwl",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert device is not None

    triggers = await async_get_triggers(hass, device.id)
    types = {t[CONF_TYPE] for t in triggers}
    assert types == {PRAYER_TIME_TRIGGER, PRAYER_REMINDER_TRIGGER}
    assert all(t["domain"] == DOMAIN for t in triggers)
    assert all(t["device_id"] == device.id for t in triggers)


async def test_attach_trigger_fires(hass: HomeAssistant) -> None:
    """Test attached device trigger runs when matching bus event fires."""
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

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert device is not None

    fired = asyncio.Event()

    async def action(run_variables: dict, _context: Context | None) -> None:
        assert "trigger" in run_variables
        assert run_variables["trigger"]["platform"] == "device"
        fired.set()

    trigger_config = {
        CONF_PLATFORM: "device",
        "domain": DOMAIN,
        CONF_DEVICE_ID: device.id,
        CONF_TYPE: PRAYER_TIME_TRIGGER,
    }

    unsub = await async_attach_trigger(
        hass,
        trigger_config,
        action,
        TriggerInfo(
            domain=DOMAIN,
            name="test",
            platform="device",
            home_assistant_start=False,
            variables=None,
            trigger_data={},
        ),
    )

    hass.bus.async_fire(
        MAWAQEET_EVENT,
        {
            "device_id": device.id,
            "type": PRAYER_TIME_TRIGGER,
            "prayer": str(PrayerTime.FAJR),
        },
    )
    await hass.async_block_till_done()
    assert fired.is_set()

    unsub()
