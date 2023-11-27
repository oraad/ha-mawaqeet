from typing import Optional

from adhanpy.calculation.Madhab import Madhab as AdhanMadhab
from adhanpy.calculation.HighLatitudeRule import (
    HighLatitudeRule as AdhanHighLatitudeRule,
)

from .const import LOGGER, METHOD_ADJUSTMENTS, ISHAA_ANGLE, ISHAA_INTERVAL
from .enum import Madhab, HighLatitudeRule, CalculationMethod
from .calculation_method import CALCULATION_METHOD_PARAMETERS


ADHANPY_ISHAA_ANGLE = "isha_angle"
ADHANPY_ISHAA_INTERVAL = "isha_interval"


class CalculationMethodMapper:
    @staticmethod
    def toAdhanPy(calc_method: CalculationMethod | str):
        if isinstance(calc_method, str):
            method = CalculationMethod(calc_method)
        else:
            method = calc_method

        calc_method_params = CALCULATION_METHOD_PARAMETERS.get(method).copy()

        if calc_method_params is None:
            return {}

        method_adj = calc_method_params[METHOD_ADJUSTMENTS]
        calc_method_params[METHOD_ADJUSTMENTS] = PrayerAdjustments(**method_adj)
        if calc_method_params.get(ISHAA_ANGLE) is not None:
            calc_method_params[ADHANPY_ISHAA_ANGLE] = calc_method_params[ISHAA_ANGLE]
            del calc_method_params[ISHAA_ANGLE]
        if calc_method_params.get(ISHAA_INTERVAL) is not None:
            calc_method_params[ADHANPY_ISHAA_INTERVAL] = calc_method_params[
                ISHAA_INTERVAL
            ]
            del calc_method_params[ISHAA_INTERVAL]

        return calc_method_params


class MadhabMapper:
    @staticmethod
    def toAdhanPy(madhab: Optional[str]) -> AdhanMadhab:
        if madhab is None:
            return None

        _madhab = Madhab(madhab)

        match (_madhab):
            case Madhab.SHAFI:
                return AdhanMadhab.SHAFI
            case Madhab.HANAFI:
                return AdhanMadhab.HANAFI
            case _:
                return AdhanMadhab.SHAFI

    @staticmethod
    def toMawaqeet(madhab: AdhanMadhab) -> Madhab:
        if madhab is None:
            return None

        match (madhab):
            case AdhanMadhab.SHAFI:
                return Madhab.SHAFI
            case AdhanMadhab.HANAFI:
                return Madhab.HANAFI


class HighLatitudeRuleMapper:
    @staticmethod
    def toAdhanPy(high_latitude_rule: Optional[str]) -> HighLatitudeRule:
        if high_latitude_rule is None:
            return None

        _high_latitude_rule = HighLatitudeRule(high_latitude_rule)

        match (_high_latitude_rule):
            case HighLatitudeRule.MIDDLE_OF_THE_NIGHT:
                return AdhanHighLatitudeRule.MIDDLE_OF_THE_NIGHT
            case HighLatitudeRule.SEVENTH_OF_THE_NIGHT:
                return AdhanHighLatitudeRule.SEVENTH_OF_THE_NIGHT
            case HighLatitudeRule.TWILIGHT_ANGLE:
                return AdhanHighLatitudeRule.TWILIGHT_ANGLE
            case _:
                return AdhanHighLatitudeRule.MIDDLE_OF_THE_NIGHT

    @staticmethod
    def toMawaqeet(high_latitude_rule: AdhanHighLatitudeRule) -> HighLatitudeRule:
        if high_latitude_rule is None:
            return None

        match (high_latitude_rule):
            case AdhanHighLatitudeRule.MIDDLE_OF_THE_NIGHT:
                return HighLatitudeRule.MIDDLE_OF_THE_NIGHT
            case AdhanHighLatitudeRule.SEVENTH_OF_THE_NIGHT:
                return HighLatitudeRule.SEVENTH_OF_THE_NIGHT
            case AdhanHighLatitudeRule.TWILIGHT_ANGLE:
                return HighLatitudeRule.TWILIGHT_ANGLE


class PrayerAdjustments:
    fajr: int
    # Fajr offset in minutes

    sunrise: int
    # Sunrise offset in minutes

    dhuhr: int
    # Dhuhr offset in minutes

    asr: int
    # Asr offset in minutes

    maghrib: int
    # Maghrib offset in minutes

    isha: int
    # Isha offset in minutes

    def __init__(
        self,
        fajr: int = 0,
        shuruq: int = 0,
        dhuhr: int = 0,
        asr: int = 0,
        maghrib: int = 0,
        ishaa: int = 0,
    ):
        """
        Gets a PrayerAdjustments object to offset prayer times (defaulting to 0)
        param fajr offset from fajr in minutes
        param sunrise offset from sunrise in minutes
        param dhuhr offset from dhuhr in minutes
        param asr offset from asr in minutes
        param maghrib offset from maghrib in minutes
        param isha offset from isha in minutes
        """
        self.fajr = fajr
        self.sunrise = shuruq
        self.dhuhr = dhuhr
        self.asr = asr
        self.maghrib = maghrib
        self.isha = ishaa
