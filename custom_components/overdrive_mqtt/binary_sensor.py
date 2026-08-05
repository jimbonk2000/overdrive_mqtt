from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, INVALID_VALUES

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    
    binary_sensors = [
        # System Connection Link
        OverdriveOnlineBinarySensor(entry, entry_data),
        
        # Power & Charging State Vectors
        OverdriveBinarySensor(entry, entry_data, "is_charging", "Charging Status", BinarySensorDeviceClass.BATTERY_CHARGING),
        OverdriveBinarySensor(entry, entry_data, "is_dcfc", "DC Fast Charging Status", BinarySensorDeviceClass.BATTERY_CHARGING),
        OverdriveBinarySensor(entry, entry_data, "is_parked", "Parking Status", None),
        OverdriveBinarySensor(entry, entry_data, "ac_on", "Climate Control", BinarySensorDeviceClass.RUNNING),
        OverdriveBinarySensor(entry, entry_data, "charging_gun", "Charging Gun Connection", BinarySensorDeviceClass.PLUG),
        OverdriveBinarySensor(entry, entry_data, "charging_v2l", "V2L Discharge Action Status", None),
        
        # Operational Utilities
        OverdriveBinarySensor(entry, entry_data, "key_battery", "Key Battery Low Alert", BinarySensorDeviceClass.BATTERY),
        OverdriveBinarySensor(entry, entry_data, "drift_mode", "Drift Mode Configuration", None),
        OverdriveBinarySensor(entry, entry_data, "engine_coolant_level", "Engine Coolant Level Problem Alert", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "emergency_alarm", "Emergency Panic Alarm Status", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "speed_limit_warning", "Speed Limit Warnings Status", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "child_presence_detection", "Child Presence Subsystem Status", None),
        OverdriveBinarySensor(entry, entry_data, "key_start_state", "Engine Key Ignition Position State", None),
        OverdriveBinarySensor(entry, entry_data, "key_bt_low_power", "Bluetooth Key Low Power Status Alert", BinarySensorDeviceClass.BATTERY),
        OverdriveBinarySensor(entry, entry_data, "key_detection_reminder", "Key Detection Reminder Flag", None),
        OverdriveBinarySensor(entry, entry_data, "wireless_charging_left", "Wireless Charger Pad Left Status", BinarySensorDeviceClass.POWER),
        OverdriveBinarySensor(entry, entry_data, "wireless_charging_right", "Wireless Charger Pad Right Status", BinarySensorDeviceClass.POWER),
        
        # Lighting Modules Diagnostics
        OverdriveBinarySensor(entry, entry_data, "light_left_turn", "Indicator Signal Left Active Status", evaluator=lambda x: x != -10011 and x > 0),
        OverdriveBinarySensor(entry, entry_data, "light_right_turn", "Indicator Signal Right Active Status", evaluator=lambda x: x != -10011 and x > 0),
        OverdriveBinarySensor(entry, entry_data, "light_low_beam", "Headlights Low Beam Active Status", BinarySensorDeviceClass.LIGHT),
        OverdriveBinarySensor(entry, entry_data, "light_high_beam", "Headlights High Beam Active Status", BinarySensorDeviceClass.LIGHT),
        OverdriveBinarySensor(entry, entry_data, "light_rear_fog", "Fog Lights Rear Active Status", BinarySensorDeviceClass.LIGHT),
        OverdriveBinarySensor(entry, entry_data, "light_front_fog", "Fog Lights Front Active Status", BinarySensorDeviceClass.LIGHT),
        OverdriveBinarySensor(entry, entry_data, "light_hazard", "Hazard Emergency Lights Active Status", BinarySensorDeviceClass.LIGHT),
        OverdriveBinarySensor(entry, entry_data, "light_drl", "Daytime Running Lights DRL Active Status", BinarySensorDeviceClass.LIGHT),
        
        # Structural Doors Security Perimeter Unpacking Array
        OverdriveArrayBinarySensor(entry, entry_data, "door_lock", 0, "Door Front Left", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry, entry_data, "door_lock", 1, "Door Front Right", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry, entry_data, "door_lock", 2, "Door Rear Left", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry, entry_data, "door_lock", 3, "Door Rear Right", BinarySensorDeviceClass.LOCK, invert=True),
        OverdriveArrayBinarySensor(entry, entry_data, "door_lock", 4, "Hood", BinarySensorDeviceClass.DOOR),
        OverdriveArrayBinarySensor(entry, entry_data, "door_lock", 5, "Trunk", BinarySensorDeviceClass.DOOR),
        OverdriveArrayBinarySensor(entry, entry_data, "door_lock", 6, "Fuel Charging Flap Door", BinarySensorDeviceClass.DOOR),
        
        # Structural Windows Opening Unpacking Array
        OverdriveArrayBinarySensor(entry, entry_data, "window_open", 0, "Window Front Left", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry, entry_data, "window_open", 1, "Window Front Right", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry, entry_data, "window_open", 2, "Window Rear Left", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry, entry_data, "window_open", 3, "Window Rear Right", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry, entry_data, "window_open", 4, "Sunroof Window Extension", BinarySensorDeviceClass.WINDOW),
        OverdriveArrayBinarySensor(entry, entry_data, "window_open", 5, "Sunshade Window", BinarySensorDeviceClass.WINDOW),
        
        # Pneumatic Tire Defect Status Monitoring Flags
        OverdriveArrayBinarySensor(entry, entry_data, "tyre_p_state_fl", 0, "Tyre Evaluation Status Front Left Flaw Detect", BinarySensorDeviceClass.PROBLEM),
        OverdriveArrayBinarySensor(entry, entry_data, "tyre_p_state_fr", 0, "Tyre Evaluation Status Front Right Flaw Detect", BinarySensorDeviceClass.PROBLEM),
        OverdriveArrayBinarySensor(entry, entry_data, "tyre_p_state_rl", 0, "Tyre Evaluation Status Rear Left Flaw Detect", BinarySensorDeviceClass.PROBLEM),
        OverdriveArrayBinarySensor(entry, entry_data, "tyre_p_state_rr", 0, "Tyre Evaluation Status Rear Right Flaw Detect", BinarySensorDeviceClass.PROBLEM),
        
        # Pneumatic Tire Real-Time Leak Warnings
        OverdriveBinarySensor(entry, entry_data, "tyre_leak_fl", "Tyre Leak Alert Front Left", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "tyre_leak_fr", "Tyre Leak Alert Front Right", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "tyre_leak_rl", "Tyre Leak Alert Rear Left", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "tyre_leak_rr", "Tyre Leak Alert Rear Right", BinarySensorDeviceClass.PROBLEM),
        
        # Pneumatic Tire Receiver Wireless Telemetry Signaling Drops
        OverdriveBinarySensor(entry, entry_data, "tyre_signal_fl", "Tyre Sensor Communication Fault Front Left", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "tyre_signal_fr", "Tyre Sensor Communication Fault Front Right", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "tyre_signal_rl", "Tyre Sensor Communication Fault Rear Left", BinarySensorDeviceClass.PROBLEM),
        OverdriveBinarySensor(entry, entry_data, "tyre_signal_rr", "Tyre Sensor Communication Fault Rear Right", BinarySensorDeviceClass.PROBLEM),
        
        # Occupant Safety Systems Buckle Sensor Arrays
        OverdriveArrayBinarySensor(entry, entry_data, "seatbelt", 0, "Seatbelt Buckle Status Driver", BinarySensorDeviceClass.SAFETY),
        OverdriveArrayBinarySensor(entry, entry_data, "seatbelt", 1, "Seatbelt Buckle Status Passenger", BinarySensorDeviceClass.SAFETY),
        
        # Comfort System States Arrays
        OverdriveArrayBinarySensor(entry, entry_data, "seat_heat", 0, "Seat Heater Left Active", BinarySensorDeviceClass.RUNNING),
        OverdriveArrayBinarySensor(entry, entry_data, "seat_heat", 1, "Seat Heater Right Active", BinarySensorDeviceClass.RUNNING),
        OverdriveArrayBinarySensor(entry, entry_data, "seat_cool", 0, "Seat Cooler Left Active", BinarySensorDeviceClass.RUNNING),
        OverdriveArrayBinarySensor(entry, entry_data, "seat_cool", 1, "Seat Cooler Right Active", BinarySensorDeviceClass.RUNNING),
    ]
    
    # Inject proximity radar sensor array loops
    for idx in range(9):
        binary_sensors.append(
            OverdriveArrayBinarySensor(entry, entry_data, "radar_distances", idx, f"Proximity Radar Alert Index {idx}", BinarySensorDeviceClass.MOTION, evaluator=lambda x: x < 50)
        )
        
    async_add_entities(binary_sensors)

