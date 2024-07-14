"""MawaqeetEntity class."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
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
        self._attr_device_info = coordinator.device.device_info
