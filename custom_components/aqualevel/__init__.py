"""The AquaLevel integration."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Only use the sensor platform initially to validate connection
PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the AquaLevel component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up AquaLevel from a config entry."""
    host = entry.data["host"]
    
    # Create a simple session for testing connection
    session = async_get_clientsession(hass)
    
    # Test connection to device
    try:
        async with session.get(f"http://{host}/tank-data", timeout=10) as resp:
            _LOGGER.debug(f"Connection test to {host}/tank-data: status={resp.status}")
    except Exception as err:
        _LOGGER.error(f"Connection test failed: {err}")
    
    # Store entry data
    hass.data[DOMAIN][entry.entry_id] = {
        "host": host,
        "session": session
    }

    # Only set up the sensor platform initially
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok
