from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfTemperature, UnitOfElectricPotential, UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Overdrive sensors."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        OverdriveSensor(entry.entry_id, entry_data, "soc", "Battery State of Charge", PERCENTAGE, SensorDeviceClass.BATTERY),
        OverdriveSensor(entry.entry_id, entry_data, "odometer", "Odometer", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, SensorStateClass.TOTAL_INCREASING),
        OverdriveSensor(entry.entry_id, entry_data, "ev_range_km", "EV Range", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
        OverdriveSensor(entry_id=entry.entry_id, data_store=entry_data, key="volt_12v", name="12V Battery Voltage", unit=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE),
        OverdriveSensor(entry_id=entry.entry_id, data_store=entry_data, key="gear", name="Selected Gear"),
    ]
    async_add_entities(sensors)

class OverdriveSensor(SensorEntity):
    """Representation of an Overdrive metric Sensor."""
    
    def __init__(self, entry_id, data_store, key, name, unit=None, device_class=None, state_class=None):
        self._entry_id = entry_id
        self._data_store = data_store
        self._key = key
        self._attr_name = f"Overdrive {name}"
        self._attr_unique_id = f"overdrive_{entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._data_store.get("online", False)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        payload = self._data_store.get("data", {})
        self._attr_native_value = payload.get(self._key)
        self.async_write_ha_state()
