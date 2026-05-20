"""Test config flow."""

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DOMAIN,
    FAJR_ANGLE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    MADHAB,
)
from custom_components.mawaqeet.enum import CalculationMethod


def _location_unique_id(latitude: float, longitude: float) -> str:
    """Match config_flow._location_unique_id."""
    return f"{latitude:.6f}_{longitude:.6f}"


async def test_user_flow(hass: HomeAssistant) -> None:
    """Test user step leads to adjustment."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5, CONF_LONGITUDE: -0.12},
            CALCULATION_METHOD: "mwl",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "adjustment"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {MADHAB: "shafi"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Home"


async def test_duplicate_location(hass: HomeAssistant) -> None:
    """Test duplicate location is rejected."""
    location = {CONF_LATITUDE: 51.5, CONF_LONGITUDE: -0.12}
    MockConfigEntry(
        domain=DOMAIN,
        unique_id=_location_unique_id(
            location[CONF_LATITUDE], location[CONF_LONGITUDE]
        ),
        data={
            CONF_NAME: "Existing",
            CONF_LOCATION: location,
            CALCULATION_METHOD: "mwl",
        },
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Other",
            CONF_LOCATION: location,
            CALCULATION_METHOD: "mwl",
        },
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_flow(hass: HomeAssistant) -> None:
    """Test reconfigure updates entry data."""
    location = {CONF_LATITUDE: 51.5, CONF_LONGITUDE: -0.12}
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id=_location_unique_id(
            location[CONF_LATITUDE], location[CONF_LONGITUDE]
        ),
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: location,
            CALCULATION_METHOD: "mwl",
        },
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    new_location = {CONF_LATITUDE: 40.7, CONF_LONGITUDE: -74.0}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "NYC",
            CONF_LOCATION: new_location,
            CALCULATION_METHOD: "isna",
        },
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_NAME] == "NYC"
    assert entry.data[CONF_LOCATION] == new_location
    assert entry.data[CALCULATION_METHOD] == "isna"
    assert entry.unique_id == _location_unique_id(
        new_location[CONF_LATITUDE], new_location[CONF_LONGITUDE]
    )

    await hass.async_block_till_done()
    assert entry.state == ConfigEntryState.LOADED
    entry.runtime_data.coordinator.clear_event_sub()


async def test_custom_calculation_adjustment(hass: HomeAssistant) -> None:
    """Test custom calculation method shows angle fields in adjustment step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Custom",
            CONF_LOCATION: {CONF_LATITUDE: 51.5, CONF_LONGITUDE: -0.12},
            CALCULATION_METHOD: str(CalculationMethod.CUSTOM),
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "adjustment"
    assert FAJR_ANGLE in result["data_schema"].schema

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            MADHAB: "shafi",
            FAJR_ANGLE: 18.0,
            ISHAA_ANGLE: 17.0,
            ISHAA_INTERVAL: 0,
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    entry = hass.config_entries.async_entries(DOMAIN)[-1]
    assert entry.options[FAJR_ANGLE] == 18.0


async def test_options_flow_reload(hass: HomeAssistant) -> None:
    """Test saving options reloads the config entry."""
    location = {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278}
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id=_location_unique_id(
            location[CONF_LATITUDE], location[CONF_LONGITUDE]
        ),
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: location,
            CALCULATION_METHOD: "mwl",
        },
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state == ConfigEntryState.LOADED

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "adjustment"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {MADHAB: "hanafi"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert entry.options[MADHAB] == "hanafi"
