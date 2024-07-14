"""
Custom integration Home Assistant.

For more details about this integration, please refer to
https://github.com/oraad/ha-mawaqeet
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import MawaqeetDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.EVENT,
    Platform.BUTTON,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    coordinator = MawaqeetDataUpdateCoordinator(hass=hass, config_entry=entry)
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: MawaqeetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
        coordinator.clear_event_sub()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Triggered by config entry options updates."""
    coordinator: MawaqeetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.clear_event_sub()
    await hass.config_entries.async_reload(entry.entry_id)
    await coordinator.async_request_refresh()
