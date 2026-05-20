"""
Custom integration to integrate Mawaqeet with Home Assistant.

For more details about this integration, please refer to
https://github.com/oraad/ha-mawaqeet
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import MawaqeetDataUpdateCoordinator
from .data import MawaqeetRuntimeData
from .options import migrate_options, options_need_migration
from .service import async_setup_services

_LOGGER = logging.getLogger(__name__)

CARD_BUNDLE_FILENAME = "mawaqeet-prayer-card.js"

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

    from .data import MawaqeetConfigEntry

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PARALLEL_UPDATES = 1

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.EVENT,
]


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Set up the Mawaqeet integration."""
    async_setup_services(hass)
    await _async_register_frontend(hass)
    return True


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the Lovelace prayer card module under /mawaqeet/."""
    if hass.data.get(DOMAIN, {}).get("frontend_registered"):
        return

    www = Path(__file__).parent / "www"
    bundle = www / CARD_BUNDLE_FILENAME
    if not www.is_dir() or not bundle.is_file():
        _LOGGER.warning(
            "Mawaqeet Lovelace card bundle missing at %s. "
            "Rebuild with: cd custom_components/mawaqeet/frontend "
            "&& npm ci && npm run build",
            bundle,
        )
        return

    await hass.http.async_register_static_paths(
        [StaticPathConfig("/mawaqeet", www, cache_headers=False)]
    )
    hass.data.setdefault(DOMAIN, {})["frontend_registered"] = True


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: MawaqeetConfigEntry) -> bool:
    """Set up this integration using UI."""
    await _async_register_frontend(hass)

    if options_need_migration(entry.options):
        hass.config_entries.async_update_entry(
            entry, options=migrate_options(entry.options)
        )

    coordinator = MawaqeetDataUpdateCoordinator(hass=hass, config_entry=entry)
    entry.runtime_data = MawaqeetRuntimeData(coordinator=coordinator)

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(coordinator.clear_event_sub)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: MawaqeetConfigEntry) -> bool:
    """Handle removal of an entry."""
    if entry.runtime_data is not None:
        entry.runtime_data.coordinator.clear_event_sub()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
