"""The PoolPro Sync integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PoolProSyncClient
from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN
from .coordinator import PoolProSyncCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PoolPro Sync from a config entry."""
    session = async_get_clientsession(hass)
    client = PoolProSyncClient(
        session, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    )
    await client.async_login()

    coordinator = PoolProSyncCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
