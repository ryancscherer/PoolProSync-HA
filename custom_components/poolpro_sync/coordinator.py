"""Push-based data coordinator for PoolPro Sync.

Unlike a typical polling DataUpdateCoordinator, this is fed by a persistent
WebSocket subscription: the device pushes property updates as they change,
plus a periodic full-state refresh request (see FULL_REFRESH_INTERVAL_SECONDS)
to keep rarely-changing properties from going stale.
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import PoolProSyncClient, PoolProSyncWebSocketClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PoolProSyncCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Holds the latest known properties for one PoolPro Sync device."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        client: PoolProSyncClient,
        product_id: str,
        device_id: str,
    ) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.client = client
        self.device_id = device_id
        self.product_id = product_id
        self.data: dict[str, Any] = {}
        self._ws_client = PoolProSyncWebSocketClient(
            session, client, product_id, device_id, self._handle_properties
        )

    def _handle_properties(self, properties: dict[str, Any]) -> None:
        self.async_set_updated_data({**self.data, **properties})

    async def async_start(self) -> None:
        """Start the background WebSocket subscription."""
        await self._ws_client.async_start()

    async def async_stop(self) -> None:
        """Stop the background WebSocket subscription."""
        await self._ws_client.async_stop()

    async def async_write_properties(self, properties: dict[str, Any]) -> None:
        """Write one or more properties to the device."""
        await self._ws_client.async_write_properties(properties)
