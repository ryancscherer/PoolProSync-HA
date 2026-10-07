"""Client for the PoolPro Sync cloud API (a JetLinks-based IoT backend).

Protocol reverse-engineered from packet captures — see API_NOTES.md.

The app authenticates with a fixed, non-account-specific login before
addressing a device by its device ID, then uses a JetLinks messaging
WebSocket to receive live property reports and send property writes /
function invocations.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp

from .const import DEFAULT_HOST, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

# Fixed credential used by every copy of the PoolPro Sync app to reach the
# JetLinks device gateway. Not specific to any account.
_LOGIN_USERNAME = "websocket"
_LOGIN_PASSWORD = "qushiyun@IOT123"

_RECONNECT_MIN_DELAY = 5
_RECONNECT_MAX_DELAY = 60


class PoolProSyncAuthError(Exception):
    """Raised when authentication with PoolPro Sync fails."""


class PoolProSyncApiError(Exception):
    """Raised on an unexpected PoolPro Sync API response."""


class PoolProSyncClient:
    """Thin wrapper around the PoolPro Sync cloud HTTP API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
    ) -> None:
        self._session = session
        self._base_url = f"http://{host}:{port}/api"
        self._ws_base_url = f"ws://{host}:{port}/api/messaging"
        self.token: str | None = None

    async def async_login(self) -> str:
        """Authenticate and store the session token."""
        try:
            resp = await self._session.post(
                f"{self._base_url}/authorize/login",
                json={
                    "username": _LOGIN_USERNAME,
                    "password": _LOGIN_PASSWORD,
                    "remember": False,
                    "expires": 3600000,
                    "verifyCode": "",
                    "verifyKey": "",
                },
            )
        except aiohttp.ClientError as err:
            raise PoolProSyncApiError(f"Error connecting to PoolPro Sync: {err}") from err

        if resp.status == 401:
            raise PoolProSyncAuthError("PoolPro Sync rejected login credentials")
        if resp.status != 200:
            raise PoolProSyncApiError(f"Unexpected login status {resp.status}")

        data = await resp.json(content_type=None)
        result = data.get("result")
        if data.get("status") != 200 or not result or "token" not in result:
            raise PoolProSyncAuthError(data.get("message", "Login failed"))

        self.token = result["token"]
        return self.token

    async def async_get_device_detail(self, device_id: str) -> dict[str, Any]:
        """Fetch device metadata/detail for a given device ID."""
        if not self.token:
            await self.async_login()

        resp = await self._session.get(
            f"{self._base_url}/device-instance/{device_id}/detail",
            headers={"X-Access-Token": self.token},
        )
        if resp.status == 401:
            raise PoolProSyncAuthError("PoolPro Sync token rejected")
        if resp.status != 200:
            raise PoolProSyncApiError(f"Unexpected status {resp.status}")

        data = await resp.json(content_type=None)
        if "result" not in data:
            raise PoolProSyncApiError(data.get("message", "Unexpected response"))
        return data["result"]

    def websocket_url(self) -> str:
        """Build the messaging WebSocket URL for the current token."""
        if not self.token:
            raise PoolProSyncAuthError("Not logged in")
        return f"{self._ws_base_url}/{self.token}"


