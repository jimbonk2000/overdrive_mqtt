from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up tracking entity."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OverdriveVehicleTracker(entry.entry_id, entry_data)])

class OverdriveVehicleTracker(TrackerEntity):
    """Tracks vehicle position on the UI map via lat/lon telemetry attributes."""

    def __init__(self, entry_id, data_store):
        self._entry_id = entry_id
        self._data_store = data_store
        self._attr_name = "Overdrive Vehicle Position"
        self._attr_unique_id = f"overdrive_{entry_id}_tracker"

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def available(self) -> bool:
        return self._data_store.get("online", False)

    @property
    def latitude(self) -> float | None:
        return self._data_store.get("data", {}).get("lat")

    @property
    def longitude(self) -> float | None:
        return self._data_store.get("data", {}).get("lon")

    @property
    def extra_state_attributes(self) -> dict:
        payload = self._data_store.get("data", {})
        return {
            "elevation_meters": payload.get("elevation"),
            "heading_degrees": payload.get("heading")
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, f"{DOMAIN}_{self._entry_id}_update", self._update_callback)
        )

    @callback
    def _update_callback(self):
        self.async_write_ha_state()
