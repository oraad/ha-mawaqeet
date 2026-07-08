"""Test config flow."""

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.calculation import compute_prayer_times
from custom_components.mawaqeet.config_flow import _build_adjustment_schema
from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DOMAIN,
    FAJR_ANGLE,
    HIGH_LATITUDE_RULE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    MADHAB,
)
from custom_components.mawaqeet.enum import CalculationMethod, PrayerTime


def _location_unique_id(latitude: float, longitude: float) -> str:
    """Match config_flow._location_unique_id."""
    return f"{latitude:.6f}_{longitude:.6f}"


async def test_user_flow(hass: HomeAssistant) -> None:
    """Test user step leads to calculation then adjustment."""
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
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "calculation"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: "mwl"},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "adjustment"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {MADHAB: "shafi"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Home"
    assert CALCULATION_METHOD not in result["data"]
    assert result["options"][CALCULATION_METHOD] == "mwl"


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
        },
        options={CALCULATION_METHOD: "mwl"},
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Other",
            CONF_LOCATION: location,
        },
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_flow(hass: HomeAssistant) -> None:
    """Test reconfigure updates entry data without touching calculation method."""
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
        },
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
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
        },
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_NAME] == "NYC"
    assert entry.data[CONF_LOCATION] == new_location
    assert CALCULATION_METHOD not in entry.data
    assert entry.options[CALCULATION_METHOD] == "mwl"
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
        },
    )
    assert result["step_id"] == "calculation"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: str(CalculationMethod.CUSTOM)},
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
    assert entry.options[CALCULATION_METHOD] == str(CalculationMethod.CUSTOM)
    assert entry.options[FAJR_ANGLE] == 18.0
    assert CALCULATION_METHOD not in entry.data


async def test_options_flow_change_method(hass: HomeAssistant) -> None:
    """Test options flow can change calculation method then adjustments."""
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
        },
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state == ConfigEntryState.LOADED

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "calculation"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: "isna"},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "adjustment"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {MADHAB: "hanafi"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert entry.options[CALCULATION_METHOD] == "isna"
    assert entry.options[MADHAB] == "hanafi"
    entry.runtime_data.coordinator.clear_event_sub()


async def test_options_flow_custom_shows_angles(hass: HomeAssistant) -> None:
    """Test switching to custom method in options shows angle fields."""
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
        },
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: str(CalculationMethod.CUSTOM)},
    )
    assert result["step_id"] == "adjustment"
    assert FAJR_ANGLE in result["data_schema"].schema
    entry.runtime_data.coordinator.clear_event_sub()


async def test_migrate_calculation_method_from_data(hass: HomeAssistant) -> None:
    """Test setup migrates calculation method from data into options."""
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
            CALCULATION_METHOD: "isna",
        },
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state == ConfigEntryState.LOADED
    assert CALCULATION_METHOD not in entry.data
    assert entry.options[CALCULATION_METHOD] == "isna"
    entry.runtime_data.coordinator.clear_event_sub()


async def test_migrate_strips_method_when_in_both_data_and_options(
    hass: HomeAssistant,
) -> None:
    """Test dual data+options method keeps options and strips data."""
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
        options={CALCULATION_METHOD: "isna", MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    assert CALCULATION_METHOD not in entry.data
    assert entry.options[CALCULATION_METHOD] == "isna"
    entry.runtime_data.coordinator.clear_event_sub()


async def test_options_custom_to_mwl_strips_angles(hass: HomeAssistant) -> None:
    """Test custom→MWL drops angles and matches clean MWL Ishaa."""
    location = {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278}
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id=_location_unique_id(
            location[CONF_LATITUDE], location[CONF_LONGITUDE]
        ),
        data={CONF_NAME: "Home", CONF_LOCATION: location},
        options={
            CALCULATION_METHOD: str(CalculationMethod.CUSTOM),
            MADHAB: "shafi",
            FAJR_ANGLE: 12.0,
            ISHAA_ANGLE: 12.0,
            ISHAA_INTERVAL: 90,
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: "mwl"},
    )
    assert result["step_id"] == "adjustment"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {MADHAB: "shafi"},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert entry.options[CALCULATION_METHOD] == "mwl"
    assert FAJR_ANGLE not in entry.options
    assert ISHAA_ANGLE not in entry.options
    assert ISHAA_INTERVAL not in entry.options

    clean_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_NAME: "Clean", CONF_LOCATION: location},
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    asserted = compute_prayer_times(entry)
    clean = compute_prayer_times(clean_entry)
    assert (
        asserted["prayer_times"][PrayerTime.ISHAA]
        == clean["prayer_times"][PrayerTime.ISHAA]
    )
    entry.runtime_data.coordinator.clear_event_sub()


def test_adjustment_schema_includes_high_latitude_for_preset() -> None:
    """Test high latitude rule is available for non-custom methods."""
    schema = _build_adjustment_schema("mwl")
    assert HIGH_LATITUDE_RULE in schema.schema
    assert FAJR_ANGLE not in schema.schema
