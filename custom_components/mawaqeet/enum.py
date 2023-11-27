from enum import StrEnum, auto


class PrayerTime(StrEnum):
    FAJR = auto()
    SHURUQ = auto()
    DHUHR = auto()
    ASR = auto()
    MAGHRIB = auto()
    ISHAA = auto()
    MIDNIGHT = auto()
    LAST_THIRD = auto()


class PrayerTimeOption(StrEnum):
    CALCULATION_METHOD = auto()
    MADHAB = auto()
    NIGHT_LENGTH = auto()  # From Maghtib to Shuruq
    NIGHT_DURATION = auto()  # From Maghrib to Fajr
    HIGH_LATITUDE_RULE = auto()
    FAJR_ANGLE = auto()
    ISHAA_ANGLE = auto()
    ISHAA_INTERVAL = auto()
    FAJR_OFFSET = auto()
    SHURUQ_OFFSET = auto()
    DHUHR_OFFSET = auto()
    ASR_OFFSET = auto()
    MAGHRIB_OFFSET = auto()
    ISHAA_OFFSET = auto()


class PrayerTimeReminder(StrEnum):
    FAJR_REMINDER = auto()
    SHURUQ_REMINDER = auto()
    DHUHR_REMINDER = auto()
    ASR_REMINDER = auto()
    MAGHRIB_REMINDER = auto()
    ISHAA_REMINDER = auto()


class CalculationMethod(StrEnum):
    MUSLIM_WORLD_LEAGUE = "mwl"
    EGYPTIAN = "egyptian"
    KARACHI = "karachi"
    UMM_AL_QURA = "umm_al_qura"
    DUBAI = "dubai"
    MOON_SIGHTING_COMMITTEE = "msc"
    ISNA = "isna"
    KUWAIT = "kuwait"
    QATAR = "qatar"
    SINGAPORE = "singapore"
    UOIF = "uoif"
    CUSTOM = "custom"


class PrayerAdjustment(StrEnum):
    FAJR = auto()
    SHURUQ = auto()
    DHUHR = auto()
    ASR = auto()
    MAGHRIB = auto()
    ISHAA = auto()


class Madhab(StrEnum):
    SHAFI = auto()
    HANAFI = auto()


class HighLatitudeRule(StrEnum):
    MIDDLE_OF_THE_NIGHT = auto()
    SEVENTH_OF_THE_NIGHT = auto()
    TWILIGHT_ANGLE = auto()
