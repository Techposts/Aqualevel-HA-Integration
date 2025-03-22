"""AquaLevel number platform for configurable settings."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfLength, VOLUME_LITERS, UnitOfTime
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
        AquaLevelEmptyDistanceNumber(coordinator),
        AquaLevelFullDistanceNumber(coordinator),
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
        param_name: str = None
    ):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = name_suffix
        self._attr_unique_id = f"{coordinator.host}_{key}"
        self._key = key
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._param_name = param_name or key
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
        await self.coordinator.async_update_setting(self._param_name, value)


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
            param_name="tankHeight"
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
            param_name="tankDiameter"
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
            param_name="emptyDistance"
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
            param_name="fullDistance"
        )
