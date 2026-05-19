"""Test device triggers."""

from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_TYPE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DOMAIN,
    PRAYER_REMINDER_TRIGGER,
    PRAYER_TIME_TRIGGER,
)
from custom_components.mawaqeet.device_trigger import async_get_triggers


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
