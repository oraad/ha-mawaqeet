from typing import TypedDict

from .const import (
    FAJR_ANGLE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    METHOD_ADJUSTMENTS,
    FAJR,
    SHURUQ,
    DHUHR,
    ASR,
    MAGHRIB,
    ISHAA,
)
from .enum import CalculationMethod


class MethodAdjustment(TypedDict):
    fajr: int
    shuruq: int
    dhuhr: int
    asr: int
    maghrib: int
    ishaa: int


class CalculationMethodParameter(TypedDict):
    fajr_angle: float
    ishaa_angle: float
    ishaa_interval: int
    method_adjustments: MethodAdjustment


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
