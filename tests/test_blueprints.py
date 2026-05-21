"""Validate repository automation blueprints against Home Assistant schemas."""

from pathlib import Path

import pytest
from homeassistant.components.automation.config import (
    AUTOMATION_BLUEPRINT_SCHEMA,
    ValidationStatus,
    _async_validate_config_item,
)
from homeassistant.components.blueprint.const import CONF_INPUT, CONF_USE_BLUEPRINT
from homeassistant.components.blueprint.models import Blueprint, BlueprintInputs
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.util import yaml as yaml_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mawaqeet.const import CALCULATION_METHOD, DOMAIN

BLUEPRINTS_DIR = Path(__file__).resolve().parents[1] / "blueprints"

EMPTY_MEDIA = {"media_content_id": "", "media_content_type": "music"}

FAKE_MEDIA = {
    "media_content_id": "media-source://test/adhan.mp3",
    "media_content_type": "music",
}

# Minimal inputs per blueprint (merged with blueprint defaults where defined).
MINIMAL_BLUEPRINT_INPUTS: dict[str, dict] = {
    "prayer_reminder_notify.yaml": {
        "tts_entity": "media_player.test",
    },
    "fajr_wakeup.yaml": {
        "target_lights": [],
        "people": [],
        "optional_media": EMPTY_MEDIA,
    },
    "prayer_time_lights.yaml": {
        "target_lights": [],
        "target_scene": "",
    },
}


@pytest.fixture
async def mawaqeet_device_id(hass: HomeAssistant) -> str:
    """Mawaqeet device registry id for blueprint triggers."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Home",
            CONF_LOCATION: {CONF_LATITUDE: 51.5, CONF_LONGITUDE: -0.12},
            CALCULATION_METHOD: "mwl",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    device = dr.async_get(hass).async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert device is not None
    return device.id


def _load_blueprint(path: Path) -> dict:
    return yaml_util.load_yaml_dict(path)


async def _validate_substituted_automation(
    hass: HomeAssistant,
    config: dict,
) -> None:
    """Run full HA automation validation; raises on schema errors."""
    result = await _async_validate_config_item(
        hass,
        config,
        raise_on_errors=True,
        warn_on_errors=False,
    )
    assert result.validation_status == ValidationStatus.OK, result.validation_error


def _substituted_automation(
    blueprint_data: dict,
    blueprint_path: str,
    inputs: dict,
) -> dict:
    blueprint = Blueprint(
        blueprint_data,
        expected_domain="automation",
        path=blueprint_path,
        schema=AUTOMATION_BLUEPRINT_SCHEMA,
    )
    instance_config = {
        CONF_USE_BLUEPRINT: {
            "path": blueprint_path,
            CONF_INPUT: inputs,
        },
        "alias": "Blueprint schema test",
    }
    blueprint_inputs = BlueprintInputs(blueprint, instance_config)
    blueprint_inputs.validate()
    return blueprint_inputs.async_substitute()


@pytest.mark.parametrize(
    "blueprint_path",
    sorted(BLUEPRINTS_DIR.glob("*.yaml")),
    ids=lambda p: p.name,
)
def test_blueprint_yaml_matches_automation_schema(blueprint_path: Path) -> None:
    """Blueprint YAML must match Home Assistant automation blueprint schema."""
    data = _load_blueprint(blueprint_path)
    AUTOMATION_BLUEPRINT_SCHEMA(data)


@pytest.mark.parametrize(
    "blueprint_name",
    sorted(MINIMAL_BLUEPRINT_INPUTS.keys()),
)
async def test_blueprint_generated_automation_valid(
    hass: HomeAssistant,
    mawaqeet_device_id: str,
    blueprint_name: str,
) -> None:
    """Substituted automation passes HA trigger, condition, and action validation."""
    path = BLUEPRINTS_DIR / blueprint_name
    data = _load_blueprint(path)
    inputs = {
        "device_id": mawaqeet_device_id,
        **MINIMAL_BLUEPRINT_INPUTS[blueprint_name],
    }
    config = _substituted_automation(data, blueprint_name, inputs)
    await _validate_substituted_automation(hass, config)


@pytest.mark.parametrize(
    ("blueprint_name", "playback_mode"),
    [
        ("adhan_home_assistant.yaml", "media_playback"),
        ("adhan_home_assistant.yaml", "announcement"),
        ("adhan_music_assistant.yaml", "media_playback"),
        ("adhan_music_assistant.yaml", "announcement"),
    ],
)
async def test_adhan_blueprint_modes_validate(
    hass: HomeAssistant,
    mawaqeet_device_id: str,
    blueprint_name: str,
    playback_mode: str,
) -> None:
    """Adhan blueprints validate per playback mode with default unused media."""
    path = BLUEPRINTS_DIR / blueprint_name
    data = _load_blueprint(path)
    inputs = {
        "device_id": mawaqeet_device_id,
        "playback_mode": playback_mode,
        "player_fajr": ["media_player.test_fajr"],
        "player_other": ["media_player.test_other"],
    }
    if playback_mode == "media_playback":
        inputs["media_fajr_playback"] = FAKE_MEDIA
        inputs["media_other_playback"] = FAKE_MEDIA
    else:
        inputs["media_fajr_announce"] = FAKE_MEDIA
        inputs["media_other_announce"] = FAKE_MEDIA

    config = _substituted_automation(data, blueprint_name, inputs)
    await _validate_substituted_automation(hass, config)


async def test_adhan_blueprint_defaults_only_unused_media(
    hass: HomeAssistant,
    mawaqeet_device_id: str,
) -> None:
    """Adhan blueprints accept defaults for unused mode-specific media fields."""
    for blueprint_name in ("adhan_home_assistant.yaml", "adhan_music_assistant.yaml"):
        path = BLUEPRINTS_DIR / blueprint_name
        data = _load_blueprint(path)
        inputs = {
            "device_id": mawaqeet_device_id,
            "playback_mode": "media_playback",
            "player_fajr": ["media_player.test_fajr"],
            "player_other": ["media_player.test_other"],
            "media_fajr_playback": FAKE_MEDIA,
            "media_other_playback": FAKE_MEDIA,
        }
        config = _substituted_automation(data, blueprint_name, inputs)
        await _validate_substituted_automation(hass, config)
