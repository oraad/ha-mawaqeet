"""Sensor platform for mawaqeet."""
from __future__ import annotations

from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)

from .const import DOMAIN
from .coordinator import MawaqeetDataUpdateCoordinator
from .entity import MawaqeetEntity
from .enum import PrayerTime, PrayerTimeOption

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
    # SensorEntityDescription(
    #     key=PrayerTimeOption.FAJR_ANGLE,
    #     translation_key=PrayerTimeOption.FAJR_ANGLE,
    #     native_unit_of_measurement="°",
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.ISHAA_ANGLE,
    #     translation_key=PrayerTimeOption.ISHAA_ANGLE,
    #     native_unit_of_measurement="°",
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.ISHAA_INTERVAL,
    #     translation_key=PrayerTimeOption.ISHAA_INTERVAL,
    #     native_unit_of_measurement="min",
    #     suggested_display_precision=0,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    SensorEntityDescription(
        key=PrayerTimeOption.HIGH_LATITUDE_RULE,
        translation_key=PrayerTimeOption.HIGH_LATITUDE_RULE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=PrayerTimeOption.NIGHT_LENGTH,
        translation_key=PrayerTimeOption.NIGHT_LENGTH,
        native_unit_of_measurement="ms",
        unit_of_measurement="h",
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=PrayerTimeOption.NIGHT_DURATION,
        translation_key=PrayerTimeOption.NIGHT_DURATION,
        native_unit_of_measurement="s",
        unit_of_measurement="h",
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.FAJR_OFFSET,
    #     translation_key=PrayerTimeOption.FAJR_OFFSET,
    #     native_unit_of_measurement="min",
    #     suggested_display_precision=0,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.SHURUQ_OFFSET,
    #     translation_key=PrayerTimeOption.SHURUQ_OFFSET,
    #     native_unit_of_measurement="min",
    #     suggested_display_precision=0,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.DHUHR_OFFSET,
    #     translation_key=PrayerTimeOption.DHUHR_OFFSET,
    #     native_unit_of_measurement="min",
    #     suggested_display_precision=0,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.ASR_OFFSET,
    #     translation_key=PrayerTimeOption.ASR_OFFSET,
    #     native_unit_of_measurement="min",
    #     suggested_display_precision=0,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.MAGHRIB_OFFSET,
    #     translation_key=PrayerTimeOption.MAGHRIB_OFFSET,
    #     native_unit_of_measurement="min",
    #     suggested_display_precision=0,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
    # SensorEntityDescription(
    #     key=PrayerTimeOption.ISHAA_OFFSET,
    #     translation_key=PrayerTimeOption.ISHAA_OFFSET,
    #     native_unit_of_measurement="min",
    #     suggested_display_precision=0,
    #     entity_category=EntityCategory.DIAGNOSTIC,
    # ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
):
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
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
