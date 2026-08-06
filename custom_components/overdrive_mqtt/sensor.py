from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfTemperature, UnitOfElectricPotential, UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, INVALID_VALUES
from datetime import datetime, timezone

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        # System & Timestamps
        OverdriveSensor(entry, entry_data, "utc", "UTC Timestamp"),
        OverdriveSensor(entry, entry_data, "vd_timestamp", "VD Timestamp"),
        
        # Core EV Metrics
        OverdriveSensor(entry, entry_data, "soc", "Battery State of Charge", PERCENTAGE, SensorDeviceClass.BATTERY),
        OverdriveSensor(entry, entry_data, "odometer", "Odometer", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, SensorStateClass.TOTAL_INCREASING),
        OverdriveSensor(entry, entry_data, "ev_range_km", "EV Range", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
        OverdriveSensor(entry, entry_data, "volt_12v", "12V Battery Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        OverdriveSensor(entry, entry_data, "gear", "Selected Gear"),
        OverdriveSensor(entry, entry_data, "speed", "Speed", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED),
        # Powertrain Performance Tracking
        OverdriveSensor(entry, entry_data, "power", "Power", "kW", SensorDeviceClass.POWER),
        OverdriveSensor(entry, entry_data, "charge_power", "Charge Power", "kW", SensorDeviceClass.POWER),
        OverdriveSensor(entry, entry_data, "consumption_50km", "Consumption 50km", "kWh/100km"),
        OverdriveSensor(entry, entry_data, "accel_pct", "Accelerator Pedal", PERCENTAGE),
        OverdriveSensor(entry, entry_data, "brake_pct", "Brake Pedal", PERCENTAGE),
        OverdriveSensor(entry, entry_data, "steering_deg", "Steering Angle", "°"),
        OverdriveSensor(entry, entry_data, "slope_deg", "Slope", "°"),
        
        # Core High Voltage Battery Diagnostics
        OverdriveSensor(entry, entry_data, "soh", "State of Health", PERCENTAGE),
        OverdriveSensor(entry, entry_data, "soh_oem", "State of Health OEM", PERCENTAGE),
        OverdriveSensor(entry, entry_data, "capacity", "Capacity", "kWh"),
        OverdriveSensor(entry, entry_data, "capacity_ah", "Capacity Ah", "Ah"),
        OverdriveSensor(entry, entry_data, "hv_pack_v", "HV Pack Voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        
        # Cell Health & Deviations
        OverdriveSensor(entry, entry_data, "cell_v_max", "Cell Voltage Max", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        OverdriveSensor(entry, entry_data, "cell_v_min", "Cell Voltage Min", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        OverdriveSensor(entry, entry_data, "cell_v_delta", "Cell Voltage Delta", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE),
        OverdriveSensor(entry, entry_data, "cell_t_max", "Cell Temp Max", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "cell_t_min", "Cell Temp Min", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "cell_t_avg", "Cell Temp Avg", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "cell_t_delta", "Cell Temp Delta", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        # Physical Module Temperatures
        OverdriveSensor(entry, entry_data, "ext_temp", "Exterior Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "batt_temp", "Battery Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "bodywork_batt_temp", "Bodywork Battery Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        
        # Distance & Efficiency Counters
        OverdriveSensor(entry, entry_data, "trip_km", "Trip Distance", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
        OverdriveSensor(entry, entry_data, "trip_hours", "Trip Duration", "h", SensorDeviceClass.DURATION),
        OverdriveSensor(entry, entry_data, "trip_kwh", "Trip Energy Used", "kWh"),
        OverdriveSensor(entry, entry_data, "driving_time_hours", "Total Driving Time", "h", SensorDeviceClass.DURATION),
        OverdriveSensor(entry, entry_data, "total_elec_con", "Total Electric Consumption", "kWh", state_class=SensorStateClass.TOTAL_INCREASING),
        OverdriveSensor(entry, entry_data, "total_fuel_con", "Total Fuel Consumption", "L"),
        OverdriveSensor(entry, entry_data, "bodywork_range_km", "Bodywork Range", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
        OverdriveSensor(entry, entry_data, "ev_mileage_km", "EV Cumulative Mileage", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
        
        # Motors & Internal Mechanical Diagnostics
        OverdriveSensor(entry, entry_data, "motor_front_rpm", "Motor Front RPM", "rpm"),
        OverdriveSensor(entry, entry_data, "motor_front_torque", "Motor Front Torque", "Nm"),
        OverdriveSensor(entry, entry_data, "engine_rpm", "Engine RPM", "rpm"),
        OverdriveSensor(entry, entry_data, "oil_level", "Engine Oil Level"),
        OverdriveSensor(entry, entry_data, "engine_code", "Engine Diagnostic Code"),
        OverdriveSensor(entry, entry_data, "batt_12v_level", "12V Battery Level State"),
        
        # System Modes & Operational Profiles
        OverdriveSensor(entry, entry_data, "energy_mode", "Energy Mode Configuration"),
        OverdriveSensor(entry, entry_data, "op_mode", "Operational Mode Configuration"),
        OverdriveSensor(entry, entry_data, "charging_state", "Charging State Code"),
        OverdriveSensor(entry, entry_data, "charger_state", "Charger State Code"),
        OverdriveSensor(entry, entry_data, "charging_mode", "Charging Mode Code"),
        OverdriveSensor(entry, entry_data, "charging_type", "Charging Type Code"),
        # Cabin Utilities
        OverdriveSensor(entry, entry_data, "ac_cycle", "AC Cycle Mode"),
        OverdriveSensor(entry, entry_data, "ac_wind", "AC Wind Level"),
        OverdriveSensor(entry, entry_data, "ac_fan", "AC Fan Speed"),
        OverdriveSensor(entry, entry_data, "temp_unit", "Temperature Unit Profile"),
        OverdriveSensor(entry, entry_data, "ambient_colour", "Ambient Lighting Color Index"),
        OverdriveSensor(entry, entry_data, "sunroof_state", "Sunroof Structural State"),
        OverdriveSensor(entry, entry_data, "sunroof_pos", "Sunroof Raw Position Data"),
        OverdriveSensor(entry, entry_data, "sunshade_pct", "Sunshade Position Percentage", PERCENTAGE),
        OverdriveSensor(entry, entry_data, "wireless_charging_status", "Wireless Charger Charging Status"),
        
        # Safety Subsystems
        OverdriveSensor(entry, entry_data, "mcu_status", "MCU Status Alert Level"),
        OverdriveSensor(entry, entry_data, "power_level", "Power Limit Operational Level"),
        
        # Individual Pneumatic Tire Pressures (kPa)
        OverdriveSensor(entry, entry_data, "tyre_p_fl", "Tyre Pressure Front Left", "kPa", SensorDeviceClass.PRESSURE),
        OverdriveSensor(entry, entry_data, "tyre_p_fr", "Tyre Pressure Front Right", "kPa", SensorDeviceClass.PRESSURE),
        OverdriveSensor(entry, entry_data, "tyre_p_rl", "Tyre Pressure Rear Left", "kPa", SensorDeviceClass.PRESSURE),
        OverdriveSensor(entry, entry_data, "tyre_p_rr", "Tyre Pressure Rear Right", "kPa", SensorDeviceClass.PRESSURE),
        
        # Individual Pneumatic Tire Temperatures (°C)
        OverdriveSensor(entry, entry_data, "tyre_t_fl", "Tyre Temp Front Left", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "tyre_t_fr", "Tyre Temp Front Right", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "tyre_t_rl", "Tyre Temp Rear Left", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        OverdriveSensor(entry, entry_data, "tyre_t_rr", "Tyre Temp Rear Right", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
        
        # Diagnostic Tire Fault Evaluation Counters
        OverdriveSensor(entry, entry_data, "tyre_system_state", "Tyre System Status Evaluation"),
        OverdriveSensor(entry, entry_data, "tyre_temp_state", "Tyre Temperature Evaluation Flags"),
    ]
    async_add_entities(sensors)

class OverdriveSensor(SensorEntity):
    def __init__(self, entry: ConfigEntry, data_store, key, name, unit=None, device_class=None, state_class=None):
        self._entry = entry
        self._entry_id = entry.entry_id
        self._data_store = data_store
        self._key = key
        self._attr_name = f"{entry.title} {name}"
        self._attr_unique_id = f"overdrive_{self._entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def available(self) -> bool:
        # Dipaksa selalu True agar data terakhir tidak berubah menjadi 'unavailable'
        return True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": self._entry.title,
            "manufacturer": "Overdrive",
            "model": "Vehicle Telemetry Interface",
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        # Proteksi: Jangan perbarui data jika status jaringan sedang offline
        if not self._data_store.get("online", False):
            return

        payload = self._data_store.get("data", {})
        val = payload.get(self._key)
        
        if val in INVALID_VALUES or val == "NULL":
            self._attr_native_value = None
        else:
            self._attr_native_value = val
            
        self.async_write_ha_state()
