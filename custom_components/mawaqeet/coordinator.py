"""DataUpdateCoordinator for mawaqeet."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import homeassistant.util.dt as dt_util
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .calculation import async_compute_prayer_times
from .const import (
    DEFAULT_REMINDER_MINUTES,
    DOMAIN,
    LOGGER,
    MAWAQEET_EVENT,
    PRAYER_REMINDER_TRIGGER,
    PRAYER_TIME_TRIGGER,
    REMINDER_ENABLED,
    REMINDER_MINUTES,
)
from .enum import REMINDER_SCHEDULE_PRAYERS, PrayerTime, prayer_reminder_minutes_key
from .models import MawaqeetData, PrayerTimeEntries

if TYPE_CHECKING:
    from .data import MawaqeetConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class MawaqeetDataUpdateCoordinator(DataUpdateCoordinator[MawaqeetData]):
    """Class to manage fetching data from the API."""

    config_entry: MawaqeetConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: MawaqeetConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
        )
        self._event_unsubs: list[CALLBACK_TYPE] = []

    @property
    def device_id(self) -> str | None:
        """Return the device registry id for this config entry."""
        device_registry = dr.async_get(self.hass)
        if device_entry := device_registry.async_get_device(
            identifiers={(DOMAIN, self.config_entry.entry_id)}
        ):
            return device_entry.id
        return None

    def _get_reminder_minutes(self, prayer: PrayerTime) -> int:
        """Return reminder lead time in minutes for a prayer."""
        options = self.config_entry.options
        key = prayer_reminder_minutes_key(prayer)
        if key in options:
            return int(options[key])
        if REMINDER_MINUTES in options:
            return int(options[REMINDER_MINUTES])
        return DEFAULT_REMINDER_MINUTES

    @callback
    def async_schedule_future_update(self, prayer_times: PrayerTimeEntries) -> None:
        """Schedule future update for sensors."""
        utc_now = dt_util.now()
        options = self.config_entry.options
        reminder_enabled = options.get(REMINDER_ENABLED, True)

        for prayer, prayer_dt in prayer_times.items():
            if prayer_dt > utc_now:
                event_unsub = async_track_point_in_time(
                    self.hass,
                    self._async_fire_prayer_event(PRAYER_TIME_TRIGGER, str(prayer)),
                    prayer_dt,
                )
                self._event_unsubs.append(event_unsub)

                if reminder_enabled and prayer in REMINDER_SCHEDULE_PRAYERS:
                    reminder_minutes = self._get_reminder_minutes(prayer)
                    reminder_at = prayer_dt - timedelta(minutes=reminder_minutes)
                    if reminder_at > utc_now:
                        event_unsub = async_track_point_in_time(
                            self.hass,
                            self._async_fire_prayer_event(
                                PRAYER_REMINDER_TRIGGER, str(prayer)
                            ),
                            reminder_at,
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

    def _prayer_event_data(self, trigger_type: str, prayer: str) -> dict[str, Any]:
        """Build bus event payload for a prayer trigger."""
        return {
            "device_id": self.device_id,
            "type": trigger_type,
            "prayer": prayer,
        }

    @callback
    def fire_prayer_event_now(self, trigger_type: str, prayer: str) -> None:
        """Fire a prayer time or reminder event immediately."""
        self.hass.bus.async_fire(
            MAWAQEET_EVENT,
            self._prayer_event_data(trigger_type, prayer),
        )

    def _async_fire_prayer_event(self, trigger_type: str, prayer: str) -> Any:
        """Return a callback that builds event data at fire time."""

        @callback
        def fire_event(dt: datetime) -> None:
            self.hass.bus.async_fire(
                MAWAQEET_EVENT,
                self._prayer_event_data(trigger_type, prayer),
                time_fired=dt.timestamp(),
            )

        return fire_event

    async def _async_update_data(self) -> MawaqeetData:
        """Update data via library."""
        self.clear_event_sub()
        mawaqeet_data = await async_compute_prayer_times(self.hass, self.config_entry)

        self.async_schedule_future_update(mawaqeet_data["prayer_times"])
        return mawaqeet_data

    def clear_event_sub(self) -> None:
        """Clean Event Subscription."""
        for event_unsub in self._event_unsubs:
            event_unsub()
        self._event_unsubs.clear()
