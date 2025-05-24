from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
from .spa_client import ControlMySpaClient

DATA_SCHEMA = vol.Schema({
    "email": str,
    "password": str,
    vol.Optional("use_celsius", default=True): bool
})

class ControlMySpaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        import logging
        import traceback
        _LOGGER = logging.getLogger(__name__)
        errors = {}

        if user_input is not None:
            try:
                client = ControlMySpaClient(user_input["email"], user_input["password"])
                await self.hass.async_add_executor_job(client.login)
                await self.hass.async_add_executor_job(client.get_profile)
                return self.async_create_entry(title="Control My Spa", data={
                    "email": user_input["email"],
                    "password": user_input["password"]
                }, options={
                    "Celsius": user_input["use_celsius"]
                })
            except Exception as e:
                _LOGGER.error("Integration setup failed: %s\n%s", e, traceback.format_exc())
                if "401" in str(e) or "403" in str(e):
                    errors["base"] = "auth"
                else:
                    errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

