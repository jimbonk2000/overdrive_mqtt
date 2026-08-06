from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, INVALID_VALUES

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OverdriveVehicleTracker(entry, entry_data)])

class OverdriveVehicleTracker(TrackerEntity):
    def __init__(self, entry: ConfigEntry, data_store):
        self._entry = entry
        self._entry_id = entry.entry_id
        self._data_store = data_store
        self._attr_name = f"{entry.title} Position Tracker"
        self._attr_unique_id = f"overdrive_{self._entry_id}_tracker"
        self._lat = None
        self._lon = None
        self._elevation = None
        self._heading = None

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def available(self) -> bool:
        return True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": self._entry.title,
            "manufacturer": "Overdrive",
            "model": "Vehicle Telemetry Interface",
        }

    @property
    def latitude(self) -> float | None:
        return self._lat

    @property
    def longitude(self) -> float | None:
        return self._lon

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "elevation_meters": self._elevation,
            "heading_degrees": self._heading
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        if not self._data_store.get("online", False):
            return

        payload = self._data_store.get("data", {})
        lat = payload.get("lat")
        lon = payload.get("lon")
        elev = payload.get("elevation")
        head = payload.get("heading")

        if lat not in INVALID_VALUES: self._lat = lat
        if lon not in INVALID_VALUES: self._lon = lon
        if elev not in INVALID_VALUES: self._elevation = elev
        if head not in INVALID_VALUES: self._heading = head

        self.async_write_ha_state()
