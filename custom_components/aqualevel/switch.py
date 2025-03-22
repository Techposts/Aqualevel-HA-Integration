"""AquaLevel switch platform for toggling alerts."""
import logging
import asyncio

from homeassistant.components.switch import SwitchEntity
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
    """Set up AquaLevel switch entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        AquaLevelAlertsEnabledSwitch(coordinator),
    ]
    
    async_add_entities(entities)


class AquaLevelAlertsEnabledSwitch(CoordinatorEntity, SwitchEntity):
    """Switch for enabling/disabling alerts."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AquaLevelDataUpdateCoordinator):
        """Initialize the switch entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_alerts_enabled"
        self._attr_name = "Alerts Enabled"
        self._attr_icon = "mdi:bell-ring-outline"
            
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
        return (self.coordinator.data is not None and 
                "alertsEnabled" in self.coordinator.data)

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if not self.coordinator.data:
            return False
        return bool(self.coordinator.data.get("alertsEnabled", True))

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self.coordinator.async_update_settings(alerts_enabled=True)
        
        # Optimistically update state
        self.async_write_ha_state()
        
        # Force a state refresh
        await asyncio.sleep(2)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self.coordinator.async_update_settings(alerts_enabled=False)
        
        # Optimistically update state
        self.async_write_ha_state()
        
        # Force a state refresh
        await asyncio.sleep(2)
        await self.coordinator.async_refresh()
