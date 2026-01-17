"""Binary sensor platform for Aqara Camera G3."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AqaraG3DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSORS = {
    "motion_detect": ("mdtrigger_enable", "Motion Detect", "mdi:motion-sensor"),
    "face_detect": ("face_detect_enable", "Face Detect", "mdi:face-recognition"),
    "pets_detect": ("pets_detect_enable", "Pets Detect", "mdi:paw"),
    "human_detect": ("human_detect_enable", "Human Detect", "mdi:account"),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Aqara Camera G3 binary sensor platform."""
    data = hass.data[DOMAIN].get(entry.entry_id)
    if not data or not isinstance(data, dict):
        _LOGGER.error("Integration data not found or invalid for entry %s", entry.entry_id)
        return

    coordinator = data.get("coordinator")
    if not coordinator or not isinstance(coordinator, AqaraG3DataUpdateCoordinator):
        _LOGGER.error("Coordinator not found or invalid for entry %s", entry.entry_id)
        return

    entities = [
        AqaraG3BinarySensor(coordinator, key, api_key, name, icon)
        for key, (api_key, name, icon) in SENSORS.items()
    ]
    async_add_entities(entities, update_before_add=True)


class AqaraG3BinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Aqara Camera G3 binary sensor."""

    def __init__(
        self,
        coordinator: AqaraG3DataUpdateCoordinator,
        sensor_key: str,
        api_key: str,
        sensor_name: str,
        icon: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._api_key = api_key
        self._attr_name = f"Aqara G3 {sensor_name}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{sensor_key}"
        self._attr_icon = icon
        self._logged_no_data = False

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
    def is_on(self) -> bool | None:
        """Return True if the sensor is on."""
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
        self._logged_no_data = False

        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)
