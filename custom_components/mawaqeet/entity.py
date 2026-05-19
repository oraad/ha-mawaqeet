"""MawaqeetEntity class."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.loader import async_get_loaded_integration

from .const import ATTRIBUTION, DOMAIN, NAME
from .coordinator import MawaqeetDataUpdateCoordinator


class MawaqeetEntity(CoordinatorEntity[MawaqeetDataUpdateCoordinator]):
    """MawaqeetEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: MawaqeetDataUpdateCoordinator, entity_name: str
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id + "_" + entity_name
        entry = coordinator.config_entry
        integration = async_get_loaded_integration(coordinator.hass, DOMAIN)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data[CONF_NAME],
            manufacturer=NAME,
            model=integration.version,
            entry_type=DeviceEntryType.SERVICE,
        )
