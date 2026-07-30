from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_TOPIC

class OverdriveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Overdrive MQTT", data=user_input)

        schema = vol.Schema({
            vol.Required("topic", default=DEFAULT_TOPIC): str
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