class OverdriveOnlineBinarySensor(BinarySensorEntity):
    def __init__(self, entry: ConfigEntry, data_store):
        self._entry = entry
        self._entry_id = entry.entry_id
        self._data_store = data_store
        self._attr_name = f"{entry.title} Network Status"
        self._attr_unique_id = f"overdrive_{self._entry_id}_network_status"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry_id)}, "name": self._entry.title}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        self._attr_is_on = self._data_store.get("online", False)
        self.async_write_ha_state()

class OverdriveBinarySensor(BinarySensorEntity):
    def __init__(self, entry: ConfigEntry, data_store, key, name, device_class=None, evaluator=None):
        self._entry = entry
        self._entry_id = entry.entry_id
        self._data_store = data_store
        self._key = key
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"overdrive_{self._entry_id}_{key}"
        self._attr_device_class = device_class
        self._evaluator = evaluator

    @property
    def available(self) -> bool:
        return self._data_store.get("online", False)

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry_id)}, "name": self._entry.title}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        payload = self._data_store.get("data", {})
        val = payload.get(self._key)
        
        if val in INVALID_VALUES:
            self._attr_is_on = None
        elif self._evaluator:
            self._attr_is_on = bool(self._evaluator(val))
        else:
            self._attr_is_on = bool(val == 1)
            
        self.async_write_ha_state()

