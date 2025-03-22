from __future__ import annotations

import asyncio
import logging
import aiohttp
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout

from .const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_NAME

_LOGGER = logging.getLogger(__name__)

def _validate_host(host: str) -> bool:
    """Validate the given host string."""
    return isinstance(host, str) and len(host) > 0

async def _try_connect(hass, host: str) -> bool:
    """Try connecting to the AquaLevel device."""
    session = async_get_clientsession(hass)
    
    # Try connecting to the status endpoint
    for endpoint in ["/tank-data", "/settings", "/status"]:
        try:
            async with async_timeout.timeout(5):
                url = f"http://{host}{endpoint}"
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            await response.json()
                            return True
                        except:
                            pass
        except (asyncio.TimeoutError, aiohttp.ClientError):
            continue
    
    return False

class AquaLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aqua Level."""
    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the user-initiated config flow."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input.get(CONF_NAME)
            
            if _validate_host(host):
                # Check if we can connect to the device
                if await _try_connect(self.hass, host):
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                    
                    data = {CONF_HOST: host}
                    if name:
                        data[CONF_NAME] = name
                        
                    return self.async_create_entry(
                        title=name or host, 
                        data=data
                    )
                else:
                    errors[CONF_HOST] = "cannot_connect"
            else:
                errors[CONF_HOST] = "invalid_host"

        # Show the form
        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_NAME): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow handler."""
        return AquaLevelOptionsFlowHandler(config_entry)

class AquaLevelOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Aqua Level options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Manage Aqua Level options."""
        return self.async_create_entry(title="", data={})
