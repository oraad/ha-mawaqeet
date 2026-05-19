"""Async calculation client for prayer times (wraps adhanpy)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import homeassistant.util.dt as dt_util
from adhanpy.PrayerTimes import (  # type: ignore[import-untyped]
    CalculationParameters,
    PrayerTimes,
)
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from .const import FAJR_ANGLE, HIGH_LATITUDE_RULE, ISHAA_ANGLE, ISHAA_INTERVAL, MADHAB
from .enum import (
    HighLatitudeRule,
    Madhab,
    PrayerAdjustment,
    PrayerTime,
    PrayerTimeOption,
)
from .mapper import (
    CalculationMethodMapper,
    HighLatitudeRuleMapper,
    MadhabMapper,
    PrayerAdjustmentMapper,
    PrayerAdjustments,
)
from .models import Coordinates, MawaqeetData, PrayerTimeConfig, PrayerTimeEntries
from .options import get_calculation_method

if TYPE_CHECKING:
    from .data import MawaqeetConfigEntry


def _get_adjustments(config_entry: MawaqeetConfigEntry) -> Any:
    options = config_entry.options
    adjustments = PrayerAdjustments(
        fajr=int(options.get(str(PrayerAdjustment.FAJR), 0)),
        shuruq=int(options.get(str(PrayerAdjustment.SHURUQ), 0)),
        dhuhr=int(options.get(str(PrayerAdjustment.DHUHR), 0)),
        asr=int(options.get(str(PrayerAdjustment.ASR), 0)),
        maghrib=int(options.get(str(PrayerAdjustment.MAGHRIB), 0)),
        ishaa=int(options.get(str(PrayerAdjustment.ISHAA), 0)),
    )
    return PrayerAdjustmentMapper.to_adhanpy(adjustments)


def _get_calculation_parameters(
    config_entry: MawaqeetConfigEntry,
) -> CalculationParameters:
    options = config_entry.options
    calculation_method = get_calculation_method(config_entry)
    calc_method_params = CalculationMethodMapper.to_adhanpy(calculation_method)

    calculation_parameters = CalculationParameters(
        **{
            "fajr_angle": float(options.get(FAJR_ANGLE, 0.0)),
            "isha_angle": float(options.get(ISHAA_ANGLE, 0.0)),
            "isha_interval": int(options.get(ISHAA_INTERVAL, 0)),
            **calc_method_params,
        }
    )

    madhab: str = options.get(MADHAB, Madhab.SHAFI)
    high_latitude_rule: str = options.get(
        HIGH_LATITUDE_RULE, HighLatitudeRule.MIDDLE_OF_THE_NIGHT
    )
    calculation_parameters.madhab = MadhabMapper.to_adhanpy(madhab)
    calculation_parameters.high_latitude_rule = HighLatitudeRuleMapper.to_adhanpy(
        high_latitude_rule
    )
    return calculation_parameters


def _get_mawaqeet_parameters(
    config_entry: MawaqeetConfigEntry,
) -> tuple[Coordinates, CalculationParameters]:
    location: dict[str, float] = config_entry.data.get(CONF_LOCATION, {})
    coordinates: Coordinates = (
        float(location.get(CONF_LATITUDE, 0.0)),
        float(location.get(CONF_LONGITUDE, 0.0)),
    )
    calculation_parameters = _get_calculation_parameters(config_entry)
    calculation_parameters.adjustments = _get_adjustments(config_entry)
    return coordinates, calculation_parameters


def _get_night_times(
    today: PrayerTimes, tomorrow: PrayerTimes
) -> tuple[timedelta, datetime, datetime]:
    night_duration = tomorrow.fajr - today.maghrib
    half_of_night = night_duration.seconds / 2
    third_of_night = night_duration.seconds / 3
    midnight = tomorrow.fajr - timedelta(seconds=half_of_night)
    last_third = tomorrow.fajr - timedelta(seconds=third_of_night)
    return night_duration, midnight, last_third


def compute_prayer_times(config_entry: MawaqeetConfigEntry) -> MawaqeetData:
    """Compute prayer times synchronously (adhanpy; use executor from async)."""
    coordinates, calculation_parameters = _get_mawaqeet_parameters(config_entry)
    today = dt_util.now()
    tomorrow = today + timedelta(days=1)

    today_prayer = PrayerTimes(
        coordinates, today, calculation_parameters=calculation_parameters
    )
    tomorrow_prayer = PrayerTimes(
        coordinates, tomorrow, calculation_parameters=calculation_parameters
    )

    night_duration, midnight, last_third = _get_night_times(
        today_prayer, tomorrow_prayer
    )

    prayer_times: PrayerTimeEntries = {
        PrayerTime.FAJR: today_prayer.fajr,
        PrayerTime.SHURUQ: today_prayer.sunrise,
        PrayerTime.DHUHR: today_prayer.dhuhr,
        PrayerTime.ASR: today_prayer.asr,
        PrayerTime.MAGHRIB: today_prayer.maghrib,
        PrayerTime.ISHAA: today_prayer.isha,
        PrayerTime.MIDNIGHT: midnight,
        PrayerTime.LAST_THIRD: last_third,
    }

    calc_params = today_prayer.calculation_parameters
    calc_method = get_calculation_method(config_entry)
    madhab = MadhabMapper.to_mawaqeet(calc_params.madhab)
    high_latitude_rule = HighLatitudeRuleMapper.to_mawaqeet(
        calc_params.high_latitude_rule
    )

    prayer_times_config: PrayerTimeConfig = {
        PrayerTimeOption.CALCULATION_METHOD: str(calc_method),
        PrayerTimeOption.MADHAB: str(madhab),
        PrayerTimeOption.NIGHT_LENGTH: today_prayer.night_length,
        PrayerTimeOption.NIGHT_DURATION: night_duration.seconds,
        PrayerTimeOption.HIGH_LATITUDE_RULE: str(high_latitude_rule),
        PrayerTimeOption.FAJR_ANGLE: calc_params.fajr_angle,
        PrayerTimeOption.ISHAA_ANGLE: calc_params.isha_angle,
        PrayerTimeOption.ISHAA_INTERVAL: calc_params.isha_interval or 0,
        PrayerTimeOption.FAJR_OFFSET: calc_params.adjustments.fajr,
        PrayerTimeOption.SHURUQ_OFFSET: calc_params.adjustments.sunrise,
        PrayerTimeOption.DHUHR_OFFSET: calc_params.adjustments.dhuhr,
        PrayerTimeOption.ASR_OFFSET: calc_params.adjustments.asr,
        PrayerTimeOption.MAGHRIB_OFFSET: calc_params.adjustments.maghrib,
        PrayerTimeOption.ISHAA_OFFSET: calc_params.adjustments.isha,
    }

    return {
        "prayer_times": prayer_times,
        "prayer_times_config": prayer_times_config,
    }


async def async_compute_prayer_times(
    hass: HomeAssistant, config_entry: MawaqeetConfigEntry
) -> MawaqeetData:
    """Compute prayer times without blocking the event loop."""
    return await hass.async_add_executor_job(compute_prayer_times, config_entry)
