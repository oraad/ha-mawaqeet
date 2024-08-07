"""Adds config flow for Mawaqeet."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlow,
)
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.selector import (
    LocationSelector,
    LocationSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CALCULATION_METHOD,
    DOMAIN,
    FAJR_ANGLE,
    HIGH_LATITUDE_RULE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    MADHAB,
)
from .enum import CalculationMethod, HighLatitudeRule, Madhab, PrayerAdjustment

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult

DATA_SCHEMA = {
    vol.Required(CONF_NAME): str,
    # vol.Required(CONF_LATITUDE): cv.latitude,
    # vol.Required(CONF_LONGITUDE): cv.longitude,
    vol.Required(CONF_LOCATION): LocationSelector(LocationSelectorConfig()),
    vol.Required(CALCULATION_METHOD): SelectSelector(
        SelectSelectorConfig(
            options=[
                SelectOptionDict(value=str(m), label=str(m)) for m in CalculationMethod
            ],
            mode=SelectSelectorMode.DROPDOWN,
            multiple=False,
            translation_key=CALCULATION_METHOD,
        )
    ),
}

CALCULATION_SCHEMA = {
    vol.Required(FAJR_ANGLE): NumberSelector(
        NumberSelectorConfig(min=12, max=20, mode=NumberSelectorMode.BOX, step=0.1)
    ),
    vol.Required(ISHAA_ANGLE): NumberSelector(
        NumberSelectorConfig(min=12, max=20, mode=NumberSelectorMode.BOX, step=0.1)
    ),
    vol.Required(ISHAA_INTERVAL): NumberSelector(
        NumberSelectorConfig(min=0, max=120, mode=NumberSelectorMode.BOX, step=10)
    ),
    vol.Optional(HIGH_LATITUDE_RULE): SelectSelector(
        SelectSelectorConfig(
            options=[
                SelectOptionDict(value=str(r), label=str(r)) for r in HighLatitudeRule
            ],
            mode=SelectSelectorMode.DROPDOWN,
            multiple=False,
            translation_key=HIGH_LATITUDE_RULE,
        )
    ),
}

ADJUSTMENT_SCHEMA = {
    vol.Required(MADHAB): SelectSelector(
        SelectSelectorConfig(
            options=[SelectOptionDict(value=str(m), label=str(m)) for m in Madhab],
            mode=SelectSelectorMode.DROPDOWN,
            multiple=False,
            translation_key=MADHAB,
        )
    ),
    vol.Optional(str(PrayerAdjustment.FAJR), 0): NumberSelector(
        NumberSelectorConfig(min=-30, max=30, mode=NumberSelectorMode.BOX, step=1)
    ),
    vol.Optional(str(PrayerAdjustment.SHURUQ), 0): NumberSelector(
        NumberSelectorConfig(min=-30, max=30, mode=NumberSelectorMode.BOX, step=1)
    ),
    vol.Optional(str(PrayerAdjustment.DHUHR), 0): NumberSelector(
        NumberSelectorConfig(min=-30, max=30, mode=NumberSelectorMode.BOX, step=1)
    ),
    vol.Optional(str(PrayerAdjustment.ASR), 0): NumberSelector(
        NumberSelectorConfig(min=-30, max=30, mode=NumberSelectorMode.BOX, step=1)
    ),
    vol.Optional(str(PrayerAdjustment.MAGHRIB), 0): NumberSelector(
        NumberSelectorConfig(min=-30, max=30, mode=NumberSelectorMode.BOX, step=1)
    ),
    vol.Optional(str(PrayerAdjustment.ISHAA), 0): NumberSelector(
        NumberSelectorConfig(min=-30, max=30, mode=NumberSelectorMode.BOX, step=1)
    ),
}


def _get_data_schema(
    hass: HomeAssistant, config_entry: ConfigEntry | None = None
) -> dict:
    """Get a schema with default values."""
    if config_entry is None:
        return {
            CONF_NAME: hass.config.location_name,
            CONF_LOCATION: {
                CONF_LATITUDE: hass.config.latitude,
                CONF_LONGITUDE: hass.config.longitude,
            },
            CALCULATION_METHOD: str(CalculationMethod.MUSLIM_WORLD_LEAGUE),
        }

    return {
        CONF_NAME: config_entry.data.get(CONF_NAME),
        CONF_LOCATION: config_entry.data.get(CONF_LOCATION),
        CALCULATION_METHOD: config_entry.data.get(CALCULATION_METHOD),
    }


@callback
def configured_instances(hass: HomeAssistant) -> set[str]:
    """Return a set of configured instances."""
    entries = [
        str(entry.data.get(CONF_LOCATION))
        for entry in hass.config_entries.async_entries(DOMAIN)
    ]
    return set(entries)


class MawaqeetFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Mawaqeet."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        if user_input is not None:
            is_coordinates_predefined = str(
                user_input.get(CONF_LOCATION)
            ) in configured_instances(self.hass)

            if is_coordinates_predefined:
                _errors[CONF_LOCATION] = "coordinates_configured"

            if len(_errors) == 0:
                self.user_data = user_input
                return await self.async_step_adjustment()

        data_schema = self.add_suggested_values_to_schema(
            vol.Schema(DATA_SCHEMA), _get_data_schema(self.hass)
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=_errors, last_step=False
        )

    async def async_step_adjustment(self, user_input: dict | None = None) -> FlowResult:
        """Step adjustment."""
        _errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=self.user_data[CONF_NAME], data=self.user_data, options=user_input
            )

        data_schema = vol.Schema({})
        if self.user_data[CALCULATION_METHOD] == str(CalculationMethod.CUSTOM):
            data_schema = data_schema.extend(CALCULATION_SCHEMA)

        data_schema = data_schema.extend(ADJUSTMENT_SCHEMA)

        suggested_values = {
            FAJR_ANGLE: 18,
            ISHAA_ANGLE: 18,
            ISHAA_INTERVAL: 0,
        }

        data_schema = self.add_suggested_values_to_schema(data_schema, suggested_values)
        return self.async_show_form(
            step_id="adjustment", data_schema=data_schema, errors=_errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for Mawaqeet."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(OptionsFlow):
    """Options flow for Mawaqeet component."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the Mawaqeet OptionsFlow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> Any:
        """Step init."""
        return await self.async_step_adjustment(user_input)

    async def async_step_adjustment(self, user_input: dict | None = None) -> FlowResult:
        """Configure options for Mawaqeet."""
        _errors: dict = {}

        if user_input is not None:
            # Update config entry with data from user input
            self.hass.config_entries.async_update_entry(
                self._config_entry, options=user_input
            )
            return self.async_create_entry(
                title=self._config_entry.title, data=user_input
            )

        data_schema = vol.Schema({})
        if self._config_entry.data[CALCULATION_METHOD] == str(CalculationMethod.CUSTOM):
            data_schema = data_schema.extend(CALCULATION_SCHEMA)

        data_schema = data_schema.extend(ADJUSTMENT_SCHEMA)
        options = self._config_entry.options
        data_schema = self.add_suggested_values_to_schema(data_schema, options)

        return self.async_show_form(
            step_id="adjustment",
            data_schema=data_schema,
            errors=_errors,
        )
