"""The PoolPro Sync integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PoolProSyncClient
from .const import CONF_DEVICE_ID, CONF_HOST, CONF_PORT, CONF_PRODUCT_ID, DOMAIN
from .coordinator import PoolProSyncCoordinator

PLATFORMS = ["sensor", "switch", "select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PoolPro Sync from a config entry."""
    session = async_get_clientsession(hass)
    client = PoolProSyncClient(
        session, host=entry.data[CONF_HOST], port=entry.data[CONF_PORT]
    )
    await client.async_login()

    coordinator = PoolProSyncCoordinator(
        hass, session, client, entry.data[CONF_PRODUCT_ID], entry.data[CONF_DEVICE_ID]
    )
    await coordinator.async_start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: PoolProSyncCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_stop()
    return unload_ok
