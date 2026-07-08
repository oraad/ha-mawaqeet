"""Test in-flow prayer times preview."""

from unittest.mock import MagicMock

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.calculation import (
    compute_prayer_times_from_options,
)
from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DOMAIN,
    MADHAB,
)
from custom_components.mawaqeet.enum import CalculationMethod, PrayerTime
from custom_components.mawaqeet.preview import (
    async_setup_preview,
    format_preview_state,
    ws_start_preview,
)


async def _call_preview(
    hass: HomeAssistant,
    connection: MagicMock,
    msg: dict,
) -> None:
    """Invoke the async preview handler (bypass scheduling wrapper)."""
    await ws_start_preview.__wrapped__(hass, connection, msg)


def test_format_preview_state_contains_prayers() -> None:
    """Test preview state is a compact schedule string."""
    data = compute_prayer_times_from_options(
        {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
        {CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    state = format_preview_state(data["prayer_times"])
    assert "Fajr" in state
    assert "Dhuhr" in state
    assert "Ishaa" in state
    assert " · " in state


async def test_config_flow_forms_include_preview(hass: HomeAssistant) -> None:
    """Test calculation and adjustment steps advertise preview."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5, CONF_LONGITUDE: -0.12},
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "calculation"
    assert result.get("preview") == DOMAIN

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: "mwl"},
    )
    assert result["step_id"] == "adjustment"
    assert result.get("preview") == DOMAIN


async def test_options_flow_forms_include_preview(hass: HomeAssistant) -> None:
    """Test options calculation and adjustment steps advertise preview."""
    location = {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278}
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id=f"{location[CONF_LATITUDE]:.6f}_{location[CONF_LONGITUDE]:.6f}",
        data={CONF_NAME: "Home", CONF_LOCATION: location},
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "calculation"
    assert result.get("preview") == DOMAIN

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: "isna"},
    )
    assert result["step_id"] == "adjustment"
    assert result.get("preview") == DOMAIN
    entry.runtime_data.coordinator.clear_event_sub()


async def test_ws_preview_config_adjustment(hass: HomeAssistant) -> None:
    """Test websocket preview returns schedule for config adjustment step."""
    await async_setup_preview(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: "mwl"},
    )
    assert result["step_id"] == "adjustment"
    flow_id = result["flow_id"]

    messages: list[dict] = []

    def send_message(msg: dict | str | bytes) -> None:
        if isinstance(msg, dict):
            messages.append(msg)

    connection = MagicMock()
    connection.send_message = send_message
    connection.send_result = MagicMock(
        side_effect=lambda msg_id, result=None: messages.append(
            {"id": msg_id, "type": "result", "success": True, "result": result}
        )
    )
    connection.subscriptions = {}

    await _call_preview(
        hass,
        connection,
        {
            "id": 1,
            "type": f"{DOMAIN}/start_preview",
            "flow_type": "config_flow",
            "flow_id": flow_id,
            "user_input": {MADHAB: "shafi", "fajr": 0},
        },
    )

    events = [m for m in messages if m.get("type") == "event"]
    assert events
    preview = events[0]["event"]
    assert "error" not in preview
    assert "Fajr" in preview["state"]
    assert preview["attributes"][str(PrayerTime.FAJR)]


async def test_ws_preview_offset_changes_state(hass: HomeAssistant) -> None:
    """Test changing fajr offset changes preview state."""
    await async_setup_preview(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CALCULATION_METHOD: "mwl"},
    )
    flow_id = result["flow_id"]

    async def _preview(user_input: dict) -> str:
        messages: list[dict] = []

        def send_message(msg: dict | str | bytes) -> None:
            if isinstance(msg, dict):
                messages.append(msg)

        connection = MagicMock()
        connection.send_message = send_message
        connection.send_result = MagicMock(
            side_effect=lambda msg_id, result=None: messages.append(
                {"id": msg_id, "type": "result", "success": True, "result": result}
            )
        )
        connection.subscriptions = {}
        await _call_preview(
            hass,
            connection,
            {
                "id": 1,
                "type": f"{DOMAIN}/start_preview",
                "flow_type": "config_flow",
                "flow_id": flow_id,
                "user_input": user_input,
            },
        )
        events = [m for m in messages if m.get("type") == "event"]
        assert events
        return events[0]["event"]["state"]

    state_zero = await _preview({MADHAB: "shafi", "fajr": 0})
    state_shifted = await _preview({MADHAB: "shafi", "fajr": 15})
    assert state_zero != state_shifted


async def test_ws_preview_options_calculation(hass: HomeAssistant) -> None:
    """Test options calculation-step preview uses entry madhab/offsets."""
    await async_setup_preview(hass)
    location = {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278}
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id=f"{location[CONF_LATITUDE]:.6f}_{location[CONF_LONGITUDE]:.6f}",
        data={CONF_NAME: "Home", CONF_LOCATION: location},
        options={CALCULATION_METHOD: "mwl", MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "calculation"
    flow_id = result["flow_id"]

    messages: list[dict] = []

    def send_message(msg: dict | str | bytes) -> None:
        if isinstance(msg, dict):
            messages.append(msg)

    connection = MagicMock()
    connection.send_message = send_message
    connection.send_result = MagicMock(
        side_effect=lambda msg_id, result=None: messages.append(
            {"id": msg_id, "type": "result", "success": True, "result": result}
        )
    )
    connection.subscriptions = {}

    await _call_preview(
        hass,
        connection,
        {
            "id": 1,
            "type": f"{DOMAIN}/start_preview",
            "flow_type": "options_flow",
            "flow_id": flow_id,
            "user_input": {CALCULATION_METHOD: "isna"},
        },
    )

    events = [m for m in messages if m.get("type") == "event"]
    assert events
    preview = events[0]["event"]
    assert "Fajr" in preview["state"]
    assert preview["attributes"][CALCULATION_METHOD] == "isna"
    entry.runtime_data.coordinator.clear_event_sub()


async def test_ws_preview_custom_method_seeds_angles(hass: HomeAssistant) -> None:
    """Test calculation-step custom preview uses non-zero default angles."""
    await async_setup_preview(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
        },
    )
    assert result["step_id"] == "calculation"
    flow_id = result["flow_id"]

    messages: list[dict] = []

    def send_message(msg: dict | str | bytes) -> None:
        if isinstance(msg, dict):
            messages.append(msg)

    connection = MagicMock()
    connection.send_message = send_message
    connection.send_result = MagicMock(
        side_effect=lambda msg_id, result=None: messages.append(
            {"id": msg_id, "type": "result", "success": True, "result": result}
        )
    )
    connection.subscriptions = {}

    await _call_preview(
        hass,
        connection,
        {
            "id": 1,
            "type": f"{DOMAIN}/start_preview",
            "flow_type": "config_flow",
            "flow_id": flow_id,
            "user_input": {CALCULATION_METHOD: str(CalculationMethod.CUSTOM)},
        },
    )

    events = [m for m in messages if m.get("type") == "event"]
    assert events
    preview = events[0]["event"]
    assert "error" not in preview
    assert "Fajr" in preview["state"]
    assert preview["attributes"][CALCULATION_METHOD] == str(CalculationMethod.CUSTOM)
