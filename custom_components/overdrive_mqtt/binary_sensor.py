from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up binary sensors."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    
    binary_sensors = [
        # Network connectivity indicator
        OverdriveOnlineBinarySensor(entry.entry_id, entry_data),
        
        # Base operational states
        OverdriveBinarySensor(entry.entry_id, entry_data, "is_charging", "Charging Status", BinarySensorDeviceClass.BATTERY_CHARGING),
        OverdriveBinarySensor(entry.entry_id, entry_data, "is_parked", "Parking Status", None),
        OverdriveBinarySensor(entry.entry_id, entry_data, "ac_on", "Climate Control", BinarySensorDeviceClass.RUNNING),
        
        # Mapped Array Elements (Doors)
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "door_lock", 0, "Door Front Left", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "door_lock", 1, "Door Front Right", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "door_lock", 2, "Door Rear Left", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "door_lock", 3, "Door Rear Right", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "door_lock", 4, "Hood", BinarySensorDeviceClass.DOOR, invert=False),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "door_lock", 5, "Trunk", BinarySensorDeviceClass.DOOR, invert=False),
        
        # Mapped Array Elements (Windows)
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "window_open", 0, "Window Front Left", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "window_open", 1, "Window Front Right", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "window_open", 2, "Window Rear Left", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry.entry_id, entry_data, "window_open", 3, "Window Rear Right", BinarySensorDeviceClass.WINDOW),
    ]
    async_add_entities(binary_sensors)


class OverdriveOnlineBinarySensor(BinarySensorEntity):
    """Indicates if MQTT payloads are actively ticking from the vehicle."""
    
    def __init__(self, entry_id, data_store):
        self._entry_id = entry_id
        self._data_store = data_store
        self._attr_name = "Overdrive Network Status"
        self._attr_unique_id = f"overdrive_{entry_id}_network_status"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        self._attr_is_on = self._data_store.get("online", False)
        self.async_write_ha_state()


class OverdriveBinarySensor(BinarySensorEntity):
    """Standard True/False payload sensor properties."""

    def __init__(self, entry_id, data_store, key, name, device_class=None):
        self._entry_id = entry_id
        self._data_store = data_store
        self._key = key
        self._attr_name = f"Overdrive {name}"
        self._attr_unique_id = f"overdrive_{entry_id}_{key}"
        self._attr_device_class = device_class

    @property
    def available(self) -> bool:
        return self._data_store.get("online", False)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        payload = self._data_store.get("data", {})
        val = payload.get(self._key, 0)
        self._attr_is_on = bool(val == 1)
        self.async_write_ha_state()


class OverdriveArrayBinarySensor(BinarySensorEntity):
    """Extracts positions out of structural nested arrays."""

    def __init__(self, entry_id, data_store, key, index, name, device_class=None, invert=False):
        self._entry_id = entry_id
        self._data_store = data_store
        self._key = key
        self._index = index
        self._attr_name = f"Overdrive {name}"
        self._attr_unique_id = f"overdrive_{entry_id}_{key}_{index}"
        self._attr_device_class = device_class
        self._invert = invert

    @property
    def available(self) -> bool:
        return self._data_store.get("online", False)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        payload = self._data_store.get("data", {})
        target_array = payload.get(self._key, [])
        
        if len(target_array) > self._index:
            raw_val = target_array[self._index]
            
            # For door_lock: -1 indicates locked. 
            # If invert=True and class=LOCK, True means unlocked, False means locked.
            if self._invert:
                self._attr_is_on = bool(raw_val != -1)
            else:
                self._attr_is_on = bool(raw_val > 0)
        else:
            self._attr_is_on = False
            
        self.async_write_ha_state()
