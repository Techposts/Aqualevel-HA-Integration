"""
AquaLevel integration for Home Assistant.
For more details about this integration, please refer to the documentation at
https://github.com/techposts/aqualevel-homeassistant
"""
import asyncio
import logging
import aiohttp
import voluptuous as vol
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    UnitOfLength,
    PERCENTAGE,
    VOLUME_LITERS,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# Define platform names
DOMAIN = "aqualevel"
DEFAULT_NAME = "AquaLevel"
DATA_UPDATED = f"{DOMAIN}_data_updated"

# Add all platforms
PLATFORMS = ["sensor", "number", "button", "binary_sensor", "switch"]

# Configuration schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

# Scan interval (how often to poll the device)
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the AquaLevel component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Register services
    from .service import async_setup_services
    await async_setup_services(hass)
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up AquaLevel from a config entry."""
    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)

    coordinator = AquaLevelDataUpdateCoordinator(hass, host, name)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        raise ConfigEntryNotReady(f"Failed to connect to AquaLevel at {host}")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # If this is the last entry, unload services
        if not hass.data[DOMAIN]:
            from .service import async_unload_services
            await async_unload_services(hass)
            
    return unload_ok

class AquaLevelDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AquaLevel data."""

    def __init__(self, hass, host, name):
        """Initialize."""
        self.host = host
        self.name = name
        self.session = async_get_clientsession(hass)
        self.data = {}
        self.available = True

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from AquaLevel."""
        try:
            # Fetch tank data
            tank_data = await self._fetch_tank_data()
            settings = await self._fetch_settings()
            
            if settings is None and tank_data is None:
                self.available = False
                raise UpdateFailed("Failed to update data from AquaLevel device")
            
            # Use previous settings data if new fetch failed
            if settings is None and hasattr(self, "data") and "tankHeight" in self.data:
                settings = {
                    k: v for k, v in self.data.items() 
                    if k not in ["distance", "waterLevel", "percentage", "volume"]
                }
            
            # Combine the data (with defaults for missing values)
            data = {}
            
            # Add tank data values
            if tank_data:
                data.update({
                    "distance": tank_data.get("distance", 0),
                    "waterLevel": tank_data.get("waterLevel", 0),
                    "percentage": tank_data.get("percentage", 0),
                    "volume": tank_data.get("volume", 0),
                })
            
            # Add settings values
            if settings:
                data.update({
                    "tankHeight": settings.get("tankHeight", 100),
                    "tankDiameter": settings.get("tankDiameter", 50),
                    "tankVolume": settings.get("tankVolume", 200),
                    "sensorOffset": settings.get("sensorOffset", 5),
                    "emptyDistance": settings.get("emptyDistance", 95),
                    "fullDistance": settings.get("fullDistance", 5),
                    "measurementInterval": settings.get("measurementInterval", 5),
                    "readingSmoothing": settings.get("readingSmoothing", 5),
                    "alertLevelLow": settings.get("alertLevelLow", 10),
                    "alertLevelHigh": settings.get("alertLevelHigh", 90),
                    "alertsEnabled": settings.get("alertsEnabled", True),
                })
            
            self.available = True
            return data
        except Exception as err:
            self.available = False
            _LOGGER.exception("Error communicating with AquaLevel: %s", err)
            raise UpdateFailed(f"Error communicating with AquaLevel: {err}")

    async def _fetch_tank_data(self):
        """Fetch current tank data from device."""
        try:
            async with self.session.get(f"http://{self.host}/tank-data", timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    _LOGGER.error("Failed to get tank data, status: %s", resp.status)
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.debug("Error fetching tank data: %s", err)
            return None
        except ValueError as err:
            _LOGGER.error("Error parsing tank data JSON: %s", err)
            return None

    async def _fetch_settings(self):
        """Fetch settings from device."""
        try:
            async with self.session.get(f"http://{self.host}/settings", timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    _LOGGER.error("Failed to get settings, status: %s", resp.status)
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.debug("Error fetching settings: %s", err)
            return None
        except ValueError as err:
            _LOGGER.error("Error parsing settings JSON: %s", err)
            return None

    async def async_update_settings(self, **kwargs):
        """Update device settings."""
        _LOGGER.debug(f"Updating AquaLevel settings: {kwargs}")
        
        # Prepare parameters for API
        params = {}
        
        # Map parameters from HA to device format
        param_map = {
            'tank_height': 'tankHeight',
            'tank_diameter': 'tankDiameter',
            'tank_volume': 'tankVolume',
            'sensor_offset': 'sensorOffset',
            'empty_distance': 'emptyDistance',
            'full_distance': 'fullDistance',
            'measurement_interval': 'measurementInterval',
            'reading_smoothing': 'readingSmoothing',
            'alert_level_low': 'alertLevelLow',
            'alert_level_high': 'alertLevelHigh',
            'alerts_enabled': 'alertsEnabled',
        }
        
        # Map parameters
        for ha_param, device_param in param_map.items():
            if ha_param in kwargs:
                value = kwargs[ha_param]
                
                # Convert booleans to integers for the API
                if isinstance(value, bool):
                    value = 1 if value else 0
                    
                params[device_param] = value
        
        if not params:
            _LOGGER.warning("No valid parameters to update")
            return False
        
        # Construct query string
        param_strings = [f"{k}={v}" for k, v in params.items()]
        url = f"http://{self.host}/set?{('&'.join(param_strings))}"
        
        _LOGGER.debug(f"Sending update request to: {url}")
        
        try:
            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    response_text = await resp.text()
                    _LOGGER.debug(f"Device response: {response_text}")
                    
                    # Trigger immediate data refresh
                    await self.async_refresh()
                    return True
                else:
                    _LOGGER.error(f"Failed to update settings. Status: {resp.status}")
                    return False
        except Exception as err:
            _LOGGER.error(f"Error updating settings: {err}")
            return False

    async def async_calibrate(self, calibration_type):
        """Calibrate the tank sensor."""
        if calibration_type not in ["empty", "full"]:
            _LOGGER.error(f"Invalid calibration type: {calibration_type}")
            return False
            
        url = f"http://{self.host}/calibrate?type={calibration_type}"
        
        try:
            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    response_text = await resp.text()
                    _LOGGER.debug(f"Calibration response: {response_text}")
                    
                    # Trigger immediate data refresh
                    await self.async_refresh()
                    return True
                else:
                    _LOGGER.error(f"Calibration failed. Status: {resp.status}")
                    return False
        except Exception as err:
            _LOGGER.error(f"Error during calibration: {err}")
            return False
