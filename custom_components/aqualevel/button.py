"""AquaLevel button platform."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up AquaLevel button entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        AquaLevelCalibrateEmptyButton(coordinator),
        AquaLevelCalibrateFullButton(coordinator),
    ]
    
    async_add_entities(entities)


class AquaLevelCalibrateEmptyButton(CoordinatorEntity, ButtonEntity):
    """Button for calibrating the empty tank level."""

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_calibrate_empty"
        self._attr_name = "Calibrate Empty Tank"
        self._attr_icon = "mdi:water-off"
        
        # Device info for device registry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=coordinator.name,
            manufacturer="TechPosts Media",
            model="AquaLevel Water Tank Monitor",
            sw_version="1.0",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Calibrating empty tank")
        await self.coordinator.async_calibrate("empty")


class AquaLevelCalibrateFullButton(CoordinatorEntity, ButtonEntity):
    """Button for calibrating the full tank level."""

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_calibrate_full"
        self._attr_name = "Calibrate Full Tank"
        self._attr_icon = "mdi:water"
        
        # Device info for device registry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=coordinator.name,
            manufacturer="TechPosts Media",
            model="AquaLevel Water Tank Monitor",
            sw_version="1.0",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Calibrating full tank")
        await self.coordinator.async_calibrate("full")
