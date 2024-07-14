"""Calculation Method."""

from dataclasses import dataclass
from typing import NotRequired, TypedDict

from .const import (
    ASR,
    DHUHR,
    FAJR_ANGLE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    MAGHRIB,
    METHOD_ADJUSTMENTS,
    SHURUQ,
)
from .enum import CalculationMethod


@dataclass(frozen=True)
class PrayerAdjustments:
    """Prayer Adjustments."""

    fajr: int = 0
    # Fajr offset in minutes
    shuruq: int = 0
    # Sunrise offset in minutes
    dhuhr: int = 0
    # Dhuhr offset in minutes
    asr: int = 0
    # Asr offset in minutes
    maghrib: int = 0
    # Maghrib offset in minutes
    ishaa: int = 0
    # Isha offset in minutes


class MethodAdjustment(TypedDict):
    """Method adjustment dict."""

    fajr: NotRequired[int]
    shuruq: NotRequired[int]
    dhuhr: NotRequired[int]
    asr: NotRequired[int]
    maghrib: NotRequired[int]
    ishaa: NotRequired[int]


class CalculationMethodParameter(TypedDict):
    """Calculation Method Paramter."""

    fajr_angle: NotRequired[float]
    ishaa_angle: NotRequired[float]
    ishaa_interval: NotRequired[int]
    method_adjustments: NotRequired[MethodAdjustment]


CALCULATION_METHOD_PARAMETERS: dict[CalculationMethod, CalculationMethodParameter] = {
    CalculationMethod.CUSTOM: {},
    CalculationMethod.MUSLIM_WORLD_LEAGUE: {
        FAJR_ANGLE: 18.0,
        ISHAA_ANGLE: 17.0,
        METHOD_ADJUSTMENTS: {DHUHR: 1},
    },
    CalculationMethod.EGYPTIAN: {
        FAJR_ANGLE: 19.5,
        ISHAA_ANGLE: 17.5,
        METHOD_ADJUSTMENTS: {DHUHR: 1},
    },
    CalculationMethod.KARACHI: {
        FAJR_ANGLE: 18.0,
        ISHAA_ANGLE: 18.0,
        METHOD_ADJUSTMENTS: {DHUHR: 1},
    },
    CalculationMethod.UMM_AL_QURA: {FAJR_ANGLE: 18.5, ISHAA_INTERVAL: 90},
    CalculationMethod.DUBAI: {
        FAJR_ANGLE: 18.2,
        ISHAA_ANGLE: 18.2,
        METHOD_ADJUSTMENTS: {SHURUQ: -3, DHUHR: 3, ASR: 3, MAGHRIB: 3},
    },
    CalculationMethod.MOON_SIGHTING_COMMITTEE: {
        FAJR_ANGLE: 18.0,
        ISHAA_ANGLE: 18.0,
        METHOD_ADJUSTMENTS: {DHUHR: 5, MAGHRIB: 3},
    },
    CalculationMethod.ISNA: {
        FAJR_ANGLE: 15.0,
        ISHAA_ANGLE: 15.0,
        METHOD_ADJUSTMENTS: {DHUHR: 1},
    },
    CalculationMethod.KUWAIT: {FAJR_ANGLE: 18.0, ISHAA_ANGLE: 17.5},
    CalculationMethod.QATAR: {FAJR_ANGLE: 18.0, ISHAA_INTERVAL: 90},
    CalculationMethod.SINGAPORE: {
        FAJR_ANGLE: 20.0,
        ISHAA_ANGLE: 18.0,
        METHOD_ADJUSTMENTS: {DHUHR: 1},
    },
    CalculationMethod.UOIF: {FAJR_ANGLE: 12.0, ISHAA_ANGLE: 12.0},
}
