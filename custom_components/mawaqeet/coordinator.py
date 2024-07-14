"""DataUpdateCoordinator for mawaqeet."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, TypedDict

import homeassistant.util.dt as dt_util
from adhanpy.calculation.PrayerAdjustments import (
    PrayerAdjustments as AdhanPrayerAdjustments,
)
from adhanpy.PrayerTimes import CalculationParameters, PrayerTimes
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import (
    CALCULATION_METHOD,
    DOMAIN,
    FAJR_ANGLE,
    HIGH_LATITUDE_RULE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    LOGGER,
    MADHAB,
    MAWAQEET_EVENT,
    PRAYER_TIME_TRIGGER,
)
from .device_info import MawaqeetDeviceInfo
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

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

type NightTimes = tuple[timedelta, datetime, datetime]
type PrayerTimeEntries = dict[PrayerTime, datetime]
type PrayerTimeConfig = dict[PrayerTimeOption, Any]
type Coordinates = tuple[float, float]


class MawaqeetData(TypedDict):
    """Mawaqeet Data."""

    prayer_times: PrayerTimeEntries
    prayer_times_config: PrayerTimeConfig


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MawaqeetDataUpdateCoordinator(DataUpdateCoordinator[MawaqeetData]):
    """Class to manage fetching data from the API."""

    _event_unsubs: list[CALLBACK_TYPE]
    _device: MawaqeetDeviceInfo

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
        )

        self.config_entry = config_entry
        self._device = MawaqeetDeviceInfo(
            hass, self.config_entry, DeviceEntryType.SERVICE
        )
        self._event_unsubs = []

    @property
    def device(self) -> MawaqeetDeviceInfo:
        """Mawaqeet Device Info."""
        return self._device

    def __get_adjustments(self) -> AdhanPrayerAdjustments:
        if self.config_entry is None:
            return AdhanPrayerAdjustments()

        options = self.config_entry.options
        fajr_adj: int = options.get(str(PrayerAdjustment.FAJR), 0)
        shuruq_adj: int = options.get(str(PrayerAdjustment.SHURUQ), 0)
        dhuhr_adj: int = options.get(str(PrayerAdjustment.DHUHR), 0)
        asr_adj: int = options.get(str(PrayerAdjustment.ASR), 0)
        maghrib_adj: int = options.get(str(PrayerAdjustment.MAGHRIB), 0)
        ishaa_adj: int = options.get(str(PrayerAdjustment.ISHAA), 0)

        adjustments = PrayerAdjustments(
            fajr=fajr_adj,
            shuruq=shuruq_adj,
            dhuhr=dhuhr_adj,
            asr=asr_adj,
            maghrib=maghrib_adj,
            ishaa=ishaa_adj,
        )

        return PrayerAdjustmentMapper.to_adhanpy(adjustments)

    def __get_calculation_parameters(self) -> CalculationParameters:
        data = self.config_entry.data
        options = self.config_entry.options

        calculation_method: str = data.get(
            CALCULATION_METHOD, CalculationMethod.MUSLIM_WORLD_LEAGUE
        )

        fajr_angle: float | None = options.get(FAJR_ANGLE)
        ishaa_angle: float | None = options.get(ISHAA_ANGLE)
        ishaa_interval: int | None = options.get(ISHAA_INTERVAL)

        madhab: str = options.get(MADHAB, Madhab.SHAFI)
        high_latitude_rule: str = options.get(
            HIGH_LATITUDE_RULE, HighLatitudeRule.MIDDLE_OF_THE_NIGHT
        )

        calc_method_params = CalculationMethodMapper.to_adhanpy(calculation_method)

        calculation_parameters = CalculationParameters(
            **{
                "fajr_angle": fajr_angle,
                "isha_angle": ishaa_angle,
                "isha_interval": ishaa_interval,
                **calc_method_params,
            }
        )

        if madhab is not None:
            calculation_parameters.madhab = MadhabMapper.to_adhanpy(madhab)

        if high_latitude_rule is not None:
            calculation_parameters.high_latitude_rule = (
                HighLatitudeRuleMapper.to_adhanpy(high_latitude_rule)
            )

        return calculation_parameters

    def __get_mawaqeet_parameters(self) -> tuple[Coordinates, CalculationParameters]:
        location: dict[str, float] = self.config_entry.data.get(CONF_LOCATION, {})
        latitude: float = location.get(CONF_LATITUDE, 0.0)
        longitude: float = location.get(CONF_LONGITUDE, 0.0)

        coordinates = (latitude, longitude)

        adjustments = self.__get_adjustments()
        calculation_parameters = self.__get_calculation_parameters()

        calculation_parameters.adjustments = adjustments

        return coordinates, calculation_parameters

    def __get_night_times(
        self, today: PrayerTimes, tomorrow: PrayerTimes
    ) -> NightTimes:
        night_duration = tomorrow.fajr - today.maghrib
        half_of_night = night_duration.seconds / 2
        third_of_night = night_duration.seconds / 3

        midnight = tomorrow.fajr - timedelta(seconds=half_of_night)
        last_third = tomorrow.fajr - timedelta(seconds=third_of_night)

        return night_duration, midnight, last_third

    def get_new_prayer_times_info(self) -> MawaqeetData:
        """Fetch prayer times for today."""
        coordinates, calculation_parameters = self.__get_mawaqeet_parameters()

        today = dt_util.now()
        tomorrow = today + timedelta(days=1)

        today_prayer = PrayerTimes(
            coordinates, today, calculation_parameters=calculation_parameters
        )
        tomorrow_prayer = PrayerTimes(
            coordinates, tomorrow, calculation_parameters=calculation_parameters
        )

        night_duration, midnight, last_third = self.__get_night_times(
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

        calc_method = self.config_entry.data.get(CALCULATION_METHOD)
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

    @callback
    def async_schedule_future_update(self, prayer_times: PrayerTimeEntries) -> None:
        """Schedule future update for sensors."""
        utc_now = dt_util.now()

        for prayer, prayer_dt in prayer_times.items():
            if prayer_dt > utc_now:
                event_unsub = async_track_point_in_time(
                    self.hass,
                    self._async_fire_prayer_event(PRAYER_TIME_TRIGGER, str(prayer)),
                    prayer_dt,
                )
                self._event_unsubs.append(event_unsub)

        next_update_at = prayer_times[PrayerTime.LAST_THIRD]
        event_unsub = async_track_point_in_time(
            self.hass, self.async_request_update, next_update_at
        )
        self._event_unsubs.append(event_unsub)

    async def async_request_update(self, _: datetime) -> None:
        """Request update from coordinator."""
        await self.async_request_refresh()

    def _async_fire_prayer_event(self, trigger_type: str, prayer: str) -> Any:
        event_data = {
            "device_id": self._device.device_id,
            "type": trigger_type,
            "prayer": prayer,
        }

        async def fire_event(dt: datetime) -> None:
            self.hass.bus.async_fire(
                MAWAQEET_EVENT, event_data, time_fired=dt.timestamp()
            )

        return fire_event

    async def _async_update_data(self) -> MawaqeetData:
        """Update data via library."""
        mawaqeet_data = await self.hass.async_add_executor_job(
            self.get_new_prayer_times_info
        )

        self.async_schedule_future_update(mawaqeet_data["prayer_times"])
        return mawaqeet_data

    def clear_event_sub(self) -> None:
        """Clean Event Subscription."""
        for event_unsub in self._event_unsubs:
            event_unsub()
        self._event_unsubs.clear()
