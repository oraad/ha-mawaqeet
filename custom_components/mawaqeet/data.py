"""Custom types for mawaqeet."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import MawaqeetDataUpdateCoordinator

type MawaqeetConfigEntry = ConfigEntry[MawaqeetRuntimeData]


@dataclass
class MawaqeetRuntimeData:
    """Runtime data for the Mawaqeet integration."""

    coordinator: MawaqeetDataUpdateCoordinator
