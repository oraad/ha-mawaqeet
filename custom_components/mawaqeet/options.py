"""Options helpers for Mawaqeet."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .const import (
    CALCULATION_METHOD,
    DEFAULT_REMINDER_MINUTES,
    FAJR_ANGLE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    REMINDER_MINUTES,
)
from .enum import (
    REMINDER_SCHEDULE_PRAYERS,
    CalculationMethod,
    prayer_reminder_minutes_key,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

CUSTOM_ONLY_OPTION_KEYS = (FAJR_ANGLE, ISHAA_ANGLE, ISHAA_INTERVAL)


def get_calculation_method(config_entry: ConfigEntry) -> str:
    """Return the calculation method id from options, with legacy data fallback."""
    return config_entry.options.get(
        CALCULATION_METHOD,
        config_entry.data.get(
            CALCULATION_METHOD, str(CalculationMethod.MUSLIM_WORLD_LEAGUE)
        ),
    )


def migrate_options(options: dict[str, Any]) -> dict[str, Any]:
    """Migrate reminders and strip custom-only keys for preset methods."""
    migrated = dict(options)
    legacy_minutes = migrated.get(REMINDER_MINUTES)
    changed = False

    for prayer in REMINDER_SCHEDULE_PRAYERS:
        key = prayer_reminder_minutes_key(prayer)
        if key not in migrated:
            migrated[key] = (
                int(legacy_minutes)
                if legacy_minutes is not None
                else DEFAULT_REMINDER_MINUTES
            )
            changed = True

    if changed and REMINDER_MINUTES in migrated:
        del migrated[REMINDER_MINUTES]

    method = migrated.get(CALCULATION_METHOD)
    if method is not None and method != str(CalculationMethod.CUSTOM):
        for key in CUSTOM_ONLY_OPTION_KEYS:
            migrated.pop(key, None)

    return migrated


def options_need_migration(options: dict[str, Any]) -> bool:
    """Return True if options still use legacy reminder_minutes only."""
    if REMINDER_MINUTES not in options:
        return False
    return any(
        prayer_reminder_minutes_key(prayer) not in options
        for prayer in REMINDER_SCHEDULE_PRAYERS
    )


def calculation_method_needs_migration(config_entry: ConfigEntry) -> bool:
    """Return True if calculation_method is still present in entry data."""
    return CALCULATION_METHOD in config_entry.data


def migrate_calculation_method(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Move calculation method from entry data into options and strip data."""
    if not calculation_method_needs_migration(config_entry):
        return

    method = config_entry.data[CALCULATION_METHOD]
    new_data = {
        key: value
        for key, value in config_entry.data.items()
        if key != CALCULATION_METHOD
    }
    new_options = dict(config_entry.options)
    if CALCULATION_METHOD not in new_options:
        new_options[CALCULATION_METHOD] = method
    new_options = migrate_options(new_options)
    hass.config_entries.async_update_entry(
        config_entry, data=new_data, options=new_options
    )
