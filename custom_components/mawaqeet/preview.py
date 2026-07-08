"""Config and options flow prayer-time preview (websocket)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.const import ATTR_FRIENDLY_NAME, ATTR_ICON, CONF_LOCATION
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .calculation import compute_prayer_times_from_options
from .const import (
    CALCULATION_METHOD,
    CUSTOM_PREVIEW_DEFAULTS,
    DOMAIN,
    MADHAB,
)
from .enum import CalculationMethod, Madhab, PrayerTime, PrayerTimeOption
from .options import get_calculation_method

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from homeassistant.components.websocket_api import ActiveConnection
    from homeassistant.core import HomeAssistant

PREVIEW_PRAYERS: tuple[PrayerTime, ...] = (
    PrayerTime.FAJR,
    PrayerTime.SHURUQ,
    PrayerTime.DHUHR,
    PrayerTime.ASR,
    PrayerTime.MAGHRIB,
    PrayerTime.ISHAA,
)

_PREVIEW_TITLES: dict[PrayerTime, str] = {
    PrayerTime.FAJR: "Fajr",
    PrayerTime.SHURUQ: "Shuruq",
    PrayerTime.DHUHR: "Dhuhr",
    PrayerTime.ASR: "Asr",
    PrayerTime.MAGHRIB: "Maghrib",
    PrayerTime.ISHAA: "Ishaa",
}


def format_preview_state(prayer_times: Mapping[PrayerTime, datetime]) -> str:
    """Format today's prayer times as a compact single-row schedule."""
    parts: list[str] = []
    for prayer in PREVIEW_PRAYERS:
        when = prayer_times[prayer]
        local = dt_util.as_local(when)
        parts.append(f"{_PREVIEW_TITLES[prayer]} {local.strftime('%H:%M')}")
    return " · ".join(parts)


def _preview_attributes(
    data: Mapping[str, Any],
) -> dict[str, Any]:
    """Build attributes for the generic entity preview row."""
    prayer_times: Mapping[PrayerTime, datetime] = data["prayer_times"]
    config = data["prayer_times_config"]
    attributes: dict[str, Any] = {
        ATTR_FRIENDLY_NAME: "Today's prayer times",
        ATTR_ICON: "mdi:mosque",
        CALCULATION_METHOD: config[PrayerTimeOption.CALCULATION_METHOD],
        MADHAB: config[PrayerTimeOption.MADHAB],
    }
    for prayer in PREVIEW_PRAYERS:
        attributes[str(prayer)] = dt_util.as_local(prayer_times[prayer]).isoformat()
    return attributes


def _ensure_custom_angle_defaults(options: dict[str, Any]) -> dict[str, Any]:
    """Seed custom angles when previewing custom before the adjustment step."""
    if options.get(CALCULATION_METHOD) != str(CalculationMethod.CUSTOM):
        return options
    seeded = dict(options)
    for key, value in CUSTOM_PREVIEW_DEFAULTS.items():
        seeded.setdefault(key, value)
    return seeded


def _merge_preview_params(
    hass: HomeAssistant,
    flow_type: str,
    flow_id: str,
    user_input: dict[str, Any],
) -> tuple[dict[str, float], dict[str, Any]]:
    """Resolve location + options for the current preview subscription."""
    if flow_type == "config_flow":
        flow = hass.config_entries.flow.async_get(flow_id)
        context = flow["context"]
        location = context.get(CONF_LOCATION)
        if not location:
            msg = "Location not available for preview"
            raise HomeAssistantError(msg)

        step_id = flow.get("step_id")
        options: dict[str, Any] = {
            MADHAB: str(Madhab.SHAFI),
            CALCULATION_METHOD: context.get(
                CALCULATION_METHOD, str(CalculationMethod.MUSLIM_WORLD_LEAGUE)
            ),
        }
        if step_id == "calculation":
            options[CALCULATION_METHOD] = user_input.get(
                CALCULATION_METHOD, options[CALCULATION_METHOD]
            )
        else:
            options.update(user_input)
            options[CALCULATION_METHOD] = context.get(
                CALCULATION_METHOD, options[CALCULATION_METHOD]
            )
        return location, _ensure_custom_angle_defaults(options)

    if flow_type == "options_flow":
        flow = hass.config_entries.options.async_get(flow_id)
        config_entry = hass.config_entries.async_get_entry(flow["handler"])
        if config_entry is None:
            msg = "Config entry not found"
            raise HomeAssistantError(msg)

        location = config_entry.data.get(CONF_LOCATION)
        if not location:
            msg = "Location not available for preview"
            raise HomeAssistantError(msg)

        step_id = flow.get("step_id")
        options = dict(config_entry.options)
        if step_id == "calculation":
            options[CALCULATION_METHOD] = user_input.get(
                CALCULATION_METHOD, get_calculation_method(config_entry)
            )
        else:
            options.update(user_input)
            options[CALCULATION_METHOD] = flow["context"].get(
                CALCULATION_METHOD,
                options.get(CALCULATION_METHOD, get_calculation_method(config_entry)),
            )
        return location, _ensure_custom_angle_defaults(options)

    msg = f"Unsupported flow type: {flow_type}"
    raise HomeAssistantError(msg)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/start_preview",
        vol.Required("flow_id"): str,
        vol.Required("flow_type"): vol.Any("config_flow", "options_flow"),
        vol.Required("user_input"): dict,
    }
)
@websocket_api.async_response
async def ws_start_preview(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Generate a live prayer-times preview for config or options flows."""
    try:
        location, options = _merge_preview_params(
            hass, msg["flow_type"], msg["flow_id"], msg["user_input"]
        )
        data = await hass.async_add_executor_job(
            compute_prayer_times_from_options, location, options
        )
    except Exception as err:  # noqa: BLE001 - surface as preview error
        error_message = str(err)
        connection.send_result(msg["id"])
        connection.send_message(
            websocket_api.event_message(msg["id"], {"error": error_message})
        )
        connection.subscriptions[msg["id"]] = lambda: None
        return

    state = format_preview_state(data["prayer_times"])
    attributes = _preview_attributes(data)

    connection.send_result(msg["id"])
    connection.send_message(
        websocket_api.event_message(
            msg["id"],
            {"state": state, "attributes": attributes},
        )
    )
    connection.subscriptions[msg["id"]] = lambda: None


async def async_setup_preview(hass: HomeAssistant) -> None:
    """Register the preview websocket command once per hass instance."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("preview_registered"):
        return
    websocket_api.async_register_command(hass, ws_start_preview)
    domain_data["preview_registered"] = True
