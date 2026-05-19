"""Test diagnostics."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import CALCULATION_METHOD, DOMAIN, MADHAB
from custom_components.mawaqeet.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics_redacts_location(hass: HomeAssistant) -> None:
    """Test diagnostics redacts coordinates."""
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
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state == ConfigEntryState.LOADED

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["entry_id"] == entry.entry_id
    assert result["data"][CONF_LOCATION] == "**REDACTED**"
    assert "fajr" in result["prayer_times"]
    assert result["options"][MADHAB] == "shafi"
