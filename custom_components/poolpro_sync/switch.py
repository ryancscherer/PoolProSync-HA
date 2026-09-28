"""Switch platform for PoolPro Sync.

Only pHSwitch is exposed here — it's the one boolean-ish, writable property
confirmed in the device's metadata schema (values "0"/"1", not "OFF"/"ON").
PumpStatus and CellStatus are read/report only per the schema (no "write"
capability), so they're sensors, not switches.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PoolProSyncCoordinator

_PH_SWITCH_KEY = "pHSwitch"
_ON_VALUE = "1"
_OFF_VALUE = "0"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up PoolPro Sync switches from a config entry."""
    coordinator: PoolProSyncCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PoolProSyncPhSwitch(coordinator, entry)])


class PoolProSyncPhSwitch(CoordinatorEntity[PoolProSyncCoordinator], SwitchEntity):
    """pH dosing pump switch."""

    _attr_name = "pH Pump"

    def __init__(self, coordinator: PoolProSyncCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{_PH_SWITCH_KEY}"

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(_PH_SWITCH_KEY)
        if value is None:
            return None
        return str(value) == _ON_VALUE

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_properties({_PH_SWITCH_KEY: _ON_VALUE})

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_properties({_PH_SWITCH_KEY: _OFF_VALUE})
