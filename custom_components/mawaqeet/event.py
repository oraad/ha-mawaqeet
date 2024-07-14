"""Sensor platform for mawaqeet."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypedDict

from homeassistant.components.event import (
    EventEntity,
    EventEntityDescription,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_TYPE
from homeassistant.core import Event, HomeAssistant, callback

from .const import (
    DOMAIN,
    LOGGER,
    MAWAQEET_EVENT,
    PRAYER,
    PRAYER_REMINDER_TRIGGER,
    PRAYER_TIME_TRIGGER,
)
from .entity import MawaqeetEntity
from .enum import PrayerTime

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MawaqeetDataUpdateCoordinator

LATEST_PRAYER_TIME = "latest_prayer_time"
LATEST_PRAYER_REMINDER = "latest_prayer_reminder"

PRAYER_TIMES = [str(prayer_time) for prayer_time in PrayerTime]


class MawaqeetEventData(TypedDict):
    """Mawaqeet Event Data."""

    device_id: str
    type: str
    prayer: str


type TRIGGER_TYPE = Literal["prayer_time", "prayer_reminder"] | None


@dataclass(frozen=True)
class MawaqeetEventEntityDescription(EventEntityDescription):
    """Mawaqeet Event Entity Description."""

    trigger_type: TRIGGER_TYPE = None


ENTITY_DESCRIPTIONS = (
    MawaqeetEventEntityDescription(
        key=LATEST_PRAYER_TIME,
        translation_key=LATEST_PRAYER_TIME,
        device_class=None,
        event_types=PRAYER_TIMES,
        trigger_type=PRAYER_TIME_TRIGGER,
    ),
    MawaqeetEventEntityDescription(
        key=LATEST_PRAYER_REMINDER,
        translation_key=LATEST_PRAYER_REMINDER,
        device_class=None,
        event_types=PRAYER_TIMES,
        trigger_type=PRAYER_REMINDER_TRIGGER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> None:
    """Set up the event platform."""
    coordinator: MawaqeetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        MawaqeetEvent(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class MawaqeetEvent(MawaqeetEntity, EventEntity):
    """Mawaqeet Event class."""

    entity_description: MawaqeetEventEntityDescription

    def __init__(
        self,
        coordinator: MawaqeetDataUpdateCoordinator,
        entity_description: MawaqeetEventEntityDescription,
    ) -> None:
        """Initialize the event class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def filter_event(event_data: MawaqeetEventData) -> bool:
            LOGGER.debug(
                "trigger_type: %s, device_id: %s, event_type: %s, bool result: %s",
                self.entity_description.trigger_type,
                event_data[CONF_DEVICE_ID],
                event_data[CONF_TYPE],
                event_data[CONF_DEVICE_ID] == self.coordinator.device.device_id
                and event_data[CONF_TYPE] == self.entity_description.trigger_type,
            )
            return (
                event_data[CONF_DEVICE_ID] == self.coordinator.device.device_id
                and event_data[CONF_TYPE] == self.entity_description.trigger_type
            )

        self.hass.bus.async_listen(
            MAWAQEET_EVENT,
            self._async_handle_event,
            event_filter=filter_event,
        )

    @callback
    def _async_handle_event(self, event: Event[MawaqeetEventData]) -> None:
        """Handle event."""
        prayer = event.data.get(PRAYER)
        self._trigger_event(prayer)
        self.async_write_ha_state()
