"""AquaLevel binary sensor platform."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up AquaLevel binary sensor entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        AquaLevelLowWaterAlert(coordinator),
        AquaLevelHighWaterAlert(coordinator),
    ]
    
    async_add_entities(entities)


class AquaLevelAlertBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class for AquaLevel alert binary sensors."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self, 
        coordinator,
        name_suffix: str,
        key: str,
        icon: str = None,
    ):
        """Initialize the binary sensor entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_{key}"
        self._attr_name = name_suffix
        self._key = key
        if icon:
            self._attr_icon = icon
            
        # Device info for device registry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=coordinator.name,
            manufacturer="TechPosts Media",
            model="AquaLevel Water Tank Monitor",
            sw_version="1.0",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not self.coordinator.data:
            return False
            
        # Check for required data to determine alert state
        required_keys = ["percentage"]
        if not all(key in self.coordinator.data for key in required_keys):
            return False
            
        # Check alert threshold values are available
        if self._key == "low_water_alert" and "alertLevelLow" not in self.coordinator.data:
            return False
        if self._key == "high_water_alert" and "alertLevelHigh" not in self.coordinator.data:
            return False
            
        return True


class AquaLevelLowWaterAlert(AquaLevelAlertBinarySensor):
    """Binary sensor for low water level alert."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Low Water Alert",
            key="low_water_alert",
            icon="mdi:water-alert",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the water level is below the low alert threshold."""
        if not self.coordinator.data:
            return False
            
        # Only show alert if alerts are enabled
        if not self.coordinator.data.get("alertsEnabled", True):
            return False
            
        percentage = self.coordinator.data.get("percentage", 0)
        low_threshold = self.coordinator.data.get("alertLevelLow", 10)
        
        return percentage <= low_threshold


class AquaLevelHighWaterAlert(AquaLevelAlertBinarySensor):
    """Binary sensor for high water level alert."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="High Water Alert",
            key="high_water_alert",
            icon="mdi:water-alert",
        )

    @property
    def is_on(self) -> bool:
        """Return true if the water level is above the high alert threshold."""
        if not self.coordinator.data:
            return False
            
        # Only show alert if alerts are enabled
        if not self.coordinator.data.get("alertsEnabled", True):
            return False
            
        percentage = self.coordinator.data.get("percentage", 0)
        high_threshold = self.coordinator.data.get("alertLevelHigh", 90)
        
        return percentage >= high_threshold
