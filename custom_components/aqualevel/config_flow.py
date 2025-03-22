"""Config flow for AquaLevel integration."""
from __future__ import annotations

import asyncio
import logging
import aiohttp
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import HomeAssistantError

from . import DOMAIN, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    }
)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class AquaLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AquaLevel."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await self._validate_input(user_input)
                
                # Set this as the unique ID
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors
        )

    async def _validate_input(self, data):
        """Validate the user input allows us to connect."""
        host = data[CONF_HOST]
        name = data.get(CONF_NAME, DEFAULT_NAME)
        
        # Verify that we can connect to the device
        session = async_get_clientsession(self.hass)
        
        try:
            # First try tank-data endpoint
            tank_url = f"http://{host}/tank-data"
            async with session.get(tank_url, timeout=10) as response:
                if response.status != 200:
                    raise CannotConnect
                
                # Try to parse response
                try:
                    await response.json()
                except:
                    # If not JSON, see if we get a valid response at all
                    text = await response.text()
                    if not text:
                        raise CannotConnect
                    
        except (asyncio.TimeoutError, aiohttp.ClientError):
            # If tank-data fails, try settings endpoint
            try:
                settings_url = f"http://{host}/settings"
                async with session.get(settings_url, timeout=10) as response:
                    if response.status != 200:
                        raise CannotConnect
                    await response.json()
            except (asyncio.TimeoutError, aiohttp.ClientError, ValueError):
                raise CannotConnect
            
        # If we get here, the connection was successful
        return {
            "title": name
        }

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Return the options flow handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for AquaLevel."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({})
        )
