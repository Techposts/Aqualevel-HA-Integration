"""AquaLevel number platform for configurable settings."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfLength, PERCENTAGE, VOLUME_LITERS, UnitOfTime
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
    """Set up AquaLevel number entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        AquaLevelTankHeightNumber(coordinator),
        AquaLevelTankDiameterNumber(coordinator),
        AquaLevelTankVolumeNumber(coordinator),
        AquaLevelSensorOffsetNumber(coordinator),
        AquaLevelEmptyDistanceNumber(coordinator),
        AquaLevelFullDistanceNumber(coordinator),
        AquaLevelMeasurementIntervalNumber(coordinator),
        AquaLevelReadingSmoothingNumber(coordinator),
        AquaLevelAlertLevelLowNumber(coordinator),
        AquaLevelAlertLevelHighNumber(coordinator),
    ]
    
    async_add_entities(entities)


class AquaLevelNumberEntity(CoordinatorEntity, NumberEntity):
    """Base class for AquaLevel number entities."""

    _attr_has_entity_name = True

    def __init__(
        self, 
        coordinator: AquaLevelDataUpdateCoordinator,
        name_suffix: str,
        key: str,
        minimum: float,
        maximum: float,
        step: float,
        unit: str = None,
        icon: str = None,
        service_param: str = None
    ):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = name_suffix
        self._attr_unique_id = f"{coordinator.host}_{key}"
        self._key = key
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._service_param = service_param or key
        if unit:
            self._attr_native_unit_of_measurement = unit
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
        """Return the current value."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._key)

    async def async_set_native_value(self, value):
        """Set new value."""
        await self.coordinator.async_update_settings(**{self._service_param: value})


class AquaLevelTankHeightNumber(AquaLevelNumberEntity):
    """Representation of the tank height setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Tank Height",
            key="tankHeight",
            minimum=10,
            maximum=500,
            step=0.1,
            unit=UnitOfLength.CENTIMETERS,
            icon="mdi:arrow-up-down",
            service_param="tank_height"
        )


class AquaLevelTankDiameterNumber(AquaLevelNumberEntity):
    """Representation of the tank diameter setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Tank Diameter",
            key="tankDiameter",
            minimum=10,
            maximum=500,
            step=0.1,
            unit=UnitOfLength.CENTIMETERS,
            icon="mdi:arrow-left-right",
            service_param="tank_diameter"
        )


class AquaLevelTankVolumeNumber(AquaLevelNumberEntity):
    """Representation of the tank volume setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Tank Volume",
            key="tankVolume",
            minimum=1,
            maximum=10000,
            step=0.1,
            unit=VOLUME_LITERS,
            icon="mdi:tank",
            service_param="tank_volume"
        )


class AquaLevelSensorOffsetNumber(AquaLevelNumberEntity):
    """Representation of the sensor offset setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Sensor Offset",
            key="sensorOffset",
            minimum=0,
            maximum=100,
            step=0.1,
            unit=UnitOfLength.CENTIMETERS,
            icon="mdi:arrow-collapse-up",
            service_param="sensor_offset"
        )


class AquaLevelEmptyDistanceNumber(AquaLevelNumberEntity):
    """Representation of the empty distance setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Empty Distance",
            key="emptyDistance",
            minimum=10,
            maximum=500,
            step=0.1,
            unit=UnitOfLength.CENTIMETERS,
            icon="mdi:signal-distance-variant",
            service_param="empty_distance"
        )


class AquaLevelFullDistanceNumber(AquaLevelNumberEntity):
    """Representation of the full distance setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Full Distance",
            key="fullDistance",
            minimum=0,
            maximum=100,
            step=0.1,
            unit=UnitOfLength.CENTIMETERS,
            icon="mdi:signal-distance-variant",
            service_param="full_distance"
        )


class AquaLevelMeasurementIntervalNumber(AquaLevelNumberEntity):
    """Representation of the measurement interval setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Measurement Interval",
            key="measurementInterval",
            minimum=1,
            maximum=3600,
            step=1,
            unit=UnitOfTime.SECONDS,
            icon="mdi:timer-outline",
            service_param="measurement_interval"
        )


class AquaLevelReadingSmoothingNumber(AquaLevelNumberEntity):
    """Representation of the reading smoothing setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Reading Smoothing",
            key="readingSmoothing",
            minimum=1,
            maximum=50,
            step=1,
            icon="mdi:chart-bell-curve",
            service_param="reading_smoothing"
        )


class AquaLevelAlertLevelLowNumber(AquaLevelNumberEntity):
    """Representation of the low alert level setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="Low Alert Level",
            key="alertLevelLow",
            minimum=0,
            maximum=100,
            step=1,
            unit=PERCENTAGE,
            icon="mdi:alert-outline",
            service_param="alert_level_low"
        )


class AquaLevelAlertLevelHighNumber(AquaLevelNumberEntity):
    """Representation of the high alert level setting."""

    def __init__(self, coordinator):
        """Initialize the entity."""
        super().__init__(
            coordinator=coordinator,
            name_suffix="High Alert Level",
            key="alertLevelHigh",
            minimum=0,
            maximum=100,
            step=1,
            unit=PERCENTAGE,
            icon="mdi:alert-outline",
            service_param="alert_level_high"
        )
