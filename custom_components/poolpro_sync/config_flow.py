"""Config flow for the PoolPro Sync integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PoolProSyncApiError, PoolProSyncAuthError, PoolProSyncClient
from .const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_PORT,
    CONF_PRODUCT_ID,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PRODUCT_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): str,
        vol.Optional(CONF_PRODUCT_ID, default=DEFAULT_PRODUCT_ID): str,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class PoolProSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PoolPro Sync.

    There's no per-account login — the app uses a fixed backend credential
    and identifies your equipment purely by its device ID (found in the
    PoolPro Sync app's device details screen, e.g. a MAC-like string such as
    "AABBCC112233").
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = PoolProSyncClient(
                session,
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
            )
            try:
                await client.async_login()
                await client.async_get_device_detail(user_input[CONF_DEVICE_ID])
            except PoolProSyncAuthError:
                errors["base"] = "invalid_auth"
            except PoolProSyncApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating PoolPro Sync device")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_DEVICE_ID], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
