"""Sensor platform for PoolPro Sync.

Entity definitions here are placeholders. Replace the keys/units below once
the real telemetry fields are documented in API_NOTES.md.
"""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PoolProSyncCoordinator

# TODO: replace with real fields from API_NOTES.md (key must match the
# coordinator's data dict once async_get_status() is implemented).
SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="water_temperature",
        name="Water Temperature",
        native_unit_of_measurement="°F",
    ),
    SensorEntityDescription(
        key="ph",
        name="pH",
    ),
    SensorEntityDescription(
        key="chlorine",
        name="Chlorine",
        native_unit_of_measurement="ppm",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up PoolPro Sync sensors from a config entry."""
    coordinator: PoolProSyncCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PoolProSyncSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class PoolProSyncSensor(CoordinatorEntity[PoolProSyncCoordinator], SensorEntity):
    """A single PoolPro Sync telemetry sensor."""

    def __init__(
        self,
        coordinator: PoolProSyncCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.key)
