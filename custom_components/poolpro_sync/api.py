"""Async client for the PoolPro Sync cloud API.

The endpoints/payloads below are placeholders. Fill them in from
``API_NOTES.md`` once the real API has been captured — do not guess at
shapes here.
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

# TODO: replace with the real base URL from API_NOTES.md
BASE_URL = "https://api.poolprosync.com/v1"


class PoolProSyncAuthError(Exception):
    """Raised when authentication with PoolPro Sync fails."""


class PoolProSyncApiError(Exception):
    """Raised on an unexpected PoolPro Sync API response."""


class PoolProSyncClient:
    """Thin wrapper around the PoolPro Sync cloud API."""

    def __init__(
        self, session: aiohttp.ClientSession, username: str, password: str
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._token: str | None = None

    async def async_login(self) -> None:
        """Authenticate and store a session token.

        TODO: implement against the real login endpoint documented in
        API_NOTES.md once traffic capture is done.
        """
        raise NotImplementedError(
            "PoolPro Sync login endpoint not yet documented — see API_NOTES.md"
        )

    async def async_get_status(self) -> dict[str, Any]:
        """Fetch the latest telemetry for all devices/pools.

        TODO: implement against the real telemetry endpoint documented in
        API_NOTES.md.
        """
        raise NotImplementedError(
            "PoolPro Sync telemetry endpoint not yet documented — see API_NOTES.md"
        )
