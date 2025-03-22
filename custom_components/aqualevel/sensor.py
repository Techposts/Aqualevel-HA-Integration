"""AquaLevel sensor platform for water level and volume readings."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfLength, 
    PERCENTAGE, 
    VOLUME_LITERS,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from . import DOMAIN, AquaLevelDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up AquaLevel sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        AquaLevelDistanceSensor(coordinator),
        AquaLevelWaterLevelSensor(coordinator),
        AquaLevelWaterPercentageSensor(coordinator),
    ]
    
    async_add_entities(entities)


class AquaLevelSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for AquaLevel sensors."""

    _attr_has_entity_name = True

    def __init__(
        self, 
        coordinator: AquaLevelDataUpdateCoordinator,
        name_suffix: str,
        key: str,
        device_class: str = None,
        state_class: str = None,
        unit_of_measurement: str = None,
        icon: str = None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_{key}"
        self._attr_name = name_suffix
        self._key = key
        
        if device_class:
            self._attr_device_class = device_class
        if state_class:
            self._attr_state_class = state_class
        if unit_of_measurement:
            self._attr_native_unit_of_measurement = unit_of_measurement
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
        return self.coordinator.data is not None and self._key in self.coordinator.data

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None or self._key not in self.coordinator.data:
            return None
        return self.coordinator.data[self._key]


class AquaLevelDistanceSensor(AquaLevelSensorBase):
    """Representation of the distance measurement from the ultrasonic sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Distance",
            key="distance",
            device_class=SensorDeviceClass.DISTANCE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfLength.CENTIMETERS,
            icon="mdi:ruler",
        )


class AquaLevelWaterLevelSensor(AquaLevelSensorBase):
    """Representation of the water level height in the tank."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Water Level",
            key="waterLevel",
            device_class=SensorDeviceClass.DISTANCE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfLength.CENTIMETERS,
            icon="mdi:water",
        )


class AquaLevelWaterPercentageSensor(AquaLevelSensorBase):
    """Representation of the water level as a percentage."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Water Percentage",
            key="percentage",
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=PERCENTAGE,
            icon="mdi:water-percent",
        )
