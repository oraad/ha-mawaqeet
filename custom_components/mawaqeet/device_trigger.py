from typing import Any
import logging
import voluptuous as vol

from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_PLATFORM,
    CONF_TYPE,
)

from homeassistant.core import HomeAssistant, CALLBACK_TYPE
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    LOGGER,
    MAWAQEET_EVENT,
    PRAYER_TIME_TRIGGER,
    PRAYER_REMINDER_TRIGGER,
)

DEVICE = "device"
EVENT = "event"

TRIGGER_TYPES = {PRAYER_TIME_TRIGGER, PRAYER_REMINDER_TRIGGER}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """Return a list of triggers."""

    triggers = []

    # Determine which triggers are supported by this device_id ...

    base_trigger = {
        # Required fields of TRIGGER_BASE_SCHEMA
        CONF_PLATFORM: DEVICE,
        CONF_DOMAIN: DOMAIN,
        CONF_DEVICE_ID: device_id,
    }

    triggers.append({**base_trigger, CONF_TYPE: PRAYER_TIME_TRIGGER})
    triggers.append({**base_trigger, CONF_TYPE: PRAYER_REMINDER_TRIGGER})

    return triggers


# async def async_get_trigger_capabilities(
#     hass: HomeAssistant, config: ConfigType
# ) -> dict[str, vol.Schema]:
#     """List trigger capabilities."""
#     return await toggle_entity.async_get_trigger_capabilities(hass, config)


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""

    event_config: vol.Schema = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: EVENT,
            event_trigger.CONF_EVENT_TYPE: MAWAQEET_EVENT,
            event_trigger.CONF_EVENT_DATA: {
                CONF_DEVICE_ID: config[CONF_DEVICE_ID],
                CONF_TYPE: config[CONF_TYPE],
            },
        }
    )

    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type=DEVICE
    )
