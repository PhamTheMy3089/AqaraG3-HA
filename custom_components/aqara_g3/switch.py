"""Switch platform for Aqara Camera G3."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
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
    """Set up the Aqara Camera G3 switch platform."""
    data = hass.data[DOMAIN].get(entry.entry_id)
    if not data or not isinstance(data, dict):
        _LOGGER.error("Integration data not found or invalid for entry %s", entry.entry_id)
        return

    coordinator = data.get("coordinator")
    if not coordinator or not isinstance(coordinator, AqaraG3DataUpdateCoordinator):
        _LOGGER.error("Coordinator not found or invalid for entry %s", entry.entry_id)
        return

    async_add_entities([AqaraG3VideoSwitch(coordinator)], update_before_add=True)


class AqaraG3VideoSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control video on/off."""

    _attr_name = "Aqara G3 Video"
    _attr_icon = "mdi:video"

    def __init__(self, coordinator: AqaraG3DataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_set_video"

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
        """Return True if video is enabled."""
        data = self.coordinator.data
        if not isinstance(data, dict):
            return None

        value = data.get("set_video")
        if value is None:
            return None

        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on video."""
        await self.coordinator.api.set_video(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off video."""
        await self.coordinator.api.set_video(False)
        await self.coordinator.async_request_refresh()
