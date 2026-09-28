"""Tests for the PoolPro Sync API client.

These are placeholders that lock in current (unimplemented) behavior. Once
api.py is implemented against real captured traffic, replace these with
tests against mocked HTTP responses built from API_NOTES.md fixtures.
"""

import pytest

from custom_components.poolpro_sync.api import PoolProSyncClient


async def test_login_not_yet_implemented(aiohttp_client_session):
    client = PoolProSyncClient(aiohttp_client_session, "user", "pass")
    with pytest.raises(NotImplementedError):
        await client.async_login()


async def test_get_status_not_yet_implemented(aiohttp_client_session):
    client = PoolProSyncClient(aiohttp_client_session, "user", "pass")
    with pytest.raises(NotImplementedError):
        await client.async_get_status()
