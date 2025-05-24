import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from .spa_client import ControlMySpaClient
from .const import DOMAIN

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    email = entry.data["email"]
    password = entry.data["password"]

    client = ControlMySpaClient(email, password)

    async def fetch_data():
        await hass.async_add_executor_job(client.ensure_authenticated)
        return await hass.async_add_executor_job(client.fetch_spa_data)

    coordinator = DataUpdateCoordinator(
        hass,
        logger=logging.getLogger(__name__),
        name="control_my_spa",
        update_method=fetch_data,
        update_interval=timedelta(minutes=1),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
