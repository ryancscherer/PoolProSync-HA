"""Sensor platform for PoolPro Sync.

Property keys and units come from the device's JetLinks metadata schema
(see API_NOTES.md). Values are exposed as reported by the device — scaling
(e.g. whether WaterTemp is whole degrees or tenths) has not been confirmed
against the app's display yet, so treat absolute values with a grain of
salt until cross-checked.
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

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(key="WaterTemp", name="Water Temperature"),
    SensorEntityDescription(key="internal_temperature", name="Controller Temperature"),
    SensorEntityDescription(key="SaltLevel", name="Salt Level", native_unit_of_measurement="ppm"),
    SensorEntityDescription(key="CellStatus", name="Cell Status"),
    SensorEntityDescription(key="ActualOutput", name="Chlorine Output", native_unit_of_measurement="%"),
    SensorEntityDescription(key="ChlorineProduction", name="Chlorine Production", native_unit_of_measurement="g"),
    SensorEntityDescription(key="COPPER_LEVEL", name="Copper Level", native_unit_of_measurement="ppm"),
    SensorEntityDescription(key="Fault", name="Fault Code"),
    SensorEntityDescription(key="WIFI_RSSI", name="Wi-Fi Signal"),
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
