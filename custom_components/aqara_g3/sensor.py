"""Sensor platform for Aqara Camera G3."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AqaraG3DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aqara Camera G3 sensor platform."""
    coordinator: AqaraG3DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    sensors = [
        AqaraG3Sensor(coordinator, "motion_detect", "Motion Detect", "mdi:motion-sensor"),
        AqaraG3Sensor(coordinator, "face_detect", "Face Detect", "mdi:face-recognition"),
        AqaraG3Sensor(coordinator, "pets_detect", "Pets Detect", "mdi:paw"),
        AqaraG3Sensor(coordinator, "human_detect", "Human Detect", "mdi:account"),
        AqaraG3Sensor(coordinator, "wifi_rssi", "WiFi RSSI", "mdi:wifi"),
        AqaraG3Sensor(coordinator, "alarm_status", "Alarm Status", "mdi:alarm"),
    ]

    async_add_entities(sensors, update_before_add=True)


class AqaraG3Sensor(CoordinatorEntity, SensorEntity):
    """Representation of an Aqara Camera G3 sensor."""

    def __init__(
        self,
        coordinator: AqaraG3DataUpdateCoordinator,
        sensor_key: str,
        sensor_name: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = f"Aqara G3 {sensor_name}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{sensor_key}"
        self._attr_icon = icon

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        # Map sensor keys to API response keys
        sensor_map = {
            "motion_detect": "mdtrigger_enable",
            "face_detect": "face_detect_enable",
            "pets_detect": "pets_detect_enable",
            "human_detect": "human_detect_enable",
            "wifi_rssi": "device_wifi_rssi",
            "alarm_status": "alarm_status",
        }

        api_key = sensor_map.get(self._sensor_key)
        if not api_key:
            return None

        # Parse API response structure: result.resultList[0].{api_key}.value
        try:
            data = self.coordinator.data
            if not isinstance(data, dict):
                return None
            
            result = data.get("result", {})
            result_list = result.get("resultList", [])
            if not result_list or len(result_list) == 0:
                return None
            
            device_data = result_list[0]
            if not isinstance(device_data, dict):
                return None
            
            sensor_data = device_data.get(api_key, {})
            if isinstance(sensor_data, dict):
                value = sensor_data.get("value")
            else:
                value = sensor_data
            
            return str(value) if value is not None else None
        except (KeyError, TypeError, IndexError) as err:
            _LOGGER.debug("Error parsing sensor data for %s: %s", self._sensor_key, err)
            return None

