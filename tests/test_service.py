"""Test Mawaqeet services."""

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import (
    CALCULATION_METHOD,
    DOMAIN,
    MADHAB,
    PRAYER,
    PRAYER_REMINDER_TRIGGER,
    PRAYER_TIME_TRIGGER,
)
from custom_components.mawaqeet.event import LATEST_PRAYER_REMINDER, LATEST_PRAYER_TIME
from custom_components.mawaqeet.service import CONF_CONFIG_ENTRY, CONF_TRIGGER_TYPE


def _entry_data() -> dict:
    return {
        CONF_NAME: "Home",
        CONF_LOCATION: {CONF_LATITUDE: 51.5074, CONF_LONGITUDE: -0.1278},
        CALCULATION_METHOD: "mwl",
    }


def _event_entity_id(hass: HomeAssistant, entry_id: str, suffix: str) -> str:
    registry = er.async_get(hass)
    entity = next(
        e
        for e in er.async_entries_for_config_entry(registry, entry_id)
        if e.domain == "event" and e.unique_id.endswith(suffix)
    )
    return entity.entity_id


async def test_trigger_prayer_time_event(hass: HomeAssistant) -> None:
    """Test trigger_event fires latest_prayer_time."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        data=_entry_data(),
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state == ConfigEntryState.LOADED

    await hass.services.async_call(
        DOMAIN,
        "trigger_event",
        {
            CONF_CONFIG_ENTRY: entry.entry_id,
            CONF_TRIGGER_TYPE: PRAYER_TIME_TRIGGER,
            PRAYER: "fajr",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    entity_id = _event_entity_id(hass, entry.entry_id, f"_{LATEST_PRAYER_TIME}")
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes.get("event_type") == "fajr"


async def test_trigger_prayer_reminder_event(hass: HomeAssistant) -> None:
    """Test trigger_event fires latest_prayer_reminder."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        data=_entry_data(),
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    await hass.services.async_call(
        DOMAIN,
        "trigger_event",
        {
            CONF_CONFIG_ENTRY: entry.entry_id,
            CONF_TRIGGER_TYPE: PRAYER_REMINDER_TRIGGER,
            PRAYER: "dhuhr",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    entity_id = _event_entity_id(hass, entry.entry_id, f"_{LATEST_PRAYER_REMINDER}")
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes.get("event_type") == "dhuhr"


async def test_trigger_event_rejects_unknown_config_entry(hass: HomeAssistant) -> None:
    """Test trigger_event rejects a missing or foreign config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        data=_entry_data(),
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    with pytest.raises(ServiceValidationError, match="not found"):
        await hass.services.async_call(
            DOMAIN,
            "trigger_event",
            {
                CONF_CONFIG_ENTRY: "missing-entry-id",
                CONF_TRIGGER_TYPE: PRAYER_TIME_TRIGGER,
                PRAYER: "fajr",
            },
            blocking=True,
        )


async def test_trigger_event_requires_loaded_entry(hass: HomeAssistant) -> None:
    """Test trigger_event rejects an unloaded config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        data=_entry_data(),
        options={MADHAB: "shafi"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state == ConfigEntryState.NOT_LOADED

    with pytest.raises(ServiceValidationError, match="not loaded"):
        await hass.services.async_call(
            DOMAIN,
            "trigger_event",
            {
                CONF_CONFIG_ENTRY: entry.entry_id,
                CONF_TRIGGER_TYPE: PRAYER_TIME_TRIGGER,
                PRAYER: "fajr",
            },
            blocking=True,
        )
