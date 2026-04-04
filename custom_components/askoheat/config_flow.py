"""Config flow for Askoheat integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import AskoheatApiClient, AskoheatConnectionError
from .const import (
    CONF_SCAN_INTERVAL, CONF_SENSORS, CON_INPUT_SETTING,
    DEFAULT_SCAN_INTERVAL, DOMAIN, INPUT_SETTING_SETPOINT,
    PAR_ARTICLE_NAME, PAR_ID,
)

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


class AskoheatConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Askoheat."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None
        self._par_data: dict[str, Any] = {}
        self._connected_sensors: list[int] = []
        self._setpoint_warning: bool = False

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            client = AskoheatApiClient(host=self._host)
            try:
                self._par_data = await client.get_par()
                self._connected_sensors = await client.detect_connected_sensors()
                con = await client.get_con()
                input_setting = int(con.get(CON_INPUT_SETTING, "0"))
                self._setpoint_warning = not (input_setting & INPUT_SETTING_SETPOINT)
            except Exception:
                errors["base"] = "cannot_connect"
            finally:
                await client.close()

            if not errors:
                unique_id = self._par_data.get(PAR_ID, self._host)
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                title = self._par_data.get(PAR_ARTICLE_NAME, f"Askoheat ({self._host})")
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_HOST: self._host,
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                        CONF_SENSORS: self._connected_sensors,
                        "setpoint_warning": self._setpoint_warning,
                    },
                )
        return self.async_show_form(step_id="user", data_schema=USER_SCHEMA, errors=errors)

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        self._host = str(discovery_info.host)
        client = AskoheatApiClient(host=self._host)
        try:
            self._par_data = await client.get_par()
            self._connected_sensors = await client.detect_connected_sensors()
        except Exception:
            return self.async_abort(reason="cannot_connect")
        finally:
            await client.close()

        unique_id = self._par_data.get(PAR_ID, self._host)
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: self._host})
        self.context["title_placeholders"] = {
            "name": self._par_data.get(PAR_ARTICLE_NAME, "Askoheat"),
        }
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            title = self._par_data.get(PAR_ARTICLE_NAME, f"Askoheat ({self._host})")
            return self.async_create_entry(
                title=title,
                data={
                    CONF_HOST: self._host,
                    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    CONF_SENSORS: self._connected_sensors,
                },
            )
        return self.async_show_form(step_id="zeroconf_confirm")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AskoheatOptionsFlow(config_entry)


class AskoheatOptionsFlow(OptionsFlow):
    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_SCAN_INTERVAL, default=current_interval): vol.All(int, vol.Range(min=1, max=300)),
            }),
        )