class PoolProSyncWebSocketClient:
    """Maintains a subscription to a device's live property stream.

    Reconnects (and re-authenticates, since the token is tied to a login
    session) automatically on disconnect.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        client: PoolProSyncClient,
        product_id: str,
        device_id: str,
        on_properties: Callable[[dict[str, Any]], None],
    ) -> None:
        self._session = session
        self._client = client
        self._product_id = product_id
        self._device_id = device_id
        self._on_properties = on_properties
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._run_task: asyncio.Task | None = None
        self._refresh_task: asyncio.Task | None = None
        self._stopped = False

    async def async_start(self) -> None:
        """Start the background connection task."""
        self._stopped = False
        self._run_task = asyncio.create_task(self._async_run())

    async def async_stop(self) -> None:
        """Stop the background connection task."""
        self._stopped = True
        if self._refresh_task:
            self._refresh_task.cancel()
        if self._run_task:
            self._run_task.cancel()
        if self._ws is not None and not self._ws.closed:
            await self._ws.close()

    async def async_write_properties(self, properties: dict[str, Any]) -> None:
        """Send a WRITE_PROPERTY command for the device."""
        if self._ws is None or self._ws.closed:
            raise PoolProSyncApiError("PoolPro Sync websocket is not connected")
        now_ms = int(time.time() * 1000)
        await self._ws.send_json(
            {
                "type": "sub",
                "topic": f"/device-message-sender/{self._product_id}/{self._device_id}",
                "parameter": {
                    "messageType": "WRITE_PROPERTY",
                    "header": {"async": False},
                    "deviceId": self._device_id,
                    "messageId": now_ms,
                    "timestamp": now_ms,
                    "properties": properties,
                },
                "id": str(now_ms),
            }
        )

    async def _async_run(self) -> None:
        delay = _RECONNECT_MIN_DELAY
        while not self._stopped:
            try:
                await self._client.async_login()
                async with self._session.ws_connect(
                    self._client.websocket_url()
                ) as ws:
                    self._ws = ws
                    await self._async_subscribe(ws)
                    self._refresh_task = asyncio.create_task(
                        self._async_periodic_refresh()
                    )
                    delay = _RECONNECT_MIN_DELAY
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            self._handle_message(msg.data)
                        elif msg.type in (
                            aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR,
                        ):
                            break
            except (aiohttp.ClientError, PoolProSyncAuthError, asyncio.TimeoutError) as err:
                _LOGGER.debug("PoolPro Sync websocket error, reconnecting: %s", err)
            finally:
                if self._refresh_task:
                    self._refresh_task.cancel()
                    self._refresh_task = None
                self._ws = None

            if self._stopped:
                break
            await asyncio.sleep(delay)
            delay = min(delay * 2, _RECONNECT_MAX_DELAY)

    async def _async_subscribe(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        await ws.send_json(
            {
                "type": "sub",
                "topic": f"/device/{self._product_id}/{self._device_id}/**",
                "parameter": {"headers": {"async": False}},
                "id": str(int(time.time() * 1000)),
            }
        )
        await self._async_request_full_report(ws)

    async def _async_request_full_report(
        self, ws: aiohttp.ClientWebSocketResponse
    ) -> None:
        now_ms = int(time.time() * 1000)
        await ws.send_json(
            {
                "type": "sub",
                "topic": f"/device-message-sender/{self._product_id}/{self._device_id}",
                "parameter": {
                    "messageType": "INVOKE_FUNCTION",
                    "inputs": [],
                    "timestamp": now_ms,
                    "functionId": "triggerReport",
                    "deviceId": self._device_id,
                    "headers": {"async": False},
                },
                "id": str(now_ms),
            }
        )

    async def _async_periodic_refresh(self) -> None:
        from .const import FULL_REFRESH_INTERVAL_SECONDS

        while True:
            await asyncio.sleep(FULL_REFRESH_INTERVAL_SECONDS)
            if self._ws is not None and not self._ws.closed:
                await self._async_request_full_report(self._ws)

    def _handle_message(self, raw: str) -> None:
        try:
            data = json.loads(raw)
        except ValueError:
            return
        payload = data.get("payload")
        if not isinstance(payload, dict):
            return
        message_type = payload.get("messageType")
        if message_type == "REPORT_PROPERTY":
            properties = payload.get("properties")
            if properties:
                self._on_properties(properties)
        elif message_type == "INVOKE_FUNCTION_REPLY" and payload.get("success") is False:
            # The device itself can be slow/unresponsive over its own MQTT
            # link to the gateway - a timeout here doesn't mean our request
            # was malformed, and periodic refresh will simply retry later.
            _LOGGER.debug(
                "PoolPro Sync function '%s' failed: %s",
                payload.get("functionId"),
                payload.get("message", payload.get("code")),
            )
