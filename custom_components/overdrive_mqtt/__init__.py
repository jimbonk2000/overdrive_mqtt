import json
import logging
from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, PLATFORMS, CONF_TELEMETRY_TOPIC, CONF_AVAILABILITY_TOPIC

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Overdrive MQTT fields from configuration entry keys."""
    hass.data.setdefault(DOMAIN, {})
    
    hass.data[DOMAIN][entry.entry_id] = {
        "data": {},
        "online": True  # Defaults to True until checked against explicit payload parameters
    }

    entry_data = hass.data[DOMAIN][entry.entry_id]
    telemetry_topic = entry.data.get(CONF_TELEMETRY_TOPIC)
    availability_topic = entry.data.get(CONF_AVAILABILITY_TOPIC)

    @callback
    def telemetry_received(msg):
        """Parse core stream metrics."""
        try:
            payload = json.loads(msg.payload)
            entry_data["data"] = payload
            async_dispatcher_send(hass, f"{DOMAIN}_{entry.entry_id}_update")
        except Exception as err:
            _LOGGER.error("Failed to parse Overdrive telemetry payload: %s", err)

    @callback
    def availability_received(msg):
        """Parse status on dedicated availability wire (online/offline)."""
        status = msg.payload.strip().lower()
        # Accommodates typical standard formats like online/offline or true/false
        is_online = status in ["online", "true", "1"]
        
        if entry_data["online"] != is_online:
            entry_data["online"] = is_online
            async_dispatcher_send(hass, f"{DOMAIN}_{entry.entry_id}_update")

    await mqtt.async_subscribe(hass, telemetry_topic, telemetry_received)
    await mqtt.async_subscribe(hass, availability_topic, availability_received)
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Safely drop configurations out of current runtime memory."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
