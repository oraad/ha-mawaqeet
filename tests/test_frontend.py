"""Tests for Lovelace card registration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.mawaqeet.const import DOMAIN
from custom_components.mawaqeet.frontend import (
    CARD_PATH,
    CARD_URL,
    CARD_URL_VERSIONED,
    async_register_lovelace_resource,
    async_register_static_path,
)


async def test_register_static_path_missing_bundle(hass: HomeAssistant) -> None:
    """Test warning when card bundle is missing."""
    hass.data[DOMAIN] = {}
    with patch.object(Path, "is_file", return_value=False):
        await async_register_static_path(hass)
    assert "static_registered" not in hass.data[DOMAIN]


async def test_lovelace_resource_already_registered(hass: HomeAssistant) -> None:
    """Test early return when resource flag is already set."""
    hass.data[DOMAIN] = {"lovelace_resource_registered": True}
    await async_register_lovelace_resource(hass)


async def test_lovelace_retries_exhausted(hass: HomeAssistant) -> None:
    """Test warning when Lovelace never becomes available."""
    hass.data[DOMAIN] = {}
    with (
        patch(
            "custom_components.mawaqeet.frontend._async_retry_or_fail",
            return_value=False,
        ),
        patch("custom_components.mawaqeet.frontend._LOGGER") as mock_logger,
    ):
        await async_register_lovelace_resource(hass)
    mock_logger.warning.assert_called()


async def test_lovelace_dict_style_data(hass: HomeAssistant) -> None:
    """Test Lovelace data exposed via mapping interface."""

    class MockLovelaceResources:
        def async_items(self) -> list:
            return []

        async def async_create_item(self, item: dict) -> None:
            self.created = item

    resources = MockLovelaceResources()

    class MockLovelace:
        def get(self, key: str, default: object = None) -> object | None:
            return {"mode": "storage", "resources": resources}.get(key, default)

    hass.data[DOMAIN] = {}
    hass.data["lovelace"] = MockLovelace()
    await async_register_lovelace_resource(hass)
    assert hass.data[DOMAIN]["lovelace_resource_registered"] is True


async def test_lovelace_yaml_mode_no_resources(hass: HomeAssistant) -> None:
    """Test warning when Lovelace has no resources API (YAML mode)."""

    class MockLovelace:
        mode = "yaml"

    hass.data[DOMAIN] = {}
    hass.data["lovelace"] = MockLovelace()
    with patch(
        "custom_components.mawaqeet.frontend._async_retry_or_fail",
        return_value=False,
    ):
        await async_register_lovelace_resource(hass)


async def test_lovelace_resources_api_unavailable(hass: HomeAssistant) -> None:
    """Test warning when resources object lacks create API."""

    class MockResources:
        def async_items(self) -> list:
            return []

    class MockLovelace:
        mode = "storage"
        resources = MockResources()

    hass.data[DOMAIN] = {}
    hass.data["lovelace"] = MockLovelace()
    await async_register_lovelace_resource(hass)


async def test_lovelace_updates_existing_resource(hass: HomeAssistant) -> None:
    """Test updating an outdated Lovelace resource entry."""
    updated: list[dict] = []

    class MockLovelaceResources:
        def async_items(self) -> list:
            return [{"id": "abc", "url": CARD_URL, "type": "module"}]

        async def async_create_item(self, _item: dict) -> None:
            pass

        async def async_update_item(self, item_id: str, updates: dict) -> None:
            updated.append({"id": item_id, **updates})

    class MockLovelace:
        mode = "storage"
        resources = MockLovelaceResources()

    hass.data[DOMAIN] = {}
    hass.data["lovelace"] = MockLovelace()
    await async_register_lovelace_resource(hass)
    assert updated[0]["url"] == CARD_URL_VERSIONED
    assert hass.data[DOMAIN]["lovelace_resource_registered"] is True


async def test_lovelace_existing_resource_current(hass: HomeAssistant) -> None:
    """Test no update when resource URL is already current."""

    class MockLovelaceResources:
        def async_items(self) -> list:
            return [{"id": "abc", "url": CARD_URL_VERSIONED, "res_type": "module"}]

        async def async_create_item(self, _item: dict) -> None:
            pass

        async def async_update_item(self, _item_id: str, _updates: dict) -> None:
            msg = "should not update"
            raise AssertionError(msg)

    class MockLovelace:
        mode = "storage"
        resources = MockLovelaceResources()

    hass.data[DOMAIN] = {}
    hass.data["lovelace"] = MockLovelace()
    await async_register_lovelace_resource(hass)
    assert hass.data[DOMAIN]["lovelace_resource_registered"] is True


async def test_lovelace_update_item_failure(hass: HomeAssistant) -> None:
    """Test warning when resource update raises."""

    class MockLovelaceResources:
        def async_items(self) -> list:
            return [{"id": "abc", "url": CARD_URL, "type": "js"}]

        async def async_create_item(self, _item: dict) -> None:
            pass

        async def async_update_item(self, _item_id: str, _updates: dict) -> None:
            msg = "update failed"
            raise RuntimeError(msg)

    class MockLovelace:
        mode = "storage"
        resources = MockLovelaceResources()

    hass.data[DOMAIN] = {}
    hass.data["lovelace"] = MockLovelace()
    await async_register_lovelace_resource(hass)


async def test_lovelace_create_item_failure(hass: HomeAssistant) -> None:
    """Test warning when resource creation raises."""

    class MockLovelaceResources:
        def async_items(self) -> list:
            return []

        async def async_create_item(self, _item: dict) -> None:
            msg = "create failed"
            raise RuntimeError(msg)

    class MockLovelace:
        mode = "storage"
        resources = MockLovelaceResources()

    hass.data[DOMAIN] = {}
    hass.data["lovelace"] = MockLovelace()
    await async_register_lovelace_resource(hass)
    assert "lovelace_resource_registered" not in hass.data[DOMAIN]


async def test_static_path_runtime_error_idempotent(hass: HomeAssistant) -> None:
    """Test static path registration tolerates duplicate registration."""
    hass.data[DOMAIN] = {}
    if not CARD_PATH.is_file():
        pytest.skip("Card bundle not built")

    class MockHttp:
        call_count = 0

        async def async_register_static_paths(self, _paths: object) -> None:
            type(self).call_count += 1
            if type(self).call_count > 1:
                msg = "already registered"
                raise RuntimeError(msg)

    hass.http = MockHttp()
    await async_register_static_path(hass)
    await async_register_static_path(hass)
    assert hass.data[DOMAIN]["static_registered"] is True
