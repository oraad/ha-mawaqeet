"""Options helpers for Mawaqeet."""

from __future__ import annotations

from typing import Any

from .const import DEFAULT_REMINDER_MINUTES, REMINDER_MINUTES
from .enum import REMINDER_SCHEDULE_PRAYERS, prayer_reminder_minutes_key


def migrate_options(options: dict[str, Any]) -> dict[str, Any]:
    """Migrate legacy global reminder_minutes to per-prayer keys."""
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

    return migrated


def options_need_migration(options: dict[str, Any]) -> bool:
    """Return True if options still use legacy reminder_minutes only."""
    if REMINDER_MINUTES not in options:
        return False
    return any(
        prayer_reminder_minutes_key(prayer) not in options
        for prayer in REMINDER_SCHEDULE_PRAYERS
    )