class OverdriveArrayBinarySensor(BinarySensorEntity):
    def __init__(self, entry: ConfigEntry, data_store, key, index, name, device_class=None, invert=False, evaluator=None):
        self._entry = entry
        self._entry_id = entry.entry_id
        self._data_store = data_store
        self._key = key
        self._index = index
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"overdrive_{self._entry_id}_{key}_{index}"
        self._attr_device_class = device_class
        self._invert = invert
        self._evaluator = evaluator

    @property
    def available(self) -> bool:
        return self._data_store.get("online", False)

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._entry_id)}, "name": self._entry.title}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self) -> None:
        """Handle updated data from the coordinator."""
        raw_val = self.coordinator.data.get(self.entity_description.key)

        # Bug 1 Fix: Verify target array index logic handles both lists and dict objects safely
        if hasattr(self, "_index") and self._index is not None:
            if isinstance(raw_val, (list, dict, str)):
                if len(raw_val) > self._index:
                    raw_val = raw_val[self._index]
                else:
                    raw_val = None
            else:
                # If target container is an absolute integer rather than array, default use case
                raw_val = raw_val

        # Bug 2 Fix: Safely parse conditional states against potential NoneType outputs
        if raw_val is not None:
            try:
                self._attr_is_on = bool(int(raw_val) > 0)
            except (ValueError, TypeError):
                # Fallback evaluate string booleans natively if int translation fails
                self._attr_is_on = str(raw_val).lower() in ("true", "1", "on", "yes")
        else:
            self._attr_is_on = False

        try:
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed writing state for binary sensor %s: %s", self.entity_id, err)
