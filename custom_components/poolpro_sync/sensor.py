"""Sensor platform for PoolPro Sync.

Property keys and units come from the device's JetLinks metadata schema
(see API_NOTES.md). WaterTemp is confirmed reported in tenths of a degree
(raw 200 == 20.0C, confirmed against a live device) and scaled accordingly;
internal_temperature shares the same unit type so the same scaling is
applied, though not independently cross-checked against the app's display.
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PoolProSyncCoordinator


@dataclass(frozen=True, kw_only=True)
class PoolProSyncSensorDescription(SensorEntityDescription):
    """Describes a PoolPro Sync sensor, with an optional raw-value scale."""

    scale: float = 1


SENSOR_DESCRIPTIONS: tuple[PoolProSyncSensorDescription, ...] = (
    PoolProSyncSensorDescription(
        key="WaterTemp",
        name="Water Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
    ),
    PoolProSyncSensorDescription(
        key="internal_temperature",
        name="Controller Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        scale=0.1,
    ),
    PoolProSyncSensorDescription(
        key="SaltLevel",
        name="Salt Level",
        native_unit_of_measurement="ppm",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PoolProSyncSensorDescription(key="CellStatus", name="Cell Status"),
    PoolProSyncSensorDescription(
        key="ActualOutput",
        name="Chlorine Output",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PoolProSyncSensorDescription(
        key="ChlorineProduction",
        name="Chlorine Production",
        native_unit_of_measurement="g",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PoolProSyncSensorDescription(
        key="COPPER_LEVEL",
        name="Copper Level",
        native_unit_of_measurement="ppm",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PoolProSyncSensorDescription(key="Fault", name="Fault Code"),
    PoolProSyncSensorDescription(
        key="WIFI_RSSI",
        name="Wi-Fi Signal",
        state_class=SensorStateClass.MEASUREMENT,
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

    entity_description: PoolProSyncSensorDescription

    def __init__(
        self,
        coordinator: PoolProSyncCoordinator,
        entry: ConfigEntry,
        description: PoolProSyncSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self.entity_description.key)
        if raw is None or self.entity_description.scale == 1:
            return raw
        try:
            return round(raw * self.entity_description.scale, 1)
        except TypeError:
            return raw
