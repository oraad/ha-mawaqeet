"""Test options migration."""

from custom_components.mawaqeet.const import REMINDER_MINUTES
from custom_components.mawaqeet.enum import PrayerTime, prayer_reminder_minutes_key
from custom_components.mawaqeet.options import migrate_options, options_need_migration


def test_migrate_legacy_reminder_minutes() -> None:
    """Legacy global reminder_minutes is copied to each prayer."""
    options = {REMINDER_MINUTES: 20, "madhab": "shafi"}
    migrated = migrate_options(options)

    assert REMINDER_MINUTES not in migrated
    for prayer in (
        PrayerTime.FAJR,
        PrayerTime.SHURUQ,
        PrayerTime.DHUHR,
        PrayerTime.ASR,
        PrayerTime.MAGHRIB,
        PrayerTime.ISHAA,
    ):
        assert migrated[prayer_reminder_minutes_key(prayer)] == 20


def test_options_need_migration() -> None:
    """Detect legacy-only reminder options."""
    assert options_need_migration({REMINDER_MINUTES: 15, "madhab": "shafi"})
    assert not options_need_migration(
        {prayer_reminder_minutes_key(PrayerTime.FAJR): 10, "madhab": "shafi"}
    )
