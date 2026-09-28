"""Tests for the PoolPro Sync API client and websocket protocol handling."""

import json

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from custom_components.poolpro_sync.api import (
    PoolProSyncApiError,
    PoolProSyncAuthError,
    PoolProSyncClient,
    PoolProSyncWebSocketClient,
)


async def _make_client(app: web.Application) -> tuple[TestClient, PoolProSyncClient]:
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    poolpro_client = PoolProSyncClient(
        client.session, host=server.host, port=server.port
    )
    return client, poolpro_client


async def test_login_success():
    async def login_handler(request):
        return web.json_response(
            {"status": 200, "message": "success", "result": {"token": "abc123"}}
        )

    app = web.Application()
    app.router.add_post("/api/authorize/login", login_handler)
    client, poolpro_client = await _make_client(app)
    try:
        token = await poolpro_client.async_login()
    finally:
        await client.close()

    assert token == "abc123"
    assert poolpro_client.token == "abc123"


async def test_login_invalid_credentials():
    async def login_handler(request):
        return web.json_response({}, status=401)

    app = web.Application()
    app.router.add_post("/api/authorize/login", login_handler)
    client, poolpro_client = await _make_client(app)
    try:
        with pytest.raises(PoolProSyncAuthError):
            await poolpro_client.async_login()
    finally:
        await client.close()


async def test_login_server_error():
    async def login_handler(request):
        return web.json_response({}, status=500)

    app = web.Application()
    app.router.add_post("/api/authorize/login", login_handler)
    client, poolpro_client = await _make_client(app)
    try:
        with pytest.raises(PoolProSyncApiError):
            await poolpro_client.async_login()
    finally:
        await client.close()


async def test_get_device_detail_requires_login_first():
    async def login_handler(request):
        return web.json_response(
            {"status": 200, "message": "success", "result": {"token": "abc123"}}
        )

    async def device_handler(request):
        assert request.headers.get("X-Access-Token") == "abc123"
        return web.json_response(
            {"status": 200, "message": "success", "result": {"id": "TESTDEVICE"}}
        )

    app = web.Application()
    app.router.add_post("/api/authorize/login", login_handler)
    app.router.add_get(
        "/api/device-instance/TESTDEVICE/detail", device_handler
    )
    client, poolpro_client = await _make_client(app)
    try:
        detail = await poolpro_client.async_get_device_detail("TESTDEVICE")
    finally:
        await client.close()

    assert detail == {"id": "TESTDEVICE"}


def test_websocket_client_handles_report_property():
    received: list[dict] = []
    ws_client = PoolProSyncWebSocketClient(
        session=None,
        client=None,
        product_id="SLIMLINE",
        device_id="TESTDEVICE",
        on_properties=received.append,
    )
    message = json.dumps(
        {
            "payload": {
                "messageType": "REPORT_PROPERTY",
                "properties": {"WaterTemp": 215, "PumpStatus": "OFF"},
            },
            "topic": "/device/SLIMLINE/TESTDEVICE/message/property/report",
            "type": "result",
        }
    )
    ws_client._handle_message(message)
    assert received == [{"WaterTemp": 215, "PumpStatus": "OFF"}]


def test_websocket_client_ignores_non_property_messages():
    received: list[dict] = []
    ws_client = PoolProSyncWebSocketClient(
        session=None,
        client=None,
        product_id="SLIMLINE",
        device_id="TESTDEVICE",
        on_properties=received.append,
    )
    ws_client._handle_message(json.dumps({"requestId": "1", "type": "complete"}))
    ws_client._handle_message("not json")
    assert received == []
