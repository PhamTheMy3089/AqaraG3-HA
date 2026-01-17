"""Button platform for Aqara Camera G3."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
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
    """Set up the Aqara Camera G3 button platform."""
    data = hass.data[DOMAIN].get(entry.entry_id)
    if not data or not isinstance(data, dict):
        _LOGGER.error("Integration data not found or invalid for entry %s", entry.entry_id)
        return

    coordinator = data.get("coordinator")
    if not coordinator or not isinstance(coordinator, AqaraG3DataUpdateCoordinator):
        _LOGGER.error("Coordinator not found or invalid for entry %s", entry.entry_id)
        return

    async_add_entities([AqaraG3RefreshFaceListButton(coordinator)], update_before_add=True)


class AqaraG3RefreshFaceListButton(CoordinatorEntity, ButtonEntity):
    """Button to refresh face list."""

    _attr_name = "Aqara G3 Refresh Face List"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: AqaraG3DataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_refresh_face_list"

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

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.async_get_face_map(force_refresh=True)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.warning("Failed to refresh face list: %s", err)
