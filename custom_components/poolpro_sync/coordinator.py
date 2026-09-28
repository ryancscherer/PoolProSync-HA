"""Data update coordinator for PoolPro Sync."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PoolProSyncApiError, PoolProSyncAuthError, PoolProSyncClient
from .const import DEFAULT_SCAN_INTERVAL_SECONDS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class PoolProSyncCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the PoolPro Sync cloud API on an interval."""

    def __init__(self, hass: HomeAssistant, client: PoolProSyncClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get_status()
        except PoolProSyncAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except PoolProSyncApiError as err:
            raise UpdateFailed(f"Error communicating with PoolPro Sync: {err}") from err
