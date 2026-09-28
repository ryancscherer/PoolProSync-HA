"""Shared pytest fixtures."""

import aiohttp
import pytest


@pytest.fixture
async def aiohttp_client_session():
    async with aiohttp.ClientSession() as session:
        yield session
