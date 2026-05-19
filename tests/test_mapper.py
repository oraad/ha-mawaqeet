"""Test mapper modules."""

from adhanpy.calculation.Madhab import Madhab as AdhanMadhab

from custom_components.mawaqeet.calculation_method import PrayerAdjustments
from custom_components.mawaqeet.enum import CalculationMethod, HighLatitudeRule, Madhab
from custom_components.mawaqeet.mapper import (
    CalculationMethodMapper,
    HighLatitudeRuleMapper,
    MadhabMapper,
    PrayerAdjustmentMapper,
)


def test_calculation_method_mapper_mwl() -> None:
    """Test MWL maps to adhanpy parameters."""
    params = CalculationMethodMapper.to_adhanpy(CalculationMethod.MUSLIM_WORLD_LEAGUE)
    assert "fajr_angle" in params


def test_madhab_mapper_roundtrip() -> None:
    """Test madhab mapping."""
    assert MadhabMapper.to_adhanpy(Madhab.HANAFI) == AdhanMadhab.HANAFI
    assert MadhabMapper.to_mawaqeet(AdhanMadhab.HANAFI) == Madhab.HANAFI


def test_high_latitude_rule_mapper() -> None:
    """Test high latitude rule mapping."""
    assert (
        HighLatitudeRuleMapper.to_mawaqeet(
            HighLatitudeRuleMapper.to_adhanpy(HighLatitudeRule.TWILIGHT_ANGLE)
        )
        == HighLatitudeRule.TWILIGHT_ANGLE
    )


def test_prayer_adjustment_mapper() -> None:
    """Test prayer adjustment mapping."""
    adjustments = PrayerAdjustments(fajr=1, asr=-2)
    adhan = PrayerAdjustmentMapper.to_adhanpy(adjustments)
    assert adhan.fajr == 1
    assert adhan.asr == -2
