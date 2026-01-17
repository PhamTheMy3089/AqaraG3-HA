"""The Aqara Camera G3 integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components import persistent_notification

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SERVICE_REFRESH_FACE_LIST
from .coordinator import AqaraG3DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.BINARY_SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Aqara Camera G3 integration."""
    hass.data.setdefault(DOMAIN, {})
    
    async def _handle_refresh_face_list(call) -> None:
        """Handle refresh face list service call."""
        entry_id = call.data.get("entry_id")
        if not entry_id:
            # If only one entry exists, use it
            if len(hass.data.get(DOMAIN, {})) == 1:
                entry_id = next(iter(hass.data[DOMAIN].keys()))
        if not entry_id:
            _LOGGER.error("No entry_id provided for refresh_face_list")
            return

        data = hass.data.get(DOMAIN, {}).get(entry_id)
        if not data or not isinstance(data, dict):
            _LOGGER.error("Integration data not found for entry %s", entry_id)
            return

        coordinator = data.get("coordinator")
        if not coordinator:
            _LOGGER.error("Coordinator not found for entry %s", entry_id)
            return

        face_map = await coordinator.async_get_face_map(force_refresh=True)
        if not face_map:
            message = "No faces found from Aqara API."
        else:
            lines = [f"{name} → {face_id}" for face_id, name in face_map.items()]
            message = "Face list:\n" + "\n".join(lines)

        persistent_notification.async_create(
            hass,
            message,
            title="Aqara G3 Face List",
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_FACE_LIST,
        _handle_refresh_face_list,
        schema=vol.Schema({vol.Optional("entry_id"): str}),
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aqara Camera G3 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create coordinator
    coordinator = AqaraG3DataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
    }

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

