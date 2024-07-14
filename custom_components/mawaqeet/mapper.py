"""Mawaqeet Mapper module."""

from typing import NotRequired, TypedDict

from adhanpy.calculation.HighLatitudeRule import (
    HighLatitudeRule as AdhanHighLatitudeRule,
)
from adhanpy.calculation.Madhab import Madhab as AdhanMadhab
from adhanpy.calculation.PrayerAdjustments import (
    PrayerAdjustments as AdhanPrayerAdjustments,
)

from .calculation_method import (
    CALCULATION_METHOD_PARAMETERS,
    PrayerAdjustments,
)
from .const import ISHAA_ANGLE, ISHAA_INTERVAL, METHOD_ADJUSTMENTS
from .enum import CalculationMethod, HighLatitudeRule, Madhab

ADHANPY_ISHAA_ANGLE = "isha_angle"
ADHANPY_ISHAA_INTERVAL = "isha_interval"

ADHANPY_METHOD_ADJUSTMENTS = "method_adjustments"


class AdhanCalculationMethodParameter(TypedDict):
    """Adhan Calculation Method Paramter."""

    fajr_angle: NotRequired[float]
    isha_angle: NotRequired[float]
    isha_interval: NotRequired[int]
    method_adjustments: NotRequired[AdhanPrayerAdjustments]


class CalculationMethodMapper:
    """Calculation Method Mapper."""

    @staticmethod
    def to_adhanpy(
        calc_method: CalculationMethod | str,
    ) -> AdhanCalculationMethodParameter:
        """Map Calculation method to AdhanPy Data."""
        if isinstance(calc_method, str):
            method = CalculationMethod(calc_method)
        else:
            method = calc_method

        calculation_parameters = AdhanCalculationMethodParameter()

        calc_method_params = CALCULATION_METHOD_PARAMETERS.get(method)

        if calc_method_params is None:
            return calculation_parameters

        calc_method_params = calc_method_params.copy()

        if calc_method_params is None:
            return calculation_parameters

        if (method_adj := calc_method_params.get(METHOD_ADJUSTMENTS)) is not None:
            method_adj = PrayerAdjustments(**method_adj)
            calculation_parameters[ADHANPY_METHOD_ADJUSTMENTS] = (
                PrayerAdjustmentMapper.to_adhanpy(method_adj)
            )

        if (ishaa_angle := calc_method_params.get(ISHAA_ANGLE)) is not None:
            calculation_parameters[ADHANPY_ISHAA_ANGLE] = ishaa_angle
        if (ishaa_interval := calc_method_params.get(ISHAA_INTERVAL)) is not None:
            calculation_parameters[ADHANPY_ISHAA_INTERVAL] = ishaa_interval

        return calculation_parameters


class MadhabMapper:
    """Madhab Mapper."""

    @staticmethod
    def to_adhanpy(madhab: str | None) -> AdhanMadhab:
        """Map Madhab to AdhanPy."""
        if madhab is None:
            return AdhanMadhab.SHAFI

        _madhab = Madhab(madhab)

        match _madhab:
            case Madhab.SHAFI:
                return AdhanMadhab.SHAFI
            case Madhab.HANAFI:
                return AdhanMadhab.HANAFI
            case _:
                return AdhanMadhab.SHAFI

    @staticmethod
    def to_mawaqeet(madhab: AdhanMadhab | None) -> Madhab:
        """Map Madhab to Mawaqeet."""
        if madhab is None:
            return Madhab.SHAFI

        match madhab:
            case AdhanMadhab.SHAFI:
                return Madhab.SHAFI
            case AdhanMadhab.HANAFI:
                return Madhab.HANAFI


class HighLatitudeRuleMapper:
    """High Latitude Rule Mapper."""

    @staticmethod
    def to_adhanpy(high_latitude_rule: str | None) -> AdhanHighLatitudeRule:
        """Map High Latitude Rule to AdhanPy."""
        if high_latitude_rule is None:
            return AdhanHighLatitudeRule.MIDDLE_OF_THE_NIGHT

        _high_latitude_rule = HighLatitudeRule(high_latitude_rule)

        match _high_latitude_rule:
            case HighLatitudeRule.MIDDLE_OF_THE_NIGHT:
                return AdhanHighLatitudeRule.MIDDLE_OF_THE_NIGHT
            case HighLatitudeRule.SEVENTH_OF_THE_NIGHT:
                return AdhanHighLatitudeRule.SEVENTH_OF_THE_NIGHT
            case HighLatitudeRule.TWILIGHT_ANGLE:
                return AdhanHighLatitudeRule.TWILIGHT_ANGLE
            case _:
                return AdhanHighLatitudeRule.MIDDLE_OF_THE_NIGHT

    @staticmethod
    def to_mawaqeet(
        high_latitude_rule: AdhanHighLatitudeRule | None,
    ) -> HighLatitudeRule:
        """Map High Latitude Rule to Mawaqeet."""
        if high_latitude_rule is None:
            return HighLatitudeRule.MIDDLE_OF_THE_NIGHT

        match high_latitude_rule:
            case AdhanHighLatitudeRule.MIDDLE_OF_THE_NIGHT:
                return HighLatitudeRule.MIDDLE_OF_THE_NIGHT
            case AdhanHighLatitudeRule.SEVENTH_OF_THE_NIGHT:
                return HighLatitudeRule.SEVENTH_OF_THE_NIGHT
            case AdhanHighLatitudeRule.TWILIGHT_ANGLE:
                return HighLatitudeRule.TWILIGHT_ANGLE


class PrayerAdjustmentMapper:
    """Prayer Adjustment Mapper."""

    @staticmethod
    def to_adhanpy(prayer_adjustment: PrayerAdjustments) -> AdhanPrayerAdjustments:
        """Map Prayer Adjustments to AdhanPy."""
        return AdhanPrayerAdjustments(
            prayer_adjustment.fajr,
            prayer_adjustment.shuruq,
            prayer_adjustment.dhuhr,
            prayer_adjustment.asr,
            prayer_adjustment.maghrib,
            prayer_adjustment.ishaa,
        )

    @staticmethod
    def to_mawaqeet(
        prayer_adjustments: AdhanPrayerAdjustments,
    ) -> PrayerAdjustments:
        """Map Prayer Adjustments to Mawaqeet."""
        return PrayerAdjustments(
            prayer_adjustments.fajr,
            prayer_adjustments.sunrise,
            prayer_adjustments.dhuhr,
            prayer_adjustments.asr,
            prayer_adjustments.maghrib,
            prayer_adjustments.isha,
        )
