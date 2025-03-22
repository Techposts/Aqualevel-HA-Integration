"""AquaLevel services."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    UnitOfLength, 
    PERCENTAGE, 
    VOLUME_LITERS,
    UnitOfTime,
)

from . import DOMAIN, AquaLevelDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_CALIBRATE = "calibrate"
SERVICE_UPDATE_SETTINGS = "update_settings"

# Parameter constants
ATTR_ENTITY_ID = "entity_id"
ATTR_CALIBRATION_TYPE = "calibration_type"
ATTR_TANK_HEIGHT = "tank_height"
ATTR_TANK_DIAMETER = "tank_diameter"
ATTR_TANK_VOLUME = "tank_volume"
ATTR_SENSOR_OFFSET = "sensor_offset"
ATTR_EMPTY_DISTANCE = "empty_distance"
ATTR_FULL_DISTANCE = "full_distance"
ATTR_MEASUREMENT_INTERVAL = "measurement_interval"
ATTR_READING_SMOOTHING = "reading_smoothing"
ATTR_ALERT_LEVEL_LOW = "alert_level_low"
ATTR_ALERT_LEVEL_HIGH = "alert_level_high"
ATTR_ALERTS_ENABLED = "alerts_enabled"

# Schema for the calibrate service
CALIBRATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_CALIBRATION_TYPE): vol.In(["empty", "full"]),
    }
)

# Schema for the update_settings service
UPDATE_SETTINGS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(ATTR_TANK_HEIGHT): vol.All(vol.Coerce(float), vol.Range(min=10, max=500)),
        vol.Optional(ATTR_TANK_DIAMETER): vol.All(vol.Coerce(float), vol.Range(min=10, max=500)),
        vol.Optional(ATTR_TANK_VOLUME): vol.All(vol.Coerce(float), vol.Range(min=1, max=10000)),
        vol.Optional(ATTR_SENSOR_OFFSET): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_EMPTY_DISTANCE): vol.All(vol.Coerce(float), vol.Range(min=10, max=500)),
        vol.Optional(ATTR_FULL_DISTANCE): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_MEASUREMENT_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
        vol.Optional(ATTR_READING_SMOOTHING): vol.All(vol.Coerce(int), vol.Range(min=1, max=50)),
        vol.Optional(ATTR_ALERT_LEVEL_LOW): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_ALERT_LEVEL_HIGH): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional(ATTR_ALERTS_ENABLED): cv.boolean,
    }
)

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the AquaLevel integration."""
    
    async def async_calibrate_service(service_call: ServiceCall) -> None:
        """Handle calibrate service calls."""
        entity_ids = service_call.data.get(ATTR_ENTITY_ID)
        calibration_type = service_call.data.get(ATTR_CALIBRATION_TYPE)
        
        if not entity_ids:
            return
            
        # Find first valid coordinator from entities
        coordinators = []
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if isinstance(coordinator, AquaLevelDataUpdateCoordinator):
                coordinators.append(coordinator)
        
        if not coordinators:
            _LOGGER.warning("No AquaLevel device found for service call")
            return
            
        # Apply calibration to all coordinators
        for coordinator in coordinators:
            await coordinator.async_calibrate(calibration_type)
    
    async def async_update_settings_service(service_call: ServiceCall) -> None:
        """Handle update settings service calls."""
        entity_ids = service_call.data.get(ATTR_ENTITY_ID)
        
        if not entity_ids:
            return
            
        # Find first valid coordinator from entities
        coordinators = []
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if isinstance(coordinator, AquaLevelDataUpdateCoordinator):
                coordinators.append(coordinator)
        
        if not coordinators:
            _LOGGER.warning("No AquaLevel device found for service call")
            return
            
        # Extract settings
        settings = {}
        
        if ATTR_TANK_HEIGHT in service_call.data:
            settings["tank_height"] = service_call.data[ATTR_TANK_HEIGHT]
        if ATTR_TANK_DIAMETER in service_call.data:
            settings["tank_diameter"] = service_call.data[ATTR_TANK_DIAMETER]
        if ATTR_TANK_VOLUME in service_call.data:
            settings["tank_volume"] = service_call.data[ATTR_TANK_VOLUME]
        if ATTR_SENSOR_OFFSET in service_call.data:
            settings["sensor_offset"] = service_call.data[ATTR_SENSOR_OFFSET]
        if ATTR_EMPTY_DISTANCE in service_call.data:
            settings["empty_distance"] = service_call.data[ATTR_EMPTY_DISTANCE]
        if ATTR_FULL_DISTANCE in service_call.data:
            settings["full_distance"] = service_call.data[ATTR_FULL_DISTANCE]
        if ATTR_MEASUREMENT_INTERVAL in service_call.data:
            settings["measurement_interval"] = service_call.data[ATTR_MEASUREMENT_INTERVAL]
        if ATTR_READING_SMOOTHING in service_call.data:
            settings["reading_smoothing"] = service_call.data[ATTR_READING_SMOOTHING]
        if ATTR_ALERT_LEVEL_LOW in service_call.data:
            settings["alert_level_low"] = service_call.data[ATTR_ALERT_LEVEL_LOW]
        if ATTR_ALERT_LEVEL_HIGH in service_call.data:
            settings["alert_level_high"] = service_call.data[ATTR_ALERT_LEVEL_HIGH]
        if ATTR_ALERTS_ENABLED in service_call.data:
            settings["alerts_enabled"] = service_call.data[ATTR_ALERTS_ENABLED]
            
        # Apply settings to all coordinators
        for coordinator in coordinators:
            await coordinator.async_update_settings(**settings)
    
    # Register our services with Home Assistant
    hass.services.async_register(
        DOMAIN,
        SERVICE_CALIBRATE,
        async_calibrate_service,
        schema=CALIBRATE_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_SETTINGS,
        async_update_settings_service,
        schema=UPDATE_SETTINGS_SCHEMA,
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload AquaLevel services."""
    if hass.services.has_service(DOMAIN, SERVICE_CALIBRATE):
        hass.services.async_remove(DOMAIN, SERVICE_CALIBRATE)
        
    if hass.services.has_service(DOMAIN, SERVICE_UPDATE_SETTINGS):
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_SETTINGS)