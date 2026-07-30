from homeassistant import config_entries
import voluptuous as vol
from .const import (
    DOMAIN, 
    DEFAULT_NAME,
    CONF_TELEMETRY_TOPIC, 
    CONF_AVAILABILITY_TOPIC, 
    DEFAULT_TELEMETRY_TOPIC, 
    DEFAULT_AVAILABILITY_TOPIC
)

class OverdriveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_TELEMETRY_TOPIC, default=DEFAULT_TELEMETRY_TOPIC): str,
            vol.Required(CONF_AVAILABILITY_TOPIC, default=DEFAULT_AVAILABILITY_TOPIC): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)
