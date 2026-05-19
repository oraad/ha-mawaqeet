"""Test sensor platform."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import CALCULATION_METHOD, DOMAIN, MADHAB
from custom_components.mawaqeet.enum import PrayerTime, PrayerTimeOption


async def test_sensor_states(hass: HomeAssistant) -> None:
    """Test prayer time and diagnostic sensors have values after setup."""
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

    registry = er.async_get(hass)
    fajr_uid = f"{entry.entry_id}_{PrayerTime.FAJR}"
    fajr = registry.async_get_entity_id("sensor", DOMAIN, fajr_uid)
    method = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_{PrayerTimeOption.CALCULATION_METHOD}"
    )
    assert fajr is not None
    assert hass.states.get(fajr) is not None
    assert hass.states.get(method) is not None
    assert hass.states.get(method).state == "mwl"


async def test_diagnostic_sensors_disabled_by_default(hass: HomeAssistant) -> None:
    """Test optional diagnostic sensors are disabled by default."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
            CALCULATION_METHOD: "mwl",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    registry = er.async_get(hass)
    night = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_{PrayerTimeOption.NIGHT_DURATION}"
    )
    assert night is not None
    entry_entity = registry.async_get(night)
    assert entry_entity is not None
    assert entry_entity.disabled_by is er.RegistryEntryDisabler.INTEGRATION
