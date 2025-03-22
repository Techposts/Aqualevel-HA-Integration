"""Platform for AquaLevel sensor integration."""
import logging
import asyncio
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up AquaLevel sensor based on a config entry."""
    host = entry.data["host"]
    session = async_get_clientsession(hass)
    
    async_add_entities([AquaLevelSensor(host, session)], True)

class AquaLevelSensor(SensorEntity):
    """Representation of an AquaLevel sensor."""

    def __init__(self, host, session):
        """Initialize the sensor."""
        self._host = host
        self._session = session
        self._name = "AquaLevel Water Percentage"
        self._attr_unique_id = f"{host}_water_percentage"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_should_poll = True
        self._available = True
        self._state = None
        self._attr_icon = "mdi:water-percent"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Get the latest data and update states."""
        try:
            url = f"http://{self._host}/tank-data"
            async with self._session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        self._state = data.get("percentage")
                        self._available = True
                        _LOGGER.debug(f"Data update successful: {data}")
                    except:
                        # Try to parse as text if not json
                        text = await resp.text()
                        _LOGGER.debug(f"Response not JSON, got: {text}")
                        self._available = False
                else:
                    self._available = False
        except Exception as err:
            _LOGGER.error(f"Error fetching data: {err}")
            self._available = False
