"""Test integration setup and unload."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import CALCULATION_METHOD, DOMAIN, MADHAB


async def test_setup_and_unload(hass: HomeAssistant) -> None:
    """Test setup and unload."""
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
    assert entry.runtime_data is not None
    assert entry.runtime_data.coordinator.data is not None

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state == ConfigEntryState.NOT_LOADED
