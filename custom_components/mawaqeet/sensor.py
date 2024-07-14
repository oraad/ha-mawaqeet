"""Sensor platform for mawaqeet."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .entity import MawaqeetEntity
from .enum import PrayerTime, PrayerTimeOption

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MawaqeetDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key=PrayerTime.FAJR,
        translation_key=PrayerTime.FAJR,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTime.SHURUQ,
        translation_key=PrayerTime.SHURUQ,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTime.DHUHR,
        translation_key=PrayerTime.DHUHR,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTime.ASR,
        translation_key=PrayerTime.ASR,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTime.MAGHRIB,
        translation_key=PrayerTime.MAGHRIB,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTime.ISHAA,
        translation_key=PrayerTime.ISHAA,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTime.MIDNIGHT,
        translation_key=PrayerTime.MIDNIGHT,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTime.LAST_THIRD,
        translation_key=PrayerTime.LAST_THIRD,
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=PrayerTimeOption.CALCULATION_METHOD,
        translation_key=PrayerTimeOption.CALCULATION_METHOD,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=PrayerTimeOption.MADHAB,
        translation_key=PrayerTimeOption.MADHAB,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=PrayerTimeOption.HIGH_LATITUDE_RULE,
        translation_key=PrayerTimeOption.HIGH_LATITUDE_RULE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=PrayerTimeOption.NIGHT_LENGTH,
        translation_key=PrayerTimeOption.NIGHT_LENGTH,
        native_unit_of_measurement="ms",
        suggested_unit_of_measurement="h",
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=PrayerTimeOption.NIGHT_DURATION,
        translation_key=PrayerTimeOption.NIGHT_DURATION,
        native_unit_of_measurement="s",
        suggested_unit_of_measurement="h",
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    coordinator: MawaqeetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        MawaqeetSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MawaqeetSensor(MawaqeetEntity, SensorEntity):
    """Mawaqeet Sensor class."""

    def __init__(
        self,
        coordinator: MawaqeetDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    @property
    def native_value(self) -> datetime | Any | None:
        """Return the native value of the sensor."""
        key = self.entity_description.key
        if key in PrayerTime:
            prayer_time = PrayerTime(key)
            value = self.coordinator.data["prayer_times"].get(prayer_time)
        elif key in PrayerTimeOption:
            prayer_time_option = PrayerTimeOption(key)
            value = self.coordinator.data["prayer_times_config"].get(prayer_time_option)
        return value
