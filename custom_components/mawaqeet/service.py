"""Services for Mawaqeet."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    PRAYER,
    PRAYER_REMINDER_TRIGGER,
    PRAYER_TIME_TRIGGER,
)
from .enum import PrayerTime

SERVICE_TRIGGER_EVENT = "trigger_event"

CONF_CONFIG_ENTRY = "config_entry"
CONF_TRIGGER_TYPE = "trigger_type"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CONFIG_ENTRY): selector.ConfigEntrySelector(
            {"integration": DOMAIN}
        ),
        vol.Required(CONF_TRIGGER_TYPE): vol.In(
            (PRAYER_TIME_TRIGGER, PRAYER_REMINDER_TRIGGER)
        ),
        vol.Required(PRAYER): vol.All(cv.string, vol.In(tuple(PrayerTime))),
    }
)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register Mawaqeet services."""

    async def handle_trigger_event(call: ServiceCall) -> None:
        """Handle trigger_event service call."""
        entry_id: str = call.data[CONF_CONFIG_ENTRY]
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN:
            msg = f"Config entry {entry_id} not found for {DOMAIN}"
            raise ServiceValidationError(msg)
        if entry.state is not ConfigEntryState.LOADED:
            msg = f"Config entry {entry_id} is not loaded"
            raise ServiceValidationError(msg)
        coordinator = entry.runtime_data.coordinator
        coordinator.fire_prayer_event_now(
            call.data[CONF_TRIGGER_TYPE],
            call.data[PRAYER],
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_TRIGGER_EVENT,
        handle_trigger_event,
        schema=SERVICE_SCHEMA,
    )
