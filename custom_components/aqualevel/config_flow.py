from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any, Dict, Optional

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode
import async_timeout

from .const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_NAME

_LOGGER = logging.getLogger(__name__)

def _validate_host(host: str) -> bool:
    """Validate the given host string."""
    return isinstance(host, str) and len(host) > 0

async def _try_endpoint(session, url, timeout=5, retries=2):
    """Try connecting to an endpoint with retries."""
    for attempt in range(retries):
        try:
            async with async_timeout.timeout(timeout):
                async with session.get(url) as response:
                    if response.status == 200:
                        await response.json()
                        return True
        except (asyncio.TimeoutError, aiohttp.ClientError, ValueError):
            if attempt == retries - 1:
                return False
    return False

class AquaLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aqua Level."""
    VERSION = 1

    def __init__(self):
        self._host: Optional[str] = None
        self._discovered_devices: Dict[str, str] = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the user-initiated config flow."""
        errors = {}

        if not self._discovered_devices:
            self._discovered_devices = await self._discover_devices()

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input.get(CONF_NAME)
            
            if _validate_host(host):
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
                errors[CONF_HOST] = "invalid_host"

        # Different schema based on whether devices were discovered
        if self._discovered_devices:
            schema = vol.Schema({
                vol.Required(CONF_HOST): SelectSelector(
                    SelectSelectorConfig(
                        options=list(self._discovered_devices.keys()),
                        mode=SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Optional(CONF_NAME): str,
            })
        else:
            # No devices discovered, allow manual entry
            schema = vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME): str,
            })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_zeroconf(self, discovery_info: Dict[str, Any]) -> FlowResult:
        """Handle discovery via Zeroconf."""
        if not discovery_info.get("host"):
            return self.async_abort(reason="no_host_info")

        self._host = discovery_info["host"]
        await self.async_set_unique_id(self._host)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=self._host, data={CONF_HOST: self._host})

    async def _discover_devices(self) -> Dict[str, str]:
        """Discover AquaLevel devices on the local network."""
        session = async_get_clientsession(self.hass)
        discovered = {}
        
        # Try both possible hostname formats
        hostnames = ["aqua-level", "aqualevel-garden", "aqualevel-main"]
        
        for hostname in hostnames:
            try:
                addr_info = await self.hass.async_add_executor_job(
                    socket.gethostbyname, f"{hostname}.local"
                )
                url = f"http://{addr_info}/status"
                if await _try_endpoint(session, url):
                    discovered[addr_info] = hostname
            except socket.gaierror:
                _LOGGER.debug("Could not resolve %s.local", hostname)
        
        # Try to scan for devices with aqualevel- prefix
        try:
            import zeroconf
            browser = zeroconf.ServiceBrowser(
                zeroconf.Zeroconf(), "_http._tcp.local.",
                handlers=[self._on_service_state_change]
            )
            # Give some time for discovery
            await asyncio.sleep(3)
            browser.cancel()
        except (ImportError, Exception) as err:
            _LOGGER.debug("Error during mDNS scan: %s", err)
            
        return discovered
    
    def _on_service_state_change(self, zeroconf, service_type, name, state_change):
        """Handle zeroconf state changes."""
        if state_change in [zeroconf.ServiceStateChange.Added, zeroconf.ServiceStateChange.Updated]:
            info = zeroconf.get_service_info(service_type, name)
            if info and "aqualevel" in name.lower():
                # Extract IP address
                for addr in info.parsed_addresses():
                    self._discovered_devices[addr] = name.split('.')[0]

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
