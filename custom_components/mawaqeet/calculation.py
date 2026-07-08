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

from .const import (
    CALCULATION_METHOD,
    FAJR_ANGLE,
    HIGH_LATITUDE_RULE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    MADHAB,
)
from .enum import (
    CalculationMethod,
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
from .options import get_calculation_method

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant

    from .data import MawaqeetConfigEntry
    from .models import Coordinates, MawaqeetData, PrayerTimeConfig, PrayerTimeEntries


def _get_adjustments(options: Mapping[str, Any]) -> Any:
    """Build adhanpy adjustments from options."""
    adjustments = PrayerAdjustments(
        fajr=int(options.get(str(PrayerAdjustment.FAJR), 0)),
        shuruq=int(options.get(str(PrayerAdjustment.SHURUQ), 0)),
        dhuhr=int(options.get(str(PrayerAdjustment.DHUHR), 0)),
        asr=int(options.get(str(PrayerAdjustment.ASR), 0)),
        maghrib=int(options.get(str(PrayerAdjustment.MAGHRIB), 0)),
        ishaa=int(options.get(str(PrayerAdjustment.ISHAA), 0)),
    )
    return PrayerAdjustmentMapper.to_adhanpy(adjustments)


def _get_calculation_parameters(options: Mapping[str, Any]) -> CalculationParameters:
    """Build adhanpy calculation parameters from options."""
    calculation_method = options.get(
        CALCULATION_METHOD, str(CalculationMethod.MUSLIM_WORLD_LEAGUE)
    )
    calc_method_params = CalculationMethodMapper.to_adhanpy(calculation_method)

    if calculation_method == str(CalculationMethod.CUSTOM):
        params: dict[str, Any] = {
            "fajr_angle": float(options.get(FAJR_ANGLE, 18.0)),
            "isha_angle": float(options.get(ISHAA_ANGLE, 18.0)),
            "isha_interval": int(options.get(ISHAA_INTERVAL, 0)),
            **calc_method_params,
        }
    else:
        params = dict(calc_method_params)

    calculation_parameters = CalculationParameters(**params)

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
    location: Mapping[str, float],
    options: Mapping[str, Any],
) -> tuple[Coordinates, CalculationParameters]:
    """Resolve coordinates and calculation parameters."""
    coordinates: Coordinates = (
        float(location.get(CONF_LATITUDE, 0.0)),
        float(location.get(CONF_LONGITUDE, 0.0)),
    )
    calculation_parameters = _get_calculation_parameters(options)
    calculation_parameters.adjustments = _get_adjustments(options)
    return coordinates, calculation_parameters


def _get_night_times(
    today: PrayerTimes, tomorrow: PrayerTimes
) -> tuple[timedelta, datetime, datetime]:
    night_duration = tomorrow.fajr - today.maghrib
    half_of_night = night_duration.total_seconds() / 2
    third_of_night = night_duration.total_seconds() / 3
    midnight = tomorrow.fajr - timedelta(seconds=half_of_night)
    last_third = tomorrow.fajr - timedelta(seconds=third_of_night)
    return night_duration, midnight, last_third


def compute_prayer_times_from_options(
    location: Mapping[str, float],
    options: Mapping[str, Any],
) -> MawaqeetData:
    """Compute prayer times from location and options dictionaries."""
    coordinates, calculation_parameters = _get_mawaqeet_parameters(location, options)
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
    calc_method = options.get(
        CALCULATION_METHOD, str(CalculationMethod.MUSLIM_WORLD_LEAGUE)
    )
    madhab = MadhabMapper.to_mawaqeet(calc_params.madhab)
    high_latitude_rule = HighLatitudeRuleMapper.to_mawaqeet(
        calc_params.high_latitude_rule
    )

    prayer_times_config: PrayerTimeConfig = {
        PrayerTimeOption.CALCULATION_METHOD: str(calc_method),
        PrayerTimeOption.MADHAB: str(madhab),
        PrayerTimeOption.NIGHT_LENGTH: today_prayer.night_length,
        PrayerTimeOption.NIGHT_DURATION: int(night_duration.total_seconds()),
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


def compute_prayer_times(config_entry: MawaqeetConfigEntry) -> MawaqeetData:
    """Compute prayer times synchronously (adhanpy; use executor from async)."""
    location: dict[str, float] = config_entry.data.get(CONF_LOCATION, {})
    options = {
        **config_entry.options,
        CALCULATION_METHOD: get_calculation_method(config_entry),
    }
    return compute_prayer_times_from_options(location, options)


async def async_compute_prayer_times(
    hass: HomeAssistant, config_entry: MawaqeetConfigEntry
) -> MawaqeetData:
    """Compute prayer times without blocking the event loop."""
    return await hass.async_add_executor_job(compute_prayer_times, config_entry)
