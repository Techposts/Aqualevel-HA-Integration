"""Config flow for AquaLevel integration."""
import logging
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_NAME, default="AquaLevel"): str,
})

class AquaLevelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AquaLevel."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                # Validate input
                host = user_input[CONF_HOST]
                
                # Test connection to device
                session = async_get_clientsession(self.hass)
                
                try:
                    # Try tank-data endpoint
                    async with session.get(f"http://{host}/tank-data", timeout=10) as resp:
                        if resp.status == 200:
                            # Connection successful
                            await self.async_set_unique_id(host)
                            self._abort_if_unique_id_configured()
                            return self.async_create_entry(
                                title=user_input.get(CONF_NAME, "AquaLevel"),
                                data=user_input,
                            )
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    # Try settings endpoint as fallback
                    try:
                        async with session.get(f"http://{host}/settings", timeout=10) as resp:
                            if resp.status == 200:
                                # Connection successful
                                await self.async_set_unique_id(host)
                                self._abort_if_unique_id_configured()
                                return self.async_create_entry(
                                    title=user_input.get(CONF_NAME, "AquaLevel"),
                                    data=user_input,
                                )
                    except:
                        pass
                
                # If we get here, connection failed
                errors["base"] = "cannot_connect"
            except Exception as error:
                _LOGGER.exception("Unexpected exception: %s", error)
                errors["base"] = "unknown"
        
        # Show form
        return self.async_show_form(
            step_id="user", 
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )
