"""Constants for mawaqeet."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Mawaqeet"
DOMAIN = "mawaqeet"
ATTRIBUTION = ""
DOCUMENTATION_URL = "https://github.com/oraad/ha-mawaqeet"

MAWAQEET_EVENT = "mawaqeet_event"
PRAYER_TIME_TRIGGER = "prayer_time"
PRAYER_REMINDER_TRIGGER = "prayer_reminder"

PRAYER = "prayer"
FAJR = "fajr"
SHURUQ = "shuruq"
DHUHR = "dhuhr"
ASR = "asr"
MAGHRIB = "maghrib"
ISHAA = "ishaa"

CALCULATION_METHOD = "calculation_method"
METHOD_ADJUSTMENTS = "method_adjustments"
MADHAB = "madhab"
FAJR_ANGLE = "fajr_angle"
ISHAA_ANGLE = "ishaa_angle"
ISHAA_INTERVAL = "ishaa_interval"
HIGH_LATITUDE_RULE = "high_latitude_rule"
REMINDER_ENABLED = "reminder_enabled"
REMINDER_MINUTES = "reminder_minutes"  # legacy global fallback
DEFAULT_REMINDER_MINUTES = 15
