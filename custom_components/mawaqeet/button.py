"""Sensor platform for mawaqeet."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.const import EntityCategory, CONF_TYPE
from homeassistant.const import CONF_DEVICE_ID, CONF_TYPE
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
    ButtonDeviceClass,
)

from .const import (
    DOMAIN,
    MAWAQEET_EVENT,
    PRAYER_TIME_TRIGGER,
    PRAYER_REMINDER_TRIGGER,
    PRAYER,
)
from .coordinator import MawaqeetDataUpdateCoordinator
from .entity import MawaqeetEntity
from .enum import PrayerTime

FAJR_TIME = "fajr_time"
SHURUQ_TIME = "shuruq_time"
DHUHR_TIME = "dhuhr_time"

FAJR_REMINDER = "fajr_reminder"
SHURUQ_REMINDER = "shuruq_reminder"
DHUHR_REMINDER = "dhuhr_reminder"


@dataclass
class MawaqeetButtonEntityDescription(ButtonEntityDescription):
    prayer: PrayerTime = None
    trigger_type: str = None


ENTITY_DESCRIPTIONS = (
    MawaqeetButtonEntityDescription(
        key=FAJR_TIME,
        translation_key=FAJR_TIME,
        device_class=None,
        prayer=PrayerTime.FAJR,
        trigger_type=PRAYER_TIME_TRIGGER,
    ),
    MawaqeetButtonEntityDescription(
        key=SHURUQ_TIME,
        translation_key=SHURUQ_TIME,
        device_class=None,
        prayer=PrayerTime.SHURUQ,
        trigger_type=PRAYER_TIME_TRIGGER,
    ),
    MawaqeetButtonEntityDescription(
        key=DHUHR_TIME,
        translation_key=DHUHR_TIME,
        device_class=None,
        prayer=PrayerTime.DHUHR,
        trigger_type=PRAYER_TIME_TRIGGER,
    ),
    MawaqeetButtonEntityDescription(
        key=FAJR_REMINDER,
        translation_key=FAJR_REMINDER,
        device_class=None,
        prayer=PrayerTime.FAJR,
        trigger_type=PRAYER_REMINDER_TRIGGER,
    ),
    MawaqeetButtonEntityDescription(
        key=SHURUQ_REMINDER,
        translation_key=SHURUQ_REMINDER,
        device_class=None,
        prayer=PrayerTime.SHURUQ,
        trigger_type=PRAYER_REMINDER_TRIGGER,
    ),
    MawaqeetButtonEntityDescription(
        key=DHUHR_REMINDER,
        translation_key=DHUHR_REMINDER,
        device_class=None,
        prayer=PrayerTime.DHUHR,
        trigger_type=PRAYER_REMINDER_TRIGGER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
    """Set up the button platform."""
    coordinator: MawaqeetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        MawaqeetButton(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MawaqeetButton(MawaqeetEntity, ButtonEntity):
    """Mawaqeet Button class."""

    entity_description: MawaqeetButtonEntityDescription

    def __init__(
        self,
        coordinator: MawaqeetDataUpdateCoordinator,
        entity_description: MawaqeetButtonEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    async def async_press(self) -> None:
        device_id = self.coordinator.device.device_id
        type = self.entity_description.trigger_type
        prayer = self.entity_description.prayer

        event_data = {
            CONF_DEVICE_ID: device_id,
            CONF_TYPE: type,
            PRAYER: prayer,
        }
        self.hass.bus.async_fire(MAWAQEET_EVENT, event_data)
