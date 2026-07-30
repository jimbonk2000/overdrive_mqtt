import json
import logging
from datetime import timedelta
from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_point_in_time
import homeassistant.util.dt as dt_util
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor", "device_tracker"]
WATCHDOG_TIMEOUT = 60  # Seconds before marking vehicle offline

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Overdrive MQTT from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    hass.data[DOMAIN][entry.entry_id] = {
        "data": {},
        "topic": entry.data.get("topic"),
        "online": False,
        "timer_unsub": None
    }

    entry_data = hass.data[DOMAIN][entry.entry_id]

    @callback
    def mark_offline(now):
        """Callback when no MQTT message has arrived within the timeout window."""
        entry_data["online"] = False
        async_dispatcher_send(hass, f"{DOMAIN}_{entry.entry_id}_update")
        _LOGGER.warning("Overdrive vehicle has missed its check-in window. Marked offline.")

    @callback
    def mqtt_message_received(msg):
        """Handle incoming Overdrive data payload."""
        try:
            payload = json.loads(msg.payload)
            entry_data["data"] = payload
            entry_data["online"] = True

            # Reset the watchdog disconnect timer
            if entry_data["timer_unsub"]:
                entry_data["timer_unsub"]()
            
            future_time = dt_util.utcnow() + timedelta(seconds=WATCHDOG_TIMEOUT)
            entry_data["timer_unsub"] = async_track_point_in_time(hass, mark_offline, future_time)

            # Broadcast changes out to all entities
            async_dispatcher_send(hass, f"{DOMAIN}_{entry.entry_id}_update")
        except Exception as err:
            _LOGGER.error("Failed to parse Overdrive MQTT JSON payload: %s", err)

    await mqtt.async_subscribe(hass, entry.data.get("topic"), mqtt_message_received)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    entry_data = hass.data[DOMAIN].get(entry.entry_id, {})
    if entry_data.get("timer_unsub"):
        entry_data["timer_unsub"]()
        
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
