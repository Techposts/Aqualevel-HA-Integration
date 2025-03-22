"""AquaLevel services."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from . import DOMAIN, AquaLevelDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_CALIBRATE = "calibrate"

# Parameter constants
ATTR_ENTITY_ID = "entity_id"
ATTR_CALIBRATION_TYPE = "calibration_type"

# Schema for the calibrate service
CALIBRATE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_CALIBRATION_TYPE): vol.In(["empty", "full"]),
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
            
        # Find valid coordinators from entities
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
    
    # Register our service with Home Assistant
    hass.services.async_register(
        DOMAIN,
        SERVICE_CALIBRATE,
        async_calibrate_service,
        schema=CALIBRATE_SCHEMA,
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload AquaLevel services."""
    if hass.services.has_service(DOMAIN, SERVICE_CALIBRATE):
        hass.services.async_remove(DOMAIN, SERVICE_CALIBRATE)
