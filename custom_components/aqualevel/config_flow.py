"""Config flow for AquaLevel integration."""
from __future__ import annotations

import asyncio
import logging
import aiohttp
import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components import zeroconf

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


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AquaLevel."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the config flow."""
        self._host = None
        self._name = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Set this as the unique ID
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                # Try to connect to validate
                info = await self._validate_input(user_input)
                
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

    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo) -> FlowResult:
        """Handle zeroconf discovery."""
        # Check if this is our device
        hostname = discovery_info.hostname
        if not hostname.startswith("aqualevel-"):
            return self.async_abort(reason="not_aqualevel_device")

        # Extract name and IP address
        self._name = hostname.replace(".local.", "")
        self._host = discovery_info.host
        
        # Set unique ID based on host
        await self.async_set_unique_id(self._host)
        self._abort_if_unique_id_configured()
        
        # Store discovered device info
        self.context["title_placeholders"] = {"name": self._name}
        
        return await self.async_step_confirm_discovery()
        
    async def async_step_confirm_discovery(self, user_input=None) -> FlowResult:
        """Handle confirmation of discovered device."""
        if user_input is not None:
            try:
                info = await self._validate_input({
                    CONF_HOST: self._host,
                    CONF_NAME: self._name
                })
                
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_HOST: self._host,
                        CONF_NAME: self._name
                    }
                )
            except CannotConnect:
                return self.async_abort(reason="cannot_connect")
            except Exception:
                _LOGGER.exception("Unexpected exception")
                return self.async_abort(reason="unknown")
                
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": self._name},
            data_schema=vol.Schema({})
        )
        
    async def _validate_input(self, data):
        """Validate the user input allows us to connect."""
        host = data[CONF_HOST]
        name = data.get(CONF_NAME, DEFAULT_NAME)
        
        # Verify that we can connect to the device
        session = async_get_clientsession(self.hass)
        
        try:
            # First try tank-data endpoint
            tank_data_url = f"http://{host}/tank-data"
            async with session.get(tank_data_url, timeout=10) as response:
                if response.status != 200:
                    raise CannotConnect
                
                # Try to parse response as JSON
                await response.json()
                
        except (asyncio.TimeoutError, aiohttp.ClientError, ValueError):
            # If tank-data fails, try settings endpoint
            try:
                settings_url = f"http://{host}/settings"
                async with session.get(settings_url, timeout=10) as response:
                    if response.status != 200:
                        raise CannotConnect
                    
                    # Try to parse response as JSON
                    await response.json()
            except (asyncio.TimeoutError, aiohttp.ClientError, ValueError):
                raise CannotConnect
            
        # If we get here, the connection was successful
        return {
            "title": name
        }
