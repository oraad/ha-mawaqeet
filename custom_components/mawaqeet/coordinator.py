"""DataUpdateCoordinator for mawaqeet."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.core import HomeAssistant, CALLBACK_TYPE, callback
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
import homeassistant.util.dt as dt_util
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_LOCATION,
)

from adhanpy.PrayerTimes import PrayerTimes, CalculationParameters

from .const import (
    DOMAIN,
    LOGGER,
    MAWAQEET_EVENT,
    PRAYER_TIME_TRIGGER,
    PRAYER_REMINDER_TRIGGER,
    CALCULATION_METHOD,
    HIGH_LATITUDE_RULE,
    FAJR_ANGLE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    MADHAB,
)
from .enum import PrayerTime, PrayerTimeOption, PrayerAdjustment
from .device_info import MawaqeetDeviceInfo
from .mapper import (
    CalculationMethodMapper,
    MadhabMapper,
    HighLatitudeRuleMapper,
    PrayerAdjustments,
)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MawaqeetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry
    _event_unsubs: list[CALLBACK_TYPE] = []
    _device: MawaqeetDeviceInfo

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
        )
        self._device = MawaqeetDeviceInfo(
            hass, self.config_entry, DeviceEntryType.SERVICE
        )

    @property
    def device(self):
        return self._device

    def __get_adjustments(self):
        options = self.config_entry.options
        fajr_adj: int = options.get(PrayerAdjustment.FAJR)
        shuruq_adj: int = options.get(str(PrayerAdjustment.SHURUQ))
        dhuhr_adj: int = options.get(str(PrayerAdjustment.DHUHR))
        asr_adj: int = options.get(str(PrayerAdjustment.ASR))
        maghrib_adj: int = options.get(str(PrayerAdjustment.MAGHRIB))
        ishaa_adj: int = options.get(str(PrayerAdjustment.ISHAA))

        return PrayerAdjustments(
            fajr=fajr_adj,
            shuruq=shuruq_adj,
            dhuhr=dhuhr_adj,
            asr=asr_adj,
            maghrib=maghrib_adj,
            ishaa=ishaa_adj,
        )

    def __get_calculation_parameters(self):
        data = self.config_entry.data
        options = self.config_entry.options
        calculation_method: str = data.get(CALCULATION_METHOD)
        fajr_angle: float = options.get(FAJR_ANGLE)
        ishaa_angle: float = options.get(ISHAA_ANGLE)
        ishaa_interval: int = options.get(ISHAA_INTERVAL)

        madhab: str = options.get(MADHAB)
        high_latitude_rule: str = options.get(HIGH_LATITUDE_RULE)

        calc_method_params = CalculationMethodMapper.toAdhanPy(calculation_method)

        calculation_parameters = CalculationParameters(
            **{
                "fajr_angle": fajr_angle,
                "isha_angle": ishaa_angle,
                "isha_interval": ishaa_interval,
                **calc_method_params,
            }
        )

        if madhab is not None:
            calculation_parameters.madhab = MadhabMapper.toAdhanPy(madhab)
        if high_latitude_rule is not None:
            calculation_parameters.high_latitude_rule = (
                HighLatitudeRuleMapper.toAdhanPy(high_latitude_rule)
            )

        return calculation_parameters

    def __get_mawaqeet_parameters(self):
        location: dict = self.config_entry.data.get(CONF_LOCATION)
        latitude: float = location.get(CONF_LATITUDE)
        longitude: float = location.get(CONF_LONGITUDE)

        coordinates = (latitude, longitude)

        adjustments = self.__get_adjustments()
        calculation_parameters = self.__get_calculation_parameters()

        calculation_parameters.adjustments = adjustments

        return coordinates, calculation_parameters

    def __get_night_times(self, today: PrayerTimes, tomorrow: PrayerTimes):
        night_duration = tomorrow.fajr - today.maghrib
        half_of_night = night_duration.seconds / 2
        third_of_night = night_duration.seconds / 3

        midnight = tomorrow.fajr - timedelta(seconds=half_of_night)
        last_third = tomorrow.fajr - timedelta(seconds=third_of_night)

        return night_duration, midnight, last_third

    def get_new_prayer_times_info(self):
        """Fetch prayer times for today."""

        coordinates, calculation_parameters = self.__get_mawaqeet_parameters()

        today = dt_util.now().date()
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

        prayer_times = {
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

        # calc_method = CalculationMethodMapper.toMawaqeet(calc_params.method)
        calc_method = self.config_entry.data.get(CALCULATION_METHOD)
        madhab = MadhabMapper.toMawaqeet(calc_params.madhab)
        high_latitude_rule = HighLatitudeRuleMapper.toMawaqeet(
            calc_params.high_latitude_rule
        )

        prayer_times_config = {
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

        return prayer_times, prayer_times_config

    @callback
    def async_schedule_future_update(
        self, prayer_times: dict[PrayerTime, datetime]
    ) -> None:
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

    def _async_fire_prayer_event(self, type: str, prayer: str):
        event_data = {
            "device_id": self._device.device_id,
            "type": type,
            "prayer": prayer,
        }

        async def fire_event(dt: datetime):
            self.hass.bus.async_fire(MAWAQEET_EVENT, event_data, time_fired=dt)

        return fire_event

    async def _async_update_data(self):
        """Update data via library."""

        prayer_times, prayer_times_config = await self.hass.async_add_executor_job(
            self.get_new_prayer_times_info
        )

        self.async_schedule_future_update(prayer_times)
        return prayer_times | prayer_times_config

    def clear_event_sub(self):
        for event_unsub in self._event_unsubs:
            event_unsub()
        self._event_unsubs.clear()
