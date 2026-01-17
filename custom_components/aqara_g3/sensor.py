"""Sensor platform for Aqara Camera G3."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AqaraG3DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Sensor type mapping: sensor_key -> (api_key, value_type)
SENSOR_TYPES: dict[str, tuple[str, type[bool] | type[int] | type[str]]] = {
    "wifi_rssi": ("device_wifi_rssi", int),
    "alarm_status": ("alarm_status", bool),
    "last_face_name": ("last_face_name", str),
    "last_face_person": ("last_face_person", str),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aqara Camera G3 sensor platform."""
    # Get coordinator from hass.data
    data = hass.data[DOMAIN].get(entry.entry_id)
    if not data or not isinstance(data, dict):
        _LOGGER.error("Integration data not found or invalid for entry %s", entry.entry_id)
        return
    
    coordinator = data.get("coordinator")
    if not coordinator or not isinstance(coordinator, AqaraG3DataUpdateCoordinator):
        _LOGGER.error("Coordinator not found or invalid for entry %s", entry.entry_id)
        return

    sensors = [
        AqaraG3Sensor(coordinator, "wifi_rssi", "WiFi RSSI", "mdi:wifi"),
        AqaraG3Sensor(coordinator, "alarm_status", "Alarm Status", "mdi:alarm"),
        AqaraG3Sensor(coordinator, "last_face_name", "Last Face", "mdi:account-box"),
        AqaraG3Sensor(coordinator, "last_face_person", "Last Face Person", "mdi:account-badge"),
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
        self._api_key, self._value_type = SENSOR_TYPES.get(
            sensor_key, ("", str)
        )
        self._attr_name = f"Aqara G3 {sensor_name}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{sensor_key}"
        self._attr_icon = icon
        self._logged_no_data = False
        if sensor_key == "wifi_rssi":
            self._attr_native_unit_of_measurement = "dBm"
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name="Aqara Camera G3",
            manufacturer="Aqara",
            model="Camera G3",
            configuration_url="https://home.aqara.com",
        )

    @property
    def native_value(self) -> bool | int | str | None:
        """Return the state of the sensor with correct type."""
        if self.coordinator.data is None:
            return None

        if not self._api_key:
            return None

        # Coordinator returns a normalized attr->value dict
        try:
            data = self.coordinator.data
            if not isinstance(data, dict):
                return None

            value = data.get(self._api_key)
            if value is None:
                if not self._logged_no_data:
                    _LOGGER.debug(
                        "Missing api key '%s' for %s. Available keys: %s",
                        self._api_key,
                        self._sensor_key,
                        list(data.keys()),
                    )
                    self._logged_no_data = True
                return None
            # Reset log flag when data becomes available again
            self._logged_no_data = False

            if value is None:
                return None

            # Convert value to correct type
            try:
                if self._value_type == bool:
                    # Handle "0"/"1", 0/1, "true"/"false", True/False
                    if isinstance(value, bool):
                        return value
                    if isinstance(value, str):
                        return value.lower() in ("1", "true", "yes", "on")
                    return bool(value)
                elif self._value_type == int:
                    return int(value)
                elif self._value_type == str:
                    return str(value)
                else:
                    return value
            except (ValueError, TypeError) as err:
                _LOGGER.debug(
                    "Error converting value %s to %s for %s: %s",
                    value,
                    self._value_type.__name__,
                    self._sensor_key,
                    err,
                )
                return None

        except (KeyError, TypeError, IndexError) as err:
            _LOGGER.debug("Error parsing sensor data for %s: %s", self._sensor_key, err)
            return None

