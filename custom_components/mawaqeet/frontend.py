"""Lovelace prayer card static path and resource registration."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

LOVELACE_REGISTER_MAX_RETRIES = 3
LOVELACE_REGISTER_RETRY_DELAY = 2

CARD_BUNDLE_FILENAME = "mawaqeet-prayer-card.js"
CARD_PATH = Path(__file__).parent / "www" / CARD_BUNDLE_FILENAME
CARD_URL = f"/mawaqeet/{CARD_BUNDLE_FILENAME}"

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"
try:
    with _MANIFEST_PATH.open(encoding="utf-8") as manifest_file:
        _VERSION = json.load(manifest_file).get("version", "0.0.0")
except (OSError, json.JSONDecodeError):
    _VERSION = "0.0.0"

CARD_URL_VERSIONED = f"{CARD_URL}?v={_VERSION}"


def _integration_data(hass: HomeAssistant) -> dict[str, Any]:
    """Return domain data bucket for frontend registration flags."""
    return hass.data.setdefault(DOMAIN, {})


async def _async_retry_or_fail(retry_count: int, condition_name: str) -> bool:
    """Return True if Lovelace registration should retry."""
    if retry_count < LOVELACE_REGISTER_MAX_RETRIES:
        _LOGGER.debug(
            "%s, retrying in %ds (attempt %d/%d)",
            condition_name,
            LOVELACE_REGISTER_RETRY_DELAY,
            retry_count + 1,
            LOVELACE_REGISTER_MAX_RETRIES,
        )
        await asyncio.sleep(LOVELACE_REGISTER_RETRY_DELAY)
        return True
    return False


async def async_register_static_path(hass: HomeAssistant) -> None:
    """Register static paths to serve the Lovelace card module."""
    if _integration_data(hass).get("static_registered"):
        return

    www = CARD_PATH.parent
    if not www.is_dir() or not CARD_PATH.is_file():
        _LOGGER.warning(
            "Mawaqeet Lovelace card bundle missing at %s. "
            "Rebuild with: cd custom_components/mawaqeet/frontend "
            "&& npm ci && npm run build",
            CARD_PATH,
        )
        return

    with contextlib.suppress(RuntimeError):
        await hass.http.async_register_static_paths(
            [StaticPathConfig("/mawaqeet", www, cache_headers=False)]
        )

    _integration_data(hass)["static_registered"] = True
    _LOGGER.debug("Registered static path for Mawaqeet card at %s", CARD_URL)


async def async_register_lovelace_resource(
    hass: HomeAssistant,
    retry_count: int = 0,
) -> None:
    """Register the prayer card as a Lovelace resource (storage mode)."""
    if _integration_data(hass).get("lovelace_resource_registered"):
        return None

    lovelace_data = hass.data.get("lovelace")
    if lovelace_data is None:
        if await _async_retry_or_fail(retry_count, "Lovelace not initialized yet"):
            return await async_register_lovelace_resource(hass, retry_count + 1)
        _LOGGER.warning(
            "Could not auto-register Mawaqeet card: Lovelace not ready "
            "after %d retries. Add manually under Settings -> Dashboards -> "
            "Resources -> %s (JavaScript module)",
            LOVELACE_REGISTER_MAX_RETRIES,
            CARD_URL_VERSIONED,
        )
        return None

    lovelace_mode = getattr(lovelace_data, "mode", None)
    if lovelace_mode is None and hasattr(lovelace_data, "get"):
        lovelace_mode = lovelace_data.get("mode")

    resources = getattr(lovelace_data, "resources", None)
    if resources is None and hasattr(lovelace_data, "get"):
        resources = lovelace_data.get("resources")

    if resources is None:
        if await _async_retry_or_fail(
            retry_count,
            f"Lovelace resources not available yet (mode={lovelace_mode})",
        ):
            return await async_register_lovelace_resource(hass, retry_count + 1)
        _LOGGER.warning(
            "Could not auto-register Mawaqeet card: Lovelace in YAML mode "
            "(mode=%s). Add to configuration.yaml: lovelace: resources: "
            "[{url: %s, type: module}]",
            lovelace_mode,
            CARD_URL_VERSIONED,
        )
        return None

    if not hasattr(resources, "async_create_item") or not hasattr(
        resources, "async_items"
    ):
        _LOGGER.warning(
            "Could not auto-register Mawaqeet card: Lovelace resources API "
            "unavailable (mode=%s). Add manually under Settings -> Dashboards -> "
            "Resources -> %s (JavaScript module)",
            lovelace_mode,
            CARD_URL_VERSIONED,
        )
        return None

    existing_resource = None
    for resource in resources.async_items():
        url = resource.get("url", "")
        if url.startswith(CARD_URL):
            existing_resource = resource
            break

    if existing_resource:
        existing_type = existing_resource.get(
            "type", existing_resource.get("res_type", "module")
        )
        if (
            existing_resource.get("url") != CARD_URL_VERSIONED
            or existing_type != "module"
        ):
            try:
                await resources.async_update_item(
                    existing_resource["id"],
                    {"url": CARD_URL_VERSIONED, "res_type": "module"},
                )
                _LOGGER.info(
                    "Updated Mawaqeet prayer card Lovelace resource to v%s",
                    _VERSION,
                )
            except (OSError, RuntimeError, ValueError) as err:
                _LOGGER.warning("Failed to update Mawaqeet Lovelace resource: %s", err)
        else:
            _LOGGER.debug("Mawaqeet prayer card Lovelace resource already current")
        _integration_data(hass)["lovelace_resource_registered"] = True
        return None

    try:
        await resources.async_create_item(
            {"url": CARD_URL_VERSIONED, "res_type": "module"}
        )
        _LOGGER.info(
            "Registered Mawaqeet prayer card as Lovelace resource (v%s)", _VERSION
        )
        _integration_data(hass)["lovelace_resource_registered"] = True
    except (OSError, RuntimeError, ValueError) as err:
        _LOGGER.warning("Failed to register Mawaqeet Lovelace resource: %s", err)
    return None


async def async_setup_card(hass: HomeAssistant) -> None:
    """Register static path and Lovelace resource for the prayer card."""
    await async_register_static_path(hass)
    await async_register_lovelace_resource(hass)
