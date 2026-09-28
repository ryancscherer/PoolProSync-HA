"""Select platform for PoolPro Sync.

PowerMode and WorkMode are both enum, read/write/report properties per the
device's metadata schema — confirmed working by capturing an actual
PowerMode write (AUTO -> OFF -> AUTO) round-trip through the app.
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PoolProSyncCoordinator


@dataclass(frozen=True, kw_only=True)
class PoolProSyncSelectDescription(SelectEntityDescription):
    """Describes a PoolPro Sync select entity."""

    options: tuple[str, ...] = ()


SELECT_DESCRIPTIONS: tuple[PoolProSyncSelectDescription, ...] = (
    PoolProSyncSelectDescription(
        key="PowerMode",
        name="Power Mode",
        options=("AUTO", "OFF", "ON"),
    ),
    PoolProSyncSelectDescription(
        key="WorkMode",
        name="Work Mode",
        options=("NULL", "SPA", "WINTER", "BOOST", "BACKWASH", "SALT_TEST", "SALT_ADD"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up PoolPro Sync select entities from a config entry."""
    coordinator: PoolProSyncCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PoolProSyncSelect(coordinator, entry, description)
        for description in SELECT_DESCRIPTIONS
    )


class PoolProSyncSelect(CoordinatorEntity[PoolProSyncCoordinator], SelectEntity):
    """A single writable enum property."""

    entity_description: PoolProSyncSelectDescription

    def __init__(
        self,
        coordinator: PoolProSyncCoordinator,
        entry: ConfigEntry,
        description: PoolProSyncSelectDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_options = list(description.options)
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        return self.coordinator.data.get(self.entity_description.key)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write_properties(
            {self.entity_description.key: option}
        )
