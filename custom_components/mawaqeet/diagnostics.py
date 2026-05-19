"""Diagnostics support for Mawaqeet."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE

from .enum import REMINDER_SCHEDULE_PRAYERS

if TYPE_CHECKING:
    from .data import MawaqeetConfigEntry

TO_REDACT = {
    CONF_LOCATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
}


async def async_get_config_entry_diagnostics(
    _hass: object, entry: MawaqeetConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    data = coordinator.data
    prayer_times = (
        {str(prayer): dt.isoformat() for prayer, dt in data["prayer_times"].items()}
        if data
        else {}
    )
    return {
        "entry_id": entry.entry_id,
        "unique_id": entry.unique_id,
        "data": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "prayer_times": prayer_times,
        "prayer_times_config": dict(data["prayer_times_config"]) if data else {},
        "reminder_schedule_prayers": [str(p) for p in REMINDER_SCHEDULE_PRAYERS],
    }
