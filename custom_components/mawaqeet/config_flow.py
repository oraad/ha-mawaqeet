"""Adds config flow for Mawaqeet."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.selector import (
    BooleanSelector,
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
    DEFAULT_REMINDER_MINUTES,
    DOCUMENTATION_URL,
    DOMAIN,
    FAJR_ANGLE,
    HIGH_LATITUDE_RULE,
    ISHAA_ANGLE,
    ISHAA_INTERVAL,
    MADHAB,
    REMINDER_ENABLED,
)
from .enum import (
    REMINDER_SCHEDULE_PRAYERS,
    CalculationMethod,
    HighLatitudeRule,
    Madhab,
    PrayerAdjustment,
    prayer_reminder_minutes_key,
)
from .options import migrate_options

REMINDER_MINUTES_SELECTOR = NumberSelector(
    NumberSelectorConfig(min=1, max=60, mode=NumberSelectorMode.BOX, step=1)
)

DATA_SCHEMA = {
    vol.Required(CONF_NAME): str,
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
    vol.Optional(REMINDER_ENABLED, default=True): BooleanSelector(),
    **{
        vol.Optional(
            prayer_reminder_minutes_key(prayer), default=DEFAULT_REMINDER_MINUTES
        ): REMINDER_MINUTES_SELECTOR
        for prayer in REMINDER_SCHEDULE_PRAYERS
    },
}

DEFAULT_ADJUSTMENT_VALUES = {
    FAJR_ANGLE: 18,
    ISHAA_ANGLE: 18,
    ISHAA_INTERVAL: 0,
    REMINDER_ENABLED: True,
    **{
        prayer_reminder_minutes_key(prayer): DEFAULT_REMINDER_MINUTES
        for prayer in REMINDER_SCHEDULE_PRAYERS
    },
}


def _location_unique_id(location: dict[str, float]) -> str:
    """Build a stable unique id from a location dict."""
    latitude = location[CONF_LATITUDE]
    longitude = location[CONF_LONGITUDE]
    return f"{latitude:.6f}_{longitude:.6f}"


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


def _merged_options(config_entry: ConfigEntry) -> dict[str, Any]:
    """Return options with defaults and legacy migration applied."""
    return migrate_options({**DEFAULT_ADJUSTMENT_VALUES, **config_entry.options})


def _build_adjustment_schema(calculation_method: str) -> vol.Schema:
    """Build the adjustment options schema."""
    data_schema = vol.Schema({})
    if calculation_method == str(CalculationMethod.CUSTOM):
        data_schema = data_schema.extend(CALCULATION_SCHEMA)
    return data_schema.extend(ADJUSTMENT_SCHEMA)


class MawaqeetFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Mawaqeet."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self.user_data: dict[str, Any] = {}

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            await self.async_set_unique_id(
                _location_unique_id(user_input[CONF_LOCATION])
            )
            self._abort_if_unique_id_configured()
            self.user_data = user_input
            return await self.async_step_adjustment()

        data_schema = self.add_suggested_values_to_schema(
            vol.Schema(DATA_SCHEMA), _get_data_schema(self.hass)
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={"documentation_url": DOCUMENTATION_URL},
            last_step=False,
        )

    async def async_step_adjustment(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Step adjustment."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.user_data[CONF_NAME],
                data=self.user_data,
                options=migrate_options(user_input),
            )

        data_schema = _build_adjustment_schema(self.user_data[CALCULATION_METHOD])
        data_schema = self.add_suggested_values_to_schema(
            data_schema, DEFAULT_ADJUSTMENT_VALUES
        )
        return self.async_show_form(step_id="adjustment", data_schema=data_schema)

    async def async_step_reconfigure(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            new_unique_id = _location_unique_id(user_input[CONF_LOCATION])
            await self.async_set_unique_id(new_unique_id)
            if new_unique_id == reconfigure_entry.unique_id:
                self._abort_if_unique_id_mismatch()
            else:
                self._abort_if_unique_id_configured()
            return self.async_update_reload_and_abort(
                reconfigure_entry,
                data_updates=user_input,
                unique_id=new_unique_id,
            )

        data_schema = self.add_suggested_values_to_schema(
            vol.Schema(DATA_SCHEMA), _get_data_schema(self.hass, reconfigure_entry)
        )

        return self.async_show_form(step_id="reconfigure", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: ConfigEntry,
    ) -> MawaqeetOptionsFlowHandler:
        """Get the options flow for Mawaqeet."""
        return MawaqeetOptionsFlowHandler()


class MawaqeetOptionsFlowHandler(OptionsFlowWithReload):
    """Options flow for Mawaqeet component."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure options for Mawaqeet."""
        return await self.async_step_adjustment(user_input)

    async def async_step_adjustment(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure adjustment options."""
        if user_input is not None:
            return self.async_create_entry(data=migrate_options(user_input))

        calculation_method = self.config_entry.data[CALCULATION_METHOD]
        data_schema = _build_adjustment_schema(calculation_method)
        data_schema = self.add_suggested_values_to_schema(
            data_schema, _merged_options(self.config_entry)
        )

        return self.async_show_form(step_id="adjustment", data_schema=data_schema)
